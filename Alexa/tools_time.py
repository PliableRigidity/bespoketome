from datetime import datetime
from config import TIMEZONE
import zoneinfo
from tools_geo import geocode_location

def get_time():
    """Get the current local time in the configured timezone."""
    tz = zoneinfo.ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    return {
        "iso": now.isoformat(timespec='seconds'),
        "tz": TIMEZONE,
        "human": now.strftime("%I:%M %p").lstrip("0"),
        "place": None  # No specific place for local time
    }

def get_time_in(location_name):
    """Get the current local time in a specified location."""
    location = geocode_location(location_name)
    tz_name = zoneinfo.ZoneInfo(location["timezone"])
    now = datetime.now(tz_name)
    place = f'{location["name"]}, {location["country"]}'
    return {
        "place": place,
        "location": place,
        "tz": location["timezone"],
        "iso": now.isoformat(timespec='seconds'),
        "human": now.strftime("%I:%M %p").lstrip("0")
        }

