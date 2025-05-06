from flask import Flask
from app.routes.user_routes import user_bp  
from app.routes.movie_routes import movie_bp  
from app.routes.rating_routes import rating_bp  
from app.routes.recommending_route import recommendation_bp  
from scheduler import start_scheduler

app = Flask(__name__)

# Enregistrer la Blueprint 'user_bp' pour la gestion des utilisateurs
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(movie_bp, url_prefix='/movie')
app.register_blueprint(rating_bp, url_prefix='/rating')
app.register_blueprint(recommendation_bp, url_prefix='/recommending')


# Démarrer le cron job
start_scheduler()

if __name__ == "__main__":
    app.run(debug=True)
