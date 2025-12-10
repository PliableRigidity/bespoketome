import requests
from config import OPEN_METEO_GEOCODE

def geocode_location(name):
    """Geocode a location name to latitude and longitude using Open-Meteo Geocoding API."""
    params = {
        "name": name,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    response = requests.get(OPEN_METEO_GEOCODE, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()

    results = data.get("results")
    if not results:
        raise ValueError(f"Could not geocode location: {name}")

    result = results[0]
    return {
        "name": result["name"],
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "country": result.get("country", ""),
        "country_code": result.get("country_code", ""),
        "timezone": result.get("timezone", ""),
    }
