import requests
import sqlite3
import json

# TMDB API Configuration
API_KEY = "e3eafb9029e2afac2596e27c4206659c" 
BASE_URL = "https://api.themoviedb.org/3/movie"
LANGUAGE = "en-US"

# Database connection 
def create_connection():
    conn = sqlite3.connect('movie.db')
    return conn

# Get genre ids for a specific movie from TMDB 
def fetch_genre_ids(movie_id):
    url = f"{BASE_URL}/{movie_id}?language={LANGUAGE}&api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        movie_data = response.json()
        genre_ids = [genre['id'] for genre in movie_data.get('genres', [])]
        return genre_ids
    else:
        print(f"Error fetching data for movie_id {movie_id}")
        return []

# Get all movie IDs from the database
def fetch_movie_ids():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id FROM movie_sentiments")
    movie_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return movie_ids

# Update genre ids in the database
def update_genre_ids(movie_id, genre_ids):
    conn = create_connection()
    cursor = conn.cursor()
    genre_ids_json = json.dumps(genre_ids)  # Convert genre_ids list to JSON 
    cursor.execute('''
        UPDATE movie_sentiments
        SET genre_ids = ?
        WHERE movie_id = ?
    ''', (genre_ids_json, movie_id))
    conn.commit()
    conn.close()

# Update genre_ids for each movie in the database
def main():
    # Get all movie IDs from the database
    movie_ids = fetch_movie_ids()
    
    for movie_id in movie_ids:
        print(f"Processing movie_id {movie_id}")
        
        # Get genre_ids from TMDB API
        genre_ids = fetch_genre_ids(movie_id)
        
        # Update the database with the genre_ids
        if genre_ids:
            update_genre_ids(movie_id, genre_ids)
            print(f"Updated genre_ids for movie_id {movie_id}")
        else:
            print(f"Skipping movie_id {movie_id} due to missing genre_ids")

if __name__ == "__main__":
    main()
