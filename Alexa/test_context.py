"""
Test script to verify context memory is working
"""
from context_manager import get_context
from dispatcher import handle_user_text

def test_context():
    print("Testing context memory...\n")
    
    # Clear any existing context
    context = get_context()
    context.clear()
    
    # Test 1: Ask about weather in a city
    print("Test 1: Ask about weather")
    response1 = handle_user_text("What's the weather in Tokyo?")
    print(f"User: What's the weather in Tokyo?")
    print(f"Jarvis: {response1}\n")
    
    # Test 2: Follow-up question using context
    print("Test 2: Follow-up question (should remember Tokyo)")
    response2 = handle_user_text("What about the time there?")
    print(f"User: What about the time there?")
    print(f"Jarvis: {response2}\n")
    
    # Show context
    print("Conversation history:")
    print(context.get_summary())
    print("\n" + "="*50 + "\n")
    
    # Test 3: Clear and verify
    context.clear()
    print("Context cleared.")
    print("Conversation history after clear:")
    print(context.get_summary())

if __name__ == "__main__":
    test_context()
