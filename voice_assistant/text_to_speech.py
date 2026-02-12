import sounddevice as sd
import numpy as np
from kokoro_onnx import Kokoro
from .config import KOKORO_MODEL_PATH, KOKORO_VOICES_PATH, KOKORO_VOICE
import re
import threading

class TextToSpeech:
    def __init__(self):
        print("Loading Kokoro TTS model...")
        self.kokoro = Kokoro(KOKORO_MODEL_PATH, KOKORO_VOICES_PATH)
        self.voice = KOKORO_VOICE
        self.should_stop = False
        print(f"Kokoro TTS loaded with voice: {self.voice}!")
    
    def stop(self):
        """Stop current speech"""
        self.should_stop = True
        sd.stop()
        
    def split_into_phrases(self, text):
        """Split text into natural phrases (lebih smooth dari per kalimat)"""
        # Split by koma, period, semicolon, dan conjunction words
        # Ini bikin streaming lebih natural
        phrases = re.split(r'([,;.!?]|\s+and\s+|\s+but\s+|\s+or\s+|\s+so\s+)', text)
        
        # Combine split results jadi phrases yang proper
        result = []
        current = ""
        
        for i, phrase in enumerate(phrases):
            current += phrase
            
            # Kalau ketemu punctuation atau conjunction, break
            if phrase.strip() in [',', ';', '.', '!', '?'] or 'and' in phrase or 'but' in phrase:
                if current.strip():
                    result.append(current.strip())
                    current = ""
        
        # Tambahin sisa
        if current.strip():
            result.append(current.strip())
        
        return result if result else [text]
        
    def speak(self, text):
        """Convert text to speech - IMPROVED STREAMING"""
        try:
            self.should_stop = False
            
            # Limit text length
            if len(text) > 300:
                text = text[:300] + "..."
            
            # Split jadi phrases kecil untuk streaming lebih smooth
            phrases = self.split_into_phrases(text)
            
            # Pre-generate beberapa audio chunks untuk reduce latency
            audio_queue = []
            
            # Generate audio di background thread sambil play
            def generate_audio():
                for phrase in phrases:
                    if self.should_stop:
                        break
                    if phrase.strip():
                        audio, sr = self.kokoro.create(
                            phrase, 
                            voice=self.voice, 
                            speed=1.3
                        )
                        audio_queue.append((audio, sr))
            
            # Start generation thread
            gen_thread = threading.Thread(target=generate_audio)
            gen_thread.start()
            
            # Play audio sambil generate
            played_count = 0
            while gen_thread.is_alive() or played_count < len(phrases):
                if self.should_stop:
                    print("🛑 Speech interrupted!")
                    gen_thread.join(timeout=0.1)
                    return False
                
                # Play kalau ada audio ready
                if played_count < len(audio_queue):
                    audio, sr = audio_queue[played_count]
                    sd.play(audio, sr)
                    sd.wait()
                    played_count += 1
                else:
                    # Tunggu sebentar kalau belum ready
                    import time
                    time.sleep(0.01)
            
            gen_thread.join()
            return True
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return False