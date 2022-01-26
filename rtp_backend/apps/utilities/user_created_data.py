import bleach  # pip install bleach
from flask import make_response, request

from . import http_status_codes as status


def get_data_value_or_none(data, key):
    if data and isinstance(data, dict) and key in data:
        return data.get(key)
    return None


def make_dict_safe(dict_to_clean: dict) -> dict:
    if dict_to_clean == None:
        return -1
    try:
        cleaned_dict = {}
        for key in dict_to_clean:
            if type(dict_to_clean[key]) == list:
                cleaned_list = []
                for item in dict_to_clean[key]:
                    cleaned_list.append(bleach.clean(item))
                cleaned_dict[key] = cleaned_list
            elif type(dict_to_clean[key]) == bool or type(dict_to_clean[key]) == int:
                cleaned_dict[bleach.clean(key)] = dict_to_clean[key]
            else:
                cleaned_dict[bleach.clean(key)] = bleach.clean(dict_to_clean[key])
        return cleaned_dict
    except TypeError:
        return -2


def get_request_dict() -> dict:
    data = make_dict_safe(request.get_json())

    if data == -1:
        return make_response(
            {"errors": ["You have to send the data in the body as JSON."]},
            status.BAD_REQUEST,
        )

    if data == -2:
        return make_response(
            {
                "errors": [
                    "Some or more values ​​in the JSON body were null or do not correspond to the required column type in the database."
                ]
            },
            status.BAD_REQUEST,
        )

    return data
