"""
Defines the database models for experiments and process variables.
"""

from flask import url_for
from rtp_backend import db

users_to_experiments = db.Table(
    "users_to_experiments",
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id"), primary_key=True),
    db.Column(
        "experiment_short_id",
        db.Integer,
        db.ForeignKey("experiment.short_id"),
        primary_key=True,
    ),
)


class ProcessVariable(db.Model):
    """This database model is often abbreviated as "PV".
    A "ProcessVariable" always belongs to an "Experiment".

    Args:
        db (SQLAlchemy): The database of the flask app.
    """

    # The pv_string defines the PV.
    # We also used it to generate the short_id of the associated experiment.
    pv_string = db.Column(db.String(100), primary_key=True)

    # You can give the pv a human-readable name,
    # which can be displayed in the user interface
    # for easier differentiation of the experiments by the user.
    human_readable_name = db.Column(db.String(100), nullable=True)

    # Each PV can be assigned to only one experiment.
    # The associated experiment is defined by this short_id,
    # which is also located at the beginning of the pv_string.
    experiment_short_id = db.Column(
        db.String(100), db.ForeignKey("experiment.short_id"), nullable=False
    )

    available_for_mqtt_publish = db.Column(db.Boolean, default=False, nullable=False)

    default_threshold_min = db.Column(db.String(100), nullable=True)
    default_threshold_max = db.Column(db.String(100), nullable=True)

    def __repr__(self) -> str:
        return self.pv_string

    def to_dict(self) -> dict:
        """This method a dictionary with the keys and values of the database model.

        Returns:
            dict: Dictionary with the keys and values of the database model.
        """

        return {
            "pv_string": self.pv_string,
            "human_readable_name": self.human_readable_name,
            "experiment_short_id": self.experiment_short_id,
            "available_for_mqtt_publish": self.available_for_mqtt_publish,
            "default_threshold_min": self.default_threshold_min,
            "default_threshold_max": self.default_threshold_max,
        }


class Experiment(db.Model):
    """This class defines the database model for the experiments.
    This model uses the models "User" and "ProcessVariable".

    Args:
        db (SQLAlchemy): The database of the flask app.
    """

    # Each experiment has a short_id as primary_key.
    # This is generated via the pv_strings of the process variables of an experiment.
    short_id = db.Column(db.String(100), primary_key=True)

    # You can give the experiment a human-readable name,
    # which can be displayed in the user interface
    # for easier differentiation of the experiments by the user.
    human_readable_name = db.Column(db.String(100), nullable=True)

    # An experiment can contain several process variables.
    # These are defined via the "ProcessVariable" database model.
    process_variables = db.relationship(
        "ProcessVariable", backref="experiment", lazy=True
    )

    # Administrators can assign Users to experiments.
    # This allows them to query the data of the PVs of the experiment.
    users = db.relationship(
        "User",
        secondary=users_to_experiments,
        lazy="subquery",
        backref=db.backref("experiments", lazy=True),
    )

    def __rep__(self):
        return self.short_id

    def to_dict(self, include_user_ids=False) -> dict:
        """This method a dictionary with the keys and values of the database model.

        Args:
            include_user_ids (bool, optional): If True, dict contains user_ids. Defaults to False.

        Returns:
            dict: Dictionary with the keys and values of the database model.
        """

        experiment_data_dictionary = {
            "short_id": self.short_id,
            "human_readable_name": self.human_readable_name,
            "process_variable_urls": [
                url_for("experiments.pv", pv_string=pv.pv_string)
                for pv in self.process_variables
            ],
        }

        # Should only be accessed by admins.
        if include_user_ids is True:
            if self.users == None:
                experiment_data_dictionary["user_urls"] = []
            else:
                experiment_data_dictionary["user_urls"] = [
                    url_for("auth.user", user_id=user.user_id) for user in self.users
                ]

        return experiment_data_dictionary
