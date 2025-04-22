from pymongo import MongoClient

# Connexion à MongoDB Atlas
client = MongoClient("mongodb+srv://dbUser:dbUserPassword@cluster0.2bemzsg.mongodb.net/recommender?retryWrites=true&w=majority&appName=Cluster0")

# Sélection de la base de données et des collections
db = client["recommender"]
items_collection = db["items"]
users_collection = db["users"]
ratings_collection = db["ratings"]
