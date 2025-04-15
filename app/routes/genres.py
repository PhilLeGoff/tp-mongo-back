from flask import Blueprint, jsonify, request
from bson import ObjectId
from app.extensions import mongo
from app.services.genre_service import GenreService
from collections import Counter

genres_bp = Blueprint('genres', __name__)
genre_service = GenreService(mongo)


@genres_bp.route('/', methods=['GET'])
def get_genres():
    posts = genres_bp.get_genres()
    return jsonify(posts), 200

@genres_bp.route("/popular", methods=["GET"])
def get_common_genres():
    all_movies = mongo.db.movies.find({}, {"genres": 1})
    
    genres = []
    for movie in all_movies:
        if "genres" in movie and isinstance(movie["genres"], list):
            for g in movie["genres"]:
                if isinstance(g, dict) and "name" in g:
                    genres.append(g["name"])
                elif isinstance(g, str):
                    genres.append(g)
    
    genre_counts = Counter(genres)
    sorted_genres = genre_counts.most_common(5)

    return jsonify(sorted_genres), 200

@genres_bp.route("/<genre_name>", methods=["GET"])
def get_movies_by_genre(genre_name):
    query = {
        "genres": {
            "$elemMatch": {
                "name": {"$regex": f"^{genre_name}$", "$options": "i"}
            }
        }
    }
    movies = list(mongo.db.movies.find(query, {"_id": 0}))
    return jsonify(movies), 200