import winsound
import threading

def _beep_async(freq, duration):
    try:
        winsound.Beep(freq, duration)
    except Exception:
        pass

def play_start_sound(enabled=True):
    """Play high pitched beep when listening starts"""
    if enabled:
        threading.Thread(target=_beep_async, args=(1200, 160), daemon=True).start()

def play_processing_sound(enabled=True):
    """Play mid pitched beep when processing audio"""
    if enabled:
        threading.Thread(target=_beep_async, args=(800, 120), daemon=True).start()

def play_success_sound(enabled=True):
    """Play pleasant success double beep"""
    if enabled:
        def _double():
            _beep_async(1000, 80)
            _beep_async(1400, 100)
        threading.Thread(target=_double, daemon=True).start()

def play_error_sound(enabled=True):
    """Play low error tone"""
    if enabled:
        threading.Thread(target=_beep_async, args=(400, 250), daemon=True).start()
