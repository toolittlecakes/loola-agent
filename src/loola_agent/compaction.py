"""Context compaction: when the next request would not fit, replace older history with a model-written summary.

Sizing is practical, not exact (there is no tokenizer here, see README "Assumptions"):
- the server's prompt count of the last request is exact; everything added after it is counted in UTF-8 bytes plus
  a small per-message allowance. BPE tokens average 3-4 bytes, so this over-estimates in practice;
- the first request is not estimated, and after every response the agent checks the server's own count against
  the window, so a wrong estimate surfaces as an explicit error instead of a silent overflow.

A regular request is sent only if room for a later summary request stays reserved, whatever optional `compact_at`
is set. The summary request is the context of an earlier, measured request plus the instruction, so it fits and
shares that request's cached prefix. It keeps the same tools and tool_choice: `tool_choice: "none"` made OpenCode Go
drop the tools from the prompt, which changed the prefix and missed the cache."""
import json
from dataclasses import dataclass

from .events import AssistantMessage, Compaction, Event, UserMessage, build_context, to_message

MESSAGE_OVERHEAD = 16  # tokens a chat template may add around one message (role markers, tool-call wrapping)

SUMMARY_INSTRUCTION = """\
Your context is about to be compacted: everything above, except the user's own messages, will be replaced \
by the summary you write now. Write it so you can continue the task without the original messages:
- the goal and constraints as you understand them;
- what is done and verified (with the evidence), what is in progress, what is next;
- exact identifiers verbatim: file paths, commands, repositories, issue/PR numbers, SHAs, tool names, errors;
- approaches that failed and why, so you do not repeat them;
- skills you are following (name and SKILL.md path): re-read them before continuing their procedure.
Reply with the summary only, without tool calls."""


class CompactionError(RuntimeError):
    pass


@dataclass(frozen=True)
class CompactionPolicy:
    context_window: int
    compact_at: int | None = None  # optional earlier trigger; the window limit applies regardless of it
    keep_recent_tokens: int | None = None  # recent history kept verbatim; default: a fifth of the trigger level
    summary_max_tokens: int = 4096
    enabled: bool = True  # False: only enforce the window and fail when it is exceeded (the measurement baseline)

    @property
    def keep_recent(self) -> int:
        # Well below the trigger, so the compacted context does not trigger compaction again right away.
        return self.keep_recent_tokens if self.keep_recent_tokens is not None else \
            (self.compact_at or self.context_window) // 5

    def reserve(self, reply_max_tokens: int) -> int:
        if not self.enabled:
            return reply_max_tokens
        return max(reply_max_tokens, _bytes(SUMMARY_INSTRUCTION) + MESSAGE_OVERHEAD + self.summary_max_tokens)

    def fits(self, bound: int, reply_max_tokens: int) -> bool:
        return bound + self.reserve(reply_max_tokens) <= self.context_window

    def wants_compaction(self, bound: int, reply_max_tokens: int) -> bool:
        return not self.fits(bound, reply_max_tokens) or (self.compact_at is not None and bound > self.compact_at)


def context_bound(events: list[Event]) -> int | None:
    """Estimated prompt tokens of the next request; None before anything was measured (the first request)."""
    anchor = next((i for i in range(len(events) - 1, -1, -1)
                   if isinstance(events[i], AssistantMessage | Compaction)), None)
    if anchor is None:
        return None
    match events[anchor]:
        case AssistantMessage(usage=usage):  # its prompt is exact; the reply itself is counted like new messages
            known, unmeasured = usage.prompt, events[anchor:]
        case Compaction(tokens_after=tokens_after):
            known, unmeasured = tokens_after, events[anchor + 1:]
    return known + sum(_message_bytes(m) for e in unmeasured if (m := to_message(e)) is not None)


def bound_after_compaction(events: list[Event], compaction: Compaction) -> int:
    """`events` end with `compaction`. The first request's measured prompt covers the system prompt, tools and
    template; the summarized prefix had the exact size events[cut].usage.prompt, so the kept tail is the rest."""
    first = next(e for e in events if isinstance(e, AssistantMessage))
    head = build_context("", events)[1]  # the user's messages with the summary
    tail = compaction.tokens_before - events[compaction.cut].usage.prompt
    return first.usage.prompt + _message_bytes(head) + tail


def choose_cut(events: list[Event], bound: int, keep_recent_tokens: int) -> int | None:
    """Earliest measured request boundary whose tail fits `keep_recent_tokens` (the latest one otherwise).
    A boundary is an assistant message after the latest compaction: the context it was generated from is
    exactly `build_context(events[:i])`, all tool calls before it are answered, and its size is known."""
    start = next((i + 1 for i in range(len(events) - 1, -1, -1) if isinstance(events[i], Compaction)), 0)
    boundaries = [i for i in range(start, len(events)) if isinstance(events[i], AssistantMessage)]
    if not boundaries:
        return None
    return next((i for i in boundaries if bound - events[i].usage.prompt <= keep_recent_tokens), boundaries[-1])


def summary_request(system_prompt: str, events: list[Event], cut: int) -> list[dict]:
    return build_context(system_prompt, [*events[:cut], UserMessage(SUMMARY_INSTRUCTION)])


def _message_bytes(message: dict) -> int:
    return _bytes(message) + MESSAGE_OVERHEAD


def _bytes(value: object) -> int:
    return len((value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)).encode())
