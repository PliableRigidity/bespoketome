# dispatcher.py
from planner import plan
from tools_time import get_time, get_time_in
from tool_weather import get_weather
from tool_web import search_web
from tool_creative import brainstorm_ideas
from tool_arxiv import search_arxiv

from context_manager import get_context

def _fmt_time_result(res: dict) -> str:
    if res.get("place"):
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
    4) Save conversation to context.
    """
    decision = plan(user_text)

    action = decision.get("action")
    response = ""
    
    if action == "final":
        response = decision.get("text", "Okay.")
    elif action == "call_tool":
        name = decision.get("name")
        args = decision.get("args", {})
        if name == "get_time":
            response = _fmt_time_result(get_time())
        elif name == "get_time_in":
            place = args.get("place", "").strip()
            if not place:
                response = "Which city or country?"
            else:
                try:
                    response = _fmt_time_result(get_time_in(place))
                except Exception as e:
                    response = f"I couldn't resolve that place. {e}"
        elif name == "get_weather":
            place = args.get("place", "").strip()
            if not place:
                response = "Which city or country?"
            else:
                try:
                    response = _fmt_weather_result(get_weather(place))
                except Exception as e:
                    response = f"I couldn't get weather for that place. {e}"
        elif name == "search_web":
            query = args.get("query", "").strip()
            if not query:
                response = "What should I search for?"
            else:
                try:
                    response = search_web(query)
                except Exception as e:
                    response = f"I couldn't search the web. {e}"
        elif name == "brainstorm":
            topic = args.get("topic", "").strip()
            if not topic:
                response = "I need a topic to brainstorm about."
            else:
                try:
                    response = brainstorm_ideas(topic)
                except Exception as e:
                    response = f"I couldn't brainstorm ideas. {e}"
                    
        elif name == "search_arxiv":
            query = args.get("query", "").strip()
            if not query:
                response = "What papers should I search for?"
            else:
                try:
                    response = search_arxiv(query)
                except Exception as e:
                    response = f"I couldn't search ArXiv. {e}"
                    

                    
        else:
            response = "Sorry, I can't do that yet."
    elif action == "call_tools":
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
            elif name == "search_web":
                query = args.get("query", "").strip()
                if not query:
                    pieces.append("What should I search for?")
                else:
                    try:
                        pieces.append(search_web(query))
                    except Exception as e:
                        pieces.append(f"Search failed: {e}")
        response = " ".join(pieces) if pieces else "Done."
    else:
        response = "Sorry, I didn't understand that."
    
    # Save conversation turn to context
    context = get_context()
    context.add_turn(user_text, response)
    
    return response
