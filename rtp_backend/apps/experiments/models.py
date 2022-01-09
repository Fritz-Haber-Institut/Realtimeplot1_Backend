"""
Defines the database models for experiments and process variables.
"""

from rtp_backend import db


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
    user_ids = db.Column(db.Text(length=36), db.ForeignKey("user.user_id"))
    
    def __rep__(self):
        return self.short_id

    def to_dict(self, include_user_ids=False) -> dict:
        """This method a dictionary with the keys and values of the database model.

        Args:
            include_user_ids (bool, optional): If True, dict contains user_ids. Defaults to False.

        Returns:
            dict: Dictionary with the keys and values of the database model.
        """

        process_variables = []
        for process_variable in self.process_variables:
            process_variables.append(process_variable.pv_string)

        experiment_data_dictionary = {
            "short_id": self.short_id,
            "human_readable_name": self.human_readable_name,
            "process_variables": process_variables,
        }

        # Should only be accessed by admins.
        if include_user_ids is True:
            experiment_data_dictionary["user_ids"] = self.user_ids

        return experiment_data_dictionary
