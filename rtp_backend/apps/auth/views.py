import datetime
import re
from uuid import uuid4

import jwt  # pip install Flask-JWT
from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    make_response,
    request,
    url_for,
)
from sqlalchemy import exc

from rtp_backend.apps.email.helper_functions import delete_subscriptions
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.generic_responses import (
    already_exists_in_database,
    forbidden_because_not_an_admin,
    invalid_credentials,
    no_credentials,
    respond_with_404,
    successfully_deleted,
)
from rtp_backend.apps.utilities.user_created_data import get_request_dict

from .decorators import token_required
from .helper_functions import is_admin, is_last_admin
from .models import User, UserTypeEnum, db
from .password import check_password_hash, get_hash

auth_blueprint = Blueprint(
    "auth",
    __name__,
    template_folder="auth/",
)


@auth_blueprint.route("/get_access_token", methods=["POST"])
def get_access_token():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return no_credentials()

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

        return jsonify(
            {
                "access_token": token.decode(),
                "user_url": url_for("auth.user", user_id=user.user_id),
            }
        )

    return invalid_credentials()


@auth_blueprint.route("/users", methods=["GET", "POST"])
@token_required
def users(current_user):
    if not is_admin(current_user):
        return forbidden_because_not_an_admin()

    if request.method == "GET":
        return make_response(
            {"users": [user.to_dict() for user in User.query.all()]},
            status.OK,
        )

    elif request.method == "POST":
        data = get_request_dict()

        if type(data) == Response:
            return data

        if User.query.filter_by(login_name=data.get("login_name")).first():
            return already_exists_in_database("user", data.get("login_name"))
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
                    preferred_language=data.get("preferred_language"),
                )
                db.session.add(new_user)
                db.session.commit()

                user_dict = new_user.to_dict()
                user_dict["temporary_password"] = temporary_password

                return {"user": user_dict}

            except exc.IntegrityError as e:
                db.session.rollback()
                return make_response(
                    {
                        "errors": [
                            "The user creation request did not contain all of the information required."
                        ]
                    },
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
        return respond_with_404("user", user_id)

    if not (
        current_user.user_type == UserTypeEnum.admin or current_user.user_id == user_id
    ):
        return make_response(
            {
                "errors": [
                    f"Only administrators or the user with user_id {user_id} can access this endpoint."
                ]
            },
            status.FORBIDDEN,
        )

    if request.method == "GET":
        return {"user": user.to_dict()}

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
        user_with_login_name = User.query.filter_by(login_name=login_name).first()
        if login_name:
            if user_with_login_name:
                errors.append(
                    f"login_name: The login_name ({login_name}) is already in use."
                )

            else:
                user.login_name = login_name
        try:
            user_type = data.get("user_type")
            if (
                user_type
                and user.user_type == UserTypeEnum.admin
                and UserTypeEnum(user_type).name == "user"
                and is_last_admin()
            ):
                errors.append(
                    f"user_type: The user_type cannot be changed from 'admin' to 'user' because the user '{user.login_name}' is the last registered admin in the database."
                )
            elif user_type and current_user.user_type == UserTypeEnum.admin:
                user.user_type = UserTypeEnum(user_type).name
        except ValueError:
            errors.append(
                f"user_type: The user_type ({user_type}) is not valid and was therefore not accepted."
            )

        password = data.get("password")
        if "password" in data:
            if password.strip() != "" and request.authorization:
                auth_password = request.authorization.password
                auth_username = request.authorization.username
                if current_user.user_type == UserTypeEnum.admin or (
                    check_password_hash(auth_password, user.password_hash)
                    and (auth_username == user.login_name or auth_username == "")
                ):
                    user.password_hash = get_hash(password)
                else:
                    errors.append(
                        f"password: You are not authorized to change the password. Only administrators and the user {user.login_name} which must authenticate with their access-token + password are allowed to change the password."
                    )
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
                {
                    "errors": [
                        f"The user ({user.login_name}) is the only registered admin and therefore cannot be deleted."
                    ]
                },
                status.CONFLICT,
            )
        delete_subscriptions(user.user_id)
        db.session.delete(user)
        db.session.commit()
        return successfully_deleted("user", user.login_name)
