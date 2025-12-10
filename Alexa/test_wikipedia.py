"""
Test Wikipedia extraction and enhanced search
"""
from tool_web import search_web

def test_wikipedia_extraction():
    print("="*70)
    print("TESTING WIKIPEDIA EXTRACTION")
    print("="*70 + "\n")
    
    # Test queries that should return Wikipedia results
    test_queries = [
        "Who is Albert Einstein?",
        "What is photosynthesis?",
        "Tell me about the Roman Empire",
        "What is Python programming language?",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 70)
        try:
            response = search_web(query)
            print(f"Response:\n{response}\n")
        except Exception as e:
            print(f"Error: {e}\n")
        print("=" * 70)

if __name__ == "__main__":
    test_wikipedia_extraction()
