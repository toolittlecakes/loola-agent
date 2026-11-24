"""Agent loop: streams events, keeps the session as an append-only event list (see events.py)."""
from collections.abc import AsyncIterator
from dataclasses import replace

from .compaction import (CompactionError, CompactionPolicy, bound_after_compaction, choose_cut, context_bound,
                         summary_request)
from .events import (INTERRUPTED, NOT_EXECUTED, AssistantMessage, Compaction, Event, RunFinished, SummaryDiscarded,
                     ToolResult, ToolStarted, UserMessage, build_context, unanswered_tool_calls)
from .llm import LLM, Completion, Usage
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
    the caller (CLI, TUI, web) decides how to render and persist them. One `send` at a time."""

    def __init__(self, llm: LLM, toolbox: Toolbox, system_prompt: str = SYSTEM_PROMPT, max_turns: int = 1000,
                 compaction: CompactionPolicy | None = None):
        self.llm, self.toolbox, self.system_prompt, self.max_turns = llm, toolbox, system_prompt, max_turns
        self.compaction = compaction
        self.events: list[Event] = []
        self._sending = False

    async def send(self, content: str) -> AsyncIterator[Event]:
        if self._sending:
            raise RuntimeError("send() is already running for this conversation")
        self._sending = True
        try:
            async for event in self._run(content):
                yield event
        finally:
            self._sending = False

    async def _run(self, content: str) -> AsyncIterator[Event]:
        # Close calls left open by a cancelled run: the protocol requires a result for every call, and the
        # model must know the command may have partially run. Re-running or dropping them silently would lie.
        for call in unanswered_tool_calls(self.events):
            yield self._append(ToolResult(call["id"], call["function"]["name"], INTERRUPTED))
        yield self._append(UserMessage(content))
        usage = Usage()
        for turn in range(1, self.max_turns + 1):
            if self.compaction:
                async for event in self._compact(self.compaction):
                    usage += event.usage
                    yield event
            completion = await self.llm.complete(build_context(self.system_prompt, self.events),
                                                 self.toolbox.schemas())
            usage += completion.usage
            yield self._append(AssistantMessage(completion.message, completion.finish_reason, completion.usage))
            self._check_window(completion)
            text = completion.message.get("content") or ""
            tool_calls = completion.message.get("tool_calls") or []
            if completion.finish_reason == "length":  # a cut-off reply may hold a partial batch: run none of it
                for call in tool_calls:
                    yield self._append(ToolResult(call["id"], call["function"]["name"], NOT_EXECUTED))
                yield self._append(RunFinished("truncated", text, turn, usage))
                return
            if not tool_calls:
                yield self._append(RunFinished("done" if text.strip() else "empty_reply", text, turn, usage))
                return
            for call in tool_calls:
                name, arguments = call["function"]["name"], call["function"]["arguments"]
                yield self._append(ToolStarted(call["id"], name, arguments))
                yield self._append(ToolResult(call["id"], name, await self.toolbox.call(name, arguments)))
        yield self._append(RunFinished("max_turns", "", self.max_turns, usage))

    def _check_window(self, completion: Completion) -> None:
        """The server's count is exact: make a wrong estimate (or an oversized first request) visible."""
        policy = self.compaction
        if policy and completion.usage.prompt + self.llm.max_tokens > policy.context_window:
            raise CompactionError(f"The request used {completion.usage.prompt} prompt tokens: with a "
                                  f"{self.llm.max_tokens}-token reply it exceeds the {policy.context_window}-token "
                                  f"window (the first request is too large, or the size estimate was low).")

    async def _compact(self, policy: CompactionPolicy) -> AsyncIterator[Compaction | SummaryDiscarded]:
        reply = self.llm.max_tokens
        bound = context_bound(self.events)
        if bound is None or not policy.wants_compaction(bound, reply):
            return
        cut = choose_cut(self.events, bound, policy.keep_recent) if policy.enabled else None
        if cut is None:  # compaction disabled, or nothing sent since the last one
            if policy.fits(bound, reply):
                return
            raise CompactionError(f"The next request may need ~{bound} tokens, more than the "
                                  f"{policy.context_window}-token window allows"
                                  f"{'' if policy.enabled else ' (compaction is disabled)'}.")
        # When the bulk is the most recent turn (e.g. one huge tool output), summarizing the rest cannot help:
        # even an empty summary would not shrink the context, so do not pay for one.
        empty = Compaction("", cut, bound, 0, Usage())
        if bound_after_compaction([*self.events, empty], empty) >= bound:
            if policy.fits(bound, reply):
                return
            raise CompactionError(f"The next request may need ~{bound} tokens and compaction cannot shrink it: "
                                  f"the most recent turn alone does not fit the {policy.context_window}-token window.")
        completion = await self.llm.complete(summary_request(self.system_prompt, self.events, cut),
                                             self.toolbox.schemas(), max_tokens=policy.summary_max_tokens)
        summary = completion.message.get("content") or ""
        compaction = Compaction(summary, cut, bound, 0, completion.usage)
        after = bound_after_compaction([*self.events, compaction], compaction)
        if completion.finish_reason != "stop" or completion.message.get("tool_calls") or not summary.strip():
            reason = f"no complete summary (finish_reason={completion.finish_reason!r})"
        elif after >= bound or not policy.fits(after, reply):
            reason = f"the summary does not shrink the context enough (~{bound} -> ~{after} tokens)"
        else:
            yield self._append(replace(compaction, tokens_after=after))
            return
        yield self._append(SummaryDiscarded(reason, completion.usage))  # paid for, so it stays in the transcript
        if not policy.fits(bound, reply):
            raise CompactionError(f"Compaction failed: {reason}, and the context does not fit the "
                                  f"{policy.context_window}-token window.")

    def _append[E: Event](self, event: E) -> E:
        self.events.append(event)
        return event
