import requests
import sqlite3

# TMDB API Configuration
API_KEY = "e3eafb9029e2afac2596e27c4206659c"
BASE_URL = "https://api.themoviedb.org/3/movie"
LANGUAGE = "en-US"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Database connection
def create_connection():
    conn = sqlite3.connect('movie.db')
    return conn

# Get all movie IDs from the database
def fetch_movie_ids():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id FROM movie_sentiments")
    movie_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return movie_ids

def fetch_poster_url(movie_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}", params={"api_key": API_KEY})
    if response.status_code == 200:
        movie_data = response.json()
        poster_path = movie_data.get("poster_path")
        poster_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None
        return poster_url
    else:
        print(f"Error fetching data for movie_id {movie_id}")
        return None

def update_poster_urls(movie_id, poster_url):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
            UPDATE movie_sentiments
            SET poster_url = ?
            WHERE movie_id = ?
        ''', (poster_url, movie_id))
    conn.commit()
    conn.close()

def save_images_to_database():
    conn = sqlite3.connect("movie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, poster_url FROM movie_sentiments")
    movies = cursor.fetchall()

    for movie_id, poster_url in movies:
        try:
            response = requests.get(poster_url)
            response.raise_for_status()
            image_data = response.content  # Get binary content of the image

            # Update the database with the image binary data
            cursor.execute(
                "UPDATE movie_sentiments SET poster_image = ? WHERE movie_id = ?",
                (image_data, movie_id),
            )
            print(f"Saved image for movie ID {movie_id}")
        except Exception as e:
            print(f"Failed to download image for movie ID {movie_id}: {e}")

    conn.commit()
    conn.close()

def main():
    # Get all movie IDs from the database
    movie_ids = fetch_movie_ids()

    for movie_id in movie_ids:
        print(f"Processing movie_id {movie_id}")

        # Get poster_urls from TMDB API
        poster_url = fetch_poster_url(movie_id)

        # Update the database with the poster_urls
        if poster_url:
            update_poster_urls(movie_id, poster_url)
            print(f"Updated poster_url for movie_id {movie_id}")
        else:
            print(f"Skipping movie_id {movie_id} due to missing poster_ur")

    print("Saving images to database...")
    save_images_to_database()

if __name__ == "__main__":
    main()

