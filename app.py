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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np


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
# @app.route("/api/movies")
# def movies():
#     return jsonify(get_movies())
# API_KEY = os.getenv("API_KEY")
# TMDB_MOVIES_URL = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=fr-FR&page=1"
# TMDB_GENRE_URL = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=fr-FR"
# IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
# def get_genre_mapping():
#     response = requests.get(TMDB_GENRE_URL)
#     genres = response.json().get("genres", [])
#     return {genre["id"]: genre["name"] for genre in genres}
# def get_movies():
#     response = requests.get(TMDB_MOVIES_URL)
#     data = response.json()
#     genre_map = get_genre_mapping()
#     movies = []
    
#     for movie in data.get("results", []):
#         movie_info = {
#             "id": movie["id"],
#             "title": movie["title"],
#             "image_url": IMAGE_BASE_URL + movie["poster_path"] if movie["poster_path"] else "",
#             "genres": [genre_map.get(gid, "Inconnu") for gid in movie["genre_ids"]],
#             "overview": movie["overview"],
#             "trailer_url": f"https://www.youtube.com/results?search_query={movie['title'].replace(' ', '+')}+bande+annonce"
#         }
#         movies.append(movie_info)
#         save_movie_if_not_exists(movie_info)
#     return movies
# def save_movie_if_not_exists(movie_info):
#     movie_info["_id"] = movie_info["id"]  # Utilise l'id TMDB comme _id MongoDB
#     existing_movie = items_collection.find_one({"_id": movie_info["_id"]})
#     if not existing_movie:
#         items_collection.insert_one(movie_info)


@app.route("/api/movies")
def movies():
    return jsonify(get_movies())

API_KEY = os.getenv("API_KEY")
TMDB_GENRE_URL = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=fr-FR"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def get_genre_mapping():
    response = requests.get(TMDB_GENRE_URL)
    genres = response.json().get("genres", [])
    return {genre["id"]: genre["name"] for genre in genres}

def get_movies():
    genre_map = get_genre_mapping()
    movies = []

    for page in range(1, 16):  # Pages 1 à 10 => 200 films
        TMDB_MOVIES_URL = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=fr-FR&page={page}"
        response = requests.get(TMDB_MOVIES_URL)
        data = response.json()

        for movie in data.get("results", []):
            movie_info = {
                "_id": movie["id"],  # Utilise l'id TMDB comme _id MongoDB
                "title": movie["title"],
                "image_url": IMAGE_BASE_URL + movie["poster_path"] if movie.get("poster_path") else "",
                "genres": [genre_map.get(gid, "Inconnu") for gid in movie.get("genre_ids", [])],
                "overview": movie.get("overview", ""),
                "trailer_url": f"https://www.youtube.com/results?search_query={movie['title'].replace(' ', '+')}+bande+annonce"
            }

            movies.append(movie_info)
            save_movie_if_not_exists(movie_info)

    return movies

def save_movie_if_not_exists(movie_info):
    if not items_collection.find_one({"_id": movie_info["_id"]}):
        items_collection.insert_one(movie_info)


# @app.route("/api/recommendations/<user_id>", methods=["GET"])
# def recommend_movies(user_id):
#     # 1. Récupérer toutes les notes de cet utilisateur
#     user_ratings = list(ratings_collection.find({"user_id": user_id}))
#     rated_item_ids = [str(rating["item_id"]) for rating in user_ratings]
#     user_rated_scores = {str(rating["item_id"]): rating["rating"] for rating in user_ratings}
#     print("Récupérer tous les user ratings :", len(user_ratings))
#     print("Récupérer tous les rating item_ids :", len(rated_item_ids))

#     if not user_ratings:
#         return jsonify({"message": "L'utilisateur n'a pas encore noté de films."}), 404

#     # 2. Récupérer tous les films (notés et non notés)
#     all_items = list(items_collection.find())
#     print("Récupérer tous les films (notés et non notés) :", len(all_items))

#     # 3. Préparer les textes pour TF-IDF (genres + overview) et l’identifiant unique
#     documents = []
#     item_id_list = []
#     for item in all_items:
#         genres = " ".join(item.get("genres", []))
#         overview = item.get("overview", "")
#         text = f"{genres} {overview}"
#         documents.append(text)

#         # Gérer l'identifiant : 'id' ou '_id'
#         item_id = str(item.get("id", item.get("_id")))
#         item_id_list.append(item_id)

#     print("Récupérer tous les item_id des films :", len(item_id_list))
#     print("Récupérer tous les item_id des films  :", (item_id_list))


#     # 4. Vectoriser avec TF-IDF
#     vectorizer = TfidfVectorizer()
#     X = vectorizer.fit_transform(documents)

#     # y_test = vraies valeurs, y_pred = valeurs prédites par ton modèle
#     print("R² Score:", r2_score(y_test, y_pred))
#     print("MAE:", mean_absolute_error(y_test, y_pred))
#     print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))

