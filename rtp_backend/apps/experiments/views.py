from flask import Blueprint, Response, jsonify, make_response, request

from rtp_backend.apps.auth.decorators import token_required
from rtp_backend.apps.auth.helper_functions import is_admin
from rtp_backend.apps.auth.models import User, UserTypeEnum
from rtp_backend.apps.email.helper_functions import delete_subscriptions
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.generic_responses import (
    already_exists_in_database,
    forbidden_because_not_an_admin,
    respond_with_404,
)
from rtp_backend.apps.utilities.user_created_data import get_request_dict

from .helper_functions import get_experiment_dict, pv_string_to_experiment
from .models import Experiment, ProcessVariable, db

experiments_blueprint = Blueprint(
    "experiments",
    __name__,
    template_folder="experiments/",
)


@experiments_blueprint.route("/pvs", methods=["GET", "POST"])
@token_required
def pvs(current_user):
    if current_user.user_type != UserTypeEnum.admin:
        return forbidden_because_not_an_admin()

    if request.method == "GET":
        pvs = ProcessVariable.query.all()
        return make_response(
            {"process_variables": [pv.to_dict() for pv in pvs]},
            status.OK,
        )

    elif request.method == "POST":
        data = get_request_dict()
        if type(data) == Response:
            return data

        pv_string = data.get("pv_string")
        if not pv_string:
            return make_response(
                jsonify(
                    {
                        "errors": [
                            {
                                "pv_string": "No pv_string was specified. To create a process variable, you must provide a pv_string because it serves as primary_key."
                            }
                        ]
                    }
                ),
                status.BAD_REQUEST,
            )

        human_readable_name = data.get("human_readable_name")
        default_threshold_min = data.get("default_threshold_min")
        default_threshold_max = data.get("default_threshold_max")

        # check for existing PV
        pv_in_db = ProcessVariable.query.filter_by(pv_string=pv_string).first()
        if pv_in_db:
            return already_exists_in_database("process variable", pv_string)

        experiment = pv_string_to_experiment(pv_string)

        # create pv
        new_pv = ProcessVariable(
            pv_string=pv_string,
            experiment_short_id=experiment.short_id,
            human_readable_name=human_readable_name,
            default_threshold_max=default_threshold_max,
            default_threshold_min=default_threshold_min,
        )

        available_for_mqtt_publish = data.get("available_for_mqtt_publish")
        if available_for_mqtt_publish:
            if isinstance(available_for_mqtt_publish, bool):
                new_pv.available_for_mqtt_publish = available_for_mqtt_publish
            else:
                errors.append(
                    "available_for_mqtt_publish: Value must be either true or false."
                )

        db.session.add(new_pv)
        db.session.commit()

        return make_response(
            {"process_variable": new_pv.to_dict()},
            status.OK,
        )


@experiments_blueprint.route("/pvs/<pv_string>", methods=["GET", "PUT", "DELETE"])
@token_required
def pv(current_user, pv_string):
    if current_user.user_type != UserTypeEnum.admin:
        return forbidden_because_not_an_admin()

    pv_in_db = ProcessVariable.query.filter_by(pv_string=pv_string).first()
    if not pv_in_db:
        return respond_with_404("process variable", pv_string)

    experiment = pv_string_to_experiment(pv_string)

    if request.method == "GET":
        return {"process_variable": pv_in_db.to_dict()}

    if request.method == "PUT":
        data = get_request_dict()
        if type(data) == Response:
            return data

        errors = []

        new_pv_string = data.get("pv_string")
        if new_pv_string:
            pv_in_db.pv_string = new_pv_string

            new_experiment_data = pv_string_to_experiment(new_pv_string)
            if type(new_experiment_data) == Response:
                return {"experiment": new_experiment_data}

            if experiment.short_id != new_experiment_data.short_id:
                pv_in_db.experiment_short_id = new_experiment_data.short_id

                # Delete old experiment when no more PVs remain in it
                if experiment and len(experiment.process_variables) <= 1:
                    db.session.delete(experiment)

        human_readable_name = data.get("human_readable_name")
        if "human_readable_name" in data:
            pv_in_db.human_readable_name = human_readable_name

        if "experiment_short_id" in data:
            errors.append(
                "experiment_short_id: The experiment_short_id cannot be changed manually as it is generated from the pv_string. Change the characters in the pv_string before the first colon to change the short_id and thus assign the pv_string to a new experiment."
            )

        available_for_mqtt_publish = data.get("available_for_mqtt_publish")
        if available_for_mqtt_publish:
            if isinstance(available_for_mqtt_publish, bool):
                pv_in_db.available_for_mqtt_publish = available_for_mqtt_publish
            else:
                errors.append(
                    "available_for_mqtt_publish: Value must be either true or false."
                )

        default_threshold_min = data.get("default_threshold_min")
        if default_threshold_min:
            if isinstance(default_threshold_min, int):
                pv_in_db.default_threshold_min = default_threshold_min
            else:
                errors.append("default_threshold_min: Value must be Integer.")

        default_threshold_max = data.get("default_threshold_max")
        if default_threshold_max:
            if isinstance(default_threshold_max, int):
                pv_in_db.default_threshold_max = default_threshold_max
            else:
                errors.append("default_threshold_max: Value must be Integer.")
        db.session.commit()

        return make_response(
            {"process_variable": pv_in_db.to_dict(), "errors": errors},
            status.OK,
        )

    elif request.method == "DELETE":
        db.session.delete(pv_in_db)
        deleted_experiment = None

        if experiment and len(experiment.process_variables) < 1:
            deleted_experiment = experiment.short_id
            db.session.delete(experiment)

        delete_subscriptions(pv_string=pv_string)
        db.session.commit()
        return make_response(
            jsonify(
                {
                    "deleted_process_variable": pv_string,
                    "deleted_experiement": deleted_experiment,
                }
            ),
            status.OK,
        )


