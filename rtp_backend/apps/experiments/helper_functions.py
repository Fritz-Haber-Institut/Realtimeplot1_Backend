"""
Contains functions that make the Experiment model
and the ProcessVariable model more accessible to other modules.
"""

import rtp_backend.apps.utilities.http_status_codes as status
from flask import make_response
from rtp_backend.apps.auth.helper_functions import is_admin
from rtp_backend.apps.auth.models import User

from .models import Experiment, db


def return_experiment_if_user_in_experiment(experiment_short_id, user):
    experiment = Experiment.query.filter_by(short_id=experiment_short_id).first()
    if not experiment:
        return respond_with_404("experiment", experiment_short_id)

    experiment_users = experiment.users
    if not user in experiment_users or not experiment_users:
        return make_response(
            {
                "errors": [
                    "Only users that are assigned to the experiment can access it."
                ]
            },
            status.FORBIDDEN,
        )

    return experiment


def get_experiment_short_id_from_pv_string(pv_string: str) -> str or None:
    """This function extracts the short_id of an experiment from a pv_string.

    Args:
        pv_string (str): pv_string from which the short_id is to be taken.

    Returns:
        str or None: Returns the short_id or None if it is not found.
    """

    if pv_string is None:
        return None

    pv_string_data = pv_string.split(":")

    if len(pv_string_data) > 0:
        return pv_string_data[0]

    return None


def pv_string_to_experiment(pv_string: str) -> Experiment:
    """This function searches for an experiment for a pv_string.
    If it does not exist, this function creates it.

    Args:
        pv_string (str): which contains the short_id of the experiment.

    Returns:
        Experiment: found or newly created experiment.
    """

    experiment_short_id = get_experiment_short_id_from_pv_string(pv_string)
    if experiment_short_id is None:
        return make_response(
            "COULD NOT FIND EXPERIMENT_SHORT_ID IN PV_STRING",
            status.BAD_REQUEST,
        )

    # check for existing Experiment
    experiment_in_database = Experiment.query.filter_by(
        short_id=experiment_short_id
    ).first()

    # create one if none
    if not experiment_in_database:
        experiment_in_database = Experiment(short_id=experiment_short_id)

        db.session.add(experiment_in_database)

    return experiment_in_database


def get_experiment_dict(
    requesting_user: User, experiment_to_return: Experiment
) -> dict:
    """Returns the experiment as dict depending on the user_type.
    user_ids are only returned if the user is an admin.

    Args:
        requesting_user (User): The user requesting the data.
        experiment_to_return (Experiment): The experiment to return.

    Returns:
        dict: A dictionary with the data of the experiment.
    """
    if is_admin(requesting_user):
        return experiment_to_return.to_dict(include_user_ids=True)
    return experiment_to_return.to_dict(include_user_ids=False)
