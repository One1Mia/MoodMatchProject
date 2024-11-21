import sqlite3
import json


 # Sort by mood similarity first, then by genre similarity



# Create a connection to the database
def create_connection():
    conn = sqlite3.connect('movie.db')
    return conn

# Get all movie data from the database
def fetch_all_movies():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, title, sentiment, mood, genre_ids FROM movie_sentiments")
    movies = cursor.fetchall()
    conn.close()
    return movies, len(movies)

# Calculate similarity based on mood overlap 
def calculate_mood_similarity(mood1, mood2):
    # Calculate mood similarity 
    all_moods = set(mood1.keys()).union(set(mood2.keys()))
    
    # Calculate the sum of minimum overlaps
    mood_similarity = sum([min(mood1.get(mood, 0), mood2.get(mood, 0)) for mood in all_moods])

    # Calculate the maximum possible overlap (sum of maximum values from both moods)
    max_possible_similarity = sum([max(mood1.get(mood, 0), mood2.get(mood, 0)) for mood in all_moods])

    # Percentage of mood similarity
    return (mood_similarity / max_possible_similarity) * 100 if max_possible_similarity > 0 else 0

# Calculate genre similarity 
def calculate_genre_similarity(selected_genres, movie_genres):
    # Calculate genre overlap 
    common_genres = len(set(selected_genres).intersection(set(movie_genres)))
    genre_similarity = (common_genres / len(selected_genres)) * 100 if len(selected_genres) > 0 else 0
    return genre_similarity

# Recommend movies based on sentiment, genre overlap, and mood similarity
def recommend_similar_movies(user_movie_title):
    # Get the user's selected movie data
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, title, sentiment, mood, genre_ids FROM movie_sentiments WHERE title LIKE ?", (f"%{user_movie_title}%",))
    selected_movie = cursor.fetchone()
    conn.close()

    if not selected_movie:
        print("Movie not found in the database.")
        return

    selected_movie_id, selected_movie_title, selected_sentiment, selected_mood, selected_genre_ids = selected_movie
    selected_sentiment = json.loads(selected_sentiment)
    selected_mood = json.loads(selected_mood)
    selected_genre_ids = json.loads(selected_genre_ids) 

    # Get all movies from the database for comparison
    all_movies, movie_count = fetch_all_movies()

    # Filter movies with positive sentiment greater than negative + neutral
    filtered_movies = []
    for movie in all_movies:
        movie_id, title, sentiment, mood, genre_ids = movie
        if movie_id != selected_movie_id:  # Skip the movie being compared with itself
            sentiment = json.loads(sentiment)
            mood = json.loads(mood)
            genre_ids = json.loads(genre_ids)

            # Check sentiment condition: Only include if positive > neutral + negative
            if sentiment["positive"] <= (sentiment["neutral"] + sentiment["negative"]):
                continue  # Skip this movie if the sentiment is not positive enough

            # Calculate genre similarity
            genre_similarity = calculate_genre_similarity(selected_genre_ids, genre_ids)

            # Only add movies with at least the same genres
            if genre_similarity > 0:  # If genre similarity is more than 0%
                filtered_movies.append((movie_id, title, sentiment, mood, genre_ids, genre_similarity))

    # Sort by genre similarity 
    filtered_movies.sort(key=lambda x: x[5], reverse=True)

    # Calculate mood similarity for the top genre-similar movies
    similarities = []
    for movie_id, title, sentiment, mood, genre_ids, genre_similarity in filtered_movies:
        # Calculate mood similarity
        mood_similarity = calculate_mood_similarity(selected_mood, mood)
        
        # Only consider movies with mood similarity > 0
        if mood_similarity > 0:
            similarities.append((title, genre_similarity, mood_similarity))

    # Sort by mood similarity first, then by genre similarity
    similarities.sort(key=lambda x: (x[2], x[1]), reverse=True)

    # Print the top 5 recommended movies with genre and mood similarity percentages
    print(f"\nRecommended movies similar to '{selected_movie_title}':")
    for i, (movie_title, genre_sim, mood_sim) in enumerate(similarities[:5]):
        print(f"{i+1}. {movie_title}")
        print(f"   Genre Similarity: {genre_sim:.2f}%")
        print(f"   Mood Similarity: {mood_sim:.2f}%")


def main():
    user_movie_title = input("Enter the name of a movie: ").strip()

    # Get recommendations based on user input
    recommend_similar_movies(user_movie_title)

if __name__ == "__main__":
    main()
