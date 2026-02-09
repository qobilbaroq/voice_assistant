# speech_to_text.py
from faster_whisper import WhisperModel
from config import WHISPER_MODEL, WHISPER_DEVICE
import numpy as np

class SpeechToText:
    def __init__(self):
        print("Loading Whisper model...")
        self.model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE)
        print("Whisper model loaded!")
        
    def transcribe(self, audio_data, sample_rate=16000):
        """Convert audio to text"""
        try:
            # Convert numpy array to float32
            audio_np = np.array(audio_data, dtype=np.float32)
            
            # Transcribe
            segments, info = self.model.transcribe(audio_np, language="en")
            
            # Combine all segments
            text = " ".join([segment.text for segment in segments])
            
            return text.strip()
        except Exception as e:
            print(f"STT Error: {e}")
            return ""