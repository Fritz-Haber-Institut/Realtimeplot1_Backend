import datetime
from functools import wraps

import jwt  # pip install Flask-JWT
from flask import Blueprint, current_app, jsonify, make_response, request

from .apps.utilities import http_status_codes as status
from .models import User, db
from .password import check_password_hash

auth_blueprint = Blueprint(
    "entries",
    __name__,
    template_folder="auth/",
)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "x-access-tokens" in request.headers:
            token = request.headers["x-access-tokens"]

        if not token:
            return jsonify({"message": "missing access_token"})
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = Users.query.filter_by(user_id=data["user_id"]).first()
        except:
            return jsonify({"message": "invalid access_token"})

        return f(current_user, *args, **kwargs)

    return decorator


@auth_blueprint.route("/get_access_token", methods=["POST"])
def get_access_token():
    auth = request.authorization
    if not auth or not auth.login_name or not auth.password:
        return make_response(
            "UNAUTHORIZED",
            status.UNAUTHORIZED,
            {"Authentication": "login_name and password required"},
        )

    user = Users.query.filter_by(login_name=auth.login_name).first()
    if check_password_hash(user.password_hash, auth.password):
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

        return jsonify({"access_token": token})

    return make_response(
        "UNAUTHORIZED", status.UNAUTHORIZED, {"Authentication": "login_name and password required"}
    )
