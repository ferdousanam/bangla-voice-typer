import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import threading
import subprocess

_LOGGER_INITIALIZED = False
_LOG_FILE_PATH = None
_LOG_DIR_PATH = None


def _resolve_log_dir() -> str:
    """
    Resolves the directory where log files should be stored.
    Prefers a 'logs' subdirectory next to the app/executable.
    Falls back to %APPDATA%/BanglaVoiceTyper/logs or temp directory if unwritable.
    """
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        # src/core/logger.py -> src/core -> src -> project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    candidate = os.path.join(base_dir, "logs")
    try:
        os.makedirs(candidate, exist_ok=True)
        # Test write permission
        test_file = os.path.join(candidate, ".perm_test")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(test_file)
        return candidate
    except Exception:
        pass

    # Fallback: AppData / LocalAppData
    appdata = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    fallback = os.path.join(appdata, "BanglaVoiceTyper", "logs")
    try:
        os.makedirs(fallback, exist_ok=True)
        return fallback
    except Exception:
        import tempfile
        temp_dir = os.path.join(tempfile.gettempdir(), "BanglaVoiceTyper", "logs")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir


def get_log_dir_path() -> str:
    global _LOG_DIR_PATH
    if _LOG_DIR_PATH is None:
        _LOG_DIR_PATH = _resolve_log_dir()
    return _LOG_DIR_PATH


def get_log_file_path() -> str:
    global _LOG_FILE_PATH
    if _LOG_FILE_PATH is None:
        _LOG_FILE_PATH = os.path.join(get_log_dir_path(), "app.log")
    return _LOG_FILE_PATH


def setup_logging(level=logging.INFO) -> logging.Logger:
    """
    Configures application-wide logging with:
    1. Rotating file handler (UTF-8, 5MB max, 5 backups).
    2. Console stream handler (if terminal/stdout is active).
    3. Global sys.excepthook to capture uncaught crashes.
    4. Threading excepthook to capture thread crashes.
    """
    global _LOGGER_INITIALIZED
    logger = logging.getLogger("BanglaVoiceTyper")

    if _LOGGER_INITIALIZED:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    log_file = get_log_file_path()

    log_format = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)-7s] [%(name)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Rotating File Handler
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding="utf-8",
            delay=True
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"Failed to initialize file logger at {log_file}: {e}\n")

    # 2. Console Stream Handler (if console stdout is available)
    try:
        if sys.stdout and hasattr(sys.stdout, "write"):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(log_format)
            logger.addHandler(console_handler)
    except Exception:
        pass

    # 3. Global Exception Hook for main thread
    def _uncaught_exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical(
            "Uncaught exception in main thread:",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = _uncaught_exception_handler

    # 4. Threading Exception Hook for background worker threads
    if hasattr(threading, "excepthook"):
        def _thread_exception_handler(args):
            logger.critical(
                f"Uncaught exception in background thread '{args.thread.name}': {args.exc_type.__name__}: {args.exc_value}",
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
            )
        threading.excepthook = _thread_exception_handler

    _LOGGER_INITIALIZED = True
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Returns a child logger or the root app logger"""
    if not _LOGGER_INITIALIZED:
        setup_logging()
    if name:
        return logging.getLogger(f"BanglaVoiceTyper.{name}")
    return logging.getLogger("BanglaVoiceTyper")


def open_log_file():
    """Opens the application log file in default text editor or notepad"""
    log_file = get_log_file_path()
    if not os.path.exists(log_file):
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"--- Bangla Voice Typer Log File Initialized ---\n")
        except Exception:
            pass

    try:
        if sys.platform == "win32":
            os.startfile(log_file)
        else:
            subprocess.Popen(["xdg-open", log_file])
    except Exception:
        # Fallback to notepad
        try:
            subprocess.Popen(["notepad.exe", log_file])
        except Exception:
            pass


def open_log_folder():
    """Opens the folder containing the log file in file manager"""
    log_file = get_log_file_path()
    log_dir = get_log_dir_path()
    try:
        if sys.platform == "win32":
            if os.path.exists(log_file):
                subprocess.Popen(f'explorer.exe /select,"{os.path.abspath(log_file)}"')
            else:
                subprocess.Popen(f'explorer.exe "{os.path.abspath(log_dir)}"')
        else:
            subprocess.Popen(["xdg-open", log_dir])
    except Exception:
        pass
