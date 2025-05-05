from flask import Blueprint, request, jsonify
from app.services.user_service import register_user, login_user

user_bp = Blueprint("user", __name__)

# Route pour l'inscription
@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    message, status_code = register_user(data)
    return jsonify(message), status_code

# Route pour la connexion
@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    message, status_code = login_user(data)
    return jsonify(message), status_code
