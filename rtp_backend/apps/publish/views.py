from socket import gaierror

import paho.mqtt.client as mqtt  # pip install paho-mqtt
from flask import Blueprint, Response, current_app, jsonify, make_response, request
from rtp_backend.apps.auth.decorators import token_required
from rtp_backend.apps.auth.helper_functions import is_admin
from rtp_backend.apps.auth.models import User, UserTypeEnum
from rtp_backend.apps.experiments.models import Experiment, ProcessVariable, db
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.generic_responses import (
    already_exists_in_database,
    forbidden_because_not_an_admin,
    respond_with_404,
)
from rtp_backend.apps.utilities.user_created_data import get_request_dict

from .helper_functions import pv_string_to_mqtt_channel

publish_blueprint = Blueprint("publish", __name__)


@publish_blueprint.route("/<pv_string>", methods=["POST"])
@token_required
def publish(current_user, pv_string, value="20"):
    client = mqtt.Client()

    try:
        client.connect(current_app.config["MQTT_SERVER_URL"])
    except gaierror:
        return make_response(
            {
                "errors": [
                    "The MQTT server to which this request should be forwarded cannot be reached."
                ]
            },
            status.BAD_GATEWAY,
        )

    mqtt_channel = pv_string_to_mqtt_channel(pv_string)
    if mqtt_channel:
        client.publish(mqtt_channel, value)
    else:
        make_response("ERROR", 500)
    client.disconnect()

    return make_response("OK", 200)
