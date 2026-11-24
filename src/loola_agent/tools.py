"""Tools: a minimal protocol, a toolbox that validates calls against JSON Schema, and the bash tool."""
import asyncio, json, os, signal, subprocess, tempfile
from typing import IO, Protocol, Self

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match


class Tool(Protocol):
    name: str
    description: str
    parameters: dict  # JSON Schema of the arguments object

    async def run(self, args: dict) -> str: ...


class Toolbox:
    """Dispatches model tool calls. Mistakes of the model come back as text so it can fix the call itself."""

    def __init__(self, tools: list[Tool]):
        self._tools = {tool.name: tool for tool in tools}
        if len(self._tools) != len(tools):
            raise ValueError("Duplicate tool names")
        self._validators = {}
        for tool in tools:
            Draft202012Validator.check_schema(tool.parameters)
            self._validators[tool.name] = Draft202012Validator(tool.parameters)

    def schemas(self) -> list[dict]:
        return [{"type": "function", "function": {"name": t.name, "description": t.description,
                                                  "parameters": t.parameters}} for t in self._tools.values()]

    async def call(self, name: str, raw_arguments: str) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: unknown tool '{name}'. Available tools: {', '.join(self._tools)}."
        try:
            args = json.loads(raw_arguments)
        except json.JSONDecodeError as e:
            return f"Error: arguments for '{name}' are not valid JSON ({e}). Re-issue the call with a JSON object."
        if error := best_match(self._validators[name].iter_errors(args)):
            where = "/".join(map(str, error.absolute_path)) or "<root>"
            return (f"Error: invalid arguments for '{name}' at {where}: {error.message}. "
                    f"Expected schema: {json.dumps(tool.parameters)}")
        return await tool.run(args)


class Bash:
    """Runs non-interactive shell commands. Use as an async context manager:
    on exit it kills background processes the commands left behind."""

    name = "bash"
    parameters = {"type": "object",
                  "properties": {"command": {"type": "string", "description": "The bash command to execute."}},
                  "required": ["command"]}

    def __init__(self, timeout: float = 120, max_output: int = 10_000):
        self.timeout, self.max_output = timeout, max_output
        self.description = (
            f"Execute a shell command and return its exit code and combined stdout/stderr (long output is truncated). "
            f"stdin is closed, so commands must not wait for input. Timeout: {timeout:g}s. "
            f"Run long-lived processes (servers, watchers) in the background with output redirected to a file, "
            f"e.g. `cmd > /tmp/server.log 2>&1 &`, then read the file; they are killed when the agent exits.")
        self._process_groups: set[int] = set()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        for pgid in self._process_groups:
            _kill_group(pgid)
        self._process_groups.clear()

    async def run(self, args: dict) -> str:
        # Output goes to a file, not a pipe: background jobs don't block the call and partial output
        # survives a timeout. Each command gets its own process group, so it can be killed as a whole.
        env = {k: v for k, v in os.environ.items() if not k.startswith("LLM_")}
        with tempfile.TemporaryFile() as out:
            proc = await asyncio.create_subprocess_shell(
                args["command"], stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, env=env,
                start_new_session=True)
            self._process_groups.add(proc.pid)
            try:
                status = f"Exit code: {await asyncio.wait_for(proc.wait(), self.timeout)}"
            except TimeoutError:
                _kill_group(proc.pid)
                await proc.wait()
                status = f"Error: command timed out after {self.timeout:g}s and was killed. Output so far:"
            except asyncio.CancelledError:
                _kill_group(proc.pid)
                raise
            if not _group_alive(proc.pid):  # nothing left in background: forget it to avoid PID reuse surprises
                self._process_groups.discard(proc.pid)
            return f"{status}\n{self._read_head_tail(out)}"

    def _read_head_tail(self, f: IO[bytes]) -> str:
        size = f.seek(0, os.SEEK_END)
        f.seek(0)
        if size <= self.max_output:
            return f.read().decode(errors="replace")
        half = self.max_output // 2
        head = f.read(half)
        f.seek(-half, os.SEEK_END)
        tail = f.read()
        marker = f"\n[... {size - 2 * half} bytes truncated; use head/tail/grep/sed -n to read specific parts ...]\n"
        return head.decode(errors="replace") + marker + tail.decode(errors="replace")


def _group_alive(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    return True


def _kill_group(pgid: int) -> None:
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:  # the whole group has already exited
        pass
