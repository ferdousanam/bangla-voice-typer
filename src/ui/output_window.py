import datetime
import pyperclip
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton
)
from PyQt6.QtCore import Qt
from src.ui.styles import resolve_theme, FONT_FAMILY

def get_output_window_style(theme: str) -> str:
    if theme == "light":
        return f"""
        QWidget {{
            background-color: #f8fafc;
            color: #0f172a;
            font-family: {FONT_FAMILY};
        }}
        QLabel#HeaderTitle {{
            color: #0f172a;
            font-size: 16px;
            font-weight: bold;
        }}
        QLabel#HeaderSubtitle {{
            color: #64748b;
            font-size: 12px;
        }}
        QTextEdit {{
            background-color: #ffffff;
            color: #0f172a;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            font-family: {FONT_FAMILY};
        }}
        QPushButton.ToolBtn {{
            background-color: #f1f5f9;
            color: #334155;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 7px 14px;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton.ToolBtn:hover {{
            background-color: #e2e8f0;
            color: #0f172a;
        }}
        QPushButton#CopyBtn {{
            background-color: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 7px 16px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton#CopyBtn:hover {{
            background-color: #1d4ed8;
        }}
        """
    else:
        return f"""
        QWidget {{
            background-color: #0d0f13;
            color: #f8fafc;
            font-family: {FONT_FAMILY};
        }}
        QLabel#HeaderTitle {{
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
        }}
        QLabel#HeaderSubtitle {{
            color: #94a3b8;
            font-size: 12px;
        }}
        QTextEdit {{
            background-color: #151821;
            color: #f8fafc;
            border: 1px solid #282d3b;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            font-family: {FONT_FAMILY};
        }}
        QPushButton.ToolBtn {{
            background-color: #1a1e28;
            color: #cbd5e1;
            border: 1px solid #282d3b;
            border-radius: 8px;
            padding: 7px 14px;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton.ToolBtn:hover {{
            background-color: #262c3a;
            color: #ffffff;
        }}
        QPushButton#CopyBtn {{
            background-color: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 7px 16px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton#CopyBtn:hover {{
            background-color: #1d4ed8;
        }}
        """

class OutputWindow(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setWindowTitle("টাইপিং হিস্ট্রি ও আউটপুট — বাংলা ভয়েস টাইপার")
        self.resize(480, 360)
        self._init_ui()
        self.apply_theme()

    def apply_theme(self):
        active_theme = resolve_theme(self.config.get("theme", "system"))
        self.setStyleSheet(get_output_window_style(active_theme))

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QLabel("📝 টাইপিং হিস্ট্রি ও আউটপুট")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        sub_header = QLabel("ভয়েস থেকে টাইপ হওয়া সমস্ত টেক্সট এখানে সংরক্ষিত থাকে")
        sub_header.setObjectName("HeaderSubtitle")
        layout.addWidget(sub_header)

        # Text display area
        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("কথা বললে এখানে আউটপুট টেক্সট জমা হবে...")
        layout.addWidget(self.text_area)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_clear = QPushButton("🗑️ পরিষ্কার করুন")
        self.btn_clear.setProperty("class", "ToolBtn")
        self.btn_clear.clicked.connect(self.text_area.clear)
        btn_layout.addWidget(self.btn_clear)

        btn_layout.addStretch()

        self.btn_copy = QPushButton("📋 সব কপি করুন")
        self.btn_copy.setObjectName("CopyBtn")
        self.btn_copy.clicked.connect(self._copy_all)
        btn_layout.addWidget(self.btn_copy)

        layout.addLayout(btn_layout)

    def append_output(self, text: str):
        """Append transcribed text with timestamp"""
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        formatted = f"[{now_str}] {text.strip()}\n"
        self.text_area.append(formatted)
        # Move cursor to end
        cursor = self.text_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_area.setTextCursor(cursor)

    def _copy_all(self):
        content = self.text_area.toPlainText().strip()
        if content:
            pyperclip.copy(content)
            self.btn_copy.setText("✓ কপি হয়েছে!")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, lambda: self.btn_copy.setText("📋 সব কপি করুন"))
