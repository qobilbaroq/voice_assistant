# config.py
import os

# Paths
PIPER_MODEL_PATH = os.path.expanduser("~/piper_voices/en_GB-semaine-medium.onnx")
WAKE_WORD_MODEL = "hey_jarvis"  

# Whisper Settings
WHISPER_MODEL = "small"
WHISPER_DEVICE = "cpu"

# Ollama Settings
OLLAMA_MODEL = "gemma3:1b"
OLLAMA_HOST = "http://localhost:11434"

# Audio Settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024

# TTS Settings
PIPER_SPEAKER = 2  # 0-3 untuk semaine (4 speakers)

# Wake Word Settings
WAKE_WORD_THRESHOLD = 0.5