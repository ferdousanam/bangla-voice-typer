from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QWidget,
    QSpinBox, QListWidget, QListWidgetItem, QStackedWidget,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor
from src.ui.styles import get_settings_dialog_style, resolve_theme
from src.config import get_app_version
from src.core.logger import open_log_file, open_log_folder, get_log_file_path


class ToggleSwitch(QWidget):
    """
    Modern styled toggle switch.
    Smooth pill rendering with antialiased sliding thumb.
    """
    toggled = pyqtSignal(bool)

    def __init__(self, checked=False, parent=None, theme="dark"):
        super().__init__(parent)
        self._checked = bool(checked)
        self._theme = theme
        self.setFixedSize(44, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool):
        if self._checked != checked:
            self._checked = bool(checked)
            self.update()
            self.toggled.emit(self._checked)

    def set_theme(self, theme: str):
        self._theme = theme
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        radius = h / 2.0

        if self._checked:
            # Active accent color (OpenCode accent blue)
            bg_color = QColor("#2563eb")
            thumb_color = QColor("#ffffff")
            thumb_x = w - h + 2.0
        else:
            # Inactive color based on theme
            bg_color = QColor("#3f3f46") if self._theme == "dark" else QColor("#cbd5e1")
            thumb_color = QColor("#e4e4e7") if self._theme == "dark" else QColor("#ffffff")
            thumb_x = 2.0

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(QRectF(0, 0, w, h), radius, radius)

        thumb_size = h - 4.0
        painter.setBrush(thumb_color)
        painter.drawEllipse(QRectF(thumb_x, 2.0, thumb_size, thumb_size))
        painter.end()


