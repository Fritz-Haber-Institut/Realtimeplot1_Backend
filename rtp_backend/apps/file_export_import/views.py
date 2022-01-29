import io
import time

import bleach  # pip install bleach
import paho.mqtt.client as mqtt  # pip install paho-mqtt
from flask import Blueprint, make_response, request, send_file

from rtp_backend.apps.auth.decorators import token_required
from rtp_backend.apps.auth.models import UserTypeEnum
from rtp_backend.apps.experiments.helper_functions import (
    get_experiment_short_id_from_pv_string,
    pv_string_to_experiment,
)
from rtp_backend.apps.experiments.models import Experiment, ProcessVariable, db
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.generic_responses import forbidden_because_not_an_admin

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
        attachment_filename=f"{timestr}-rtpserver-export.rtpdb",
        mimetype="text/plain",
    )


def split_csv(line):
    return [
        attribute.replace(SEMICOLON_PLACEHOLDER, ";") for attribute in line.split(";")
    ]


def create_pv_from_csv(line, experiment_human_readable_name):
    attributes = split_csv(line)

    attributes_dict = {}
    for attribute in attributes:
        if attribute.startswith("pv_string="):
            attribute = attribute.replace("pv_string=", "")
            attributes_dict["pv_string"] = attribute

        elif attribute.startswith("human_readable_name="):
            attribute = attribute.replace("human_readable_name=", "")
            attributes_dict["human_readable_name"] = attribute

        elif attribute.startswith("available_for_mqtt_publish="):
            attribute = attribute.replace("available_for_mqtt_publish=", "")
            if attribute.lower() == "true":
                attributes_dict["available_for_mqtt_publish"] = True
            else:
                attributes_dict["available_for_mqtt_publish"] = False

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
        )

        db.session.add(pv)

    if "human_readable_name" in attributes_dict:
        pv.human_readable_name = attributes_dict["human_readable_name"]

    if "default_threshold_max" in attributes_dict:
        pv.default_threshold_max = attributes_dict["default_threshold_max"]

    if "default_threshold_min" in attributes_dict:
        pv.default_threshold_min = attributes_dict["default_threshold_min"]

    if "available_for_mqtt_publish" in attributes_dict:
        pv.available_for_mqtt_publish = attributes_dict["available_for_mqtt_publish"]

    experiment = pv_string_to_experiment(pv.pv_string)
    if (
        experiment_human_readable_name
        and experiment
        and not experiment.human_readable_name
    ):
        experiment.human_readable_name = experiment_human_readable_name

    db.session.commit()


@file_blueprint.route("/import", methods=["POST"])
@token_required
def import_file(current_user):
    if current_user.user_type != UserTypeEnum.admin:
        return forbidden_because_not_an_admin()

    data = request.data
    if not data:
        return make_response(
            {"errors": ["No data found. Nothing could be imported."]},
            status.BAD_REQUEST,
        )

    number_of_experiments_found_in_file = 0
    number_of_process_variables_found_in_file = 0

    data = data.decode("utf-8")
    lines = data.split("\n")

    last_experiment_human_readable_name = None
    errors = []

    for index, line in enumerate(lines):
        line = line.strip()
        line = bleach.clean(line)

        if line.startswith("[EXPERIMENT]"):
            number_of_experiments_found_in_file += 1
            attributes = split_csv(line)
            for attribute in attributes:
                if attribute.startswith("human_readable_name"):
                    attribute = attribute.replace("human_readable_name=", "")
                    last_experiment_human_readable_name = attribute
        elif line.startswith("[PROCESS_VARIABLE]"):
            number_of_process_variables_found_in_file += 1
            try:
                create_pv_from_csv(line, last_experiment_human_readable_name)
            except:
                errors.append(
                    f"line-{index + 1}: An error occurred while creating the process variable. Check if the pv_string and the other attributes are set correctly, and start the import again. Valid process variables are not affected."
                )

    number_of_experiments_now_in_database = Experiment.query.count()
    number_of_process_variables_now_in_database = ProcessVariable.query.count()
    return {
        "messages": [
            "Import complete. Please check the number of entries found, compare them with the number in the database, and consult the error messages if necessary!"
        ],
        "errors": errors,
        "number_of_experiments_found_in_file": number_of_experiments_found_in_file,
        "number_of_process_variables_found_in_file": number_of_process_variables_found_in_file,
        "number_of_experiments_now_in_database": number_of_experiments_now_in_database,
        "number_of_process_variables_now_in_database": number_of_process_variables_now_in_database,
    }
