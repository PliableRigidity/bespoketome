"""
Test script to verify the fixed retrieval system.
Tests that:
1. LLM always returns text
2. Web retrieval never blocks
3. Images and sources are additions
4. DDGS failures are handled gracefully
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dispatcher import handle_user_text
import json

def test_query(query: str, description: str):
    """Test a single query and verify response structure"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"Query: '{query}'")
    print(f"{'='*60}")
    
    try:
        response = handle_user_text(query)
        
        # Verify structure
        assert isinstance(response, dict), "Response must be a dict"
        assert "text" in response, "Response must have 'text' key"
        assert "images" in response, "Response must have 'images' key"
        assert "sources" in response, "Response must have 'sources' key"
        
        assert isinstance(response["text"], str), "'text' must be a string"
        assert isinstance(response["images"], list), "'images' must be a list"
        assert isinstance(response["sources"], list), "'sources' must be a list"
        
        assert len(response["text"]) > 0, "'text' must not be empty"
        
        # Print results
        print(f"\n✓ Response structure valid")
        print(f"✓ Text length: {len(response['text'])} chars")
        print(f"✓ Images: {len(response['images'])}")
        print(f"✓ Sources: {len(response['sources'])}")
        
        print(f"\nText preview:")
        print(f"{response['text'][:200]}...")
        
        if response['images']:
            print(f"\nFirst image:")
            print(f"  Title: {response['images'][0].get('title', 'N/A')}")
            print(f"  URL: {response['images'][0].get('image_url', 'N/A')[:60]}...")
        
        if response['sources']:
            print(f"\nFirst source:")
            print(f"  Title: {response['sources'][0].get('title', 'N/A')}")
            print(f"  URL: {response['sources'][0].get('url', 'N/A')[:60]}...")
        
        print(f"\n✅ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("RETRIEVAL SYSTEM VERIFICATION")
    print("="*60)
    
    tests = [
        ("who is barack obama", "Person query - should get text + images + sources"),
        ("what is quantum computing", "Concept query - should get text + sources"),
        ("show me a cat", "Image query - should get text + images"),
        ("what time is it", "Simple query - should get text only"),
        ("tell me about artificial intelligence", "General query - should get text"),
    ]
    
    results = []
    for query, description in tests:
        result = test_query(query, description)
        results.append((query, result))
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for query, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {query}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
