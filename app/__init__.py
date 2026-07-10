from flask import Flask
from config import config
from app.extension import db, migrate, csrf

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.models import maitre

    from app.views.main import bp_main
    from app.views.maitre import bp_maitres


    app.register_blueprint(bp_main)
    app.register_blueprint(bp_maitres)


    return app