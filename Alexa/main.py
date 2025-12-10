from dispatcher import handle_user_text
from context_manager import get_context
import sys

def main():
    print("--------------------------------------------------")
    print("       JARVIS TERMINAL INTERFACE v2.0")
    print("--------------------------------------------------")
    print("Type 'exit' or 'quit' to stop.")
    print("Type 'clear context' to clear conversation history.")
    print("Type 'show context' to view conversation history.")
    print("\nExamples:")
    print(" - time in Tokyo")
    print(" - weather in London")
    print(" - latest news on AI")
    print(" - who is Elon Musk")
    print(" - what are the specs of a Tesla Model 3")
    print(" - how does a car engine work")
    print(" - what is photosynthesis")
    print(" - price of iPhone 15")
    print("--------------------------------------------------\n")
    
    context = get_context()
    
    while True:
        try:
            user_text = input("You: ").strip()
            if not user_text:
                continue
            if user_text.lower() in ["exit", "quit"]:
                print("Goodbye.")
                break
            
            # Handle context management commands
            if user_text.lower() == "clear context":
                context.clear()
                print("Jarvis: Conversation history cleared.\n")
                continue
            
            if user_text.lower() == "show context":
                summary = context.get_summary()
                print(f"Jarvis: {summary}\n")
                continue
            
            print("Thinking...", end="\r")
            response = handle_user_text(user_text)
            # Clear "Thinking..." line
            print(" " * 20, end="\r")
            print(f"Jarvis: {response}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
