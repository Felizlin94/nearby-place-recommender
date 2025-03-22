import requests
from app.config import GOOGLE_API_KEY


def search_nearby_places_new(
    lat, lng, radius=1000, place_type="restaurant", max_results=20
):
    url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.formattedAddress,"
            "places.location,places.rating,places.userRatingCount,places.primaryType"
        ),
    }

    body = {
        "includedTypes": [place_type],
        "maxResultCount": max_results,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": float(radius),
            }
        },
    }

    response = requests.post(url, headers=headers, json=body)
    print("Google API Nearby Search Response:", response.json())

    return response.json()


def get_place_details_new(place_id):
    """
    Google Places API v1 Place Details (New) - GET Request
    """
    url = f"https://places.googleapis.com/v1/places/{place_id}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": (
            "id,displayName,formattedAddress,rating,userRatingCount,reviews"
        ),
    }

    response = requests.get(url, headers=headers)
    return response.json()
