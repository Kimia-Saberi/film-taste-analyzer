import json
import os
import time
import pandas as pd

import requests

from load_data import load_films
from tmdb import search_movie, get_movie_details, extract_info

CACHE_PATH = "data/cache/tmdb_cache.json"
LIMIT = None  # set to None to run all films
RETRY_MISSING = False


def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def find_exact(results, title):
    for result in results:
        if result["title"].lower() == title.lower() or result["original_title"].lower() == title.lower():
            return result
    return None


def fetch_film(title, year):
    data = search_movie(title, year)
    if data["results"]:
        match = find_exact(data["results"], title) or data["results"][0]
        return extract_info(get_movie_details(match["id"]))

    for nearby_year in (year - 1, year + 1):
        data = search_movie(title, nearby_year)
        match = find_exact(data["results"], title)
        if match:
            return extract_info(get_movie_details(match["id"]))

    return None

def enrich(films, cache):
    todo = films[~films["letterboxd_uri"].isin(list(cache))]
    if LIMIT:
        todo = todo.head(LIMIT)
    print(f"{len(cache)} films already cached, fetching {len(todo)} now")

    for i, row in enumerate(todo.itertuples(), start=1):
        try:
            cache[row.letterboxd_uri] = fetch_film(row.title, row.year)
        except requests.RequestException as error:
            print(f"Error for {row.title} ({row.year}): {error}")
            continue
        if i % 25 == 0:
            save_cache(cache)
            print(f"{i}/{len(todo)} done")
        time.sleep(0.25)

    save_cache(cache)

def build_table(films, cache):
    rows = [
        {"letterboxd_uri": uri, **info}
        for uri, info in cache.items()
        if info is not None
    ]
    tmdb = pd.DataFrame(rows).rename(columns={"title": "tmdb_title"})
    return films.merge(tmdb, on="letterboxd_uri", how="inner")


if __name__ == "__main__":
    films = load_films()
    cache = load_cache()
    if RETRY_MISSING:
        cache = {uri: info for uri, info in cache.items() if info is not None}
    enrich(films, cache)

    not_found = [uri for uri, info in cache.items() if info is None]
    print(f"Cached: {len(cache)}, not found on TMDb: {len(not_found)}")

    films_by_uri = films.set_index("letterboxd_uri")
    for uri in not_found:
        film = films_by_uri.loc[uri]
        print(f"  {film['title']} ({film['year']})")

    table = build_table(films, cache)
    table.to_json(
        "data/processed/films_enriched.json",
        orient="records",
        indent=2,
        force_ascii=False,
        date_format="iso",
    )
    print(f"Saved {len(table)} films with TMDb data")
        