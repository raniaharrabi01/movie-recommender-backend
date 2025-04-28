from flask import Flask, request, jsonify
from db import users_collection, items_collection, ratings_collection
from bson import ObjectId
from models.rating import create_rating
from models.user import create_user
from models.item import create_item
import bcrypt
import requests
import jwt
import datetime
import os
from dotenv import load_dotenv

# Initialisation de l'app Flask
app = Flask(__name__)

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# Endpoint pour ajouter un film
@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    item = {
        "title": data["title"],
        "genre": data["genre"],
        "overview": data.get("overview", ""),
        "image_url": data.get("image_url", ""),
        "trailer_url": data.get("trailer_url", "")
    }
    result = items_collection.insert_one(item)
    return jsonify({"message": "Item ajouté", "id": str(result.inserted_id)})


# Endpoint pour noter un film
@app.route("/ratings", methods=["POST"])
def add_rating():
    data = request.json
    rating = create_rating(data["user_id"], data["item_id"], data["rating"])
    result = ratings_collection.insert_one(rating)
    return jsonify({"message": "Note ajoutée", "id": str(result.inserted_id)})

#récupérer tous les films
@app.route('/items', methods=['GET'])
def get_all_items():
    items = list(items_collection.find())
    for item in items:
        item["_id"] = str(item["_id"])
    return jsonify(items)

#récupérer tous les utilisateurs
@app.route('/users', methods=['GET'])
def get_all_users():
    users = list(users_collection.find())
    for user in users:
        user["_id"] = str(user["_id"])
    return jsonify(users)

# API pour récupérer les favoris d'un utilisateur avec rating >= 4
@app.route("/api/favorites/<user_id>")
def get_favorites(user_id):
    # Trouver les item_id avec rating >= 4 pour cet utilisateur
    favorites = ratings_collection.find({
        "user_id": user_id,
        "rating": {"$gte": 4}
    })
    favorite_item_ids = [fav["item_id"] for fav in favorites]
    # Maintenant, trouver les détails des films correspondants
    favorite_movies = list(items_collection.find({"item_id": {"$in": favorite_item_ids}}))
    return jsonify(favorite_movies)


#Route d’inscription user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    name = data["name"]
    # Vérifier si l'email existe déjà
    if users_collection.find_one({"email": email}):
        return jsonify({"message": "Email déjà utilisé"}), 400
    # Hasher le mot de passe
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {
        "name": name,
        "email": email,
        "password": hashed_pw
    }
    result = users_collection.insert_one(user)
    return jsonify({"message": "Utilisateur inscrit", "id": str(result.inserted_id)}), 201

#Route de connexion
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "Utilisateur non trouvé"}), 404
    if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        # Création du token JWT
        payload = {
            "user_id": str(user["_id"]),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # expiration dans 2h
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({
            "message": "Connexion réussie",
            "token": token,
            "user_id": str(user["_id"]),
            "name": user["name"]
        })
    else:
        return jsonify({"message": "Mot de passe incorrect"}), 401


# Route pour récupérer toutes les notes d'un utilisateur
@app.route("/user/<user_id>/ratings", methods=["GET"])
def get_user_ratings(user_id):
    ratings = list(ratings_collection.find({"user_id": user_id}))
    for rating in ratings:
        rating["_id"] = str(rating["_id"])  # Convertir ObjectId pour qu'il soit JSON serializable
    return jsonify(ratings)


 # afficher les films de TMDB
@app.route("/api/movies")
def movies():
    return jsonify(get_movies())
API_KEY = os.getenv("API_KEY")
TMDB_MOVIES_URL = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=fr-FR&page=1"
TMDB_GENRE_URL = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=fr-FR"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
def get_genre_mapping():
    response = requests.get(TMDB_GENRE_URL)
    genres = response.json().get("genres", [])
    return {genre["id"]: genre["name"] for genre in genres}
def get_movies():
    response = requests.get(TMDB_MOVIES_URL)
    data = response.json()
    genre_map = get_genre_mapping()
    movies = []
    for movie in data.get("results", []):
        movie_info = {
            "id": movie["id"],
            "title": movie["title"],
            "image_url": IMAGE_BASE_URL + movie["poster_path"] if movie["poster_path"] else "",
            "genres": [genre_map.get(gid, "Inconnu") for gid in movie["genre_ids"]],
            "overview": movie["overview"],
            "trailer_url": f"https://www.youtube.com/results?search_query={movie['title'].replace(' ', '+')}+bande+annonce"
        }
        movies.append(movie_info)
        save_movie_if_not_exists(movie_info)
    return movies
def save_movie_if_not_exists(movie_info):
    # Vérifie si le film existe déjà
    existing_movie = items_collection.find_one({"item_id": movie_info["id"]})
    if not existing_movie:
        # Si n'existe pas, insérer dans la base
        items_collection.insert_one(movie_info)


if __name__ == "__main__":
    app.run(debug=True)
