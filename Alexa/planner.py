# planner.py
import json
import re
import requests
from config import (
    OLLAMA_URL,
    OLLAMA_MODEL,
    USE_OLLAMA,
    LLM_TEMPERATURE,
)
from context_manager import get_context

# ---------------------------------------------------------------------
#  SYSTEM RULES  (updated to forbid fake tools like get_definition)
# ---------------------------------------------------------------------
SYSTEM_RULES = """You are a local assistant planner with conversation memory.
You MUST output ONLY JSON. No extra text, no commentary.

CONTEXT AWARENESS:
- You have access to previous conversation turns in the message history.
- Use this context to understand follow-up questions and references.
- If the user says "it", "that", "there", etc., refer to previous messages.
- Example: User asks "weather in Paris", then "what about the time?" - you should know they mean Paris.

Valid response shapes:
1) {"action":"call_tool","name":"<tool>","args":{...}}
2) {"action":"call_tools","calls":[{"name":"<tool>","args":{...}}, ...]}
3) {"action":"final","text":"<short, speakable reply under 60 words>"}

TOOLS YOU ARE ALLOWED TO CALL (and ONLY these):
- get_time: args {}
  Use ONLY for questions about the current local time.

- get_time_in: args {"place": string}
  Use ONLY for questions about the time in a specific city/country.

- get_weather: args {"place": string}
  Use ONLY for questions about weather in a specific city/country.

- search_web: args {"query": string}
  Use for ANY question that requires factual information, news, specs, or specific data.

- brainstorm: args {"topic": string}
  Use for CREATIVE tasks, generating IDEAS, suggestions, or "thinking" tasks.

- search_arxiv: args {"query": string}
  Use for ACADEMIC RESEARCH, finding scientific papers, or searching for specific publications.



IMPORTANT RULES:
- DEFAULT TO SEARCH for facts.
- USE BRAINSTORM for ideas/creativity.
- USE SEARCH_ARXIV for academic/scientific papers.

- When in doubt, USE search_web. It's better to search than to guess or say you don't know.
- DO NOT say "I'm not familiar with that" or "I don't understand" for factual questions.
- DO NOT try to answer factual questions from memory - always search for current, accurate info.
- DO NOT invent new tools.

ONLY use {"action":"final","text":"..."} for:
- Simple greetings: "hello", "hi", "good morning"
- Questions about YOUR capabilities: "what can you do", "how do you work"
- Casual conversation that doesn't require facts: "how are you"
- Clarification requests when user input is unclear

- If the user asks for BOTH time and weather in the same place, respond with:
  {"action":"call_tools","calls":[
    {"name":"get_time_in","args":{"place":"<that location>"}},
    {"name":"get_weather","args":{"place":"<that location>"}}
  ]}

- If the user asks for weather but gives no place, respond with:
  {"action":"final","text":"Which city or country should I check the weather for?"}

Formatting rules:
- Output ONLY one valid JSON object.
- NO markdown fences like ```json.
- Keep "text" under 60 words, and phrased for speaking aloud.
"""

