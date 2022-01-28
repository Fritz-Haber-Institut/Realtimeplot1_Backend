from flask import Blueprint, Response, current_app, make_response, request

from rtp_backend.apps.auth.decorators import token_required
from rtp_backend.apps.auth.models import UserTypeEnum
from rtp_backend.apps.experiments.helper_functions import (
    return_experiment_if_user_in_experiment,
)
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.generic_responses import forbidden_because_not_an_admin
from rtp_backend.apps.utilities.user_created_data import get_request_dict

from .helper_functions import get_data_for_experiment

experiment_pv_data_blueprint = Blueprint(
    "experiment_pv_data",
    __name__,
    template_folder="experiment_pv_data/",
)


@experiment_pv_data_blueprint.route("/<experiment_short_id>", methods=["POST"])
@token_required
def data(current_user, experiment_short_id):
    experiment = return_experiment_if_user_in_experiment(
        experiment_short_id, current_user
    )
    if isinstance(experiment, Response):
        return experiment

    if request.method == "POST":
        data = get_request_dict()
        warnings = []

        since = until = None
        if type(data) != Response:
            since = data.get("since")
            until = data.get("until")
        else:
            warnings.append(
                f'Time frame not specified. The data is in a server-defined time frame of {current_app.config["DEFAULT_ARCHIVER_TIME_PERIOD"]} hours up to the current time.'
            )

        experiment_data = get_data_for_experiment(experiment, since, until)

    if isinstance(experiment_data, Response):
        return experiment_data

    return make_response(
        {"data": experiment_data, "warnings": warnings},
        status.OK,
    )


@experiment_pv_data_blueprint.route("/validate_pv_string/<pv_string>", methods=["GET"])
@token_required
def validate_pv(current_user, pv_string):
    if current_user.user_type != UserTypeEnum.admin:
        return forbidden_because_not_an_admin()

    pv_string_exists = get_data_for_experiment(
        process_variable=pv_string, only_validate=True
    )

    return make_response(
        {"pv_string_exists": pv_string_exists},
        status.OK,
    )
