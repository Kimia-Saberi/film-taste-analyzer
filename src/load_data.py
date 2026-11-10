import pandas as pd

RAW = "data/raw"


def load_films():
    watched = pd.read_csv(f"{RAW}/watched.csv")
    ratings = pd.read_csv(f"{RAW}/ratings.csv")

    films = watched.merge(
        ratings[["Letterboxd URI", "Rating"]],
        on="Letterboxd URI",
        how="left",
    )

    films = films.rename(columns={
        "Date": "logged_date",
        "Name": "title",
        "Year": "year",
        "Letterboxd URI": "letterboxd_uri",
        "Rating": "rating",
    })
    films["logged_date"] = pd.to_datetime(films["logged_date"])
    return films


if __name__ == "__main__":
    films = load_films()
    print(films.shape)
    print(films.head())
    print("Rated:", films["rating"].notna().sum())
    print(films["rating"].value_counts().sort_index())
    films.to_csv("data/processed/films.csv", index=False)