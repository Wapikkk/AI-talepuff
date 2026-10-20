import os
import re
from collections.abc import Mapping
from dataclasses import dataclass

SUPPORTED_PROVIDERS = ("ollama",)
_KEEP_ALIVE_RE = re.compile(r"^-?\d+[smh]?$")


@dataclass(frozen=True)
class Settings:
    llm_provider: str = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"
    ollama_keep_alive: str = "30m"
    llm_timeout_seconds: float = 180.0
    llm_context_window: int = 4096
    llm_max_output_tokens: int = 4096
    words_per_minute: int = 120
    max_attempts: int = 3

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        env = os.environ if env is None else env
        defaults = cls()

        def text(key: str, default: str) -> str:
            return (env.get(key) or "").strip() or default

        def number(key: str, default, cast, low, high):
            raw = env.get(key)
            if raw is None or not raw.strip():
                return default
            try:
                value = cast(raw)
            except ValueError as exc:
                raise ValueError(f"{key} harus berupa angka, bukan {raw!r}") from exc
            if not low <= value <= high:
                raise ValueError(f"{key} harus di antara {low} dan {high}, bukan {value}")
            return value

        provider = text("LLM_PROVIDER", defaults.llm_provider).lower()
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"LLM_PROVIDER harus salah satu dari {SUPPORTED_PROVIDERS}, bukan {provider!r}")

        ollama_url = text("OLLAMA_URL", defaults.ollama_url).rstrip("/")
        if not ollama_url.startswith(("http://", "https://")):
            raise ValueError("OLLAMA_URL harus diawali http:// atau https://")

        keep_alive = text("OLLAMA_KEEP_ALIVE", defaults.ollama_keep_alive).lower()
        if not _KEEP_ALIVE_RE.match(keep_alive):
            raise ValueError(f"OLLAMA_KEEP_ALIVE harus berupa angka detik atau berakhiran s/m/h, bukan {keep_alive!r}")

        return cls(
            llm_provider=provider,
            ollama_url=ollama_url,
            ollama_model=text("OLLAMA_MODEL", defaults.ollama_model),
            ollama_keep_alive=keep_alive,
            llm_timeout_seconds=number("LLM_TIMEOUT_SECONDS", defaults.llm_timeout_seconds, float, 5, 600),
            llm_context_window=number("LLM_CONTEXT_WINDOW", defaults.llm_context_window, int, 1024, 32768),
            llm_max_output_tokens=number("LLM_MAX_OUTPUT_TOKENS", defaults.llm_max_output_tokens, int, 256, 32768),
            words_per_minute=number("WORDS_PER_MINUTE", defaults.words_per_minute, int, 60, 240),
            max_attempts=number("STORY_MAX_ATTEMPTS", defaults.max_attempts, int, 1, 5),
        )
