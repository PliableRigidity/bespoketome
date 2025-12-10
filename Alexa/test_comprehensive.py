"""
Comprehensive test for Jarvis's expanded search capabilities
"""
from dispatcher import handle_user_text
from context_manager import get_context

def test_comprehensive_search():
    print("="*60)
    print("TESTING JARVIS COMPREHENSIVE SEARCH CAPABILITIES")
    print("="*60 + "\n")
    
    # Clear context
    context = get_context()
    context.clear()
    
    test_queries = [
        # Specifications
        ("What are the specs of a Tesla Model 3?", "Car Specifications"),
        ("How much does an iPhone 15 cost?", "Product Pricing"),
        ("What's the top speed of a Bugatti Chiron?", "Performance Specs"),
        
        # How things work
        ("How does a car engine work?", "Mechanical Explanation"),
        ("How do you make coffee?", "How-to Guide"),
        ("Explain photosynthesis", "Scientific Explanation"),
        
        # General knowledge
        ("What is gravity?", "Physics Definition"),
        ("What is the capital of France?", "Geography"),
        
        # People
        ("Who is Elon Musk?", "Person Information"),
        
        # Comparisons
        ("Which is better iPhone or Samsung?", "Product Comparison"),
        
        # Current events
        ("Latest news on AI", "Current Events"),
    ]
    
    for query, category in test_queries:
        print(f"[{category}]")
        print(f"User: {query}")
        try:
            response = handle_user_text(query)
            print(f"Jarvis: {response[:200]}...")  # Show first 200 chars
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 60 + "\n")
    
    print("="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_comprehensive_search()
