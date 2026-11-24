"""Tools: a minimal protocol and a toolbox that validates calls against JSON Schema.

Direct tools are declared to the model in every request. Deferred tools are not: the model finds them with
`tool_search` (BM25 over names and descriptions; matching schemas come back as the tool result) and runs them
with `tool_call`. The declared tool list therefore never changes during a session, so the prompt prefix
(and the server's KV cache for it) stays valid however many tools the model discovers."""
import json, math, re
from collections import Counter
from collections.abc import Sequence
from typing import Protocol

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match


class Tool(Protocol):
    name: str
    description: str
    parameters: dict  # JSON Schema of the arguments object

    async def run(self, args: dict) -> str: ...


class Toolbox:
    """Dispatches model tool calls. Mistakes of the model come back as text so it can fix the call itself."""

    def __init__(self, direct: Sequence[Tool], deferred: Sequence[Tool] = (), deferred_hint: str = ""):
        meta: list[Tool] = [ToolSearch(deferred, deferred_hint), ToolCall(self)] if deferred else []
        self._declared = [*direct, *meta]
        self._tools = {tool.name: tool for tool in [*self._declared, *deferred]}
        if len(self._tools) != len(self._declared) + len(deferred):
            raise ValueError("Duplicate tool names")
        self._validators = {name: _validator(tool.parameters) for name, tool in self._tools.items()}
        self._has_deferred = bool(deferred)
        # Snapshot: the declared tools are the start of the cached prompt prefix and must not change in a session.
        self._schemas = json.loads(json.dumps([
            {"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.parameters}}
            for t in self._declared]))

    def schemas(self) -> list[dict]:
        return self._schemas

    async def call(self, name: str, raw_arguments: str) -> str:
        try:
            args = json.loads(raw_arguments)
        except json.JSONDecodeError as e:
            return f"Error: arguments for '{name}' are not valid JSON ({e}). Re-issue the call with a JSON object."
        return await self.dispatch(name, args)

    async def dispatch(self, name: str, args: object) -> str:
        tool = self._tools.get(name)
        if tool is None:
            hint = "Use tool_search to find tools." if self._has_deferred else \
                f"Available tools: {', '.join(t.name for t in self._declared)}."
            return f"Error: unknown tool '{name}'. {hint}"
        if error := best_match(self._validators[name].iter_errors(args)):
            where = "/".join(map(str, error.absolute_path)) or "<root>"
            return (f"Error: invalid arguments for '{name}' at {where}: {error.message}. "
                    f"Expected schema: {json.dumps(tool.parameters)}")
        return await tool.run(args)


def _validator(schema: dict) -> Draft202012Validator:
    Draft202012Validator.check_schema(schema)
    # Most real-world schemas allow unknown keys, so a misspelled argument would be silently ignored by the tool.
    # Rejecting it lets the model see and fix the typo.
    return Draft202012Validator({"additionalProperties": False, **schema})


SEARCH_RESULTS = 5


class ToolSearch:
    name = "tool_search"
    parameters = {"type": "object",
                  "properties": {"query": {"type": "string", "description": "Keywords describing the action you need."}},
                  "required": ["query"]}

    def __init__(self, tools: Sequence[Tool], hint: str):
        self.description = ("Search the catalog of additional tools that are not listed here. Returns matching "
                            "tools (top 5) with their parameter schemas; run them with tool_call. " + hint).strip()
        self._tools = tools
        self._index = BM25([_tokens(f"{t.name} {t.description} {' '.join(t.parameters.get('properties', {}))}")
                            for t in tools])

    async def run(self, args: dict) -> str:
        scores = self._index.scores(_tokens(args["query"]))
        ranked = sorted(((s, i) for i, s in enumerate(scores) if s > 0), key=lambda pair: -pair[0])[:SEARCH_RESULTS]
        if not ranked:
            return "No tools match this query. Try other keywords."
        return json.dumps([{"name": self._tools[i].name, "description": self._tools[i].description,
                            "parameters": self._tools[i].parameters} for _, i in ranked], ensure_ascii=False)


class ToolCall:
    name = "tool_call"
    description = "Run a tool found with tool_search. `arguments` must match that tool's parameter schema."
    parameters = {"type": "object",
                  "properties": {"name": {"type": "string", "description": "Tool name from tool_search."},
                                 "arguments": {"type": "object", "description": "Arguments for the tool."}},
                  "required": ["name", "arguments"]}

    def __init__(self, toolbox: Toolbox):
        self._toolbox = toolbox

    async def run(self, args: dict) -> str:
        return await self._toolbox.dispatch(args["name"], args["arguments"])


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", text).lower())


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.2, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = [Counter(doc) for doc in docs]
        self.lengths = [len(doc) for doc in docs]
        self.avg_length = sum(self.lengths) / len(docs) if docs else 0
        df = Counter(term for doc in docs for term in set(doc))
        self.idf = {t: math.log(1 + (len(docs) - n + 0.5) / (n + 0.5)) for t, n in df.items()}

    def scores(self, query: list[str]) -> list[float]:
        return [sum(self.idf[t] * tf[t] * (self.k1 + 1)
                    / (tf[t] + self.k1 * (1 - self.b + self.b * length / self.avg_length))
                    for t in set(query) if t in tf)
                for tf, length in zip(self.docs, self.lengths)]
