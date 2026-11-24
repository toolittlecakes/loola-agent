"""Deferred tools: discovery via tool_search, execution via tool_call, a stable declared tool list."""
import json
from pathlib import Path

import pytest

from loola_agent import Agent, Completion, DummyTool, Toolbox, Usage, load_catalog

CATALOG = Path(__file__).parent.parent / "examples" / "github_tools.json"
ISSUE = DummyTool("issue_read", "Get information about a specific issue in a GitHub repository.",
                  {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"},
                                                    "issue_number": {"type": "number"}},
                   "required": ["owner", "repo", "issue_number"]})
STARS = DummyTool("list_stargazers", "List users who starred a repository.",
                  {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}}})


class Direct:
    name, description = "direct", "Always declared."
    parameters = {"type": "object", "properties": {}}

    async def run(self, args):
        return "direct ok"


def declared_names(toolbox):
    return [t["function"]["name"] for t in toolbox.schemas()]


def test_only_direct_and_meta_tools_are_declared():
    assert declared_names(Toolbox([Direct()], deferred=[ISSUE, STARS])) == ["direct", "tool_search", "tool_call"]
    assert declared_names(Toolbox([Direct()])) == ["direct"]


async def test_search_returns_matching_tools_with_schemas():
    result = json.loads(await Toolbox([Direct()], deferred=[ISSUE, STARS]).call("tool_search", '{"query": "issue"}'))
    assert [t["name"] for t in result] == ["issue_read"]
    assert result[0]["parameters"] == ISSUE.parameters


async def test_search_without_matches_says_so():
    result = await Toolbox([Direct()], deferred=[ISSUE]).call("tool_search", '{"query": "kubernetes"}')
    assert result.startswith("No tools match")


async def test_tool_call_runs_a_deferred_tool():
    args = {"name": "issue_read", "arguments": {"owner": "o", "repo": "r", "issue_number": 1}}
    result = json.loads(await Toolbox([Direct()], deferred=[ISSUE]).call("tool_call", json.dumps(args)))
    assert (result["tool"], result["arguments"]) == ("issue_read", args["arguments"])


@pytest.mark.parametrize("arguments, expected", [
    ({"owner": "o", "repo": "r"}, "'issue_number' is a required property"),
    ({"owner": "o", "repo": "r", "issue_number": "1"}, "at issue_number: '1' is not of type 'number'"),
    ({"owner": "o", "repo": "r", "issue_number": 1, "repo_name": "r"}, "'repo_name' was unexpected"),
])
async def test_tool_call_validates_against_the_deferred_tool_schema(arguments, expected):
    result = await Toolbox([Direct()], deferred=[ISSUE]).call(
        "tool_call", json.dumps({"name": "issue_read", "arguments": arguments}))
    assert result.startswith("Error: invalid arguments for 'issue_read'") and expected in result
    assert json.dumps(ISSUE.parameters) in result


async def test_unknown_tool_points_to_search():
    result = await Toolbox([Direct()], deferred=[ISSUE]).call("tool_call", '{"name": "nope", "arguments": {}}')
    assert result == "Error: unknown tool 'nope'. Use tool_search to find tools."


def test_duplicate_names_across_direct_and_deferred_fail_fast():
    with pytest.raises(ValueError, match="Duplicate"):
        Toolbox([ISSUE], deferred=[ISSUE])


def test_github_example_catalog_loads_and_its_schemas_are_valid():
    tools, hint = load_catalog(CATALOG)
    toolbox = Toolbox([Direct()], deferred=tools, deferred_hint=hint)  # validates every schema
    assert len(tools) == 91 and "pull_requests" in hint
    assert len(json.dumps(Toolbox([Direct(), *tools]).schemas())) > 20 * len(json.dumps(toolbox.schemas()))


async def test_agent_discovers_and_calls_a_deferred_tool_with_a_stable_tool_list():
    class RecordingLLM:
        def __init__(self, *script):
            self.script, self.tools, self.contexts = list(script), [], []

        async def complete(self, messages, tools):
            self.tools.append(tools)
            self.contexts.append(messages)
            return self.script.pop(0)

    def tool_turn(call_id, name, args):
        call = {"id": call_id, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}
        return Completion({"role": "assistant", "content": None, "tool_calls": [call]}, "tool_calls", Usage(1, 1))

    llm = RecordingLLM(
        tool_turn("s", "tool_search", {"query": "issue"}),
        tool_turn("c", "tool_call", {"name": "issue_read", "arguments": {"owner": "o", "repo": "r", "issue_number": 7}}),
        Completion({"role": "assistant", "content": "issue 7 read"}, "stop", Usage(1, 1)))
    events = [e async for e in Agent(llm, Toolbox([Direct()], deferred=[ISSUE, STARS])).send("read issue 7")]

    assert events[-1].status == "done"
    assert llm.tools[0] == llm.tools[1] == llm.tools[2]  # declared tools never change -> prefix cache stays valid
    assert '"issue_read"' in llm.contexts[1][-1]["content"]  # the schema arrived as a tool result
    assert json.loads(llm.contexts[2][-1]["content"])["arguments"]["issue_number"] == 7


async def test_search_returns_at_most_five_tools_and_has_no_limit_knob():
    tools, hint = load_catalog(CATALOG)
    toolbox = Toolbox([Direct()], deferred=tools, deferred_hint=hint)
    assert len(json.loads(await toolbox.call("tool_search", '{"query": "repository"}'))) == 5
    assert "'limit' was unexpected" in await toolbox.call("tool_search", '{"query": "repository", "limit": -1}')
