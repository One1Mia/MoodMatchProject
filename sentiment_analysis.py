from transformers import pipeline

# Load pre-trained NLP models for sentiment and mood analysis from Hugging Face
sentiment_analyzer = pipeline("sentiment-analysis")
emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

# Anlyse sentiment and mood of reviews
def analyze_reviews(reviews):
    analysis = {"sentiment": {"positive": 0, "neutral": 0, "negative": 0}, "moods": {}}

    for review in reviews:
        # Sentiment analysis
        sentiment_result = sentiment_analyzer(review, truncation=True)
        sentiment = sentiment_result[0]["label"].lower()
        analysis["sentiment"][sentiment] += 1

        # Mood classification
        mood_result = emotion_classifier(review, truncation=True)
        mood = mood_result[0]["label"]
        analysis["moods"][mood] = analysis["moods"].get(mood, 0) + 1

    return analysis
