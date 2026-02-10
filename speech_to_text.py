from faster_whisper import WhisperModel
from config import WHISPER_MODEL, WHISPER_DEVICE
import numpy as np

class SpeechToText:
    def __init__(self):
        print("Loading Whisper model...")
        self.model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE)
        print("Whisper model loaded!")
        
    def transcribe(self, audio_data, sample_rate=16000, language='id'):
        """Convert audio to text. Default language is Indonesian ('id')."""
        try:
            # Convert numpy array to float32
            audio_np = np.array(audio_data, dtype=np.float32)

            # Force the model to use Indonesian by default
            segments, info = self.model.transcribe(audio_np, language=language)

            # Combine all segments
            text = " ".join([segment.text for segment in segments]).strip()

            return text
        except Exception as e:
            print(f"STT Error: {e}")
            return ""