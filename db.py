from pymongo import MongoClient

# Connexion à MongoDB local (par défaut)
client = MongoClient("mongodb://localhost:27017/")

# Création/connexion à la base de données
db = client["recommender"]

# Accès aux collections
users_collection = db["users"]
items_collection = db["items"]
ratings_collection = db["ratings"]