import time
import threading
import concurrent.futures
import pyaudio
import speech_recognition as sr
from PyQt6.QtCore import QObject, pyqtSignal

from src.core.logger import get_logger
from src.core.audio_feedback import (
    play_start_sound,
    play_processing_sound,
    play_success_sound,
    play_error_sound,
    play_cancel_sound
)
from src.core.clipboard import paste_text

class SpeechEngine(QObject):
    listening_started = pyqtSignal()
    processing_started = pyqtSignal()
    transcription_success = pyqtSignal(str)
    transcription_cancelled = pyqtSignal()
    error_occurred = pyqtSignal(str)
    state_idle = pyqtSignal()

    def __init__(self, config_manager):
        super().__init__()
        self.logger = get_logger("speech_engine")
        self.config = config_manager
        self.recognizer = sr.Recognizer()
        
        self.is_recording = False
        self.is_processing = False
        self._cancel_requested = False
        self._current_session_id = 0
        self._lock = threading.Lock()
        self._apply_settings()

    def _apply_settings(self):
        """Apply dynamic configuration updates to speech recognizer"""
        if self.config:
            self.recognizer.energy_threshold = self.config.get("energy_threshold", 300)
            self.recognizer.pause_threshold = self.config.get("pause_threshold", 0.8)
            self.logger.debug(
                f"SpeechEngine settings applied: energy_threshold={self.recognizer.energy_threshold}, "
                f"pause_threshold={self.recognizer.pause_threshold}"
            )

    def start_recording(self):
        """Starts recording if idle"""
        with self._lock:
            if self.is_processing or self.is_recording:
                self.logger.debug("start_recording called but engine is already recording or processing.")
                return
            self._cancel_requested = False
            self.is_recording = True
            self.is_processing = False
            self._current_session_id += 1
            session_id = self._current_session_id
        self.logger.info(f"Recording initiated (session #{session_id}).")
        threading.Thread(target=self._record_and_transcribe_worker, args=(session_id,), daemon=True).start()

    def stop_recording(self):
        """Stops recording if currently active and proceeds to transcription"""
        with self._lock:
            if self.is_recording:
                self.logger.info("Recording stop requested (proceeding to transcription).")
                self.is_recording = False

    def cancel(self):
        """
        Immediately cancels and interrupts ongoing recording or transcription processing.
        Discards audio and prevents pasting any text.
        """
        with self._lock:
            if not self.is_recording and not self.is_processing:
                self.logger.debug("cancel called but engine is neither recording nor processing.")
                return False
            self.logger.info(f"Voice recognition cancellation requested (session #{self._current_session_id}).")
            self._cancel_requested = True
            self.is_recording = False
            self.is_processing = False
            self._current_session_id += 1

        play_cancel_sound(self.config.get("sound_feedback", True))
        self.transcription_cancelled.emit()
        self.state_idle.emit()
        return True

    def toggle_recording(self):
        """
        Toggles recording:
        - If recording: stops recording and transcribes
        - If processing: cancels transcription immediately
        - If idle: starts recording
        """
        if self.is_recording:
            self.stop_recording()
        elif self.is_processing:
            self.cancel()
        else:
            self.start_recording()

    def trigger_transcription(self):
        """Alias for toggle_recording"""
        self.toggle_recording()

    def _call_gemini_api(self, client, model: str, wav_bytes: bytes, prompt: str) -> str:
        from google.genai import types
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"),
                prompt
            ]
        )
        return (response.text or "").strip()

    def _transcribe_with_gemini(self, audio, api_key: str, model_name: str, session_id: int = None) -> str:
        """Transcribe audio using Google Gemini API with fallback and timeout"""
        from google import genai
        from google.genai import types

        wav_bytes = audio.get_wav_data(convert_rate=16000, convert_width=2)
        # Google Gemini API client timeout (15s for fast fallback and responsive experience)
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=15000)
        )

        prompt = (
            "You are an expert, highly accurate Bengali speech-to-text transcriber. "
            "Listen to the audio carefully and transcribe what was spoken into natural, fluent Bengali. "
            "Rules:\n"
            "1. Add natural punctuation (দাঁড়ি ।, কমা ,, প্রশ্নবোধক চিহ্ন ?) where sentences naturally end.\n"
            "2. If English technical terms or common loanwords (like file, email, computer, send, online, message, call, download) "
            "are spoken, transcribe them contextually in Bengali or English as spoken.\n"
            "3. Filter out filler words like 'umm', 'uhh'.\n"
            "4. Return ONLY the transcribed text. Do NOT add notes, explanations, or quotes."
        )

        candidates = [model_name, "gemini-3.1-flash-lite", "gemini-3.5-flash"]
        seen = set()
        models_to_try = [m for m in candidates if m and not (m in seen or seen.add(m))]

        last_err = None
        for m in models_to_try:
            if self._cancel_requested or (session_id is not None and self._current_session_id != session_id):
                self.logger.info("Gemini transcription cancelled before API dispatch.")
                return ""
            try:
                self.logger.debug(f"Attempting Gemini transcription using model '{m}'...")
                text = self._call_gemini_api(client, m, wav_bytes, prompt)
                if text:
                    self.logger.info(f"Gemini transcription successful with model '{m}'")
                    return text
            except Exception as e:
                if self._cancel_requested or (session_id is not None and self._current_session_id != session_id):
                    self.logger.info("Gemini transcription cancelled during call.")
                    return ""
                last_err = e
                err_msg = str(e) or type(e).__name__
                self.logger.warning(f"Gemini model '{m}' failed: {err_msg}", exc_info=True)
                continue

        if last_err and not (self._cancel_requested or (session_id is not None and self._current_session_id != session_id)):
            self.logger.error("All candidate Gemini models failed.", exc_info=True)
            raise last_err
        return ""

    def _record_and_transcribe_worker(self, session_id: int):
        sound_enabled = self.config.get("sound_feedback", True)
        language = self.config.get("language", "bn-BD")
        engine_mode = self.config.get("engine", "gemini")
        gemini_key = self.config.get("gemini_api_key", "").strip()
        gemini_model = self.config.get("gemini_model", "gemini-3.1-flash-lite")

        p = pyaudio.PyAudio()
        stream = None
        frames = []

        try:
            # 1. Start Audio Stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )

            self.logger.info(f"Microphone stream opened for session #{session_id}. Recording started...")
            self.listening_started.emit()
            play_start_sound(sound_enabled)

            # Record continuously until user explicitly stops, cancels, or 3-minute safety limit
            max_chunks = int(16000 / 1024 * 180)
            chunk_count = 0

            while self.is_recording and chunk_count < max_chunks:
                if self._cancel_requested or self._current_session_id != session_id:
                    self.logger.info(f"Session #{session_id}: Recording loop detected cancellation.")
                    break
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
                chunk_count += 1

        except Exception as audio_err:
            if not self._cancel_requested and self._current_session_id == session_id:
                self.logger.error(f"Microphone recording error: {audio_err}", exc_info=True)
                play_error_sound(sound_enabled)
                self.error_occurred.emit(f"মাইক সমস্যা: {audio_err}")
                self.state_idle.emit()
            return
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    pass
            p.terminate()

        # Check if cancelled during recording
        with self._lock:
            if self._cancel_requested or self._current_session_id != session_id:
                self.logger.info(f"Session #{session_id} discarded post-recording due to cancellation.")
                return
            self.is_recording = False
            self.is_processing = True

        raw_bytes = b"".join(frames)
        # If less than 0.35s was recorded, cancel
        if len(raw_bytes) < (16000 * 2 * 0.35):
            self.logger.info(f"Recorded audio too brief ({len(raw_bytes)} bytes). Discarding.")
            with self._lock:
                if self._current_session_id == session_id:
                    self.is_processing = False
            self.state_idle.emit()
            return

        try:
            self.logger.info(
                f"Audio recording completed ({len(raw_bytes)} bytes, ~{len(raw_bytes)/32000:.1f}s). Processing session #{session_id} with engine='{engine_mode}', lang='{language}'..."
            )
            self.processing_started.emit()
            play_processing_sound(sound_enabled)

            audio_data = sr.AudioData(raw_bytes, 16000, 2)
            text = ""

            # Try Gemini AI Engine if configured
            if engine_mode == "gemini" and gemini_key:
                try:
                    text = self._transcribe_with_gemini(audio_data, gemini_key, gemini_model, session_id=session_id)
                except Exception as gemini_err:
                    if self._cancel_requested or self._current_session_id != session_id:
                        self.logger.info(f"Session #{session_id} cancelled during Gemini transcription.")
                        return
                    err_txt = str(gemini_err) or type(gemini_err).__name__
                    self.logger.warning(f"Gemini fallback triggered due to: {err_txt}. Falling back to Google STT...", exc_info=True)
                    text = self.recognizer.recognize_google(audio_data, language=language)
            else:
                if engine_mode == "gemini" and not gemini_key:
                    self.logger.info("No Gemini API key configured. Using Google STT engine.")
                text = self.recognizer.recognize_google(audio_data, language=language)

            # Check if cancelled while network request was in progress
            with self._lock:
                if self._cancel_requested or self._current_session_id != session_id:
                    self.logger.info(f"Session #{session_id} discarded output because session was cancelled.")
                    return

            text = (text or "").strip()

            if text:
                self.logger.info(f"Transcription succeeded for session #{session_id}: '{text}'")
                paste_text(text)
                play_success_sound(sound_enabled)
                self.transcription_success.emit(text)
            else:
                self.logger.warning("Transcription resulted in empty text.")
                self.error_occurred.emit("কোনো কথা শোনা যায়নি")

        except sr.UnknownValueError:
            if not self._cancel_requested and self._current_session_id == session_id:
                self.logger.warning("Speech recognition could not understand audio (sr.UnknownValueError).")
                play_error_sound(sound_enabled)
                self.error_occurred.emit("কথাটি বোঝা যায়নি")
        except sr.RequestError as e:
            if not self._cancel_requested and self._current_session_id == session_id:
                self.logger.error(f"Speech recognition network/request error: {e}", exc_info=True)
                play_error_sound(sound_enabled)
                self.error_occurred.emit(f"ইন্টারনেট ত্রুটি: {e}")
        except Exception as e:
            if not self._cancel_requested and self._current_session_id == session_id:
                self.logger.error(f"Unexpected error in speech engine: {e}", exc_info=True)
                play_error_sound(sound_enabled)
                self.error_occurred.emit(f"ত্রুটি: {e}")
        finally:
            with self._lock:
                if self._current_session_id == session_id:
                    self.is_recording = False
                    self.is_processing = False
                    self.state_idle.emit()
