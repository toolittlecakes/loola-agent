"""Minimal coding agent loop — one tool: bash."""
import json, os, signal, subprocess, sys, tempfile, time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import IO, Literal
import requests


LLM_BASE_URL = os.environ["LLM_BASE_URL"]
LLM_API_KEY = os.environ["LLM_API_KEY"]
LLM_MODEL = os.environ["LLM_MODEL"]
LLM_HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {LLM_API_KEY}"}
LLM_TIMEOUT = (10, 600)  # connect, read (seconds)
LLM_RETRIES = 3
RETRY_BACKOFF = 2.0  # seconds, doubled on each retry
TRANSIENT_STATUS = {429, 500, 502, 503, 504}
MAX_TURNS = 1000
BASH_TIMEOUT = 120
MAX_TOOL_OUTPUT = 10_000  # bytes of tool output kept in context (head + tail)
RUNS_DIR = Path(__file__).parent / "runs"

SYSTEM_PROMPT = """\
You are a coding agent. Your job is to help the user with programming tasks.

You have access to ONE tool: `bash` — which executes shell commands and returns stdout/stderr.

Workflow:
1. Plan what needs to be done.
2. Use `bash` to read files, run commands, write code, etc.
3. After gathering enough information or completing the task, give your final answer in natural language.
4. To finish, reply with a regular message (no tool call).

Be concise. Explain what you're doing before each command."""

LLM_TOOLS = [
    {"type": "function",
     "function": {"name": "bash",
                  "description": f"Execute a non-interactive shell command (stdin is closed, {BASH_TIMEOUT}s timeout) "
                                 "and return its exit code and combined stdout/stderr. Long outputs are truncated.",
                  "parameters": {"type": "object",
                                 "properties": {
                                     "command": {"type": "string", "description": "The bash command to execute."}
                                 },
                                 "required": ["command"]}
                 }
            }]


@dataclass
class Usage:
    prompt: int = 0
    completion: int = 0
    cached: int | None = None  # None: the server does not report cached prompt tokens

    def add(self, usage: dict) -> None:
        self.prompt += usage["prompt_tokens"]
        self.completion += usage["completion_tokens"]
        cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
        if cached is not None:
            self.cached = (self.cached or 0) + cached


@dataclass
class RunResult:
    status: Literal["done", "truncated", "empty_reply", "max_turns"]
    answer: str
    turns: int
    usage: Usage


def log(text: str) -> None:
    print(text, file=sys.stderr, flush=True)


def record(transcript: Path, event: dict) -> None:
    with transcript.open("a") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_head_tail(f: IO[bytes]) -> str:
    size = f.seek(0, os.SEEK_END)
    f.seek(0)
    if size <= MAX_TOOL_OUTPUT:
        return f.read().decode(errors="replace")
    half = MAX_TOOL_OUTPUT // 2
    head = f.read(half)
    f.seek(-half, os.SEEK_END)
    tail = f.read()
    marker = f"\n[... {size - 2 * half} bytes truncated; use head/tail/grep/sed -n to read specific parts ...]\n"
    return head.decode(errors="replace") + marker + tail.decode(errors="replace")


def run_bash(command: str) -> str:
    # Output goes to a file, not a pipe: background jobs (`server &`) don't block the call,
    # and partial output survives a timeout. Own session lets us kill the whole process group.
    env = {k: v for k, v in os.environ.items() if not k.startswith("LLM_")}
    with tempfile.TemporaryFile() as out:
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,
                                env=env, start_new_session=True)
        try:
            status = f"Exit code: {proc.wait(timeout=BASH_TIMEOUT)}"
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            status = f"Error: command timed out after {BASH_TIMEOUT}s and was killed. Output so far:"
        return f"{status}\n{read_head_tail(out)}"


def call_tool(name: str, raw_arguments: str) -> str:
    """Model mistakes come back as tool results, so the model can fix the call itself."""
    if name != "bash":
        return f"Error: unknown tool '{name}'. Available tools: bash."
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as e:
        return f"Error: tool arguments are not valid JSON ({e}). Re-issue the call with a valid JSON object."
    if not isinstance(arguments, dict) or not isinstance(arguments.get("command"), str):
        return 'Error: tool arguments must be a JSON object like {"command": "<string>"}.'
    return run_bash(arguments["command"])


