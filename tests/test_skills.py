"""Skills: SKILL.md parsing, the system prompt section, and on-demand loading through bash with a stable prefix."""
import json
from pathlib import Path

import pytest

from loola_agent import Agent, Bash, Completion, Toolbox, Usage
from loola_agent.agent import SYSTEM_PROMPT
from loola_agent import load_skills, skills_prompt

SKILLS = Path(__file__).parent.parent / "skills"


class FakeLLM:
    def __init__(self, *script: Completion):
        self.script, self.calls = list(script), []

    async def complete(self, messages, tools):
        self.calls.append((messages, tools))
        return self.script.pop(0)


def reply(content=None, command=None):
    message = {"role": "assistant", "content": content}
    if command:
        message["tool_calls"] = [{"id": "c1", "type": "function",
                                  "function": {"name": "bash", "arguments": json.dumps({"command": command})}}]
    return Completion(message, "tool_calls" if command else "stop", Usage(10, 2, 8))


def write_skill(root: Path, dirname: str, text: str) -> None:
    (root / dirname).mkdir()
    (root / dirname / "SKILL.md").write_text(text)


def test_demo_skills_are_loaded_sorted_without_frontmatter_in_body():
    skills = load_skills(SKILLS)
    assert [s.name for s in skills] == ["ci-failure-triage", "fix-github-issue", "review-pull-request"]
    assert all(s.location.is_absolute() and not s.body.startswith("---") for s in skills)


@pytest.mark.parametrize("text, error", [
    ("# no frontmatter", "expected YAML frontmatter"),
    ("---\nname: other\ndescription: d\n---\nbody", "name must equal the directory name"),
    ("---\nname: s\n---\nbody", "description must be"),
])
def test_invalid_skill_fails_loudly_with_its_path(tmp_path, text, error):
    write_skill(tmp_path, "s", text)
    with pytest.raises(ValueError, match=error) as e:
        load_skills(tmp_path)
    assert str(tmp_path / "s" / "SKILL.md") in str(e.value)


def test_lazy_prompt_lists_skills_without_bodies_and_eager_inlines_them():
    skills = load_skills(SKILLS)
    lazy, eager = skills_prompt(skills), skills_prompt(skills, eager=True)
    for s in skills:
        assert s.description in lazy and str(s.location) in lazy and s.body not in lazy
        assert s.body in eager


async def test_skill_is_read_on_demand_and_the_prompt_prefix_never_changes():
    skill = load_skills(SKILLS)[1]
    llm = FakeLLM(reply("reading the skill", f"cat {skill.location}"), reply("PR opened"))
    async with Bash() as bash:
        agent = Agent(llm, Toolbox([bash]), system_prompt=SYSTEM_PROMPT + "\n\n" + skills_prompt([skill]))
        [event async for event in agent.send("fix issue #12")]
    (first, first_tools), (second, second_tools) = llm.calls
    assert first[0] == second[0] and first_tools == second_tools  # same system prompt and tools: cached prefix
    assert second[:len(first)] == first  # history is append-only
    assert skill.body in second[-1]["content"] and second[-1]["role"] == "tool"
