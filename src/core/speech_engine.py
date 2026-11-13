import time
import threading
import concurrent.futures
import pyaudio
import speech_recognition as sr
from PyQt6.QtCore import QObject, pyqtSignal

from src.core.audio_feedback import (
    play_start_sound,
    play_processing_sound,
    play_success_sound,
    play_error_sound
)
from src.core.clipboard import paste_text

class SpeechEngine(QObject):
    listening_started = pyqtSignal()
    processing_started = pyqtSignal()
    transcription_success = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    state_idle = pyqtSignal()

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.recognizer = sr.Recognizer()
        
        self.is_recording = False
        self.is_processing = False
        self._lock = threading.Lock()

    def start_recording(self):
        """Starts recording if idle"""
        with self._lock:
            if self.is_processing or self.is_recording:
                return
            self.is_recording = True
        threading.Thread(target=self._record_and_transcribe_worker, daemon=True).start()

    def stop_recording(self):
        """Stops recording if currently active"""
        with self._lock:
            if self.is_recording:
                self.is_recording = False

    def toggle_recording(self):
        """
        Toggles recording:
        - If idle: starts recording
        - If recording: stops recording and transcribes
        """
        if self.is_recording:
            self.stop_recording()
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

    def _transcribe_with_gemini(self, audio, api_key: str, model_name: str) -> str:
        """Transcribe audio using Google Gemini API with fallback and timeout"""
        from google import genai

        wav_bytes = audio.get_wav_data(convert_rate=16000, convert_width=2)
        client = genai.Client(api_key=api_key)

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

        candidates = [model_name, "gemini-3.5-flash", "gemini-3.1-flash-lite"]
        seen = set()
        models_to_try = [m for m in candidates if m and not (m in seen or seen.add(m))]

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            last_err = None
            for m in models_to_try:
                try:
                    future = executor.submit(self._call_gemini_api, client, m, wav_bytes, prompt)
                    text = future.result(timeout=8.5)
                    if text:
                        return text
                except Exception as e:
                    last_err = e
                    print(f"[Gemini {m} failed]: {e}")
                    continue

            if last_err:
                raise last_err
            return ""

    def _record_and_transcribe_worker(self):
        sound_enabled = self.config.get("sound_feedback", True)
        language = self.config.get("language", "bn-BD")
        engine_mode = self.config.get("engine", "gemini")
        gemini_key = self.config.get("gemini_api_key", "").strip()
        gemini_model = self.config.get("gemini_model", "gemini-3.5-flash")

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

            self.listening_started.emit()
            play_start_sound(sound_enabled)

            # Record continuously until user explicitly stops (or 3-minute safety limit)
            max_chunks = int(16000 / 1024 * 180)
            chunk_count = 0

            while self.is_recording and chunk_count < max_chunks:
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
                chunk_count += 1

        except Exception as audio_err:
            print(f"[Mic Error]: {audio_err}")
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

        # 2. Transition to Processing
        with self._lock:
            self.is_recording = False
            self.is_processing = True

        raw_bytes = b"".join(frames)
        # If less than 0.35s was recorded, cancel
        if len(raw_bytes) < (16000 * 2 * 0.35):
            self.state_idle.emit()
            with self._lock:
                self.is_processing = False
            return

        try:
            self.processing_started.emit()
            play_processing_sound(sound_enabled)

            audio_data = sr.AudioData(raw_bytes, 16000, 2)
            text = ""

            # Try Gemini AI Engine if configured
            if engine_mode == "gemini" and gemini_key:
                try:
                    text = self._transcribe_with_gemini(audio_data, gemini_key, gemini_model)
                except Exception as gemini_err:
                    print(f"[Gemini Fallback]: {gemini_err}. Falling back to Google STT...")
                    text = self.recognizer.recognize_google(audio_data, language=language)
            else:
                text = self.recognizer.recognize_google(audio_data, language=language)

            text = (text or "").strip()

            if text:
                paste_text(text)
                play_success_sound(sound_enabled)
                self.transcription_success.emit(text)
            else:
                self.error_occurred.emit("কোনো কথা শোনা যায়নি")

        except sr.UnknownValueError:
            play_error_sound(sound_enabled)
            self.error_occurred.emit("কথাটি বোঝা যায়নি")
        except sr.RequestError as e:
            play_error_sound(sound_enabled)
            self.error_occurred.emit(f"ইন্টারনেট ত্রুটি: {e}")
        except Exception as e:
            play_error_sound(sound_enabled)
            self.error_occurred.emit(f"ত্রুটি: {e}")
        finally:
            with self._lock:
                self.is_recording = False
                self.is_processing = False
            self.state_idle.emit()
