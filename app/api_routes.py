from fastapi import APIRouter, Query
from app.place_fetcher import search_nearby_places, get_place_details, geocode_address
from app.langchain_recommender import recommend_from_raw_places
from app.utils import save_raw_json, log_ingestion
from typing import Optional, Tuple, List, Dict

router = APIRouter()


def get_detailed_places(
    location_name: Optional[str],
    lat: Optional[float],
    lng: Optional[float],
    radius: int,
    place_type: str,
    max_results: int,
    lang: str,
) -> Tuple[List[Dict], Optional[str], Optional[str]]:
    if location_name and (lat is None or lng is None):
        lat, lng = geocode_address(location_name)
        if lat is None or lng is None:
            return [], None, f"Failed to geocode '{location_name}'."

    if lat is None or lng is None:
        return [], None, "Please provide either lat/lng or location_name."

    data = search_nearby_places(lat, lng, radius, place_type, max_results, lang)
    places = data.get("places", [])
    detailed_places = []

    for place in places:
        place_id = place.get("id")
        if place_id:
            details = get_place_details(place_id, lang=lang)
            if details:
                detailed_places.append(details)

    return detailed_places, f"{lat},{lng}", None


@router.get("/fetch-reviews")
def fetch_reviews(
    location_name: str = Query(
        None, description="Optional place name (e.g. 'Shinjuku Station')"
    ),
    lat: float = Query(None, description="Latitude of location"),
    lng: float = Query(None, description="Longitude of location"),
    radius: int = Query(800, description="Search radius in meters"),
    place_type: str = Query("restaurant", description="Type of place to search"),
    max_results: int = Query(20, description="Max number of places to fetch"),
    lang: str = Query("zh-TW", description="Preferred language (e.g. zh-TW, ja, en)"),
):
    detailed_places, resolved_location, error = get_detailed_places(
        location_name, lat, lng, radius, place_type, max_results, lang
    )

    if error:
        return {"error": error}

    saved_files = []
    for place in detailed_places:
        place_id = place.get("id")
        if place_id:
            filename = f"{place_id}.json"
            save_raw_json(place, filename)
            saved_files.append(filename)

    log_ingestion(
        {
            "route": "/fetch-reviews",
            "location": location_name or resolved_location,
            "file_count": len(saved_files),
            "files": saved_files,
        }
    )

    return {
        "message": f"{len(saved_files)} places fetched and saved.",
        "location": location_name or resolved_location,
        "files": saved_files,
    }


@router.get("/recommend")
def recommend(
    location_name: str = Query(..., description="Place name (e.g. 'Shinjuku Station')"),
    query: str = Query(
        ..., description="User query (e.g. 'spicy ramen outdoor seating')"
    ),
    radius: int = Query(800, description="Search radius in meters"),
    place_type: str = Query("restaurant", description="Type of place to search"),
    max_results: int = Query(20, description="Max number of places to fetch"),
    lang: str = Query("zh-TW", description="Preferred language (e.g. zh-TW, ja, en)"),
):
    detailed_places, resolved_location, error = get_detailed_places(
        location_name, None, None, radius, place_type, max_results, lang
    )

    if error:
        return {"error": error}

    if not detailed_places:
        return {"error": "No detailed places fetched."}

    result = recommend_from_raw_places(query, detailed_places, lang=lang)

    log_ingestion(
        {
            "route": "/recommend",
            "location": location_name,
            "query": query,
            "file_count": len(detailed_places),
            "result": result,
        }
    )

    return {
        "location": location_name,
        "query": query,
        "result": result,
    }
