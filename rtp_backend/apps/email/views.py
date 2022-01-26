from socket import gaierror

import bleach  # pip install bleach
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
from sqlalchemy import exc

from .models import Subscription

email_blueprint = Blueprint("email", __name__)


@email_blueprint.route("/subscribe/<pv_string>", methods=["POST"])
@token_required
def subscribe_to_pv(current_user, pv_string):
    data = get_request_dict()
    if type(data) == Response:
        return data

    pv_string = bleach.clean(pv_string)
    if not ProcessVariable.query.filter_by(pv_string=pv_string).first():
        return respond_with_404("process variable", pv_string)

    errors = []

    email = data.get("email")
    if not email:
        errors.append(["email: Missing email."])

    threshold_min = data.get("threshold_min")
    if not email:
        errors.append(["threshold_min: Missing threshold_min."])

    threshold_max = data.get("threshold_max")
    if not email:
        errors.append(["threshold_max: Missing threshold_max."])

    if (
        Subscription.query.filter_by(
            user_id=current_user.user_id, pv_string=pv_string
        ).count()
        >= 1
    ):
        return already_exists_in_database(
            "subscription", f"user_id={current_user.user_id},pv_string={pv_string}"
        )

    message = f"Hello {current_user.first_name} {current_user.last_name}.\nPlease check the {pv_string} process variable! A threshold value has been breached."
    try:
        new_subscription = Subscription(
            user_id=current_user.user_id,
            email=email,
            pv_string=pv_string,
            threshold_min=threshold_min,
            threshold_max=threshold_max,
        )
        db.session.add(new_subscription)
        db.session.commit()

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

        mqtt_channel = current_app.config("EMAIL_MQTT_CHANNEL")
        threshold_unit = current_app.config("THRESHOLD_UNIT")

        client.publish(
            mqtt_channel,
            {
                "email": email,
                "pv": pv_string,
                "min_threshold": threshold_min,
                "max_threshold": threshold_max,
                "threshold_unit": threshold_unit,
                "active": 1,
                "message": message,
            },
        )
        client.disconnect()

        return {"subscription": new_subscription.to_dict()}

    except exc.IntegrityError:
        db.session.rollback()
        return make_response({"errors": errors}, status.BAD_REQUEST)


@email_blueprint.route("/unsubscribe/<pv_string>", methods=["DELETE"])
@token_required
def unsubscribe_from_pv(current_user, pv_string):

    subscription = Subscription.query.filter_by(
        user_id=current_user.user_id, pv_string=pv_string
    ).first()
    if not pv:
        return respond_with_404(
            "subscription", f"user_id={current_user.user_id},pv_string={pv_string}"
        )

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

        mqtt_channel = current_app.config("EMAIL_MQTT_CHANNEL")
        threshold_unit = current_app.config("THRESHOLD_UNIT")
        message = f"Hello {current_user.first_name} {current_user.last_name}.\nPlease check the {pv_string} process variable! A threshold value has been breached."

        client.publish(
            mqtt_channel,
            {
                "email": subscription.email,
                "pv": pv_string,
                "min_threshold": subscription.threshold_min,
                "max_threshold": subscription.threshold_max,
                "threshold_unit": threshold_unit,
                "active": 0,
                "message": message,
            },
        )
        client.disconnect()

        db.session.delete(subscription)
        db.session.commit()

    return {
        "message": f"Successfully deleted subscription (user_id={current_user.user_id},pv_string={pv_string})"
    }
