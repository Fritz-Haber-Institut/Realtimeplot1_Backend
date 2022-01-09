import datetime
import re
from uuid import uuid4

import jwt  # pip install Flask-JWT
from flask import (Blueprint, Response, abort, current_app, jsonify,
                   make_response, request, url_for)
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.user_created_data import get_request_dict
from sqlalchemy import exc

from .decorators import token_required
from .models import User, UserTypeEnum, db
from .password import check_password_hash, get_hash

auth_blueprint = Blueprint(
    "auth",
    __name__,
    template_folder="auth/",
)

def is_last_admin() -> bool:
    return User.query.filter_by(user_type=UserTypeEnum.admin).count() <= 1


def create_user_dict(user: User) -> dict:
    user_dict = user.to_dict()
    user_dict["url"] = url_for("auth.user", user_id=user.user_id)
    return user_dict


@auth_blueprint.route("/get_access_token", methods=["POST"])
def get_access_token():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response(
            "UNAUTHORIZED",
            status.UNAUTHORIZED,
            {"Authentication": "login_name and password required"},
        )

    user = User.query.filter_by(login_name=auth.username).first()
    if user and check_password_hash(auth.password, user.password_hash):
        token = jwt.encode(
            {
                "user_id": user.user_id,
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(
                    minutes=current_app.config["ACCESS_TOKEN_VALIDITY_TIME"]
                ),
            },
            current_app.config["SECRET_KEY"],
            "HS256",
        )

        return jsonify({"access_token": token.decode(), "user_url": url_for("auth.user", user_id=user.user_id)})

    return make_response(
        "FORBIDDEN",
        status.FORBIDDEN,
        {"Authentication": "Invalid combination of login_name and password"},
    )


@auth_blueprint.route("/users", methods=["GET", "POST"])
@token_required
def users(current_user):
    if request.method == "GET":
        if current_user.user_type == UserTypeEnum.admin:
            return make_response({"users": [create_user_dict(user) for user in User.query.all()]}, status.OK)
        else:
            return make_response(
                "FORBIDDEN",
                status.FORBIDDEN,
                {"Authentication": "Only administrators can access this endpoint"},
            )
    if request.method == "POST":
        data = get_request_dict()

        if type(data) == Response:
            return data

        if User.query.filter_by(login_name=data.get("login_name")).first():
            return make_response(
                "USER ALREADY EXISTS",
                status.CONFLICT,
            )
        else:
            try:
                temporary_password = str(uuid4())
                new_user = User(
                    user_id=str(uuid4()),
                    login_name=data.get("login_name"),
                    first_name=data.get("first_name"),
                    last_name=data.get("last_name"),
                    email=data.get("email"),
                    password_hash=get_hash(temporary_password),
                    user_type=UserTypeEnum(data.get("user_type")).name,
                    preferred_language=data.get("preferred_language")
                )
                db.session.add(new_user)
                db.session.commit()

                user_dict = create_user_dict(new_user)
                user_dict["temporary_password"] = temporary_password

                return user_dict

            except exc.IntegrityError as e:
                db.session.rollback()
                return make_response(
                    e.orig.args[0],
                    status.BAD_REQUEST,
                )
            except ValueError as e:
                db.session.rollback()
                return make_response(
                    e.args[0],
                    status.BAD_REQUEST,
                )


@auth_blueprint.route("/users/current", methods=["GET", "PUT", "DELETE"])
@auth_blueprint.route("/users/<user_id>", methods=["GET", "PUT", "DELETE"])
@token_required
def user(current_user, user_id=None):
    if not user_id:
        user_id = current_user.user_id

    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return abort(404)

    if not (
        current_user.user_type == UserTypeEnum.admin or current_user.user_id == user_id
    ):
        return make_response(
            "FORBIDDEN",
            status.FORBIDDEN,
            {
                "Authentication": f"Only administrators or the user with user_id {user_id} can access this endpoint."
            },
        )

    if request.method == "GET":
        return user.to_dict()

    if request.method == "PUT":
        data = get_request_dict()
        if type(data) == Response:
            return data

        errors = []

        if "email" in data:
            email = data.get("email")
            if email == "" or re.match("[^@]+@[^@]+\.[^@]+", email):
                user.email = email
            else:
                errors.append(f"email: {email} is not a valid email address")

        first_name = data.get("first_name")
        if first_name:
            user.first_name = first_name

        last_name = data.get("last_name")
        if last_name:
            user.last_name = last_name

        login_name = data.get("login_name")
        if first_name:
            user.login_name = login_name
        try:
            user_type = data.get("user_type")
            if user_type and user.user_type == UserTypeEnum.admin and UserTypeEnum(user_type).name == "user" and is_last_admin():
                errors.append(f"user_type: The user_type cannot be changed from 'admin' to 'user' because the user '{user.login_name}' is the last registered admin in the database.")
            elif user_type and current_user.user_type == UserTypeEnum.admin:
                user.user_type = UserTypeEnum(user_type).name
        except ValueError as e:
            errors.append(f"user_type: {e}")
            
        password = data.get("password")
        if "password" in data:
            if password.strip() != "":
                auth_password = request.authorization.password
                auth_username = request.authorization.username
                if  current_user.user_type == UserTypeEnum.admin or (check_password_hash(auth_password, user.password_hash) and (auth_username == user.login_name or auth_username == "")):
                    user.password_hash = get_hash(password)
                else: 
                    errors.append(f"password: You are not authorized to change the password. Only administrators and the user {user.login_name} which must authenticate with their access-token + password are allowed to change the password.")
            else:
                errors.append(f"password: The password must not be empty.")

        preferred_language = data.get("preferred_language")
        if preferred_language:
            user.preferred_language = preferred_language
            
        db.session.commit()
        response_dict = {"user": user.to_dict()}
        if len(errors) >= 1:
            response_dict["errors"] = errors
        return jsonify(response_dict)


    if request.method == "DELETE":
        if (
            user.user_type == UserTypeEnum.admin
            and User.query.filter_by(user_type=UserTypeEnum.admin).count() <= 1
        ):
            return make_response(
                f"{user.login_name} IS THE ONLY REGISTERED ADMIN AND THEREFORE CANNOT BE DELETED",
                status.CONFLICT,
            )

        db.session.delete(user)
        db.session.commit()
        return make_response(
            f"USER {user.login_name} SUCCESSFULLY DELETED",
            status.OK,
        )
