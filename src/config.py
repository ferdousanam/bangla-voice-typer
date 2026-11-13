import json
import os
import sys

def get_base_dir() -> str:
    """Returns directory of executable when frozen (portable), or project root in dev mode"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_app_version() -> str:
    """Dynamically resolve application version from version.txt, package metadata, or fallback"""
    base_dir = get_base_dir()
    for candidate in ["version.txt", "VERSION"]:
        v_path = os.path.join(base_dir, candidate)
        if os.path.exists(v_path):
            try:
                with open(v_path, "r", encoding="utf-8") as f:
                    ver = f.read().strip()
                    if ver:
                        return ver if ver.startswith("v") else f"v{ver}"
            except Exception:
                pass
    try:
        from src import __version__
        return f"v{__version__.lstrip('v')}"
    except Exception:
        return "v2.0.0"

CONFIG_FILE = os.path.join(get_base_dir(), "config.json")

DEFAULT_CONFIG = {
    "engine": "gemini",
    "gemini_api_key": "",
    "gemini_model": "gemini-3.5-flash",
    "theme": "system",
    "hotkey": "ctrl+shift+b",
    "language": "bn-BD",
    "sound_feedback": True,
    "always_on_top": True,
    "auto_hide_widget": False,
    "energy_threshold": 300,
    "pause_threshold": 0.8,
    "timeout": 6,
    "phrase_time_limit": 18
}

class ConfigManager:
    def __init__(self, filepath=None):
        self.filepath = filepath or os.path.join(get_base_dir(), "config.json")
        self.config = self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            self.save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure all default keys exist
                for key, val in DEFAULT_CONFIG.items():
                    if key not in data:
                        data[key] = val
                return data
        except Exception:
            return DEFAULT_CONFIG.copy()

    def save(self, data=None):
        if data is not None:
            self.config = data
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save()
