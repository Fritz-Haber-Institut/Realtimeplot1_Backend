"""
This module provides generic responses. You can use it to get consistently formatted responses.
"""

from flask import Response, jsonify, make_response

from . import http_status_codes as status


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
                "error": f"The {object_type} ({object_identifier}) is not present in the database."
            }
        ),
        status.NOT_FOUND,
    )
