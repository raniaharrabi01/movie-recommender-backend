from database.mongo import ratings_collection
from app.models.rating import create_rating
from database.mongo import items_collection 

def add_or_update_rating(data):   
    rating = create_rating(data["user_id"], data["item_id"], data["rating"]) 
    result = ratings_collection.update_one(
        {"user_id": data["user_id"], "item_id": data["item_id"]},
        {"$set": {"rating": data["rating"]}},
        upsert=True
    )
    if result.matched_count > 0:
        if result.modified_count > 0:
            return {
                "message": "Rating mis à jour",
                "id": str(rating["item_id"])
            }
        else:
            return {
                "message": "Aucune modification nécessaire, le rating est déjà à cette valeur",
                "id": str(rating["item_id"])
            }
    else:
        return {
            "message": "Nouveau rating ajouté",
            "id": str(result.upserted_id)  # Utilisation de l'ID inséré
        }

def get_favorites(user_id):
    favorites = ratings_collection.find({
        "user_id": user_id,
        "rating": {"$gte": 4}
    })
    favorite_item_ids = [fav["item_id"] for fav in favorites]
    print(len(favorite_item_ids))
    print(favorite_item_ids)
    favorite_movies = list(items_collection.find({"_id": {"$in": favorite_item_ids}}))
    print(len(favorite_movies))
    return favorite_movies