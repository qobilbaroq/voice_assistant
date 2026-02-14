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
        
    def transcribe(self, audio_data, sample_rate=16000, language=None):
        """
        Convert audio to text with auto language detection
        
        Args:
            audio_data: Audio numpy array
            sample_rate: Sample rate (default 16000)
            language: Language code ('en', 'id', or None for auto-detect)
        """
        try:
            audio_np = np.array(audio_data, dtype=np.float32)

            # Transcribe with language detection
            segments, info = self.model.transcribe(
                audio_np, 
                language=language,  # None = auto-detect
                beam_size=1,  # Faster
                vad_filter=True  # Filter noise
            )

            text = " ".join([segment.text for segment in segments]).strip()
            
            # Print detected language (for debugging)
            if language is None and hasattr(info, 'language'):
                print(f"Detected language: {info.language}")
            
            return text
            
        except Exception as e:
            print(f"STT Error: {e}")
            return ""