import requests
import csv
import os

API_KEY = os.getenv("API_KEY")  # Assure-toi que ta clé API est définie dans les variables d'environnement
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_GENRE_URL = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=fr-FR"

def get_genre_mapping():
    response = requests.get(TMDB_GENRE_URL)
    genres = response.json().get("genres", [])
    return {genre["id"]: genre["name"] for genre in genres}

def get_movies():
    genre_map = get_genre_mapping()
    movies = []

    for page in range(1, 500):  # Exemple : 5 pages = 100 films
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=fr-FR&page={page}"
        response = requests.get(url)
        data = response.json()

        for movie in data.get("results", []):
            movie_info = {
                "_id": movie["id"],
                "title": movie["title"],
                "image_url": IMAGE_BASE_URL + movie["poster_path"] if movie.get("poster_path") else "",
                "genres": ", ".join([genre_map.get(gid, "Inconnu") for gid in movie.get("genre_ids", [])]),
                "overview": movie.get("overview", ""),
                "trailer_url": f"https://www.youtube.com/results?search_query={movie['title'].replace(' ', '+')}+bande+annonce"
            }
            movies.append(movie_info)

    return movies

def save_movies_to_csv(movies, filename="movies_data.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["_id", "title", "image_url", "genres", "overview", "trailer_url"])
        writer.writeheader()
        for movie in movies:
            writer.writerow(movie)

# --- Exécution principale ---
movies = get_movies()
save_movies_to_csv(movies)
print("✅ Fichier movies_data.csv généré avec succès.")

