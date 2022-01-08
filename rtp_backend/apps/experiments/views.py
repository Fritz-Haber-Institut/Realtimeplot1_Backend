import datetime
import re
from uuid import uuid4

import jwt  # pip install Flask-JWT
from flask import (Blueprint, Response, abort, current_app, jsonify,
                   make_response, request, url_for)
from rtp_backend.apps.auth.decorators import token_required
from rtp_backend.apps.auth.models import UserTypeEnum
from rtp_backend.apps.utilities import http_status_codes as status
from rtp_backend.apps.utilities.user_created_data import get_request_dict
from sqlalchemy import exc

from .models import Experiment, ProcessVariable, db

experiments_blueprint = Blueprint(
    "experiments",
    __name__,
    template_folder="experiments/",
)


def pv_string_to_experiment(pv_string: str) -> Experiment:
    experiment_short_id = get_experiment_short_id_from_pv_string(pv_string)
    if experiment_short_id == None:
            return make_response(
            "COULD NOT FIND EXPERIMENT_SHORT_ID IN PV_STRING",
            status.BAD_REQUEST,
        )
        
    # check for existing Experiment
    experiment = Experiment.query.filter_by(short_id=experiment_short_id).first()
        
    # create one if none
    if not experiment:
        experiment = Experiment(
            short_id=experiment_short_id
        )
        
        db.session.add(experiment)
        
    return experiment

def get_experiment_short_id_from_pv_string(pv_string: str):
    pv_string_data = pv_string.split(":")
    
    if len(pv_string_data) > 0:
        return pv_string_data[0]
    
    return None


@experiments_blueprint.route("/pvs", methods=["GET", "POST"])
@token_required
def pvs(current_user):
    if current_user.user_type != UserTypeEnum.admin:
        return make_response(
                "FORBIDDEN",
                status.FORBIDDEN,
                {"Authentication": "Only administrators can access this endpoint"},
            )
    
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
        
        pv_string = data['pv_string']
        
        # check for existing PV
        pv_in_db = ProcessVariable.query.filter_by(pv_string=pv_string).first()
        if pv_in_db:
            return make_response(
                f"PROCESS VARIABLE {pv_string} ALREADY IN DATABASE",
                status.CONFLICT,
            )
        
        experiment = pv_string_to_experiment(pv_string)
        
        # create pv
        new_pv = ProcessVariable(
                    pv_string=pv_string,
                    experiment_short_id=experiment.short_id,
        )
        
        db.session.add(new_pv)
        db.session.commit()
        
        return make_response(
                new_pv.to_dict(),
                status.OK,
        )

    
@experiments_blueprint.route("/pvs/<pv_string>", methods=["PUT", "DELETE"])
@token_required
def pv(current_user, pv_string):
    if current_user.user_type != UserTypeEnum.admin:
        return make_response(
                "FORBIDDEN",
                status.FORBIDDEN,
                {"Authentication": "Only administrators can access this endpoint"},
            )
        
    pv_in_db = ProcessVariable.query.filter_by(pv_string=pv_string).first()
    if not pv_in_db:
        return make_response(
            f"NO PROCESS VARIABLE {pv_string} IN DATABASE",
            status.NOT_FOUND,
        )
    
    experiment = pv_string_to_experiment(pv_string)
                
    if request.method == "PUT":
        data = get_request_dict()
        if type(data) == Response:
            return data
        
        new_pv_string = data.get("pv_string")
        if new_pv_string:
            pv_in_db.pv_string = new_pv_string
            
            new_experiment_data = pv_string_to_experiment(new_pv_string)
            if type(new_experiment_data) == Response:
                return new_experiment_data
            
            if experiment.short_id != new_experiment_data.short_id:
                pv_in_db.experiment_short_id=new_experiment_data.short_id
                
                # Delete old experiment when no more PVs remain in it    
                if experiment and len(experiment.process_variables) <= 1:
                    db.session.delete(experiment)
            
        human_readable_name = data.get("human_readable_name")
        if human_readable_name:
            pv_in_db.pv_string = human_readable_name
        
        db.session.commit()
            
        return make_response(
                pv_in_db.to_dict(),
                status.OK,
            )
        
    elif request.method == "DELETE":
        db.session.delete(pv_in_db)
        deleted_experiment = None
        
        print(len(experiment.process_variables))
        if experiment and len(experiment.process_variables) < 1:
            deleted_experiment = experiment.short_id
            db.session.delete(experiment)
                    
        db.session.commit() 
        return make_response(
            jsonify({"deleted_process_variable": pv_string, "deleted_experiement": deleted_experiment}),
            status.OK,
        )
