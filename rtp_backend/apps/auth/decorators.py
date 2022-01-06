import jwt  # pip install Flask-JWT
from .models import User
from flask import make_response, request, current_app
from rtp_backend.apps.utilities import http_status_codes as status
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "x-access-tokens" in request.headers:
            token = request.headers["x-access-tokens"]

        if not token:
            return make_response(
                "MISSING ACCESS-TOKEN",
                status.UNAUTHORIZED,
                {"Authentication": "missing access_token"},
            )
        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            current_user = User.query.filter_by(user_id=data["user_id"]).first()
        except:
            return make_response(
                "INVALID ACCESS-TOKEN",
                status.FORBIDDEN,
                {"Authentication": "invalid access_token"},
            )

        return f(current_user, *args, **kwargs)

    return decorator