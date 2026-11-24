"""Toolbox validation and bash tool behavior."""
import asyncio, json, os, time

import pytest
from jsonschema.exceptions import SchemaError

from loola_agent import Bash, Toolbox


@pytest.fixture
async def bash():
    async with Bash(timeout=1) as tool:
        yield tool


async def run(bash, command):
    return await bash.run({"command": command})


@pytest.mark.parametrize("raw, expected", [
    ('{"command": "echo hi"', "not valid JSON"),
    ("", "not valid JSON"),
    ('["ls", "-la"]', "at <root>: ['ls', '-la'] is not of type 'object'"),
    ('{"command": ["ls", "-la"]}', "at command: ['ls', '-la'] is not of type 'string'"),
    ("{}", "'command' is a required property"),
])
async def test_invalid_arguments_are_explained_to_the_model(bash, raw, expected):
    result = await Toolbox([bash]).call("bash", raw)
    assert result.startswith("Error:") and expected in result


async def test_schema_error_includes_the_expected_schema(bash):
    result = await Toolbox([bash]).call("bash", "{}")
    assert json.dumps(bash.parameters) in result


async def test_unknown_tool_lists_available_tools(bash):
    assert await Toolbox([bash]).call("python", "{}") == "Error: unknown tool 'python'. Available tools: bash."


async def test_valid_call_is_dispatched(bash):
    assert await Toolbox([bash]).call("bash", '{"command": "echo hi"}') == "Exit code: 0\nhi\n"


def test_invalid_tool_schema_fails_fast(bash):
    class Broken:
        name, description, parameters = "broken", "", {"type": "nope"}

    with pytest.raises(SchemaError):
        Toolbox([Broken()])


async def test_huge_output_is_truncated_head_and_tail(bash):
    output = await run(bash, "seq 1 300000")
    assert len(output) < bash.max_output + 200
    assert "\n1\n2\n" in output and "300000" in output and "bytes truncated" in output


async def test_llm_secrets_are_not_visible_to_commands(bash, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-secret")
    assert "sk-secret" not in await run(bash, "env")


async def test_stdin_is_closed(bash):
    assert (await run(bash, "cat")).startswith("Exit code: 0")


async def test_background_job_does_not_block(bash):
    started = time.monotonic()
    assert "started" in await run(bash, "sleep 5 > /dev/null 2>&1 & echo started")
    assert time.monotonic() - started < 1


async def test_timeout_kills_process_group_and_keeps_partial_output(bash, tmp_path):
    marker = tmp_path / "after"
    output = await run(bash, f"echo test_1 PASSED; (sleep 1.5; touch {marker}) & sleep 30")
    assert "timed out" in output and "test_1 PASSED" in output
    await asyncio.sleep(1)
    assert not marker.exists()


async def test_background_jobs_are_killed_on_exit(tmp_path):
    marker = tmp_path / "after"
    async with Bash() as bash:
        await run(bash, f"(sleep 1; touch {marker}) > /dev/null 2>&1 &")
    await asyncio.sleep(1.5)
    assert not marker.exists()


async def test_invalid_utf8_output_keeps_exit_code_and_side_effects(bash, tmp_path):
    output = await run(bash, f"echo created > {tmp_path}/marker; printf '\\377\\376'; exit 3")
    assert output.startswith("Exit code: 3") and (tmp_path / "marker").exists()


async def test_cancelled_command_kills_its_process_group(bash, tmp_path):
    marker = tmp_path / "after"
    task = asyncio.create_task(run(bash, f"(sleep 0.5; touch {marker}) & sleep 30"))
    await asyncio.sleep(0.2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    await asyncio.sleep(0.8)
    assert not marker.exists()
