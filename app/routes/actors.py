from flask import Blueprint, jsonify
from app.services.actor_service import ActorService
from app.extensions import mongo  # ✅ utilise l'instance directement

actors_bp = Blueprint("actors", __name__)

@actors_bp.route("/<int:actor_id>", methods=["GET"])
def get_actor(actor_id):
    service = ActorService(mongo=mongo)  # ✅ utilise l'instance injectée via mongo.init_app(app)
    actor = service.get_actor_details(actor_id)
    if actor:
        return jsonify(actor)
    return jsonify({"error": "Actor not found"}), 404
