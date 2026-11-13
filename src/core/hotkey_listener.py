import time
from pynput import keyboard
from PyQt6.QtCore import QObject, pyqtSignal


def normalize_hotkey(hotkey_str: str) -> str:
    """
    Normalizes any hotkey format into a valid pynput hotkey string.
    Examples:
        'ctrl+alt+b'        -> '<ctrl>+<alt>+b'
        '<ctrl>+<alt>+b'    -> '<ctrl>+<alt>+b'
        'Ctrl + Alt + B'    -> '<ctrl>+<alt>+b'
        'Alt + Shift + B'   -> '<alt>+<shift>+b'
        'Ctrl + Alt + Space'-> '<ctrl>+<alt>+<space>'
    """
    cleaned = str(hotkey_str).lower().replace("<", "").replace(">", "").strip()
    parts = [p.strip() for p in cleaned.split("+") if p.strip()]
    normalized = []
    for p in parts:
        if p in ("ctrl", "control"):
            normalized.append("<ctrl>")
        elif p in ("alt", "option"):
            normalized.append("<alt>")
        elif p == "shift":
            normalized.append("<shift>")
        elif p in ("win", "cmd", "super"):
            normalized.append("<cmd>")
        elif p == "space":
            normalized.append("<space>")
        else:
            normalized.append(p)
    return "+".join(normalized)


class HotkeyListener(QObject):
    start_triggered = pyqtSignal()
    stop_triggered = pyqtSignal()
    toggle_triggered = pyqtSignal()

    def __init__(self, config_manager, speech_engine=None):
        super().__init__()
        self.config = config_manager
        self.speech_engine = speech_engine

        self.listener = None
        self.custom_hotkey = None
        self.win_down = False
        self.last_win_space_time = 0

        self._setup_custom_hotkey()

    def _setup_custom_hotkey(self):
        """Builds pynput HotKey using normalized configuration"""
        raw_hotkey = self.config.get("hotkey", "ctrl+shift+b")
        norm = normalize_hotkey(raw_hotkey)
        try:
            parsed_keys = keyboard.HotKey.parse(norm)
            self.custom_hotkey = keyboard.HotKey(parsed_keys, self._on_custom_hotkey_activated)
            print(f"[Hotkey Configured]: {norm}")
        except Exception as e:
            print(f"[Hotkey Config Error for '{norm}']: {e}. Falling back to '<ctrl>+<shift>+b'")
            parsed_keys = keyboard.HotKey.parse("<ctrl>+<shift>+b")
            self.custom_hotkey = keyboard.HotKey(parsed_keys, self._on_custom_hotkey_activated)

    def _on_custom_hotkey_activated(self):
        """Called when configured combination (e.g. Ctrl + Alt + B) is fully pressed"""
        print("[Hotkey Listener]: Custom shortcut triggered!")
        self.toggle_triggered.emit()

    def start(self):
        self.stop()
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
        except Exception as e:
            print(f"[Hotkey Listener Error]: {e}")

    def stop(self):
        if self.listener is not None:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None

    def update_hotkey(self):
        """Re-parse configuration and re-arm custom hotkey"""
        self._setup_custom_hotkey()

    def _on_press(self, key):
        # 1. Feed canonical key to pynput HotKey engine
        if self.listener and self.custom_hotkey:
            try:
                canonical = self.listener.canonical(key)
                self.custom_hotkey.press(canonical)
            except Exception:
                pass

        # 2. Track Windows (Super/Cmd) key state
        if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            self.win_down = True

        # 3. Handle Natural Win + Space Dictation Workflow
        elif key == keyboard.Key.space and self.win_down:
            now = time.time()
            is_rec = self.speech_engine.is_recording if self.speech_engine else False

            if is_rec:
                # When recording: Win + Single Space STOPS recording & types text
                print("[Hotkey Listener]: Win + Space STOP triggered")
                self.stop_triggered.emit()
                self.last_win_space_time = 0
            else:
                # When idle: Win + Double Space STARTS recording
                if (now - self.last_win_space_time) <= 0.55:
                    print("[Hotkey Listener]: Win + Space START triggered")
                    self.start_triggered.emit()
                    self.last_win_space_time = 0
                else:
                    self.last_win_space_time = now

    def _on_release(self, key):
        # 1. Update HotKey state
        if self.listener and self.custom_hotkey:
            try:
                canonical = self.listener.canonical(key)
                self.custom_hotkey.release(canonical)
            except Exception:
                pass

        # 2. Release Windows key
        if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            self.win_down = False
