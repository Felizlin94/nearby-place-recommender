import os
import json
from app.nlp_utils import get_top_keywords, extract_reviews_from_json

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "review_summaries.json")


def summarize_all_places():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    summaries = []

    for filename in os.listdir(RAW_DIR):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(RAW_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        place_id = data.get("id")
        name = data.get("displayName", {}).get("text", "Unknown Place")
        reviews = extract_reviews_from_json(filepath)

        if not reviews:
            continue

        top_keywords = get_top_keywords(reviews, top_k=5)
        top_review = max(reviews, key=len)  # Use longest review as top one  <---- logic

        summaries.append(
            {
                "place_id": place_id,
                "name": name,
                "top_keywords": top_keywords,
                "top_review": top_review,
            }
        )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print(f"Summaries written to {OUTPUT_PATH}")


if __name__ == "__main__":
    summarize_all_places()
