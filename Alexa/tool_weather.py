import requests
from datetime import datetime, timezone

from config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL
from tools_geo import geocode_location

def get_weather(location_name):
    """Get current weather for a specified location using OpenWeather."""
    if not OPENWEATHER_API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY is not set in config or environment.")

    # 1) Geocode location (still via Open-Meteo)
    location = geocode_location(location_name)
    lat, lon = location["latitude"], location["longitude"]

    # 2) Call OpenWeather current weather API
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",  # return °C, m/s
    }

    response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()

    # 3) Parse response
    weather_list = data.get("weather", [])
    weather = weather_list[0] if weather_list else {}
    main = data.get("main", {})
    wind = data.get("wind", {})

    # Description: prefer full description, fallback to 'main'
    desc = (weather.get("description") or weather.get("main") or "").lower()

    # Temperature in °C (because units=metric)
    temp_c = main.get("temp")

    # Wind: OpenWeather returns m/s in metric; convert to km/h
    wind_ms = wind.get("speed")
    wind_kmh = wind_ms * 3.6 if wind_ms is not None else None

    # Time: OpenWeather 'dt' is a Unix timestamp (UTC)
    dt_unix = data.get("dt")
    time_iso = (
        datetime.fromtimestamp(dt_unix, tz=timezone.utc).isoformat()
        if dt_unix
        else None
    )

    # Place label: prefer geocoded name + country for consistency
    place = f'{location["name"]}, {location.get("country", "").strip()}'.strip(", ")

    return {
        "place": place,
        "location": place,
        "temperature_c": temp_c,
        "temperature": temp_c,
        "latitude": lat,
        "longitude": lon,
        "wind_speed_kmh": wind_kmh,
        "windspeed": wind_kmh,
        "weather_desc": desc,
        "weather_description": desc,
        "time": time_iso,
    }
