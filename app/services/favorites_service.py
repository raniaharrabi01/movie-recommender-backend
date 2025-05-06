from database.mongo import favorites_collection
from app.models.favorites import create_favorite
from database.mongo import items_collection
from bson import ObjectId

def add_favorite(data):
    """
    Ajoute un film aux favoris d'un utilisateur.
    """
    favorite = create_favorite(data["user_id"], data["item_id"])
    # Vérifier si le favori existe déjà
    existing_favorite = favorites_collection.find_one({
        "user_id": favorite["user_id"],
        "item_id": favorite["item_id"]
    })
    if existing_favorite:
        return {"message": "Le film est déjà dans les favoris."}, 400

    # Ajouter le favori à la collection
    favorites_collection.insert_one(favorite)
    return {"message": "Film ajouté aux favoris avec succès."}, 201


def remove_favorite(user_id, item_id):
    """
    Supprime un film des favoris d'un utilisateur.
    """
    # Vérifier si le favori existe
    result = favorites_collection.delete_one({
        "user_id": user_id,
        "item_id": item_id
    })
    if result.deleted_count == 0:
        return {"message": "Le film n'est pas dans les favoris."}, 404

    return {"message": "Film supprimé des favoris avec succès."}, 200


def get_favorites(user_id):
    favorites_cursor = favorites_collection.find({
        "user_id": user_id,
    })

    favorites = list(favorites_cursor)
    print("🎯 Favoris trouvés :", favorites)

    # Convertir les item_id en int
    favorite_item_ids = [int(fav["item_id"]) for fav in favorites]
    print("🎬 IDs de films favoris :", favorite_item_ids)

    favorite_movies = list(items_collection.find({"_id": {"$in": favorite_item_ids}}))
    print("📽️ Films correspondants :", favorite_movies)

    return favorite_movies

