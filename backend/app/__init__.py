import configparser
from flask import Flask
import os
from .extensions import mongo


def create_app():
    app = Flask(__name__)
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(".ini")))

    # Configuration
    app.config["MONGO_URI"] = config['PROD']['DB_URI']
    # app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    from .routes.movies import movies_bp
    app.register_blueprint(movies_bp, url_prefix='/films')

    # Error handlers
    # from .errors.handlers import register_error_handlers
    # register_error_handlers(app)

    return app
