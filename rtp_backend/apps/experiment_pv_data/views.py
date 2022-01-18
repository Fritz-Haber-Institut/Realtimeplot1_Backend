from flask import Blueprint, Response, jsonify, make_response, request
from rtp_backend.apps.auth.decorators import token_required
from rtp_backend.apps.auth.helper_functions import is_admin
from rtp_backend.apps.auth.models import User, UserTypeEnum
from rtp_backend.apps.experiments.views import experiment
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.generic_responses import (
    already_exists_in_database,
    forbidden_because_not_an_admin,
    respond_with_404,
)
from rtp_backend.apps.utilities.user_created_data import get_request_dict

from rtp_backend.apps.experiments.helper_functions import (
    get_experiment_dict,
    pv_string_to_experiment,
    get_experiment_short_id_from_pv_string
)
from rtp_backend.apps.experiments.models import Experiment, ProcessVariable, db
from .helper_functions import get_data_for_experiment

experiments_blueprint = Blueprint(
    "experiment_pv_data",
    __name__,
    template_folder="experiment_pv_data/",
)

@experiments_blueprint.route("/data/<experiment_short_id>", methods=["GET"])
@token_required
def data(current_user, experiment_short_id):
    experiment = Experiment.query.filter_by(short_id=experiment_short_id).all()
    if not experiment:
        respond_with_404("experiment", "experiment_short_id")

    experiment_user_ids = experiment.user_ids
    if not current_user.user_id in experiment_user_ids:
        make_response(
            {"errors": "Only User ....."},
            status.FORBIDDEN
        )

    if request.method == "GET":
        data = get_data_for_experiment(experiment)

        if isinstance(data, Response):
            return data

        return make_response(
            {"data": data},
            status.OK,
        )