import bleach  # pip install bleach
from flask import make_response, request

from . import http_status_codes as status


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
            else:
                cleaned_dict[bleach.clean(key)] = bleach.clean(dict_to_clean[key])
        print(cleaned_dict)
        return cleaned_dict
    except TypeError:
        return -2


def get_request_dict() -> dict:
    data = make_dict_safe(request.get_json())

    if data == -1:
        return make_response(
            "DATA MUST BE PROVIDED IN THE BODY AS JSON",
            status.BAD_REQUEST,
        )

    if data == -2:
        return make_response(
            "VALUES MUST NOT BE null",
            status.BAD_REQUEST,
        )

    return data
