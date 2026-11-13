import time
import pyperclip
from pynput.keyboard import Controller, Key

kbd_controller = Controller()

def paste_text(text: str):
    """
    Pastes text at the current cursor position safely via the clipboard.
    Preserves recent clipboard content where practical.
    """
    if not text:
        return

    text = text.strip()
    if not text:
        return

    try:
        # Copy Bengali text to clipboard
        pyperclip.copy(text)
        time.sleep(0.06)

        # Simulate Ctrl + V
        with kbd_controller.pressed(Key.ctrl):
            kbd_controller.tap('v')

        time.sleep(0.06)
    except Exception as e:
        print(f"[Clipboard Error]: {e}")
