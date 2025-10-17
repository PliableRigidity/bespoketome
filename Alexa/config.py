# config.py
import os

# --- LLM / Planner config ---
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b-instruct")
USE_OLLAMA = os.getenv("USE_OLLAMA", "1") == "1"     # set to 0 to force regex fallback
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# --- Timezone (your local default) ---
TIMEZONE = os.getenv("TIMEZONE", "Europe/London")

# --- Open-Meteo APIs (no keys needed) ---
OPEN_METEO_GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"