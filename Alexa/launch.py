"""
Launcher for the voice assistant
"""
import sys

def main():
    print("🚀 BespokeToMe Voice Assistant")
    print("=" * 50)
    print("\nChoose mode:")
    print("1. Voice Assistant (Full voice interaction)")
    print("2. Text Assistant (Text-only testing)")
    print("\nPress 1 or 2, then Enter: ", end="")
    
    choice = input().strip()
    
    if choice == "1":
        print("\n🎤 Starting Voice Assistant...")
        from voice_assistant import VoiceAssistant
        assistant = VoiceAssistant()
        assistant.run()
    elif choice == "2":
        print("\n⌨️ Starting Text Assistant...")
        from test_assistant import main as test_main
        test_main()
    else:
        print("❌ Invalid choice. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()


