"""Agent loop: streams events, keeps the session as an append-only event list (see events.py)."""
from collections.abc import AsyncIterator
from dataclasses import replace

from .compaction import (CompactionError, CompactionPolicy, bound_after_compaction, choose_cut, context_bound,
                         summary_request)
from .events import (INTERRUPTED, AssistantMessage, Compaction, Event, RunFinished, ToolResult, ToolStarted,
                     UserMessage, build_context, unanswered_tool_calls)
from .llm import LLM, Usage
from .tools import Toolbox

SYSTEM_PROMPT = """\
You are a coding agent. Your job is to help the user with programming tasks.

Workflow:
1. Plan what needs to be done.
2. Use the tools to read files, run commands, write code, etc.
3. After gathering enough information or completing the task, give your final answer in natural language.
4. To finish, reply with a regular message (no tool call).

Prefer a dedicated tool over a shell command for the same action (e.g. a GitHub tool over `gh` or `curl`). \
If no listed tool fits and `tool_search` is available, search for one first; use bash only when nothing fits.

Be concise. Explain what you're doing before each command."""


class Agent:
    """One conversation. `send` runs the loop for a user message and streams events;
    the caller (CLI, TUI, web) decides how to render and persist them."""

    def __init__(self, llm: LLM, toolbox: Toolbox, system_prompt: str = SYSTEM_PROMPT, max_turns: int = 1000,
                 compaction: CompactionPolicy | None = None):
        self.llm, self.toolbox, self.system_prompt, self.max_turns = llm, toolbox, system_prompt, max_turns
        self.compaction = compaction
        self.events: list[Event] = []
        if compaction and not compaction.fits(context_bound(system_prompt, [], toolbox.schemas()), llm.max_tokens):
            raise ValueError("context_window is too small for the system prompt, tools and reserved replies")

    async def send(self, content: str) -> AsyncIterator[Event]:
        # Close calls left open by a cancelled run: the protocol requires a result for every call, and the
        # model must know the command may have partially run. Re-running or dropping them silently would lie.
        for call in unanswered_tool_calls(self.events):
            yield self._append(ToolResult(call["id"], call["function"]["name"], INTERRUPTED))
        yield self._append(UserMessage(content))
        usage = Usage()
        for turn in range(1, self.max_turns + 1):
            if self.compaction and (compaction := await self._compact_if_needed(self.compaction)):
                usage += compaction.usage
                yield compaction
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

    async def _compact_if_needed(self, policy: CompactionPolicy) -> Compaction | None:
        tools, reply = self.toolbox.schemas(), self.llm.max_tokens
        bound = context_bound(self.system_prompt, self.events, tools)
        if not policy.wants_compaction(bound, reply):
            return None
        cut = choose_cut(self.events, bound, policy.keep_recent)
        if cut is None:  # nothing sent since the last compaction: only the optional threshold can be over
            if policy.fits(bound, reply):
                return None
            raise CompactionError(f"The next request may need {bound} tokens plus a reserved reply, which exceeds "
                                  f"the {policy.context_window}-token window, and there is no history to compact.")
        # When the bulk is the most recent turn (e.g. one huge tool output), summarizing the rest cannot help:
        # skip the paid summary request if the context still fits, fail now if it does not.
        empty = Compaction("", cut, bound, 0, Usage())
        expected = bound_after_compaction(self.system_prompt, [*self.events, empty], tools, empty) \
            + policy.summary_max_tokens
        if expected >= bound:
            if policy.fits(bound, reply):
                return None
            raise CompactionError(f"The next request may need {bound} tokens, and compaction cannot shrink it: "
                                  f"the most recent turn alone does not fit the {policy.context_window}-token window.")
        completion = await self.llm.complete(summary_request(self.system_prompt, self.events, cut), tools,
                                             max_tokens=policy.summary_max_tokens)
        summary = completion.message.get("content") or ""
        if completion.finish_reason != "stop" or completion.message.get("tool_calls") or not summary.strip():
            raise CompactionError(f"The summary request did not return a complete summary "
                                  f"(finish_reason={completion.finish_reason!r}).")
        compaction = Compaction(summary, cut, bound, 0, completion.usage)
        after = bound_after_compaction(self.system_prompt, [*self.events, compaction], tools, compaction)
        if not policy.fits(after, reply):
            raise CompactionError(f"Even after compaction the context may need {after} tokens: the user's messages "
                                  f"and the most recent turn do not fit the {policy.context_window}-token window.")
        self._append(replace(compaction, tokens_after=after))
        return self.events[-1]

    def _append(self, event: Event) -> Event:
        self.events.append(event)
        return event
