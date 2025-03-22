import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer


def clean_review_text(text):
    # Remove URLs, emojis, and special characters
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def extract_reviews_from_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    reviews = data.get("reviews", [])
    cleaned_reviews = []

    for review in reviews:
        text = review.get("text", "")
        cleaned = clean_review_text(text)
        if cleaned:
            cleaned_reviews.append(cleaned)

    return cleaned_reviews


def get_top_keywords(review_texts, top_k=5):
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(review_texts)
    summed = X.sum(axis=0)
    keywords = [(word, summed[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    sorted_keywords = sorted(keywords, key=lambda x: x[1], reverse=True)
    return [kw for kw, _ in sorted_keywords[:top_k]]
