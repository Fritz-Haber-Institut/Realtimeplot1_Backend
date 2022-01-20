from os import environ, path

from dotenv import load_dotenv  # pip install python-dotenv

BASE_DIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASE_DIR, ".env"))


class Config:

    # General
    SECRET_KEY = environ.get("SECRET_KEY")
    FLASK_ENV = environ.get("FLASK_ENV")
    FLASK_APP = environ.get("FLASK_APP")
    FLASK_RUN_HOST = environ.get("FLASK_RUN_HOST")

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Auth
    DEFAULT_ADMIN_NAME = environ.get("DEFAULT_ADMIN_NAME")
    DEFAULT_ADMIN_PASSWORD = environ.get("DEFAULT_ADMIN_PASSWORD")
    PASSWORD_SALT = environ.get("PASSWORD_SALT")
    ACCESS_TOKEN_VALIDITY_TIME = int(environ.get("ACCESS_TOKEN_VALIDITY_TIME"))

    # Archive
    ARCHIVER_URL = environ.get("ARCHIVER_URL")
    ARCHIVER_TIMEZONE = environ.get("ARCHIVER_TIMEZONE")
    DEFAULT_ARCHIVER_TIME_PERIOD = int(environ.get("DEFAULT_ARCHIVER_TIME_PERIOD"))
