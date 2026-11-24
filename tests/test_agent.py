"""Agent loop behavior against a scripted fake LLM."""
import asyncio, json

import pytest

from loola_agent.events import INTERRUPTED, unanswered_tool_calls
from loola_agent import (Agent, AssistantMessage, Completion, RunFinished, ToolResult, ToolStarted, Toolbox, Usage,
                         UserMessage, build_context)


class FakeLLM:
    def __init__(self, *script: Completion):
        self.script, self.calls = list(script), []

    async def complete(self, messages, tools):
        self.calls.append(messages)
        return self.script.pop(0)


class Echo:
    name, description = "echo", "Echo the text back."
    parameters = {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}

    async def run(self, args):
        return args["text"]


def reply(content=None, tool_calls=None, finish="stop", **extra):
    message = {"role": "assistant", "content": content, **extra}
    if tool_calls:
        message["tool_calls"] = tool_calls
    return Completion(message, finish, Usage(10, 2, 8))


def call(call_id, text):
    return {"id": call_id, "type": "function", "function": {"name": "echo", "arguments": json.dumps({"text": text})}}


async def run(llm, content="do the task", agent=None):
    agent = agent or Agent(llm, Toolbox([Echo()]))
    return agent, [event async for event in agent.send(content)]


async def test_parallel_tool_calls_stay_in_one_assistant_message_with_reasoning():
    llm = FakeLLM(reply("checking", [call("a", "A"), call("b", "B")], "tool_calls", reasoning_content="plan"),
                  reply("done"))
    _, events = await run(llm)
    second_context = llm.calls[1]
    assert [m["role"] for m in second_context] == ["system", "user", "assistant", "tool", "tool"]
    assert second_context[2]["reasoning_content"] == "plan"
    assert [(m["tool_call_id"], m["content"]) for m in second_context[3:]] == [("a", "A"), ("b", "B")]
    assert [type(e) for e in events] == [UserMessage, AssistantMessage, ToolStarted, ToolResult, ToolStarted,
                                         ToolResult, AssistantMessage, RunFinished]


async def test_tool_errors_go_back_to_model_and_run_continues():
    bad = {"id": "a", "type": "function", "function": {"name": "echo", "arguments": '{"text": 1}'}}
    llm = FakeLLM(reply(None, [bad], "tool_calls"), reply("done"))
    _, events = await run(llm)
    assert events[-1].status == "done"
    assert llm.calls[1][-1]["content"].startswith("Error: invalid arguments for 'echo'")


async def test_truncated_final_answer_is_a_failure():
    _, events = await run(FakeLLM(reply("Here is the plan:\n1. Move", finish="length")))
    assert events[-1].status == "truncated"


async def test_empty_reply_is_a_failure():
    _, events = await run(FakeLLM(reply("", reasoning_content="I should run the tests...")))
    assert events[-1].status == "empty_reply"


async def test_max_turns_is_a_failure():
    llm = FakeLLM(*[reply(None, [call(str(i), "x")], "tool_calls") for i in range(3)])
    agent = Agent(llm, Toolbox([Echo()]), max_turns=3)
    _, events = await run(llm, agent=agent)
    assert (events[-1].status, events[-1].turns) == ("max_turns", 3)


async def test_usage_is_accumulated_per_run():
    _, events = await run(FakeLLM(reply(None, [call("a", "x")], "tool_calls"), reply("done")))
    assert events[-1].usage == Usage(20, 4, 16)


async def test_follow_up_message_continues_the_same_conversation():
    llm = FakeLLM(reply("first"), reply("second"))
    agent, _ = await run(llm, "one")
    _, events = await run(llm, "two", agent)
    assert [m["role"] for m in llm.calls[1]] == ["system", "user", "assistant", "user"]
    assert events[-1].usage == Usage(10, 2, 8)


def test_context_is_a_projection_of_events():
    events = [UserMessage("hi"), AssistantMessage({"role": "assistant", "content": "x"}, "stop", Usage()),
              RunFinished("done", "x", 1, Usage())]
    assert build_context("sys", events) == [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"},
                                           {"role": "assistant", "content": "x"}]


class Hang:
    name, description = "hang", "Never finishes."
    parameters = {"type": "object", "properties": {}}

    async def run(self, args):
        await asyncio.Event().wait()


async def test_cancelled_tool_call_is_closed_as_interrupted_on_next_send():
    hang = {"id": "h", "type": "function", "function": {"name": "hang", "arguments": "{}"}}
    llm = FakeLLM(reply(None, [hang, call("a", "x")], "tool_calls"), reply("ok"))
    agent = Agent(llm, Toolbox([Echo(), Hang()]))
    started = asyncio.Event()

    async def consume():
        async for event in agent.send("start"):
            if isinstance(event, ToolStarted):
                started.set()

    task = asyncio.create_task(consume())
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    _, events = await run(llm, "continue", agent)
    context = llm.calls[1]
    assert [m["role"] for m in context] == ["system", "user", "assistant", "tool", "tool", "user"]
    assert [m["tool_call_id"] for m in context[3:5]] == ["h", "a"]
    assert all(m["content"] == INTERRUPTED for m in context[3:5])
    assert unanswered_tool_calls(agent.events) == []


async def test_tool_calls_in_a_truncated_reply_are_not_executed():
    executed = []

    class Spy(Echo):
        async def run(self, args):
            executed.append(args)
            return "ran"

    llm = FakeLLM(reply("partial", [call("a", "x")], "length"), reply("ok"))
    agent = Agent(llm, Toolbox([Spy()]))
    _, events = await run(llm, agent=agent)
    assert executed == [] and events[-1].status == "truncated"
    _, events = await run(llm, "continue", agent)  # history stays valid: the call got a result
    assert [m["role"] for m in llm.calls[1]] == ["system", "user", "assistant", "tool", "user"]
    assert llm.calls[1][3]["content"].startswith("Error: not executed")


async def test_a_second_concurrent_send_is_rejected():
    hang = {"id": "h", "type": "function", "function": {"name": "hang", "arguments": "{}"}}
    agent = Agent(FakeLLM(reply(None, [hang], "tool_calls")), Toolbox([Echo(), Hang()]))
    first = agent.send("one")
    async for event in first:
        if isinstance(event, ToolStarted):
            break
    with pytest.raises(RuntimeError, match="already running"):
        await anext(agent.send("two"))
    await first.aclose()
    assert not agent._sending


async def test_a_send_cancelled_before_the_reply_leaves_no_two_user_turns_in_a_row():
    llm = FakeLLM(reply("ok"))
    agent = Agent(llm, Toolbox([Echo()]))
    first = agent.send("one")
    await anext(first)  # UserMessage recorded, then abandoned
    await first.aclose()
    await run(llm, "two", agent)
    assert llm.calls[0][1:] == [{"role": "user", "content": "one\n\ntwo"}]
