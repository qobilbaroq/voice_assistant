from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Import voice assistant
import sys
sys.path.append('/home/samantha/VOICE_ASSISTANT')

from voice_assistant.wake_word_detector import WakeWordDetector
from voice_assistant.speech_to_text import SpeechToText
from voice_assistant.llm_handler import LLMHandler
from voice_assistant.text_to_speech import TextToSpeech
from voice_assistant.config import SAMPLE_RATE, CHANNELS

import sounddevice as sd
import numpy as np
import queue
import webrtcvad

# Global instances
wake_detector = None
stt = None
llm = None
tts = None
audio_queue = queue.Queue()

# State
assistant_state = {
    'status': 'standby',
    'is_running': False,
    'transcript': [],
    'is_speaking': False
}

def audio_callback(indata, frames, time_info, status):
    """Audio stream callback"""
    if status:
        print(status)
    audio_queue.put(indata.copy())

def broadcast_state():
    """Broadcast state via WebSocket"""
    socketio.emit('state_update', assistant_state)

def listen_for_speech(max_duration=10, silence_threshold=100):
    """Record speech until silence - IMPROVED VERSION"""
    print("Listening for speech...")
    vad = webrtcvad.Vad(1)
    
    recorded_audio = []
    silence_chunks = 0
    max_silence_chunks = silence_threshold  # Default: 100 (~2.5 detik)
    
    started_speaking = False
    waiting_for_speech = True
    wait_timeout = 0
    max_wait = 300  # ~9 detik wait untuk user mulai bicara
    
    with sd.InputStream(samplerate=SAMPLE_RATE, 
                       channels=CHANNELS,
                       blocksize=480) as stream:
        
        for _ in range(int(max_duration * SAMPLE_RATE / 480)):
            audio_chunk, _ = stream.read(480)
            audio_int16 = (audio_chunk.flatten() * 32767).astype(np.int16).tobytes()
            
            try:
                is_speech = vad.is_speech(audio_int16, SAMPLE_RATE)
                
                if waiting_for_speech:
                    if is_speech:
                        print("Speech detected!")
                        waiting_for_speech = False
                        started_speaking = True
                        recorded_audio.append(audio_chunk)
                    else:
                        wait_timeout += 1
                        if wait_timeout > max_wait:
                            break
                
                elif started_speaking:
                    recorded_audio.append(audio_chunk)
                    
                    if is_speech:
                        silence_chunks = 0
                    else:
                        silence_chunks += 1
                        if silence_chunks > max_silence_chunks:
                            print(f"Silence detected after {silence_chunks} chunks")
                            break
            except:
                if started_speaking:
                    recorded_audio.append(audio_chunk)
    
    if recorded_audio:
        audio_data = np.concatenate(recorded_audio, axis=0)
        return audio_data.flatten()
    return np.array([])

def wait_for_follow_up(max_wait_seconds=6):
    """Wait for user to continue speaking without wake word"""
    print(f"Waiting for follow-up ({max_wait_seconds}s timeout)...")
    
    vad = webrtcvad.Vad(1)
    timeout_chunks = 0
    max_timeout = int(max_wait_seconds * SAMPLE_RATE / 480)
    
    while timeout_chunks < max_timeout and assistant_state['is_running']:
        if not audio_queue.empty():
            audio_chunk = audio_queue.get()
            audio_int16 = (audio_chunk.flatten() * 32767).astype(np.int16).tobytes()
            
            try:
                is_speech = vad.is_speech(audio_int16, SAMPLE_RATE)
                
                if is_speech:
                    print("✅ Follow-up detected! Recording...")
                    # Clear queue
                    while not audio_queue.empty():
                        audio_queue.get()
                    
                    time.sleep(0.2)
                    return True  # User is speaking
            except:
                pass
        
        timeout_chunks += 1
        time.sleep(0.03)
    
    print("⏱️ No follow-up. Returning to wake word mode...")
    return False

