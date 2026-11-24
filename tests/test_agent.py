"""Behavior tests against a scripted fake OpenAI-compatible server (no real LLM)."""
import json, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

import agent


def reply(content=None, tool_calls=None, finish="stop", **extra):
    message = {"role": "assistant", "content": content, **extra}
    if tool_calls:
        message["tool_calls"] = tool_calls
    return {"choices": [{"index": 0, "message": message, "finish_reason": finish}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2, "prompt_tokens_details": {"cached_tokens": 8}}}


def bash_call(call_id, command=None, raw=None):
    arguments = raw if raw is not None else json.dumps({"command": command})
    return {"id": call_id, "type": "function", "function": {"name": "bash", "arguments": arguments}}


DONE = reply("done")


@pytest.fixture
def llm(monkeypatch, tmp_path):
    """Serves scripted responses in order; each item is a body dict or (status, body)."""
    state = {"script": [], "requests": []}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            state["requests"].append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            item = state["script"].pop(0)
            status, body = item if isinstance(item, tuple) else (200, item)
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(agent, "LLM_BASE_URL", f"http://127.0.0.1:{server.server_port}/v1")
    monkeypatch.setattr(agent, "RETRY_BACKOFF", 0.01)
    monkeypatch.chdir(tmp_path)

    def run(*script):
        state["script"] = list(script)
        return agent.agent_loop("do the task", tmp_path / "transcript.jsonl"), state["requests"]

    yield run
    server.shutdown()


def tool_results(request):
    return [m["content"] for m in request["messages"] if m["role"] == "tool"]


def test_parallel_tool_calls_stay_in_one_assistant_message_with_reasoning(llm):
    calls = [bash_call("a", "echo A"), bash_call("b", "echo B")]
    result, requests = llm(reply("checking", calls, "tool_calls", reasoning_content="plan"), DONE)
    assert result.status == "done"
    history = requests[1]["messages"]
    assistants = [m for m in history if m["role"] == "assistant"]
    assert len(assistants) == 1 and assistants[0]["reasoning_content"] == "plan"
    assert [m["role"] for m in history[2:]] == ["assistant", "tool", "tool"]
    assert [m["tool_call_id"] for m in history[3:]] == ["a", "b"]


@pytest.mark.parametrize("raw", ['{"command": "echo hi"', "", '["ls", "-la"]', '{"command": ["ls", "-la"]}'])
def test_malformed_arguments_go_back_to_model_and_run_continues(llm, raw):
    result, requests = llm(reply(None, [bash_call("a", raw=raw)], "tool_calls"), DONE)
    assert result.status == "done"
    assert tool_results(requests[1])[0].startswith("Error: tool arguments")


def test_unknown_tool_goes_back_to_model(llm):
    call = {"id": "a", "type": "function", "function": {"name": "python", "arguments": "{}"}}
    result, requests = llm(reply(None, [call], "tool_calls"), DONE)
    assert result.status == "done"
    assert "unknown tool 'python'" in tool_results(requests[1])[0]


def test_huge_tool_output_is_truncated_head_and_tail(llm):
    result, requests = llm(reply(None, [bash_call("a", "seq 1 300000")], "tool_calls"), DONE)
    output = tool_results(requests[1])[0]
    assert len(output) < agent.MAX_TOOL_OUTPUT + 200
    assert "\n1\n2\n" in output and "300000" in output and "bytes truncated" in output


def test_truncated_final_answer_is_a_failure(llm):
    result, _ = llm(reply("Here is the plan:\n1. Move", finish="length"))
    assert result.status == "truncated"


def test_empty_reply_is_a_failure(llm):
    result, _ = llm(reply("", reasoning_content="I should run the tests..."))
    assert result.status == "empty_reply"


def test_usage_is_accumulated(llm):
    result, _ = llm(reply(None, [bash_call("a", "true")], "tool_calls"), DONE)
    assert (result.usage.prompt, result.usage.completion, result.usage.cached) == (20, 4, 16)


def test_transient_http_errors_are_retried(llm):
    result, requests = llm((503, {"error": "overloaded"}), (429, {"error": "slow down"}), DONE)
    assert result.status == "done" and len(requests) == 3


def test_client_error_fails_fast_with_response_body(llm):
    with pytest.raises(RuntimeError, match="maximum context length"):
        llm((400, {"error": {"message": "maximum context length is 32768 tokens"}}), DONE)


def test_error_body_with_200_fails_fast(llm):
    with pytest.raises(RuntimeError, match="Unexpected LLM response"):
        llm({"error": {"message": "upstream overloaded"}})


def test_transcript_records_every_message(llm, tmp_path):
    llm(reply(None, [bash_call("a", "true")], "tool_calls"), DONE)
    roles = [json.loads(line)["message"]["role"] for line in (tmp_path / "transcript.jsonl").read_text().splitlines()]
    assert roles == ["system", "user", "assistant", "tool", "assistant"]


# run_bash edge cases


def test_llm_secrets_are_not_visible_to_commands():
    assert "sk-test-secret" not in agent.run_bash("env")


def test_stdin_is_closed():
    started = time.monotonic()
    assert agent.run_bash("cat").startswith("Exit code: 0")
    assert time.monotonic() - started < 2


def test_background_job_does_not_block(tmp_path):
    started = time.monotonic()
    output = agent.run_bash(f"sleep 5 & echo started")
    assert "started" in output and time.monotonic() - started < 2


def test_timeout_kills_process_group_and_keeps_partial_output(monkeypatch, tmp_path):
    monkeypatch.setattr(agent, "BASH_TIMEOUT", 1)
    marker = tmp_path / "after"
    output = agent.run_bash(f"echo test_1 PASSED; (sleep 2; touch {marker}) & sleep 30")
    assert "timed out" in output and "test_1 PASSED" in output
    time.sleep(1.5)
    assert not marker.exists()


def test_invalid_utf8_output_keeps_exit_code_and_side_effects(tmp_path):
    output = agent.run_bash(f"echo created > {tmp_path}/marker; printf '\\377\\376'; exit 3")
    assert output.startswith("Exit code: 3") and (tmp_path / "marker").exists()
