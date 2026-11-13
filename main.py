"""
Bangla Voice Typer (বাংলা ভয়েস টাইপার)
Main entry point
"""
import sys
from src.app import VoiceTyperApp

def main():
    app = VoiceTyperApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()
