from database.mongo import users_collection
import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# Fonction pour inscrire un utilisateur
def register_user(data):
    email = data["email"]
    password = data["password"]
    name = data["name"]

    if users_collection.find_one({"email": email}):
        return {"message": "Email déjà utilisé"}, 400

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {
        "name": name,
        "email": email,
        "password": hashed_pw
    }
    result = users_collection.insert_one(user)
    return {"message": "Utilisateur inscrit", "id": str(result.inserted_id)}, 201

# Fonction pour connecter un utilisateur
def login_user(data):
    email = data["email"]
    password = data["password"]

    user = users_collection.find_one({"email": email})
    if not user:
        return {"message": "Utilisateur non trouvé"}, 404

    if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        payload = {
            "user_id": str(user["_id"]),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return {"token": token, "message": "Login successful"}, 200
    else:
        return {"message": "Mot de passe incorrect"}, 401
