def create_rating(user_id, item_id, rating):
    return {
        "user_id": user_id,
        "item_id": item_id,
        "rating": rating
    }