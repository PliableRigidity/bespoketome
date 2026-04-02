# dispatcher.py
import logging
from typing import Dict, Any, List
from planner import plan
from tools_time import get_time, get_time_in
from tool_weather import get_weather
from tool_web import search_web
from tool_creative import brainstorm_ideas
from tool_arxiv import search_arxiv
from tool_image import image_search, should_fetch_images
from llm_client import generate_response
from context_manager import get_context
import config
import database as db
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def handle_user_text(user_text: str) -> Dict[str, Any]:
    """
    Main dispatcher: routes user input through planner and tools.
    
    CRITICAL: This function ALWAYS returns a structured response with:
    {
        "text": str,      # ALWAYS present, never empty
        "images": list,   # ALWAYS present, may be empty
        "sources": list   # ALWAYS present, may be empty
    }
    
    Web retrieval and image search are ENHANCEMENTS, not replacements.
    If they fail, we still return an LLM-generated answer.
    """
    # Initialize structured response - ALWAYS has these keys
    final_response = {
        "text": "",
        "images": [],
        "sources": []
    }
    
    # Get planner decision
    decision = plan(user_text)
    action = decision.get("action")
    
    logger.info(f"Planner decision: action={action}")
    
    # Helper to process tool results
    def process_tool_result(name: str, result: Any):
        """Process tool result and merge into final_response"""
        if name == "search_web" and isinstance(result, dict):
            # Web search returns structured dict: {answer, sources, debug}
            answer_text = result.get("answer", "")
            if answer_text:
                if final_response["text"]:
                    final_response["text"] += "\n\n" + answer_text
                else:
                    final_response["text"] = answer_text
            
            # Merge sources
            sources = result.get("sources", [])
            if sources:
                final_response["sources"].extend(sources)
                logger.info(f"Added {len(sources)} sources from web search")
                
        elif name == "image_search":
            # Image search returns list of images
            if isinstance(result, list):
                final_response["images"].extend(result)
                logger.info(f"Added {len(result)} images")
            # Don't set default text here - let LLM handle it
                
        else:
            # Other tools return string
            text_res = str(result)
            if final_response["text"]:
                final_response["text"] += "\n" + text_res
            else:
                final_response["text"] = text_res

    # Execute Action
    if action == "final":
        # Direct LLM response
        final_response["text"] = decision.get("text", "Okay.")
        
    elif action == "call_tool":
        name = decision.get("name")
        args = decision.get("args", {})
        
        logger.info(f"Calling tool: {name} with args: {args}")
        
        try:
            if name == "get_time":
                process_tool_result(name, _fmt_time_result(get_time()))
            elif name == "get_time_in":
                place = args.get("place", "").strip()
                if not place:
                    process_tool_result(name, "Which city or country?")
                else:
                    process_tool_result(name, _fmt_time_result(get_time_in(place)))
            elif name == "get_weather":
                place = args.get("place", "").strip()
                if not place:
                    process_tool_result(name, "Which city or country?")
                else:
                    process_tool_result(name, _fmt_weather_result(get_weather(place)))
            elif name == "search_web":
                query = args.get("query", "").strip()
                if not query:
                    process_tool_result(name, "What should I search for?")
                else:
                    # Web search with fallback to LLM
                    try:
                        web_result = search_web(query)
                        process_tool_result(name, web_result)
                    except Exception as e:
                        logger.error(f"Web search failed: {e}")
                        # Fallback: generate LLM answer
                        llm_answer = generate_response(user_text, get_context())
                        final_response["text"] = llm_answer
                        
            elif name == "brainstorm":
                topic = args.get("topic", "").strip()
                if not topic:
                    process_tool_result(name, "I need a topic to brainstorm about.")
                else:
                    process_tool_result(name, brainstorm_ideas(topic))
            elif name == "search_arxiv":
                query = args.get("query", "").strip()
                if not query:
                    process_tool_result(name, "What papers should I search for?")
                else:
                    process_tool_result(name, search_arxiv(query))
            elif name == "image_search":
                query = args.get("query", "").strip()
                if not query:
                    final_response["text"] = "What images should I search for?"
                else:
                    try:
                        imgs = image_search(query)
                        process_tool_result(name, imgs)
                        # If we got images but no text, generate a response
                        if not final_response["text"] and imgs:
                            final_response["text"] = f"I found {len(imgs)} image(s) for '{query}'."
                    except Exception as e:
                        logger.error(f"Image search failed: {e}")
                        final_response["text"] = f"I couldn't fetch images, but I can tell you about {query}."
                        
            else:
                # Unknown tool - try fallback
                fallback_query = args.get("query") or args.get("topic") or args.get("place")
                if fallback_query:
                    try:
                        web_result = search_web(f"{name} {fallback_query}")
                        process_tool_result("search_web", web_result)
                    except Exception as e:
                        logger.error(f"Fallback web search failed: {e}")
                        # Use LLM as last resort
                        llm_answer = generate_response(user_text, get_context())
                        final_response["text"] = llm_answer
                else:
                    final_response["text"] = f"I don't have a tool called '{name}', but let me try to help anyway."
                    llm_answer = generate_response(user_text, get_context())
                    final_response["text"] += "\n\n" + llm_answer
                    
        except Exception as e:
            logger.error(f"Tool execution error for {name}: {e}")
            # Always fallback to LLM
            final_response["text"] = generate_response(user_text, get_context())

    elif action == "call_tools":
        # Multiple tools
        for call in decision.get("calls", []):
            name = call.get("name")
            args = call.get("args", {})
            try:
                if name == "get_time":
                    process_tool_result(name, _fmt_time_result(get_time()))
                elif name == "get_time_in":
                    place = args.get("place", "").strip()
                    if place: process_tool_result(name, _fmt_time_result(get_time_in(place)))
                elif name == "get_weather":
                    place = args.get("place", "").strip()
                    if place: process_tool_result(name, _fmt_weather_result(get_weather(place)))
                elif name == "search_web":
                    query = args.get("query", "").strip()
                    if query:
                        try:
                            process_tool_result(name, search_web(query))
                        except Exception as e:
                            logger.error(f"Web search in multi-tool failed: {e}")
                elif name == "brainstorm":
                    topic = args.get("topic", "").strip()
                    if topic: process_tool_result(name, brainstorm_ideas(topic))
                elif name == "search_arxiv":
                    query = args.get("query", "").strip()
                    if query: process_tool_result(name, search_arxiv(query))
                elif name == "image_search":
                    query = args.get("query", "").strip()
                    if query:
                        try:
                            process_tool_result(name, image_search(query))
                        except Exception as e:
                            logger.error(f"Image search in multi-tool failed: {e}")
            except Exception as e:
                logger.error(f"Multi-tool execution error for {name}: {e}")
                continue
                
        if not final_response["text"] and not final_response["images"]:
            final_response["text"] = "Done."
    
    else:
        # Unknown action - use LLM
        final_response["text"] = generate_response(user_text, get_context())
    
    # Heuristic Image Fetching (if user intent suggests images but none fetched)
    if not final_response["images"] and should_fetch_images(user_text):
        logger.info("Heuristic image fetch triggered")
        try:
            imgs = image_search(user_text)
            if imgs:
                final_response["images"].extend(imgs)
                logger.info(f"Heuristic fetch added {len(imgs)} images")
        except Exception as e:
            logger.error(f"Heuristic image fetch failed: {e}")
            # Don't crash - just skip images
    
    # CRITICAL: Ensure text is never empty
    if not final_response["text"]:
        logger.warning("Response text was empty, generating fallback")
        final_response["text"] = generate_response(user_text, get_context())
    
    # Save conversation turn to context (text only)
    context = get_context()
    context.add_turn(user_text, final_response["text"])
    
    # Log final response structure
    logger.info(f"Final response: text_len={len(final_response['text'])}, images={len(final_response['images'])}, sources={len(final_response['sources'])}")
    
    # --- LOG TO DATABASE ---
    try:
        if final_response["sources"] or final_response["images"]:
            db.execute_db(
                "INSERT INTO retrieval_logs (query, web_sources, images, tool_name) VALUES (?, ?, ?, ?)",
                (
                    user_text,
                    json.dumps(final_response["sources"]),
                    json.dumps(final_response["images"]),
                    action if action == "call_tool" else "multi_tool"
                )
            )
            logger.info("Logged retrieval event to DB")
    except Exception as e:
        logger.error(f"Failed to log retrieval to DB: {e}")

    return final_response
