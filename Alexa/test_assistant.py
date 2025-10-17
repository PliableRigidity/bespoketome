# test_assistant.py
from dispatcher import handle_user_text

def main():
    print("🧠 Local Assistant Test Mode")
    print("Type a question and press Enter.")
    print("Examples:")
    print("  - what's the time")
    print("  - what's the time in tokyo")
    print("  - weather in singapore")
    print("  - what's the time and weather in new york")
    print("Type 'exit' to quit.\n")

    while True:
        user_text = input("You: ").strip()
        if not user_text:
            continue
        if user_text.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        try:
            reply = handle_user_text(user_text)
            print("Assistant:", reply)
        except Exception as e:
            print("⚠️ Error:", e)

if __name__ == "__main__":
    main()
