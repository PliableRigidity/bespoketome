# config.py
import os

# --- LLM / Planner config ---
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
USE_OLLAMA = os.getenv("USE_OLLAMA", "1") == "1"     # set to 0 to force regex fallback
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# --- Timezone (your local default) ---
TIMEZONE = os.getenv("TIMEZONE", "Europe/London")  # Change to your timezone

# --- Open-Meteo APIs (no keys needed) ---
OPEN_METEO_GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_API_KEY = "22e1474ac45784a18eb8b3cb4de8fe2c"

# --- SearxNG Web Search (local instance) ---
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8888")

# --- Voice Pipeline Config ---
# Wake word detection
WAKE_WORD_MODEL = os.getenv("WAKE_WORD_MODEL", "hey_jarvis")  # or "hey_piper" etc.
WAKE_WORD_SENSITIVITY = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))

# STT - Faster Whisper
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")  # "cuda" for GPU
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

# TTS - Piper
PIPER_MODEL_PATH = os.getenv("PIPER_MODEL_PATH", "C:/Users/IshaanV/piperdata/en_US-lessac-medium.onnx")
PIPER_CONFIG_PATH = os.getenv("PIPER_CONFIG_PATH", "C:/Users/IshaanV/piperdata/en_US-lessac-medium.onnx.json")
PIPER_USE_CUDA = os.getenv("PIPER_USE_CUDA", "false").lower() == "true"

# Audio recording
AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))
AUDIO_RATE = int(os.getenv("AUDIO_RATE", "16000"))
AUDIO_CHUNK = int(os.getenv("AUDIO_CHUNK", "1024"))
AUDIO_DEVICE_INDEX = int(os.getenv("AUDIO_DEVICE_INDEX", "0"))
