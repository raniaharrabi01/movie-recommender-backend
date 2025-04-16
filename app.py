from flask import Flask, request, jsonify
from db import users_collection, items_collection, ratings_collection
from bson import ObjectId
from models.rating import create_rating
from models.user import create_user
from models.item import create_item
import bcrypt



app = Flask(__name__)

# Endpoint pour ajouter un utilisateur
@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    user = create_user(data["name"], data["email"])
    result = users_collection.insert_one(user)
    return jsonify({"message": "Utilisateur ajouté", "id": str(result.inserted_id)})

# Endpoint pour ajouter un film
@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    item = {
        "title": data["title"],
        "genre": data["genre"],
        "description": data.get("description", ""),
        "image_url": data.get("image_url", "")
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
        return jsonify({
            "message": "Connexion réussie",
            "user_id": str(user["_id"]),
            "name": user["name"]
        })
    else:
        return jsonify({"message": "Mot de passe incorrect"}), 401



@app.route("/recommend/<user_id>", methods=["GET"])
def recommend(user_id):
    # 1. Récupérer toutes les notes de l'utilisateur
    user_ratings = list(ratings_collection.find({"user_id": user_id}))

    if not user_ratings:
        return jsonify({"message": "Aucune note trouvée pour cet utilisateur", "recommendations": []})

    # 2. Trouver les genres des films bien notés (rating >= 4.0)
    liked_item_ids = [r["item_id"] for r in user_ratings if r["rating"] >= 4.0]
    liked_items = list(items_collection.find({"_id": {"$in": [ObjectId(i) for i in liked_item_ids]}}))
    liked_genres = list({item["genre"] for item in liked_items})

    # 3. Recommander d'autres films du même genre (non encore notés)
    already_rated = set(r["item_id"] for r in user_ratings)
    recommendations = list(
        items_collection.find({
            "genre": {"$in": liked_genres},
            "_id": {"$nin": [ObjectId(i) for i in already_rated]}
        }).limit(5)
    )

    # 4. Retourner les titres recommandés
    result = [{"title": film["title"], "genre": film["genre"]} for film in recommendations]

    return jsonify({"recommendations": result})

if __name__ == "__main__":
    app.run(debug=True)
