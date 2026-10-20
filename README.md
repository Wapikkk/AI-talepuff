# AI-talepuff

Layanan AI TalePuff (FastAPI): membuat cerita pengantar tidur untuk balita lewat LLM (Ollama) dan mengubahnya menjadi suara (edge-tts). Dipanggil oleh backend Gin, bukan langsung oleh aplikasi.

## Menjalankan

```
pip install -r requirements.txt          # tambahkan requirements-dev.txt untuk tes/benchmark
ollama pull qwen3:4b
uvicorn app.main:app --env-file .env --port 8000
```

Dokumentasi API otomatis: `http://localhost:8000/docs`.

## Konfigurasi (environment variable, semua opsional)

| Variabel | Default | Keterangan |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | Penyedia LLM (saat ini hanya `ollama`) |
| `OLLAMA_URL` | `http://localhost:11434` | |
| `OLLAMA_MODEL` | `qwen3:4b` | |
| `LLM_TIMEOUT_SECONDS` | `180` | |
| `LLM_CONTEXT_WINDOW` | `4096` | |
| `LLM_MAX_OUTPUT_TOKENS` | `4096` | |
| `WORDS_PER_MINUTE` | `120` | Kecepatan baca TTS; menentukan target kata per menit |
| `STORY_MAX_ATTEMPTS` | `3` | Percobaan ulang bila cerita tidak lolos validasi |

Nilai tidak valid menghentikan aplikasi dengan pesan yang jelas.

## Struktur

```
app/
  api/        route tipis (HTTP saja)
  schemas/    kontrak request/response (Pydantic)
  services/   logika: story_generator (orkestrasi), scene_writer, prompts,
              safety (input), story_validation (keluaran), tts_service
  clients/    llm_client (antarmuka), ollama_client, factory
  core/       config
```

`StoryGenerator` hanya bergantung pada antarmuka `LLMClient`, jadi penyedia lain
cukup ditambahkan sebagai kelas baru di `app/clients/` dan dipilih di `factory.py`.

## Endpoint cerita

`POST /generate_story` menerima `character_name`, `theme`, `mood`, `length_minutes` (1-10),
`language`, `description`; field lain (mis. `child_id`) diabaikan. Balasan:
`status`, `title`, `response` (kontrak lama untuk Gin) ditambah `word_count`, `attempts`, `flags`.
Input tidak valid dibalas 422; kegagalan membuat cerita yang lolos validasi dibalas 502.
