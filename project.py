import requests
from sentiment_analysis import analyze_reviews
from database import create_tables, insert_movie_sentiment, fetch_popular_movies, fetch_movie_reviews

# TMDB API Configuration
API_KEY = "e3eafb9029e2afac2596e27c4206659c"
BASE_URL = "https://api.themoviedb.org/3"

def main():
    create_tables() 
    print("Fetching popular movies...")
    popular_movies = fetch_popular_movies()

    for movie in popular_movies:
        print(f"Processing movie: {movie['title']} ({movie['release_date']})")

        # Get reviews for the current movie
        reviews = fetch_movie_reviews(movie['id'])
        if reviews:
            print(f"Fetching reviews for {movie['title']}...")

            # Analyze sentiment and mood for the selected movie
            analysis = analyze_reviews(reviews)
            sentiment = analysis["sentiment"]
            mood = analysis["moods"]

            print(f"Sentiment Analysis: {sentiment}")
            print(f"Mood Distribution: {mood}")

            # Store the sentiment and mood counts in the database
            insert_movie_sentiment(movie['id'], movie['title'], sentiment, mood)

        print(f"Finished processing movie: {movie['title']}")

if __name__ == "__main__":
    main()
