from flask import Blueprint, jsonify, request
from bson import ObjectId
# from app.services.post_service import PostService
from app.extensions import mongo
from app.services.movie_service import MovieService

movies_bp = Blueprint('movies', __name__)
movie_service = MovieService(mongo)

@movies_bp.route('/', methods=['GET'])
def get_movies():
    posts = movie_service.get_movies()
    return jsonify(posts), 200

@movies_bp.route('/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = movie_service.get_movie(movie_id)
    if movie:
        return jsonify(movie), 200
    return jsonify({"error": "Post not found"}), 404

@movies_bp.route('/cursor', methods=['GET'])
def get_movies_cursor():
    last_id = request.args.get('last_id')
    per_page = int(request.args.get('per_page', 10))
    movies = list(movie_service.get_movies_cursor(last_id, per_page))
    return jsonify({
        "movies": movies,
        "next_cursor": str(movies[-1]['_id']) if movies else None
    }), 200

@movies_bp.route('/latest', methods=['GET'])
def get_latest_movies():
    movies = list(movie_service.get_latest())
    return jsonify(movies), 200

@movies_bp.route('/popular', methods=['GET'])
def get_popular_movies():
    movies = list(movie_service.get_popular())
    return jsonify(movies), 200

@movies_bp.route('/title_frequency', methods=['GET'])
def get_title_frequency():
    movies = list(movie_service.get_title_frequency())
    return jsonify(movies), 200
