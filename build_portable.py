"""
Bangla Voice Typer - Portable Release Builder
Generates a standalone, zero-dependency portable distribution for Windows.
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

# Force UTF-8 on Windows consoles to prevent cp1252 UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
RELEASE_DIR = DIST_DIR / "BanglaVoiceTyper"
ASSETS_DIR = ROOT_DIR / "src" / "ui" / "assets"
ICON_PATH = ASSETS_DIR / "app_icon.ico"


def get_version() -> str:
    """Resolve release version from CLI args, GitHub ref, environment or default"""
    for i, arg in enumerate(sys.argv):
        if arg in ("--version", "-v") and i + 1 < len(sys.argv):
            return sys.argv[i + 1].lstrip("v")
    ref = os.environ.get("GITHUB_REF_NAME", "").strip()
    if ref:
        return ref.lstrip("v")
    if os.environ.get("RELEASE_VERSION"):
        return os.environ.get("RELEASE_VERSION").strip().lstrip("v")
    try:
        from src import __version__
        return __version__.lstrip("v")
    except Exception:
        return "dev"


VERSION = get_version()
ZIP_NAME = f"BanglaVoiceTyper-Portable-v{VERSION}.zip"


def ensure_icon():
    """Ensure multi-resolution app_icon.ico exists"""
    if ICON_PATH.exists() and ICON_PATH.stat().st_size > 1000:
        return

    print("[INFO] Generating application icon...")
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
        from PyQt6.QtCore import Qt

        app = QApplication.instance() or QApplication(sys.argv)
        sizes = [16, 32, 48, 64, 128, 256]
        icon = QIcon()

        for s in sizes:
            pix = QPixmap(s, s)
            pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Rounded rectangle
            p.setBrush(QColor("#2563eb"))
            p.setPen(Qt.PenStyle.NoPen)
            radius = int(s * 0.22)
            margin = max(1, int(s * 0.05))
            p.drawRoundedRect(margin, margin, s - 2 * margin, s - 2 * margin, radius, radius)

            # Bangla 'ব' letter
            p.setPen(QColor("#ffffff"))
            font_size = int(s * 0.5)
            font = QFont("Kalpurush", font_size, QFont.Weight.Bold)
            font.setStyleHint(QFont.StyleHint.SansSerif)
            p.setFont(font)
            p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "ব")
            p.end()
            icon.addPixmap(pix)

        pix.save(str(ICON_PATH), "ICO")
        print(f"[OK] Icon created: {ICON_PATH}")
    except Exception as e:
        print(f"[WARN] Could not generate icon ({e}). Continuing without custom icon.")


def clean_previous_builds():
    """Clean previous build artifacts"""
    print("[CLEAN] Cleaning previous build artifacts...")
    for target in [BUILD_DIR, RELEASE_DIR, DIST_DIR / ZIP_NAME]:
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        elif target.is_file():
            try:
                target.unlink()
            except Exception:
                pass


def run_pyinstaller():
    """Runs PyInstaller with all required bundles and hooks"""
    print("[BUILD] Packaging standalone binary with PyInstaller...")

    pyinstaller_bin = sys.executable.replace("python.exe", "pyinstaller.exe")
    if not os.path.exists(pyinstaller_bin):
        pyinstaller_bin = "pyinstaller"

    cmd = [
        pyinstaller_bin,
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--name", "BanglaVoiceTyper",
        "--add-data", f"{ASSETS_DIR};src/ui/assets",
        "--collect-all", "google.genai",
        "--collect-all", "speech_recognition",
        "--hidden-import", "pynput.keyboard._win32",
        "--hidden-import", "pynput.mouse._win32",
        "--hidden-import", "pyaudio",
        "main.py"
    ]

    if ICON_PATH.exists():
        cmd.extend(["--icon", str(ICON_PATH)])

    print(f"Running command: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if result.returncode != 0:
        print("\n[ERROR] PyInstaller build failed!")
        sys.exit(result.returncode)


def add_release_files():
    """Adds default configuration and portable guide to release directory"""
    print("[CONFIG] Adding release metadata and default configuration...")

    # Default clean config.json
    default_config = (
        '{\n'
        '    "engine": "gemini",\n'
        '    "gemini_api_key": "",\n'
        '    "gemini_model": "gemini-3.1-flash-lite",\n'
        '    "theme": "system",\n'
        '    "hotkey": "ctrl+shift+b",\n'
        '    "language": "bn-BD",\n'
        '    "sound_feedback": true,\n'
        '    "always_on_top": true,\n'
        '    "auto_hide_widget": false,\n'
        '    "energy_threshold": 300,\n'
        '    "pause_threshold": 0.8,\n'
        '    "timeout": 6,\n'
        '    "phrase_time_limit": 18\n'
        '}\n'
    )
    config_dest = RELEASE_DIR / "config.json"
    if not config_dest.exists():
        config_dest.write_text(default_config, encoding="utf-8")

    # Release version file
    version_dest = RELEASE_DIR / "version.txt"
    version_dest.write_text(f"v{VERSION}", encoding="utf-8")

    # Portable instructions (Bangla + English)
    readme_content = (
        "==========================================================\n"
        "      বাংলা ভয়েস টাইপার (Bangla Voice Typer) - Portable\n"
        f"                    Version {VERSION}\n"
        "==========================================================\n\n"
        "এই সফটওয়্যারটি ১০০% পোর্টেবল (Portable)। এটি ব্যবহারের জন্য আপনার\n"
        "কম্পিউটারে Python বা কোনো অতিরিক্ত সফটওয়্যার ইনস্টল করার দরকার নেই।\n"
        "যেকোনো Windows (10/11 64-bit) কম্পিউটারে পেনড্রাইভ বা যেকোনো ফোল্ডার\n"
        "থেকে সরাসরি চালানো যাবে।\n\n"
        "----------------------------------------------------------\n"
        "১. কিভাবে চালু করবেন:\n"
        "----------------------------------------------------------\n"
        "  - ফোল্ডারের ভেতর 'BanglaVoiceTyper.exe' ফাইলে ডাবল-ক্লিক করুন।\n"
        "  - স্ক্রিনের উপরে ফ্লোটিং বার এবং উইন্ডোজ টাস্কবারের নিচে ডানপাশে\n"
        "    'ব' আইকন দেখতে পাবেন।\n\n"
        "----------------------------------------------------------\n"
        "২. Gemini API Key সেটআপ (একবারই করতে হবে):\n"
        "----------------------------------------------------------\n"
        "  - ফ্লোটিং বারে গিয়ার (Settings) আইকনে ক্লিক করুন, অথবা টাস্কবারের\n"
        "    'ব' আইকনে রাইট-ক্লিক করে 'সেটিংস' সিলেক্ট করুন।\n"
        "  - আপনার Gemini API Key টি পেস্ট করে 'সেভ করুন' চাপুন।\n"
        "  - আপনার সেটিংস স্বয়ংক্রিয়ভাবে এই ফোল্ডারের config.json এ সেভ থাকবে।\n\n"
        "----------------------------------------------------------\n"
        "৩. শর্টকাট কী (Hotkeys):\n"
        "----------------------------------------------------------\n"
        "  - Win + Double Space : ভয়েস রেকর্ডিং শুরু করুন।\n"
        "  - Win + Single Space : কথা বলা শেষে রেকর্ডিং বন্ধ করুন।\n"
        "                         (স্বয়ংক্রিয়ভাবে টেক্সট টাইপ হয়ে যাবে)\n"
        "  - Ctrl + Shift + B   : অল্টারনেটিভ টগল শর্টকাট।\n\n"
        "----------------------------------------------------------\n"
        "English Instructions:\n"
        "----------------------------------------------------------\n"
        "  1. Double click 'BanglaVoiceTyper.exe' to launch.\n"
        "  2. Open Settings (gear icon) and paste your Gemini API Key.\n"
        "  3. Use 'Win + Double Space' to record, 'Win + Single Space' to stop.\n"
        "  4. 100% Portable - No installation required. Carry anywhere!\n\n"
        "==========================================================\n"
    )
    (RELEASE_DIR / "README_PORTABLE.txt").write_text(readme_content, encoding="utf-8")
    print("[OK] Release files added.")


def create_portable_zip():
    """Zips the portable folder for direct distribution"""
    print("[ZIP] Creating portable distribution zip archive...")
    zip_path = DIST_DIR / ZIP_NAME

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
        for file in RELEASE_DIR.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(DIST_DIR)
                zip_file.write(file, arcname)

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Portable release created successfully!")
    print(f"Folder : {RELEASE_DIR}")
    print(f"Zip    : {zip_path} ({size_mb:.1f} MB)")


def main():
    print("=" * 60)
    print("   Bangla Voice Typer - Portable Build System")
    print("=" * 60)
    ensure_icon()
    clean_previous_builds()
    run_pyinstaller()
    add_release_files()
    create_portable_zip()
    print("\n[DONE] All done! The portable package is ready to be used on any PC.")


if __name__ == "__main__":
    main()