def process_user_speech(audio):
    """Process user speech - extract to avoid duplication"""
    global assistant_state
    
    if len(audio) == 0:
        return False
    
    assistant_state['status'] = 'thinking'
    broadcast_state()
    print("Processing...")
    
    # Auto-detect language (support English + Indonesian)
    text = stt.transcribe(audio, SAMPLE_RATE, language=None)
    
    if text:
        print(f"User: {text}")
        assistant_state['transcript'].append({
            'type': 'user',
            'text': text
        })
        broadcast_state()
        
        # Generate response
        response = llm.generate_response(text)
        print(f"AI: {response}")
        
        assistant_state['transcript'].append({
            'type': 'ai',
            'text': response
        })
        broadcast_state()
        
        # Speak
        assistant_state['status'] = 'speaking'
        assistant_state['is_speaking'] = True
        broadcast_state()
        
        while not audio_queue.empty():
            audio_queue.get()
        
        tts.speak(response)
        assistant_state['is_speaking'] = False
        
        time.sleep(0.5)
        while not audio_queue.empty():
            audio_queue.get()
        
        return True
    
    return False

def assistant_loop():
    """Main assistant loop - IMPROVED VERSION"""
    global assistant_state, wake_detector, stt, llm, tts
    
    # Initialize components
    print("Initializing components...")
    wake_detector = WakeWordDetector()
    stt = SpeechToText()
    llm = LLMHandler()
    tts = TextToSpeech()
    print("Components ready!")
    
    with sd.InputStream(samplerate=SAMPLE_RATE,
                       channels=CHANNELS,
                       blocksize=1280,
                       callback=audio_callback):
        
        while assistant_state['is_running']:
            if not audio_queue.empty():
                audio_chunk = audio_queue.get()
                
                # Detect wake word
                wake_detected = wake_detector.detect(audio_chunk.flatten())
                
                # Interrupt if speaking
                if assistant_state['is_speaking'] and wake_detected:
                    print("\n⚠️ Interrupt detected!")
                    tts.stop()
                    assistant_state['is_speaking'] = False
                    assistant_state['status'] = 'listening'
                    broadcast_state()
                    while not audio_queue.empty():
                        audio_queue.get()
                    time.sleep(0.5)
                    continue
                
                # Normal wake word
                if not assistant_state['is_speaking'] and wake_detected:
                    print("\n🎤 Wake word detected!")
                    assistant_state['status'] = 'recording'
                    broadcast_state()
                    
                    while not audio_queue.empty():
                        audio_queue.get()
                    
                    time.sleep(0.3)
                    
                    # Record speech with longer silence threshold
                    audio = listen_for_speech(max_duration=15, silence_threshold=100)
                    
                    # Process speech
                    if process_user_speech(audio):
                        # Success! Now wait for follow-up
                        assistant_state['status'] = 'listening'
                        broadcast_state()
                        
                        # AUTO CONTINUE: Wait for follow-up without wake word
                        if wait_for_follow_up(max_wait_seconds=8):
                            # User is speaking again!
                            assistant_state['status'] = 'recording'
                            broadcast_state()
                            
                            # Record follow-up
                            audio = listen_for_speech(max_duration=15, silence_threshold=100)
                            process_user_speech(audio)
                            
                            # Back to listening for wake word
                            assistant_state['status'] = 'listening'
                            broadcast_state()
                        else:
                            # Timeout - back to wake word mode
                            assistant_state['status'] = 'listening'
                            broadcast_state()
                    else:
                        print("❌ No speech recognized.\n")
                        assistant_state['status'] = 'listening'
                        broadcast_state()
            
            time.sleep(0.01)

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print('Client connected')
    emit('state_update', assistant_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('Client disconnected')

@socketio.on('start')
def handle_start():
    """Start voice assistant"""
    global assistant_state
    
    if not assistant_state['is_running']:
        assistant_state['is_running'] = True
        assistant_state['status'] = 'listening'
        broadcast_state()
        
        # Start assistant in background thread
        thread = threading.Thread(target=assistant_loop, daemon=True)
        thread.start()

@socketio.on('stop')
def handle_stop():
    """Stop voice assistant"""
    global assistant_state
    assistant_state['is_running'] = False
    assistant_state['status'] = 'standby'
    broadcast_state()

@socketio.on('clear')
def handle_clear():
    """Clear transcript"""
    assistant_state['transcript'] = []
    broadcast_state()

# Keep HTTP endpoints for compatibility
@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current status"""
    return jsonify(assistant_state)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)