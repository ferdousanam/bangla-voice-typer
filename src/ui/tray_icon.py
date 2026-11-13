from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt
from src.ui.styles import get_tray_menu_style, resolve_theme

def create_default_tray_icon():
    """Generates a crisp 64x64 tray icon programmatically with Bengali letter 'ব'"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw rounded gradient/blue badge background
    painter.setBrush(QColor("#2563eb"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(4, 4, 56, 56, 16, 16)

    # Draw crisp Bangla 'ব' in Kalpurush / Nirmala UI
    painter.setPen(QColor("#ffffff"))
    font = QFont("Kalpurush", 28, QFont.Weight.Bold)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "ব")

    painter.end()
    return QIcon(pixmap)

class SystemTray(QSystemTrayIcon):
    def __init__(self, app, floating_bar, on_mic_trigger=None, on_settings_trigger=None, on_history_trigger=None):
        super().__init__()
        self.app = app
        self.floating_bar = floating_bar
        self.config = floating_bar.config
        self.on_mic_trigger = on_mic_trigger
        self.on_settings_trigger = on_settings_trigger
        self.on_history_trigger = on_history_trigger

        self.setIcon(create_default_tray_icon())
        self.setToolTip("বাংলা ভয়েস টাইপার (Bangla Voice Typer)")

        self._create_menu()
        self.activated.connect(self._on_tray_activated)

    def _create_menu(self):
        self.menu = QMenu()
        self.update_theme()

        action_mic = self.menu.addAction("🎙️ ভয়েস টাইপিং শুরু করুন")
        if self.on_mic_trigger:
            action_mic.triggered.connect(self.on_mic_trigger)

        action_toggle_bar = self.menu.addAction("👁️ ফ্লোটিং বার দেখান / লুকান")
        action_toggle_bar.triggered.connect(self._toggle_bar)

        action_history = self.menu.addAction("📝 টাইপিং হিস্ট্রি ও আউটপুট")
        if self.on_history_trigger:
            action_history.triggered.connect(self.on_history_trigger)

        action_settings = self.menu.addAction("⚙️ সেটিংস")
        if self.on_settings_trigger:
            action_settings.triggered.connect(self.on_settings_trigger)

        self.menu.addSeparator()

        action_exit = self.menu.addAction("❌ বন্ধ করুন (Exit)")
        action_exit.triggered.connect(self.app.quit)

        self.setContextMenu(self.menu)

    def update_theme(self):
        active_theme = resolve_theme(self.config.get("theme", "system"))
        if hasattr(self, 'menu') and self.menu:
            self.menu.setStyleSheet(get_tray_menu_style(active_theme))

    def _toggle_bar(self):
        if self.floating_bar.isVisible():
            self.floating_bar.hide()
        else:
            self.floating_bar.show()
            self.floating_bar.raise_()
            self.floating_bar.activateWindow()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self._toggle_bar()
