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
    response = requests.get(OPEN_METEO_GEOCODE, params=params)
    response.raise_for_status()
    data = response.json()
    
    result = data["results"][0]
    return {
        "name": result["name"],
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "country": result.get("country", ""),
        "country_code": result.get("country_code", ""),
        "timezone": result.get("timezone", ""),
        }