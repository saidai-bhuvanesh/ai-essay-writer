"""
STUDX JARVIS - Voice Processor
Speech-to-Text and Text-to-Speech processing
"""

import os
import io
import wave
import logging
from typing import Optional, Callable
from pathlib import Path

logger = logging.getLogger('JARVIS.Voice')

class VoiceProcessor:
    """
    JARVIS Voice Processor
    Handles speech recognition and synthesis
    """
    
    def __init__(self):
        self.stt_engine = os.getenv('STT_ENGINE', 'whisper')
        self.tts_engine = os.getenv('TTS_ENGINE', 'pyttsx3')
        self.wake_word = os.getenv('WAKE_WORD', 'jarvis')
        self.sample_rate = int(os.getenv('SAMPLE_RATE', '16000'))
        self.language = os.getenv('LANGUAGE', 'en')
        
        self.stt_model = None
        self.tts_engine_instance = None
        self.is_listening = False
        
        self._init_stt()
        self._init_tts()
        
        logger.info(f"Voice processor initialized: STT={self.stt_engine}, TTS={self.tts_engine}")
    
    def _init_stt(self):
        """Initialize Speech-to-Text engine"""
        try:
            if self.stt_engine == 'whisper':
                import whisper
                self.stt_model = whisper.load_model("base")
                logger.info("Whisper STT model loaded")
            elif self.stt_engine == 'faster-whisper':
                from faster_whisper import WhisperModel
                self.stt_model = WhisperModel("base", device="cpu", compute_type="int8")
                logger.info("Faster-Whisper STT model loaded")
            else:
                logger.warning(f"Unknown STT engine: {self.stt_engine}")
        except ImportError as e:
            logger.error(f"Failed to import STT library: {e}")
            self.stt_model = None
        except Exception as e:
            logger.error(f"Failed to initialize STT: {e}")
            self.stt_model = None
    
    def _init_tts(self):
        """Initialize Text-to-Speech engine"""
        try:
            if self.tts_engine == 'pyttsx3':
                import pyttsx3
                self.tts_engine_instance = pyttsx3.init()
                
                # Configure voice
                voices = self.tts_engine_instance.getProperty('voices')
                if voices:
                    self.tts_engine_instance.setProperty('voice', voices[0].id)
                self.tts_engine_instance.setProperty('rate', 150)
                self.tts_engine_instance.setProperty('volume', 0.9)
                
                logger.info("pyttsx3 TTS engine initialized")
            else:
                logger.warning(f"Unknown TTS engine: {self.tts_engine}")
        except ImportError as e:
            logger.error(f"Failed to import TTS library: {e}")
            self.tts_engine_instance = None
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine_instance = None
    
    def transcribe(self, audio_data: bytes) -> str:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Raw audio bytes (16-bit PCM)
        
        Returns:
            Transcribed text
        """
        if not self.stt_model:
            logger.error("STT model not available")
            return ""
        
        try:
            # Save audio to temporary file
            temp_path = Path('/tmp') / 'jarvis_audio.wav'
            
            with wave.open(str(temp_path), 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.writeframes(audio_data)
            
            # Transcribe based on engine
            if self.stt_engine == 'whisper':
                result = self.stt_model.transcribe(str(temp_path), language=self.language)
                text = result['text'].strip()
            elif self.stt_engine == 'faster-whisper':
                segments, _ = self.stt_model.transcribe(str(temp_path), language=self.language)
                text = ' '.join([seg.text for seg in segments]).strip()
            else:
                text = ""
            
            logger.info(f"Transcribed: {text}")
            
            # Cleanup
            temp_path.unlink(missing_ok=True)
            
            return text
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def transcribe_file(self, audio_path: str) -> str:
        """Transcribe audio from file"""
        if not self.stt_model:
            logger.error("STT model not available")
            return ""
        
        try:
            if self.stt_engine == 'whisper':
                result = self.stt_model.transcribe(audio_path, language=self.language)
                return result['text'].strip()
            elif self.stt_engine == 'faster-whisper':
                segments, _ = self.stt_model.transcribe(audio_path, language=self.language)
                return ' '.join([seg.text for seg in segments]).strip()
            return ""
        except Exception as e:
            logger.error(f"File transcription error: {e}")
            return ""
    
    def speak(self, text: str, block: bool = True) -> bool:
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            block: Wait for speech to complete
        
        Returns:
            Success status
        """
        if not self.tts_engine_instance:
            logger.error("TTS engine not available")
            return False
        
        try:
            logger.info(f"Speaking: {text[:50]}...")
            
            if block:
                self.tts_engine_instance.say(text)
                self.tts_engine_instance.runAndWait()
            else:
                # Non-blocking - run in background
                import threading
                def speak_async():
                    self.tts_engine_instance.say(text)
                    self.tts_engine_instance.runAndWait()
                threading.Thread(target=speak_async, daemon=True).start()
            
            return True
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    def speak_with_callback(self, text: str, on_start: Callable = None, on_end: Callable = None):
        """Speak with callback functions"""
        import threading
        
        def speak_task():
            if on_start:
                on_start()
            
            self.speak(text, block=True)
            
            if on_end:
                on_end()
        
        threading.Thread(target=speak_task, daemon=True).start()
    
    def detect_wake_word(self, audio_data: bytes) -> bool:
        """
        Detect wake word in audio
        
        Args:
            audio_data: Raw audio bytes
        
        Returns:
            True if wake word detected
        """
        text = self.transcribe(audio_data).lower()
        
        # Simple wake word detection
        if self.wake_word.lower() in text:
            logger.info("Wake word detected!")
            return True
        
        return False
    
    def set_voice(self, voice_id: str):
        """Set TTS voice"""
        if self.tts_engine_instance:
            self.tts_engine_instance.setProperty('voice', voice_id)
            logger.info(f"Voice set to: {voice_id}")
    
    def get_available_voices(self) -> list:
        """Get available TTS voices"""
        if self.tts_engine_instance:
            return self.tts_engine_instance.getProperty('voices')
        return []
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        if self.tts_engine_instance:
            self.tts_engine_instance.setProperty('rate', rate)
            logger.info(f"Speech rate set to: {rate}")
    
    def set_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)"""
        if self.tts_engine_instance:
            self.tts_engine_instance.setProperty('volume', max(0.0, min(1.0, volume)))
            logger.info(f"Volume set to: {volume}")
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.tts_engine_instance:
            self.tts_engine_instance.stop()
            logger.info("Speech stopped")


class AudioCapture:
    """Audio capture utilities"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.frames = []
    
    def start_recording(self):
        """Start audio recording"""
        try:
            import sounddevice as sd
            
            self.frames = []
            self.is_recording = True
            
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio capture status: {status}")
                if self.is_recording:
                    self.frames.append(indata.copy())
            
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback
            )
            self.stream.start()
            
            logger.info("Audio recording started")
            
        except ImportError:
            logger.error("sounddevice not installed")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
    
    def stop_recording(self) -> bytes:
        """Stop recording and return audio data"""
        self.is_recording = False
        
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        if self.frames:
            import numpy as np
            import wave
            
            audio_data = np.concatenate(self.frames)
            audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            
            logger.info(f"Audio captured: {len(audio_bytes)} bytes")
            return audio_bytes
        
        return b''
    
    def record_chunk(self, duration_seconds: float) -> bytes:
        """Record a specific duration of audio"""
        try:
            import sounddevice as sd
            import numpy as np
            
            logger.info(f"Recording {duration_seconds}s of audio...")
            
            audio = sd.rec(
                int(duration_seconds * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            )
            sd.wait()
            
            audio_bytes = (audio * 32767).astype(np.int16).tobytes()
            return audio_bytes
            
        except ImportError:
            logger.error("sounddevice not installed")
            return b''
        except Exception as e:
            logger.error(f"Recording error: {e}")
            return b''


# Global voice processor instance
_voice_processor = None

def get_voice_processor() -> VoiceProcessor:
    """Get voice processor instance"""
    global _voice_processor
    if _voice_processor is None:
        _voice_processor = VoiceProcessor()
    return _voice_processor