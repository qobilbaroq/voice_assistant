import sounddevice as sd
import numpy as np
from kokoro_onnx import Kokoro
from .config import KOKORO_MODEL_PATH, KOKORO_VOICES_PATH, KOKORO_VOICE
import re

class TextToSpeech:
    def __init__(self):
        print("Loading Kokoro TTS model...")
        self.kokoro = Kokoro(KOKORO_MODEL_PATH, KOKORO_VOICES_PATH)
        self.voice = KOKORO_VOICE
        print(f"Kokoro TTS loaded with voice: {self.voice}!")
        
    def speak(self, text):
        """Convert text to speech and play it using Kokoro - STREAMING VERSION"""
        try:
            # Limit text length
            if len(text) > 300:
                text = text[:300] + "..."
            
            # Split text ke kalimat-kalimat (by . ! ?)
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
            
            # Generate dan play setiap kalimat langsung (streaming)
            for sentence in sentences:
                if sentence.strip():  # Skip kalimat kosong
                    # Generate audio untuk kalimat ini
                    audio, sample_rate = self.kokoro.create(
                        sentence, 
                        voice=self.voice, 
                        speed=1.3
                    )
                    
                    # Langsung play tanpa tunggu kalimat berikutnya
                    sd.play(audio, sample_rate)
                    sd.wait()  # Tunggu kalimat ini selesai baru lanjut ke kalimat berikutnya
            
            return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False
