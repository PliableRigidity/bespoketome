import requests
import json
import datetime
try:
    import config
    OLLAMA_URL = config.OLLAMA_URL
    OLLAMA_MODEL = config.OLLAMA_MODEL
except ImportError:
    # If running in a context where config is not directly importable
    from .. import config
    OLLAMA_URL = config.OLLAMA_URL
    OLLAMA_MODEL = config.OLLAMA_MODEL

def call_ollama(prompt: str, json_mode: bool = False) -> str:
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": 4096}
    }
    if json_mode:
        payload["format"] = "json"

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama call failed: {e}")
        return ""

def generate_plan(question: str, freshness: bool) -> dict:
    today = datetime.datetime.now().strftime("%B %Y")
    
    prompt = f"""You are a search query planner.
User Question: "{question}"
Current Date: {today}
Freshness Required: {freshness}

Generate 2-4 search queries to answer this question.
1. Broad query
2. Specific/Constrained query (include year {datetime.datetime.now().year} if freshness is needed)
3. Official/Source query (if applicable)

Output JSON ONLY:
{{
  "queries": ["query 1", "query 2", ...]
}}
"""
    resp = call_ollama(prompt, json_mode=True)
    if not resp:
        return {"queries": [question]}
    
    try:
        data = json.loads(resp)
        if "queries" in data and isinstance(data["queries"], list):
            return data
    except:
        pass
    
    return {"queries": [question]}

def generate_grounded_answer(question: str, chunks: list, citations: list) -> str:
    """
    Generate answer grounded in web sources.
    chunks: list of text chunks with citation_id.
    citations: list of dicts with 'id', 'url', 'title', etc.
    """
    
    context_str = ""
    for chunk in chunks:
        # chunk structure: {'text': ..., 'citation_id': ...}
        context_str += f"Source [{chunk['citation_id']}]: {chunk['text']}\n\n"

    prompt = f"""You are a helpful assistant. Answer the user's question using ONLY the provided context.
User Question: "{question}"

Context:
{context_str}

Instructions:
- Answer directly and comprehensively.
- STRICTLY base your answer on the context.
- Cite sources inline using [ID], e.g. "The sky is blue [1]."
- If the context doesn't contain the answer, say "I couldn't find sufficient information."
- Do NOT list the sources at the end, just use inline [ID]. The system will append the list.

Answer:"""
    
    return call_ollama(prompt)

def generate_direct_answer(question: str) -> str:
    """
    Generate a direct LLM answer without web sources.
    Used as fallback when web retrieval fails.
    """
    prompt = f"""You are a helpful AI assistant. Answer the user's question to the best of your knowledge.

User Question: "{question}"

Instructions:
- Provide a clear, informative answer.
- If you're not certain, acknowledge it.
- Be concise but comprehensive.
- Do not make up information.

Answer:"""
    
    answer = call_ollama(prompt)
    if not answer:
        return "I'm having trouble generating a response right now."
    return answer
