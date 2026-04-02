import requests
import json
import logging
import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Vector, a helpful, intelligent, and safe AI assistant.
Your goal is to provide accurate, concise, and helpful responses to the user.

- Be conversational and friendly.
- If you don't know something, admit it; don't make up facts.
- Keep your answers grounded in the context provided if available.
- If the user asks for code, provide clean, commented code.
- If the user asks for a creative task, be creative.
"""

def generate_response(user_text: str, context=None) -> str:
    """
    Generate a direct response using Ollama, incorporating conversation context.
    
    Args:
        user_text: The user's input text
        context: The context object (ContextManager)
        
    Returns:
        str: The generated response
    """
    try:
        url = f"{config.OLLAMA_URL}/api/chat"
        
        # Build messages list
        # Start with system prompt
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history
        if context:
            # Assuming get_context_messages returns list of dicts
            history = context.get_context_messages()
            if history:
                 messages.extend(history)
            
        # Add CURRENT user message
        # We must append this because context history likely contains PAST turns, not the current trigger
        messages.append({"role": "user", "content": user_text})
        
        payload = {
            "model": config.OLLAMA_MODEL,
            "messages": messages,
            "options": {
                "temperature": 0.7, 
                "num_ctx": 4096
            },
            "stream": False 
        }
        
        logger.info(f"Generating LLM response for: {user_text[:50]}...")
        
        # Using a session for potential connection reuse if we were doing multiple calls, 
        # but here simple post is fine.
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result.get("message", {}).get("content", "")
        
        if not content:
            logger.warning("Ollama returned empty content")
            return "I'm sorry, I couldn't generate a response."
            
        return content.strip()
        
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return "I'm having trouble connecting to my brain right now. Please check if Ollama is running."
