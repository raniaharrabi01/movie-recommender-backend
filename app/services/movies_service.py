from database.mongo import items_collection

def get_movies_from_db(page=1, limit=10):
    # Utiliser les paramètres `page` et `limit` pour paginer les résultats
    skip = (page - 1) * limit  # Le nombre d'éléments à ignorer (pages précédentes)
    movies = list(items_collection.find().skip(skip).limit(limit))  # Récupère les films avec pagination
    return movies

def count_movies_in_db():
    # Compter le nombre total de films dans la base de données
    return items_collection.count_documents({})
