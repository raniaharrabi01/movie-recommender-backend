# routes/recommendation_route.py
from flask import Blueprint, request, jsonify
from app.services.recommend_service import get_recommendations_for_movie

recommendation_bp = Blueprint("recommending", __name__)

@recommendation_bp.route("/api/recommend", methods=["GET"])
def recommend():
    query_id = request.args.get("id")
    if not query_id:
        return jsonify({"error": "Le paramètre 'id' est requis."}), 400

    response, status_code = get_recommendations_for_movie(query_id)
    return jsonify(response), status_code
