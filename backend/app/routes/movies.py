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

@movies_bp.route('/<post_id>', methods=['GET'])
def get_post(movie_id):
    movie = movie_service.get_movie(movies_bp)
    if movie:
        return jsonify(movie), 200
    return jsonify({"error": "Post not found"}), 404
