"""
Demo script to test the new image and web retrieval features
Run this to see example outputs
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from web_retrieval.search_client import execute_web_query, execute_image_search
import json

print("="*70)
print("JARVIS RETRIEVAL DEMO")
print("="*70)

# Demo 1: Web Search
print("\n[DEMO 1] Web Search: 'quantum computing'")
print("-"*70)
results = execute_web_query("quantum computing", num_results=3)
print(f"Found {len(results)} results:\n")
for i, result in enumerate(results[:2], 1):
    print(f"{i}. {result['title']}")
    print(f"   URL: {result['url']}")
    print(f"   Snippet: {result['snippet'][:100]}...")
    print()

# Demo 2: Image Search
print("\n[DEMO 2] Image Search: 'mars rover'")
print("-"*70)
images = execute_image_search("mars rover", max_results=3)
print(f"Found {len(images)} images:\n")
for i, img in enumerate(images[:2], 1):
    print(f"{i}. {img['title']}")
    print(f"   Image URL: {img['image_url'][:60]}...")
    print(f"   Thumbnail: {img['thumbnail_url'][:60] if img['thumbnail_url'] else 'N/A'}...")
    print(f"   Dimensions: {img.get('width')}x{img.get('height')}")
    print()

# Demo 3: Heuristic Test
print("\n[DEMO 3] Image Heuristic Test")
print("-"*70)

def should_fetch_images(text):
    text = text.lower().strip()
    triggers = ["show me", "picture", "image", "photo", "look like", "who is", "what is a"]
    return any(trigger in text for trigger in triggers)

test_queries = [
    ("show me a cat", True),
    ("who is elon musk", True),
    ("what is the capital of france", False),
    ("picture of the eiffel tower", True),
    ("how to code in python", False),
]

for query, expected in test_queries:
    result = should_fetch_images(query)
    status = "✓" if result == expected else "✗"
    print(f"{status} '{query}' -> {'FETCH' if result else 'SKIP'} images")

print("\n" + "="*70)
print("DEMO COMPLETE")
print("="*70)
print("\nTo test in the web UI:")
print("1. Make sure the server is running (run_web.bat)")
print("2. Go to http://localhost:5000")
print("3. Try queries like:")
print("   - 'who is barack obama'")
print("   - 'show me pictures of mars'")
print("   - 'what is quantum computing'")
print("="*70)
