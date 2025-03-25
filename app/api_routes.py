from fastapi import APIRouter, Query
from app.place_fetcher import search_nearby_places, get_place_details, geocode_address
from app.utils import save_raw_json
import json
import os

router = APIRouter()


@router.get("/fetch-reviews")
def fetch_reviews(
    lat: float = Query(..., description="Latitude of the location"),
    lng: float = Query(..., description="Longitude of the location"),
    radius: int = Query(800, description="Search radius in meters"),
    place_type: str = Query("restaurant", description="Type of place to search"),
    max_results: int = Query(20, description="Max number of places to fetch (max 20)"),
    lang: str = Query("zh-TW", description="Preferred language (e.g. zh-TW, ja, en)"),
):
    data = search_nearby_places(lat, lng, radius, place_type, max_results)
    places = data.get("places", [])
    saved_files = []

    for place in places:
        place_id = place.get("id")
        if place_id:
            details = get_place_details(place_id, lang=lang)
            filename = f"{place_id}.json"
            save_raw_json(details, filename)
            saved_files.append(filename)

    return {
        "message": f"{len(saved_files)} places fetched and saved.",
        "files": saved_files,
    }


@router.get("/recommend")
def recommend(
    location_name: str = Query(
        None, description="Optional location name (e.g., 'Akihabara Station')"
    ),
    lat: float = Query(None, description="Latitude of center location"),
    lng: float = Query(None, description="Longitude of center location"),
    vibe: str = Query(None, description="Optional vibe keyword to filter places"),
):
    # Step 1: Handle location_name → lat/lng
    if location_name and (lat is None or lng is None):
        lat, lng = geocode_address(location_name)

    # Step 2: Load summaries (already nearby)
    filepath = "data/processed/review_summaries.json"
    if not os.path.exists(filepath):
        return {"message": "Summary file not found."}

    with open(filepath, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    filtered = []

    for place in summaries:
        score = 0

        # Step 3: Vibe matching
        if vibe:
            vibe = vibe.lower()
            if vibe in place.get("vibe", "").lower():
                score += 1
            score += sum(
                1 for kw in place.get("top_keywords", []) if vibe in kw.lower()
            )

            if score == 0:
                continue

        # Add to result
        place_copy = place.copy()
        place_copy["match_score"] = score
        filtered.append(place_copy)

    # Sort by match_score
    filtered.sort(key=lambda x: x.get("match_score", 0), reverse=True)

    return filtered
