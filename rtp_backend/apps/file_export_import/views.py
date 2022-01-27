import io
import json
from socket import gaierror

import bleach  # pip install bleach
import paho.mqtt.client as mqtt  # pip install paho-mqtt
from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    make_response,
    request,
    send_file,
)
from rtp_backend.apps.auth.decorators import token_required
from rtp_backend.apps.auth.helper_functions import is_admin
from rtp_backend.apps.auth.models import User, UserTypeEnum
from rtp_backend.apps.experiments.helper_functions import (
    get_experiment_short_id_from_pv_string,
    return_experiment_if_user_in_experiment,
)
from rtp_backend.apps.experiments.models import Experiment, ProcessVariable, db
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.generic_responses import (
    already_exists_in_database,
    forbidden_because_not_an_admin,
    mqtt_server_cannot_be_reached,
    respond_with_404,
)
from rtp_backend.apps.utilities.user_created_data import (
    get_data_value_or_none,
    get_request_dict,
)
from sqlalchemy import exc

file_blueprint = Blueprint("file", __name__)


def dict_to_csv(input_dict: dict, ignore_lists: bool = True):
    output_string = ""
    for key in input_dict:
        value = input_dict[key]
        if ignore_lists and isinstance(value, list):
            pass
        else:
            if output_string != "":
                output_string += ";"
            output_string += f"{key}={value}"
    return output_string


@file_blueprint.route("/export", methods=["GET"])
@token_required
def export_file(current_user):

    lines = []
    proxy = io.StringIO()
    experiments = Experiment.query.all()

    for experiment in experiments:
        lines.append(f"[EXPERIMENT];{dict_to_csv(experiment.to_dict())}")
        process_variables = experiment.process_variables
        for process_variable in process_variables:
            lines.append(
                f"[PROCESS_VARIABLE];{dict_to_csv(process_variable.to_dict())}"
            )

    proxy = io.StringIO()

    for line in lines:
        proxy.write(f"{line}\n")

    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode())
    mem.seek(0)
    proxy.close()

    return send_file(
        mem,
        as_attachment=True,
        attachment_filename="rtp_db_data.txt",
        mimetype="text/plain",
    )


@file_blueprint.route("/import", methods=["GET"])
@token_required
def import_file(current_user):
    return ""
