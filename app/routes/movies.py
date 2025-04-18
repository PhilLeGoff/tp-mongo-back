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

@movies_bp.route('/popular', methods=['GET'])
def get_popular_movies():
    movies = list(movie_service.get_popular())
    return jsonify(movies), 200

@movies_bp.route("/latest", methods=["GET"])
def get_latest_movies():
    limit = int(request.args.get("limit", 10))
    movies = movie_service.get_latest_movies(limit)
    return jsonify(movies), 200


@movies_bp.route("/top-rated", methods=["GET"])
def top_rated_movies():
    limit = int(request.args.get("limit", 10))
    movies = movie_service.get_top_rated_movies(limit)
    return jsonify(movies), 200

@movies_bp.route("/analytics/overview", methods=["GET"])
def analytics_overview():
    try:
        data = {
            "appreciatedGenres": movie_service.get_most_appreciated_genres(),
            "topMoviesByDecade": movie_service.get_best_movies_per_decade(),
            "topRated": movie_service.get_top_rated_movies(),
            "surprise": movie_service.get_underrated_gems()
        }
        return jsonify(data), 200
    except Exception as e:
        print("❌ ERROR in analytics_overview:", e)
        return jsonify({"error": "Internal Server Error"}), 500


@movies_bp.route("/hottest", methods=["GET"])
def hottest_movies():
    try:
        limit = int(request.args.get("limit", 10))
        movies = movie_service.get_hottest_movies(limit)
        return jsonify(movies), 200
    except Exception as e:
        print("❌ ERROR in hottest_movies:", e)
        return jsonify({"error": "Internal Server Error"}), 500

@movies_bp.route('/title_frequency', methods=['GET'])
def get_title_frequency():
    movies = list(movie_service.get_title_frequency())
    return jsonify(movies), 200

# Specific routes FIRST
@movies_bp.route("/recommended/", methods=["GET"])
def get_recommendations():
    user_ip = request.remote_addr
    recommendations = movie_service.get_recommendations(user_ip)
    return jsonify(recommendations), 200

@movies_bp.route("/new-releases", methods=["GET"])
def get_new_releases():
    return jsonify(movie_service.get_new_releases()), 200

@movies_bp.route("/most-popular", methods=["GET"])
def get_most_popular():
    return jsonify(movie_service.get_most_popular()), 200

@movies_bp.route("/critically-acclaimed", methods=["GET"])
def get_critically_acclaimed():
    return jsonify(movie_service.get_critically_acclaimed()), 200

@movies_bp.route("/underrated", methods=["GET"])
def get_underrated():
    return jsonify(movie_service.get_underrated_gems(limit=15)), 200

@movies_bp.route("/best-french", methods=["GET"])
def get_best_french_movies():
    return jsonify(movie_service.get_best_french_movies())

@movies_bp.route("/best-action", methods=["GET"])
def get_best_action_movies():
    return jsonify(movie_service.get_best_action_movies())

@movies_bp.route("/nostalgia-90s", methods=["GET"])
def get_nostalgia_90s():
    return jsonify(movie_service.get_best_movies_by_decade(1990)), 200

@movies_bp.route("/sci-fi", methods=["GET"])
def get_sci_fi():
    return jsonify(movie_service.get_movies_by_genre("Science Fiction")), 200

@movies_bp.route("/true-stories", methods=["GET"])
def get_true_stories():
    return jsonify(movie_service.get_true_stories()), 200

# Dynamic ID route LAST — with unique name
@movies_bp.route('/<movie_id>', methods=['GET'])
def get_movie_by_id(movie_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        object_id = ObjectId(movie_id)
        movie = movie_service.get_movie(object_id)
        if movie:
            return jsonify(movie), 200
        return jsonify({"error": "Movie not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid movie ID"}), 400

@movies_bp.route("/details/<int:movie_id>", methods=["GET"])
def get_movie_details(movie_id):
    service = MovieService(mongo)
    movie = service.get_detailed_movie(movie_id)
    if movie:
        return jsonify(movie)
    return jsonify({"error": "Movie not found"}), 404

@movies_bp.route("/best-by-decade", methods=["GET"])
def route_best_movies_by_decade():
    return (movie_service.get_best_movies_by_decade()), 200


@movies_bp.route('/search', methods=['GET'])
def search_movies():
    keyword = request.args.get('q', '')
    genre = request.args.get('genre', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    return jsonify(movie_service.search_movies(mongo, keyword, genre, page, limit)), 200
