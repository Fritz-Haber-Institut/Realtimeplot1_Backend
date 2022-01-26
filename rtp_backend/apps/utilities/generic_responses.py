"""
This module provides generic responses. You can use it to get consistently formatted responses.
"""

from flask import Response, jsonify, make_response

from . import http_status_codes as status


def mqtt_server_cannot_be_reached():
    return make_response(
        {
            "errors": [
                "The MQTT server to which this request should be forwarded cannot be reached."
            ]
        },
        status.BAD_GATEWAY,
    )


def respond_with_404(object_type: str, object_identifier: str) -> Response:
    """This function creates a NOT_FOUND response.
    You can use it for objects that are not in the database.

    Args:
        object_type (str): The name of the database model. Examples: "User", "Experiment".
        object_identifier (str): A unique identifier of the object.

    Returns:
        Response: A 404 response (JSON) declaring that the object is not in the database.
    """
    return make_response(
        jsonify(
            {
                "errors": [
                    f"The {object_type} ({object_identifier}) is not present in the database."
                ]
            }
        ),
        status.NOT_FOUND,
    )


def successfully_deleted(object_type, object_identifier):
    return make_response(
        jsonify(
            {
                "messages": [
                    f"The {object_type} ({object_identifier}) was successfully deleted from the database."
                ]
            }
        ),
        status.OK,
    )


def already_exists_in_database(object_type: str, object_identifier: str) -> Response:
    return make_response(
        jsonify(
            {
                "errors": [
                    f"A {object_type} ({object_identifier}) is already present in the database."
                ]
            }
        ),
        status.CONFLICT,
    )


def forbidden_because_not_an_admin():
    return make_response(
        jsonify(
            {"errors": ["Only administrators are allowed to access this endpoint."]}
        ),
        status.FORBIDDEN,
    )


def invalid_credentials():
    return make_response(
        jsonify(
            {
                "errors": [
                    "The login_name and password combination is not present in the database."
                ]
            }
        ),
        status.FORBIDDEN,
    )


def no_credentials():
    return make_response(
        jsonify(
            {
                "errors": [
                    "Access requires authorization via login_name and password (Basic Auth)."
                ]
            }
        ),
        status.UNAUTHORIZED,
    )
