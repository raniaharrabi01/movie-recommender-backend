from flask import Blueprint, request, jsonify
from app.services.favorites_service import add_favorite, remove_favorite, get_favorites

favorites_bp = Blueprint("favorite", __name__)

@favorites_bp.route("/api/favorites", methods=["POST"])
def add_to_favorites():
    data = request.json
    if not data or "user_id" not in data or "item_id" not in data:
        return jsonify({"error": "Les champs 'user_id' et 'item_id' sont requis."}), 400

    response, status_code = add_favorite(data)
    return jsonify(response), status_code


@favorites_bp.route("/api/favorites/<user_id>/<item_id>", methods=["DELETE"])
def remove_from_favorites(user_id, item_id):
    response, status_code = remove_favorite(user_id, item_id)
    return jsonify(response), status_code


@favorites_bp.route("/api/favorites/<user_id>", methods=["GET"])
def get_user_favorites(user_id):
    favorites = get_favorites(user_id)
    return jsonify(favorites)
