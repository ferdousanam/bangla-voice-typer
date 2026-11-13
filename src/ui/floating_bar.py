from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QColor, QCursor
from src.ui.styles import get_floating_bar_style, resolve_theme

def format_hotkey_label(hotkey_str: str) -> str:
    """Formats '<ctrl>+<alt>+b' to 'Ctrl + Alt + B'"""
    parts = hotkey_str.replace('<', '').replace('>', '').split('+')
    clean_parts = []
    for p in parts:
        p_clean = p.strip()
        if p_clean.lower() == 'ctrl':
            clean_parts.append('Ctrl')
        elif p_clean.lower() == 'shift':
            clean_parts.append('Shift')
        elif p_clean.lower() == 'alt':
            clean_parts.append('Alt')
        elif p_clean.lower() == 'space':
            clean_parts.append('Space')
        else:
            clean_parts.append(p_clean.upper())
    return " + ".join(clean_parts)

class FloatingBar(QWidget):
    def __init__(self, config_manager, on_mic_click=None, on_settings_click=None, on_history_click=None, on_cancel_click=None):
        super().__init__()
        self.config = config_manager
        self.on_mic_click = on_mic_click
        self.on_settings_click = on_settings_click
        self.on_history_click = on_history_click
        self.on_cancel_click = on_cancel_click

        self._is_active = False
        self._drag_pos = QPoint()
        self._is_dragging = False

        # Strictly fixed size to prevent any auto-resizing or jumping
        self.setFixedSize(310, 56)

        self._init_window_flags()
        self._init_ui()
        self.reset_to_idle()

    def _init_window_flags(self):
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.config.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def apply_theme(self):
        active_theme = resolve_theme(self.config.get("theme", "system"))
        self.setStyleSheet(get_floating_bar_style(active_theme))

    def _init_ui(self):
        self.apply_theme()
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Container Widget
        self.container = QWidget()
        self.container.setObjectName("FloatingContainer")
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(10, 4, 10, 4)
        container_layout.setSpacing(6)

        # Drag Handle Icon
        self.drag_handle = QLabel("⠿")
        self.drag_handle.setStyleSheet("color: #64748b; font-size: 15px; font-weight: bold; padding-left: 2px;")
        self.drag_handle.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
        self.drag_handle.setToolTip("টেনে স্ক্রিনের যেকোনো জায়গায় নিয়ে যান")
        container_layout.addWidget(self.drag_handle)

        # Circular Mic Button
        self.btn_mic = QPushButton("🎤")
        self.btn_mic.setObjectName("MicButton")
        self.btn_mic.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_mic.setToolTip("ভয়েস টাইপিং শুরু করুন")
        if self.on_mic_click:
            self.btn_mic.clicked.connect(self.on_mic_click)
        container_layout.addWidget(self.btn_mic)

        # Status Label (Strictly fixed width, only short status words)
        self.status_label = QLabel("প্রস্তুত")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setFixedWidth(54)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.status_label)

        # Hotkey Button (Keyboard icon with tooltip)
        self.btn_hotkey = QPushButton("⌨️")
        self.btn_hotkey.setProperty("class", "ActionButton")
        self.btn_hotkey.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_hotkey.setToolTip(self._get_hotkey_tooltip())
        if self.on_settings_click:
            self.btn_hotkey.clicked.connect(lambda: self.on_settings_click(tab_index=3))
        container_layout.addWidget(self.btn_hotkey)

        # History / Output Window Button
        self.btn_history = QPushButton("📝")
        self.btn_history.setProperty("class", "ActionButton")
        self.btn_history.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_history.setToolTip("টাইপিং হিস্ট্রি ও আউটপুট দেখুন")
        if self.on_history_click:
            self.btn_history.clicked.connect(self.on_history_click)
        container_layout.addWidget(self.btn_history)

        # Settings button
        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setProperty("class", "ActionButton")
        self.btn_settings.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_settings.setToolTip("সেটিংস")
        if self.on_settings_click:
            self.btn_settings.clicked.connect(lambda: self.on_settings_click())
        container_layout.addWidget(self.btn_settings)

        # Minimize to Tray / Cancel button
        self.btn_close = QPushButton("✕")
        self.btn_close.setProperty("class", "ActionButton")
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.setToolTip("ট্রে-তে লুকিয়ে রাখুন")
        self.btn_close.clicked.connect(self._on_close_clicked)
        container_layout.addWidget(self.btn_close)

        # Soft drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        main_layout.addWidget(self.container)

    def _on_close_clicked(self):
        """If recording or processing, clicking ✕ acts as Cancel. Otherwise hides to tray."""
        if self._is_active:
            if self.on_cancel_click:
                self.on_cancel_click()
            else:
                self.set_cancelled()
        else:
            self.hide()

    def _set_mic_state(self, state: str, icon: str):
        self.btn_mic.setText(icon)
        self.btn_mic.setProperty("state", state)
        self.btn_mic.style().unpolish(self.btn_mic)
        self.btn_mic.style().polish(self.btn_mic)

    def _get_hotkey_tooltip(self) -> str:
        hotkey_name = format_hotkey_label(self.config.get("hotkey", "ctrl+shift+b"))
        return (
            f"কীবোর্ড শর্টকাট:\n"
            f"• শুরু করতে: Win + Space (পরপর ২ বার) অথবা {hotkey_name}\n"
            f"• থামাতে: Win + Space (১ বার)\n"
            f"• বাতিল করতে: Esc (যেকোনো সময়)"
        )

    def set_listening(self):
        self._is_active = True
        self.show_widget_if_hidden()
        self._set_mic_state("recording", "⏹️")
        self.btn_mic.setToolTip("রেকর্ডিং থামাতে ক্লিক করুন (Win + Space)")
        self.btn_hotkey.setToolTip("থামাতে: Win + Space (১ বার চাপুন) অথবা ⏹️ বাটনে ক্লিক করুন\nবাতিল করতে: Esc চাপুন বা ✕ ক্লিক করুন")
        self.btn_close.setToolTip("রেকর্ডিং বাতিল করুন (Esc)")
        self.btn_close.setProperty("state", "cancel")
        self.btn_close.style().unpolish(self.btn_close)
        self.btn_close.style().polish(self.btn_close)
        self.status_label.setText("শুনছি...")
        self.status_label.setToolTip("কথা বলা শেষ হলে Win + Space চাপুন বা ⏹️ ক্লিক করুন\nবাতিল করতে Esc চাপুন বা ✕ ক্লিক করুন")
        self.status_label.setStyleSheet("color: #dc2626; font-weight: bold;")

    def set_processing(self):
        self._is_active = True
        self._set_mic_state("processing", "⏳")
        self.btn_mic.setToolTip("রূপান্তর বাতিল করতে ক্লিক করুন (Esc)")
        self.btn_close.setToolTip("রূপান্তর বাতিল করুন (Esc)")
        self.btn_close.setProperty("state", "cancel")
        self.btn_close.style().unpolish(self.btn_close)
        self.btn_close.style().polish(self.btn_close)
        self.status_label.setText("রূপান্তর...")
        self.status_label.setToolTip("টেক্সটে রূপান্তর হচ্ছে...\nবাতিল করতে ⏳ বা ✕ বাটনে চাপুন (বা Esc)")
        self.status_label.setStyleSheet("color: #d97706; font-weight: bold;")

    def set_success(self, _text=""):
        """Displays completion status without inserting full text to prevent resizing"""
        self._is_active = False
        self._set_mic_state("success", "✓")
        self.btn_close.setProperty("state", "")
        self.btn_close.style().unpolish(self.btn_close)
        self.btn_close.style().polish(self.btn_close)
        self.status_label.setText("সম্পন্ন ✓")
        self.status_label.setStyleSheet("color: #16a34a; font-weight: bold;")
        QTimer.singleShot(1800, self.reset_to_idle)

    def set_cancelled(self):
        """Displays cancellation status and smoothly resets to idle"""
        self._is_active = False
        self._set_mic_state("cancelled", "🚫")
        self.btn_close.setProperty("state", "")
        self.btn_close.style().unpolish(self.btn_close)
        self.btn_close.style().polish(self.btn_close)
        self.status_label.setText("বাতিল")
        self.status_label.setToolTip("ভয়েস টাইপিং বাতিল করা হয়েছে")
        self.status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
        QTimer.singleShot(1400, self.reset_to_idle)

    def set_error(self, message):
        self._is_active = False
        self._set_mic_state("idle", "⚠️")
        self.btn_close.setProperty("state", "")
        self.btn_close.style().unpolish(self.btn_close)
        self.btn_close.style().polish(self.btn_close)
        self.status_label.setText("সমস্যা ⚠️")
        self.status_label.setToolTip(message)
        self.status_label.setStyleSheet("color: #dc2626; font-weight: bold;")
        QTimer.singleShot(2500, self.reset_to_idle)

    def reset_to_idle(self):
        self._is_active = False
        self._set_mic_state("idle", "🎤")
        self.btn_mic.setToolTip("ভয়েস টাইপিং শুরু করতে Win + Double Space চাপুন")
        self.btn_hotkey.setToolTip(self._get_hotkey_tooltip())
        self.btn_close.setToolTip("ট্রে-তে লুকিয়ে রাখুন")
        self.btn_close.setProperty("state", "")
        self.btn_close.style().unpolish(self.btn_close)
        self.btn_close.style().polish(self.btn_close)

        self.status_label.setText("প্রস্তুত")
        self.status_label.setStyleSheet("")
        self.status_label.setToolTip("শুরু: Win + Space দুবার চাপুন | থামাতে: Win + Space একবার চাপুন | বাতিল: Esc")

        if self.config.get("auto_hide_widget", False):
            self.hide()

    def show_widget_if_hidden(self):
        if not self.isVisible():
            self.show()

    def update_window_flags(self):
        was_visible = self.isVisible()
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.config.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        if was_visible:
            self.show()

    # Smooth drag handling
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
