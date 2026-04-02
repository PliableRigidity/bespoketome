import logging
from web_retrieval.search_client import execute_image_search

logger = logging.getLogger(__name__)

def should_fetch_images(user_text: str) -> bool:
    """
    Heuristic to decide if we should fetch images.
    Returns True if the user input implies an interest in visual content.
    """
    text = user_text.lower().strip()
    
    triggers = [
        "show me", "picture", "image", "photo", 
        "look like", "looks like",
        "who is", "who are",  # Celebrities/People - usually want a face
        "what is a", "what is an"  # Definitions often benefit from images
    ]
    
    # Check for direct triggers
    if any(trigger in text for trigger in triggers):
        return True
        
    return False

def image_search(query: str) -> list:
    """
    Tool function to search for images.
    
    Returns list of image objects:
    [{ "title", "image_url", "thumbnail_url", "source_url", "width", "height" }]
    
    Never raises exceptions - returns empty list on failure.
    """
    try:
        # Sanitize query
        query = query.strip()
        if not query:
            logger.warning("Image search called with empty query")
            return []
        
        # Clean query of common prefixes for better search
        clean_query = query.lower()
        for prefix in ["show me ", "images of ", "pictures of ", "photos of "]:
            if clean_query.startswith(prefix):
                clean_query = clean_query[len(prefix):]
                break
        
        logger.info(f"Image search for: '{clean_query}'")
        results = execute_image_search(clean_query)
        logger.info(f"Image search returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Image search failed: {e}", exc_info=True)
        # Never crash - return empty list
        return []
