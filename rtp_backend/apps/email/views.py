import json
from socket import gaierror

import bleach  # pip install bleach
import paho.mqtt.client as mqtt  # pip install paho-mqtt
from flask import Blueprint, Response, current_app, jsonify, make_response, request
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

from .models import Subscription

email_blueprint = Blueprint("email", __name__)


@email_blueprint.route("/subscriptions", methods=["GET"])
@email_blueprint.route("/subscriptions/<pv_string>", methods=["GET"])
@token_required
def subscriptions(current_user, pv_string=None):
    subscriptions = []
    if pv_string:
        subscriptions = Subscription.query.filter_by(
            user_id=current_user.user_id, pv_string=pv_string
        ).all()
    else:
        subscriptions = Subscription.query.filter_by(user_id=current_user.user_id).all()

    subscriptions_list = []
    for subscription in subscriptions:
        subscriptions_list.append(subscription.to_dict())

    return {"subscriptions": subscriptions_list}


@email_blueprint.route("/subscribe/<pv_string>", methods=["POST"])
@token_required
def subscribe_to_pv(current_user, pv_string):
    experiment = return_experiment_if_user_in_experiment(
        get_experiment_short_id_from_pv_string(pv_string), current_user
    )
    if isinstance(experiment, Response):
        return experiment

    data = get_request_dict()

    pv_string = bleach.clean(pv_string)
    pv = ProcessVariable.query.filter_by(pv_string=pv_string).first()
    if not pv:
        return respond_with_404("process variable", pv_string)

    if (
        Subscription.query.filter_by(
            user_id=current_user.user_id, pv_string=pv_string
        ).count()
        >= 1
    ):
        return already_exists_in_database(
            "subscription", f"user_id={current_user.user_id},pv_string={pv_string}"
        )

    errors = []

    email = get_data_value_or_none(data, "email")
    if not email:
        email = current_user.email
    if not email:
        errors.append(["email: Missing email."])

    threshold_min = get_data_value_or_none(data, "threshold_min")
    if not threshold_min:
        threshold_max = pv.default_threshold_max
    if not threshold_min:
        errors.append(["threshold_min: Missing threshold_min."])

    threshold_max = get_data_value_or_none(data, "threshold_max")
    if not threshold_max:
        threshold_max = pv.default_threshold_max
    if not threshold_max:
        errors.append(["threshold_max: Missing threshold_max."])

    message = f"Hello {current_user.first_name} {current_user.last_name}.\nPlease check the {pv_string} process variable! A threshold value has been breached."
    try:
        new_subscription = Subscription(
            user_id=current_user.user_id,
            email=email,
            pv_string=pv_string,
            threshold_min=int(threshold_min),
            threshold_max=int(threshold_max),
        )
        db.session.add(new_subscription)
        db.session.commit()

        client = mqtt.Client()

        client.connect(current_app.config["MQTT_SERVER_URL"])

        mqtt_channel = f"/{current_app.config['MQTT_CHANNEL_PREFIX']}/{current_app.config['EMAIL_MQTT_CHANNEL']}"
        threshold_unit = current_app.config["THRESHOLD_UNIT"]

        client.publish(
            mqtt_channel,
            json.dumps(
                {
                    "email": email,
                    "pv": pv_string,
                    "min_threshold": threshold_min,
                    "max_threshold": threshold_max,
                    "threshold_unit": threshold_unit,
                    "active": 1,
                    "message": message,
                },
            ),
        )
        client.disconnect()

        return {"subscription": new_subscription.to_dict()}

    except (exc.IntegrityError, TypeError):
        db.session.rollback()
        return make_response({"errors": errors}, status.BAD_REQUEST)
    except ValueError:
        return make_response(
            {"errors": ["threshold_min and threshold_max must be integers."]},
            status.BAD_REQUEST,
        )
    except gaierror:
        return mqtt_server_cannot_be_reached()


@email_blueprint.route("/unsubscribe/<pv_string>", methods=["DELETE"])
@token_required
def unsubscribe_from_pv(current_user, pv_string):
    data = get_request_dict()
    if type(data) == Response:
        return data

    email = data.get("email")
    if not email:
        make_response(
            {"errors": "The email used for the subscription must be specified."},
            status.BAD_REQUEST,
        )

    subscription = Subscription.query.filter_by(
        user_id=current_user.user_id, pv_string=pv_string, email=email
    ).first()
    if not subscription:
        return respond_with_404(
            "subscription", f"user_id={current_user.user_id},pv_string={pv_string}"
        )

    client = mqtt.Client()

    try:
        client.connect(current_app.config["MQTT_SERVER_URL"])
    except gaierror:
        return mqtt_server_cannot_be_reached()

    mqtt_channel = f"/{current_app.config['MQTT_CHANNEL_PREFIX']}/{current_app.config['EMAIL_MQTT_CHANNEL']}"
    threshold_unit = current_app.config["THRESHOLD_UNIT"]
    message = f"Hello {current_user.first_name} {current_user.last_name}.\nPlease check the {pv_string} process variable! A threshold value has been breached."

    client.publish(
        mqtt_channel,
        json.dumps(
            {
                "email": subscription.email,
                "pv": pv_string,
                "min_threshold": subscription.threshold_min,
                "max_threshold": subscription.threshold_max,
                "threshold_unit": threshold_unit,
                "active": 0,
                "message": message,
            }
        ),
    )
    client.disconnect()

    db.session.delete(subscription)
    db.session.commit()

    return {
        "message": f"Successfully deleted subscription (user_id={current_user.user_id},pv_string={pv_string})"
    }
