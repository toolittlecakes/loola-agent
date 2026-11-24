"""Context compaction: when the next request might not fit, replace older history with a model-written summary.

Guarantee (assuming a token is at least one UTF-8 byte, true for BPE tokenizers):
- the size of the next request is bounded from above: exact server counts for what was already sent and
  generated (prompt + completion of the last request), UTF-8 bytes for what was not measured yet;
- a regular request is sent only if `bound + max(reply, instruction + summary) <= context_window`, so room for a
  later summary request is always reserved, whatever optional `compact_at` threshold is set;
- the summary request reuses the exact context of an earlier request (a measured size that passed this check)
  plus the instruction, so it fits by construction and shares that request's cached prefix. It keeps the same
  tools and tool_choice: `tool_choice: "none"` makes some providers drop the tools from the prompt, which
  changes the prefix and misses the cache (observed with OpenCode Go);
- right after compaction the bound is `head + (bound_before - prompt_at_cut)`: the kept tail is exactly what the
  old bound counted beyond the measured prefix that was summarized;
- if the compacted context still does not fit, compaction fails loudly instead of looping."""
import json
from dataclasses import dataclass

from .events import AssistantMessage, Compaction, Event, build_context, to_message

MESSAGE_OVERHEAD = 16  # tokens a chat template may add around one message (role markers, separators)

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
    compact_at: int | None = None  # optional earlier trigger; the hard limit applies regardless of it
    keep_recent_tokens: int | None = None  # recent history kept verbatim; default: a fifth of the trigger level
    summary_max_tokens: int = 4096

    @property
    def keep_recent(self) -> int:
        # Well below the trigger, so the compacted context does not trigger compaction again right away.
        return self.keep_recent_tokens if self.keep_recent_tokens is not None else \
            (self.compact_at or self.context_window) // 5

    def reserve(self, reply_max_tokens: int) -> int:
        instruction = _bytes(SUMMARY_INSTRUCTION) + MESSAGE_OVERHEAD
        return max(reply_max_tokens, instruction + self.summary_max_tokens)

    def fits(self, bound: int, reply_max_tokens: int) -> bool:
        return bound + self.reserve(reply_max_tokens) <= self.context_window

    def wants_compaction(self, bound: int, reply_max_tokens: int) -> bool:
        return not self.fits(bound, reply_max_tokens) or (self.compact_at is not None and bound > self.compact_at)


def context_bound(system_prompt: str, events: list[Event], tools: list[dict]) -> int:
    """Upper bound of the prompt tokens of the next request built from `events`."""
    anchor = next((i for i in range(len(events) - 1, -1, -1)
                   if isinstance(events[i], AssistantMessage | Compaction)), None)
    if anchor is None:
        return _bytes(tools) + sum(_message_bytes(m) for m in build_context(system_prompt, events))
    match events[anchor]:
        case AssistantMessage(usage=usage):
            known = usage.prompt + usage.completion
        case Compaction(tokens_after=tokens_after):
            known = tokens_after
    unmeasured = (to_message(e) for e in events[anchor + 1:])
    return known + sum(_message_bytes(m) for m in unmeasured if m is not None)


def bound_after_compaction(system_prompt: str, events: list[Event], tools: list[dict], compaction: Compaction) -> int:
    """`events` end with `compaction`; its summarized prefix had the exact size events[cut].usage.prompt."""
    head = build_context(system_prompt, events)[:2]  # system prompt + user messages with the summary
    tail = compaction.tokens_before - events[compaction.cut].usage.prompt
    return _bytes(tools) + sum(_message_bytes(m) for m in head) + tail


def choose_cut(events: list[Event], bound: int, keep_recent_tokens: int) -> int | None:
    """Earliest measured request boundary whose tail fits `keep_recent_tokens` (the latest one otherwise).
    A boundary is an assistant message after the latest compaction: the context it was generated from is
    exactly `build_context(events[:i])`, all tool calls before it are answered, and its size is known."""
    boundaries = [i for i in range(_after_last_compaction(events), len(events))
                  if isinstance(events[i], AssistantMessage)]
    if not boundaries:
        return None
    return next((i for i in boundaries if bound - events[i].usage.prompt <= keep_recent_tokens), boundaries[-1])


def summary_request(system_prompt: str, events: list[Event], cut: int) -> list[dict]:
    return build_context(system_prompt, events[:cut]) + [{"role": "user", "content": SUMMARY_INSTRUCTION}]


def _after_last_compaction(events: list[Event]) -> int:
    return next((i + 1 for i in range(len(events) - 1, -1, -1) if isinstance(events[i], Compaction)), 0)


def _message_bytes(message: dict) -> int:
    return _bytes(message) + MESSAGE_OVERHEAD


def _bytes(value: object) -> int:
    return len((value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)).encode())
