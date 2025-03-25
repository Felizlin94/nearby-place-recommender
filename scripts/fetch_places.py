from app.place_fetcher import search_nearby_places, get_place_details
from app.utils import save_raw_json


def fetch_places_and_reviews(
    lat, lng, radius=800, place_type="restaurant", max_results=20, lang="zh-TW"
):
    data = search_nearby_places(lat, lng, radius, place_type, max_results)
    places = data.get("places", [])

    for place in places:
        place_id = place.get("id")
        if place_id:
            details = get_place_details(place_id, lang=lang)
            save_raw_json(details, f"{place_id}.json")


if __name__ == "__main__":
    # # Example: Tokyo
    # fetch_places_and_reviews(
    #     35.6895, 139.6917, radius=1000, place_type="restaurant", max_results=10, lang="ja"
    # )
    # Example: Taipei
    fetch_places_and_reviews(
        25.0018,
        121.5391,
        radius=500,
        place_type="restaurant",
        max_results=20,
        lang="zh-TW",
    )
