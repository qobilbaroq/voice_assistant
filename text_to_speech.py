# text_to_speech.py
import subprocess
import sounddevice as sd
import soundfile as sf
import os
from config import PIPER_MODEL_PATH, PIPER_SPEAKER

class TextToSpeech:
    def __init__(self):
        self.model_path = PIPER_MODEL_PATH
        self.speaker = PIPER_SPEAKER
        
    def speak(self, text):
        """Convert text to speech and play it - FAST VERSION"""
        try:
            # Limit text
            if len(text) > 300:
                text = text[:300] + "..."
            
            # Escape characters
            text = text.replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
            
            # Generate and play directly
            output_file = "/tmp/tts_output.wav"
            
            cmd = f'echo "{text}" | piper --model {self.model_path} --speaker {self.speaker} --output_file {output_file}'
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            
            # Play audio
            data, fs = sf.read(output_file)
            sd.play(data, fs)
            sd.wait()
            
            # Cleanup
            if os.path.exists(output_file):
                os.remove(output_file)
            
            return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False