import requests
from config import OLLAMA_URL, OLLAMA_MODEL

def brainstorm_ideas(topic: str) -> str:
    """
    Generate creative ideas and suggestions using the LLM's internal knowledge.
    Does NOT search the web.
    """
    prompt = f"""You are Jarvis, a creative and intelligent AI assistant.
The user wants you to brainstorm ideas about: "{topic}"

IMPORTANT INSTRUCTIONS:
- Do NOT search the web. Use your own creativity and knowledge.
- Provide UNIQUE, INNOVATIVE, and DETAILED ideas.
- Don't just list generic things; explain the 'why' and 'how'.
- If suggesting projects, include a brief tech stack or implementation idea.
- Be conversational but structured (use bullet points or numbered lists).
- Aim to impress the user with your originality.

Generate your response now:"""

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,  # Higher temperature for creativity
                "num_ctx": 4096
            }
        }
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        return f"I tried to brainstorm, but my creative circuits jammed: {str(e)}"
