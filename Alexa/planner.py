# planner.py
import json
import re
import requests
from config import OLLAMA_URL, OLLAMA_MODEL, USE_OLLAMA, LLM_TEMPERATURE

SYSTEM_RULES = """You are a local assistant planner.
Output ONLY JSON. Valid shapes:

1) {"action":"call_tool","name":"<tool>","args":{...}}
2) {"action":"call_tools","calls":[{"name":"<tool>","args":{...}}, ...]}
3) {"action":"final","text":"<short, speakable reply under 60 words>"}

Tools available:
- get_time: args {}
- get_time_in: args {"place": string}
- get_weather: args {"place": string}

Routing rules:
- If user asks local time → get_time.
- If asks time in a place → get_time_in with that place.
- If asks weather in a place → get_weather with that place.
- If a single utterance requests multiple things (e.g., "time and weather in Tokyo"),
  use action "call_tools" with both tools in the correct order.
- If unclear, ask a short clarification as 'final'.
- Output only JSON, no extra text.
"""

FEW_SHOTS = [
    {"role":"user","content":"what's the time"},
    {"role":"assistant","content":json.dumps({"action":"call_tool","name":"get_time","args":{}})},
    {"role":"user","content":"what's the time in tokyo"},
    {"role":"assistant","content":json.dumps({"action":"call_tool","name":"get_time_in","args":{"place":"tokyo"}})},
    {"role":"user","content":"weather in singapore"},
    {"role":"assistant","content":json.dumps({"action":"call_tool","name":"get_weather","args":{"place":"singapore"}})},
    {"role":"user","content":"what's the time and weather in new york"},
    {"role":"assistant","content":json.dumps({"action":"call_tools","calls":[
        {"name":"get_time_in","args":{"place":"new york"}},
        {"name":"get_weather","args":{"place":"new york"}}
    ]})},
]

def _safe_json(s: str) -> dict:
    s = s.strip()
    start, end = s.find("{"), s.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found")
    return json.loads(s[start:end+1])

def plan_with_ollama(user_text: str) -> dict:
    url = f"{OLLAMA_URL}/api/chat"
    messages = [{"role":"system","content":SYSTEM_RULES}] + FEW_SHOTS + [{"role":"user","content":user_text}]
    payload = {"model": OLLAMA_MODEL, "messages": messages, "options": {"temperature": LLM_TEMPERATURE}}
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    raw = data.get("message", {}).get("content") or data.get("content", "")
    return _safe_json(raw)

# Simple regex fallback covers common phrasing.
TIME_IN_RE = re.compile(r"(?:time\s+in|in\s+)([a-zA-Z\s\-]+)$")
WEATHER_IN_RE = re.compile(r"(?:weather\s+in|in\s+)([a-zA-Z\s\-]+)$")

def plan_with_regex(user_text: str) -> dict:
    text = user_text.lower().strip()

    wants_time = "time" in text or "clock" in text
    wants_weather = "weather" in text

    place_time = None
    place_weather = None

    # try to pull a trailing place name
    m_t = TIME_IN_RE.search(text)
    if m_t:
        place_time = m_t.group(1).strip()

    m_w = WEATHER_IN_RE.search(text)
    if m_w:
        place_weather = m_w.group(1).strip()

    calls = []
    if wants_time and wants_weather:
        # combined
        if place_time and not place_weather:
            place_weather = place_time
        if place_weather and not place_time:
            place_time = place_weather
        if place_time:
            calls.append({"name":"get_time_in","args":{"place":place_time}})
        else:
            calls.append({"name":"get_time","args":{}})
        if place_weather:
            calls.append({"name":"get_weather","args":{"place":place_weather}})
        else:
            # weather requires a place; ask for it
            return {"action":"final","text":"Which city or country should I check the weather for?"}
        return {"action":"call_tools","calls":calls}

    if wants_time:
        if place_time:
            return {"action":"call_tool","name":"get_time_in","args":{"place":place_time}}
        return {"action":"call_tool","name":"get_time","args":{}}

    if wants_weather:
        if place_weather:
            return {"action":"call_tool","name":"get_weather","args":{"place":place_weather}}
        return {"action":"final","text":"Which city or country should I check the weather for?"}

    return {"action":"final","text":"Ask me for the time, or the time/weather in a place."}

def plan(user_text: str) -> dict:
    if USE_OLLAMA:
        try:
            return plan_with_ollama(user_text)
        except Exception:
            pass
    return plan_with_regex(user_text)
