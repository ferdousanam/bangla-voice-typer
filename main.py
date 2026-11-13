"""
Bangla Voice Typer (বাংলা ভয়েস টাইপার)
Main entry point
"""
import os
import sys

# Suppress Qt font database fallback warnings for scripts handled by system fallback
os.environ.setdefault("QT_LOGGING_RULES", "qt.text.font.db.warning=false")

from src.app import VoiceTyperApp

def main():
    app = VoiceTyperApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()
