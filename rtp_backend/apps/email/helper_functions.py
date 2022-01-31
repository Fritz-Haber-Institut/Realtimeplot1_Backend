import paho.mqtt.client as mqtt  # pip install paho-mqtt
from flask import current_app

from rtp_backend.apps.auth.models import User

from .models import Subscription, db


def unsubscribe_on_mqtt_server(subscription):
    client = mqtt.Client()

    try:
        client.connect(current_app.config["MQTT_SERVER_URL"])

        user = User.query.filter_by(user_id=subscription.user_id)

        mqtt_channel = current_app.config["EMAIL_MQTT_CHANNEL"]
        threshold_unit = current_app.config["THRESHOLD_UNIT"]
        message = f"Hello {user.first_name} {user.last_name}.\nPlease check the {subscription.pv_string} process variable! A threshold value has been breached."

        client.publish(
            mqtt_channel,
            json.dumps(
                {
                    "email": subscription.email,
                    "pv": subscription.pv_string,
                    "min_threshold": subscription.threshold_min,
                    "max_threshold": subscription.threshold_max,
                    "threshold_unit": threshold_unit,
                    "active": 0,
                    "message": message,
                }
            ),
        )
        client.disconnect()

    except:
        pass


def delete_subscriptions(user_id=None, pv_string=None):
    subscriptions = []
    if user_id and pv_string:
        subscriptions = Subscription.query.filter_by(
            user_id=user_id, pv_string=pv_string
        ).all()
    elif user_id:
        subscriptions = Subscription.query.filter_by(user_id=user_id).all()
    elif pv_string:
        subscriptions = Subscription.query.filter_by(pv_string=pv_string).all()

    for subscription in subscriptions:
        unsubscribe_on_mqtt_server(subscription)
        db.session.delete(subscription)

    db.session.commit()
