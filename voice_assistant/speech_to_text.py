from faster_whisper import WhisperModel
from .config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE
import numpy as np

class SpeechToText:
    def __init__(self):
        print(f"Loading Whisper {WHISPER_MODEL} model (optimized)...")
        
        # Pakai int8 untuk kurangi RAM
        self.model = WhisperModel(
            WHISPER_MODEL, 
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE  # int8 = lebih ringan
        )
        print("Whisper model loaded!")
        
    def transcribe(self, audio_data, sample_rate=16000, language='id'):
        """Convert audio to text"""
        try:
            audio_np = np.array(audio_data, dtype=np.float32)

            # Beam size kecil = lebih cepat, kurang RAM
            segments, info = self.model.transcribe(
                audio_np, 
                language=language,
                beam_size=1,  # Default 5, kita pakai 1 = lebih ringan
                vad_filter=True  # Filter noise otomatis
            )

            text = " ".join([segment.text for segment in segments]).strip()
            return text
            
        except Exception as e:
            print(f"STT Error: {e}")
            return ""