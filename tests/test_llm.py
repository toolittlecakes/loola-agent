"""OpenAI-compatible adapter against a scripted httpx transport."""
import json

import httpx
import pytest

from loola_agent import LLMError, OpenAICompatibleLLM, Usage

OK = {"choices": [{"message": {"role": "assistant", "content": "hi", "reasoning_content": "r"},
                   "finish_reason": "stop"}],
      "usage": {"prompt_tokens": 10, "completion_tokens": 2, "prompt_tokens_details": {"cached_tokens": 8}}}


def llm_with(*responses):
    requests, script = [], list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        item = script.pop(0)
        if isinstance(item, Exception):
            raise item
        status, body = item if isinstance(item, tuple) else (200, item)
        return httpx.Response(status, json=body)

    llm = OpenAICompatibleLLM("http://llm/v1", "sk-test", "m", retry_backoff=0, transport=httpx.MockTransport(handler))
    return llm, requests


async def test_returns_message_as_is_and_parses_usage():
    llm, requests = llm_with(OK)
    completion = await llm.complete([{"role": "user", "content": "x"}], [])
    assert completion.message == OK["choices"][0]["message"]
    assert completion.usage == Usage(10, 2, 8)
    assert str(requests[0].url) == "http://llm/v1/chat/completions"


async def test_missing_cache_details_means_unknown_not_zero():
    llm, _ = llm_with({**OK, "usage": {"prompt_tokens": 1, "completion_tokens": 1}})
    assert (await llm.complete([], [])).usage.cached is None


async def test_transient_errors_are_retried():
    llm, requests = llm_with((503, {}), httpx.ConnectError("reset"), OK)
    assert (await llm.complete([], [])).message["content"] == "hi"
    assert len(requests) == 3


async def test_gives_up_after_retries():
    llm, _ = llm_with((502, {}), (502, {}), (502, {}))
    with pytest.raises(LLMError, match="after 3 attempts"):
        await llm.complete([], [])


async def test_client_error_fails_fast_with_response_body():
    llm, requests = llm_with((400, {"error": {"message": "maximum context length is 32768 tokens"}}))
    with pytest.raises(LLMError, match="maximum context length"):
        await llm.complete([], [])
    assert len(requests) == 1


async def test_error_body_with_200_fails_fast():
    llm, _ = llm_with({"error": {"message": "upstream overloaded"}})
    with pytest.raises(LLMError, match="Unexpected LLM response"):
        await llm.complete([], [])


async def test_sends_reasoning_model_compatible_payload_and_custom_headers():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=OK)

    llm = OpenAICompatibleLLM("http://llm/v1", "sk", "m", max_tokens=123, headers={"x-session": "s1"},
                              transport=httpx.MockTransport(handler))
    await llm.complete([], [])
    body = json.loads(requests[0].content)
    assert body["max_completion_tokens"] == 123 and "max_tokens" not in body and "temperature" not in body
    assert requests[0].headers["x-session"] == "s1" and requests[0].headers["user-agent"].startswith("loola-agent/")
