from database.mongo import items_collection
from collections import Counter

ids = [str(doc["_id"]) for doc in items_collection.find()]
count = Counter(ids)

for movie_id, freq in count.items():
    if freq > 1:
        print(f"ID {movie_id} apparaît {freq} fois")

