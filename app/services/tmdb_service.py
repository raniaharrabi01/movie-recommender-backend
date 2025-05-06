import requests, os
from dotenv import load_dotenv
from database.mongo import items_collection

load_dotenv()
API_KEY = os.getenv("API_KEY")
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_GENRE_URL = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=fr-FR"

def get_genre_mapping():
    response = requests.get(TMDB_GENRE_URL)
    genres = response.json().get("genres", [])
    return {genre["id"]: genre["name"] for genre in genres}

# Nouvelle fonction pour récupérer le cast et le director
def get_movie_details(movie_id):
    movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=fr-FR&append_to_response=credits"

    response = requests.get(movie_details_url)
    movie_details = response.json()

    # Extraction des 5 premiers acteurs selon l'ordre d'importance
    cast_data = movie_details.get("credits", {}).get("cast", [])
    sorted_cast = sorted(cast_data, key=lambda actor: actor.get("order", 999))
    cast = [actor["name"] for actor in sorted_cast[:5]]


    # Extraction du réalisateur
    director = next((person["name"] for person in movie_details.get("credits", {}).get("crew", []) if person["job"] == "Director"), None)

    return cast, director

def fetch_and_save_movies():
    genre_map = get_genre_mapping()
    movies = []

    for page in range(1, 51):
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=fr-FR&page={page}"
        response = requests.get(url)
        data = response.json()

        for movie in data.get("results", []):
            # Récupération des détails du film (cast, director)
            cast, director = get_movie_details(movie["id"])

            movie_info = {
                "_id": movie["id"],
                "title": movie["title"],
                "image_url": IMAGE_BASE_URL + movie["poster_path"] if movie.get("poster_path") else "",
                "genres": [genre_map.get(gid, "Inconnu") for gid in movie.get("genre_ids", [])],
                "overview": movie.get("overview", ""),
                "trailer_url": f"https://www.youtube.com/results?search_query={movie['title'].replace(' ', '+')}+bande+annonce",
                "cast": cast,  # Ajout des acteurs
                "director": director  # Ajout du réalisateur
            }
            
            # 🔄 Mise à jour si le film existe, sinon insertion
            items_collection.update_one(
                {"_id": movie_info["_id"]},
                {"$set": movie_info},
                upsert=True
            )
            movies.append(movie_info)
    return movies
