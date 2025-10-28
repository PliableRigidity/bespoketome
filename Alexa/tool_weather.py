import requests
from config import OPEN_METEO_FORECAST
from tools_geo import geocode_location

WEATHER_CODES = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "freezing rain",
    67: "heavy freezing rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    77: "snow grains",
    80: "light showers",
    81: "moderate showers",
    82: "violent showers",
    85: "light snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail"
}

def get_weather(location_name):
    """Get current weather for a specified location."""
    location = geocode_location(location_name)
    lat, lon = location["latitude"], location["longitude"]
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "timezone": location["timezone"]
    }

    response = requests.get(OPEN_METEO_FORECAST, params=params)
    response.raise_for_status()
    data = response.json()
    current_weather = data.get("current_weather")

    wcode = int(current_weather.get("weather_code", 0))
    desc = WEATHER_CODES.get(wcode, f"code{wcode}")

    temp_c = current_weather.get("temperature_2m")
    wind = current_weather.get("wind_speed_10m")
    time_iso = current_weather.get("time")
    
    place = f'{location["name"]}, {location["country"]}'

    return {
        "place": place,
        "location": place,
        "temperature_c": temp_c,
        "temperature": temp_c,
        "latitude": lat,
        "longitude": lon,
        "wind_speed_kmh": wind,
        "windspeed": wind,
        "weather_desc": desc,
        "weather_description": desc,
        "time": time_iso
    }