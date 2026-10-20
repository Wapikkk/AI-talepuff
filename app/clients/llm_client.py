from dataclasses import dataclass
from typing import Protocol


class LLMError(RuntimeError):
    """Penyedia LLM tidak bisa dihubungi atau membalas dengan error."""


@dataclass(frozen=True)
class GenerationParams:
    temperature: float = 0.7
    repeat_penalty: float | None = 1.0


@dataclass(frozen=True)
class LLMResponse:
    text: str
    output_tokens: int = 0
    generation_seconds: float = 0.0


class LLMClient(Protocol):
    async def warm_up(self) -> None:
        ...

    async def chat(
        self,
        messages: list[dict],
        schema: dict | None = None,
        params: GenerationParams = GenerationParams(),
    ) -> LLMResponse:
        ...
