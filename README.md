<section align=center>
<img src="images/logo.png" alt="Backend server logo: Simplified representation of a server." width="120" height="120" />

---

# Realtimeplot Backend <!-- omit in toc -->
This repository contains the source code for the Realtimeplot project implemented for the [Fritz Haber Institute](https://www.fhi.mpg.de/). This server software can be used together with the [Realtimeplot Frontend](https://github.com/Fritz-Haber-Institut/Realtimeplot1_Frontend).


<a href="https://github.com/Fritz-Haber-Institut/Realtimeplot1_Backend/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/Fritz-Haber-Institut/Realtimeplot1_Backend"></a>
<a href="https://github.com/Fritz-Haber-Institut/Realtimeplot1_Backend"><img alt="GitHub license" src="https://img.shields.io/github/license/Fritz-Haber-Institut/Realtimeplot1_Backend"></a>  


</section>

---

## Table of contents <!-- omit in toc -->
- [How to run the backend server](#how-to-run-the-backend-server)
  - [Create and activate virtual development environment (GNU+Linux / macOS)](#create-and-activate-virtual-development-environment-gnulinux--macos)
  - [Install requirements](#install-requirements)
  - [Configuration via .env file](#configuration-via-env-file)
  - [Start the server](#start-the-server)
- [Endpoints documentation](#endpoints-documentation)
  - [Users and authentication](#users-and-authentication)
  - [Experiments and Process variables](#experiments-and-process-variables)
    - [Get data from experiments and process variables](#get-data-from-experiments-and-process-variables)
    - [Setting variables via MQTT Publish](#setting-variables-via-mqtt-publish)
    - [Email threshold subscriptions](#email-threshold-subscriptions)
    - [Import and export of experiment configurations](#import-and-export-of-experiment-configurations)
  - [Cross-endpoint responses](#cross-endpoint-responses)
- [Contribute](#contribute)

---

## How to run the backend server

> This documentation assumes a GNU+Linux or macOS as host system. Individual commands may differ on Windows hosts.

### Create and activate virtual development environment (GNU+Linux / macOS)

A current installation of [Python 3.9](https://www.python.org/) [(GPL-compatible license)](https://docs.python.org/3/license.html) is required!

```bash
python3 -m venv venv
. venv/bin/activate
```

### Install requirements

- [Flask](https://github.com/pallets/flask/) [(BSD-3-Clause License)](https://github.com/pallets/flask/blob/main/LICENSE.rst)
- [Flask-SQLAlchemy](https://github.com/pallets/flask-sqlalchemy/) [(BSD-3-Clause License)](https://github.com/pallets/flask-sqlalchemy/blob/main/LICENSE.rst)
- [python-dotenv](https://github.com/theskumar/python-dotenv) [(BSD-3-Clause License)](https://github.com/theskumar/python-dotenv/blob/master/LICENSE)
- [Flask-JWT](https://github.com/mattupstate/flask-jwt) [(MIT License)](https://github.com/mattupstate/flask-jwt/blob/master/LICENSE)
- [Bleach](https://github.com/mozilla/bleach) [(Apache License, Version 2.0)](https://github.com/mozilla/bleach/blob/main/LICENSE)
- [Flask-CORS](https://github.com/corydolphin/flask-cors) [(MIT License)](https://github.com/corydolphin/flask-cors/blob/master/LICENSE)
- [Archiver Python Frontend](https://github.com/NSLS-II/arvpyf) [(BSD-3-Clause License)](https://github.com/NSLS-II/arvpyf/blob/master/LICENSE)
- [Eclipse Paho™ MQTT Python Client](https://github.com/eclipse/paho.mqtt.python) [(Eclipse Public License 2.0 and the
Eclipse Distribution License 1.0)](https://github.com/eclipse/paho.mqtt.python/blob/master/LICENSE.txt)

```bash
pip install Flask flask-sqlalchemy python-dotenv Flask-JWT bleach flask-cors arvpyf paho-mqtt
```

### Configuration via .env file

Create a **.env** file in the root directory of this repository!

```
# General
SECRET_KEY=your_secret_key
FLASK_ENV=development # development or production
FLASK_APP=wsgi.py
FLASK_RUN_HOST=0.0.0.0

# SQLAlchemy
SQLALCHEMY_DATABASE_URI=sqlite:///../test.db  # path to database

# Auth
DEFAULT_ADMIN_NAME=admin_login_name
DEFAULT_ADMIN_PASSWORD=admin_login_password
PASSWORD_SALT=password_salt
ACCESS_TOKEN_VALIDITY_TIME=120 # in minutes

# Archive
ARCHIVER_URL=archiver_url
ARCHIVER_TIMEZONE=Europe/Berlin
DEFAULT_ARCHIVER_TIME_PERIOD=7

# MQTT
MQTT_SERVER_URL=mqtt_server_url
MQTT_CHANNEL_PREFIX=mqtt_channel_prefix

# THRESHOLD ALARMS
EMAIL_MQTT_CHANNEL=email_mqtt_channel
THRESHOLD_UNIT=mm
```

Replace the values ​​(after the `=` symbol) with your own values!

- For `General` see: [Flask - Builtin Configuration Values](https://flask.palletsprojects.com/en/2.0.x/config/#builtin-configuration-values)
- For `SQLAlchemy`see: [Flask-SQLAlchemy - Configuration Keys](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#configuration-keys)
- You can get the URLs (`ARCHIVER_URL`, `MQTT_SERVER_URL`) and MQTT channels (`MQTT_CHANNEL_PREFIX`, `EMAIL_MQTT_CHANNEL`) from the administrators of the corresponding servers.
  - The MQTT channels are specified in the .env without a leading "/".

### Start the server

```bash
flask run
```

*Alternatively, `python wsgi.py` can also be used during development.*

The server should be accessible at http://127.0.0.1:5000/.
However, the configured URL (host + port) is also printed to the command line.

> During the first `flask run`, the server will create an admin user with the user_id 0". Username (login_name) and password correspond to the values of DEFAULT_ADMIN_NAME and DEFAULT_ADMIN_PASSWORD defined in the .env file.

## Endpoints documentation

### Users and authentication

> Authenticate, create, edit and delete users

[Documentation in docs/users_and_authentication.md](docs/users_and_authentication.md)

### Experiments and Process variables

> Create, get, edit and delete experiments and process variables

[Documentation in docs/experiments_and_process_variables.md](docs/experiments_and_process_variables.md)

#### Get data from experiments and process variables

> Receive experiment data from the archiver

[Documentation in docs/experiment_pv_data.md](docs/experiment_pv_data.md)

#### Setting variables via MQTT Publish

> Set new values for process variables

[Documentation in docs/mqtt_publish.md](docs/mqtt_publish.md)

#### Email threshold subscriptions

> Subscribe to email alerts for breached process variable thresholds

[Documentation in docs/email_threshold_subscription.md](docs/email_threshold_subscription.md)

#### Import and export of experiment configurations

> Import and export database entries

[Documentation in docs/file_import_export.md](docs/file_import_export.md)

### Cross-endpoint responses

[Documentation in docs/cross_endpoint_responses.md](docs/cross_endpoint_responses.md)

## Contribute

Feedback and contributions are always welcome.

To ensure a consistent code style, please install [pre-commit](https://pre-commit.com/) [(MIT License)](https://github.com/pre-commit/pre-commit/blob/master/LICENSE).

```zsh
pip install pre-commit
pre-commit install
```