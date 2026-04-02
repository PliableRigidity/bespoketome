import time
import logging
import urllib.parse
from duckduckgo_search import DDGS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def execute_web_query(query: str, num_results: int = 10, max_retries: int = 2) -> list:
    """
    Execute a single query using DuckDuckGo Search (DDGS) with retries and robust error handling.
    Returns list of standardized dicts:
    [
        { "title": str, "url": str, "snippet": str }
    ]
    """
    if not query or not query.strip():
        return []

    # Sanitize query
    clean_query = query.strip().lower()
    clean_query = " ".join(clean_query.split()) # Collapse excessive spaces

    results = []
    attempt = 0
    
    while attempt < max_retries:
        try:
            logger.info(f"DDGS web search attempt {attempt+1} for '{clean_query}'")
            with DDGS() as ddgs:
                # Use safesearch='moderate' as a reasonable default
                # basic text search
                ddg_results = ddgs.text(clean_query, max_results=num_results, safesearch='moderate')
                
                if not ddg_results:
                    logger.warning(f"DDGS returned no results for query: '{clean_query}'")
                    return []

                seen_urls = set()
                for r in ddg_results:
                    url = r.get("href", "")
                    if not url:
                        continue
                    
                    # Deduplicate by URL
                    if url in seen_urls:
                        continue
                    
                    seen_urls.add(url)
                    results.append({
                        "title": r.get("title", ""),
                        "url": url,
                        "snippet": r.get("body", ""),
                    })
                
                return results

        except Exception as e:
            attempt += 1
            logger.error(f"DDGS query failed (attempt {attempt}/{max_retries}) for '{clean_query}': {e}")
            if attempt < max_retries:
                time.sleep(1 * attempt) # Linear backoff
            else:
                logger.error(f"All DDGS attempts failed for '{clean_query}'")
                return []
    
    return []

def execute_image_search(query: str, max_results: int = 4) -> list:
    """
    Execute image search using DuckDuckGo (DDGS).
    Returns list of dicts:
    [
        { "title", "image_url", "thumbnail_url", "source_url", "width", "height" }
    ]
    """
    if not query or not query.strip():
        return []

    # Sanitize query
    clean_query = query.strip().lower()
    clean_query = " ".join(clean_query.split())

    results = []
    max_retries = 2
    attempt = 0
    
    while attempt < max_retries:
        try:
            logger.info(f"DDGS image search attempt {attempt+1} for '{clean_query}'")
            with DDGS() as ddgs:
                ddg_images = ddgs.images(clean_query, max_results=max_results, safesearch='moderate')
                
                if not ddg_images:
                    return []
                
                seen_urls = set()
                for img in ddg_images:
                    img_url = img.get("image", "")
                    # Filter out results missing image_url
                    if not img_url:
                        continue
                    
                    # Deduplicate by image_url
                    if img_url in seen_urls:
                        continue
                    seen_urls.add(img_url)
                    
                    results.append({
                        "title": img.get("title", ""),
                        "image_url": img_url,
                        "thumbnail_url": img.get("thumbnail", ""),
                        "source_url": img.get("url", ""),
                        "width": img.get("width"),
                        "height": img.get("height")
                    })
                return results

        except Exception as e:
            attempt += 1
            logger.error(f"DDGS image search failed (attempt {attempt}/{max_retries}) for '{clean_query}': {e}")
            if attempt < max_retries:
                time.sleep(1 * attempt)
            else:
                return []
    return []

def clean_url(url: str) -> str:
    """Remove common tracking parameters."""
    try:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        
        # Filter out utm_*, fbclid, gclid, etc.
        filtered_qs = {k: v for k, v in qs.items() if not k.startswith(('utm_', 'fbclid', 'gclid', 'yclid', '_hs'))}
        
        new_query = urllib.parse.urlencode(filtered_qs, doseq=True)
        return urllib.parse.urlunparse(parsed._replace(query=new_query))
    except Exception:
        return url
