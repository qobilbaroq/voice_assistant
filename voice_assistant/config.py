import os

# Paths
PIPER_MODEL_PATH = os.path.expanduser("~/piper_voices/en_GB-semaine-medium.onnx")
WAKE_WORD_MODEL = "hey_jarvis, alexa"  

# Whisper Settings
WHISPER_MODEL = "small"
WHISPER_DEVICE = "cpu"

# Ollama Settings
OLLAMA_MODEL = "gemma2:2b"
OLLAMA_HOST = "http://localhost:11434"

# Audio Settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024

# TTS Settings - Piper (backup)
PIPER_SPEAKER = 2  # 0-3 untuk semaine (4 speakers)

# TTS Settings - Kokoro
KOKORO_MODEL_PATH = os.path.expanduser("~/kokoro/kokoro-v0_19.onnx")
KOKORO_VOICES_PATH = os.path.expanduser("~/kokoro/voices.bin")
KOKORO_VOICE = "af_sky"  # voice default

# Wake Word Settings
WAKE_WORD_THRESHOLD = 0.5
