from database.mongo import items_collection

def check_if_movie_exists(item_id):
    movie = items_collection.find_one({"_id": item_id})
    if movie:
        print(f"✅ Movie with ID {item_id} exists in the collection.")
        return True
    else:
        print(f"❌ Movie with ID {item_id} is NOT in the collection.")
        return False
result = check_if_movie_exists(1585)
print(result)