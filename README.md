# Voice Assistant - Cara Menggunakan

Panduan singkat untuk menjalankan dan menggunakan voice assistant ini.

**Project Structure**
- voice_assistant/: package containing the actual implementation
- main.py: thin runner that imports from the package
- README.md: this file


## Prasyarat
- Python 3.8 atau lebih baru.
- Pastikan dependency terpasang. Jika tersedia, jalankan:

```
pip install -r requirements.txt
```

### Install tambahan (Ollama dan sistem audio)
- Ollama: ini adalah runtime LLM lokal. Ikuti panduan resmi di https://ollama.ai untuk memasang Ollama pada sistem Anda. Setelah terpasang, jalankan daemon Ollama sesuai dokumentasinya dan unduh model yang diperlukan.
- Paket sistem untuk audio (Linux Debian/Ubuntu):

### Komponen eksternal & instalasi
File-file di repo ini mengandalkan beberapa komponen eksternal yang harus diinstall di luar repo. Ringkasan dan langkah cepat pemasangan:

- Python: gunakan Python 3.8 atau lebih baru. Buat virtual environment disarankan.

- Ollama (LLM runtime)
	- Ikuti panduan resmi: https://ollama.ai
	- Setelah terpasang, jalankan daemon/serve sesuai dokumentasi dan tarik model yang dipakai, contohnya:

```bash
ollama pull gemma2:2b
ollama run   # atau jalankan daemon sesuai dokumentasi Ollama
```

- Kokoro (TTS via ONNX)
	- Paket Python: `kokoro_onnx` (install via pip jika tersedia):

```bash
pip install kokoro_onnx
```

	- Download model dan file suara (letakkan sesuai `voice_assistant/config.py` default):

	- Model: `~/kokoro/kokoro-v0_19.onnx`
	- Voices: `~/kokoro/voices.bin`

- OpenWakeWord (detektor wake word)
	- Paket Python yang dibutuhkan: `openwakeword` (atau sesuai dokumentasi implementasi yang dipakai):

```bash
pip install openwakeword
```

- Speech-to-text (Whisper via faster-whisper)
	- Install:

```bash
pip install faster-whisper
```

- Audio & sistem tambahan
	- `sounddevice` (audio I/O):

```bash
pip install sounddevice
```

	- `webrtcvad` (Voice Activity Detection):

```bash
pip install webrtcvad
```

	- Pada Linux (Debian/Ubuntu) Anda mungkin perlu paket system untuk audio & build tools:

```bash
sudo apt update
sudo apt install -y build-essential libsndfile1 libportaudio2 portaudio19-dev libasound2-dev
```

- Dependensi lain yang mungkin diperlukan
	- `ollama` client (jika ada), `kokoro_onnx`, `openwakeword`, `faster-whisper`, `sounddevice`, `webrtcvad`, `numpy`

Quick setup (contoh):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy sounddevice faster-whisper webrtcvad openwakeword kokoro_onnx
# lalu ikuti langkah instalasi Ollama dan download modelnya
```

Catatan:
- Nama paket pip dapat berbeda tergantung distribusi pihak ketiga; jika pip tidak menemukan paket, cek dokumentasi masing-masing proyek.
- Model TTS (Kokoro) dan file suara tidak disertakan di repo — unduh dari sumber resmi dan simpan pada path yang sesuai (`~/kokoro/...`) atau ubah `voice_assistant/config.py`.
- Jika Anda menggunakan alternatif (mis. Piper untuk TTS), pastikan model lokal dan path dikonfigurasi di `voice_assistant/config.py`.

Catatan: Jika `llm_handler.py` dikonfigurasi menggunakan Ollama, periksa `config.py` untuk pengaturan host/port atau variabel koneksi lainnya.

## Menjalankan
1. Buka terminal di folder proyek.
2. Jalankan:

```
python3 main.py
```

## Cara Pakai (sederhana)
- Tunggu program siap dan mendengarkan (akan menggunakan wake word jika ada).
- Ucapkan wake word (jika diaktifkan), lalu sampaikan perintah atau pertanyaan.
- Sistem akan memproses suara, mengirim ke modul pemrosesan, dan membalas melalui suara.

## Pengaturan cepat
- Untuk mengubah pengaturan (mis. microphone, bahasa, API keys), edit file `config.py`.

## File utama
- `main.py` — entry point aplikasi.
- `wake_word_detector.py` — deteksi wake word.
- `speech_to_text.py` — konversi suara ke teks.
- `llm_handler.py` — mengirim prompt dan menerima jawaban (opsional).
- `text_to_speech.py` — mengubah teks menjadi suara.

## Menghentikan
- Tekan `Ctrl+C` di terminal untuk menghentikan program.

## Troubleshooting singkat
- Jika tidak ada suara masuk, cek pengaturan microphone di sistem dan `config.py`.
- Jika modul external membutuhkan API key, pastikan variabel yang sesuai di `config.py` terisi.

## Platform: Windows & macOS
Project ini dikembangkan agar berjalan di Linux, tetapi dapat dijalankan di macOS dan Windows dengan beberapa persiapan tambahan:

- macOS
	- Pasang Homebrew jika belum ada: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
	- Pasang PortAudio (dipakai oleh `sounddevice`):

```bash
brew install portaudio
```

	- Buat virtualenv dan install requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

- Windows
	- Disarankan menjalankan di WSL2 (Ubuntu) untuk kemudahan instalasi, atau pastikan Build Tools (Visual Studio) tersedia untuk membangun ekstensi C jika diperlukan.
	- Jika menggunakan native Windows, instal `portaudio` binary terlebih dahulu atau gunakan prebuilt wheels untuk `sounddevice`/`webrtcvad`.
	- Langkah cepat (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Catatan penting:
- Beberapa paket (mis. `webrtcvad`, `openwakeword`) mengandung komponen native dan mungkin memerlukan toolchain (build-essential/Visual Studio) untuk kompilasi.
- `ollama` biasanya berjalan pada Linux/macOS; di Windows gunakan WSL2 atau Docker bila Ollama tidak tersedia natively.
- Model TTS (Kokoro) dan file suara harus didownload secara manual dan ditempatkan sesuai path di `voice_assistant/config.py`.



