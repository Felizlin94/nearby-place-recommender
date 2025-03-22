from fastapi import APIRouter, Query
from app.place_fetcher import search_nearby_places_new, get_place_details_new
from app.utils import save_raw_json

router = APIRouter()

@router.get("/fetch-reviews")
def fetch_reviews(
    lat: float = Query(..., description="Latitude of the location"),
    lng: float = Query(..., description="Longitude of the location"),
    place_type: str = Query("restaurant", description="Type of place to search"),
    radius: int = Query(1000, description="Search radius in meters"),
    max_results: int = Query(10, description="Max number of places to fetch (max 20)"),
):
    data = search_nearby_places_new(lat, lng, radius, place_type, max_results)
    places = data.get("places", [])
    saved_files = []

    for place in places:
        place_id = place.get("id")
        if place_id:
            details = get_place_details_new(place_id)
            filename = f"{place_id}.json"
            save_raw_json(details, filename)
            saved_files.append(filename)

    return {
        "message": f"{len(saved_files)} places fetched and saved.",
        "files": saved_files,
    }


# for testing
@router.get("/recommend")
def recommend():
    return {"message": "Here is your recommendation"}


@router.get("/places")
def get_places():
    return {"message": "Nearby places"}
