from arvpyf.ar import ArchiverReader  # pip install arvpyf
from flask import current_app


def get_data_for_experiment(experiment, since, until):
    ar_url = current_app.config["ARCHIVER_URL"]
    ar_tz = current_app.config["ARCHIVER_TIMEZONE"]
    config = {"url": ar_url, "timezone": ar_tz}
    arvReader = ArchiverReader(config)

    data = {}
    arv_pvs = [pv.pv_string for pv in experiment.process_variables]
    for pv in arv_pvs:
        data_frame = arvReader.get(pv, since, until)
        data_frame["time"] = data_frame["time"].astype(str)
        data[pv] = data_frame.to_dict("records")
    return {"experiment": experiment, "process_variables_data": data}