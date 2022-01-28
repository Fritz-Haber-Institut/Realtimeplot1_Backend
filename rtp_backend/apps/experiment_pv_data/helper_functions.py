from datetime import datetime, timedelta, tzinfo

from arvpyf.ar import ArchiverReader  # pip install arvpyf
from dateutil import tz
from flask import current_app, make_response
from rtp_backend.apps.experiments.models import Experiment
from rtp_backend.apps.utilities import http_status_codes as status

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_data_for_experiment(
    experiment=None, since=None, until=None, process_variable=None, only_validate=False
):
    try:
        ar_url = current_app.config["ARCHIVER_URL"]
        ar_tz = current_app.config["ARCHIVER_TIMEZONE"]
        config = {"url": ar_url, "timezone": ar_tz}
        arvReader = ArchiverReader(config)

        data = {}

        arv_pvs = [process_variable]

        if experiment:
            arv_pvs = [pv.pv_string for pv in experiment.process_variables]

        if not until:
            until = datetime.now(tz=tz.gettz(ar_tz)).strftime(TIME_FORMAT)

        if not since:
            since = datetime.strptime(until, TIME_FORMAT) - timedelta(
                hours=current_app.config["DEFAULT_ARCHIVER_TIME_PERIOD"]
            )
            since = since.strftime(TIME_FORMAT)

        if only_validate:
            since = until = datetime.now(tz=tz.gettz(ar_tz)).strftime(TIME_FORMAT)

        for pv in arv_pvs:
            data_frame = arvReader.get(pv, since, until)
            data_frame["time"] = data_frame["time"].astype(str)
            data[pv] = data_frame.to_dict("records")

        if only_validate:
            return True

        return {"experiment": experiment.to_dict(), "process_variables_data": data}
    except:
        if only_validate:
            return False

        return make_response(
            {"errors": ["Could not get process variable data from archiver."]},
            status.BAD_GATEWAY,
        )
