from apscheduler.schedulers.background import BackgroundScheduler
from app.services.tmdb_service import fetch_and_save_movies
from app.ai.data_preparation import prepare_data
from app.ai.train_model import train_knn_model


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_recommendation_model, 'interval', days=1)  # tous les jours
    scheduler.start()

def update_recommendation_model():
    try:
        print("🔄 Synchronisation des données TMDB...")
        fetch_and_save_movies()
        print("📊 Préparation des données...")
        prepare_data()
        print("🧠 Réentraînement du modèle de recommandation...")
        train_knn_model()
        print("✅ Mise à jour terminée.")
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")
