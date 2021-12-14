from flask import Blueprint

from .models import User, db

auth_blueprint = Blueprint(
    "entries",
    __name__,
    template_folder="auth/",
)