# ---------------------------------------------------------------------
#  FEW-SHOT examples to teach the model
# ---------------------------------------------------------------------
FEW_SHOTS = [
    # Time and weather examples
    {"role": "user", "content": "what's the time"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "get_time", "args": {}
    })},

    {"role": "user", "content": "what's the time in tokyo"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "get_time_in", "args": {"place": "tokyo"}
    })},

    # Brainstorming examples
    {"role": "user", "content": "give me some ideas for a python project"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "brainstorm", "args": {"topic": "python project ideas"}
    })},

    {"role": "user", "content": "suggest a cool name for a robot"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "brainstorm", "args": {"topic": "cool robot names"}
    })},

    # ArXiv examples
    {"role": "user", "content": "find papers on machine learning"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_arxiv", "args": {"query": "machine learning"}
    })},



    {"role": "user", "content": "search arxiv for black holes"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_arxiv", "args": {"query": "black holes"}
    })},

    {"role": "user", "content": "how can I make my room look better"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "brainstorm", "args": {"topic": "room decoration ideas"}
    })},

    {"role": "user", "content": "weather in singapore"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "get_weather", "args": {"place": "singapore"}
    })},

    {"role": "user", "content": "what's the time and weather in new york"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tools",
        "calls": [
            {"name": "get_time_in", "args": {"place": "new york"}},
            {"name": "get_weather", "args": {"place": "new york"}}
        ]
    })},

    {"role": "user", "content": "what's the weather like right now"},
    {"role": "assistant", "content": json.dumps({
        "action": "final",
        "text": "Which city or country should I check the weather for?"
    })},

    # News and current events
    {"role": "user", "content": "latest news on spacex"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "latest news spacex"}
    })},

    # People and personalities
    {"role": "user", "content": "who is elon musk"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "elon musk"}
    })},

    {"role": "user", "content": "tell me about taylor swift"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "taylor swift"}
    })},

    # Sports and events
    {"role": "user", "content": "who won the world cup 2022"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "who won world cup 2022"}
    })},

    # Specifications and technical details
    {"role": "user", "content": "what are the specs of a tesla model 3"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "tesla model 3 specs"}
    })},

    {"role": "user", "content": "how much does an iphone 15 cost"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "iphone 15 price"}
    })},

    {"role": "user", "content": "what's the top speed of a bugatti chiron"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "bugatti chiron top speed"}
    })},

    # How things work and explanations
    {"role": "user", "content": "how does a car engine work"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "how does car engine work"}
    })},

    {"role": "user", "content": "how do you make coffee"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "how to make coffee"}
    })},

    {"role": "user", "content": "explain photosynthesis"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "explain photosynthesis"}
    })},

    # General knowledge and definitions
    {"role": "user", "content": "what is gravity"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "what is gravity"}
    })},

    {"role": "user", "content": "what is the capital of france"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "capital of france"}
    })},

    # Comparisons
    {"role": "user", "content": "which is better iphone or samsung"},
    {"role": "assistant", "content": json.dumps({
        "action": "call_tool", "name": "search_web", "args": {"query": "iphone vs samsung comparison"}
    })},

    # Simple greetings (should NOT search)
    {"role": "user", "content": "hello"},
    {"role": "assistant", "content": json.dumps({
        "action": "final",
        "text": "Hello! How can I help you today?"
    })},

    {"role": "user", "content": "what can you do"},
    {"role": "assistant", "content": json.dumps({
        "action": "final",
        "text": "I can tell you the time and weather, search the web for information, and answer questions about almost anything!"
    })},
]

# ---------------------------------------------------------------------
#  Helper functions for JSON cleaning/parsing
# ---------------------------------------------------------------------
def _strip_markdown_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.lstrip("`")
        if t.lower().startswith("json"):
            t = t[4:].strip()
        if "```" in t:
            t = t.split("```", 1)[0].strip()
    return t.strip()

def _safe_json(raw: str) -> dict:
    cleaned = _strip_markdown_fences(raw)
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            wrapper = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Still not valid JSON after cleanup: {e}")
        if (
            isinstance(wrapper, dict)
            and "message" in wrapper
            and isinstance(wrapper["message"], dict)
            and "content" in wrapper["message"]
        ):
            inner = _strip_markdown_fences(wrapper["message"]["content"])
            return json.loads(inner)
        raise ValueError("Wrapper did not contain a valid plan")

    if isinstance(obj, dict) and "action" in obj:
        return obj
    if (
        isinstance(obj, dict)
        and "message" in obj
        and isinstance(obj["message"], dict)
        and "content" in obj["message"]
    ):
        inner = _strip_markdown_fences(obj["message"]["content"])
        return json.loads(inner)

    raise ValueError("JSON parsed but did not contain 'action'")

