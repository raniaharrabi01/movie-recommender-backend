from flask import Blueprint, request, jsonify
from app.services.tmdb_service import fetch_and_save_movies 
from app.services.movies_service import get_movies_from_db, count_movies_in_db, get_movie_details_from_db


movie_bp = Blueprint("movie", __name__)

@movie_bp.route("/api/movies/db")
def get_movies():
    # Récupérer les paramètres de la requête (page et limit)
    page = int(request.args.get('page', 1))  # Valeur par défaut : 1
    limit = int(request.args.get('limit', 20))  # Valeur par défaut : 10
    # Récupérer les films avec pagination
    movies = get_movies_from_db(page, limit)
    # Calculer le nombre total de films et de pages
    total_movies = count_movies_in_db()
    total_pages = (total_movies // limit) + (1 if total_movies % limit != 0 else 0)
    # Retourner les films et les informations sur la pagination
    return jsonify({
        "movies": movies,
        "total_movies": total_movies,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit
    })


@movie_bp.route("/api/movies/<int:movie_id>")
def get_movie_by_id(movie_id):
    # Appeler le service pour récupérer les détails du film
    movie = get_movie_details_from_db(movie_id)
    if not movie:
        return jsonify({"error": f"Film avec l'ID {movie_id} non trouvé."}), 404
    return jsonify(movie)

