from flask import Blueprint, request, jsonify
from app.ai.recommend import recommend_movies
from database.mongo import items_collection  # Importer la collection MongoDB

recommendation_bp = Blueprint("recommending", __name__)

@recommendation_bp.route("/api/recommend", methods=["GET"])
def recommend():
    query_id = request.args.get("id")
    if not query_id:
        return jsonify({"error": "Le paramètre 'id' est requis."}), 400
    # Obtenir les IDs des films recommandés
    recommendations = recommend_movies(query_id)
    if isinstance(recommendations, str):  # Message d'erreur
        return jsonify({"error": recommendations}), 404

    # Charger les données des films depuis MongoDB
    recommended_movies = []
    for movie_id in recommendations:
        movie = items_collection.find_one({"_id": movie_id})  # Requête MongoDB pour récupérer le film
        if movie:
            recommended_movies.append({
                "id": movie["_id"],
                "title": movie.get("title", "Titre non disponible"),
                "overview": movie.get("overview", "Résumé non disponible"),
                "genres": movie.get("genres", "Genres non disponibles"),
                "image_url": movie.get("image_url", ""),
                "director": movie.get("director", "Réalisateur non disponible"),
                "cast": movie.get("cast", [])
            })

    return jsonify(recommended_movies)