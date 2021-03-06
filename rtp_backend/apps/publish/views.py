from socket import gaierror

import paho.mqtt.client as mqtt  # pip install paho-mqtt
from flask import Blueprint, Response, current_app, make_response

from rtp_backend.apps.auth.decorators import token_required
from rtp_backend.apps.experiments.models import Experiment, ProcessVariable
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.generic_responses import (
    mqtt_server_cannot_be_reached,
    respond_with_404,
)
from rtp_backend.apps.utilities.user_created_data import get_request_dict

from .helper_functions import pv_string_to_mqtt_channel

publish_blueprint = Blueprint("publish", __name__)


@publish_blueprint.route("/<pv_string>", methods=["PUT"])
@token_required
def publish(current_user, pv_string):
    data = get_request_dict()
    if type(data) == Response:
        return data

    value = data.get("value")
    if not value:
        return make_response(
            {"errors": ["The value to be set must be supplied in the JSON body."]},
            status.BAD_REQUEST,
        )

    pv = ProcessVariable.query.filter_by(pv_string=pv_string).first()
    if not pv:
        return respond_with_404("process variable", pv_string)

    experiment_short_id = pv.experiment_short_id
    experiment = Experiment.query.filter_by(short_id=experiment_short_id).first()
    if not experiment:
        respond_with_404("experiment", experiment_short_id)

    experiment_users = experiment.users
    if not current_user in experiment_users or not experiment_users:
        return make_response(
            {
                "errors": [
                    "Process variable data can only be overwritten by users assigned to the associated experiment."
                ]
            },
            status.FORBIDDEN,
        )

    if pv.available_for_mqtt_publish == False:
        return make_response(
            {
                "errors": [
                    "The requested process variable does not accept user-set values."
                ]
            },
            status.NOT_ACCEPTABLE,
        )

    client = mqtt.Client()

    try:
        client.connect(current_app.config["MQTT_SERVER_URL"])
    except gaierror:
        return mqtt_server_cannot_be_reached()

    mqtt_channel = pv_string_to_mqtt_channel(pv_string)
    client.publish(mqtt_channel, value)
    client.disconnect()

    return make_response(
        {
            "messages": [
                "Your request has been sent to the MQTT server. It may take a while for the changes to take effect."
            ]
        },
        status.OK,
    )
