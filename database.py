import sqlite3
import json
import requests

# Database connection and table creation
def create_connection():
    conn = sqlite3.connect('movie.db')
    return conn

# Creates table movie_sentimentsin the database if it does not exist 
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movie_sentiments (
            movie_id INTEGER PRIMARY KEY,
            title TEXT,
            sentiment TEXT,
            mood TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Inserts sentiment and mood analysis data into the database
def insert_movie_sentiment(movie_id, title, sentiment, mood):
    conn = create_connection()
    cursor = conn.cursor()

    # Convert sentiment and mood dictionaries to JSON strings for storage
    sentiment_json = json.dumps(sentiment)
    mood_json = json.dumps(mood)

    cursor.execute('''
        INSERT OR REPLACE INTO movie_sentiments (movie_id, title, sentiment, mood)
        VALUES (?, ?, ?, ?)
    ''', (movie_id, title, sentiment_json, mood_json))
    conn.commit()
    conn.close()

# Get popular movies from the TMDb API, returns a list of dictionaries containing data about the movie
def fetch_popular_movies(total_pages=50):
    all_movies = []  # List to store movies across all fetched pages
    
    for page in range(1, total_pages + 1):
        print(f"Fetching page {page} of popular movies...")
        
        # API parameters
        params = {
            "api_key": "e3eafb9029e2afac2596e27c4206659c",
            "language": "en-US",
            "page": page
        }
        
        # GET request to the TMDb API for popular movies
        response = requests.get("https://api.themoviedb.org/3/movie/popular", params=params)
        
        if response.status_code == 200:
            # Parse the response JSON and extend the movie list
            data = response.json()
            all_movies.extend(data.get("results", []))
        else:
            print(f"Error fetching data for page {page}. HTTP Status: {response.status_code}")
            break  # Stop getting data if an error occurs
    
    return all_movies

# Get reviews for a movie from the TMDb API
def fetch_movie_reviews(movie_id):
   
    # API parameters
    params = {"api_key": "e3eafb9029e2afac2596e27c4206659c"}
    
    # Make a GET request to the TMDb API for movie reviews
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/reviews", params=params)
    
    if response.status_code == 200:
        # Parse the response JSON and extract the review content
        data = response.json()
        return [review["content"] for review in data.get("results", [])]
    
    # Return an empty list if no reviews are found or an error occurs
    return []
