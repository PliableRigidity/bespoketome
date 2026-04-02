import datetime
import logging
from .generation import generate_plan, generate_grounded_answer, generate_direct_answer
from .search_client import execute_web_query, clean_url
from .processing import rerank_candidates, fetch_content, chunk_text
from .cache import get_search_cache, set_search_cache

logger = logging.getLogger(__name__)

def web_search_answer(question: str, freshness: bool = False, force_refresh: bool = False) -> dict:
    """
    Web search pipeline that ALWAYS returns an answer.
    
    If web retrieval fails, falls back to direct LLM answer.
    Never returns "I couldn't find..." - always provides value.
    
    Returns:
        dict with keys: answer, citations, debug
    """
    debug_log = {"queries": [], "ranked_urls": [], "errors": [], "fallback_used": False}
    
    try:
        # 1. Freshness detection
        fresh_kw = ["latest", "recent", "news", "today", "yesterday", "current", str(datetime.datetime.now().year)]
        if any(kw in question.lower() for kw in fresh_kw):
            freshness = True
        
        # 2. Planning
        plan = generate_plan(question, freshness)
        queries = plan.get("queries", [question])
        debug_log["queries"] = queries
        logger.info(f"Generated {len(queries)} search queries")

        # 3. Search (DuckDuckGo via search_client)
        candidates = []
        seen_urls = set()
        
        for q in queries:
            # Check cache
            cache_key = f"search:{q}"
            results = get_search_cache(cache_key) if not force_refresh else None
            
            if not results:
                try:
                    results = execute_web_query(q)
                    if results:
                        set_search_cache(cache_key, results)
                        logger.info(f"Query '{q}' returned {len(results)} results")
                except Exception as e:
                    logger.error(f"Search query '{q}' failed: {e}")
                    debug_log["errors"].append(f"Query failed: {str(e)}")
                    continue
            
            if not results:
                logger.warning(f"Query '{q}' returned no results")
                continue

            for res in results:
                url = clean_url(res.get("url"))
                if url not in seen_urls:
                    seen_urls.add(url)
                    res["url"] = url # update to clean
                    candidates.append(res)
        
        # 3.1 Rerank
        top_candidates = rerank_candidates(question, candidates, top_k=4)
        debug_log["ranked_urls"] = [c["url"] for c in top_candidates]
        logger.info(f"Reranked to {len(top_candidates)} candidates")
        
        # 4. Fetch & Extract
        sources_text = []
        citations = []
        
        for idx, cand in enumerate(top_candidates):
            cid = idx + 1
            meta = {
                "id": cid,
                "title": cand.get("title"),
                "url": cand.get("url"),
                "published": cand.get("published_date"),
            }
            
            try:
                extracted = fetch_content(cand["url"])
                if extracted.get("error"):
                    logger.warning(f"Fetch failed {cand['url']}: {extracted['error']}")
                    debug_log["errors"].append(f"Fetch failed {cand['url']}: {extracted['error']}")
                    continue
                    
                text = extracted.get("text", "")
                if not text:
                    # Fallback to snippet if extraction failed but search had snippet
                    text = cand.get("snippet", "")
                    
                # Truncate immense pages
                text = text[:12000] 
                
                chunks = chunk_text(text, chunk_size=1500, overlap=100)
                # Take first 2 chunks max per source to stay in context limit
                best_chunks = chunks[:2]
                
                for ch in best_chunks:
                    sources_text.append({"text": ch, "citation_id": cid})
                    
                citations.append(meta)
            except Exception as e:
                logger.error(f"Error processing {cand['url']}: {e}")
                debug_log["errors"].append(f"Processing error: {str(e)}")
                continue

        # 5. Generate Answer
        answer = ""
        used_fallback = False
        
        if sources_text:
            # We have web sources - generate grounded answer
            logger.info(f"Generating grounded answer from {len(sources_text)} text chunks")
            try:
                # Try to generate answer from sources
                grounded_answer = generate_grounded_answer(question, sources_text, citations)
                
                # Check for "I couldn't find" or similar failure modes
                failure_phrases = [
                    "i couldn't find sufficient information",
                    "i could not find sufficient information",
                    "context doesn't contain",
                    "context does not contain"
                ]
                
                if any(phrase in grounded_answer.lower() for phrase in failure_phrases) or not grounded_answer.strip():
                     logger.warning("Grounded answer failed to find info, falling back to direct LLM.")
                     used_fallback = True
                else:
                    answer = grounded_answer
            except Exception as e:
                logger.error(f"Grounded generation failed: {e}")
                used_fallback = True
        else:
            used_fallback = True
            
        if used_fallback:
            # No web sources or grounded answer failed - fallback to direct LLM answer
            logger.warning("Using direct LLM answer (fallback)")
            debug_log["fallback_used"] = True
            # Clear citations if we are falling back (because the answer isn't based on them)
            # BUT user says: "Images and sources are ADDITIONS"
            # If we used fallback because sources were IRRELEVANT, we shouldn't show them?
            # Or if we used fallback because Fetch Failed, we have no sources anyway.
            # If we have sources but LLM couldn't use them, maybe keep them as "See also"?
            # For now, let's keep citations if they exist, but answer is direct.
            answer = generate_direct_answer(question)
        
        return {
            "answer": answer,
            "citations": citations,
            "debug": debug_log
        }
        
    except Exception as e:
        # Catastrophic failure - still return LLM answer
        logger.error(f"Web search pipeline failed catastrophically: {e}")
        debug_log["errors"].append(f"Pipeline failure: {str(e)}")
        debug_log["fallback_used"] = True
        
        try:
            answer = generate_direct_answer(question)
        except Exception as e2:
            logger.error(f"Even LLM fallback failed: {e2}")
            answer = "I'm having trouble processing that request right now, but I'm here to help."
        
        return {
            "answer": answer,
            "citations": [],
            "debug": debug_log
        }
