from arvpyf.ar import ArchiverReader  # pip install arvpyf
from arvpyf.mgmt import ArchiverConfig
from flask import make_response
from rtp_backend.apps.experiments.models import Experiment, ProcessVariable, db
from rtp_backend.apps.experiments.helper_functions import (
    get_experiment_short_id_from_pv_string,
    pv_string_to_experiment,
    get_experiment_dict,
)
from rtp_backend.apps.auth.helper_functions import is_admin
from rtp_backend.apps.auth.models import User
import json

from flask import current_app


ar_url = current_app.config["ARCHIVER_URL"]
ar_tz = current_app.config["ARCHIVER_TIMEZONE"]

config = {"url": ar_url, "timezone": ar_tz}

arvReader = ArchiverReader(config)


# arv_pvs = [pv.pv_string for pv in ProcessVariable.query.filter_by(experiment_short_id=experiment_short_id.all())]
arv_pvs = [
    pv.pv_string
    for pv in Experiment.query.filter_by(experiment_short_id=experiment_short_id.all())
]

since = "2021-12-10 10:00:00"
until = "2021-12-10 17:00:00"

# df = arvReader.get(pv, since, until)
process_variables = {}

for pv in arv_pvs:
    print(" ------- rtrieve ", pv, " ---------")
    data_frame = arvReader.get(pv, since, until)
    data_frame["time"] = data_frame["time"].astype(str)
    process_variables[pv] = data_frame.to_dict("records")  # daten

    return {"experiment": experiment, "process_variables_data": process_variables}
