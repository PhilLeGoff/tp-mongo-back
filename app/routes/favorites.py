from flask import Blueprint, request, jsonify
from app.extensions import mongo

favorites_bp = Blueprint("favorites", __name__)

def get_client_ip(req):
    return req.headers.get("X-Forwarded-For", req.remote_addr)

@favorites_bp.route("/", methods=["GET"])
def get_favorites():
    ip = get_client_ip(request)
    favorites = list(mongo.db.favorites.find({"ip": ip}, {"_id": 0}))
    return jsonify(favorites), 200

@favorites_bp.route("/toggle", methods=["POST"])
def toggle_favorite():
    ip = get_client_ip(request)
    data = request.json
    movie_id = data.get("movie_id")
    movie_data = data.get("movie_data")

    existing = mongo.db.favorites.find_one({"ip": ip, "movie_id": movie_id})

    if existing:
        mongo.db.favorites.delete_one({"_id": existing["_id"]})
        return jsonify({"message": "Removed from favorites"}), 200
    else:
        mongo.db.favorites.insert_one({
            "ip": ip,
            "movie_id": movie_id,
            "movie_data": movie_data
        })
        return jsonify({"message": "Added to favorites"}), 200