from database.mongo import items_collection

def get_movies_from_db(page=1, limit=10):
    # Utiliser les paramètres `page` et `limit` pour paginer les résultats
    skip = (page - 1) * limit  # Le nombre d'éléments à ignorer (pages précédentes)
    movies = list(items_collection.find().skip(skip).limit(limit))  # Récupère les films avec pagination
    return movies

def count_movies_in_db():
    # Compter le nombre total de films dans la base de données
    return items_collection.count_documents({})

def get_movie_details_from_db(movie_id):
    # Rechercher le film par son ID dans la collection MongoDB
    movie = items_collection.find_one({"_id": movie_id})
    if not movie:
        return None
    # Retourner les détails du film
    return {
        "id": movie["_id"],
        "title": movie.get("title", "Titre non disponible"),
        "overview": movie.get("overview", "Résumé non disponible"),
        "genres": movie.get("genres", "Genres non disponibles"),
        "image_url": movie.get("image_url", ""),
        "director": movie.get("director", "Réalisateur non disponible"),
        "cast": movie.get("cast", []),
        "rating": movie.get("rating", 0),
        "trailer url" : movie.get("trailer_url", "")
    }