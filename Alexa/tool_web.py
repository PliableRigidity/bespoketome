import json
import logging
from web_retrieval import web_search_answer

logger = logging.getLogger(__name__)

def search_web(query: str) -> dict:
    """
    Public entry point: Search web using the web_retrieval pipeline.
    
    ALWAYS returns a dict with:
      - answer: string (never empty)
      - sources: list of {title, url, snippet} dicts
      - debug: optional debug info
    
    Never raises exceptions - always returns valid response.
    """
    try:
        # Sanitize query
        query = query.strip()
        if not query:
            return {
                "answer": "I need a search query to look that up.",
                "sources": []
            }
        
        logger.info(f"Web search for: '{query}'")
        result = web_search_answer(query)
        
        answer = result.get("answer", "")
        citations = result.get("citations", [])
        
        # Convert citations to sources format
        # citations: [{id, title, url, published}]
        # sources: [{title, url, snippet}]
        sources = []
        for cit in citations:
            sources.append({
                "title": cit.get("title", ""),
                "url": cit.get("url", ""),
                "snippet": ""  # We don't have snippets in citations, could add later
            })
        
        # Ensure answer is never empty
        if not answer:
            logger.warning("Web search returned empty answer, using fallback")
            answer = "I found some sources but couldn't generate a summary."
        
        logger.info(f"Web search complete: answer_len={len(answer)}, sources={len(sources)}")
        
        return {
            "answer": answer,
            "sources": sources,
            "debug": result.get("debug", {})
        }
        
    except Exception as e:
        logger.error(f"Web search error: {e}", exc_info=True)
        # Never crash - return empty sources but still provide answer
        return {
            "answer": f"I encountered an issue with web search, but I can still help. What would you like to know about {query}?",
            "sources": [],
            "error": str(e)
        }
