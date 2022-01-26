from flask import current_app


def pv_string_to_mqtt_channel(pv_string: str) -> str:
    if pv_string == None:
        return None
    return f"{current_app.config['MQTT_CHANNEL_PREFIX']}/{pv_string.replace(':', '/')}"
