import requests
import json
import re
from config import SEARXNG_URL, OLLAMA_URL, OLLAMA_MODEL

def _scrape_searxng_html(html_content: str) -> list:
    """Scrape search results from SearXNG HTML output."""
    results = []
    articles = re.findall(r'<article class="result result-default category-general">(.*?)</article>', html_content, re.DOTALL)
    
    for article in articles:
        title_match = re.search(r'<h3><a href="[^"]*"[^>]*>(.*?)</a></h3>', article, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', title_match.group(1) if title_match else "").strip()
        
        url_match = re.search(r'href="([^"]*)"', article)
        url = url_match.group(1) if url_match else ""
        
        content_match = re.search(r'<p class="content">(.*?)</p>', article, re.DOTALL)
        content = re.sub(r'<[^>]+>', '', content_match.group(1) if content_match else "").strip()
        
        if title and url:
            results.append({"title": title, "content": content, "url": url})
            
    return results

def _extract_wikipedia_content(url: str) -> str:
    """Extract main content from a Wikipedia article."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
        
        content_match = re.search(r'<div[^>]*class="[^"]*mw-parser-output[^"]*"[^>]*>(.*?)<div[^>]*id="toc"', html, re.DOTALL)
        if not content_match:
            content_match = re.search(r'<div[^>]*class="[^"]*mw-parser-output[^"]*"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
        
        if not content_match:
            return ""
        
        paragraphs = re.findall(r'<p>(.*?)</p>', content_match.group(1), re.DOTALL)
        
        text_parts = []
        for para in paragraphs[:15]:
            para = re.sub(r'\[[\d\s,]+\]', '', para)
            para = re.sub(r'\[citation needed\]', '', para, flags=re.IGNORECASE)
            para = re.sub(r'<[^>]+>', '', para)
            para = para.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
            para = para.strip()
            if para and len(para) > 30:
                text_parts.append(para)
        
        return '\n\n'.join(text_parts[:8])
    except Exception as e:
        return ""

def _enhance_results_with_wikipedia(results: list, query: str) -> list:
    """Enhance search results selectively with Wikipedia content."""
    simple_keywords = ['capital of', 'population of', 'when was', 'when did', 'how old', 'how tall', 'how many', 'what year', 'who is the', 'where is', 'what is the name', 'price of']
    detailed_keywords = ['explain', 'how does', 'tell me about', 'what are', 'describe', 'history of', 'overview of']
    
    query_lower = query.lower()
    is_simple = any(kw in query_lower for kw in simple_keywords)
    wants_detail = any(kw in query_lower for kw in detailed_keywords)
    
    enhanced_results = []
    wiki_count = 0
    
    for i, result in enumerate(results):
        url = result.get('url', '')
        
        if 'wikipedia.org' in url and '/wiki/' in url:
            should_enhance = ((not is_simple and wants_detail) or (i == 0 and len(result.get('content', '')) < 100))
            
            if should_enhance and wiki_count < 1:
                print(f"Fetching Wikipedia content from: {url}")
                wiki_content = _extract_wikipedia_content(url)
                if wiki_content and len(wiki_content) > 200:
                    result['content'] = wiki_content[:800] if is_simple else wiki_content[:2000]
                    result['enhanced'] = True
                    wiki_count += 1
                    print(f"Enhanced with {len(result['content'])} characters")
        
        enhanced_results.append(result)
    
    return enhanced_results

def get_searxng_results(query: str, num_results: int = 5) -> list:
    """Search the web using SearxNG."""
    try:
        # Use 127.0.0.1 to avoid some localhost resolution issues
        base_url = SEARXNG_URL.replace("localhost", "127.0.0.1")
        
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": f"{base_url}/",
            "Connection": "keep-alive"
        }
        session.headers.update(headers)
        session.get(base_url, timeout=5)
        
        params = {"q": query, "format": "json", "language": "en"}
        response = session.get(f"{base_url}/search", params=params, timeout=10)
        
        if response.status_code == 403:
            params.pop("format")
            response = session.get(f"{base_url}/search", params=params, timeout=10)
            response.raise_for_status()
            return _scrape_searxng_html(response.text)[:num_results]

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
    except requests.exceptions.ConnectionError:
        return [{"error": f"Could not connect to SearXNG at {SEARXNG_URL}. Is the Docker container running?"}]
    except Exception as e:
        return [{"error": str(e)}]

def _summarize_with_llm(query: str, results: list) -> str:
    """Summarize search results using Ollama."""
    simple_keywords = ['capital of', 'population of', 'when was', 'when did', 'how old', 'how tall', 'how many', 'what year', 'who is the', 'where is', 'what is the name', 'price of']
    
    query_lower = query.lower()
    is_simple = any(kw in query_lower for kw in simple_keywords)
    
    context = ""
    for i, res in enumerate(results):
        content = res.get('content', '')
        if res.get('enhanced'):
            content = content[:1500]
        else:
            content = content[:400]
        
        source_name = res.get('url', '').split('/')[2] if '/' in res.get('url', '') else 'Unknown'
        context += f"[{i+1}] {res.get('title')} (Source: {source_name}):\n{content}\n\n"
    
    if is_simple:
        instruction = """IMPORTANT: This is a SIMPLE FACTUAL QUESTION.
- Give a DIRECT, CONCISE answer (1-2 sentences maximum)
- State the fact clearly without extra explanation
- Cite the source using [1], [2], etc.
- DO NOT provide lengthy background or context unless asked
- Example: "The capital of India is New Delhi [1]."
"""
    else:
        instruction = """IMPORTANT: Provide a COMPREHENSIVE but ORGANIZED answer.
- Extract KEY FACTS from ALL sources, not just one
- Synthesize information from multiple sources when available
- Use bullet points or short paragraphs for clarity
- Cite sources using [1], [2], etc. for different facts
- Prioritize the most relevant and recent information
- Keep it informative but conversational
"""
    
    prompt = f"""You are Jarvis, a helpful AI assistant. The user asked: "{query}"

Here are search results from MULTIPLE SOURCES:
{context}

{instruction}

Your goal is to provide an accurate, helpful answer based on the search results."""
    
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 3072
            }
        }
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=45)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        return f"I found some results but couldn't summarize them. The top result says: {results[0].get('content')}"

def search_web(query: str) -> str:
    """Public entry point: Search web and return a natural language summary."""
    results = get_searxng_results(query)
    
    if not results:
        return "I'm sorry, I couldn't find any information on that."
    
    if results[0].get("error"):
        return f"I encountered an error while searching: {results[0].get('error')}"
    
    results = _enhance_results_with_wikipedia(results, query)
    return _summarize_with_llm(query, results)
