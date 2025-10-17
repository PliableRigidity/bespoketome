# dispatcher.py
from planner import plan
from tools_time import get_time, get_time_in
from tool_weather import get_weather

def _fmt_time_result(res: dict) -> str:
    if "place" in res:
        return f"In {res['place']}, the time is {res['human']}."
    return f"The time is {res['human']}."

def _fmt_weather_result(res: dict) -> str:
    temp = res.get("temperature_c")
    desc = res.get("weather_desc")
    place = res.get("place")
    wind = res.get("wind_speed_kmh")
    if temp is not None and wind is not None:
        return f"Weather in {place}: {desc}, {temp:.0f}°C, wind {wind:.0f} km/h."
    if temp is not None:
        return f"Weather in {place}: {desc}, {temp:.0f}°C."
    return f"Weather in {place}: {desc}."

def handle_user_text(user_text: str) -> str:
    """
    1) Ask the planner (LLM/regex) what to do.
    2) Run tool(s).
    3) Return a short, speakable reply.
    """
    decision = plan(user_text)

    action = decision.get("action")
    if action == "final":
        return decision.get("text", "Okay.")

    if action == "call_tool":
        name = decision.get("name")
        args = decision.get("args", {})
        if name == "get_time":
            return _fmt_time_result(get_time())
        if name == "get_time_in":
            place = args.get("place", "").strip()
            if not place:
                return "Which city or country?"
            try:
                return _fmt_time_result(get_time_in(place))
            except Exception as e:
                return f"I couldn't resolve that place. {e}"
        if name == "get_weather":
            place = args.get("place", "").strip()
            if not place:
                return "Which city or country?"
            try:
                return _fmt_weather_result(get_weather(place))
            except Exception as e:
                return f"I couldn't get weather for that place. {e}"
        return "Sorry, I can't do that yet."

    if action == "call_tools":
        pieces = []
        for call in decision.get("calls", []):
            name = call.get("name")
            args = call.get("args", {})
            if name == "get_time":
                pieces.append(_fmt_time_result(get_time()))
            elif name == "get_time_in":
                place = args.get("place", "").strip()
                if not place:
                    pieces.append("Which city or country for the time?")
                else:
                    try:
                        pieces.append(_fmt_time_result(get_time_in(place)))
                    except Exception as e:
                        pieces.append(f"Time lookup failed: {e}")
            elif name == "get_weather":
                place = args.get("place", "").strip()
                if not place:
                    pieces.append("Which city or country for the weather?")
                else:
                    try:
                        pieces.append(_fmt_weather_result(get_weather(place)))
                    except Exception as e:
                        pieces.append(f"Weather lookup failed: {e}")
        return " ".join(pieces) if pieces else "Done."

    return "Sorry, I didn’t understand that."
