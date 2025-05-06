from app.ai.recommend import recommend_movies
from database.mongo import items_collection
from bson import ObjectId

def get_recommendations_for_movie(query_id):
    # Obtenir les IDs recommandés
    recommendations = recommend_movies(query_id)
    if isinstance(recommendations, str):  # Cas d'erreur
        return {"error": recommendations}, 404

    recommended_movies = []
    for movie_id in recommendations:
        try:
            movie = items_collection.find_one({"_id": movie_id})
        except Exception as e:
            continue  

        if movie:
            recommended_movies.append({
                "id": str(movie["_id"]),
                "title": movie.get("title", "Titre non disponible"),
                "overview": movie.get("overview", "Résumé non disponible"),
                "genres": movie.get("genres", "Genres non disponibles"),
                "image_url": movie.get("image_url", ""),
                "director": movie.get("director", "Réalisateur non disponible"),
                "cast": movie.get("cast", [])
            })
        
    return recommended_movies, 200
