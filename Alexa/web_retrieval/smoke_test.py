import sys
import argparse
# Ensure Alexa folder is in sys.path if running as script from inside or outside
# But if running a module -m web_retrieval.smoke_test from Alexa/ it should be fine.

from .pipeline import web_search_answer

def run_smoke_test(query):
    print(f"--- Smoke Test: {query} ---")
    
    try:
        result = web_search_answer(query)
        print("\nAnswer:")
        print(result["answer"])
        
        print("\nCitations:")
        for c in result["citations"]:
            print(f"[{c['id']}] {c['title']} - {c['url']}")
            
        print("\nDebug Info:")
        print(f"Queries used: {result['debug']['queries']}")
        print(f"Ranked URLs: {len(result['debug']['ranked_urls'])}")
        print(f"Errors: {len(result['debug']['errors'])}")
        
    except Exception as e:
        print(f"Smoke test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = sys.argv[1]
    else:
        q = "What is the latest news about OpenAI?"
    run_smoke_test(q)
