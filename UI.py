import sqlite3
import io
import json
import customtkinter as ctk
from PIL import Image

# Database connection
def create_connection():
    conn = sqlite3.connect("movie.db")
    return conn

# Fetch all movies (full data)
def fetch_all_movies():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, title, sentiment, mood, genre_ids FROM movie_sentiments")
    movies = cursor.fetchall()
    conn.close()
    return movies

# Fetch movies with images from the database
def fetch_movies_with_images(query=""):
    conn = create_connection()
    cursor = conn.cursor()

    # Adjust the query to filter movies based on the title (using LIKE for partial matching)
    cursor.execute("SELECT title, poster_image FROM movie_sentiments WHERE title LIKE ?", ('%' + query + '%',))
    movies = cursor.fetchall()
    conn.close()

    movie_data = []
    for title, image_blob in movies:
        if image_blob:
            image = Image.open(io.BytesIO(image_blob))
            movie_data.append((title, image))
    return movie_data

# Update the movie display based on the search query
def search_movies():
    query = search_entry.get().strip()  # Get the search query from the entry widget
    # Clear the scrollable frame to update with new search results
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Fetch filtered movies based on the search query
    movies = fetch_movies_with_images(query)

    # Display movies in a 4-column grid
    row = 0
    col = 0
    for title, image in movies:
        img = ctk.CTkImage(light_image=image.resize((150, 225), Image.Resampling.LANCZOS), size=(150, 225))

        # Create a frame for each movie (image + title)
        movie_frame = ctk.CTkFrame(scrollable_frame)
        movie_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Add the movie poster
        img_label = ctk.CTkLabel(movie_frame, image=img, text="")
        img_label.image = img  # Prevent garbage collection
        img_label.pack(pady=5)

        # Add the movie title with an updated command
        title_button = ctk.CTkButton(
            movie_frame, text=title, font=("Arial", 14),
            command=lambda t=title: open_movie_screen(t)  # Ensure correct reference of 't'
        )
        title_button.pack()

        # Move to the next column, or the next row if we've filled 4 columns
        col += 1
        if col == 4:
            col = 0
            row += 1

# Function to open a new screen for the movie title and display recommendations
def open_movie_screen(movie_title):
    new_window = ctk.CTk()
    new_window.geometry("800x600")
    new_window.title(f"Movie: {movie_title}")

    # Get movie recommendations
    recommendations_label, recommendations_list = recommend_similar_movies(movie_title)

    # Create a label to show recommendations
    recommendations_label_widget = ctk.CTkLabel(new_window, text=recommendations_label, font=("Arial", 18))
    recommendations_label_widget.pack(pady=10)

    # Create a text area to display the list of recommendations
    recommendations_text = ctk.CTkTextbox(new_window, height=300, width=600)
    recommendations_text.pack(pady=20)

    # Insert the recommendations into the textbox
    for recommendation in recommendations_list:
        recommendations_text.insert(ctk.END, recommendation + "\n")

    # Start the new window's loop
    new_window.mainloop()

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
    try:
        # Fetch the selected movie details
        cursor.execute(
            "SELECT movie_id, title, sentiment, mood, genre_ids FROM movie_sentiments WHERE title LIKE ?",
            (f"%{user_movie_title}%",)
        )
        selected_movie = cursor.fetchone()
    except sqlite3.Error as e:
        return f"Error accessing the database: {e}", []
    finally:
        conn.close()

    # If no movie is found
    if not selected_movie:
        return f"Movie '{user_movie_title}' not found in the database.", []

    # Parse the selected movie details
    selected_movie_id, selected_movie_title, selected_sentiment, selected_mood, selected_genre_ids = selected_movie

    # Handle JSON fields safely
    try:
        selected_mood = json.loads(selected_mood)
        selected_genre_ids = json.loads(selected_genre_ids) if selected_genre_ids else []
    except json.JSONDecodeError:
        return f"Error parsing data for '{user_movie_title}'.", []

    # Fetch all movies for comparison
    all_movies = fetch_all_movies()

    # Filter and calculate similarities
    filtered_movies = []
    for movie in all_movies:
        movie_id, title, sentiment, mood, genre_ids = movie

        # Skip the selected movie itself
        if movie_id == selected_movie_id:
            continue

        # Parse JSON fields for the current movie
        try:
            sentiment = json.loads(sentiment)
            mood = json.loads(mood)
            genre_ids = json.loads(genre_ids) if genre_ids else []
        except json.JSONDecodeError:
            continue  # Skip movies with invalid JSON data

        # Filter out movies with low positive sentiment
        if sentiment.get("positive", 0) <= (sentiment.get("neutral", 0) + sentiment.get("negative", 0)):
            continue

        # Calculate genre similarity
        genre_similarity = calculate_genre_similarity(selected_genre_ids, genre_ids)
        if genre_similarity > 0:
            filtered_movies.append((movie_id, title, sentiment, mood, genre_ids, genre_similarity))

    # Sort by genre similarity
    filtered_movies.sort(key=lambda x: x[5], reverse=True)

    # Calculate mood similarity for the top genre matches
    similarities = []
    for movie_id, title, sentiment, mood, genre_ids, genre_similarity in filtered_movies:
        mood_similarity = calculate_mood_similarity(selected_mood, mood)
        if mood_similarity > 0:
            similarities.append((title, genre_similarity, mood_similarity))

    # Sort by mood similarity (primary) and genre similarity (secondary)
    similarities.sort(key=lambda x: (x[2], x[1]), reverse=True)

    # Create the recommendations list
    recommendations = []
    for title, genre_sim, mood_sim in similarities[:5]:  # Top 5 recommendations
        recommendations.append(
            f"{title}\n   Genre Similarity: {genre_sim:.2f}%\n   Mood Similarity: {mood_sim:.2f}%"
        )

    return f"MoodMatches for '{selected_movie_title}':", recommendations

# Create the main Tkinter window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("800x600")
root.title("MoodMatch")

# Create an input frame for the search box and button
input_frame = ctk.CTkFrame(root)
input_frame.pack(padx=20, pady=10, fill="x")

# Create the search box (Entry widget) and button
search_label = ctk.CTkLabel(input_frame, text="Search movie:", font=('Calibri', 16))
search_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

# Allows users to input movie search
search_entry = ctk.CTkEntry(input_frame, width=400, font=('Calibri', 16))
search_entry.grid(row=0, column=1, padx=10, pady=5)

# Create a search button
search_button = ctk.CTkButton(input_frame, text="Search", command=search_movies, font=('Calibri', 16))
search_button.grid(row=0, column=2, padx=10, pady=5)

# Create a scrollable frame for movie posters and titles
scrollable_frame = ctk.CTkScrollableFrame(root, width=800, height=400)
scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Initially display all movies when no search is provided
search_movies()  # This will populate the scrollable frame with all movies

# Run the Tkinter event loop
root.mainloop()
