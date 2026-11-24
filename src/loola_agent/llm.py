"""LLM boundary: a minimal protocol and an async adapter for OpenAI-compatible /v1/chat/completions."""
import asyncio, logging
from dataclasses import dataclass
from typing import Protocol, Self

import httpx

log = logging.getLogger(__name__)

TRANSIENT_STATUS = {429, 500, 502, 503, 504}


@dataclass(frozen=True)
class Usage:
    prompt: int = 0
    completion: int = 0
    cached: int | None = None  # None: the server does not report cached prompt tokens

    def __add__(self, other: "Usage") -> "Usage":
        cached = None if self.cached is None and other.cached is None else (self.cached or 0) + (other.cached or 0)
        return Usage(self.prompt + other.prompt, self.completion + other.completion, cached)


@dataclass(frozen=True)
class Completion:
    message: dict  # assistant message exactly as the server returned it (wire format)
    finish_reason: str | None
    usage: Usage


class LLMError(RuntimeError):
    pass


class LLM(Protocol):
    max_tokens: int  # completion limit of a regular reply

    async def complete(self, messages: list[dict], tools: list[dict], *,
                       max_tokens: int | None = None) -> Completion: ...


class OpenAICompatibleLLM:
    def __init__(self, base_url: str, api_key: str, model: str, *, max_tokens: int = 8192,
                 temperature: float | None = None, headers: dict[str, str] | None = None, retries: int = 3,
                 retry_backoff: float = 2.0, transport: httpx.AsyncBaseTransport | None = None):
        self.model, self.max_tokens, self.temperature = model, max_tokens, temperature
        self.retries, self.retry_backoff = retries, retry_backoff
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/") + "/", transport=transport, timeout=httpx.Timeout(600, connect=10),
            headers={"Authorization": f"Bearer {api_key}", "User-Agent": "loola-agent/0.1.0", **(headers or {})})

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._client.aclose()

    async def complete(self, messages: list[dict], tools: list[dict], *,
                       max_tokens: int | None = None) -> Completion:
        # max_completion_tokens: reasoning models reject max_tokens; vLLM and other servers accept both.
        payload = {"model": self.model, "messages": messages, "tools": tools, "tool_choice": "auto",
                   "max_completion_tokens": max_tokens or self.max_tokens}
        if self.temperature is not None:  # many reasoning models accept only their default temperature
            payload["temperature"] = self.temperature
        response = await self._post_with_retry(payload)
        if response.is_error:
            raise LLMError(f"HTTP {response.status_code}: {response.text[:2000]}")
        body = response.json()
        if not body.get("choices") or "usage" not in body:
            raise LLMError(f"Unexpected LLM response: {response.text[:2000]}")
        choice, usage = body["choices"][0], body["usage"]
        cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
        return Completion(choice["message"], choice.get("finish_reason"),
                          Usage(usage["prompt_tokens"], usage["completion_tokens"], cached))

    async def _post_with_retry(self, payload: dict) -> httpx.Response:
        error = ""
        for attempt in range(1, self.retries + 1):
            try:
                response = await self._client.post("chat/completions", json=payload)
                if response.status_code not in TRANSIENT_STATUS:
                    return response
                error = f"HTTP {response.status_code}: {response.text[:500]}"
            except httpx.TransportError as e:  # connect/read timeouts, connection resets
                error = repr(e)
            log.warning("LLM request failed (attempt %d/%d): %s", attempt, self.retries, error)
            if attempt < self.retries:
                await asyncio.sleep(self.retry_backoff * 2 ** (attempt - 1))
        raise LLMError(f"LLM request failed after {self.retries} attempts: {error}")
