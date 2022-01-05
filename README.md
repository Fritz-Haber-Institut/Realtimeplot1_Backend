# Realtimeplot1_Backend <!-- omit in toc -->

## Table of contents <!-- omit in toc -->
- [How to run the backend server](#how-to-run-the-backend-server)
  - [Create and activate virtual development environment (GNU+Linux / macOS)](#create-and-activate-virtual-development-environment-gnulinux--macos)
  - [Install requirements](#install-requirements)
  - [Configuration via .env file](#configuration-via-env-file)
  - [Start the server](#start-the-server)
- [Endpoints](#endpoints)
  - [Auth (Authentication)](#auth-authentication)

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

```bash
pip install Flask flask-sqlalchemy python-dotenv Flask-JWT bleach
```

### Configuration via .env file

Create a **.env** file in the root directory of this repository!

```conf
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
```

### Start the server

```bash
flask run
```

The server should be accessible at http://127.0.0.1:5000/.
However, the configured URL (host + port) is also printed to the command line.

## Endpoints

### Auth (Authentication)

> Authenticate, create, edit and delete users

[Documentation in docs/endpoints/auth.md](docs/endpoints/auth.md)