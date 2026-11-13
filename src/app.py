import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.config import ConfigManager
from src.core.speech_engine import SpeechEngine
from src.core.hotkey_listener import HotkeyListener
from src.ui.floating_bar import FloatingBar
from src.ui.tray_icon import SystemTray, create_default_tray_icon
from src.ui.settings_dialog import SettingsDialog
from src.ui.output_window import OutputWindow

class VoiceTyperApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("BanglaVoiceTyper")
        self.app.setApplicationDisplayName("বাংলা ভয়েস টাইপার")
        self.app.setWindowIcon(create_default_tray_icon())

        # High-clarity native font setup
        base_font = QFont("Segoe UI", 10)
        base_font.setStyleHint(QFont.StyleHint.SansSerif)
        self.app.setFont(base_font)

        # 1. Config Manager
        self.config = ConfigManager()

        # 2. Core Engines
        self.speech_engine = SpeechEngine(self.config)
        self.hotkey_listener = HotkeyListener(self.config, speech_engine=self.speech_engine)

        # 3. Output Window (Separate Window for Transcription History)
        self.output_window = OutputWindow(self.config)
        self.settings_dialog = None

        # 4. Floating Bar (Strictly Fixed Size)
        self.floating_bar = FloatingBar(
            self.config,
            on_mic_click=self.trigger_recording,
            on_settings_click=self.open_settings,
            on_history_click=self.toggle_output_window
        )

        # 5. System Tray
        self.tray = SystemTray(
            self.app,
            self.floating_bar,
            on_mic_trigger=self.trigger_recording,
            on_settings_trigger=self.open_settings,
            on_history_trigger=self.toggle_output_window
        )

        self._connect_signals()
        self._position_floating_bar()

    def _connect_signals(self):
        # Win + Double Space -> Start Recording
        self.hotkey_listener.start_triggered.connect(self.speech_engine.start_recording)

        # Win + Single Space -> Stop Recording
        self.hotkey_listener.stop_triggered.connect(self.speech_engine.stop_recording)

        # Custom / Fallback Hotkey (Ctrl + Alt + B) -> Toggle Recording
        self.hotkey_listener.toggle_triggered.connect(self.speech_engine.toggle_recording)

        # Speech Engine state transitions -> Floating Bar updates
        self.speech_engine.listening_started.connect(self.floating_bar.set_listening)
        self.speech_engine.processing_started.connect(self.floating_bar.set_processing)
        self.speech_engine.transcription_success.connect(self.floating_bar.set_success)
        self.speech_engine.error_occurred.connect(self.floating_bar.set_error)

        # Also append output directly to the dedicated Output History Window
        self.speech_engine.transcription_success.connect(self.output_window.append_output)

    def _position_floating_bar(self):
        """Positions the fixed-size floating bar gracefully at top-center of primary screen"""
        screen = self.app.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = screen_geo.x() + (screen_geo.width() - self.floating_bar.width()) // 2
            y = screen_geo.y() + 50
            self.floating_bar.move(x, y)

    def trigger_recording(self):
        self.speech_engine.trigger_transcription()

    def open_settings(self):
        if self.settings_dialog is not None and self.settings_dialog.isVisible():
            self.settings_dialog.showNormal()
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            return

        self.settings_dialog = SettingsDialog(
            self.config,
            on_saved_callback=self._on_settings_saved,
            parent=None
        )
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def toggle_output_window(self):
        if self.output_window.isVisible():
            self.output_window.hide()
        else:
            self.output_window.show()
            self.output_window.raise_()
            self.output_window.activateWindow()

    def _on_settings_saved(self):
        # Re-apply updated configurations
        self.speech_engine._apply_settings()
        self.hotkey_listener.update_hotkey()
        self.floating_bar.apply_theme()
        self.floating_bar.update_window_flags()
        self.floating_bar.reset_to_idle()
        self.tray.update_theme()
        self.output_window.apply_theme()

    def run(self):
        # Start hotkey listener
        self.hotkey_listener.start()

        # Show tray & floating bar
        self.tray.show()
        if not self.config.get("auto_hide_widget", False):
            self.floating_bar.show()

        return self.app.exec()
