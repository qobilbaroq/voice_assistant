# Voice Assistant - Cara Menggunakan

Panduan singkat untuk menjalankan dan menggunakan voice assistant ini.

## Prasyarat
- Python 3.8 atau lebih baru.
- Pastikan dependency terpasang. Jika tersedia, jalankan:

```
pip install -r requirements.txt
```

### Install tambahan (Ollama dan sistem audio)
- Ollama: ini adalah runtime LLM lokal. Ikuti panduan resmi di https://ollama.ai untuk memasang Ollama pada sistem Anda. Setelah terpasang, jalankan daemon Ollama sesuai dokumentasinya dan unduh model yang diperlukan.
- Paket sistem untuk audio (Linux Debian/Ubuntu):


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


