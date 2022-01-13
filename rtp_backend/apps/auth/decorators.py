from functools import wraps

import jwt  # pip install Flask-JWT
from flask import current_app, make_response, request
from rtp_backend.apps.utilities import http_status_codes as status

from .models import User


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "x-access-tokens" in request.headers:
            token = request.headers["x-access-tokens"]

        if not token:
            return make_response(
                {"errors": ["Access to this resource requires a valid access-token."]},
                status.UNAUTHORIZED,
            )
        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            current_user = User.query.filter_by(user_id=data["user_id"]).first()
        except:
            return make_response(
                {"errors": ["The access-token sent is invalid or no longer accepted."]},
                status.FORBIDDEN,
            )

        return f(current_user, *args, **kwargs)

    return decorator
