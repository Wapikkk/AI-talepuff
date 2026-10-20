import re

import httpx

from app.clients.llm_client import GenerationParams, LLMError, LLMResponse

_NS = 1e9
WARMUP_TIMEOUT_SECONDS = 120.0


def _keep_alive_value(raw: str) -> int | str:
    return int(raw) if re.fullmatch(r"-?\d+", raw) else raw


class OllamaClient:
    def __init__(
        self,
        http: httpx.AsyncClient,
        model: str,
        context_window: int = 4096,
        max_output_tokens: int = 4096,
        think: bool | None = False,
        keep_alive: str | None = None,
    ) -> None:
        self._http = http
        self._model = model
        self._context_window = context_window
        self._max_output_tokens = max_output_tokens
        self._think = think
        self._keep_alive = keep_alive

    async def warm_up(self) -> None:
        payload: dict = {"model": self._model, "messages": [], "stream": False}
        if self._keep_alive is not None:
            payload["keep_alive"] = _keep_alive_value(self._keep_alive)
        try:
            response = await self._http.post("/api/chat", json=payload, timeout=WARMUP_TIMEOUT_SECONDS)
        except httpx.HTTPError as exc:
            raise LLMError(f"Tidak bisa memanaskan model Ollama: {type(exc).__name__}: {exc}") from exc
        if response.status_code != 200:
            raise LLMError(f"Ollama membalas {response.status_code} saat pemanasan: {response.text[:300]}")

    async def chat(
        self,
        messages: list[dict],
        schema: dict | None = None,
        params: GenerationParams = GenerationParams(),
    ) -> LLMResponse:
        options: dict = {
            "num_ctx": self._context_window,
            "num_predict": self._max_output_tokens,
            "temperature": params.temperature,
        }
        if params.repeat_penalty is not None:
            options["repeat_penalty"] = params.repeat_penalty

        payload: dict = {"model": self._model, "messages": messages, "stream": False, "options": options}
        if schema is not None:
            payload["format"] = schema
        if self._think is not None:
            payload["think"] = self._think
        if self._keep_alive is not None:
            payload["keep_alive"] = _keep_alive_value(self._keep_alive)

        try:
            response = await self._http.post("/api/chat", json=payload)
        except httpx.HTTPError as exc:
            raise LLMError(f"Tidak bisa menghubungi Ollama: {type(exc).__name__}: {exc}") from exc
        if response.status_code != 200:
            raise LLMError(f"Ollama membalas {response.status_code}: {response.text[:300]}")

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMError("Balasan Ollama bukan JSON yang valid") from exc
        message = data.get("message") or {}
        return LLMResponse(
            text=message.get("content", ""),
            output_tokens=data.get("eval_count", 0),
            generation_seconds=data.get("eval_duration", 0) / _NS,
        )
