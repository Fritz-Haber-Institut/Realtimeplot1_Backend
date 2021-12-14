import hashlib

from flask import Flask, current_app  # pip install Flask
from flask_sqlalchemy import SQLAlchemy  # pip install flask-sqlalchemy

db = SQLAlchemy()

def create_app():

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")

    db.init_app(app)

    with app.app_context():

        from .apps.auth.views import auth_blueprint

        app.register_blueprint(auth_blueprint, url_prefix="/auth")

        db.create_all()

        from .apps.auth.models import User, UserTypeEnum
        
        admin = User.query.filter(User.user_id == 0).first()
        if (admin == None):
            encoded_password=hashlib.md5(f"{app.config['PASSWORD_SALT']}{app.config['DEFAULT_ADMIN_PASSWORD']}".encode())
            admin = User(
                user_id=0,
                first_name=app.config['DEFAULT_ADMIN_NAME'],
                last_name=app.config['DEFAULT_ADMIN_NAME'],
                email=None,
                password_hash=encoded_password.hexdigest(),
                user_type=UserTypeEnum.admin
            )
            db.session.add(admin)
            db.session.commit()

        return app
