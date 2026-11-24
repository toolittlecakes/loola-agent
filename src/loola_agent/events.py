"""Session events. The session is an append-only list of them; the LLM context is a pure projection of it."""
from dataclasses import dataclass
from typing import Literal

from .llm import Usage

INTERRUPTED = ("Error: this tool call was interrupted before it finished; it may have had partial side effects. "
               "Check the current state and re-run it if it is still needed.")
NOT_EXECUTED = "Error: not executed: your reply was cut off by the token limit. Issue the call again if needed."
SUMMARY_HEADER = "[Earlier work in this conversation was compacted. Summary of it:]\n"


@dataclass(frozen=True)
class UserMessage:
    content: str


@dataclass(frozen=True)
class AssistantMessage:
    message: dict  # as returned by the LLM: parallel tool calls and reasoning fields stay intact
    finish_reason: str | None
    usage: Usage  # usage.prompt is the exact size of the context this message was generated from


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
class Compaction:
    summary: str
    cut: int  # index of the first event kept verbatim (always an AssistantMessage)
    tokens_before: int  # upper bound of the context that triggered compaction
    tokens_after: int  # upper bound of the context right after it
    usage: Usage  # of the summary request


@dataclass(frozen=True)
class SummaryDiscarded:
    reason: str
    usage: Usage  # a paid summary request whose result was not applied


@dataclass(frozen=True)
class RunFinished:
    status: Literal["done", "truncated", "empty_reply", "max_turns"]
    answer: str
    turns: int
    usage: Usage  # of this run only, summary requests included


Event = UserMessage | AssistantMessage | ToolStarted | ToolResult | Compaction | SummaryDiscarded | RunFinished


def to_message(event: Event) -> dict | None:
    match event:
        case UserMessage(content):
            return {"role": "user", "content": content}
        case AssistantMessage(message):
            return message
        case ToolResult(tool_call_id, _, content):
            return {"role": "tool", "tool_call_id": tool_call_id, "content": content}
    return None


def build_context(system_prompt: str, events: list[Event]) -> list[dict]:
    """System prompt, then either all events, or after a compaction: the user's own messages verbatim plus the
    latest summary (it already covers earlier ones), followed by the events kept verbatim. Adjacent user messages
    are merged into one: strict chat templates reject two user turns in a row (e.g. after a cancelled send)."""
    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    start = 0
    compactions = [e for e in events if isinstance(e, Compaction)]
    if compactions:
        last = compactions[-1]
        for event in events[:last.cut]:
            if isinstance(event, UserMessage):
                _add(messages, {"role": "user", "content": event.content})
        _add(messages, {"role": "user", "content": SUMMARY_HEADER + last.summary})
        start = last.cut
    for event in events[start:]:
        if (message := to_message(event)) is not None:
            _add(messages, message)
    return messages


def _add(messages: list[dict], message: dict) -> None:
    if message["role"] == "user" and messages[-1]["role"] == "user":
        messages[-1] = {"role": "user", "content": f"{messages[-1]['content']}\n\n{message['content']}"}
    else:
        messages.append(message)


def unanswered_tool_calls(events: list[Event]) -> list[dict]:
    """Tool calls of the last assistant message that have no result, e.g. after a cancelled run."""
    for i in range(len(events) - 1, -1, -1):
        if isinstance(events[i], AssistantMessage):
            answered = {e.tool_call_id for e in events[i + 1:] if isinstance(e, ToolResult)}
            return [c for c in events[i].message.get("tool_calls") or [] if c["id"] not in answered]
    return []
