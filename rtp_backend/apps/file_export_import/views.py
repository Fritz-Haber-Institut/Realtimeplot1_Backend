import io
import json
import time
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
    pv_string_to_experiment,
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

SEMICOLON_PLACEHOLDER = "&SMKL&"


def dict_to_csv(input_dict: dict, ignore_lists: bool = True):
    output_string = ""
    for key in input_dict:
        value = input_dict[key]
        if ignore_lists and isinstance(value, list):
            pass
        else:
            if output_string != "":
                output_string += ";"
            output_string += f"{key}={value}".replace(";", SEMICOLON_PLACEHOLDER)
    return output_string


@file_blueprint.route("/export", methods=["GET"])
@token_required
def export_file(current_user):
    if current_user.user_type != UserTypeEnum.admin:
        return forbidden_because_not_an_admin()

    lines = [
        "################################################",
        "#               rtpserver-export               #",
        "################################################\n",
        "# This file contains importable database entries of experiments and process variables.",
        "# Attention! This file was computer generated and will be read automatically. Format-changing adjustments can cause the import to fail or lead to a misconfigured server.\n",
    ]

    proxy = io.StringIO()
    experiments = Experiment.query.all()

    for experiment in experiments:
        lines.append(f"[EXPERIMENT];{dict_to_csv(experiment.to_dict())}")
        process_variables = experiment.process_variables
        for process_variable in process_variables:
            lines.append(
                f"    [PROCESS_VARIABLE];{dict_to_csv(process_variable.to_dict())}"
            )
        lines.append("")

    proxy = io.StringIO()

    for line in lines:
        proxy.write(f"{line}\n")

    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode())
    mem.seek(0)
    proxy.close()

    timestr = time.strftime("%Y%m%d-%H%M%S")

    return send_file(
        mem,
        as_attachment=True,
        attachment_filename=f"{timestr}-rtpserver-export.txt",
        mimetype="text/plain",
    )


def split_csv(line):
    return [
        attribute.replace(SEMICOLON_PLACEHOLDER, ";") for attribute in line.split(";")
    ]


def create_pv_from_csv(line, experiment_human_readable_name):
    attributes = split_csv(line)

    attributes_dict = {
        "human_readable_name": None,
        "default_threshold_max": None,
        "default_threshold_min": None,
    }
    for attribute in attributes:
        if attribute.startswith("pv_string="):
            attribute = attribute.replace("pv_string=", "")
            attributes_dict["pv_string"] = attribute

        elif attribute.startswith("human_readable_name="):
            attribute = attribute.replace("human_readable_name=", "")
            attributes_dict["human_readable_name"] = attribute

        elif attribute.startswith("available_for_mqtt_publish="):
            attribute = attribute.replace("available_for_mqtt_publish=", "")
            attributes_dict["available_for_mqtt_publish"] = bool(attribute)

        elif attribute.startswith("default_threshold_min="):
            attribute = attribute.replace("default_threshold_min=", "")
            try:
                attributes_dict["default_threshold_min"] = int(attribute)
            except ValueError:
                pass

        elif attribute.startswith("default_threshold_max="):
            attribute = attribute.replace("default_threshold_max=", "")
            try:
                attributes_dict["default_threshold_max"] = int(attribute)
            except ValueError:
                pass

    pv = ProcessVariable.query.filter_by(pv_string=attributes_dict["pv_string"]).first()
    if not pv:

        pv = ProcessVariable(
            pv_string=attributes_dict["pv_string"],
            experiment_short_id=get_experiment_short_id_from_pv_string(
                attributes_dict["pv_string"]
            ),
            human_readable_name=attributes_dict["human_readable_name"],
            default_threshold_max=attributes_dict["default_threshold_max"],
            default_threshold_min=attributes_dict["default_threshold_min"],
            available_for_mqtt_publish=attributes_dict["available_for_mqtt_publish"],
        )

        db.session.add(pv)
    else:
        pv.pv_string = attributes_dict["pv_string"]
        pv.experiment_short_id = get_experiment_short_id_from_pv_string(
            attributes_dict["pv_string"]
        )
        pv.human_readable_name = attributes_dict["human_readable_name"]
        pv.default_threshold_max = attributes_dict["default_threshold_max"]
        pv.default_threshold_min = attributes_dict["default_threshold_min"]
        pv.available_for_mqtt_publish = attributes_dict["available_for_mqtt_publish"]

    experiment = pv_string_to_experiment(pv.pv_string)
    if (
        experiment_human_readable_name
        and experiment
        and not experiment.human_readable_name
    ):
        experiment.human_readable_name = experiment_human_readable_name

    db.session.commit()


@file_blueprint.route("/import", methods=["GET"])
@token_required
def import_file(current_user):
    if current_user.user_type != UserTypeEnum.admin:
        return forbidden_because_not_an_admin()

    data = request.data
    if not data:
        return make_response({"errors": ["No data"]}, status.BAD_REQUEST)

    data = data.decode("utf-8")
    lines = data.split("\n")

    last_experiment_human_readable_name = None

    for line in lines:
        line = line.strip()
        line = bleach.clean(line)

        if line.startswith("[EXPERIMENT]"):
            attributes = split_csv(line)
            for attribute in attributes:
                if attribute.startswith("human_readable_name"):
                    attribute.replace("human_readable_name=", "")
                    last_experiment_human_readable_name = attribute
        elif line.startswith("[PROCESS_VARIABLE]"):
            create_pv_from_csv(line, last_experiment_human_readable_name)

    return {"messages": ["Successful"]}
