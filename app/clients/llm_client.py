"""Antarmuka klien LLM.

Layanan cerita hanya bergantung pada antarmuka ini, bukan pada penyedia tertentu
(Ollama, gateway OpenAI-compatible, dsb.). Menambah penyedia berarti menulis satu
kelas baru yang memenuhi `LLMClient`, tanpa menyentuh logika cerita.
"""
from dataclasses import dataclass
from typing import Protocol


class LLMError(RuntimeError):
    """Penyedia LLM tidak bisa dihubungi atau membalas dengan error."""


@dataclass(frozen=True)
class GenerationParams:
    temperature: float = 0.7
    # Hanya dipakai penyedia yang mendukungnya (Ollama); penyedia lain boleh mengabaikan.
    repeat_penalty: float | None = 1.0


@dataclass(frozen=True)
class LLMResponse:
    text: str
    output_tokens: int = 0
    generation_seconds: float = 0.0


class LLMClient(Protocol):
    async def warm_up(self) -> None:
        """Siapkan model sebelum request pertama. Penyedia yang tidak perlu boleh no-op."""
        ...

    async def chat(
        self,
        messages: list[dict],
        schema: dict | None = None,
        params: GenerationParams = GenerationParams(),
    ) -> LLMResponse:
        """Kirim percakapan; bila `schema` diberikan, balasan harus JSON sesuai schema."""
        ...
