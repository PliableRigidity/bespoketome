import requests
from config import SEARXNG_URL

def search_web(query: str, num_results: int = 3) -> list:
    """Search the web using SearxNG."""
    try:
        params = {
            "q": query,
            "format": "json",
            "engines": "google bing"
        }
        response = requests.get(f"{SEARXNG_URL}/search", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("results", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "url": item.get("url", "")
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]

def format_search_results(results: list) -> str:
    """Format search results into a speakable string."""
    if not results:
        return "No search results found."
    
    if results[0].get("error"):
        return f"Search failed: {results[0].get('error')}"
    
    # For voice responses, be more concise
    response_parts = []
    
    # Use the first result for the main answer
    first_result = results[0]
    title = first_result.get("title", "")
    content = first_result.get("content", "")
    
    # Limit content length for speech
    if len(content) > 200:
        content = content[:200] + "..."
    
    # Combine title and content for the main answer
    main_answer = f"{content}"
    if title and title.lower() not in content.lower():
        main_answer = f"{title}. {content}"
    
    response_parts.append(main_answer)
    
    # Optionally mention additional results
    if len(results) > 1:
        response_parts.append(f"I found {len(results)} results on this topic.")
    
    return " ".join(response_parts)

