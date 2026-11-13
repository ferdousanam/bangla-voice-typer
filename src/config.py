import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

DEFAULT_CONFIG = {
    "engine": "gemini",
    "gemini_api_key": "",
    "gemini_model": "gemini-3.5-flash",
    "theme": "system",
    "hotkey": "<ctrl>+<alt>+b",
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
    def __init__(self, filepath=CONFIG_FILE):
        self.filepath = filepath
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
