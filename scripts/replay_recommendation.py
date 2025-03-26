import os
import json
import argparse
from app.langchain_recommender import recommend_from_raw_places
from app.utils import log_ingestion


def load_places_from_folder(folder_path):
    places = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            try:
                with open(
                    os.path.join(folder_path, filename), "r", encoding="utf-8-sig"
                ) as f:
                    places.append(json.load(f))
            except Exception as e:
                print(f"Skipping {filename} due to error: {e}")
    return places


def save_to_log(query, result, source_folder):
    log_ingestion(
        {
            "route": "replay_recommendation",
            "source_folder": source_folder,
            "query": query,
            "file_count": len(result),
            "result": result,
        }
    )


def remove_non_ascii(text):
    return "".join(c for c in text if ord(c) < 128)


def print_safely(obj):
    try:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    except UnicodeEncodeError:
        # Fallback for terminals that can't render full Unicode
        print(remove_non_ascii(json.dumps(obj, indent=2, ensure_ascii=False)))


def main():
    parser = argparse.ArgumentParser(
        description="Replay recommendation using saved place .json files."
    )
    parser.add_argument(
        "folder", help="Folder containing place .json files (e.g., data/raw)"
    )
    parser.add_argument(
        "query", help="What the user is asking for (e.g., 'spicy ramen outdoor')"
    )
    parser.add_argument(
        "--lang",
        default="zh-TW",
        help="Optional language code for GPT output (e.g., en, zh-TW)",
    )

    args = parser.parse_args()
    places = load_places_from_folder(args.folder)

    if not places:
        print("No .json files found in the folder.")
        return

    result = recommend_from_raw_places(args.query, places, lang=args.lang)

    print("\n=== GPT Recommendations ===")
    print_safely(result)

    save_to_log(args.query, result, args.folder)


if __name__ == "__main__":
    main()
