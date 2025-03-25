import requests
from app.config import GOOGLE_API_KEY


def search_nearby_places(lat, lng, radius=800, place_type="restaurant", max_results=20):
    url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": ("places.id"),
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
    print(
        "Google API Nearby Search Response:",
        len(response.json().get("places", [])),
        "places.",
    )

    return response.json()


def get_place_details(place_id, lang="zh-TW"):
    url = f"https://places.googleapis.com/v1/places/{place_id}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": (
            "id,displayName,formattedAddress,rating,userRatingCount,types,googleMapsUri,priceRange,"
            "allowsDogs,delivery,dineIn,goodForChildren,goodForGroups,goodForWatchingSports,menuForChildren,"
            "liveMusic,parkingOptions,paymentOptions,outdoorSeating,reservable,restroom,takeout,servesBeer,"
            "servesBreakfast,servesBrunch,servesCocktails,servesCoffee,servesDessert,servesDinner,servesLunch,"
            "servesVegetarianFood,servesWine,currentOpeningHours,editorialSummary,reviews"
        ),
        "Accept-Language": lang,
    }

    response = requests.get(url, headers=headers)
    return response.json()


def geocode_address(address: str):
    """Converts a place name or address into lat/lng using the Geocoding API."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        print(f"Geocoding failed for '{address}': {data['status']}")
        return None, None
