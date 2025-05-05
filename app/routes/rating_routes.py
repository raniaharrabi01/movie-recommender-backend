from flask import Blueprint, request, jsonify
from app.services.rating_service import add_or_update_rating, get_favorites

rating_bp = Blueprint("rating", __name__)

# Route pour rating un film
@rating_bp.route("/ratings", methods=["POST"])
def rating():
    data = request.json
    message = add_or_update_rating(data)
    return jsonify(message)

# Route pour avoir tous les favories >=4 
@rating_bp.route("/api/favorites/<user_id>")
def favorites(user_id):
    favorites = get_favorites(user_id)
    return jsonify(favorites)
 
