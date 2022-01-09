"""
Contains functions that make the Experiment model
and the ProcessVariable model more accessible to other modules.
"""

import rtp_backend.apps.utilities.http_status_codes as status
from flask import make_response

from .models import Experiment, db


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
