import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from database.mongo import items_collection 

load_dotenv()
API_KEY = os.getenv("API_KEY")
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_GENRE_URL = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=fr-FR"

async def fetch_json(session, url):
    async with session.get(url) as response:
        return await response.json()

async def get_genre_mapping(session):
    response = await fetch_json(session, TMDB_GENRE_URL)
    genres = response.get("genres", [])
    return {genre["id"]: genre["name"] for genre in genres}

async def get_movie_details(session, movie_id):
    movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=fr-FR&append_to_response=credits"
    movie_details = await fetch_json(session, movie_details_url)

    cast_data = movie_details.get("credits", {}).get("cast", [])
    sorted_cast = sorted(cast_data, key=lambda actor: actor.get("order", 999))
    cast = [actor["name"] for actor in sorted_cast[:5]]

    director = next((person["name"] for person in movie_details.get("credits", {}).get("crew", []) if person["job"] == "Director"), None)

    return cast, director

async def get_movie_overview(session, movie_id):
    url_fr = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=fr-FR"
    overview_fr = (await fetch_json(session, url_fr)).get("overview", "").strip()

    if not overview_fr:
        url_en = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        overview_en = (await fetch_json(session, url_en)).get("overview", "").strip()
        return overview_en
    return overview_fr

async def fetch_and_save_movies():
    async with aiohttp.ClientSession() as session:
        genre_map = await get_genre_mapping(session)
        tasks = []

        for page in range(1, 51):
            url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=fr-FR&page={page}"
            response = await fetch_json(session, url)

            for movie in response.get("results", []):
                movie_id = movie["id"]
                tasks.append(fetch_movie_data(session, movie, genre_map))

        results = await asyncio.gather(*tasks)
        return results

async def fetch_movie_data(session, movie, genre_map):
    cast, director = await get_movie_details(session, movie["id"])
    overview = await get_movie_overview(session, movie["id"])

    movie_info = {
        "_id": movie["id"],
        "title": movie["title"],
        "image_url": IMAGE_BASE_URL + movie["poster_path"] if movie.get("poster_path") else "",
        "genres": [genre_map.get(gid, "Inconnu") for gid in movie.get("genre_ids", [])],
        "overview": overview,
        "trailer_url": f"https://www.youtube.com/results?search_query={movie['title'].replace(' ', '+')}+bande+annonce",
        "rating": movie.get("vote_average", 0),  # ⭐ Ajout de la note moyenne
        "cast": cast,
        "director": director
    }

    items_collection.update_one(
        {"_id": movie_info["_id"]},
        {"$set": movie_info},
        upsert=True
    )

if __name__ == "__main__":
    asyncio.run(fetch_and_save_movies())
