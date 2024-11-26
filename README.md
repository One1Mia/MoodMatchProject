# **MoodMatch Project**
## Project Overview
**MoodMatch** is a recommendation system that suggests movies based on the emotional tone of user reviews. By analyzing the mood profiles of movies, the program provides recommendations that align with the user's preferences, using the principle: “_If you like this, then we think you’ll also like this._” 
This project combines sentiment analysis, web scraping, and data processing to help users find movies tailored to their preferences.

## Key Features
**Sentiment Analysis:** Processes IMDb reviews and analyzes them as they were being added to the database.
> [!NOTE]
> - Found in `sentiment_analysis.py`
> - Database was made using `project.py`
> - Database is found in `database.py` _(Does not need to be run anymore)_
> - Genre in the database were made with `genre.py`

**Recommendation Engine:** Matches movies with a certain scores/grade.
> [!NOTE]
> - Found in `recommendation.py`
> - Only code that needs to be run for the program to work.
> - **Have `movie.db` in the same directory**

**Simple User Interface (UI):** Accepts movie titles as input and displays recommendations intuitively.
> [!NOTE]
> Found in `UI.py`

## How to Install and Run
**Prerequisites**
1. Python 3.9+
   
**Required Python libraries:**
1. PyTorch 
2. SQLite
3. json

**Install and Run steps**
1. Download the code as a zip file to your local computer
2. Go to your terminal and navigate to wherever you saved the project
3. Once in the project folder run python `recommendation.py`
4. To use the user interface run UI.py
   
