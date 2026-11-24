"""Agent loop. The session is an append-only list of events; the LLM context is a pure projection of it."""
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal

from .llm import LLM, Usage
from .tools import Toolbox

SYSTEM_PROMPT = """\
You are a coding agent. Your job is to help the user with programming tasks.

You have access to ONE tool: `bash` — which executes shell commands and returns stdout/stderr.

Workflow:
1. Plan what needs to be done.
2. Use `bash` to read files, run commands, write code, etc.
3. After gathering enough information or completing the task, give your final answer in natural language.
4. To finish, reply with a regular message (no tool call).

Be concise. Explain what you're doing before each command."""

INTERRUPTED = ("Error: this tool call was interrupted before it finished; it may have had partial side effects. "
               "Check the current state and re-run it if it is still needed.")


@dataclass(frozen=True)
class UserMessage:
    content: str


@dataclass(frozen=True)
class AssistantMessage:
    message: dict  # as returned by the LLM: parallel tool calls and reasoning fields stay intact
    finish_reason: str | None
    usage: Usage


@dataclass(frozen=True)
class ToolStarted:
    tool_call_id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class ToolResult:
    tool_call_id: str
    name: str
    content: str


@dataclass(frozen=True)
class RunFinished:
    status: Literal["done", "truncated", "empty_reply", "max_turns"]
    answer: str
    turns: int
    usage: Usage  # of this run only


Event = UserMessage | AssistantMessage | ToolStarted | ToolResult | RunFinished


def build_context(system_prompt: str, events: list[Event]) -> list[dict]:
    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    for event in events:
        match event:
            case UserMessage(content):
                messages.append({"role": "user", "content": content})
            case AssistantMessage(message):
                messages.append(message)
            case ToolResult(tool_call_id, _, content):
                messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": content})
    return messages


def unanswered_tool_calls(events: list[Event]) -> list[dict]:
    """Tool calls of the last assistant message that have no result, e.g. after a cancelled run."""
    for i in range(len(events) - 1, -1, -1):
        if isinstance(events[i], AssistantMessage):
            answered = {e.tool_call_id for e in events[i + 1:] if isinstance(e, ToolResult)}
            return [c for c in events[i].message.get("tool_calls") or [] if c["id"] not in answered]
    return []


class Agent:
    """One conversation. `send` runs the loop for a user message and streams events;
    the caller (CLI, TUI, web) decides how to render and persist them."""

    def __init__(self, llm: LLM, toolbox: Toolbox, system_prompt: str = SYSTEM_PROMPT, max_turns: int = 1000):
        self.llm, self.toolbox, self.system_prompt, self.max_turns = llm, toolbox, system_prompt, max_turns
        self.events: list[Event] = []

    async def send(self, content: str) -> AsyncIterator[Event]:
        # Close calls left open by a cancelled run: the protocol requires a result for every call, and the
        # model must know the command may have partially run. Re-running or dropping them silently would lie.
        for call in unanswered_tool_calls(self.events):
            yield self._append(ToolResult(call["id"], call["function"]["name"], INTERRUPTED))
        yield self._append(UserMessage(content))
        usage = Usage()
        for turn in range(1, self.max_turns + 1):
            completion = await self.llm.complete(build_context(self.system_prompt, self.events),
                                                 self.toolbox.schemas())
            usage += completion.usage
            yield self._append(AssistantMessage(completion.message, completion.finish_reason, completion.usage))
            text = completion.message.get("content") or ""
            tool_calls = completion.message.get("tool_calls") or []
            if not tool_calls:
                if completion.finish_reason == "length":
                    yield self._append(RunFinished("truncated", text, turn, usage))
                elif not text.strip():
                    yield self._append(RunFinished("empty_reply", text, turn, usage))
                else:
                    yield self._append(RunFinished("done", text, turn, usage))
                return
            for call in tool_calls:
                name, arguments = call["function"]["name"], call["function"]["arguments"]
                yield self._append(ToolStarted(call["id"], name, arguments))
                yield self._append(ToolResult(call["id"], name, await self.toolbox.call(name, arguments)))
        yield self._append(RunFinished("max_turns", "", self.max_turns, usage))

    def _append(self, event: Event) -> Event:
        self.events.append(event)
        return event
