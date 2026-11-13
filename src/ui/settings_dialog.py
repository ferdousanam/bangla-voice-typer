from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QCheckBox, QPushButton,
    QTabWidget, QWidget, QFormLayout, QDoubleSpinBox, QSpinBox
)
from PyQt6.QtCore import Qt
from src.ui.styles import get_settings_dialog_style, resolve_theme

class SettingsDialog(QDialog):
    def __init__(self, config_manager, on_saved_callback=None, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.on_saved_callback = on_saved_callback
        self.setWindowTitle("সেটিংস - বাংলা ভয়েস টাইপার")
        self.setFixedWidth(550)
        self.setModal(False)
        self.apply_theme()
        self._init_ui()

    def apply_theme(self):
        active_theme = resolve_theme(self.config.get("theme", "system"))
        self.setStyleSheet(get_settings_dialog_style(active_theme))

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        # Header Title & Subtitle
        header = QLabel("⚙️ ভয়েস টাইপার সেটিংস")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        sub_header = QLabel("ট্যাবগুলো থেকে আপনার প্রয়োজনীয় সেটিংস কাস্টমাইজ করুন")
        sub_header.setObjectName("HeaderSubtitle")
        layout.addWidget(sub_header)

        # Tabs Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Tab 1: AI Model Settings
        tab_ai = self._create_ai_tab()
        self.tabs.addTab(tab_ai, "✨ এআই ইঞ্জিন")

        # Tab 2: General & Theme Settings
        tab_general = self._create_general_tab()
        self.tabs.addTab(tab_general, "⚙️ সাধারণ ও থিম")

        # Tab 3: Behavior & Audio Settings
        tab_behavior = self._create_behavior_tab()
        self.tabs.addTab(tab_behavior, "🎙️ আচরণ ও অডিও")

        layout.addWidget(self.tabs)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 10, 0, 0)
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("বাতিল")
        self.btn_cancel.setObjectName("CancelButton")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("সংরক্ষণ করুন ✓")
        self.btn_save.setObjectName("SaveButton")
        self.btn_save.clicked.connect(self._save_and_close)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

    def _create_ai_tab(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("TabContent")
        layout = QVBoxLayout(widget)
        layout.setSpacing(14)
        layout.setContentsMargins(8, 12, 8, 12)

        # Engine selector
        top_form = QFormLayout()
        top_form.setSpacing(14)
        top_form.setContentsMargins(0, 0, 0, 0)
        top_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.combo_engine = QComboBox()
        self.combo_engine.addItem("🚀 Gemini Flash (স্মার্ট এআই — অটো বিরামচিহ্নসহ)", "gemini")
        self.combo_engine.addItem("🎙️ Google STT (ফ্রি, বেসিক — কোনো কী লাগবে না)", "google")

        current_engine = self.config.get("engine", "gemini")
        idx_engine = self.combo_engine.findData(current_engine)
        if idx_engine >= 0:
            self.combo_engine.setCurrentIndex(idx_engine)
        top_form.addRow("ইঞ্জিন নির্বাচন:", self.combo_engine)
        layout.addLayout(top_form)

        # 1. Gemini AI Config Container (Visible only when Gemini is selected)
        self.gemini_container = QWidget()
        gemini_form = QFormLayout(self.gemini_container)
        gemini_form.setSpacing(14)
        gemini_form.setContentsMargins(0, 4, 0, 0)
        gemini_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.combo_gemini_model = QComboBox()
        self.combo_gemini_model.addItem("gemini-3.5-flash (সর্বশেষ স্থিতিশীল ও দ্রুত)", "gemini-3.5-flash")
        self.combo_gemini_model.addItem("gemini-3.1-flash-lite (হালকা ও দ্রুত)", "gemini-3.1-flash-lite")
        self.combo_gemini_model.addItem("gemini-3.8-flash", "gemini-3.8-flash")

        current_model = self.config.get("gemini_model", "gemini-3.5-flash")
        idx_model = self.combo_gemini_model.findData(current_model)
        if idx_model >= 0:
            self.combo_gemini_model.setCurrentIndex(idx_model)
        gemini_form.addRow("Gemini মডেল:", self.combo_gemini_model)

        self.input_api_key = QLineEdit()
        self.input_api_key.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.input_api_key.setPlaceholderText("AIzaSy... (aistudio.google.com থেকে ফ্রি কি দিন)")
        self.input_api_key.setText(self.config.get("gemini_api_key", ""))
        gemini_form.addRow("Gemini API Key:", self.input_api_key)

        tip_label = QLabel('<a href="https://aistudio.google.com/apikey" style="color: #38bdf8; text-decoration: none;">🔗 Google AI Studio থেকে ফ্রি API Key সংগ্রহ করুন</a>')
        tip_label.setOpenExternalLinks(True)
        tip_label.setStyleSheet("font-size: 12px; padding-top: 4px;")
        gemini_form.addRow("", tip_label)

        layout.addWidget(self.gemini_container)

        # 2. Google STT Notice Container (Visible only when Google STT is selected)
        self.stt_container = QWidget()
        stt_layout = QVBoxLayout(self.stt_container)
        stt_layout.setContentsMargins(0, 4, 0, 4)

        stt_notice = QLabel(
            "✅ Google STT সিলেক্ট করা আছে।\n\n"
            "এই মোডে কোনো API Key বা এআই মডেল কনফিগারেশনের প্রয়োজন নেই। "
            "ইন্টারনেট কানেকশন থাকলেই সরাসরি কোনো সীমাবদ্ধতা ছাড়াই সাধারণ বাংলা ভয়েস টাইপিং চলবে।"
        )
        stt_notice.setObjectName("InfoHint")
        stt_notice.setWordWrap(True)
        stt_layout.addWidget(stt_notice)

        layout.addWidget(self.stt_container)
        layout.addStretch()

        # Connect dropdown change to update visibility
        self.combo_engine.currentIndexChanged.connect(self._update_engine_visibility)
        self._update_engine_visibility()

        return widget

    def _update_engine_visibility(self):
        """Conditionally show/hide AI model configuration based on chosen engine"""
        is_gemini = self.combo_engine.currentData() == "gemini"
        self.gemini_container.setVisible(is_gemini)
        self.stt_container.setVisible(not is_gemini)

    def _create_general_tab(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("TabContent")
        form = QFormLayout(widget)
        form.setSpacing(14)
        form.setContentsMargins(8, 12, 8, 12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # Theme selection
        self.combo_theme = QComboBox()
        self.theme_map = {
            "system": "💻 সিস্টেম ডিফল্ট (System Default)",
            "dark": "🌙 ডার্ক মোড (Dark Mode)",
            "light": "☀️ লাইট মোড (Light Mode)"
        }
        for code, label in self.theme_map.items():
            self.combo_theme.addItem(label, code)
        
        current_theme = self.config.get("theme", "system")
        idx_theme = self.combo_theme.findData(current_theme)
        if idx_theme >= 0:
            self.combo_theme.setCurrentIndex(idx_theme)
        form.addRow("অ্যাপ থিম:", self.combo_theme)

        # Hotkey selection
        self.combo_hotkey = QComboBox()
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

        form.addRow("টগল শর্টকাট:", self.combo_hotkey)

        lbl_hint = QLabel("💡 প্রাথমিক শর্টকাট: Win + Space (২ বার চাপলে শুরু, ১ বার চাপলে বন্ধ)")
        lbl_hint.setObjectName("InfoHint")
        lbl_hint.setWordWrap(True)
        form.addRow(lbl_hint)

        # Language selection
        self.combo_lang = QComboBox()
        self.lang_map = {
            "bn-BD": "বাংলা (বাংলাদেশ) — ডিফল্ট",
            "bn-IN": "বাংলা (ভারত)",
            "en-US": "ইংরেজি (English - US)"
        }
        for code, label in self.lang_map.items():
            self.combo_lang.addItem(label, code)
        
        current_lang = self.config.get("language", "bn-BD")
        index = self.combo_lang.findData(current_lang)
        if index >= 0:
            self.combo_lang.setCurrentIndex(index)
        form.addRow("টাইপিং ভাষা:", self.combo_lang)

        return widget

    def _create_behavior_tab(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("TabContent")
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 12, 8, 12)

        self.chk_sound = QCheckBox("শব্দ ফিডব্যাক (Audio Beep) চালু রাখুন")
        self.chk_sound.setChecked(self.config.get("sound_feedback", True))
        layout.addWidget(self.chk_sound)

        self.chk_top = QCheckBox("ফ্লোটিং বার সবসময় স্ক্রিনের উপরে রাখুন (Always on top)")
        self.chk_top.setChecked(self.config.get("always_on_top", True))
        layout.addWidget(self.chk_top)

        self.chk_autohide = QCheckBox("টাইপিং না থাকলে ফ্লোটিং বার স্বয়ংক্রিয়ভাবে লুকান")
        self.chk_autohide.setChecked(self.config.get("auto_hide_widget", False))
        layout.addWidget(self.chk_autohide)

        note_label = QLabel("💡 <b>স্মার্ট মোড সক্রিয়:</b> কথা থামলেও রেকর্ড অটোমেটিক বন্ধ হবে না। পুরো কথা শেষ হলে তবেই <code>Ctrl + Shift + B</code> বা ⏹️ বাটন চাপুন।")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #38bdf8; font-size: 13px; padding: 6px 0;")
        layout.addWidget(note_label)

        # Tuning sub-form
        tuning_form = QFormLayout()
        tuning_form.setSpacing(10)
        tuning_form.setContentsMargins(0, 8, 0, 0)
        tuning_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(20, 300)
        self.spin_timeout.setValue(int(self.config.get("phrase_time_limit", 180)))
        tuning_form.addRow("সর্বোচ্চ রেকর্ড সময় (সেকেন্ড):", self.spin_timeout)

        layout.addLayout(tuning_form)
        return widget

    def _save_and_close(self):
        new_engine = self.combo_engine.currentData()
        new_gemini_model = self.combo_gemini_model.currentData()
        new_api_key = self.input_api_key.text().strip()
        new_theme = self.combo_theme.currentData()
        raw_hotkey = self.combo_hotkey.currentData() or self.combo_hotkey.currentText()
        new_hotkey = str(raw_hotkey).lower().replace("<", "").replace(">", "").strip()
        new_lang = self.combo_lang.currentData()
        sound_feedback = self.chk_sound.isChecked()
        always_on_top = self.chk_top.isChecked()
        auto_hide = self.chk_autohide.isChecked()
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