class SettingsDialog(QDialog):
    """
    Modern Settings Dialog for Bangla Voice Typer.
    Features:
    - 2-column layout (Sidebar navigation + Card-based content)
    - Custom interactive toggle switches
    - Quick API key visibility toggle
    - Full Bangla UI localization
    """
    def __init__(self, config_manager, on_saved_callback=None, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.on_saved_callback = on_saved_callback
        self.switches = []

        self.setWindowTitle("সেটিংস — বাংলা ভয়েস টাইপার")
        self.resize(800, 580)
        self.setMinimumSize(740, 520)
        self.setModal(False)

        self._init_ui()
        self.apply_theme()

    def apply_theme(self):
        active_theme = resolve_theme(self.config.get("theme", "system"))
        self.setStyleSheet(get_settings_dialog_style(active_theme))
        bg_col = "#101012" if active_theme == "dark" else "#f8f9fa"
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{ background-color: {bg_col}; border: none; }}
            QScrollArea > QWidget > QWidget {{ background-color: {bg_col}; }}
        """)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for switch in self.switches:
            switch.set_theme(active_theme)

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # -----------------------------
        # Main Body: Sidebar + Content
        # -----------------------------
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = self._create_sidebar()
        body_layout.addWidget(sidebar)

        # 2. Right Content Area (Stacked pages with scroll)
        content_container = QWidget()
        content_container.setObjectName("ContentContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(24, 20, 24, 16)
        content_layout.setSpacing(12)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("SettingsScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.stack = QStackedWidget()
        self.stack.setObjectName("SettingsStack")

        # Add Category Pages
        self.stack.addWidget(self._create_ai_page())          # Index 0: AI Engine
        self.stack.addWidget(self._create_general_page())     # Index 1: General & Theme
        self.stack.addWidget(self._create_behavior_page())    # Index 2: Behavior & Audio
        self.stack.addWidget(self._create_shortcuts_page())   # Index 3: Shortcuts
        self.stack.addWidget(self._create_about_page())       # Index 4: About

        self.scroll_area.setWidget(self.stack)
        content_layout.addWidget(self.scroll_area)
        body_layout.addWidget(content_container, 1)

        root_layout.addWidget(body_widget, 1)

        # -----------------------------
        # Dialog Bottom Footer
        # -----------------------------
        footer = self._create_footer()
        root_layout.addWidget(footer)

        # Connect Sidebar list to Stacked Widget
        self.sidebar_list.currentRowChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int):
        self.stack.setCurrentIndex(index)
        self.scroll_area.verticalScrollBar().setValue(0)

    # -------------------------------------------------------------------------
    # UI Component Builders
    # -------------------------------------------------------------------------

    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("SidebarContainer")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 16)
        layout.setSpacing(10)

        # Top Title & Subtitle
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title_box.setContentsMargins(6, 0, 6, 8)

        lbl_title = QLabel("⚙️ সেটিংস")
        lbl_title.setObjectName("SidebarTitle")
        title_box.addWidget(lbl_title)

        lbl_sub = QLabel("বাংলা ভয়েস টাইপার")
        lbl_sub.setObjectName("SidebarSubtitle")
        title_box.addWidget(lbl_sub)
        layout.addLayout(title_box)

        # Category Group Header
        lbl_group = QLabel("কনফিগারেশন")
        lbl_group.setObjectName("NavGroupHeader")
        layout.addWidget(lbl_group)

        # Navigation List (OpenCode sidebar items)
        self.sidebar_list = QListWidget()
        self.sidebar_list.setObjectName("SidebarList")
        self.sidebar_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        nav_items = [
            ("✨  এআই ইঞ্জিন", "AI Models & Recognition Engine"),
            ("⚙️  সাধারণ ও ভাষা", "App Theme and Typing Language"),
            ("🎙️  আচরণ ও অডিও", "Audio Feedback & Display Options"),
            ("⌨️  কীবোর্ড শর্টকাট", "Hotkeys & Windows Shortcuts"),
            ("ℹ️  পরিচিতি", "App info, Version & Credits")
        ]

        for text, tooltip in nav_items:
            item = QListWidgetItem(text)
            item.setToolTip(tooltip)
            self.sidebar_list.addItem(item)

        self.sidebar_list.setCurrentRow(0)
        layout.addWidget(self.sidebar_list, 1)

        return sidebar

    def _create_footer(self) -> QWidget:
        footer = QWidget()
        footer.setObjectName("DialogFooter")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(12)

        lbl_hint = QLabel("💡 পরিবর্তন সম্পন্ন হলে 'সংরক্ষণ করুন' বাটনে চাপুন")
        lbl_hint.setObjectName("FooterHint")
        layout.addWidget(lbl_hint)

        layout.addStretch()

        self.btn_cancel = QPushButton("বাতিল")
        self.btn_cancel.setObjectName("CancelButton")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("সংরক্ষণ করুন ✓")
        self.btn_save.setObjectName("SaveButton")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self._save_and_close)
        layout.addWidget(self.btn_save)

        return footer

    def _create_card(self, title: str = None) -> (QFrame, QVBoxLayout):
        """Creates an OpenCode-style settings list card"""
        card = QFrame()
        card.setObjectName("SettingsCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        if title:
            lbl_title = QLabel(title)
            lbl_title.setObjectName("CardSectionTitle")
            layout.addWidget(lbl_title)
            layout.addWidget(self._create_separator())

        return card, layout

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setObjectName("RowSeparator")
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        return line

    def _create_setting_row(self, title: str, subtitle: str, control_widget: QWidget) -> QWidget:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 4, 0, 4)
        row_layout.setSpacing(16)

        # Left label stack
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("RowTitle")
        text_layout.addWidget(lbl_title)

        if subtitle:
            lbl_sub = QLabel(subtitle)
            lbl_sub.setObjectName("RowSubtitle")
            lbl_sub.setWordWrap(True)
            text_layout.addWidget(lbl_sub)

        row_layout.addLayout(text_layout, 1)
        row_layout.addWidget(control_widget, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return row

    # -------------------------------------------------------------------------
    # Category Pages
    # -------------------------------------------------------------------------

    def _create_ai_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header
        lbl_head = QLabel("✨ এআই ইঞ্জিন সেটিংস")
        lbl_head.setObjectName("PageTitle")
        layout.addWidget(lbl_head)

        lbl_desc = QLabel("আপনার পছন্দ অনুযায়ী স্মার্ট এআই মডেল অথবা সরাসরি Google STT বেছে নিন।")
        lbl_desc.setObjectName("PageSubtitle")
        layout.addWidget(lbl_desc)

        # Card 1: Engine Selection
        card_engine, engine_layout = self._create_card("ইঞ্জিন নির্বাচন")

        self.combo_engine = QComboBox()
        self.combo_engine.setMinimumWidth(320)
        self.combo_engine.addItem("🚀 Gemini Flash (স্মার্ট এআই — অটো বিরামচিহ্ন)", "gemini")
        self.combo_engine.addItem("🎙️ Google STT (ফ্রি, বেসিক — কী লাগবে না)", "google")

        current_engine = self.config.get("engine", "gemini")
        idx_engine = self.combo_engine.findData(current_engine)
        if idx_engine >= 0:
            self.combo_engine.setCurrentIndex(idx_engine)

        row_engine = self._create_setting_row(
            "ভয়েস রেকগনিশন ইঞ্জিন",
            "Gemini AI দীর্ঘ বাক্যে স্বয়ংক্রিয় দাঁড়ি-কমা যোগ করে, Google STT লাইটওয়েট ও আনলিমিটেড।",
            self.combo_engine
        )
        engine_layout.addWidget(row_engine)
        layout.addWidget(card_engine)

        # Card 2: Gemini Configuration (Visible if Gemini is selected)
        self.gemini_card, gemini_layout = self._create_card("Gemini এআই কনফিগারেশন")

        # Model Selector
        self.combo_gemini_model = QComboBox()
        self.combo_gemini_model.setMinimumWidth(320)
        self.combo_gemini_model.addItem("⚡ gemini-3.1-flash-lite (সুপার ফাস্ট — রিকমেন্ডেড)", "gemini-3.1-flash-lite")
        self.combo_gemini_model.addItem("🚀 gemini-3.5-flash (উন্নত ও স্থিতিশীল)", "gemini-3.5-flash")
        self.combo_gemini_model.addItem("🧪 gemini-3.8-flash (সর্বশেষ প্রিভিউ)", "gemini-3.8-flash")

        current_model = self.config.get("gemini_model", "gemini-3.1-flash-lite")
        idx_model = self.combo_gemini_model.findData(current_model)
        if idx_model >= 0:
            self.combo_gemini_model.setCurrentIndex(idx_model)

        row_model = self._create_setting_row(
            "Gemini মডেল",
            "বাংলা ট্রান্সক্রিপশনের জন্য প্রস্তাবিত মডেল নির্বাচন করুন।",
            self.combo_gemini_model
        )
        gemini_layout.addWidget(row_model)
        gemini_layout.addWidget(self._create_separator())

        # API Key Input Row with Eye Toggle
        api_key_box = QWidget()
        api_key_layout = QHBoxLayout(api_key_box)
        api_key_layout.setContentsMargins(0, 0, 0, 0)
        api_key_layout.setSpacing(6)

        self.input_api_key = QLineEdit()
        self.input_api_key.setMinimumWidth(280)
        self.input_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_api_key.setPlaceholderText("AIzaSy... API Key দিন")
        self.input_api_key.setText(self.config.get("gemini_api_key", ""))
        api_key_layout.addWidget(self.input_api_key)

        self.btn_eye = QPushButton("👁️")
        self.btn_eye.setObjectName("EyeButton")
        self.btn_eye.setToolTip("API Key দেখুন / লুকান")
        self.btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eye.clicked.connect(self._toggle_api_key_visibility)
        api_key_layout.addWidget(self.btn_eye)

        row_key = self._create_setting_row(
            "Google AI API Key",
            "আপনার নিরাপদ Gemini API Key (aistudio.google.com থেকে সংগ্রহ করুন)।",
            api_key_box
        )
        gemini_layout.addWidget(row_key)
        gemini_layout.addWidget(self._create_separator())

        # Direct link helper
        lbl_tip = QLabel('<a href="https://aistudio.google.com/apikey" style="color: #38bdf8; text-decoration: none;">🔗 Google AI Studio থেকে ফ্রি API Key সংগ্রহ করতে এখানে ক্লিক করুন ↗</a>')
        lbl_tip.setOpenExternalLinks(True)
        lbl_tip.setStyleSheet("font-size: 12px; padding: 2px 0;")
        gemini_layout.addWidget(lbl_tip)

        layout.addWidget(self.gemini_card)

        # Card 3: Google STT Notice (Visible if Google STT is selected)
        self.stt_card, stt_layout = self._create_card("Google STT মোড সক্রিয়")
        lbl_notice = QLabel(
            "✅ <b>Google STT সক্রিয় রয়েছে:</b>\n"
            "এই মোডে কোনো প্রকার API Key লাগবে না। সরাসরি ইন্টারনেট কানেকশন থাকলেই "
            "সীমাহীনভাবে সাধারণ বাংলা ভয়েস টাইপিং চলবে।"
        )
        lbl_notice.setObjectName("NoticeBox")
        lbl_notice.setWordWrap(True)
        stt_layout.addWidget(lbl_notice)
        layout.addWidget(self.stt_card)

        layout.addStretch()

        # Connect engine switcher
        self.combo_engine.currentIndexChanged.connect(self._update_engine_visibility)
        self._update_engine_visibility()

        return page

    def _toggle_api_key_visibility(self):
        if self.input_api_key.echoMode() == QLineEdit.EchoMode.Password:
            self.input_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_eye.setText("🙈")
        else:
            self.input_api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_eye.setText("👁️")

    def _update_engine_visibility(self):
        is_gemini = self.combo_engine.currentData() == "gemini"
        self.gemini_card.setVisible(is_gemini)
        self.stt_card.setVisible(not is_gemini)

    def _create_general_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header
        lbl_head = QLabel("⚙️ সাধারণ সেটিংস")
        lbl_head.setObjectName("PageTitle")
        layout.addWidget(lbl_head)

        lbl_desc = QLabel("অ্যাপ্লিকেশনের ডিসপ্লে থিম এবং ভয়েস ইনপুট ভাষা কাস্টমাইজ করুন।")
        lbl_desc.setObjectName("PageSubtitle")
        layout.addWidget(lbl_desc)

        # Card 1: Appearance & Language
        card, card_layout = self._create_card("অ্যাপ রূপরেখা ও ভাষা")

        # Theme Selector
        self.combo_theme = QComboBox()
        self.combo_theme.setMinimumWidth(260)
        self.theme_map = {
            "system": "💻 সিস্টেম ডিফল্ট (System)",
            "dark": "🌙 ডার্ক মোড (Dark Mode)",
            "light": "☀️ লাইট মোড (Light Mode)"
        }
        for code, label in self.theme_map.items():
            self.combo_theme.addItem(label, code)

        current_theme = self.config.get("theme", "system")
        idx_theme = self.combo_theme.findData(current_theme)
        if idx_theme >= 0:
            self.combo_theme.setCurrentIndex(idx_theme)

        self.combo_theme.currentIndexChanged.connect(self._on_theme_preview)

        row_theme = self._create_setting_row(
            "অ্যাপ থিম (Theme)",
            "উইন্ডোজ কালার স্কিমের সাথে সংগতিপূর্ণ আধুনিক ইন্টারফেস।",
            self.combo_theme
        )
        card_layout.addWidget(row_theme)
        card_layout.addWidget(self._create_separator())

        # Language Selector
        self.combo_lang = QComboBox()
        self.combo_lang.setMinimumWidth(260)
        self.lang_map = {
            "bn-BD": "বাংলা (বাংলাদেশ) — ডিফল্ট",
            "bn-IN": "বাংলা (ভারত)",
            "en-US": "ইংরেজি (English - US)"
        }
        for code, label in self.lang_map.items():
            self.combo_lang.addItem(label, code)

        current_lang = self.config.get("language", "bn-BD")
        idx_lang = self.combo_lang.findData(current_lang)
        if idx_lang >= 0:
            self.combo_lang.setCurrentIndex(idx_lang)

        row_lang = self._create_setting_row(
            "টাইপিং ভাষা (Language)",
            "ভয়েস রেকগনিশনের জন্য আঞ্চলিক উচ্চারণ ও ভাষা বেছে নিন।",
            self.combo_lang
        )
        card_layout.addWidget(row_lang)

        layout.addWidget(card)
        layout.addStretch()
        return page

    def _on_theme_preview(self):
        selected_theme = self.combo_theme.currentData()
        active_theme = resolve_theme(selected_theme)
        self.setStyleSheet(get_settings_dialog_style(active_theme))
        bg_col = "#101012" if active_theme == "dark" else "#f8f9fa"
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{ background-color: {bg_col}; border: none; }}
            QScrollArea > QWidget > QWidget {{ background-color: {bg_col}; }}
        """)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for switch in self.switches:
            switch.set_theme(active_theme)

    def _create_behavior_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header
        lbl_head = QLabel("🎙️ আচরণ ও অডিও")
        lbl_head.setObjectName("PageTitle")
        layout.addWidget(lbl_head)

        lbl_desc = QLabel("অডিও বিপিং ও ফ্লোটিং উইন্ডোর কার্যপদ্ধতি নিয়ন্ত্রণ করুন।")
        lbl_desc.setObjectName("PageSubtitle")
        layout.addWidget(lbl_desc)

        # Card 1: Toggle Switches
        card, card_layout = self._create_card("ইন্টারফেস ও শব্দ নিয়ন্ত্রণ")

        # Sound Feedback Switch
        active_theme = resolve_theme(self.config.get("theme", "system"))
        self.sw_sound = ToggleSwitch(self.config.get("sound_feedback", True), theme=active_theme)
        self.switches.append(self.sw_sound)

        row_sound = self._create_setting_row(
            "শব্দ সংকেত (Audio Beep)",
            "রেকর্ডিং শুরু ও বন্ধ হওয়ার মুহূর্তে ছোট শব্দ সংকেত বাজান।",
            self.sw_sound
        )
        card_layout.addWidget(row_sound)
        card_layout.addWidget(self._create_separator())

        # Always on Top Switch
        self.sw_top = ToggleSwitch(self.config.get("always_on_top", True), theme=active_theme)
        self.switches.append(self.sw_top)

        row_top = self._create_setting_row(
            "অলওয়েজ অন টপ (Always on top)",
            "ফ্লোটিং বার সবসময় স্ক্রিনে অন্যান্য সকল উইন্ডোর উপরে দৃশ্যমান থাকবে।",
            self.sw_top
        )
        card_layout.addWidget(row_top)
        card_layout.addWidget(self._create_separator())

        # Auto Hide Switch
        self.sw_autohide = ToggleSwitch(self.config.get("auto_hide_widget", False), theme=active_theme)
        self.switches.append(self.sw_autohide)

        row_autohide = self._create_setting_row(
            "অটো-হাইড উইজেট (Auto Hide)",
            "টাইপিং বা রেকর্ডিং না চললে ফ্লোটিং বার স্বয়ংক্রিয়ভাবে লুকিয়ে রাখা হবে।",
            self.sw_autohide
        )
        card_layout.addWidget(row_autohide)

        layout.addWidget(card)

        # Card 2: Recording Limits & Smart Mode Info
        card_limit, limit_layout = self._create_card("রেকর্ডিং ও স্মার্ট মোড")

        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(20, 300)
        self.spin_timeout.setSuffix(" সেকেন্ড")
        self.spin_timeout.setFixedWidth(130)
        self.spin_timeout.setValue(int(self.config.get("phrase_time_limit", 180)))

        row_spin = self._create_setting_row(
            "সর্বোচ্চ রেকর্ড সময় (Phrase Limit)",
            "একটানা কথা বলার সর্বোচ্চ সময়সীমা (ডিফল্ট ১৮০ সেকেন্ড)।",
            self.spin_timeout
        )
        limit_layout.addWidget(row_spin)
        limit_layout.addWidget(self._create_separator())

        lbl_smart_info = QLabel(
            "💡 <b>স্মার্ট মোড সক্রিয়:</b> কথা বলার মাঝে সাময়িক নীরবতা আসলেও রেকর্ড স্বয়ংক্রিয়ভাবে বন্ধ হবে না। "
            "আপনার পুরো বাক্য বা অনুচ্ছেদ শেষ হলে কীবোর্ড শর্টকাট বা ⏹️ বাটনে চাপুন।"
        )
        lbl_smart_info.setObjectName("InfoBox")
        lbl_smart_info.setWordWrap(True)
        limit_layout.addWidget(lbl_smart_info)

        layout.addWidget(card_limit)
        layout.addStretch()
        return page

    def _create_shortcuts_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header
        lbl_head = QLabel("⌨️ কীবোর্ড শর্টকাট")
        lbl_head.setObjectName("PageTitle")
        layout.addWidget(lbl_head)

        lbl_desc = QLabel("যেকোনো অ্যাপে দ্রুত ভয়েস টাইপিং শুরু বা বন্ধ করতে শর্টকাট ব্যবহার করুন।")
        lbl_desc.setObjectName("PageSubtitle")
        layout.addWidget(lbl_desc)

        # Card 1: Primary Hotkey
        card, card_layout = self._create_card("গ্লোবাল টগল শর্টকাট")

        self.combo_hotkey = QComboBox()
        self.combo_hotkey.setMinimumWidth(260)
        self.hotkey_presets = [
            ("Ctrl + Shift + B (ডিফল্ট)", "ctrl+shift+b"),
            ("Ctrl + Alt + B", "ctrl+alt+b"),
            ("Ctrl + Alt + V", "ctrl+alt+v"),
            ("Alt + Shift + B", "alt+shift+b"),
            ("Ctrl + Alt + Space", "ctrl+alt+space")
        ]
        for label, val in self.hotkey_presets:
            self.combo_hotkey.addItem(label, val)

        current_hotkey = str(self.config.get("hotkey", "ctrl+shift+b")).lower().replace("<", "").replace(">", "").strip()
        idx_hotkey = -1
        for i, (_, val) in enumerate(self.hotkey_presets):
            if val == current_hotkey:
                idx_hotkey = i
                break

        if idx_hotkey >= 0:
            self.combo_hotkey.setCurrentIndex(idx_hotkey)
        else:
            self.combo_hotkey.addItem(f"কাস্টম ({current_hotkey})", current_hotkey)
            self.combo_hotkey.setCurrentIndex(self.combo_hotkey.count() - 1)

        row_hotkey = self._create_setting_row(
            "ভয়েস টাইপার টগল শর্টকাট",
            "এই কীবোর্ড সংমিশ্রণে ভয়েস টাইপিং তাৎক্ষণিকভাবে অন বা অফ হবে।",
            self.combo_hotkey
        )
        card_layout.addWidget(row_hotkey)
        card_layout.addWidget(self._create_separator())

        # Windows double-tap shortcut badge
        lbl_badge = QLabel("Win + Space")
        lbl_badge.setObjectName("KbdBadge")

        row_win = self._create_setting_row(
            "হ্যান্ডস-ফ্রি কুইক ট্যাপ",
            "Win + Space পরপর ২ বার চাপলে রেকর্ড শুরু হয়, এবং ১ বার চাপলে বন্ধ হয়ে লেখা টাইপ হয়।",
            lbl_badge
        )
        card_layout.addWidget(row_win)

        layout.addWidget(card)

        # Card 2: Guidance
        card_guide, guide_layout = self._create_card("শর্টকাট ব্যবহারের নিয়ম")
        lbl_guide = QLabel(
            "📌 <b>কীভাবে ব্যবহার করবেন:</b><br>"
            "১. যেকোনো লেখার জায়গায় (Notepad, Word, Browser, Chat) কার্সর রাখুন।<br>"
            "২. <code>Ctrl + Shift + B</code> চাপুন (শব্দ হবে এবং ফ্লোটিং বার লাল হয়ে রেকর্ড শুরু করবে)।<br>"
            "৩. স্বাভাবিকভাবে বাংলায় কথা বলুন।<br>"
            "৪. কথা শেষ হলে আবার <code>Ctrl + Shift + B</code> চাপুন। লেখা স্বয়ংক্রিয়ভাবে নির্ভুলভাবে টাইপ হয়ে যাবে!"
        )
        lbl_guide.setObjectName("InfoBox")
        lbl_guide.setWordWrap(True)
        guide_layout.addWidget(lbl_guide)
        layout.addWidget(card_guide)

        layout.addStretch()
        return page

    def _create_about_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header
        lbl_head = QLabel("ℹ️ পরিচিতি")
        lbl_head.setObjectName("PageTitle")
        layout.addWidget(lbl_head)

        lbl_desc = QLabel("বাংলা ভয়েস টাইপার ও এর প্রযুক্তিগত বিবরণ।")
        lbl_desc.setObjectName("PageSubtitle")
        layout.addWidget(lbl_desc)

        # Card 1: App Info Card (OpenCode style About card)
        card, card_layout = self._create_card("সফটওয়্যার তথ্য")

        app_title = QLabel("🎙️ বাংলা ভয়েস টাইপার (Bangla Voice Typer)")
        app_title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 4px 0;")
        card_layout.addWidget(app_title)

        app_desc = QLabel(
            "উইন্ডোজের যেকোনো টেক্সট ফিল্ডে সরাসরি স্মার্ট বাংলা ভয়েস টাইপিং করার জন্য তৈরি ওপেন-সোর্স ডেস্কটপ টুল।"
        )
        app_desc.setStyleSheet("color: #8e8e93; font-size: 13px; line-height: 1.4;")
        app_desc.setWordWrap(True)
        card_layout.addWidget(app_desc)
        card_layout.addWidget(self._create_separator())

        # Specs Rows with ValueLabel
        val_ver = QLabel(get_app_version())
        val_ver.setObjectName("ValueLabel")
        row_ver = self._create_setting_row("সংস্করণ", "অ্যাপ্লিকেশন বিল্ড ভার্সন", val_ver)
        card_layout.addWidget(row_ver)
        card_layout.addWidget(self._create_separator())

        val_engine = QLabel("Gemini AI & Google Speech")
        val_engine.setObjectName("ValueLabel")
        row_engine = self._create_setting_row("স্পিচ ইঞ্জিন", "ভয়েস রেকগনিশন প্রযুক্তি", val_engine)
        card_layout.addWidget(row_engine)
        card_layout.addWidget(self._create_separator())

        val_lic = QLabel("MIT License")
        val_lic.setObjectName("ValueLabel")
        row_lic = self._create_setting_row("লাইসেন্স", "মুক্ত ও উন্মুক্ত সফটওয়্যার", val_lic)
        card_layout.addWidget(row_lic)

        layout.addWidget(card)

        # Card 2: Diagnostics & Logs Card
        card_log, card_log_layout = self._create_card("ডায়াগনস্টিক ও এরর লগ")

        btn_open_log = QPushButton("📋 এরর লগ দেখুন")
        btn_open_log.setObjectName("SecondaryButton")
        btn_open_log.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open_log.clicked.connect(open_log_file)
        row_open_log = self._create_setting_row("সফটওয়্যার লগ ফাইল", "যেকোনো এরর বা কার্যবিবরণী সরাসরি দেখতে ফাইলটি খুলুন", btn_open_log)
        card_log_layout.addWidget(row_open_log)
        card_log_layout.addWidget(self._create_separator())

        btn_open_folder = QPushButton("📁 ফোল্ডার খুলুন")
        btn_open_folder.setObjectName("SecondaryButton")
        btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open_folder.clicked.connect(open_log_folder)
        row_open_folder = self._create_setting_row("লগ ফোল্ডার", "লগ ফাইল সংরক্ষিত ফোল্ডারটি ফাইল এক্সপ্লোরারে খুলুন", btn_open_folder)
        card_log_layout.addWidget(row_open_folder)
        card_log_layout.addWidget(self._create_separator())

        log_path_lbl = QLabel(get_log_file_path())
        log_path_lbl.setObjectName("ValueLabel")
        log_path_lbl.setStyleSheet("font-size: 11px; color: #8e8e93;")
        log_path_lbl.setWordWrap(True)
        log_path_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        row_path = self._create_setting_row("লগ ফাইলের পাথ", "বর্তমান সক্রিয় লগ ফাইলের ডিস্ক লোকেশন", log_path_lbl)
        card_log_layout.addWidget(row_path)

        layout.addWidget(card_log)
        layout.addStretch()
        return page

    # -------------------------------------------------------------------------
    # Save & Close Logic
    # -------------------------------------------------------------------------

    def _save_and_close(self):
        new_engine = self.combo_engine.currentData()
        new_gemini_model = self.combo_gemini_model.currentData()
        new_api_key = self.input_api_key.text().strip()
        new_theme = self.combo_theme.currentData()
        raw_hotkey = self.combo_hotkey.currentData() or self.combo_hotkey.currentText()
        new_hotkey = str(raw_hotkey).lower().replace("<", "").replace(">", "").strip()
        new_lang = self.combo_lang.currentData()
        sound_feedback = self.sw_sound.isChecked()
        always_on_top = self.sw_top.isChecked()
        auto_hide = self.sw_autohide.isChecked()
        phrase_limit = self.spin_timeout.value()

        self.config.set("engine", new_engine)
        self.config.set("gemini_model", new_gemini_model)
        self.config.set("gemini_api_key", new_api_key)
        self.config.set("theme", new_theme)
        self.config.set("hotkey", new_hotkey)
        self.config.set("language", new_lang)
        self.config.set("sound_feedback", sound_feedback)
        self.config.set("always_on_top", always_on_top)
        self.config.set("auto_hide_widget", auto_hide)
        self.config.set("phrase_time_limit", phrase_limit)

        if self.on_saved_callback:
            self.on_saved_callback()

        self.accept()