def post_with_retry(payload: dict) -> requests.Response:
    error = ""
    for attempt in range(1, LLM_RETRIES + 1):
        try:
            response = requests.post(f"{LLM_BASE_URL}/chat/completions", json=payload, headers=LLM_HEADERS,
                                     timeout=LLM_TIMEOUT)
            if response.status_code not in TRANSIENT_STATUS:
                return response
            error = f"HTTP {response.status_code}: {response.text[:500]}"
        except (requests.ConnectionError, requests.Timeout) as e:
            error = repr(e)
        log(f"⚠️  LLM request failed (attempt {attempt}/{LLM_RETRIES}): {error}")
        if attempt < LLM_RETRIES:
            time.sleep(RETRY_BACKOFF * 2 ** (attempt - 1))
    raise RuntimeError(f"LLM request failed after {LLM_RETRIES} attempts: {error}")


def call_llm(messages: list[dict]) -> dict:
    payload = {"model": LLM_MODEL, "messages": messages, "tools": LLM_TOOLS, "tool_choice": "auto",
               "temperature": 0.1, "max_tokens": 4096}
    response = post_with_retry(payload)
    if not response.ok:
        raise RuntimeError(f"LLM request failed: HTTP {response.status_code}: {response.text[:2000]}")
    body = response.json()
    if not body.get("choices") or "usage" not in body:
        raise RuntimeError(f"Unexpected LLM response: {response.text[:2000]}")
    return body


def agent_loop(user_message: str, transcript: Path) -> RunResult:
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}]
    for message in messages:
        record(transcript, {"turn": 0, "message": message})
    usage = Usage()
    for turn in range(1, MAX_TURNS + 1):
        log(f"\n{'='*60}\n🔄 Turn {turn}\n{'='*60}")
        body = call_llm(messages)
        choice = body["choices"][0]
        msg = choice["message"]
        usage.add(body["usage"])
        messages.append(msg)  # as-is: keeps parallel tool calls in one message and reasoning fields intact
        record(transcript, {"turn": turn, "message": msg, "finish_reason": choice.get("finish_reason"),
                            "usage": body["usage"]})
        content = msg.get("content") or ""
        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            if choice.get("finish_reason") == "length":
                return RunResult("truncated", content, turn, usage)
            if not content.strip():
                return RunResult("empty_reply", content, turn, usage)
            return RunResult("done", content, turn, usage)
        if content:
            log(f"\n🤖 {content}")
        for tool_call in tool_calls:
            function = tool_call["function"]
            log(f"🔧 Tool: {function['name']}({function['arguments']})")
            result = call_tool(function["name"], function["arguments"])
            log(f"   → {result[:500]}{'...' if len(result) > 500 else ''}")
            tool_message = {"role": "tool", "tool_call_id": tool_call["id"], "content": result}
            messages.append(tool_message)
            record(transcript, {"turn": turn, "message": tool_message})
    return RunResult("max_turns", "", MAX_TURNS, usage)


def main() -> int:
    prompt = " ".join(sys.argv[1:]).strip()
    if not prompt:
        log('Usage: agent.py "<task>"')
        return 2
    RUNS_DIR.mkdir(exist_ok=True)
    transcript = RUNS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}.jsonl"
    log(f"📝 Transcript: {transcript}")
    result = agent_loop(prompt, transcript)
    record(transcript, {"result": asdict(result)})
    u = result.usage
    log(f"\n{'✅' if result.status == 'done' else '❌'} {result.status} after {result.turns} turns | "
        f"tokens: prompt={u.prompt} cached={'n/a' if u.cached is None else u.cached} completion={u.completion}")
    if result.answer:
        print(result.answer)
    return 0 if result.status == "done" else 1


if __name__ == "__main__":
    sys.exit(main())