# ---------------------------------------------------------------------
#  Talk to Ollama and reconstruct streamed output
# ---------------------------------------------------------------------
def plan_with_ollama(user_text: str) -> dict:
    url = f"{OLLAMA_URL}/api/chat"

    # Get conversation history
    context = get_context()
    history_messages = context.get_context_messages()
    
    messages = (
        [{"role": "system", "content": SYSTEM_RULES}]
        + FEW_SHOTS
        + history_messages  # Add conversation history
        + [{"role": "user", "content": user_text}]
    )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "options": {"temperature": LLM_TEMPERATURE},
        "format": "json",
        "stream": True,
    }

    try:
        with requests.post(url, json=payload, stream=True, timeout=30) as r:
            r.raise_for_status()
            assembled_content = ""
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = chunk.get("message", {})
                if (
                    isinstance(msg, dict)
                    and msg.get("role") == "assistant"
                    and "content" in msg
                ):
                    assembled_content += msg["content"]
                if chunk.get("done") is True:
                    break

        print(f"\nDEBUG assembled_content:\n{assembled_content}\n")
        return _safe_json(assembled_content)

    except Exception as e:
        error_type = type(e).__name__
        if "Connection" in error_type or "URLError" in error_type:
            raise Exception(
                f"Could not connect to Ollama at {OLLAMA_URL}. Is Ollama running?"
            ) from e
        elif "Timeout" in error_type:
            raise Exception("Ollama request timed out") from e
        elif "HTTP" in error_type:
            raise Exception(f"Ollama HTTP error: {e}") from e
        elif "JSON" in error_type or "ValueError" in error_type:
            raise Exception(f"Failed to parse Ollama response: {e}") from e
        else:
            raise Exception(f"Unexpected error with Ollama: {e}") from e

# ---------------------------------------------------------------------
#  Simple regex fallback if Ollama unavailable
# ---------------------------------------------------------------------
TIME_IN_RE = re.compile(r"(?:time\s+in|in\s+)([a-zA-Z\s\-]+)$")
WEATHER_IN_RE = re.compile(r"(?:weather\s+in|in\s+)([a-zA-Z\s\-]+)$")

def plan_with_regex(user_text: str) -> dict:
    text = user_text.lower().strip()
    wants_time = "time" in text or "clock" in text
    wants_weather = "weather" in text
    place_time = None
    place_weather = None

    m_t = TIME_IN_RE.search(text)
    if m_t:
        place_time = m_t.group(1).strip()
    m_w = WEATHER_IN_RE.search(text)
    if m_w:
        place_weather = m_w.group(1).strip()

    if wants_time and wants_weather:
        if place_time and not place_weather:
            place_weather = place_time
        if place_weather and not place_time:
            place_time = place_weather
        calls = []
        if place_time:
            calls.append({"name": "get_time_in", "args": {"place": place_time}})
        else:
            calls.append({"name": "get_time", "args": {}})
        if place_weather:
            calls.append({"name": "get_weather", "args": {"place": place_weather}})
        else:
            return {"action": "final", "text": "Which city or country should I check the weather for?"}
        return {"action": "call_tools", "calls": calls}

    if wants_time:
        if place_time:
            return {"action": "call_tool", "name": "get_time_in", "args": {"place": place_time}}
        return {"action": "call_tool", "name": "get_time", "args": {}}

    if wants_weather:
        if place_weather:
            return {"action": "call_tool", "name": "get_weather", "args": {"place": place_weather}}
        return {"action": "final", "text": "Which city or country should I check the weather for?"}

    return {"action": "final", "text": "I can tell you the time or weather. Ask like 'weather in Tokyo' or 'time in Paris'."}

# ---------------------------------------------------------------------
#  Public entry point used by dispatcher
# ---------------------------------------------------------------------
def plan(user_text: str) -> dict:
    if USE_OLLAMA:
        try:
            return plan_with_ollama(user_text)
        except Exception as e:
            print(f"Planner: Ollama failed with error: {e}")
    return plan_with_regex(user_text)