@experiments_blueprint.route("/<experiment_short_id>", methods=["GET", "PUT", "DELETE"])
@token_required
def experiment(requesting_user: User, experiment_short_id: str) -> Response:
    """Endpoint to query, modify or delete a single experiment.

    Args:
        requesting_user (User): The user who accessed the endpoint.
        experiment_short_id (string): The short_id of the experiment.

    Returns:
        Response: The server's response to the request.
    """

    # Get Experiment from Database or return 404
    experiment_in_database = Experiment.query.filter_by(
        short_id=experiment_short_id
    ).first()
    if experiment_in_database is None:
        return respond_with_404("experiment", experiment_short_id)

    # GET: Returns the experiment's dictionary.
    # Only include user_ids if the requesting_user is an administrator!
    if request.method == "GET":
        return {
            "experiment": get_experiment_dict(requesting_user, experiment_in_database)
        }

    # PUT: Change the values and return the modified experiment.
    # Change all valid values and return error messages for invalid values.
    elif request.method == "PUT":
        if not is_admin(requesting_user):
            return forbidden_because_not_an_admin()

        # Clean dict from harmful HTML tags.
        request_data = get_request_dict()
        if isinstance(request_data, Response):
            return get_request_dict()

        errors = []

        for key in request_data:
            if key == "human_readable_name":
                experiment_in_database.human_readable_name = request_data[
                    "human_readable_name"
                ]
            elif key == "short_id":
                errors.append(
                    "short_id: The short_id cannot be changed at the moment. Edit the individual process variables to create a new experiment with a new short_id!"
                )
            elif key == "users_to_add":
                for user_id in request_data["users_to_add"]:
                    user_in_database = User.query.filter_by(user_id=user_id).first()
                    if user_in_database:
                        user_in_database.experiments.append(experiment_in_database)
                        db.session.commit()
                    else:
                        errors.append(
                            f"users_to_add: The user ({user_id}) does not exist and therefore cannot be added to the experiment."
                        )

            elif key == "users_to_remove":
                for user_id in request_data["users_to_remove"]:
                    user_in_database = User.query.filter_by(user_id=user_id).first()
                    if user_in_database:
                        user_in_database.experiments.remove(experiment_in_database)

        db.session.commit()
        return jsonify(
            {
                "experiment": get_experiment_dict(
                    requesting_user, experiment_in_database
                ),
                "errors": errors,
            }
        )

    # DELETE: Deletes the experiment and all associated process variables.
    elif request.method == "DELETE":
        deleted_process_variables = []
        for process_variable in ProcessVariable.query.filter_by(
            experiment_short_id=experiment_in_database.short_id
        ).all():
            deleted_process_variables.append(process_variable)
            delete_subscriptions(pv_string=process_variable.pv_string)
            db.session.delete(process_variable)
        db.session.delete(experiment_in_database)
        db.session.commit()

        process_variables = []
        for process_variable in deleted_process_variables:
            process_variables.append(process_variable.pv_string)

        return jsonify(
            {
                "deleted_process_variables": process_variables,
                "deleted_experiement": experiment_short_id,
            }
        )


@experiments_blueprint.route("/", methods=["GET"])
@token_required
def experiments(requesting_user: User):
    if not is_admin(requesting_user):
        return forbidden_because_not_an_admin()

    return jsonify(
        {
            "experiments": [
                experiment.to_dict(include_user_ids=True)
                for experiment in Experiment.query.all()
            ]
        }
    )
