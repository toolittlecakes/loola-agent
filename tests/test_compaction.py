"""Compaction: every request (summary requests included) stays within the window, whatever the threshold."""
import json

import pytest

from loola_agent import (Agent, AssistantMessage, Compaction, CompactionError, CompactionPolicy, Completion,
                         SummaryDiscarded, Toolbox, Usage, UserMessage, build_context)
from loola_agent.compaction import SUMMARY_INSTRUCTION, context_bound
from loola_agent.events import SUMMARY_HEADER


class Big:
    name, description = "big", "Returns a large output."
    parameters = {"type": "object", "properties": {}}

    def __init__(self, size=3000):
        self.size = size

    async def run(self, args):
        return "x" * self.size


class SimulatedLLM:
    """A server stand-in: counts `bytes_per_token` bytes as one token (1 is the worst case the bound allows),
    rejects any request that would overflow the window, makes `turns` tool calls and then answers;
    summary requests (ending with the summary instruction) get a summary. Completion counts are the real message sizes."""

    def __init__(self, window, turns, max_tokens=500, summary=None, bytes_per_token=3):
        self.window, self.turns, self.max_tokens, self.bpt = window, turns, max_tokens, bytes_per_token
        self.summary = summary or Completion({"role": "assistant", "content": "SUMMARY " + "s" * 300}, "stop",
                                             Usage(0, 0))
        self.requests: list[dict] = []

    def tokens(self, value) -> int:
        return len(json.dumps(value).encode()) // self.bpt + 1

    async def complete(self, messages, tools, *, max_tokens=None):
        prompt = self.tokens([messages, tools])
        assert prompt + (max_tokens or self.max_tokens) <= self.window, f"overflow: {prompt} prompt tokens"
        is_summary = messages[-1]["role"] == "user" and messages[-1]["content"].endswith(SUMMARY_INSTRUCTION)
        self.requests.append({"messages": messages, "tools": tools, "summary": is_summary, "prompt": prompt})
        if is_summary:
            message, finish = self.summary.message, self.summary.finish_reason
        elif (turn := sum(not r["summary"] for r in self.requests)) <= self.turns:
            call = {"id": f"c{turn}", "type": "function", "function": {"name": "big", "arguments": "{}"}}
            message, finish = {"role": "assistant", "content": f"step {turn}", "tool_calls": [call]}, "tool_calls"
        else:
            message, finish = {"role": "assistant", "content": "all done"}, "stop"
        return Completion(message, finish, Usage(prompt, self.tokens(message)))


async def run(agent, task="long task"):
    return [e async for e in agent.send(task)]


@pytest.mark.parametrize("bytes_per_token", [1, 3])
@pytest.mark.parametrize("keep_recent", [0, 3_000])
@pytest.mark.parametrize("output_size", [800, 4_000])
@pytest.mark.parametrize("compact_at", [None, 4_000, 12_000, 19_999, 10**9])
async def test_requests_never_overflow_whatever_the_threshold(compact_at, output_size, keep_recent, bytes_per_token):
    llm = SimulatedLLM(window=20_000, turns=40, bytes_per_token=bytes_per_token)
    policy = CompactionPolicy(20_000, compact_at, keep_recent_tokens=keep_recent, summary_max_tokens=1_000)
    events = await run(Agent(llm, Toolbox([Big(output_size)]), compaction=policy))
    assert events[-1].status == "done"
    compactions = [e for e in events if isinstance(e, Compaction)]
    if 40 * output_size // bytes_per_token > 20_000:  # the outputs alone exceed the window
        assert compactions
    assert all(c.tokens_after < c.tokens_before for c in compactions)  # no paid summary without progress


async def test_lower_threshold_compacts_earlier_and_more_often():
    counts = []
    for compact_at in (None, 6_000):
        llm = SimulatedLLM(window=20_000, turns=40)
        events = await run(Agent(llm, Toolbox([Big()]), compaction=CompactionPolicy(20_000, compact_at, 3_000, 1_000)))
        counts.append(sum(isinstance(e, Compaction) for e in events))
    assert counts[1] > counts[0] > 0


async def test_summary_request_reuses_an_earlier_request_prefix_and_tools():
    llm = SimulatedLLM(window=20_000, turns=10)
    await run(Agent(llm, Toolbox([Big()]), compaction=CompactionPolicy(20_000, 8_000, 3_000, 1_000)))
    summary = next(r for r in llm.requests if r["summary"])
    earlier = [r for r in llm.requests if not r["summary"]]
    assert any(r["messages"] == summary["messages"][:-1] for r in earlier)  # same prefix -> KV cache hit
    assert summary["tools"] == earlier[0]["tools"]


async def test_context_after_compaction_is_user_messages_with_summary_then_recent_turns():
    llm = SimulatedLLM(window=20_000, turns=10)
    agent = Agent(llm, Toolbox([Big()]), compaction=CompactionPolicy(20_000, 8_000, 3_000, 1_000))
    events = await run(agent, "the original task")
    compaction = next(e for e in events if isinstance(e, Compaction))
    context = build_context(agent.system_prompt, agent.events[:agent.events.index(compaction) + 1])
    assert [m["role"] for m in context[:3]] == ["system", "user", "assistant"]
    assert context[1]["content"] == "the original task\n\n" + SUMMARY_HEADER + "SUMMARY " + "s" * 300
    assert context[2] is agent.events[compaction.cut].message
    assert compaction.tokens_after < compaction.tokens_before


