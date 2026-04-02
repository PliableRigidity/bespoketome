try:
    import trafilatura
    _HAS_TRAFILATURA = True
except ImportError:
    _HAS_TRAFILATURA = False

try:
    from sentence_transformers import CrossEncoder
    _HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    _HAS_SENTENCE_TRANSFORMERS = False

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

import requests
import time
from .cache import get_content_cache, set_content_cache

# Initialize Reranker (Lazy load to avoid startup delay if possible, but here global is okay)
# usage of CPU is requested.
RERANKER_MODEL_NAME = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
_RERANKER = None

def get_reranker():
    global _RERANKER
    if _RERANKER is None:
        if not _HAS_SENTENCE_TRANSFORMERS or not _HAS_NUMPY:
            # print("sentence_transformers or numpy not installed, skipping reranker.")
            _RERANKER = False
            return _RERANKER
            
        try:
            # print(f"Loading reranker model: {RERANKER_MODEL_NAME}...")
            _RERANKER = CrossEncoder(RERANKER_MODEL_NAME, device='cpu')
        except Exception as e:
            # print(f"Failed to load reranker: {e}")
            _RERANKER = False # sentinel for failed
    return _RERANKER

def rerank_candidates(query: str, candidates: list, top_k: int = 4) -> list:
    """Rerank candidates based on query-document relevance."""
    if not candidates:
        return []

    ranker = get_reranker()
    if not ranker:
        # Fallback: simple dedupe and return top_k
        return candidates[:top_k]

    # Prepare pairs: [ (query, title + " " + snippet), ... ]
    pairs = []
    for cand in candidates:
        text = f"{cand.get('title', '')} {cand.get('snippet', '')}"
        pairs.append((query, text))

    scores = ranker.predict(pairs)
    
    # Attach scores
    for i, cand in enumerate(candidates):
        cand['score'] = float(scores[i])

    # Sort descending
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:top_k]

def fetch_content(url: str, timeout: int = 10) -> dict:
    """
    Fetch URL content, extracting main text and metadata.
    Uses caching.
    """
    # Check cache
    cached = get_content_cache(url)
    if cached:
        return cached

    # Fetch
    try:
        if not _HAS_TRAFILATURA:
            # Fallback: simple requests get
            try:
                resp = requests.get(url, timeout=timeout)
                resp.raise_for_status()
                # Very basic text extraction as last resort
                # This is better than nothing if trafilatura is missing
                text = resp.text
                # Remove script/style tags (rudimentary)
                import re
                text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
                text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL)
                text = re.sub(r'<[^>]+>', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                
                extracted = {
                    "text": text[:5000],  # Limit length for fallback
                    "title": "",
                    "author": None,
                    "published": None,
                    "url": url,
                    "accessed": time.strftime("%Y-%m-%dT%H:%M:%S%z")
                }
                set_content_cache(url, extracted)
                return extracted
            except Exception as e:
                return {"error": f"Basic fetch failed: {str(e)}"}

        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {"error": "Empty response"}
        
        result = trafilatura.extract(downloaded, output_format='json', include_comments=False)
        if not result:
            return {"error": "Extraction failed"}
        
        # trafilatura json format: {"text": "...", "title": "...", "date": "...", ...}
        import json
        data = json.loads(result)
        
        # Normalize
        extracted = {
            "text": data.get("text", ""),
            "title": data.get("title", ""),
            "author": data.get("author"),
            "published": data.get("date"),
            "url": url,
            "accessed": time.strftime("%Y-%m-%dT%H:%M:%S%z")
        }

        set_content_cache(url, extracted)
        return extracted

    except Exception as e:
        return {"error": str(e)}

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list:
    """Simple character-based chunking."""
    if not text:
        return []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks
