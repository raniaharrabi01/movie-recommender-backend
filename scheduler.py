from apscheduler.schedulers.background import BackgroundScheduler
from app.services.tmdb_service import fetch_and_save_movies

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_save_movies, 'interval', days=1)  # tous les jours
    scheduler.start()
