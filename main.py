import sounddevice as sd
import numpy as np
import queue
import time
import webrtcvad
from voice_assistant.wake_word_detector import WakeWordDetector
from voice_assistant.speech_to_text import SpeechToText
from voice_assistant.llm_handler import LLMHandler
from voice_assistant.text_to_speech import TextToSpeech
from voice_assistant.config import SAMPLE_RATE, CHANNELS

class VoiceAssistant:
    def __init__(self):
        print("Initializing Voice Assistant...")
        
        self.wake_word_detector = WakeWordDetector()
        self.stt = SpeechToText()
        self.llm = LLMHandler()
        self.tts = TextToSpeech()
        
        self.audio_queue = queue.Queue()
        self.sample_rate = SAMPLE_RATE
        self.is_speaking = False
        
        # Stop commands
        self.stop_commands = ['stop', 'done', 'berhenti', 'cukup', 'cancel']
        
        print("Voice Assistant ready!")
        
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            print(status)
        self.audio_queue.put(indata.copy())
    
    def is_stop_command(self, text):
        """Check if text contains stop command"""
        text_lower = text.lower().strip()
        for cmd in self.stop_commands:
            if cmd in text_lower:
                return True
        return False
    
    def listen_for_speech(self, max_duration=10):
        """Record audio until silence detected - WAIT for user to start speaking"""
        print("🎤 Listening... (speak when ready)")
        vad = webrtcvad.Vad(1)
        
        recorded_audio = []
        silence_chunks = 0
        max_silence_chunks = 60
        
        started_speaking = False
        waiting_for_speech = True
        wait_timeout = 0
        max_wait = 200
        
        with sd.InputStream(samplerate=self.sample_rate, 
                           channels=CHANNELS,
                           blocksize=480) as stream:
            
            for _ in range(int(max_duration * self.sample_rate / 480)):
                audio_chunk, _ = stream.read(480)
                
                audio_int16 = (audio_chunk.flatten() * 32767).astype(np.int16).tobytes()
                
                try:
                    is_speech = vad.is_speech(audio_int16, self.sample_rate)
                    
                    if waiting_for_speech:
                        if is_speech:
                            print("🗣️ Speech detected, recording...")
                            waiting_for_speech = False
                            started_speaking = True
                            recorded_audio.append(audio_chunk)
                        else:
                            wait_timeout += 1
                            if wait_timeout > max_wait:
                                print("⏱️ Timeout waiting for speech")
                                break
                    
                    elif started_speaking:
                        recorded_audio.append(audio_chunk)
                        
                        if is_speech:
                            silence_chunks = 0
                        else:
                            silence_chunks += 1
                            
                            if silence_chunks > max_silence_chunks:
                                print("✅ End of speech detected")
                                break
                                
                except:
                    if started_speaking:
                        recorded_audio.append(audio_chunk)
        
        if recorded_audio:
            audio_data = np.concatenate(recorded_audio, axis=0)
            return audio_data.flatten()
        return np.array([])
    
    def run(self):
        """Main loop"""
        print("\n=== Voice Assistant Started ===")
        print("Listening for wake word 'Hey Jarvis'...")
        print("Say 'stop', 'done', or 'berhenti' to cancel anytime")
        print("Press Ctrl+C to stop\n")
        
        try:
            with sd.InputStream(samplerate=self.sample_rate,
                              channels=CHANNELS,
                              blocksize=1280,
                              callback=self.audio_callback):
                
                while True:
                    if not self.audio_queue.empty():
                        audio_chunk = self.audio_queue.get()
                        
                        wake_detected = self.wake_word_detector.detect(audio_chunk.flatten())
                        
                        # Interrupt jika AI sedang berbicara
                        if self.is_speaking and wake_detected:
                            print("\n⚠️ Interrupt detected! Stopping speech...")
                            self.tts.stop()
                            self.is_speaking = False
                            
                            while not self.audio_queue.empty():
                                self.audio_queue.get()
                            
                            time.sleep(0.5)
                            print("\n✅ Ready for new command!\n")
                            continue
                        
                        # Normal wake word detection
                        if not self.is_speaking and wake_detected:
                            
                            print("\n🎤 Wake word detected!")
                            
                            while not self.audio_queue.empty():
                                self.audio_queue.get()
                            
                            time.sleep(0.3)
                            
                            # Record user speech
                            audio = self.listen_for_speech(max_duration=10)
                            
                            if len(audio) > 0:
                                print("⚙️ Processing speech...")
                                text = self.stt.transcribe(audio, self.sample_rate)
                                
                                if text:
                                    print(f"💬 You: {text}")
                                    
                                    # Check untuk stop command
                                    if self.is_stop_command(text):
                                        print("🛑 Stop command detected. Returning to standby...\n")
                                        continue
                                    
                                    # Generate response
                                    print("🤔 Thinking...")
                                    response = self.llm.generate_response(text)
                                    print(f"🤖 Assistant: {response}\n")
                                    
                                    # Speak response
                                    print("🔊 Speaking...")
                                    
                                    while not self.audio_queue.empty():
                                        self.audio_queue.get()
                                    
                                    self.is_speaking = True
                                    self.tts.speak(response)
                                    self.is_speaking = False
                                    
                                    time.sleep(0.5)
                                    while not self.audio_queue.empty():
                                        self.audio_queue.get()
                                    
                                    print("\n✅ Done! Listening for wake word again...\n")
                                else:
                                    print("❌ No speech recognized. Try again.\n")
                            else:
                                print("❌ No audio recorded.\n")
                    
                    time.sleep(0.01)
                    
        except KeyboardInterrupt:
            print("\n\nShutting down Voice Assistant...")
            print("Goodbye!")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()