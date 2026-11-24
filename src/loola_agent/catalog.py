"""Example tool catalogs: real tool descriptions and schemas executed by dummy implementations."""
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DummyTool:
    name: str
    description: str
    parameters: dict

    async def run(self, args: dict) -> str:
        return json.dumps({"tool": self.name, "arguments": args, "result": "dummy implementation, no real call"})


def load_catalog(path: Path) -> tuple[list[DummyTool], str]:
    """Returns the tools and a one-line hint about what the catalog covers (for the tool_search description)."""
    tools = json.loads(path.read_text())["tools"]
    groups = sorted({t["toolset"] for t in tools})
    hint = f"The catalog has {len(tools)} tools in groups: {', '.join(groups)}."
    return [DummyTool(t["name"], t["description"], t["parameters"]) for t in tools], hint
