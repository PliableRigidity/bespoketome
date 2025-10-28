# BespokeToMe - Local Voice Assistant

A privacy-focused, locally-running voice assistant similar to Alexa or Google Home. Built with open-source tools and designed to run entirely on your machine without cloud dependencies (except for web search via SearxNG).

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Or use setup script
python setup.py

# Install Ollama and pull model
ollama pull llama3.2:3b-instruct

# Configure settings (edit Alexa/config.py)
# Update timezone, Piper model path, etc.

# Run text assistant for testing
cd Alexa && python test_assistant.py

# Or run voice assistant
python Alexa/launch.py
```

## Features

- 🎙️ **Wake Word Detection**: Uses `openwakeword` for hands-free activation
- 🗣️ **Speech-to-Text**: Powered by `faster-whisper` for accurate transcription
- 💬 **Text-to-Speech**: Uses `piper` for natural voice responses
- 🌤️ **Weather Information**: Get current weather for any location
- 🕐 **Time Queries**: Check time in any timezone
- 🔍 **Web Search**: Search the web using local SearxNG instance
- 🤖 **Ollama Integration**: Uses local LLM for intelligent command processing
- 🔒 **Privacy-First**: Everything runs locally on your machine

## Architecture

```
User Speech → Openwakeword → Faster Whisper → Planner (Ollama) 
    → Dispatcher → Tools (Weather/Time/Search) → Piper TTS → Audio Output
```

## Requirements

- Python 3.9+
- Ollama installed and running with a model (e.g., `llama3.2:3b`)
- SearxNG instance (optional, for web search)
- Microphone and speakers/headphones
- CUDA-capable GPU (optional, for faster processing)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for PyAudio on Windows:**
```bash
# PyAudio may require additional installation
# Download appropriate wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```

### 2. Install Ollama

Download and install from [ollama.ai](https://ollama.ai)

Pull a lightweight model:
```bash
ollama pull llama3.2:3b-instruct
```

### 3. Install SearxNG (Optional, for web search)

For Docker (recommended):
```bash
docker run -d -p 8080:8080 --name searxng searxng/searxng
```

For manual installation, see [SearxNG docs](https://docs.searxng.org/admin/installation.html)

### 4. Configure

Edit `Alexa/config.py` to set your preferences:

```python
# Set your local timezone
TIMEZONE = "America/New_York"

# Wake word model (e.g., "hey_jarvis", "hey_piper")
WAKE_WORD_MODEL = "hey_jarvis"

# Whisper model size (base, small, medium, large-v3)
WHISPER_MODEL = "base"

# Piper TTS model path
PIPER_MODEL_PATH = "path/to/your/model.onnx"
```

**Download Piper Models:**
Download from [rhasspy/piper](https://github.com/rhasspy/piper/releases) and update the path in config.py

## Usage

### Text Mode (Testing)

Run the test assistant for quick text-based testing:

```bash
cd Alexa
python test_assistant.py
```

Try commands like:
- "what's the time"
- "what's the time in Tokyo"
- "weather in London"
- "what's the time and weather in New York"
- "search for Python tutorials"

### Check Configuration

Before running, verify your setup:

```bash
cd Alexa
python check_config.py
```

This will check:
- ✅ All dependencies are installed
- ✅ Configuration files exist
- ✅ Ollama is running with models
- ✅ SearxNG is accessible (optional)
- ✅ Piper model is available

### Voice Mode

Start the full voice assistant:

```bash
cd Alexa
python voice_assistant.py
```

Or use the launcher:

```bash
python Alexa/launch.py
```

The assistant will:
1. Listen for the wake word
2. When detected, record your command (5 seconds)
3. Transcribe with Whisper
4. Process with the dispatcher
5. Respond via Piper TTS

Press `Ctrl+C` to exit.

## Project Structure

```
Alexa/
├── config.py              # Configuration settings
├── planner.py             # LLM planner for command routing
├── dispatcher.py          # Tool dispatcher
├── test_assistant.py      # Text-based test interface
├── voice_assistant.py     # Main voice interface
├── tool_weather.py        # Weather API integration
├── tools_time.py          # Time/timezone utilities
├── tools_geo.py           # Geocoding utilities
└── tool_web.py            # Web search integration
```

## Supported Commands

### Time Queries
- "what's the time"
- "what time is it in Tokyo"
- "time in London"

### Weather
- "weather in New York"
- "what's the weather like in Singapore"
- "weather forecast for Tokyo"

### Combined
- "time and weather in London"
- "what's the time and weather in New York"

### Web Search
- "search for Python programming"
- "find information about quantum computing"
- "tell me about the latest news"

## Configuration via Environment Variables

```bash
# Ollama settings
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.2:3b-instruct"
export USE_OLLAMA="1"

# Timezone
export TIMEZONE="America/New_York"

# Wake word
export WAKE_WORD_MODEL="hey_jarvis"
export WAKE_WORD_SENSITIVITY="0.5"

# Whisper (STT)
export WHISPER_MODEL="base"
export WHISPER_DEVICE="cpu"  # or "cuda"
export WHISPER_COMPUTE_TYPE="int8"

# Piper (TTS)
export PIPER_MODEL_PATH="/path/to/model.onnx"
export PIPER_USE_CUDA="false"

# Audio settings
export AUDIO_DEVICE_INDEX="0"
export AUDIO_RATE="16000"
export AUDIO_CHUNK="1024"

# SearxNG
export SEARXNG_URL="http://localhost:8080"
```

## Troubleshooting

### No audio input detected
- Check microphone permissions
- Update `AUDIO_DEVICE_INDEX` in config to match your input device
- Run `python -m pyaudio` to list available devices

### Wake word not detected
- Lower `WAKE_WORD_SENSITIVITY` (e.g., 0.3)
- Speak louder or closer to microphone
- Try different wake word models

### Slow transcription
- Use a smaller Whisper model (base instead of large-v3)
- Enable GPU: set `WHISPER_DEVICE="cuda"` and `WHISPER_COMPUTE_TYPE="float16"`
- Reduce audio recording duration

### Ollama connection errors
- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_URL` matches your instance
- Verify the model exists: `ollama list`

### SearxNG search failures
- Ensure SearxNG is running: `docker ps` (or check service)
- Update `SEARXNG_URL` in config.py
- Test SearxNG directly: `curl "http://localhost:8080/search?q=test"`

## Contributing

This is a personal project designed for local use. Feel free to fork and customize for your needs!

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- [openwakeword](https://github.com/dscripka/openwakeword) - Wake word detection
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Speech transcription
- [piper](https://github.com/rhasspy/piper) - Text-to-speech
- [Ollama](https://ollama.ai/) - Local LLM inference
- [Open-Meteo](https://open-meteo.com/) - Weather data
- [SearxNG](https://searxng.org/) - Web search
