from flask import Flask, current_app  # pip install Flask
from flask_cors import CORS  # pip install flask-cors
from flask_sqlalchemy import SQLAlchemy  # pip install flask-sqlalchemy

db = SQLAlchemy()

def create_app():

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")
    
    CORS(app)

    db.init_app(app)

    with app.app_context():

        from .apps.auth.views import auth_blueprint

        app.register_blueprint(auth_blueprint, url_prefix="/auth")
        
        from .apps.experiments.views import experiments_blueprint

        app.register_blueprint(experiments_blueprint, url_prefix="/experiments")

        db.create_all()

        from .apps.auth.models import User, UserTypeEnum
        from .apps.auth.password import get_hash
        
        admin = User.query.filter(User.user_id == 0).first()
        if (admin == None):
            admin = User(
                user_id=0,
                login_name=app.config['DEFAULT_ADMIN_NAME'],
                first_name=app.config['DEFAULT_ADMIN_NAME'],
                last_name=app.config['DEFAULT_ADMIN_NAME'],
                email=None,
                password_hash=get_hash(app.config['DEFAULT_ADMIN_PASSWORD']),
                user_type=UserTypeEnum.admin
            )
            db.session.add(admin)
            db.session.commit()

        return app
