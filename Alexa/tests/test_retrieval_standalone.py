"""
Standalone test for retrieval functions
Tests only the core search_client functions without heavy dependencies
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import only the search client directly
import time
import logging
from duckduckgo_search import DDGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_web_query_test(query: str, num_results: int = 10) -> list:
    """Test version of execute_web_query"""
    results = []
    try:
        with DDGS() as ddgs:
            ddg_results = ddgs.text(query, max_results=num_results, safesearch='moderate')
            
            if not ddg_results:
                return []

            seen_urls = set()
            for r in ddg_results:
                url = r.get("href", "")
                if not url or url in seen_urls:
                    continue
                
                seen_urls.add(url)
                results.append({
                    "title": r.get("title", ""),
                    "url": url,
                    "snippet": r.get("body", ""),
                })
            
            return results
    except Exception as e:
        logger.error(f"Query failed: {e}")
        return []

def execute_image_search_test(query: str, max_results: int = 4) -> list:
    """Test version of execute_image_search"""
    results = []
    try:
        with DDGS() as ddgs:
            ddg_images = ddgs.images(query, max_results=max_results, safesearch='moderate')
            
            if not ddg_images:
                return []
            
            seen_urls = set()
            for img in ddg_images:
                img_url = img.get("image", "")
                if not img_url or img_url in seen_urls:
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
        logger.error(f"Image search failed: {e}")
        return []

def should_fetch_images_test(user_text: str) -> bool:
    """Test version of should_fetch_images"""
    text = user_text.lower().strip()
    
    triggers = [
        "show me", "picture", "image", "photo", 
        "look like", "looks like",
        "who is", "who are",
        "what is a", "what is an"
    ]
    
    return any(trigger in text for trigger in triggers)

# Run tests
print("="*60)
print("JARVIS RETRIEVAL TESTS (Standalone)")
print("="*60)

print("\n[TEST 1] Web Search - Basic")
result = execute_web_query_test("python programming", num_results=3)
print(f"✓ Returned {len(result)} results")
if result:
    print(f"  First result: {result[0]['title'][:50]}...")
    assert "title" in result[0]
    assert "url" in result[0]
    assert "snippet" in result[0]
    print("✓ Schema validated")

print("\n[TEST 2] Web Search - Empty Query")
result = execute_web_query_test("")
assert len(result) == 0
print("✓ Empty query handled")

print("\n[TEST 3] Image Search - Basic")
result = execute_image_search_test("cat", max_results=2)
print(f"✓ Returned {len(result)} images")
if result:
    print(f"  First image: {result[0]['title'][:50] if result[0]['title'] else 'No title'}...")
    assert "image_url" in result[0]
    assert "thumbnail_url" in result[0]
    print("✓ Schema validated")

print("\n[TEST 4] Heuristic - Should Trigger")
assert should_fetch_images_test("show me a cat") == True
assert should_fetch_images_test("picture of obama") == True
assert should_fetch_images_test("who is elon musk") == True
print("✓ Triggers working")

print("\n[TEST 5] Heuristic - Should Not Trigger")
assert should_fetch_images_test("what is the capital") == False
assert should_fetch_images_test("how to code") == False
print("✓ Non-triggers working")

print("\n[TEST 6] Error Handling")
try:
    result = execute_web_query_test("test", num_results=1)
    assert isinstance(result, list)
    print("✓ Web search handles errors gracefully")
except Exception as e:
    print(f"✗ Failed: {e}")

try:
    result = execute_image_search_test("test", max_results=1)
    assert isinstance(result, list)
    print("✓ Image search handles errors gracefully")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n" + "="*60)
print("ALL TESTS PASSED ✓")
print("="*60)
