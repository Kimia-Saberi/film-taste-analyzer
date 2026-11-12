import os

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

if not API_KEY:
    raise SystemExit("TMDB_API_KEY is missing. Check your .env file.")


def search_movie(title, year):
    response = requests.get(
        f"{BASE_URL}/search/movie",
        params={"api_key": API_KEY, "query": title, "year": year},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()

def get_movie_details(movie_id):
    response = requests.get(
        f"{BASE_URL}/movie/{movie_id}",
        params={"api_key": API_KEY, "append_to_response": "credits"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def extract_info(details):
    directors = [
        person["name"]
        for person in details["credits"]["crew"]
        if person["job"] == "Director"
    ]
    return {
        "tmdb_id": details["id"],
        "title": details["title"],
        "genres": [g["name"] for g in details["genres"]],
        "countries": [c["iso_3166_1"] for c in details["production_countries"]],
        "runtime": details["runtime"],
        "directors": directors,
        "tmdb_rating": details["vote_average"],
    }

if __name__ == "__main__":
    data = search_movie("Parasite", 2019)
    first = data["results"][0]
    details = get_movie_details(first["id"])
    print(extract_info(details))
