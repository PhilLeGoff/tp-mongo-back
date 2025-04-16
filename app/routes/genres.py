from flask import Blueprint, jsonify, request
from app.extensions import mongo
from app.services.genre_service import GenreService

genres_bp = Blueprint('genres', __name__)
genre_service = GenreService(mongo)


@genres_bp.route('/', methods=['GET'])
def get_genres():
    posts = genre_service.get_genres()
    return jsonify(posts), 200

@genres_bp.route("/popular", methods=["GET"])
def get_common_genres():
    limit = int(request.args.get("limit", 5))
    popular_genres = genre_service.get_most_common_genres(limit)
    return jsonify(popular_genres), 200

@genres_bp.route("/<genre_name>", methods=["GET"])
def get_movies_by_genre(genre_name):
    movies = genre_service.get_movies_by_genre(genre_name)
    return jsonify(movies), 200
