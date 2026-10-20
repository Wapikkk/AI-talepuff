"""Memilih klien LLM sesuai konfigurasi.

Untuk menambah penyedia baru: tulis kelas yang memenuhi `LLMClient`, lalu tambahkan
cabangnya di sini dan nilainya di `SUPPORTED_PROVIDERS` (app/core/config.py).
"""
import httpx

from app.clients.llm_client import LLMClient
from app.clients.ollama_client import OllamaClient
from app.core.config import Settings


def build_http_client(settings: Settings) -> httpx.AsyncClient:
    """Satu klien HTTP dipakai bersama seluruh request (connection pooling)."""
    return httpx.AsyncClient(base_url=settings.ollama_url, timeout=settings.llm_timeout_seconds)


def build_llm_client(settings: Settings, http: httpx.AsyncClient) -> LLMClient:
    if settings.llm_provider == "ollama":
        return OllamaClient(
            http,
            model=settings.ollama_model,
            context_window=settings.llm_context_window,
            max_output_tokens=settings.llm_max_output_tokens,
            keep_alive=settings.ollama_keep_alive,
        )
    raise ValueError(f"Penyedia LLM tidak dikenal: {settings.llm_provider!r}")
