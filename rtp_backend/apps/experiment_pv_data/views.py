from flask import Blueprint, Response, jsonify, make_response, request
from rtp_backend.apps.auth.decorators import token_required
from rtp_backend.apps.auth.helper_functions import is_admin
from rtp_backend.apps.auth.models import User, UserTypeEnum
from rtp_backend.apps.experiments.helper_functions import (
    get_experiment_dict,
    get_experiment_short_id_from_pv_string,
    pv_string_to_experiment,
)
from rtp_backend.apps.experiments.models import Experiment, ProcessVariable, db
from rtp_backend.apps.experiments.views import experiment
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.generic_responses import (
    already_exists_in_database,
    forbidden_because_not_an_admin,
    respond_with_404,
)
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
    experiment = Experiment.query.filter_by(short_id=experiment_short_id).first()
    if not experiment:
        respond_with_404("experiment", "experiment_short_id")

    experiment_user_ids = experiment.user_ids
    if not current_user.user_id in experiment_user_ids or not experiment_user_ids:
        make_response(
            {"errors": "Only User that are allocated to experiment"}, status.FORBIDDEN
        )

    if request.method == "POST":
        data = get_request_dict()
        if type(data) == Response:
            return data

        data = data.get("experiment_data")
        if not data:
            return make_response(
                jsonify({"errors": [{"experiment_data": "Experiment was not found."}]}),
                status.BAD_REQUEST,
            )

        since = data.get("since")
        until = data.get("until")

        experiment_data = get_data_for_experiment(experiment, since, until)

        if experiment_data is None:
            return respond_with_404("experiment", experiment, since, until)

    if isinstance(experiment_data, Response):
        return experiment_data

    return make_response(
        {"data": experiment_data},
        status.OK,
    )
