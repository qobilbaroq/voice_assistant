# wake_word_detector.py
from openwakeword.model import Model
import numpy as np

class WakeWordDetector:
    def __init__(self):
        print("Loading wake word model...")
        self.model = Model()
        print(f"Available models: {list(self.model.models.keys())}")
        print("Wake word model loaded!")
        
    def detect(self, audio_chunk):
        """Detect wake word in audio chunk"""
        try:
            # Convert to int16
            audio_int16 = (audio_chunk * 32767).astype(np.int16)
            
            # Get predictions
            prediction = self.model.predict(audio_int16)
            
            # Print all predictions for debugging
            max_score = max(prediction.values())
            if max_score > 0.3:  # Lower threshold for debugging
                print(f"Scores: {prediction}")
            
            # Check if any wake word detected
            for key, value in prediction.items():
                if key == "hey_jarvis" and value > 0.4:  # Naikan dari 0.5 ke 0.7
                    print(f"✅ Detected: {key} with score {value}")
                    return True
            
            return False
        except Exception as e:
            print(f"Wake word detection error: {e}")
            return False