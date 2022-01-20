import enum
import uuid

from flask import url_for
from rtp_backend import db
from rtp_backend.apps.experiments.models import Experiment


class UserTypeEnum(enum.Enum):
    admin = "Admin"
    user = "User"


class User(db.Model):
    user_id = db.Column(
        "user_id",
        db.Text(length=36),
        default=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    login_name = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100), unique=False, nullable=False)
    last_name = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=False, nullable=True)
    password_hash = db.Column(db.String(100), unique=False, nullable=False)
    user_type = db.Column(
        db.Enum(UserTypeEnum), default=UserTypeEnum.user, nullable=False
    )
    preferred_language = db.Column(db.String(10), nullable=True, default="en")

    def __repr__(self) -> str:
        return f"<{self.user_type}: {self.first_name} {self.last_name}>"

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "login_name": self.login_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "user_type": self.user_type.value,
            "preferred_language": self.preferred_language,
            "experiment_urls": [
                url_for(
                    "experiments.experiment", experiment_short_id=experiment.short_id
                )
                for experiment in self.experiments
            ],
            "url": url_for("auth.user", user_id=self.user_id),
        }
