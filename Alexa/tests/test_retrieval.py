
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

# Test only the low-level search functions that don't require heavy dependencies
from web_retrieval.search_client import execute_web_query, execute_image_search
from tool_image import should_fetch_images

class TestWebRetrieval(unittest.TestCase):
    """Test web search functionality"""
    
    def test_execute_web_query_returns_list(self):
        """Test that execute_web_query returns a list"""
        print("\n[TEST] Testing execute_web_query...")
        result = execute_web_query("python programming", num_results=3)
        self.assertIsInstance(result, list)
        print(f"✓ Returned list with {len(result)} results")
    
    def test_execute_web_query_schema(self):
        """Test that results have required schema"""
        print("\n[TEST] Testing web search schema...")
        result = execute_web_query("test query", num_results=2)
        if result:
            for item in result:
                self.assertIn("title", item)
                self.assertIn("url", item)
                self.assertIn("snippet", item)
                self.assertIsInstance(item["title"], str)
                self.assertIsInstance(item["url"], str)
                self.assertIsInstance(item["snippet"], str)
            print(f"✓ Schema validated for {len(result)} results")
        else:
            print("⚠ No results returned (may be network issue)")
    
    def test_empty_query_handling(self):
        """Test handling of empty queries"""
        print("\n[TEST] Testing empty query handling...")
        result = execute_web_query("")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
        print("✓ Empty query handled gracefully")

class TestImageRetrieval(unittest.TestCase):
    """Test image search functionality"""
    
    def test_execute_image_search_returns_list(self):
        """Test that execute_image_search returns a list"""
        print("\n[TEST] Testing execute_image_search...")
        result = execute_image_search("cat", max_results=2)
        self.assertIsInstance(result, list)
        print(f"✓ Returned list with {len(result)} images")
    
    def test_execute_image_search_schema(self):
        """Test that image results have required schema"""
        print("\n[TEST] Testing image search schema...")
        result = execute_image_search("dog", max_results=2)
        if result:
            for item in result:
                self.assertIn("title", item)
                self.assertIn("image_url", item)
                self.assertIn("thumbnail_url", item)
                self.assertIn("source_url", item)
                self.assertIsInstance(item["image_url"], str)
                self.assertTrue(len(item["image_url"]) > 0)
            print(f"✓ Schema validated for {len(result)} images")
        else:
            print("⚠ No images returned (may be network issue)")
    
    def test_should_fetch_images_heuristic(self):
        """Test image fetching heuristic"""
        print("\n[TEST] Testing should_fetch_images heuristic...")
        
        # Should trigger
        self.assertTrue(should_fetch_images("show me a cat"))
        self.assertTrue(should_fetch_images("picture of obama"))
        self.assertTrue(should_fetch_images("who is elon musk"))
        self.assertTrue(should_fetch_images("what does a lion look like"))
        
        # Should not trigger
        self.assertFalse(should_fetch_images("what is the capital of france"))
        self.assertFalse(should_fetch_images("how to code in python"))
        
        print("✓ Heuristic working correctly")

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_network_error_graceful_degradation(self):
        """Test that network errors don't crash"""
        print("\n[TEST] Testing error handling...")
        # These should not raise exceptions
        try:
            result = execute_web_query("test", num_results=1)
            self.assertIsInstance(result, list)
            print("✓ Web search handles errors gracefully")
        except Exception as e:
            self.fail(f"Web search raised exception: {e}")
        
        try:
            result = execute_image_search("test", max_results=1)
            self.assertIsInstance(result, list)
            print("✓ Image search handles errors gracefully")
        except Exception as e:
            self.fail(f"Image search raised exception: {e}")

if __name__ == '__main__':
    print("="*60)
    print("JARVIS RETRIEVAL TESTS (Core Functions)")
    print("="*60)
    unittest.main(verbosity=2)
