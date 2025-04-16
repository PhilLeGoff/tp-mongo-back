import configparser

from dotenv import load_dotenv
from flask import Flask
import os
from .extensions import mongo
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    load_dotenv()
    CORS(app)
    # Configuration
    # app.config["MONGO_URI"] = config['PROD']['DB_URI']
    # app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("DB_URI")

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    from .routes.movies import movies_bp
    from .routes.genres import genres_bp
    app.register_blueprint(movies_bp, url_prefix='/films')
    app.register_blueprint(genres_bp, url_prefix='/genres')

    # Error handlers
    from .errors.handlers import register_error_handlers
    register_error_handlers(app)

    @app.route('/')
    def index():
        return {'message': 'Bienvenue sur l’API Movie-App 🎬'}, 200

    return app
