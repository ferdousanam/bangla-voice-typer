import os
import sys
import winreg

"""
Modern Dynamic Theming (Dark, Light, System Default) for Bangla Voice Typer
Optimized for high contrast, Segoe UI (English) & Nirmala UI/Kalpurush (Bengali)
"""

FONT_FAMILY = "'Segoe UI', 'Nirmala UI', 'Kalpurush', 'Vrinda', sans-serif"
ENGLISH_FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif"

def get_assets_dir() -> str:
    """Resolve assets directory whether running from source or frozen in PyInstaller"""
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        for rel in [os.path.join("src", "ui", "assets"), "assets"]:
            candidate = os.path.join(base_dir, rel)
            if os.path.exists(candidate):
                return candidate
        return base_dir
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

ASSETS_DIR = get_assets_dir()
CHECK_ICON = os.path.join(ASSETS_DIR, "check.svg").replace("\\", "/")
CHEVRON_DOWN_LIGHT = os.path.join(ASSETS_DIR, "chevron-down.svg").replace("\\", "/")
CHEVRON_DOWN_DARK = os.path.join(ASSETS_DIR, "chevron-down-dark.svg").replace("\\", "/")

def is_windows_dark_mode() -> bool:
    """Checks whether Windows Apps theme is set to Dark Mode via Registry"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return val == 0
    except Exception:
        return True

def resolve_theme(preference: str) -> str:
    """Resolves 'system', 'dark', or 'light' into either 'dark' or 'light'"""
    pref = (preference or "system").lower()
    if pref == "system":
        return "dark" if is_windows_dark_mode() else "light"
    return "light" if pref == "light" else "dark"

def get_floating_bar_style(theme: str = "dark") -> str:
    if theme == "light":
        return f"""
        QWidget#FloatingContainer {{
            background-color: rgba(255, 255, 255, 0.98);
            border: 1px solid #cbd5e1;
            border-radius: 22px;
        }}

        QLabel#StatusLabel {{
            color: #0f172a;
            font-size: 14px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
            padding: 2px 6px 3px 4px;
            min-height: 26px;
        }}

        QLabel#HotkeyBadge {{
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            font-family: {ENGLISH_FONT};
            padding: 3px 8px;
            margin-right: 4px;
        }}

        QPushButton.ActionButton {{
            background-color: transparent;
            border: none;
            border-radius: 14px;
            color: #64748b;
            font-size: 14px;
            font-family: {FONT_FAMILY};
            min-width: 28px;
            min-height: 28px;
            padding: 2px;
        }}

        QPushButton.ActionButton:hover {{
            background-color: #f1f5f9;
            color: #0f172a;
        }}

        QPushButton.ActionButton[state="cancel"] {{
            color: #dc2626;
            font-weight: bold;
        }}

        QPushButton.ActionButton[state="cancel"]:hover {{
            background-color: #fee2e2;
            color: #b91c1c;
        }}

        QPushButton#MicButton {{
            background-color: #2563eb;
            border: none;
            border-radius: 16px;
            color: #ffffff;
            font-size: 15px;
            min-width: 32px;
            min-height: 32px;
            max-width: 32px;
            max-height: 32px;
        }}

        QPushButton#MicButton:hover {{
            background-color: #1d4ed8;
        }}

        QPushButton#MicButton[state="recording"] {{
            background-color: #dc2626;
        }}

        QPushButton#MicButton[state="processing"] {{
            background-color: #d97706;
        }}

        QPushButton#MicButton[state="success"] {{
            background-color: #16a34a;
        }}

        QPushButton#MicButton[state="cancelled"] {{
            background-color: #ef4444;
        }}

        QToolTip {{
            background-color: #ffffff;
            color: #0f172a;
            border: 1px solid #cbd5e1;
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 13px;
            font-family: {FONT_FAMILY};
        }}
        """
    else:
        return f"""
        QWidget#FloatingContainer {{
            background-color: #13151b;
            border: 1px solid #2d3342;
            border-radius: 22px;
        }}

        QLabel#StatusLabel {{
            color: #f8fafc;
            font-size: 14px;
            font-weight: 500;
            font-family: {FONT_FAMILY};
            padding: 2px 6px 3px 4px;
            min-height: 26px;
        }}

        QLabel#HotkeyBadge {{
            background-color: #202430;
            color: #cbd5e1;
            border: 1px solid #363e52;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            font-family: {ENGLISH_FONT};
            padding: 3px 8px;
            margin-right: 4px;
        }}

        QPushButton.ActionButton {{
            background-color: transparent;
            border: none;
            border-radius: 14px;
            color: #94a3b8;
            font-size: 14px;
            font-family: {FONT_FAMILY};
            min-width: 28px;
            min-height: 28px;
            padding: 2px;
        }}

        QPushButton.ActionButton:hover {{
            background-color: #262c3a;
            color: #ffffff;
        }}

        QPushButton.ActionButton[state="cancel"] {{
            color: #ef4444;
            font-weight: bold;
        }}

        QPushButton.ActionButton[state="cancel"]:hover {{
            background-color: #3f1a1a;
            color: #f87171;
        }}

        QPushButton#MicButton {{
            background-color: #2563eb;
            border: none;
            border-radius: 16px;
            color: #ffffff;
            font-size: 15px;
            min-width: 32px;
            min-height: 32px;
            max-width: 32px;
            max-height: 32px;
        }}

        QPushButton#MicButton:hover {{
            background-color: #1d4ed8;
        }}

        QPushButton#MicButton[state="recording"] {{
            background-color: #dc2626;
        }}

        QPushButton#MicButton[state="processing"] {{
            background-color: #d97706;
        }}

        QPushButton#MicButton[state="success"] {{
            background-color: #16a34a;
        }}

        QPushButton#MicButton[state="cancelled"] {{
            background-color: #ef4444;
        }}

        QToolTip {{
            background-color: #1c202a;
            color: #f8fafc;
            border: 1px solid #363e52;
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 13px;
            font-family: {FONT_FAMILY};
        }}
        """

def get_settings_dialog_style(theme: str = "dark") -> str:
    chevron_icon = CHEVRON_DOWN_DARK if theme == "light" else CHEVRON_DOWN_LIGHT

    if theme == "light":
        return f"""
        QDialog {{
            background-color: #f8f9fa;
            color: #0f172a;
            font-family: {FONT_FAMILY};
        }}

        QDialog QLabel {{
            color: #0f172a;
            font-family: {FONT_FAMILY};
        }}

        /* Left Sidebar (Light Mode) */
        QWidget#SidebarContainer {{
            background-color: #f1f3f5;
            border-right: 1px solid #e2e8f0;
        }}

        QLabel#SidebarTitle {{
            color: #0f172a;
            font-size: 15px;
            font-weight: 700;
            font-family: {FONT_FAMILY};
        }}

        QLabel#SidebarSubtitle {{
            color: #64748b;
            font-size: 11px;
            font-family: {ENGLISH_FONT};
        }}

        QLabel#NavGroupHeader {{
            color: #64748b;
            font-size: 11px;
            font-weight: 700;
            font-family: {FONT_FAMILY};
            letter-spacing: 0.5px;
            padding: 12px 12px 4px 12px;
        }}

        QListWidget#SidebarList {{
            background-color: transparent;
            border: none;
            outline: none;
            padding: 0px 4px;
        }}

        QListWidget#SidebarList::item {{
            height: 38px;
            padding-left: 10px;
            border-radius: 6px;
            margin: 2px 4px;
            color: #475569;
            font-size: 13px;
            font-weight: 500;
            font-family: {FONT_FAMILY};
        }}

        QListWidget#SidebarList::item:hover {{
            background-color: #e2e8f0;
            color: #0f172a;
        }}

        QListWidget#SidebarList::item:selected {{
            background-color: #e2e8f0;
            color: #0f172a;
            font-weight: 600;
        }}

        /* Content Area & Scroll */
        QWidget#ContentContainer {{
            background-color: #f8f9fa;
        }}

        QScrollArea#SettingsScrollArea {{
            background-color: transparent;
            border: none;
        }}

        QScrollArea#SettingsScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}

        QWidget#ScrollContent {{
            background-color: transparent;
        }}

        /* Completely invisible scrollbar */
        QScrollBar:vertical, QScrollBar:horizontal {{
            background: transparent;
            width: 0px;
            height: 0px;
            margin: 0px;
            border: none;
        }}
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
            background: transparent;
            width: 0px;
            height: 0px;
        }}
        QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{
            background: transparent;
            width: 0px;
            height: 0px;
        }}

        /* Headers */
        QLabel#PageTitle {{
            color: #0f172a;
            font-size: 18px;
            font-weight: 700;
            font-family: {FONT_FAMILY};
            padding-bottom: 2px;
        }}

        QLabel#PageSubtitle {{
            color: #64748b;
            font-size: 12px;
            font-family: {FONT_FAMILY};
            margin-bottom: 12px;
        }}

        /* Setting Cards */
        QFrame#SettingsCard {{
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 4px 16px;
        }}

        QLabel#CardSectionTitle {{
            color: #0f172a;
            font-size: 13px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
            padding: 4px 0px 2px 0px;
        }}

        QLabel#RowTitle {{
            color: #0f172a;
            font-size: 13px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
        }}

        QLabel#RowSubtitle {{
            color: #64748b;
            font-size: 11px;
            font-family: {FONT_FAMILY};
        }}

        QLabel#ValueLabel {{
            color: #475569;
            font-size: 13px;
            font-weight: 500;
            font-family: {FONT_FAMILY};
        }}

        QFrame#RowSeparator {{
            background-color: #f1f5f9;
            height: 1px;
            border: none;
            max-height: 1px;
        }}

        /* Controls */
        QLineEdit, QComboBox, QSpinBox {{
            background-color: #ffffff;
            color: #0f172a;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 13px;
            font-family: {FONT_FAMILY};
            min-height: 22px;
        }}

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 1px solid #2563eb;
            background-color: #ffffff;
        }}

        QComboBox {{
            padding-right: 28px;
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border-left: 1px solid #e2e8f0;
        }}

        QComboBox::down-arrow {{
            image: url({chevron_icon});
            width: 10px;
            height: 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: #ffffff;
            color: #0f172a;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 4px;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#EyeButton {{
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 13px;
        }}

        QPushButton#EyeButton:hover {{
            background-color: #e2e8f0;
            color: #0f172a;
        }}

        /* Badges & Notice Boxes */
        QLabel#NoticeBox {{
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 8px;
            padding: 10px 14px;
            color: #166534;
            font-size: 12px;
            font-family: {FONT_FAMILY};
            line-height: 1.4;
        }}

        QLabel#InfoBox {{
            background-color: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 10px 14px;
            color: #1e40af;
            font-size: 12px;
            font-family: {FONT_FAMILY};
            line-height: 1.4;
        }}

        QLabel#KbdBadge {{
            background-color: #f1f5f9;
            color: #0f172a;
            border: 1px solid #cbd5e1;
            border-radius: 5px;
            padding: 4px 8px;
            font-family: {ENGLISH_FONT};
            font-size: 12px;
            font-weight: 600;
        }}

        /* Footer */
        QWidget#DialogFooter {{
            background-color: #f1f3f5;
            border-top: 1px solid #e2e8f0;
        }}

        QLabel#FooterHint {{
            color: #64748b;
            font-size: 11px;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#SaveButton {{
            background-color: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 8px 18px;
            font-size: 13px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#SaveButton:hover {{
            background-color: #1d4ed8;
        }}

        QPushButton#CancelButton {{
            background-color: #ffffff;
            color: #475569;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#CancelButton:hover {{
            background-color: #f1f5f9;
            color: #0f172a;
        }}

        QPushButton#SecondaryButton {{
            background-color: #f1f5f9;
            color: #334155;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 500;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#SecondaryButton:hover {{
            background-color: #e2e8f0;
            color: #0f172a;
        }}
        """
    else:
        return f"""
        QDialog {{
            background-color: #101012;
            color: #f4f4f5;
            font-family: {FONT_FAMILY};
        }}

        QDialog QLabel {{
            color: #f4f4f5;
            font-family: {FONT_FAMILY};
        }}

        /* Left Sidebar (Dark Mode) */
        QWidget#SidebarContainer {{
            background-color: #0d0d0f;
            border-right: 1px solid #1f1f23;
        }}

        QLabel#SidebarTitle {{
            color: #ffffff;
            font-size: 15px;
            font-weight: 700;
            font-family: {FONT_FAMILY};
        }}

        QLabel#SidebarSubtitle {{
            color: #71717a;
            font-size: 11px;
            font-family: {ENGLISH_FONT};
        }}

        QLabel#NavGroupHeader {{
            color: #71717a;
            font-size: 11px;
            font-weight: 700;
            font-family: {FONT_FAMILY};
            letter-spacing: 0.5px;
            padding: 12px 12px 4px 12px;
        }}

        QListWidget#SidebarList {{
            background-color: transparent;
            border: none;
            outline: none;
            padding: 0px 4px;
        }}

        QListWidget#SidebarList::item {{
            height: 38px;
            padding-left: 10px;
            border-radius: 6px;
            margin: 2px 4px;
            color: #a1a1aa;
            font-size: 13px;
            font-weight: 500;
            font-family: {FONT_FAMILY};
        }}

        QListWidget#SidebarList::item:hover {{
            background-color: #18181b;
            color: #f4f4f5;
        }}

        QListWidget#SidebarList::item:selected {{
            background-color: #27272a;
            color: #ffffff;
            font-weight: 600;
        }}

        /* Content Area & Scroll */
        QWidget#ContentContainer {{
            background-color: #101012;
        }}

        QScrollArea#SettingsScrollArea {{
            background-color: transparent;
            border: none;
        }}

        QScrollArea#SettingsScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}

        QWidget#ScrollContent {{
            background-color: transparent;
        }}

        /* Completely invisible scrollbar */
        QScrollBar:vertical, QScrollBar:horizontal {{
            background: transparent;
            width: 0px;
            height: 0px;
            margin: 0px;
            border: none;
        }}
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
            background: transparent;
            width: 0px;
            height: 0px;
        }}
        QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{
            background: transparent;
            width: 0px;
            height: 0px;
        }}

        /* Headers */
        QLabel#PageTitle {{
            color: #ffffff;
            font-size: 18px;
            font-weight: 700;
            font-family: {FONT_FAMILY};
            padding-bottom: 2px;
        }}

        QLabel#PageSubtitle {{
            color: #8e8e93;
            font-size: 12px;
            font-family: {FONT_FAMILY};
            margin-bottom: 12px;
        }}

        /* Setting Cards */
        QFrame#SettingsCard {{
            background-color: #161619;
            border: 1px solid #27272b;
            border-radius: 10px;
            padding: 4px 16px;
        }}

        QLabel#CardSectionTitle {{
            color: #f4f4f5;
            font-size: 13px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
            padding: 4px 0px 2px 0px;
        }}

        QLabel#RowTitle {{
            color: #f4f4f5;
            font-size: 13px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
        }}

        QLabel#RowSubtitle {{
            color: #71717a;
            font-size: 11px;
            font-family: {FONT_FAMILY};
        }}

        QLabel#ValueLabel {{
            color: #a1a1aa;
            font-size: 13px;
            font-weight: 500;
            font-family: {FONT_FAMILY};
        }}

        QFrame#RowSeparator {{
            background-color: #232328;
            height: 1px;
            border: none;
            max-height: 1px;
        }}

        /* Controls */
        QLineEdit, QComboBox, QSpinBox {{
            background-color: #0c0c0e;
            color: #f4f4f5;
            border: 1px solid #2c2c32;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 13px;
            font-family: {FONT_FAMILY};
            min-height: 22px;
        }}

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 1px solid #3b82f6;
            background-color: #121215;
        }}

        QComboBox {{
            padding-right: 28px;
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border-left: 1px solid #26262b;
        }}

        QComboBox::down-arrow {{
            image: url({chevron_icon});
            width: 10px;
            height: 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: #161619;
            color: #f4f4f5;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
            border: 1px solid #2e2e34;
            border-radius: 6px;
            padding: 4px;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#EyeButton {{
            background-color: #1c1c1f;
            color: #a1a1aa;
            border: 1px solid #2c2c32;
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 13px;
        }}

        QPushButton#EyeButton:hover {{
            background-color: #27272a;
            color: #ffffff;
        }}

        /* Badges & Notice Boxes */
        QLabel#NoticeBox {{
            background-color: rgba(34, 197, 94, 0.08);
            border: 1px solid rgba(34, 197, 94, 0.22);
            border-radius: 8px;
            padding: 10px 14px;
            color: #4ade80;
            font-size: 12px;
            font-family: {FONT_FAMILY};
            line-height: 1.4;
        }}

        QLabel#InfoBox {{
            background-color: rgba(56, 189, 248, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.22);
            border-radius: 8px;
            padding: 10px 14px;
            color: #38bdf8;
            font-size: 12px;
            font-family: {FONT_FAMILY};
            line-height: 1.4;
        }}

        QLabel#KbdBadge {{
            background-color: #1c1c20;
            color: #38bdf8;
            border: 1px solid #2d2d35;
            border-radius: 5px;
            padding: 4px 8px;
            font-family: {ENGLISH_FONT};
            font-size: 12px;
            font-weight: 600;
        }}

        /* Footer */
        QWidget#DialogFooter {{
            background-color: #0e0e10;
            border-top: 1px solid #1f1f23;
        }}

        QLabel#FooterHint {{
            color: #71717a;
            font-size: 11px;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#SaveButton {{
            background-color: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 8px 18px;
            font-size: 13px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#SaveButton:hover {{
            background-color: #1d4ed8;
        }}

        QPushButton#CancelButton {{
            background-color: #161619;
            color: #a1a1aa;
            border: 1px solid #2c2c32;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#CancelButton:hover {{
            background-color: #222226;
            color: #f4f4f5;
        }}

        QPushButton#SecondaryButton {{
            background-color: #222226;
            color: #e4e4e7;
            border: 1px solid #333338;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 500;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#SecondaryButton:hover {{
            background-color: #2c2c32;
            color: #ffffff;
        }}
        """

def get_tray_menu_style(theme: str = "dark") -> str:
    if theme == "light":
        return f"""
            QMenu {{
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px;
                font-family: {FONT_FAMILY};
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 6px 20px 6px 12px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background-color: #2563eb;
                color: #ffffff;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: #e2e8f0;
                margin: 4px 6px;
            }}
        """
    else:
        return f"""
            QMenu {{
                background-color: #161922;
                color: #f1f5f9;
                border: 1px solid #2d3340;
                border-radius: 8px;
                padding: 6px;
                font-family: {FONT_FAMILY};
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 6px 20px 6px 12px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background-color: #2563eb;
                color: #ffffff;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: #2d3340;
                margin: 4px 6px;
            }}
        """
