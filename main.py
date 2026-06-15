"""Main entry point for the AI Assistant."""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description="AI Assistant")
    parser.add_argument("--mode", choices=["cli", "api", "voice"],
                        default="cli", help="Run mode")
    args = parser.parse_args()

    from core.assistant import AIAssistant

    print("Starting AI Assistant...")
    assistant = AIAssistant()

    if args.mode == "cli":
        from cli.interface import CLI
        CLI(assistant).run()
    elif args.mode == "api":
        from api.server import start_server
        import config
        start_server(assistant, config.API_HOST, config.API_PORT)
    elif args.mode == "voice":
        from voice.voice_assistant import VoiceAssistant
        VoiceAssistant(assistant).run()


if __name__ == "__main__":
    main()
