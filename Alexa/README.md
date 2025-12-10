# JARVIS - AI Assistant

A powerful AI assistant with both terminal and web interfaces, featuring context memory, web search, Wikipedia integration, and more.

## Features

- 🤖 **Dual Interface**: Use via terminal or web browser
- 🧠 **Context Memory**: Remembers conversation history
- 🌐 **Web Search**: Powered by local SearXNG instance
- 📚 **Wikipedia Integration**: Extracts full article content
- ⏰ **Time & Weather**: Get current time and weather for any location
- 💬 **Natural Conversations**: Context-aware responses
- 🎨 **Beautiful Web UI**: Modern, responsive design

## Quick Start

### Terminal Interface

```bash
# Run the terminal interface
run.bat

# Or manually:
.venv\Scripts\python.exe main.py
```

### Web Interface

```bash
# Run the web server
run_web.bat

# Or manually:
.venv\Scripts\python.exe web_server.py
```

Then open your browser to: **http://localhost:5000**

## Usage Examples

### Time & Weather
- "What time is it in Tokyo?"
- "Weather in London"
- "Time and weather in New York"

### Information & Knowledge
- "Who is Elon Musk?"
- "What is photosynthesis?"
- "Explain how a car engine works"
- "What are the specs of a Tesla Model 3?"

### Current Events
- "Latest news on AI"
- "Who won the World Cup 2022?"

### Context Commands (Terminal & Web)
- `clear context` - Clear conversation history
- `show context` - View conversation history
- `exit` or `quit` - Exit (terminal only)

## Architecture

### Core Components

- **`main.py`** - Terminal interface
- **`web_server.py`** - Flask web server
- **`dispatcher.py`** - Routes user requests to appropriate tools
- **`planner.py`** - LLM-based intent recognition
- **`context_manager.py`** - Conversation history management
- **`tool_web.py`** - Web search with Wikipedia extraction
- **`tool_weather.py`** - Weather information
- **`tools_time.py`** - Time queries
- **`config.py`** - Configuration settings

### How It Works

1. **User Input** → Terminal or Web UI
2. **Planner** → Analyzes intent using Llama 3.2
3. **Dispatcher** → Calls appropriate tool(s)
4. **Tools** → Execute actions (search, weather, time, etc.)
5. **Response** → Natural language reply
6. **Context** → Saves conversation turn

## Configuration

Edit `config.py` to customize:

```python
# LLM Settings
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:latest"

# Search Settings
SEARXNG_URL = "http://localhost:8888"

# Weather API
OPENWEATHER_API_KEY = "your_key_here"

# Timezone
TIMEZONE = "Europe/London"
```

## Requirements

- Python 3.8+
- Ollama with Llama 3.2
- SearXNG (Docker recommended)
- Flask (for web interface)

## API Endpoints (Web Interface)

### POST /api/chat
Send a message to Jarvis

**Request:**
```json
{
  "message": "What time is it in Tokyo?"
}
```

**Response:**
```json
{
  "response": "In Tokyo, the time is 8:30 PM.",
  "system": false
}
```

### GET /api/context
Get conversation history

**Response:**
```json
{
  "history": [
    {
      "user": "What time is it?",
      "assistant": "The time is 11:30 AM."
    }
  ]
}
```

### DELETE /api/context
Clear conversation history

**Response:**
```json
{
  "message": "Context cleared"
}
```

## Tips

1. **Better Responses**: The more specific your question, the better the answer
2. **Follow-ups**: Use context - ask "What about Paris?" after asking about Tokyo
3. **Wikipedia**: Questions about people, places, concepts get detailed Wikipedia content
4. **Web Search**: For current events, always gets latest information

## Troubleshooting

### "Could not connect to SearXNG"
- Make sure SearXNG Docker container is running
- Check `SEARXNG_URL` in `config.py`

### "Could not connect to Ollama"
- Ensure Ollama is running: `ollama serve`
- Verify Llama 3.2 is installed: `ollama pull llama3.2`

### Web UI not loading
- Check if port 5000 is available
- Try accessing: http://127.0.0.1:5000

## License

MIT License - Feel free to use and modify!
