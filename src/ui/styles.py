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
            background-color: #f8fafc;
            color: #0f172a;
            font-family: {FONT_FAMILY};
        }}

        QLabel {{
            color: #1e293b;
            font-size: 14px;
            font-family: {FONT_FAMILY};
            padding-top: 2px;
        }}

        QLabel#HeaderTitle {{
            color: #0f172a;
            font-size: 19px;
            font-weight: bold;
            font-family: {FONT_FAMILY};
            padding-bottom: 2px;
        }}

        QLabel#HeaderSubtitle {{
            color: #64748b;
            font-size: 13px;
            font-family: {FONT_FAMILY};
            margin-bottom: 4px;
        }}

        /* Modern Tabs (Light Mode) */
        QTabWidget::pane {{
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            background-color: #ffffff;
            padding: 16px;
            top: -1px;
        }}

        QTabBar::tab {{
            background-color: #f1f5f9;
            color: #64748b;
            border: 1px solid #e2e8f0;
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 8px 16px;
            margin-right: 4px;
            font-size: 13px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
        }}

        QTabBar::tab:selected {{
            background-color: #ffffff;
            color: #2563eb;
            border-color: #e2e8f0;
            border-bottom: 2px solid #2563eb;
        }}

        QTabBar::tab:hover:!selected {{
            background-color: #e2e8f0;
            color: #0f172a;
        }}

        /* Card Widgets inside tabs */
        QWidget#TabContent {{
            background-color: transparent;
        }}

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: #ffffff;
            color: #0f172a;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            font-family: {FONT_FAMILY};
            min-height: 22px;
        }}

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid #2563eb;
            background-color: #ffffff;
        }}

        QComboBox {{
            padding-right: 30px;
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 28px;
            border-left: 1px solid #e2e8f0;
        }}

        QComboBox::down-arrow {{
            image: url({chevron_icon});
            width: 12px;
            height: 12px;
        }}

        QComboBox QAbstractItemView {{
            background-color: #ffffff;
            color: #0f172a;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 6px;
            font-family: {FONT_FAMILY};
        }}

        QCheckBox {{
            color: #1e293b;
            font-size: 14px;
            font-family: {FONT_FAMILY};
            spacing: 12px;
            padding: 3px 0;
        }}

        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 6px;
            border: 2px solid #94a3b8;
            background-color: #ffffff;
        }}

        QCheckBox::indicator:hover {{
            border-color: #64748b;
        }}

        QCheckBox::indicator:checked {{
            background-color: #2563eb;
            border-color: #2563eb;
            image: url({CHECK_ICON});
        }}

        QPushButton#SaveButton {{
            background-color: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: bold;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#SaveButton:hover {{
            background-color: #1d4ed8;
        }}

        QPushButton#CancelButton {{
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#CancelButton:hover {{
            background-color: #e2e8f0;
            color: #0f172a;
        }}
        """
    else:
        return f"""
        QDialog {{
            background-color: #0d0f13;
            color: #f8fafc;
            font-family: {FONT_FAMILY};
        }}

        QLabel {{
            color: #f1f5f9;
            font-size: 14px;
            font-family: {FONT_FAMILY};
            padding-top: 2px;
        }}

        QLabel#HeaderTitle {{
            color: #ffffff;
            font-size: 19px;
            font-weight: bold;
            font-family: {FONT_FAMILY};
            padding-bottom: 2px;
        }}

        QLabel#HeaderSubtitle {{
            color: #94a3b8;
            font-size: 13px;
            font-family: {FONT_FAMILY};
            margin-bottom: 4px;
        }}

        /* Modern Tabs (Dark Mode) */
        QTabWidget::pane {{
            border: 1px solid #282d3b;
            border-radius: 12px;
            background-color: #151821;
            padding: 16px;
            top: -1px;
        }}

        QTabBar::tab {{
            background-color: #1a1e28;
            color: #94a3b8;
            border: 1px solid #282d3b;
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 8px 16px;
            margin-right: 4px;
            font-size: 13px;
            font-weight: 600;
            font-family: {FONT_FAMILY};
        }}

        QTabBar::tab:selected {{
            background-color: #151821;
            color: #38bdf8;
            border-color: #282d3b;
            border-bottom: 2px solid #38bdf8;
        }}

        QTabBar::tab:hover:!selected {{
            background-color: #222735;
            color: #f1f5f9;
        }}

        /* Card Widgets inside tabs */
        QWidget#TabContent {{
            background-color: transparent;
        }}

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: #0e1016;
            color: #ffffff;
            border: 1px solid #333a4c;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            font-family: {FONT_FAMILY};
            min-height: 22px;
        }}

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid #3b82f6;
            background-color: #131620;
        }}

        QComboBox {{
            padding-right: 30px;
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 28px;
            border-left: 1px solid #282d3b;
        }}

        QComboBox::down-arrow {{
            image: url({chevron_icon});
            width: 12px;
            height: 12px;
        }}

        QComboBox QAbstractItemView {{
            background-color: #151821;
            color: #f8fafc;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
            border: 1px solid #333a4c;
            border-radius: 8px;
            padding: 6px;
            font-family: {FONT_FAMILY};
        }}

        QCheckBox {{
            color: #f1f5f9;
            font-size: 14px;
            font-family: {FONT_FAMILY};
            spacing: 12px;
            padding: 3px 0;
        }}

        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 6px;
            border: 2px solid #64748b;
            background-color: #0e1016;
        }}

        QCheckBox::indicator:hover {{
            border-color: #94a3b8;
            background-color: #131620;
        }}

        QCheckBox::indicator:checked {{
            background-color: #2563eb;
            border-color: #2563eb;
            image: url({CHECK_ICON});
        }}

        QPushButton#SaveButton {{
            background-color: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: bold;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#SaveButton:hover {{
            background-color: #1d4ed8;
        }}

        QPushButton#CancelButton {{
            background-color: #1e222e;
            color: #cbd5e1;
            border: 1px solid #333a4c;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-family: {FONT_FAMILY};
        }}

        QPushButton#CancelButton:hover {{
            background-color: #282d3d;
            color: #ffffff;
            border-color: #475569;
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