#     # 5. Séparer X_train (films notés) et X_test (films non notés)
#     rated_indices = [i for i, item_id in enumerate(item_id_list) if item_id in rated_item_ids]
#     unrated_indices = [i for i, item_id in enumerate(item_id_list) if item_id not in rated_item_ids]

#     print("Récupérer tous les films notés :", len(rated_indices))
#     print("Récupérer tous les films non notés :", len(unrated_indices))

#     # 6. Préparer X_train et y_train
#     X_train = X[rated_indices]
#     y_train = np.array([user_rated_scores[item_id_list[i]] for i in rated_indices])

#     # 7. Préparer X_test et les IDs à prédire
#     X_test = X[unrated_indices]
#     test_item_ids = [item_id_list[i] for i in unrated_indices]

#     # 8. Entraîner un modèle de régression
#     model = LinearRegression()
#     model.fit(X_train, y_train)

#     # 9. Prédire les notes
#     predicted_ratings = model.predict(X_test)
#     print(predicted_ratings)

#     # 10. Sélectionner les films avec une note prédite ≥ 4
#     recommended_movies = []
#     for idx, pred_rating in enumerate(predicted_ratings):
#         if pred_rating >= 4:
#             movie_id = test_item_ids[idx]
#             movie = next((item for item in all_items if str(item.get("id", item.get("_id"))) == movie_id), None)
#             if movie:
#                 movie["_id"] = str(movie["_id"])
#                 recommended_movies.append(movie)

#     return jsonify(recommended_movies) 

from sklearn.model_selection import cross_val_predict
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

@app.route("/api/recommendations/<user_id>", methods=["GET"])
def recommend_movies(user_id):
    # 1. Récupérer toutes les notes de cet utilisateur
    user_ratings = list(ratings_collection.find({"user_id": user_id}))
    rated_item_ids = [str(rating["item_id"]) for rating in user_ratings]
    user_rated_scores = {str(rating["item_id"]): rating["rating"] for rating in user_ratings}
    print("Récupérer tous les user ratings :", len(user_ratings))
    print("Récupérer tous les rating item_ids :", len(rated_item_ids))

    if not user_ratings:
        return jsonify({"message": "L'utilisateur n'a pas encore noté de films."}), 404

    # 2. Récupérer tous les films (notés et non notés)
    all_items = list(items_collection.find())
    print("Récupérer tous les films (notés et non notés) :", len(all_items))

    # 3. Préparer les textes pour TF-IDF (genres + overview) et l’identifiant unique
    documents = []
    item_id_list = []
    for item in all_items:
        genres = " ".join(item.get("genres", []))
        overview = item.get("overview", "")
        text = f"{genres} {overview}"
        documents.append(text)

        # Gérer l'identifiant : 'id' ou '_id'
        item_id = str(item.get("id", item.get("_id")))
        item_id_list.append(item_id)

    print("Récupérer tous les item_id des films :", len(item_id_list))

    # 4. Vectoriser avec TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(documents)

    # 5. Séparer X_train (films notés) et X_test (films non notés)
    rated_indices = [i for i, item_id in enumerate(item_id_list) if item_id in rated_item_ids]
    unrated_indices = [i for i, item_id in enumerate(item_id_list) if item_id not in rated_item_ids]

    print("Récupérer tous les films notés :", len(rated_indices))
    print("Récupérer tous les films non notés :", len(unrated_indices))

    # 6. Préparer X_train et y_train
    X_train = X[rated_indices]
    y_train = np.array([user_rated_scores[item_id_list[i]] for i in rated_indices])

    # 7. Entraîner un modèle de régression
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 8. Évaluer le modèle sur les films notés
    y_pred_train = cross_val_predict(model, X_train, y_train, cv=5)

    print("Évaluation sur les films notés :")
    print("R² Score:", r2_score(y_train, y_pred_train))
    print("MAE:", mean_absolute_error(y_train, y_pred_train))
    print("RMSE:", np.sqrt(mean_squared_error(y_train, y_pred_train)))

    # 9. Prédire les notes pour les films non notés
    X_test = X[unrated_indices]
    test_item_ids = [item_id_list[i] for i in unrated_indices]
    predicted_ratings = model.predict(X_test)

    print(predicted_ratings)

    # 10. Sélectionner les films avec une note prédite ≥ 4
    recommended_movies = []
    for idx, pred_rating in enumerate(predicted_ratings):
        if pred_rating >= 4:
            movie_id = test_item_ids[idx]
            movie = next((item for item in all_items if str(item.get("id", item.get("_id"))) == movie_id), None)
            if movie:
                movie["_id"] = str(movie["_id"])
                recommended_movies.append(movie)

    return jsonify(recommended_movies)


if __name__ == "__main__":
    app.run(debug=True)
