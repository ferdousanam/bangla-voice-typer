import time
from pynput import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

class HotkeyListener(QObject):
    start_triggered = pyqtSignal()
    stop_triggered = pyqtSignal()
    toggle_triggered = pyqtSignal()

    def __init__(self, config_manager, speech_engine=None):
        super().__init__()
        self.config = config_manager
        self.speech_engine = speech_engine
        
        self.listener = None
        self.win_down = False
        self.ctrl_down = False
        self.alt_down = False
        self.last_win_space_time = 0

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
        # Refresh listener if needed
        self.start()

    def _on_press(self, key):
        # 1. Track Modifiers
        if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            self.win_down = True
        elif key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.ctrl_down = True
        elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            self.alt_down = True

        # 2. Check Win + Space Commands
        if key == keyboard.Key.space and self.win_down:
            now = time.time()
            is_rec = self.speech_engine.is_recording if self.speech_engine else False

            if is_rec:
                # When recording: Win + Single Space STOPS recording
                self.stop_triggered.emit()
                self.last_win_space_time = 0
            else:
                # When idle: Win + Double Space STARTS recording
                if (now - self.last_win_space_time) <= 0.55:
                    self.start_triggered.emit()
                    self.last_win_space_time = 0
                else:
                    self.last_win_space_time = now

        # 3. Check fallback/custom shortcut: Ctrl + Alt + B
        elif self.ctrl_down and self.alt_down and hasattr(key, 'char') and key.char and key.char.lower() == 'b':
            self.toggle_triggered.emit()

    def _on_release(self, key):
        if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            self.win_down = False
        elif key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.ctrl_down = False
        elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            self.alt_down = False
