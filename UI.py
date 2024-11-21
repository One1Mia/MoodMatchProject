import sqlite3
import json
from tkinter import Tk, Label, Entry, Button, Text, Listbox, Scrollbar, END, VERTICAL, RIGHT, Y

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


# Get all movie titles from the database
def fetch_all_movie_titles():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM movie_sentiments")
    movies = cursor.fetchall()
    conn.close()
    return [movie[0] for movie in movies]

# Calculate similarity based on mood overlap
def calculate_mood_similarity(mood1, mood2):
    all_moods = set(mood1.keys()).union(set(mood2.keys()))
    mood_similarity = sum([min(mood1.get(mood, 0), mood2.get(mood, 0)) for mood in all_moods])
    max_possible_similarity = sum([max(mood1.get(mood, 0), mood2.get(mood, 0)) for mood in all_moods])
    return (mood_similarity / max_possible_similarity) * 100 if max_possible_similarity > 0 else 0

# Calculate genre similarity
def calculate_genre_similarity(selected_genres, movie_genres):
    common_genres = len(set(selected_genres).intersection(set(movie_genres)))
    return (common_genres / len(selected_genres)) * 100 if len(selected_genres) > 0 else 0

# Recommend movies based on sentiment, genre overlap, and mood similarity
def recommend_similar_movies(user_movie_title):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, title, sentiment, mood, genre_ids FROM movie_sentiments WHERE title LIKE ?", (f"%{user_movie_title}%",))
    selected_movie = cursor.fetchone()
    conn.close()

    if not selected_movie:
        return f"Movie '{user_movie_title}' not found in the database.", []

    selected_movie_id, selected_movie_title, selected_sentiment, selected_mood, selected_genre_ids = selected_movie
    selected_sentiment = json.loads(selected_sentiment)
    selected_mood = json.loads(selected_mood)
    selected_genre_ids = json.loads(selected_genre_ids)

    all_movies, _ = fetch_all_movies()

    filtered_movies = []
    for movie in all_movies:
        movie_id, title, sentiment, mood, genre_ids = movie
        if movie_id != selected_movie_id:
            sentiment = json.loads(sentiment)
            mood = json.loads(mood)
            genre_ids = json.loads(genre_ids)

            if sentiment["positive"] <= (sentiment["neutral"] + sentiment["negative"]):
                continue

            genre_similarity = calculate_genre_similarity(selected_genre_ids, genre_ids)

            if genre_similarity > 0:
                filtered_movies.append((movie_id, title, sentiment, mood, genre_ids, genre_similarity))

    filtered_movies.sort(key=lambda x: x[5], reverse=True)

    similarities = []
    for movie_id, title, sentiment, mood, genre_ids, genre_similarity in filtered_movies:
        mood_similarity = calculate_mood_similarity(selected_mood, mood)
        if mood_similarity > 0:
            similarities.append((title, genre_similarity, mood_similarity))

    similarities.sort(key=lambda x: (x[2], x[1]), reverse=True)

    recommendations = []
    for title, genre_sim, mood_sim in similarities[:5]:
        recommendations.append(f"{title}\n   Genre Similarity: {genre_sim:.2f}%\n   Mood Similarity: {mood_sim:.2f}%")
    
    return f"Recommended movies similar to '{selected_movie_title}':", recommendations

# Tkinter UI setup
def get_recommendations():
    user_movie_title = movie_input.get().strip()
    result_label.config(text="Loading recommendations...")
    recommendations, movies_list = recommend_similar_movies(user_movie_title)

    result_label.config(text=recommendations)
    recommendations_text.delete(1.0, END)
    recommendations_text.insert(END, "\n".join(movies_list))

def load_movie_titles():
    movie_titles = fetch_all_movie_titles()
    movie_listbox.delete(0, END)
    for title in movie_titles:
        movie_listbox.insert(END, title)

# Create the main Tkinter window
root = Tk()
root.title("MoodMatch")

# Input label and entry field
Label(root, text="Enter the name of a movie:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
movie_input = Entry(root, width=50)
movie_input.grid(row=0, column=1, padx=10, pady=5)

# Submit button
Button(root, text="Get Recommendations", command=get_recommendations).grid(row=0, column=2, padx=10, pady=5)

# Scrollable movie listbox with scrollbar
Label(root, text="Movie List:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
scrollbar = Scrollbar(root, orient=VERTICAL)
movie_listbox = Listbox(root, yscrollcommand=scrollbar.set, height=15, width=50)
scrollbar.config(command=movie_listbox.yview)
scrollbar.grid(row=2, column=2, sticky="ns")
movie_listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

# Load movie titles into the listbox
load_movie_titles()

# Result label
result_label = Label(root, text="")
result_label.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

# Recommendations display
recommendations_text = Text(root, height=15, width=80)
recommendations_text.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

# Run the Tkinter event loop
root.mainloop()
