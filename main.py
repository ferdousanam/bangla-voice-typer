"""
Bangla Voice Typer (বাংলা ভয়েস টাইপার)
Main entry point
"""
import os
import sys
import platform

# Suppress Qt font database fallback warnings for scripts handled by system fallback
os.environ.setdefault("QT_LOGGING_RULES", "qt.text.font.db.warning=false")

from src.core.logger import setup_logging, get_log_file_path
from src.config import get_app_version, get_base_dir

def main():
    logger = setup_logging()
    app_version = get_app_version()
    logger.info("=" * 60)
    logger.info(f"Starting Bangla Voice Typer {app_version}")
    logger.info(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
    logger.info(f"Python: {platform.python_version()} ({sys.executable})")
    logger.info(f"Base Directory: {get_base_dir()}")
    logger.info(f"Log File: {get_log_file_path()}")
    logger.info("=" * 60)

    try:
        from src.app import VoiceTyperApp
        app = VoiceTyperApp()
        exit_code = app.run()
        logger.info(f"Bangla Voice Typer exited cleanly with code: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.critical("Fatal error encountered in application:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