async def test_summary_cost_is_counted_in_run_usage():
    llm = SimulatedLLM(window=20_000, turns=10)
    events = await run(Agent(llm, Toolbox([Big()]), compaction=CompactionPolicy(20_000, 8_000, 3_000, 1_000)))
    assert events[-1].usage.prompt == sum(r["prompt"] for r in llm.requests)


async def test_a_turn_too_large_to_keep_fails_loudly():
    llm = SimulatedLLM(window=20_000, turns=3)
    agent = Agent(llm, Toolbox([Big(size=40_000)]), compaction=CompactionPolicy(20_000, None, 3_000, 1_000))
    with pytest.raises(CompactionError, match="most recent turn alone does not fit"):
        await run(agent)


async def test_truncated_summary_fails_loudly_when_the_context_does_not_fit_and_is_recorded():
    truncated = Completion({"role": "assistant", "content": "SUMMARY partial"}, "length", Usage(0, 1000))
    llm = SimulatedLLM(window=20_000, turns=40, summary=truncated)
    agent = Agent(llm, Toolbox([Big()]), compaction=CompactionPolicy(20_000, None, 3_000, 1_000))
    seen = []
    with pytest.raises(CompactionError, match="complete summary"):
        async for event in agent.send("long task"):
            seen.append(event)
    assert isinstance(seen[-1], SummaryDiscarded)  # the paid request reaches the transcript before the error


def test_bound_is_the_last_measured_prompt_plus_bytes_of_everything_after_it():
    reply = {"role": "assistant", "content": "x"}
    events = [UserMessage("task"), AssistantMessage(reply, "stop", Usage(1_000, 50)), UserMessage("more")]
    added = [reply, {"role": "user", "content": "more"}]
    assert context_bound(events) == 1_000 + sum(len(json.dumps(m).encode()) + 16 for m in added)
    assert context_bound([UserMessage("task")]) is None  # the first request is measured by the server


class OneShotLLM:
    max_tokens = 500

    def __init__(self, prompt):
        self.prompt = prompt

    async def complete(self, messages, tools, *, max_tokens=None):
        return Completion({"role": "assistant", "content": "done"}, "stop", Usage(self.prompt, 1))


async def test_a_request_the_server_measured_over_the_window_fails_loudly():
    agent = Agent(OneShotLLM(prompt=19_600), Toolbox([Big()]), compaction=CompactionPolicy(20_000))
    with pytest.raises(CompactionError, match="exceeds the 20000-token window"):
        await run(agent)


async def test_baseline_without_compaction_fails_when_the_window_is_exceeded():
    llm = SimulatedLLM(window=20_000, turns=40)
    agent = Agent(llm, Toolbox([Big()]), compaction=CompactionPolicy(20_000, enabled=False))
    with pytest.raises(CompactionError, match="compaction is disabled"):
        await run(agent)
    assert not any(r["summary"] for r in llm.requests)


async def test_a_summary_that_does_not_shrink_the_context_is_discarded_but_paid_for():
    verbose = Completion({"role": "assistant", "content": "SUMMARY " + "s" * 20_000}, "stop", Usage(0, 0))
    llm = SimulatedLLM(window=40_000, turns=6, summary=verbose)
    agent = Agent(llm, Toolbox([Big()]), compaction=CompactionPolicy(40_000, 3_000, 0, 1_000))
    events = await run(agent)
    discarded = [e for e in events if isinstance(e, SummaryDiscarded)]
    assert discarded and not any(isinstance(e, Compaction) for e in events)
    assert events[-1].status == "done"
    assert events[-1].usage.prompt == sum(r["prompt"] for r in llm.requests)  # discarded summaries counted


async def test_tool_call_instead_of_summary_fails_loudly():
    call = {"id": "x", "type": "function", "function": {"name": "big", "arguments": "{}"}}
    not_summary = Completion({"role": "assistant", "content": None, "tool_calls": [call]}, "tool_calls", Usage(0, 0))
    llm = SimulatedLLM(window=20_000, turns=40, summary=not_summary)
    agent = Agent(llm, Toolbox([Big()]), compaction=CompactionPolicy(20_000, None, 3_000, 1_000))
    with pytest.raises(CompactionError, match="complete summary"):
        await run(agent)


async def test_soft_threshold_skips_a_summary_that_cannot_shrink_the_context():
    llm = SimulatedLLM(window=60_000, turns=1)  # the only bulk is the most recent turn
    agent = Agent(llm, Toolbox([Big(size=30_000)]), compaction=CompactionPolicy(60_000, 1_000, 0, 1_000))
    events = await run(agent)
    assert events[-1].status == "done"
    assert not any(r["summary"] for r in llm.requests)
