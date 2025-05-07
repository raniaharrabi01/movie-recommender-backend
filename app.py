from flask import Flask
from app.routes.user_routes import user_bp  
from app.routes.movie_routes import movie_bp  
from app.routes.favorite_routes import favorites_bp  
from app.routes.recommending_route import recommendation_bp  
from scheduler import start_scheduler
from flask_cors import CORS

app = Flask(__name__)

# Enregistrer la Blueprint 'user_bp' pour la gestion des utilisateurs
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(movie_bp, url_prefix='/movie')
app.register_blueprint(favorites_bp, url_prefix='/favorite')
app.register_blueprint(recommendation_bp, url_prefix='/recommending')


if __name__ == "__main__":
    app.run(debug=True)
