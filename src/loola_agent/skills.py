"""Agent Skills (agentskills.io): one directory per skill with a SKILL.md (YAML frontmatter `name` and `description`,
then markdown instructions) and optional bundled files next to it.

Only the catalog (name, description, location) goes into the system prompt. When a task matches, the model reads
SKILL.md with bash, so the instructions land in the history as an ordinary tool result. The system prompt is fixed
for the session: loading a skill never changes the prompt prefix, and the server's KV cache for it stays valid."""
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
FRONTMATTER = re.compile(r"---\n(.*?)\n---\n(.*)", re.DOTALL)


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    location: Path  # absolute path to SKILL.md
    body: str


def load_skills(root: Path) -> list[Skill]:
    """Skills of `root/*/SKILL.md`, sorted by name so the rendered prompt is byte-stable between runs."""
    skills = [_parse(path.resolve()) for path in sorted(root.glob("*/SKILL.md"))]
    if not skills:
        raise ValueError(f"No skills in {root}: expected {root}/<name>/SKILL.md")
    return skills


def _parse(path: Path) -> Skill:
    match = FRONTMATTER.fullmatch(path.read_text())
    if match is None:
        raise ValueError(f"{path}: expected YAML frontmatter between '---' lines")
    meta = yaml.safe_load(match[1])
    name, description = meta.get("name"), meta.get("description")
    if name != path.parent.name or not NAME.fullmatch(name) or len(name) > 64:
        raise ValueError(f"{path}: name must equal the directory name, lowercase-hyphenated, at most 64 chars")
    if not isinstance(description, str) or not 0 < len(description) <= 1024:
        raise ValueError(f"{path}: description must be 1-1024 chars")
    return Skill(name, description.strip(), path, match[2].strip())


def skills_prompt(skills: list[Skill], *, eager: bool = False) -> str:
    """System prompt section. Lazy (default): catalog only, bodies are read on demand.
    Eager: every body inline, the baseline for measuring what lazy loading saves."""
    if eager:
        bodies = "\n\n".join(f'<skill name="{s.name}" location="{s.location}">\n{s.body}\n</skill>' for s in skills)
        return ("## Skills\nFollow a skill's instructions when the task matches it. Resolve relative paths in a skill "
                f"against the directory of its SKILL.md.\n\n{bodies}")
    catalog = "\n".join(f"<skill><name>{s.name}</name><description>{s.description}</description>"
                        f"<location>{s.location}</location></skill>" for s in skills)
    return ("## Skills\nSkills are instructions for specific kinds of tasks. When a task matches a skill's "
            "description, read its whole SKILL.md with bash (`cat <location>`; if the output is truncated, read "
            "the rest with `sed -n`) before acting and follow it. Resolve "
            "relative paths in a skill against the directory of its SKILL.md. If a skill you are following is no "
            "longer in the conversation (older messages get summarized), read it again.\n"
            f"<available_skills>\n{catalog}\n</available_skills>")
