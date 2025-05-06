from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Connexion à MongoDB Atlas
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))

# Sélection de la base de données et des collections
db = client["recommender"]
items_collection = db["items"]
users_collection = db["users"]
favorites_collection = db["favorites"]
