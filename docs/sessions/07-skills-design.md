# Sub-agent: skills design

Full bb session log, converted from the raw event stream: inputs, agent messages, reasoning, commands with output, file changes and tool calls (long outputs truncated to 4000 characters). Local paths, thread ids and emails are redacted; outputs that came from the developer's private projects are replaced with a placeholder.

---

## [input]

Контекст: тестовое задание — минимальный async coding-agent SDK на Python, репо ~/projects/loola-test-task (прочитай TASK.md, src/loola_agent/*, git log). Задание требует «динамическую подгрузку скиллов/тулов, чтобы не держать десятки описаний в системном промпте». Тулы уже сделаны: фиксированный набор объявленных тулов (bash + tool_search + tool_call), deferred-тулы находятся BM25-поиском, их схемы приходят результатом тула, массив tools не меняется (prompt cache). История — append-only список событий, контекст — чистая проекция build_context(system_prompt, events). Дальше будет compaction (событие compaction: summary + хвост последних ходов, system prompt и tools не меняются).

Твоя задача — только дизайн (read-only: в репо ничего не меняй, параллельно в нём пишет другой агент). Скрэтч/прототипы — только в <local path>
Придумай, как добавить скиллы максимально идиоматично и супер просто, чтобы нативно легло в демо-стиль:
1. Коротко: как скиллы устроены в Agent Skills (SKILL.md, frontmatter name/description, progressive disclosure, ресурсы рядом), в Claude Code, Codex и Pi — что в промпте, как грузится тело, куда попадает в контекст. Опирайся на прошлые ресерчи (скилл session-recall; отчёты в <local path>) и проверяй по докам/исходникам там, где не уверен. Pi установлен локально (<local path>).
2. 2–3 варианта для нас (например: список name+description в system prompt + чтение тела через bash cat; отдельный тул load_skill; скиллы как документы в том же tool_search). Для каждого: сколько кода, что с prompt cache (статичность префикса), что с compaction (тело скилла пропадает из хвоста — как модель узнает/перечитает), как это показать в замере «до/после» (все тела скиллов в промпте vs ленивая подгрузка), риски.
3. Рекомендация одним вариантом + эскиз кода (сигнатуры, где живёт в SDK, как подключается в CLI) + 2–3 демо-скилла, полезных для GitHub-задач агента (короткие, реалистичные), + какие тесты.
Помни правила пользователя: никакого оверинжиниринга, один явный путь, без фолбэков.

Результат: отчёт на русском в <local path> (абзацы без hard-wrap), в финальном ответе — выжимка и рекомендация.

<details><summary>reasoning</summary>

````
I'm going to look through the repo and the previous reports first to get oriented.
````
</details>

**[agent]**

Начну с чтения репо и прошлых отчётов, чтобы дизайн лёг на существующий код.

**[command]** exit=0

````
cd ~/projects/loola-test-task && git log --oneline -25 && git status --porcelain | head && ls -R src tests 2>/dev/null | head -50 && cat TASK.md && ls -la <local path>
````

````
3b62d26 feat: deferred tools via tool_search/tool_call with a fixed declared tool list
0071731 fix: close tool calls left open by a cancelled run before the next message
ed21859 refactor: split the agent into an async SDK with a thin CLI shell
aba8673 fix: make the base agent loop survive long multi-step runs
1d6d373 chore: read LLM endpoint config from env so the agent can run without editing code
44f5083 chore: import original test task code as baseline
src:
loola_agent

src/loola_agent:
__init__.py
__pycache__
agent.py
bash.py
catalog.py
cli.py
llm.py
tools.py

src/loola_agent/__pycache__:
__init__.cpython-313.pyc
agent.cpython-313.pyc
bash.cpython-313.pyc
catalog.cpython-313.pyc
cli.cpython-313.pyc
llm.cpython-313.pyc
tools.cpython-313.pyc

tests:
__pycache__
test_agent.py
test_deferred.py
test_llm.py
test_tools.py

tests/__pycache__:
conftest.cpython-313-pytest-9.2.0.pyc
test_agent.cpython-313-pytest-9.2.0.pyc
test_deferred.cpython-313-pytest-9.2.0.pyc
test_llm.cpython-313-pytest-9.2.0.pyc
test_tools.cpython-313-pytest-9.2.0.pyc
# Test Task _ Loola 

Задача: Реализуйте в харнессе два механизма: динамическую подгрузку скиллов/тулов (чтобы не держать десятки описаний инструментов в системном промпте сразу) и умный Context Compaction при переполнении окна.Проверьте агента на длинной многошаговой задаче до и после изменений, замерьте расход токенов и успешность выполнения.Улучшите этот код (на ваш вкус).

! Если вы разрабатываете с помощью агента, то оставьте в коде ваш AGENTS.md, и лог вашей сессии с агентом (в любом виде)

Ответьте на вопросы при выполнении?

1. Как сделать compaction и подгрузку скиллов так, чтобы не инвалидировать Prompt Cache (KV-cache префикса) на каждом шаге?
1. Какие ошибки тулов нужно отдавать обратно модели для само-исправления, а какие — перехватывать детерминированно на уровне харнесса?
Загрузите код на github, отправьте нам ссылку.

```python
"""Minimal coding agent loop — one tool: bash."""
import json, sys, subprocess
import requests


LLM_BASE_URL = "http://ip:port/v1"
LLM_API_KEY = "..."
LLM_MODEL = "..."
LLM_HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {LLM_API_KEY}"}
MAX_TURNS = 1000

SYSTEM_PROMPT = """\
You are a coding agent. Your job is to help the user with programming tasks.

You have access to ONE tool: `bash` — which executes shell commands and returns stdout/stderr.

Workflow:
1. Plan what needs to be done.
2. Use `bash` to read files, run commands, write code, etc.
3. After gathering enough information or completing the task, give your final answer in natural language.
4. To finish, reply with a regular message (no tool call).

Be concise. Explain what you're doing before each command."""

LLM_TOOLS = [
    {"type": "function",
     "function": {"name": "bash",
                  "description": "Execute a shell command and return the output.",
                  "parameters": {"type": "object",
                                 "properties": {
                                     "command": {"type": "string", "description": "The bash command to execute."}
                                 },
                                 "required": ["command"]}
                 }
            }]


def run_bash(command: str) -> str:
    try:
        command_result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        out = command_result.stdout + (f"\nSTDERR:\n{command_result.stderr}" if command_result.stderr else "")
        return f"Exit code: {command_result.returncode}\n{out}"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 120s"


def call_tool(name: str, arguments: dict) -> str:
    func = {"bash": run_bash}.get(name)
    if not func:
        return f"Error: unknown tool '{name}'"
    try:
        return func(**arguments)
    except Exception as e:
        return f"Error calling {name}: {e}"


def call_llm(messages):
    payload = {"model": LLM_MODEL, "messages": messages, "tools": LLM_TOOLS, 
… [2540 more characters truncated]
````

**[command]** exit=0

````
cd ~/projects/loola-test-task && wc -l src/loola_agent/*.py tests/*.py && cat src/loola_agent/agent.py src/loola_agent/tools.py src/loola_agent/catalog.py
````

````
17 src/loola_agent/__init__.py
  121 src/loola_agent/agent.py
   79 src/loola_agent/bash.py
   22 src/loola_agent/catalog.py
   73 src/loola_agent/cli.py
   81 src/loola_agent/llm.py
  122 src/loola_agent/tools.py
  131 tests/test_agent.py
  104 tests/test_deferred.py
   62 tests/test_llm.py
  103 tests/test_tools.py
  915 total
"""Agent loop. The session is an append-only list of events; the LLM context is a pure projection of it."""
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal

from .llm import LLM, Usage
from .tools import Toolbox

SYSTEM_PROMPT = """\
You are a coding agent. Your job is to help the user with programming tasks.

Workflow:
1. Plan what needs to be done.
2. Use the tools to read files, run commands, write code, etc.
3. After gathering enough information or completing the task, give your final answer in natural language.
4. To finish, reply with a regular message (no tool call).

Be concise. Explain what you're doing before each command."""

INTERRUPTED = ("Error: this tool call was interrupted before it finished; it may have had partial side effects. "
               "Check the current state and re-run it if it is still needed.")


@dataclass(frozen=True)
class UserMessage:
    content: str


@dataclass(frozen=True)
class AssistantMessage:
    message: dict  # as returned by the LLM: parallel tool calls and reasoning fields stay intact
    finish_reason: str | None
    usage: Usage


@dataclass(frozen=True)
class ToolStarted:
    tool_call_id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class ToolResult:
    tool_call_id: str
    name: str
    content: str


@dataclass(frozen=True)
class RunFinished:
    status: Literal["done", "truncated", "empty_reply", "max_turns"]
    answer: str
    turns: int
    usage: Usage  # of this run only


Event = UserMessage | AssistantMessage | ToolStarted | ToolResult | RunFinished


def build_context(system_prompt: str, events: list[Event]) -> list[dict]:
    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    for event in events:
        match event:
            case UserMessage(content):
                messages.append({"role": "user", "content": content})
            case AssistantMessage(message):
                messages.append(message)
            case ToolResult(tool_call_id, _, content):
                messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": content})
    return messages


def unanswered_tool_calls(events: list[Event]) -> list[dict]:
    """Tool calls of the last assistant message that have no result, e.g. after a cancelled run."""
    for i in range(len(events) - 1, -1, -1):
        if isinstance(events[i], AssistantMessage):
            answered = {e.tool_call_id for e in events[i + 1:] if isinstance(e, ToolResult)}
            return [c for c in events[i].message.get("tool_calls") or [] if c["id"] not in answered]
    return []


class Agent:
    """One conversation. `send` runs the loop for a user message and streams events;
    the caller (CLI, TUI, web) decides how to render and persist them."""

    def __init__(self, llm: LLM, toolbox: Toolbox, system_prompt: str = SYSTEM_PROMPT, max_turns: int = 1000):
        self.llm, self.toolbox, self.system_prompt, self.max_turns = llm, toolbox, system_prompt, max_turns
        self.events: list[Event] = []

    async def send(self, content: str) -> AsyncIterator[Event]:
        # Close calls left open by a cancelled run: the protocol requires a result for every call, and the
        # model must know the command may have partially run. Re-running or dropping them silently would lie.
        for call in unanswered_tool_calls(self.events):
            yield self._append(ToolResult(call["id"], call["function"]["name"], INTERRUPTED))
        yield self._append(UserMessage(content))
        usage = Usage()
        for turn in range(1, self.max_turns + 1):
            completion = await self.l
… [8446 more characters truncated]
````

**[command]** exit=0

````
cd ~/projects/loola-test-task && cat src/loola_agent/cli.py src/loola_agent/__init__.py src/loola_agent/bash.py && sed -n 1,80p src/loola_agent/llm.py && ls -a && cat AGENTS.md 2>/dev/null | head -80
````

````
"""Command-line shell around the SDK: env config, rendering to stderr, JSONL transcript, exit code."""
import argparse, asyncio, json, logging, os, sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .agent import Agent, AssistantMessage, Event, RunFinished, ToolResult, ToolStarted
from .llm import LLMError, OpenAICompatibleLLM
from .bash import Bash
from .catalog import load_catalog
from .tools import Toolbox

RUNS_DIR = Path.home() / ".loola-agent" / "runs"


def render(event: Event, turn: int) -> None:
    match event:
        case AssistantMessage(message):
            print(f"\n{'=' * 60}\n🔄 Turn {turn}\n{'=' * 60}", file=sys.stderr)
            if message.get("content") and message.get("tool_calls"):
                print(f"\n🤖 {message['content']}", file=sys.stderr)
        case ToolStarted(_, name, arguments):
            print(f"🔧 Tool: {name}({arguments})", file=sys.stderr)
        case ToolResult(_, _, content):
            print(f"   → {content[:500]}{'...' if len(content) > 500 else ''}", file=sys.stderr)
        case RunFinished(status, _, turns, u):
            cached = "n/a" if u.cached is None else u.cached
            print(f"\n{'✅' if status == 'done' else '❌'} {status} after {turns} turns | "
                  f"tokens: prompt={u.prompt} cached={cached} completion={u.completion}", file=sys.stderr)


def toolbox(bash: Bash, catalog: Path | None, mode: str) -> Toolbox:
    if catalog is None:
        return Toolbox([bash])
    tools, hint = load_catalog(catalog)
    return Toolbox([bash, *tools]) if mode == "direct" else Toolbox([bash], deferred=tools, deferred_hint=hint)


async def run(task: str, transcript: Path, catalog: Path | None, mode: str) -> RunFinished:
    async with OpenAICompatibleLLM(os.environ["LLM_BASE_URL"], os.environ["LLM_API_KEY"],
                                   os.environ["LLM_MODEL"]) as llm, Bash() as bash:
        agent = Agent(llm, toolbox(bash, catalog, mode))
        turn = 0
        with transcript.open("a") as f:
            async for event in agent.send(task):
                f.write(json.dumps({"type": type(event).__name__, **asdict(event)}, ensure_ascii=False) + "\n")
                f.flush()
                turn += isinstance(event, AssistantMessage)
                render(event, turn)
    assert isinstance(event, RunFinished)
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal coding agent. Reads LLM_BASE_URL, LLM_API_KEY, LLM_MODEL.")
    parser.add_argument("task", nargs="+")
    parser.add_argument("--transcript", type=Path, help=f"JSONL event log (default: {RUNS_DIR}/<timestamp>.jsonl)")
    parser.add_argument("--catalog", type=Path, help="extra tools (JSON catalog, dummy implementations)")
    parser.add_argument("--catalog-mode", choices=["deferred", "direct"], default="deferred",
                        help="deferred: found via tool_search; direct: all declared in every request")
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING, format="⚠️  %(message)s")
    transcript = args.transcript or RUNS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}.jsonl"
    transcript.parent.mkdir(parents=True, exist_ok=True)
    print(f"📝 Transcript: {transcript}", file=sys.stderr)
    try:
        result = asyncio.run(run(" ".join(args.task), transcript, args.catalog, args.catalog_mode))
    except LLMError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    if result.answer:
        print(result.answer)
    return 0 if result.status == "done" else 1
"""Minimal async coding agent SDK.

    async with OpenAICompatibleLLM(base_url, api_key, model) as llm, Bash() as bash:
        agent = Agent(llm, Toolbox([bash], deferred=more_tools))
        async for event in agent.send("fix the failing test"):
            ...  # render / persist events; the last one is RunFinished
"""
from .agent import (SYSTEM_PROMPT, Agent, AssistantMessage, Event, RunFinished, ToolResult, 
… [7878 more characters truncated]
````

**[command]** exit=0

````
cd ~/projects/loola-test-task && ls -R examples | head -30 && cat tests/test_deferred.py | head -60 && R=<local path> grep -n -i "skill" $R/*.md | head -80
````

````
examples:
github_tools.json
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
<local path> **MCP Skills** (`--features=skills`, выключены по умолчанию) заменяют server instructions на набор workflow-скиллов (`skills/list`): ещё один способ progressive disclosure, но для инструкций, а не тулов.
<local path> Скиллы работают отдельно и по-простому: в промпте только `<available_skills>` (name / description / location), модель сама читает `SKILL.md` через `read`/`bash`. Отдельного механизма активации у скиллов нет.
<local path> Первый `system`-message сессии содержит все секции промпта (`preamble`, `tools`, `rules`, `docs`, `skills`, `cwd`, …) и `toolsAdded` с начальным набором. Последующие изменения идут отдельными `system`-messages в середине истории ([CA/docs/session-format.md:80-84](<local path>), там же JSONL-пример).
<local path>
… [1714 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking the recall report for anything on skills, and I want to look at how Pi handles skills too, along with Claude Code's Skill tool and Codex's skill injection. Grepping the recall file now.
````
</details>

**[agent]**

Pi уже частично разобран в прошлом отчёте. Проверю детали Pi по исходникам и посмотрю, что есть про Claude Code/Codex.

**[command]** exit=0

````
P=<local path> sed -n 1,200p $P/docs/skills.md | head -150; echo ----; sed -n 260,320p $P/dist/core/skills.js; echo ----; sed -n 90,115p $P/dist/core/system-prompt.js
````

````
# Skills

Skills give Pi specialized instructions and supporting files for a particular kind of work. Pi advertises each available skill by name and description, then loads its full instructions only when the task calls for them.

Use a skill when a workflow needs more context than a prompt template but does not need a new executable integration point. Skills can bundle scripts, references, and assets alongside their instructions.

Pi implements the [Agent Skills specification](https://agentskills.io/specification). Most invalid fields produce warnings rather than stopping startup.

## Create a skill

A skill is a directory containing `SKILL.md`:

```text
pdf-tools/
├── SKILL.md
├── scripts/
│   └── extract.sh
├── references/
│   └── formats.md
└── assets/
    └── template.json
```

Start `SKILL.md` with frontmatter followed by direct instructions:

```markdown
---
name: pdf-tools
description: Extract text and tables from PDF files. Use when reading, converting, or inspecting PDFs.
---

# PDF tools

Read `references/formats.md` before converting a document. Run scripts relative to this skill directory.
```

The description determines when the model considers loading the skill. State both what the skill does and when it applies. Avoid descriptions such as “Helps with PDFs,” which do not provide enough routing information.

Use relative paths from the skill directory when referring to bundled files. Pi tells the model where the skill lives so it can resolve those paths.

## Understand how skills load

At startup, Pi scans configured skill locations and adds each skill’s name, description, and path to the system prompt. It does not add the full instructions.

When a task matches, the model reads `SKILL.md` and follows its instructions. This keeps detailed guidance out of context until it is needed. A model might fail to load a relevant skill, so use `/skill:name` when you need to force it.

Arguments after `/skill:name` are appended to the loaded instructions as a user request:

```text
/skill:pdf-tools extract report.pdf
```

Set `disable-model-invocation: true` in frontmatter when a skill should be available only through its explicit command. The `enableSkillCommands` [setting](settings.md) controls whether skill commands appear in interactive command discovery; manually entered `/skill:name` commands still work.

<a id="choose-where-it-loads"></a>

## Add it to Pi

Place the skill in your user or project skills directory. Directories containing `SKILL.md` are discovered recursively.

Pi also supports the Agent Skills locations `~/.agents/skills/` and `.agents/skills/`. Project `.agents/skills/` directories are discovered from the working directory through its ancestors, stopping at the repository root when one exists.

Pi accepts some standalone Markdown skills, but a directory containing `SKILL.md` is the portable form and should be preferred. See [Settings](settings.md#resources) and [Pi Packages](packages.md) for additional locations.

Project skills can instruct the model to run scripts or modify files. Review unfamiliar skills and their supporting files before granting project trust.

## Write portable frontmatter

The Agent Skills specification defines these fields:

| Field | Purpose |
|---|---|
| `name` | Command and display name |
| `description` | Routing description shown to the model |
| `license` | License name or bundled license file |
| `compatibility` | Environment requirements |
| `metadata` | Additional key-value metadata |
| `allowed-tools` | Experimental pre-approved tool list |
| `disable-model-invocation` | Hide the skill from automatic model selection |

Names use lowercase letters, numbers, and hyphens, with no leading, trailing, or consecutive hyphens. They can contain at most 64 characters; descriptions can contain at most 1024.

Pi neither requires nor warns when the declared name differs from the parent directory. Other Agent Skills implementations may enforce that requirement, so matching names rem
… [5217 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking whether Pi's compaction keeps skill reading intact, so I'll grep for "skill" in the compaction code.
````
</details>

**[agent]**

Проверю, как Pi обращается со скиллами при compaction и что делает `/skill:name` (как тело попадает в контекст).

**[command]** exit=0

````
P=<local path> grep -rln -i "skill" $P | head -30; echo ---; grep -rn -i "skill" $P/core/compaction/*.js 2>/dev/null | head -20; grep -rn "<skill" $P --include=*.js | head -20
````

````
<persisted-output>
Output too large (41.1KB). Full output saved to: <local path>

Preview (first 2KB):
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
<local path>
...
</persisted-output>
````

**[command]** exit=0

````
P=<local path> ls $P/core | head -80; grep -n -i "skill" $P/core/agent-session.js | head -40
````

````
agent-session-runtime.d.ts
agent-session-runtime.d.ts.map
agent-session-runtime.js
agent-session-runtime.js.map
agent-session-services.d.ts
agent-session-services.d.ts.map
agent-session-services.js
agent-session-services.js.map
agent-session.d.ts
agent-session.d.ts.map
agent-session.js
agent-session.js.map
auth-guidance.d.ts
auth-guidance.d.ts.map
auth-guidance.js
auth-guidance.js.map
auth-storage.d.ts
auth-storage.d.ts.map
auth-storage.js
auth-storage.js.map
bash-executor.d.ts
bash-executor.d.ts.map
bash-executor.js
bash-executor.js.map
bug-report-upload.d.ts
bug-report-upload.d.ts.map
bug-report-upload.js
bug-report-upload.js.map
bug-report.d.ts
bug-report.d.ts.map
bug-report.js
bug-report.js.map
cache-stats.d.ts
cache-stats.d.ts.map
cache-stats.js
cache-stats.js.map
cache-warmer.d.ts
cache-warmer.d.ts.map
cache-warmer.js
cache-warmer.js.map
client-identity.d.ts
client-identity.d.ts.map
client-identity.js
client-identity.js.map
compaction
crash-log.d.ts
crash-log.d.ts.map
crash-log.js
crash-log.js.map
defaults.d.ts
defaults.d.ts.map
defaults.js
defaults.js.map
diagnostics.d.ts
diagnostics.d.ts.map
diagnostics.js
diagnostics.js.map
event-bus.d.ts
event-bus.d.ts.map
event-bus.js
event-bus.js.map
exec.d.ts
exec.d.ts.map
exec.js
exec.js.map
experimental.d.ts
experimental.d.ts.map
experimental.js
experimental.js.map
export-html
extensions
footer-data-provider.d.ts
footer-data-provider.d.ts.map
footer-data-provider.js
footer-data-provider.js.map
http-dispatcher.d.ts
http-dispatcher.d.ts.map
http-dispatcher.js
http-dispatcher.js.map
index.d.ts
60: * Parse a skill block from message text.
61: * Returns null if the text doesn't contain a skill block.
63:export function parseSkillBlock(text) {
64:    const match = text.match(/^<skill name="([^"]+)" location="([^"]+)">\n([\s\S]*?)\n<\/skill>(?:\n\n([\s\S]+))?$/);
1317:        const loadedSkills = this._resourceLoader.getSkills().skills;
1321:            skills: loadedSkills,
1669:        // Emit input event for extension interception (before skill/template expansion)
1676:        // Expand skill commands (/skill:name args) and prompt templates (/template args)
1679:            expandedText = this._expandSkillCommand(expandedText);
1741:     * Expand skill commands (/skill:name args) to their full content.
1742:     * Returns the expanded text, or the original text if not a skill command or skill not found.
1745:    _expandSkillCommand(text) {
1746:        if (!text.startsWith("/skill:"))
1749:        const skillName = spaceIndex === -1 ? text.slice(7) : text.slice(7, spaceIndex);
1751:        const skill = this.resourceLoader.getSkills().skills.find((s) => s.name === skillName);
1752:        if (!skill)
1753:            return text; // Unknown skill, pass through
1755:            const content = readFileSync(skill.filePath, "utf-8");
1757:            const skillBlock = `<skill name="${skill.name}" location="${skill.filePath}">\nReferences are relative to ${skill.baseDir}.\n\n${body}\n</skill>`;
1758:            return args ? `${skillBlock}\n\n${args}` : skillBlock;
1763:                extensionPath: skill.filePath,
1764:                event: "skill_expansion",
1777:        let expandedText = this._expandSkillCommand(processedInput.text);
1791:     * Expands skill commands and prompt templates. Errors on extension commands.
1802:     * Expands skill commands and prompt templates. Errors on extension commands.
1926:     * @param options.expandPromptTemplates Whether to dispatch extension commands and expand skill commands and prompt templates. Default: false.
2706:        const { skillPaths, promptPaths, themePaths } = await this._extensionRunner.emitResourcesDiscover(this._cwd, reason);
2707:        if (skillPaths.length === 0 && promptPaths.length === 0 && themePaths.length === 0) {
2711:            skillPaths: this.buildExtensionResourcePaths(skillPaths),
2774:            const skills = this._resourceLoader.getSkills().skills.map((skill) => ({
2775:                name: `skill:${ski
… [225 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking whether Pi's compaction keeps track of skills, so I'll grep the compaction directory for that.
````
</details>

**[command]** exit=0

````
P=<local path> ls $P/core/compaction; grep -rn -i "skill\|read-files\|readFiles\|<read" $P/core/compaction/*.js | head -20
````

````
branch-summarization.d.ts
branch-summarization.d.ts.map
branch-summarization.js
branch-summarization.js.map
compaction.d.ts
compaction.d.ts.map
compaction.js
compaction.js.map
index.d.ts
index.d.ts.map
index.js
index.js.map
utils.d.ts
utils.d.ts.map
utils.js
utils.js.map
<local path>            if (Array.isArray(details.readFiles)) {
<local path>                for (const f of details.readFiles)
<local path>    const { readFiles, modifiedFiles } = computeFileLists(fileOps);
<local path>    summary += formatFileOperations(readFiles, modifiedFiles);
<local path>        readFiles,
<local path>            if (Array.isArray(details.readFiles)) {
<local path>                for (const f of details.readFiles)
<local path>    const { readFiles, modifiedFiles } = computeFileLists(fileOps);
<local path>    summary += formatFileOperations(readFiles, modifiedFiles);
<local path>        details: { readFiles, modifiedFiles },
<local path> * Returns readFiles (files only read, not modified) and modifiedFiles.
<local path>    return { readFiles: readOnly, modifiedFiles };
<local path> function formatFileOperations(readFiles, modifiedFiles) {
<local path>    if (readFiles.length > 0) {
<local path>        sections.push(`<read-files>\n${readFiles.join("\n")}\n</read-files>`);
````

<details><summary>reasoning</summary>

````
I'm checking how the compaction summary picks up files: it lists anything read through the read tool, so a SKILL.md opened via bash wouldn't show there. I'll look at the utils file ops extraction to confirm. Then on to Claude Code and Codex, where my grep for "skill" in the recall report came back empty, so I still need to verify that.

I'm looking at how Claude Code and Codex surface skills. In Claude Code, the skill listing arrives in a system-reminder message rather than the system prompt, and invoking a skill injects the SKILL.md body as a user message. I want to check the docs on whether invoked skills are re-attached after compaction, and then do the same for Codex.
````
</details>

<details><summary>reasoning</summary>

````
Список в system prompt, тело читается `read`/`bash` в хвост, а при compaction в summary попадает `<read-files>` (только для `read`). Далее проверю Claude Code и Codex.
````
</details>

**[tool: ToolSearch]**

````
{
 "query": "select:WebFetch,WebSearch",
 "max_results": 2
}
````

````
Matched tools: WebFetch, WebSearch
````

**[tool: webFetch]**

````
https://developers.openai.com/codex/skills
````

**[tool: webFetch]**

````
https://agentskills.io/integrate-skills
````

**[tool: webFetch]**

````
https://code.claude.com/docs/en/skills
````

**[tool: webFetch]**

````
https://code.claude.com/docs/en/skills
````

**[tool: webFetch]**

````
https://learn.chatgpt.com/docs/build-skills
````

<details><summary>reasoning</summary>

````
I'm noting that the skills listing shows up as a system-reminder in the user message rather than in the system prompt, which I can see from this session itself. The Skill tool's own description says the same thing, and new skills arrive as a delta listing, so I can point to that as my own observation.

Next I want to check the Codex side against its source, so I'm looking for whether the codex source is on this machine, either under ~/.codex or as an npm install. Codex is compiled Rust, so a binary alone won't show me the code. Before grepping raw session logs I'll try the session-recall skill to see if there's past research on this.
````
</details>

<details><summary>reasoning</summary>

````
Claude Code и Agent Skills подтверждены документацией; по Codex общей документации мало, поэтому сначала проверю прошлые исследования через session-recall и при необходимости исходники codex-rs.
````
</details>

**[tool: Skill]**

````
{
 "skill": "session-recall",
 "args": "codex skills injection SKILL.md how codex loads skills ($skill mention, available skills section, compaction)"
}
````

````
Launching skill: session-recall
````

**[command]** exit=0

````
bb thread search "codex skill" 2>&1 | head -20; bb thread search "SKILL.md injection" 2>&1 | head -10; grep -n -i "skill" <local path> | head
````

````
{
  "active": {
    "total": 220,
    "results": [
      {
        "thread": {
          "id": "thr_…",
          "projectId": "proj_personal",
          "environmentId": "env_apmfq398aq",
          "providerId": "claude-code",
          "title": "Codex Cloud environments: start skill и хранение",
          "titleFallback": "Что за параметр start skill в настройке облачного environment",
          "sectionId": null,
          "status": "idle",
          "parentThreadId": null,
          "sourceThreadId": null,
          "lifecycleOwnerThreadId": null,
          "originKind": null,
          "originPluginId": null,
          "visibility": "visible",
{
  "active": {
    "total": 27,
    "results": [
      {
        "thread": {
          "id": "thr_…",
          "projectId": "proj_personal",
          "environmentId": "env_c2uuttjhie",
          "providerId": "claude-code",
````

<details><summary>reasoning</summary>

````
I'm going to skip the noisy results and check Codex directly from the source on GitHub instead. I'll look up the codex-rs skills render file.
````
</details>

**[agent]**

Поиск по тредам шумный (220 хитов на «codex skill»). Быстрее проверить Codex по исходникам codex-rs на GitHub.

**[command]** exit=0

````
cd /tmp && gh api -X GET search/code -f q='repo:openai/codex "available_skills" OR "## Skills" path:codex-rs' --jq '.items[].path' 2>&1 | head; gh api repos/openai/codex/contents/codex-rs/core/src/skills --jq '.[].path' 2>&1 | head -30
````

````
codex-rs/ext/skills/src/catalog_prompt.rs
codex-rs/ext/skills/src/render_tests.rs
{"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/contents#get-repository-content","status":"404"}gh: Not Found (HTTP 404)
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
gh api repos/openai/codex/contents/codex-rs/ext/skills/src --jq '.[].path'; gh api repos/openai/codex/contents/codex-rs/ext/skills/src/catalog_prompt.rs --jq .content | base64 -d | head -120
````

````
codex-rs/ext/skills/src/aliases.rs
codex-rs/ext/skills/src/aliases_tests.rs
codex-rs/ext/skills/src/catalog.rs
codex-rs/ext/skills/src/catalog_delta.rs
codex-rs/ext/skills/src/catalog_delta_tests.rs
codex-rs/ext/skills/src/catalog_observability.rs
codex-rs/ext/skills/src/catalog_prompt.rs
codex-rs/ext/skills/src/catalog_state.rs
codex-rs/ext/skills/src/catalog_tests.rs
codex-rs/ext/skills/src/cloud_cache_tests.rs
codex-rs/ext/skills/src/cloud_skill.rs
codex-rs/ext/skills/src/config.rs
codex-rs/ext/skills/src/dynamic_skill_selector.rs
codex-rs/ext/skills/src/dynamic_skill_selector
codex-rs/ext/skills/src/extension.rs
codex-rs/ext/skills/src/extension_tests.rs
codex-rs/ext/skills/src/fragments.rs
codex-rs/ext/skills/src/host_aliases.rs
codex-rs/ext/skills/src/host_outcome.rs
codex-rs/ext/skills/src/host_prompt.rs
codex-rs/ext/skills/src/host_roots.rs
codex-rs/ext/skills/src/host_roots_tests.rs
codex-rs/ext/skills/src/host_service.rs
codex-rs/ext/skills/src/host_service_tests.rs
codex-rs/ext/skills/src/host_snapshot.rs
codex-rs/ext/skills/src/invocation.rs
codex-rs/ext/skills/src/invocation_tests.rs
codex-rs/ext/skills/src/lib.rs
codex-rs/ext/skills/src/loader
codex-rs/ext/skills/src/preparation.rs
codex-rs/ext/skills/src/provider.rs
codex-rs/ext/skills/src/provider
codex-rs/ext/skills/src/render.rs
codex-rs/ext/skills/src/render_dedup.rs
codex-rs/ext/skills/src/render_observability.rs
codex-rs/ext/skills/src/render_observability_tests.rs
codex-rs/ext/skills/src/render_tests.rs
codex-rs/ext/skills/src/required.rs
codex-rs/ext/skills/src/selection.rs
codex-rs/ext/skills/src/shadow_selection_experiment
codex-rs/ext/skills/src/sources.rs
codex-rs/ext/skills/src/state.rs
codex-rs/ext/skills/src/step_state.rs
codex-rs/ext/skills/src/telemetry.rs
codex-rs/ext/skills/src/tools
codex-rs/ext/skills/src/warnings.rs
codex-rs/ext/skills/src/world_state.rs
codex-rs/ext/skills/src/world_state_catalogs.rs
use crate::catalog::SkillSourceKind;

const SKILLS_INTRO_WITH_SOURCE_LOCATORS: &str = "A skill is a set of instructions provided through a `SKILL.md` source. Below is the list of skills that can be used. Each entry includes a name, description, and source locator. `file` locators are on the host filesystem, `executor package` locators are owned by their execution environment, `cloud package` locators are opaque package identifiers, and `custom resource` locators use their provider's access mechanism.";
const SKILLS_INTRO_WITH_HOST_ALIASES: &str = "A skill is a set of local instructions to follow that is stored in a `SKILL.md` file. Below is the list of skills that can be used. Each entry includes a name, description, and a short path that can be expanded into an absolute path using the skill roots table.";
const SKILLS_INTRO_WITH_RESOURCE_ALIASES: &str = "A skill is a set of instructions provided through a `SKILL.md` source. Below is the list of skills that can be used. Each entry includes a name, description, and source locator. Short locators can be expanded using the skill roots table.";
const RESOURCE_ALIAS_INSTRUCTIONS: &str = "- Root aliases: Pass short package locators directly to `skills.read`; it resolves their matching alias from `### Skill roots`.";
const SKILLS_HOW_TO_USE_WITH_SOURCE_LOCATORS: &str = r###"- Discovery: The list above is the skills available in this session (name + description + source locator). `file` entries live on the host filesystem, `executor package` and `cloud package` entries are accessed directly through `skills.read`, and `custom resource` entries use their provider's access mechanism.
- Trigger rules: If the user names a skill (with `$SkillName` or plain text) OR the task clearly matches a skill's description shown above, you must use that skill for that turn. Multiple mentions mean use them all. Do not carry skills across turns unless re-mentioned.
- Missing/blocked: If a named skill isn't in the list or its source can't be read, say so briefly and continue with the best fallback.
- How to use a skill (p
… [7674 more characters truncated]
````

<details><summary>reasoning</summary>

````
The skills are listed under the "## Skills" section, and the model reads each SKILL.md itself through the shell. I should also check how explicit $mentions get injected, so I'll look at invocation.rs and fragments.rs briefly.
````
</details>

<details><summary>reasoning</summary>

````
Codex подтверждён: секция `## Skills` содержит name, description и path, а тело навыка модель читает сама. Далее проверю, что делает явный `$skill` и где эта секция находится.
````
</details>

**[command]** exit=0

````
gh api repos/openai/codex/contents/codex-rs/ext/skills/src/fragments.rs --jq .content | base64 -d | head -80; echo ======; gh api repos/openai/codex/contents/codex-rs/ext/skills/src/invocation.rs --jq .content | base64 -d | grep -n -i "skill>\|user\|developer\|inject\|compact" | head -30
````

````
use codex_extension_api::ContextualUserFragment;
use codex_protocol::models::ContentItem;
use codex_protocol::models::ContentItemKind;
use codex_protocol::models::ContentItemMetadata;
use codex_protocol::models::input_text;
use codex_protocol::protocol::SKILLS_INSTRUCTIONS_CLOSE_TAG;
use codex_protocol::protocol::SKILLS_INSTRUCTIONS_OPEN_TAG;

use crate::catalog_prompt::SkillPrompt;
use crate::catalog_prompt::render_available_skills_body;
use crate::tools::SkillToolAuthority;

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct AvailableSkillsInstructions {
    prompt: SkillPrompt,
    skill_root_lines: Vec<String>,
    skill_lines: Vec<String>,
}

impl AvailableSkillsInstructions {
    pub(crate) fn from_skill_lines(
        prompt: SkillPrompt,
        skill_root_lines: Vec<String>,
        mut skill_lines: Vec<String>,
        include_skills_usage_instructions: bool,
    ) -> Self {
        if include_skills_usage_instructions {
            skill_lines.push("### How to use skills".to_string());
            if let Some(instructions) = prompt.kind.alias_instructions() {
                skill_lines.push(instructions.to_string());
            }
            skill_lines.push(prompt.usage_instructions());
        }
        Self {
            prompt,
            skill_root_lines,
            skill_lines,
        }
    }
}

impl ContextualUserFragment for AvailableSkillsInstructions {
    fn content_metadata(&self) -> ContentItemMetadata {
        ContentItemMetadata::skills()
    }

    fn role(&self) -> &'static str {
        "developer"
    }

    fn content_kind(&self) -> ContentItemKind {
        ContentItemKind("skills.catalog".to_string())
    }

    fn markers(&self) -> (&'static str, &'static str) {
        Self::type_markers()
    }

    fn type_markers() -> (&'static str, &'static str) {
        (SKILLS_INSTRUCTIONS_OPEN_TAG, SKILLS_INSTRUCTIONS_CLOSE_TAG)
    }

    fn body(&self) -> ContentItem {
        input_text(render_available_skills_body(
            self.prompt,
            &self.skill_root_lines,
            &self.skill_lines,
        ))
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct SkillInstructions {
    pub(crate) name: String,
    pub(crate) path: String,
    pub(crate) contents: String,
    pub(crate) resource_access: Option<SkillResourceAccess>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
======
````

**[command]** exit=0

````
gh api repos/openai/codex/contents/codex-rs/ext/skills/src/fragments.rs --jq .content | base64 -d | sed -n 80,170p
````

````
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct SkillResourceAccess {
    pub(crate) authority: SkillToolAuthority,
    pub(crate) package: String,
    pub(crate) main_resource: String,
}

impl ContextualUserFragment for SkillInstructions {
    fn content_metadata(&self) -> ContentItemMetadata {
        ContentItemMetadata::skills()
    }

    fn role(&self) -> &'static str {
        "user"
    }

    fn content_kind(&self) -> ContentItemKind {
        ContentItemKind("skills.selected_skill_instructions".to_string())
    }

    fn markers(&self) -> (&'static str, &'static str) {
        Self::type_markers()
    }

    fn type_markers() -> (&'static str, &'static str) {
        ("<skill>", "</skill>")
    }

    fn body(&self) -> ContentItem {
        let name = &self.name;
        let path = &self.path;
        let contents = &self.contents;
        let resource_access = self
            .resource_access
            .as_ref()
            .map(|access| {
                let metadata = serde_json::json!({
                    "authority": access.authority,
                    "package": access.package,
                    "main_resource": access.main_resource,
                });
                format!("\n<resource_access>{metadata}</resource_access>")
            })
            .unwrap_or_default();
        input_text(format!(
            "\n<name>{name}</name>\n<path>{path}</path>{resource_access}\n{contents}\n"
        ))
    }
}
````

<details><summary>reasoning</summary>

````
Похоже, compaction в Codex оставляет только пользовательские сообщения и summary, а contextual-фрагменты вроде environment context потом заново подтягиваются через initial context. Глубоко в исходники я не лез, так что так и скажу: по исходникам проверил не до конца.

Я собираюсь проверить в исходниках codex compact.rs, есть ли там фильтрация по contextual-фрагментам.
````
</details>

**[agent]**

Последняя проверка по Codex — что происходит со скиллами при compaction.

**[command]** exit=0

````
gh api -X GET search/code -f q='repo:openai/codex path:codex-rs/core compact is_contextual_user_fragment' --jq '.items[].path' 2>&1 | head; gh api repos/openai/codex/contents/codex-rs/core/src/compact.rs --jq .content 2>/dev/null | base64 -d | grep -n -i "contextual\|initial_context\|skill\|collect_user_messages" | head -30
````

````
codex-rs/core/src/agent/control/user_authorization.rs
codex-rs/core/src/context_manager/history_user_authorization.rs
codex-rs/core/src/context/mod.rs
15:use crate::context::ContextualUserFragment;
71:/// Thread-local policy that preserves inherited context without changing model or skill budgets.
97:        .build_initial_context_with_world_state(step_context, world_state)
112:    let history = insert_initial_context_before_last_real_user_or_summary(
447:        .assemble_initial_context(&replacement_step_context, rendered)
619:pub(crate) fn collect_user_messages(items: &[ResponseItem]) -> Vec<CompactedUserMessage<'_>> {
682:pub(crate) fn insert_initial_context_before_last_real_user_or_summary(
684:    initial_context: Vec<ResponseItemEnvelope>,
725:        compacted_history.splice(insertion_index..insertion_index, initial_context);
727:        compacted_history.extend(initial_context);
854:    history.push(ResponseItemEnvelope::new(ContextualUserFragment::into(
````

**[command]** exit=0

````
gh api repos/openai/codex/contents/codex-rs/core/src/compact.rs --jq .content | base64 -d | sed -n 615,680p
````

````
harness_metadata: Option<&'a CodexHarnessMetadata>,
}

#[cfg(test)]
pub(crate) fn collect_user_messages(items: &[ResponseItem]) -> Vec<CompactedUserMessage<'_>> {
    items
        .iter()
        .filter_map(|item| compacted_user_message(item, /*harness_metadata*/ None))
        .collect()
}

fn annotated_user_messages(
    items: &[ResponseItemEnvelope],
) -> impl DoubleEndedIterator<Item = (usize, CompactedUserMessage<'_>)> {
    items.iter().enumerate().filter_map(|(position, envelope)| {
        let message = compacted_user_message(&envelope.item, envelope.metadata.as_ref())?;
        Some((position, message))
    })
}

fn compacted_user_message<'a>(
    item: &'a ResponseItem,
    harness_metadata: Option<&'a CodexHarnessMetadata>,
) -> Option<CompactedUserMessage<'a>> {
    let Some(TurnItem::UserMessage(user)) = crate::event_mapping::parse_turn_item(item) else {
        return None;
    };
    let message = user.message();
    if is_summary_message(&message) {
        return None;
    }
    Some(CompactedUserMessage {
        message,
        original: item,
        harness_metadata,
    })
}

pub(crate) fn is_summary_message(message: &str) -> bool {
    message.starts_with(format!("{SUMMARY_PREFIX}\n").as_str())
}

pub(crate) fn is_real_user_or_agent_message(item: &ResponseItem) -> bool {
    if let ResponseItem::AgentMessage { content, .. } = item {
        return !matches!(
            content.first(),
            Some(AgentMessageInputContent::InputText { text })
                if text.starts_with("Message Type: FINAL_ANSWER\n")
        );
    }
    matches!(item, ResponseItem::Message { role, .. } if role == "user")
        && matches!(
            crate::event_mapping::parse_turn_item(item),
            Some(TurnItem::UserMessage(user)) if !is_summary_message(&user.message())
        )
}

/// Inserts canonical initial context into compacted replacement history at the
/// model-expected boundary.
///
/// Placement rules:
/// - Prefer immediately before the last real user, agent message, or retained standalone output.
/// - If no real user messages remain, insert before the compaction summary so
///   the summary stays last.
/// - If there are no user messages, insert before the last compaction item so
///   that item remains last (remote compaction may return only compaction items).
````

<details><summary>reasoning</summary>

````
I'm fairly sure that parse_turn_item drops contextual fragments like skill instructions, which have <skill> markers. So after a Codex compaction, the catalog is re-inserted as initial context, while injected skill bodies and SKILL.md files read by tools are lost and only real user messages plus the summary remain. I'll hedge that in the write-up, since it rests on reading compact.rs.

I'm weighing a design where the skills catalog goes into the system prompt as name, description, and location, with each skill body loaded on demand through bash `cat`. That needs only a small loader and a prompt-rendering function, with no changes to the agent loop or toolbox. Because the system prompt stays fixed for the session, the prefix remains stable, and after compaction the model can still re-read SKILL.md, so the summary should note which skills were in use.

Next I'm weighing a lazy option against an eager one: a `--skills-mode` switch that either inlines full skill bodies into the system prompt or keeps only the catalog there. Both keep the system prompt static, so caching works either way, and the real difference is how many prompt tokens get paid on every turn, especially with many skills.

Now I'm weighing a dedicated `skill` tool, something like `load_skill(name)` with an enum of skill names. The catalog could live in the tool description or the system prompt, and the tool would return the body wrapped in `<skill_content>` tags along with the skill's directory and resource list. The appeal is that those structured tags would let the harness recognize skill results and re-attach them after compaction.

Now I'm weighing a third option: indexing skills as documents in the same tool_search catalog. That would keep the prompt small even with hundreds of skills, but discovery would depend on the model searching for the right thing, and tool_search returns schemas that skills don't have.

The next part weighs a third option, a separate lazy loader (A) for the skills, and I'm leaning toward the system-prompt catalog with bash `cat`. It's the standard pattern that Pi and Codex use, and it adds no new tools and needs no loop changes. The tool_search route is less clear: it only exists when deferred tools are declared, and it mixes discovery with tools that skills aren't, so the model might never search and the skill would go unused. I'm also noting a possible Codex dynamic skill selector in the source, though I don't need it for this.

I'm weighing whether compaction could stay simpler with the skills catalog in the system prompt: the model can always re-read SKILL.md, so the summarizer only needs to list which skills were in use. The one real advantage of a dedicated skill tool is that the harness could detect skill loads deterministically, whereas spotting them in bash commands is fragile. I'll keep that as a possible upgrade if I see failures in practice, rather than building it into the demo now.

I'm weighing whether the eager mode should be included as a measurement baseline, mirroring the `--catalog-mode direct|deferred` switch, so the token cost of inlining full bodies can be compared directly against the lazy catalog. The system prompt stays byte-stable across a session because the skill list is sorted, so caching works either way.

I'm settling on `skills_prompt(skills, eager)`, which renders the full bodies inline for the eager baseline, about five lines. I'll also check the GitHub demo skills against the tool names in `examples/github_tools.json`, since a skill that names a deferred tool lets the model call it directly, and a wrong name just returns the expected schema.

Next I'm checking the tool names in `examples/github_tools.json`, so the GitHub demo skills can refer to real tools.
````
</details>

<details><summary>reasoning</summary>

````
Все четыре системы проверены; теперь смотрю инструменты в examples/github_tools.json, чтобы строить на них демо-скиллы.
````
</details>

**[command]** exit=0

````
cd ~/projects/loola-test-task && jq -r '.tools[] | "\(.toolset)\t\(.name)"' examples/github_tools.json | sort | head -120 | column -t | head -100; jq '.tools|length' examples/github_tools.json; cat pyproject.toml; cat .gitignore
````

````
actions                actions_get
actions                actions_list
actions                actions_run_trigger
actions                get_job_logs
code_quality           get_code_quality_finding
code_security          get_code_scanning_alert
code_security          list_code_scanning_alerts
context                get_me
context                get_team_members
context                get_teams
context                ui_get
copilot                assign_copilot_to_issue
copilot                request_copilot_review
copilot_issue_intents  assign_copilot_to_issue_with_intent
dependabot             get_dependabot_alert
dependabot             list_dependabot_alerts
discussions            discussion_comment_write
discussions            get_discussion
discussions            get_discussion_comments
discussions            list_discussion_categories
discussions            list_discussions
gists                  create_gist
gists                  get_gist
gists                  list_gists
gists                  update_gist
git                    get_repository_tree
governance             create_repository_ruleset
governance             custom_properties_read
governance             custom_properties_write
governance             repository_ruleset_read
issues                 add_issue_comment
issues                 issue_read
issues                 issue_write
issues                 list_issue_fields
issues                 list_issue_types
issues                 list_issues
issues                 search_issues
issues                 sub_issue_write
issues                 update_issue_comment
labels                 get_label
labels                 label_write
labels                 list_label
notifications          dismiss_notification
notifications          get_notification_details
notifications          list_notifications
notifications          manage_notification_subscription
notifications          manage_repository_notification_subscription
notifications          mark_all_notifications_read
orgs                   search_orgs
projects               projects_get
projects               projects_list
projects               projects_write
pull_requests          add_comment_to_pending_review
pull_requests          add_reply_to_pull_request_comment
pull_requests          create_pull_request
pull_requests          list_pull_requests
pull_requests          merge_pull_request
pull_requests          pull_request_read
pull_requests          pull_request_review_write
pull_requests          search_pull_requests
pull_requests          update_pull_request
pull_requests          update_pull_request_branch
repos                  create_branch
repos                  create_or_update_file
repos                  create_repository
repos                  delete_file
repos                  fork_repository
repos                  get_commit
repos                  get_file_contents
repos                  get_latest_release
repos                  get_release_by_tag
repos                  get_tag
repos                  list_branches
repos                  list_commits
repos                  list_releases
repos                  list_repository_collaborators
repos                  list_tags
repos                  push_files
repos                  search_code
repos                  search_commits
repos                  search_repositories
secret_protection      get_secret_scanning_alert
secret_protection      list_secret_scanning_alerts
security_advisories    get_global_security_advisory
security_advisories    list_global_security_advisories
security_advisories    list_org_repository_security_advisories
security_advisories    list_repository_security_advisories
stargazers             list_starred_repositories
stargazers             star_repository
stargazers             unstar_repository
users                  search_users
91
[project]
name = "loola-agent"
version = "0.1.0"
description = "Minimal async coding agent SDK + CLI (Loola test task)"
requires-python = ">=3.1
… [629 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm weighing whether to add PyYAML or hand-parse the frontmatter, since the spec is YAML and descriptions can run across lines. A tiny parser that only reads single-line `name:` and `description:` fields would be an unstated restriction, so adding the dependency looks more honest and only costs one line. I'm leaning toward pyyaml with `yaml.safe_load`.

I'm settling on the frontmatter question: I'll use pyyaml with `yaml.safe_load`, which keeps one explicit parsing path and fails loudly on invalid input rather than falling back to something lenient. Next I want to build a quick prototype in a scratch directory to check code size and token counts, with three short GitHub-related demo skills and some tests.

I'm sketching out three demo skills for GitHub work: one for fixing issues, one for triaging CI failures with a small script that pulls out the first error, and one for reviewing PRs against a checklist. Before writing them I want to confirm the argument names for the pull_request_read, get_job_logs, pull_request_review_write, and issue_read tools so the skills match the real interfaces.
````
</details>

<details><summary>reasoning</summary>

````
Я построю демо-скиллы как workflow поверх существующих deferred GitHub-тулов и сверю их точные параметры.
````
</details>

**[command]** exit=0

````
cd ~/projects/loola-test-task && for t in issue_read pull_request_read pull_request_review_write add_comment_to_pending_review get_job_logs actions_list create_pull_request create_branch push_files; do jq -c --arg t $t '.tools[]|select(.name==$t)|{name, req:.parameters.required, props:(.parameters.properties|to_entries|map({k:.key, enum:.value.enum})) }' examples/github_tools.json; done
````

````
{"name":"issue_read","req":["method","owner","repo","issue_number"],"props":[{"k":"issue_number","enum":null},{"k":"method","enum":["get","get_comments","get_sub_issues","get_parent","get_labels"]},{"k":"owner","enum":null},{"k":"page","enum":null},{"k":"perPage","enum":null},{"k":"repo","enum":null}]}
{"name":"pull_request_read","req":["method","owner","repo","pullNumber"],"props":[{"k":"after","enum":null},{"k":"method","enum":["get","get_diff","get_status","get_files","get_commits","get_review_comments","get_reviews","get_comments","get_check_runs"]},{"k":"owner","enum":null},{"k":"page","enum":null},{"k":"perPage","enum":null},{"k":"pullNumber","enum":null},{"k":"repo","enum":null}]}
{"name":"pull_request_review_write","req":["method","owner","repo","pullNumber"],"props":[{"k":"body","enum":null},{"k":"commitID","enum":null},{"k":"event","enum":["APPROVE","REQUEST_CHANGES","COMMENT"]},{"k":"method","enum":["create","submit_pending","delete_pending","resolve_thread","unresolve_thread"]},{"k":"owner","enum":null},{"k":"pullNumber","enum":null},{"k":"repo","enum":null},{"k":"threadId","enum":null}]}
{"name":"add_comment_to_pending_review","req":["owner","repo","pullNumber","path","body","subjectType"],"props":[{"k":"body","enum":null},{"k":"line","enum":null},{"k":"owner","enum":null},{"k":"path","enum":null},{"k":"pullNumber","enum":null},{"k":"repo","enum":null},{"k":"side","enum":["LEFT","RIGHT"]},{"k":"startLine","enum":null},{"k":"startSide","enum":["LEFT","RIGHT"]},{"k":"subjectType","enum":["FILE","LINE"]}]}
{"name":"get_job_logs","req":["owner","repo"],"props":[{"k":"failed_only","enum":null},{"k":"job_id","enum":null},{"k":"owner","enum":null},{"k":"repo","enum":null},{"k":"return_content","enum":null},{"k":"run_id","enum":null},{"k":"tail_lines","enum":null}]}
{"name":"actions_list","req":["method","owner","repo"],"props":[{"k":"method","enum":["list_workflows","list_workflow_runs","list_workflow_jobs","list_workflow_run_artifacts"]},{"k":"owner","enum":null},{"k":"page","enum":null},{"k":"perPage","enum":null},{"k":"repo","enum":null},{"k":"resource_id","enum":null},{"k":"workflow_jobs_filter","enum":null},{"k":"workflow_runs_filter","enum":null}]}
{"name":"create_pull_request","req":["owner","repo","title","head","base"],"props":[{"k":"base","enum":null},{"k":"body","enum":null},{"k":"draft","enum":null},{"k":"head","enum":null},{"k":"maintainer_can_modify","enum":null},{"k":"owner","enum":null},{"k":"repo","enum":null},{"k":"reviewers","enum":null},{"k":"title","enum":null}]}
{"name":"create_branch","req":["owner","repo","branch"],"props":[{"k":"branch","enum":null},{"k":"from_branch","enum":null},{"k":"owner","enum":null},{"k":"repo","enum":null}]}
{"name":"push_files","req":["owner","repo","branch","files","message"],"props":[{"k":"branch","enum":null},{"k":"files","enum":null},{"k":"message","enum":null},{"k":"owner","enum":null},{"k":"repo","enum":null}]}
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm going to prototype now, putting the skills module, demo skill folders, and a test file in a scratch directory. For running the tests, I want to avoid touching the repo, since `uv run` might sync and write a `.venv` there. So I'll call the project's existing venv Python directly with pytest, setting PYTHONPATH to the scratch directory.

The next thinking is about the test setup and the module design. I'm avoiding `uv run` inside the repo, so I'll run the tests with an ephemeral environment that has the needed dependencies and points PYTHONPATH at the repo's src. I'm also setting PYTHONDONTWRITEBYTECODE so nothing gets written into the repo. Then I'm sketching the skills module: a small Skill dataclass that holds a name, description, and path, read from each skill's SKILL.md frontmatter.

I'm sketching the skills module's core: a frozen Skill dataclass, a loader that collects each `*/SKILL.md` and rejects duplicate names, and a parser that splits the YAML frontmatter and raises a clear error when name or description is missing. I'm also planning a `skills_prompt` function with an inline option, so I can measure the full-body version against the catalog-only one.

I'm sketching the loader and parser: frozen Skill dataclass, a validator that checks the name against the directory and rejects duplicates, and a prompt builder with an inline option for measuring full bodies against the catalog-only version.

Now I'm laying out the skills module as a frozen dataclass, a loader that rejects duplicate names, and a prompt builder with an inline option for measuring full bodies.

Now I'm sketching the skills module's interface: a frozen `Skill` dataclass, a `--skills-mode` switch between lazy and eager, and a prompt builder that wires into the agent's system prompt.

I'm weighing whether to use an explicit `--skills` flag instead of scanning `.agents/skills` automatically, since an explicit flag is simpler and matches how `--catalog` already works. Skills are instructions, so I'll only load them from the directory the user names. For measurement, I'm planning to run the same long GitHub task under three setups (no skills, inline, lazy), tracking total and cached prompt tokens, turns, and whether the skill steps were followed. With only three demo skills the difference will be small, so I'm also considering extrapolating the token cost to a larger number of skills.

I'm considering using the larger anthropics/skills repo, which has around fifteen skills, as a measurement set instead of writing more demos. Pointing `--skills` at a cloned copy would show the cost of eager loading with real skills. Some of those skills are source-available rather than Apache 2.0, so I'd need to check licenses, and they'd stay local for measurement only, never committed. I'll count tokens with tiktoken's o200k encoding on the three demo skills and on that cloned set, starting the prototype in scratch.
````
</details>

<details><summary>reasoning</summary>

````
Параметры проверены. Сейчас собираю прототип в scratch-папке, репозиторий не трогаю, чтобы в отчёте были реальные цифры токенов.
````
</details>

**[command]** exit=0

````
S=<local path> mkdir -p $S/proto/loola_skills $S/proto/skills/{fix-github-issue,ci-failure-triage/scripts,review-pull-request/references} $S/proto/tests && ls $S
````

````
proto
````

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+"""Agent Skills (agentskills.io): one directory per skill with a SKILL.md (YAML frontmatter `name` and `description`,
+then markdown instructions) and optional bundled files next to it.
+
+Only the catalog (name, description, location) goes into the system prompt. When a task matches, the model reads
+SKILL.md with bash, so the instructions land in the history as an ordinary tool result. The system prompt is fixed
+for the session: loading a skill never changes the prompt prefix, and the server's KV cache for it stays valid."""
+import re
+from dataclasses import dataclass
+from pathlib import Path
+
+import yaml
+
+NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
+FRONTMATTER = re.compile(r"---\n(.*?)\n---\n(.*)", re.DOTALL)
+
+
+@dataclass(frozen=True)
+class Skill:
+    name: str
+    description: str
+    location: Path  # absolute path to SKILL.md
+    body: str
+
+
+def load_skills(root: Path) -> list[Skill]:
+    """Skills of `root/*/SKILL.md`, sorted by name so the rendered prompt is byte-stable between runs."""
+    skills = [_parse(path.resolve()) for path in sorted(root.glob("*/SKILL.md"))]
+    if not skills:
+        raise ValueError(f"No skills in {root}: expected {root}/<name>/SKILL.md")
+    return skills
+
+
+def _parse(path: Path) -> Skill:
+    match = FRONTMATTER.fullmatch(path.read_text())
+    if match is None:
+        raise ValueError(f"{path}: expected YAML frontmatter between '---' lines")
+    meta = yaml.safe_load(match[1])
+    name, description = meta.get("name"), meta.get("description")
+    if name != path.parent.name or not NAME.fullmatch(name) or len(name) > 64:
+        raise ValueError(f"{path}: name must equal the directory name, lowercase-hyphenated, at most 64 chars")
+    if not isinstance(description, str) or not 0 < len(description) <= 1024:
+        raise ValueError(f"{path}: description must be 1-1024 chars")
+    return Skill(name, description.strip(), path, match[2].strip())
+
+
+def skills_prompt(skills: list[Skill], *, eager: bool = False) -> str:
+    """System prompt section. Lazy (default): catalog only, bodies are read on demand.
+    Eager: every body inline, the baseline for measuring what lazy loading saves."""
+    if eager:
+        bodies = "\n\n".join(f'<skill name="{s.name}" location="{s.location}">\n{s.body}\n</skill>' for s in skills)
+        return ("## Skills\nFollow a skill's instructions when the task matches it. Resolve relative paths in a skill "
+                f"against the directory of its SKILL.md.\n\n{bodies}")
+    catalog = "\n".join(f"<skill><name>{s.name}</name><description>{s.description}</description>"
+                        f"<location>{s.location}</location></skill>" for s in skills)
+    return ("## Skills\nSkills are instructions for specific kinds of tasks. When a task matches a skill's "
+            "description, read its SKILL.md with bash (`cat <location>`) before acting and follow it. Resolve "
+            "relative paths in a skill against the directory of its SKILL.md. If a skill you are following is no "
+            "longer in the conversation (older messages get summarized), read it again.\n"
+            f"<available_skills>\n{catalog}\n</available_skills>")

````

<details><summary>reasoning</summary>

````
I'm skipping XML escaping for descriptions with `<` or `&`, since the models handle it fine and it's a minor point. Next I'm drafting the demo skills: short, realistic ones that name the deferred tools and tell the model to look up schemas with tool_search and call them with tool_call.
````
</details>

<details><summary>reasoning</summary>

````
Сейчас делаю три демо-скилла: каждый — workflow поверх deferred GitHub-тулов, и два из них получают bundled-ресурс (скрипт и чеклист рядом с SKILL.md).
````
</details>

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+---
+name: fix-github-issue
+description: Fix a bug reported in a GitHub issue and open a pull request for it. Use when the task references an issue number or URL and asks to fix, resolve, or implement it.
+---
+
+# Fix a GitHub issue
+
+GitHub tools are not declared directly: get their schemas with `tool_search` and run them with `tool_call`.
+
+1. Read the issue and its discussion: `issue_read` with `method: "get"`, then `method: "get_comments"`. Write down the expected and the actual behaviour in one line each.
+2. Reproduce locally before changing code. Prefer a failing test next to the existing tests for that module; if the bug cannot be reproduced, stop and report what you tried instead of guessing a fix.
+3. Make the smallest change that makes the test pass. Do not refactor unrelated code in the same PR.
+4. Run the full test suite. A PR with failing tests is not done.
+5. Branch `fix/<issue-number>-<short-slug>`, one commit with a conventional message (`fix: <what was wrong>`).
+6. Open the PR with `create_pull_request`:
+   - title: the commit message;
+   - body: `Fixes #<issue-number>`, then the root cause in 1-2 sentences, then how it was verified (test name, command).
+7. Answer with the PR URL and the root cause.

````

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+---
+name: ci-failure-triage
+description: Find why a GitHub Actions run failed and fix it. Use when CI, a workflow run, a check, or a build is red, or when asked why tests fail on GitHub but not locally.
+---
+
+# Triage a failed CI run
+
+GitHub tools are not declared directly: get their schemas with `tool_search` and run them with `tool_call`.
+
+1. Find the failed run: `actions_list` with `method: "list_workflow_runs"`; take the newest run with conclusion `failure` on the branch in question.
+2. Fetch only the failed jobs' logs: `get_job_logs` with `run_id`, `failed_only: true`, `return_content: true`, `tail_lines: 300`.
+3. Save the logs to a file and run `scripts/first_error.sh <file>`: it prints the first error with context. The first error is the cause; later ones are usually fallout.
+4. Classify before fixing:
+   - code or test bug: reproduce locally with the same command the job ran, then fix;
+   - environment difference (versions, missing service, secrets): compare the workflow file with the local setup and fix the workflow, not the code;
+   - flaky (passes on re-run, timing-dependent): say so and do not "fix" it with retries or sleeps.
+5. Answer with the failing step, the root cause, and the fix (or why no code change is needed).

````

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+#!/usr/bin/env bash
+# Print the first error-looking line of a CI log with 5 lines of context before and 20 after.
+set -euo pipefail
+line=$(grep -n -m1 -E '(^|[^a-z])(error|failed|FAILED|Error|Traceback|panic:)' "$1" | cut -d: -f1) || {
+  echo "No error-looking lines in $1"; exit 1; }
+sed -n "$((line > 5 ? line - 5 : 1)),$((line + 20))p" "$1"

````

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+---
+name: review-pull-request
+description: Review a GitHub pull request and leave line comments plus a verdict. Use when asked to review, check, or approve a PR.
+---
+
+# Review a pull request
+
+GitHub tools are not declared directly: get their schemas with `tool_search` and run them with `tool_call`.
+
+1. Read the PR description and the diff: `pull_request_read` with `method: "get"`, then `method: "get_diff"`. Check `method: "get_check_runs"`: if CI is red, say so first.
+2. Go through `references/checklist.md` for every changed file. Report only real problems: a bug, a missing test for changed behaviour, a broken contract. Skip style nits that a linter would catch.
+3. Leave comments as one review, not as separate comments:
+   - `pull_request_review_write` with `method: "create"` (no `event`) opens a pending review;
+   - `add_comment_to_pending_review` for each problem, `subjectType: "LINE"`, on the line of the new code (`side: "RIGHT"`), with what is wrong and a concrete fix;
+   - `pull_request_review_write` with `method: "submit_pending"` and `event`: `REQUEST_CHANGES` if any comment is a bug, otherwise `APPROVE` or `COMMENT`.
+4. Answer with the verdict and the list of problems by severity.

````

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+# Review checklist
+
+- Does the change do what the PR description says, and nothing else?
+- Are error paths handled where they can actually happen (I/O, network, user input), and not invented elsewhere?
+- Is changed behaviour covered by a test that would fail without the change?
+- Public API, CLI flags, config or data formats: backwards compatible, or the break is stated in the description?
+- Secrets, tokens, or personal data in code, logs, or fixtures?
+- Concurrency: shared state, missing awaits, resources not closed on error?

````

<details><summary>reasoning</summary>

````
I'm drafting the test plan now: parsing and sorting the demo skills while leaving frontmatter out of the body, checking that malformed skills raise a ValueError with the path, confirming the lazy prompt lists names, descriptions and locations without bodies while the eager one includes them, and finally an integration test where a scripted fake LLM calls bash to cat a skill's location and then answers, with assertions on the system message.

I'm checking that the agent's system message and tool list stay the same across both requests, and that the skill body shows up in a tool result. The test will use the real Bash tool, so I still need to find the fake LLM pattern already used in test_agent.py.
````
</details>

**[agent]**

Тесты: посмотрю, какой fake LLM уже используется в `tests/test_agent.py`, чтобы прототип тестов был в стиле репо.

**[command]** exit=0

````
cd ~/projects/loola-test-task && sed -n 1,50p tests/test_agent.py
````

````
"""Agent loop behavior against a scripted fake LLM."""
import asyncio, json

import pytest

from loola_agent.agent import INTERRUPTED, unanswered_tool_calls
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
Shell cwd was reset to <local path>
````

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+"""Skills: SKILL.md parsing, the system prompt section, and on-demand loading through bash with a stable prefix."""
+import json
+from pathlib import Path
+
+import pytest
+
+from loola_agent import Agent, Bash, Completion, Toolbox, Usage
+from loola_agent.agent import SYSTEM_PROMPT
+from loola_skills.skills import load_skills, skills_prompt
+
+SKILLS = Path(__file__).parent.parent / "skills"
+
+
+class FakeLLM:
+    def __init__(self, *script: Completion):
+        self.script, self.calls = list(script), []
+
+    async def complete(self, messages, tools):
+        self.calls.append((messages, tools))
+        return self.script.pop(0)
+
+
+def reply(content=None, command=None):
+    message = {"role": "assistant", "content": content}
+    if command:
+        message["tool_calls"] = [{"id": "c1", "type": "function",
+                                  "function": {"name": "bash", "arguments": json.dumps({"command": command})}}]
+    return Completion(message, "tool_calls" if command else "stop", Usage(10, 2, 8))
+
+
+def write_skill(root: Path, dirname: str, text: str) -> None:
+    (root / dirname).mkdir()
+    (root / dirname / "SKILL.md").write_text(text)
+
+
+def test_demo_skills_are_loaded_sorted_without_frontmatter_in_body():
+    skills = load_skills(SKILLS)
+    assert [s.name for s in skills] == ["ci-failure-triage", "fix-github-issue", "review-pull-request"]
+    assert all(s.location.is_absolute() and not s.body.startswith("---") for s in skills)
+
+
<email>("text, error", [
+    ("# no frontmatter", "expected YAML frontmatter"),
+    ("---\nname: other\ndescription: d\n---\nbody", "name must equal the directory name"),
+    ("---\nname: s\n---\nbody", "description must be"),
+])
+def test_invalid_skill_fails_loudly_with_its_path(tmp_path, text, error):
+    write_skill(tmp_path, "s", text)
+    with pytest.raises(ValueError, match=error) as e:
+        load_skills(tmp_path)
+    assert str(tmp_path / "s" / "SKILL.md") in str(e.value)
+
+
+def test_lazy_prompt_lists_skills_without_bodies_and_eager_inlines_them():
+    skills = load_skills(SKILLS)
+    lazy, eager = skills_prompt(skills), skills_prompt(skills, eager=True)
+    for s in skills:
+        assert s.description in lazy and str(s.location) in lazy and s.body not in lazy
+        assert s.body in eager
+
+
+async def test_skill_is_read_on_demand_and_the_prompt_prefix_never_changes():
+    skill = load_skills(SKILLS)[1]
+    llm = FakeLLM(reply("reading the skill", f"cat {skill.location}"), reply("PR opened"))
+    async with Bash() as bash:
+        agent = Agent(llm, Toolbox([bash]), system_prompt=SYSTEM_PROMPT + "\n\n" + skills_prompt([skill]))
+        [event async for event in agent.send("fix issue #12")]
+    (first, first_tools), (second, second_tools) = llm.calls
+    assert first[0] == second[0] and first_tools == second_tools  # same system prompt and tools: cached prefix
+    assert second[:len(first)] == first  # history is append-only
+    assert skill.body in second[-1]["content"] and second[-1]["role"] == "tool"

````

**[command]** exit=0

````
S=<local path> cd $S && chmod +x skills/ci-failure-triage/scripts/first_error.sh && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$S:$HOME/projects/loola-test-task/src uv run --no-project -p 3.13 --with pyyaml --with pytest --with pytest-asyncio --with httpx --with jsonschema pytest -q -p no:cacheprovider -o asyncio_mode=auto tests 2>&1 | tail -15
````

````
Installed 19 packages in 72ms
<local path> PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
......                                                                   [100%]
6 passed in 0.82s
````

<details><summary>reasoning</summary>

````
The six tests pass, and the eager-loading test does check that the skill body is inline. I also want to confirm the integration test really asserts the body appears in the tool content, so nothing is passing silently. Next I'll run first_error.sh, then measure token counts for lazy versus eager loading on three demo skills, using tiktoken's o200k encoding, and for anthropics/skills to see scale. I'll clone that repo into a scratch directory and only read its text without executing anything.
````
</details>

<details><summary>reasoning</summary>

````
Все 6 тестов проходят на реальном SDK; сейчас сравниваю расход токенов lazy и eager на трёх демо-скиллах и на наборе anthropics/skills.
````
</details>

**[command]** exit=1

````
S=<local path> mkdir -p $S/ext && cd $S/ext && git clone -q --depth 1 https://github.com/anthropics/skills.git anthropic-skills 2>&1 | tail -2; ls anthropic-skills/skills | head -30; printf 'step 1\nok\nnpm ERR! missing script: build\nmore\n' > /tmp/ci.log && $S/proto/skills/ci-failure-triage/scripts/first_error.sh /tmp/ci.log
````

````
Exit code 1
academy-guide
algorithmic-art
brand-guidelines
canvas-design
claude-api
discernment-nudge
doc-coauthoring
docx
frontend-design
internal-comms
mcp-builder
pdf
pptx
skill-creator
slack-gif-creator
theme-factory
web-artifacts-builder
webapp-testing
xlsx
No error-looking lines in /tmp/ci.log
````

<details><summary>reasoning</summary>

````
I'm writing a regex that should match error and fail terms case-insensitively, so it also catches things like "err!" and "traceback". I'm also noting that "0 errors" will produce false positives, which is fine for this demo.

Still writing the regex pattern...
````
</details>

**[agent]**

Скрипт не поймал `npm ERR!` — расширю паттерн (case-insensitive) и перепроверю.

**[command]** exit=0

````
S=<local path> cat > $S <<'SH'
#!/usr/bin/env bash
# Print the first error-looking line of a CI log with 5 lines of context before and 20 after.
set -euo pipefail
line=$(grep -n -m1 -i -E '\b(error|err!|fail(ed|ure)?|traceback|panic)\b' "$1" | cut -d: -f1) || {
  echo "No error-looking lines in $1"; exit 1; }
sed -n "$((line > 5 ? line - 5 : 1)),$((line + 20))p" "$1"
SH
chmod +x $S; $S /tmp/ci.log; printf 'ok\n' > /tmp/ok.log; $S /tmp/ok.log; echo "exit=$?"
````

````
No error-looking lines in /tmp/ci.log
No error-looking lines in /tmp/ok.log
exit=1
````

<details><summary>reasoning</summary>

````
I'm checking a regex: `err!\b` won't match "ERR!" because there's a space after the `!`, so no word boundary sits there. I'll restructure the alternation so `err!` stands alone without the trailing `\b`, and keep the boundary only on the word-based alternatives.
````
</details>

**[agent]**

`\b` после `!` не срабатывает (оба символа не-словесные). Чиню группировку.

**[command]** exit=1

````
S=<local path> sed -i "s/'\\\\b(error|err!|fail(ed|ure)?|traceback|panic)\\\\b'/'\\\\b(err!|(error|fail(ed|ure)?|traceback|panic)\\\\b)'/" $S && sed -n 4p $S && $S /tmp/ci.log; printf 'a\nFAILED tests/test_x.py::test_y - AssertionError\n' > /tmp/py.log && $S /tmp/py.log; printf 'errors=0 ok\n' > /tmp/n.log; $S /tmp/n.log
````

````
Exit code 1
line=$(grep -n -m1 -i -E '\b(err!|(error|fail(ed|ure)?|traceback|panic)\b)' "$1" | cut -d: -f1) || {
step 1
ok
npm ERR! missing script: build
more
a
FAILED tests/test_x.py::test_y - AssertionError
No error-looking lines in /tmp/n.log
````

<details><summary>reasoning</summary>

````
I've confirmed the rule checks pass with no errors. Next I'm measuring token counts using the o200k_base tiktoken encoding as a proxy: the base system prompt, the lazy and eager sections for the three-skill demo, and the 19 Anthropic skills under both loading modes. I also want to check whether any frontmatter fields like license or long descriptions affect the numbers, and that the loader handles name mismatches correctly.
````
</details>

**[agent]**

Скрипт работает (и не ловит ложное `errors=0`). Теперь замер токенов (tiktoken `o200k_base` как прокси токенайзера).

**[command]** exit=0

````
S=<local path> cd $S/proto && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$S/proto:$HOME/projects/loola-test-task/src uv run --no-project -p 3.13 --with pyyaml --with tiktoken --with httpx --with jsonschema - "$S" <<'PY' 2>&1 | tail -20
import sys
from pathlib import Path
import tiktoken
from loola_agent.agent import SYSTEM_PROMPT
from loola_skills.skills import load_skills, skills_prompt
enc = tiktoken.get_encoding("o200k_base")
n = lambda s: len(enc.encode(s))
root = Path(sys.argv[1])
print("base system prompt", n(SYSTEM_PROMPT))
for label, d in [("demo-3", root/"proto/skills"), ("anthropic", root/"ext/anthropic-skills/skills")]:
    try:
        sk = load_skills(d)
    except ValueError as e:
        print(label, "ERR", e); continue
    lazy, eager = n(skills_prompt(sk)), n(skills_prompt(sk, eager=True))
    print(f"{label}: {len(sk)} skills | lazy section {lazy} tok ({lazy/len(sk):.0f}/skill) | eager {eager} tok | bodies min/median/max",
          sorted(n(s.body) for s in sk)[0], sorted(n(s.body) for s in sk)[len(sk)//2], max(n(s.body) for s in sk))
PY
````

````
Installed 18 packages in 87ms
base system prompt 90
demo-3: 3 skills | lazy section 392 tok (131/skill) | eager 974 tok | bodies min/median/max 252 255 264
anthropic ERR <local path> description must be 1-1024 chars
````

<details><summary>reasoning</summary>

````
I'm noticing the claude-api description runs past 1024 characters, which breaks the spec cap. The loader will reject it on purpose since we own these skills. For measurement only, I'll have the script parse each one separately and skip the invalid ones, leaving the loader alone.
````
</details>

<details><summary>reasoning</summary>

````
Описание `claude-api` в `anthropics/skills` длиннее лимита спеки в 1024 символа, поэтому наш loader его отвергает. Для замера исключу такие файлы на уровне скрипта, а не loader'а.
````
</details>

**[command]** exit=0

````
S=<local path> cd $S/proto && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$S/proto:$HOME/projects/loola-test-task/src uv run --no-project -p 3.13 --with pyyaml --with tiktoken --with httpx --with jsonschema - "$S" <<'PY' 2>&1 | tail -20
import sys
from pathlib import Path
import tiktoken
from loola_skills.skills import _parse, skills_prompt
enc = tiktoken.get_encoding("o200k_base"); n = lambda s: len(enc.encode(s))
root = Path(sys.argv[1]) / "ext/anthropic-skills/skills"
sk, bad = [], []
for p in sorted(root.glob("*/SKILL.md")):
    try: sk.append(_parse(p.resolve()))
    except ValueError as e: bad.append(str(e).split(": ",1)[1][:60] + " :: " + p.parent.name)
lazy, eager = n(skills_prompt(sk)), n(skills_prompt(sk, eager=True))
b = sorted(n(s.body) for s in sk)
print(f"anthropic: {len(sk)} valid, rejected={bad}")
print(f"lazy {lazy} tok ({lazy/len(sk):.0f}/skill), eager {eager} tok; bodies min/median/max {b[0]}/{b[len(b)//2]}/{b[-1]}")
for turns in (10, 30):
    print(f"{turns} turns: extra prompt tokens eager-lazy = {(eager-lazy)*turns}")
PY
````

````
anthropic: 18 valid, rejected=['description must be 1-1024 chars :: claude-api']
lazy 2944 tok (164/skill), eager 43309 tok; bodies min/median/max 239/1972/7171
10 turns: extra prompt tokens eager-lazy = 403650
30 turns: extra prompt tokens eager-lazy = 1210950
````

<details><summary>reasoning</summary>

````
I'm comparing the numbers so far, then turning to option B, which raises code size and how compaction re-attaches skills, along with option C. I also need to look at the static system prompt line about re-reading a skill after it drops out of the conversation, and whether the compaction summary should list the skills in use by name. Since the compaction module writes that summary itself, I'm considering adding a bullet for skills being followed.

I'm weighing the compaction side now: the static system prompt line about re-reading a skill that has dropped out of the conversation, and whether the compaction summary should name the skills in use. I'm also checking the cache angle, since the skill listing sits in the system prompt and stays stable because it loads once at startup. The main risk with lazy loading is that the model never reads the skill, so I'd track how often the SKILL.md read appears in the transcript and compare success rates against eager mode.

I'm now weighing whether a bash `cat` of a large SKILL.md gets cut off by the 10k-byte output limit, since bigger skills could exceed that and lose their middle. The truncation marker already points to `sed -n` for reading the rest, so the risk is mainly about skill size. I'm considering keeping SKILL.md under about 10KB and moving longer material into references, possibly with a load-time check.

I'm weighing option B against the lazy-load approach: a `load_skill` tool with a small code footprint, where the compaction harness could re-attach skill bodies after a summary because those tool results are easy to find. The catalog can stay static in the system prompt or tool description either way, and the tool list is fixed at session start, so the cache isn't affected.

Now I'm weighing option C against the others: putting skills into tool_search would mean search results return each skill's name, description, and location, which is about fifteen lines of code. It also changes what tool_search returns, since the results would mix kinds of entries. More importantly, the model would have to decide to search for a skill before it could use one, which works against keeping the catalog always visible. That costs nothing in prompt space even with many skills, and the cache stays intact. Compaction would work the same way as option A, re-searching and re-reading, but under-triggering would be much more likely, so I'm leaning against it.

Settling on option A as the recommendation, since lazy loading keeps the catalog small and the cache stable. Next I'm sketching the CLI wiring: a `--skills` path plus a `--skills-mode` flag that defaults to lazy.

Now I'm wiring the CLI: a `--skills` path plus a `--skills-mode` flag that defaults to lazy, with the skills prompt appended to the system prompt in either case. The loader and its exports go in `skills.py`, and the demo skills live under `examples/skills/`.

I'm sketching the measurement plan now: a matrix of no skills, eager, and lazy modes on the same long task, repeated several times per mode. For each run I'd track total prompt tokens, cached tokens, turn count, and status, plus whether the SKILL.md read shows up in the tool events and whether the skill's steps were actually followed.

I'm planning the measurement now: a table of prompt tokens per request for both the demo and Anthropic skill sets, and a way to observe effects on a real run. Since the directory takes only one path, I'd copy both sets into a temporary folder for that run rather than add multiple `--skills` flags. I'm leaving the Anthropic skills out of the repo because some of them are source-available and shouldn't be vendored, so I'd measure against them locally only. On caching, lazy mode means the SKILL.md read lands in the conversation tail and gets cached as part of the history prefix on later turns, while eager mode puts every body in the system prompt instead.

Cache hits shrink the dollar gap, since cached prefix tokens are billed much lower on providers li
… [2274 more characters truncated]
````
</details>

<details><summary>reasoning</summary>

````
Подсчёт готов: каталог занимает 392 токена против 974 у трёх демо-скиллов, а у 18 скиллов Anthropic — 2 944 против 43 309 на каждый запрос. Заодно проверю, что Bash-инструмент обрезает вывод на 10 000 байт, и большой SKILL.md может обрезаться посередине.
````
</details>

**[command]** exit=0

````
S=<local path> wc -c $S/proto/skills/*/SKILL.md | tail -4; echo; for f in $S/ext/anthropic-skills/skills/*/SKILL.md; do echo "$(wc -c <$f) $(basename $(dirname $f))"; done | sort -n | awk '{a[NR]=$0} END{print "count>10000:"; for(i=1;i<=NR;i++){split(a[i],x," "); if(x[1]>10000) print "  "a[i]}}'; grep -c "" $S/proto/loola_skills/skills.py; grep -cv '^\s*\(#\|$\)' $S/proto/loola_skills/skills.py
````

````
1251 <local path>
1230 <local path>
1208 <local path>
3689 total

count>10000:
  10592 discernment-nudge
  11129 mcp-builder
  11939 canvas-design
  15815 doc-coauthoring
  19769 algorithmic-art
  28365 pptx
  33168 skill-creator
  105146 claude-api
59
48
````

<details><summary>reasoning</summary>

````
I've confirmed that 7 of the 19 skills exceed the 10KB limit, which means a plain `cat` would truncate them. The fix I'm leaning toward is keeping each SKILL.md under the limit and moving long material into references/, since the truncation marker tells the model to page through with `sed -n`, so it isn't silent. I can also mention two options: document the paging convention, or have load_skills reject oversized skills up front.

I'm weighing a prompt change: adding a line telling the model to read the rest with `sed -n` if a `cat` is truncated, which costs roughly 15 tokens. I'll add it to the skills prompt and update the prototype to read SKILL.md completely, then rerun the tests and recompute the lazy token costs.
````
</details>

<details><summary>reasoning</summary>

````
Подтвердилось: 7 из 19 скиллов Anthropic весят больше 10 КБ и обрезаются `cat`. Обрезка видна по маркеру, поэтому добавлю в промпт Codex фразу дочитывать до конца файла и перепроверю тесты и замер.
````
</details>

**[file change]**

`<local path>` (update)

````
--- a<local path>
+++ b<local path>
-            "description, read its SKILL.md with bash (`cat <location>`) before acting and follow it. Resolve "
+            "description, read its whole SKILL.md with bash (`cat <location>`; if the output is truncated, read "
+            "the rest with `sed -n`) before acting and follow it. Resolve "

````

**[command]** exit=0

````
S=<local path> cd $S && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$S:$HOME/projects/loola-test-task/src uv run --no-project -p 3.13 --with pyyaml --with pytest --with pytest-asyncio --with httpx --with jsonschema --with tiktoken pytest -q -p no:cacheprovider -o asyncio_mode=auto -W ignore tests 2>&1 | tail -2 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$S:$HOME/projects/loola-test-task/src uv run --no-project -p 3.13 --with pyyaml --with tiktoken --with httpx --with jsonschema - <<'PY'
from pathlib import Path
import tiktoken
from loola_skills.skills import load_skills, skills_prompt
n = lambda s: len(tiktoken.get_encoding("o200k_base").encode(s))
sk = load_skills(Path("skills"))
print("demo lazy", n(skills_prompt(sk)), "eager", n(skills_prompt(sk, eager=True)))
print(skills_prompt(sk)[:900])
PY
````

````
......                                                                   [100%]
6 passed in 0.57s
demo lazy 408 eager 974
## Skills
Skills are instructions for specific kinds of tasks. When a task matches a skill's description, read its whole SKILL.md with bash (`cat <location>`; if the output is truncated, read the rest with `sed -n`) before acting and follow it. Resolve relative paths in a skill against the directory of its SKILL.md. If a skill you are following is no longer in the conversation (older messages get summarized), read it again.
<available_skills>
<skill><name>ci-failure-triage</name><description>Find why a GitHub Actions run failed and fix it. Use when CI, a workflow run, a check, or a build is red, or when asked why tests fail on GitHub but not locally.</description><location><local path>></skill>
<skill><name>fix-github-issue</name><description>Fix a bug reported in a G
````

<details><summary>reasoning</summary>

````
Now I'm working out how the report should be laid out: a Russian heading for the loola-agent skills design, a TL;DR with the recommendation, and a first section comparing how other systems handle this, starting with the Agent Skills spec.

Now I'm planning the report's remaining sections: how the other systems (Claude Code, Codex, Pi) place their catalogs and bodies and handle compaction, then the constraints that matter for us, the three options compared, and the recommended approach with its code sketch and open risks.
````
</details>

**[agent]**

Прототип готов и проверен (6/6 тестов, замеры). Пишу отчёт.

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+# Скиллы в loola-agent: дизайн
+
+## TL;DR
+
+Рекомендую вариант A, так же устроены Agent Skills, Pi и Codex. В system prompt кладём только каталог: name, description и путь к SKILL.md. Тело модель читает сама через `bash cat`, и оно попадает в историю обычным `ToolResult`. Новых тулов нет, `Agent`, `Toolbox` и `build_context` не меняются. Это один модуль `skills.py` (~50 строк) плюс два флага CLI. System prompt фиксируется на всю сессию, поэтому префикс кэшируется. Compaction system prompt не трогает, так что каталог переживает её всегда. Если тело скилла ушло в summary, модель перечитывает файл: про это одна статичная фраза в секции скиллов и пункт «active skills» в промпте суммаризатора. Для замера «до/после» есть флаг `--skills-mode eager|lazy`, он симметричен уже существующему `--catalog-mode direct|deferred`.
+
+Прототип и демо-скиллы лежат в [reports/skills/proto](<local path>). 6 тестов проходят против текущего SDK из репо, в репо я ничего не менял.
+
+Замер prompt-токенов на каждый запрос (tiktoken `o200k_base`):
+
+| Набор | lazy (каталог) | eager (все тела) | Разница × 30 ходов |
+|---|---|---|---|
+| 3 демо-скилла (GitHub) | 408 | 974 | ~17k |
+| 18 скиллов из `anthropics/skills` | 2 944 (~164/скилл) | 43 309 | ~1.2M |
+
+## 1. Как это устроено у других
+
+Везде одна и та же трёхуровневая progressive disclosure из [спеки Agent Skills](https://agentskills.io/integrate-skills). Уровень 1: каталог name + description, около 50–100 токенов на скилл, виден всегда. Уровень 2: тело SKILL.md (рекомендуется меньше 5k токенов), грузится, когда модель решила, что скилл нужен. Уровень 3: `scripts/`, `references/`, `assets/` рядом с SKILL.md, читаются по ссылкам из тела. Различаются системы деталями: где лежит каталог, кто грузит тело и что с ним происходит при compaction.
+
+| | Каталог | Как грузится тело | Куда попадает | Compaction |
+|---|---|---|---|---|
+| **Agent Skills (спека)** | Секция system prompt **или** описание тула активации, оба варианта легитимны. Формат `<available_skills>` с name/description/location | File-read (модель читает своим тулом) **или** отдельный `activate_skill(name)` с enum имён | Tool result | Советует «exempt skill content from pruning», например помечать результаты тула активации тегами |
+| **Claude Code** | Отдельный листинг в контексте (в этой сессии он приходит `system-reminder`-сообщением, а не в system prompt). Бюджет ~1% окна, description ≤1536 символов | Тул `Skill`: тело входит в разговор одним сообщением и не перечитывается. Повторный вызов того же скилла даёт короткую заметку вместо копии | Сообщение в хвосте | **Re-attach**: после summary заново прикладывает последнюю загрузку каждого скилла, первые 5k токенов каждого, всего ≤25k, начиная со свежих ([docs](https://code.claude.com/docs/en/skills)) |
+| **Codex** | Developer-фрагмент `## Skills`: name + description + path и длинный блок «How to use skills». Бюджет 2% окна или 8k символов ([catalog_prompt.rs](https://github.com/openai/codex/blob/main/codex-rs/ext/skills/src/catalog_prompt.rs), [docs](https://learn.chatgpt.com/docs/build-skills)) | Модель сама открывает SKILL.md («read completely… if truncated, continue until EOF»). Явный `$skill` инжектит `<skill><name/><path/>body</skill>` user-фрагментом ([fragments.rs](https://github.com/openai/codex/blob/main/codex-rs/ext/skills/src/fragments.rs)) | Tool result или user-фрагмент | По `compact.rs`: остаются реальные user-сообщения и summary, initial context (с каталогом) вставляется заново. Тела скиллов отдельно не сохраняются |
+| **Pi** | Секция `skills` system prompt: `<available_skills>` с name/description/location и фраза «Use the read tool to load a skill's file…» ([skills.js](<local path>)). Без read/bash-тула сек
… [18358 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking whether my uv run wrote anything into the repo. With PYTHONDONTWRITEBYTECODE and PYTHONPATH pointed at the repo's src, I don't think it did. Another agent may be writing there too, so I'll leave git status alone. Next I'm putting together the final answer: a brief summary with a recommendation and the key details.
````
</details>

**[agent]**

Отчёт готов: [skills-design.md](<local path>). Рядом лежит рабочий прототип: [reports/skills/proto](<local path>). Его 6 тестов проходят против текущего SDK из репо; сам репо я не трогал.

**Рекомендация: в system prompt только каталог скиллов, тело модель читает через `bash cat`** (вариант A). Так советует спека Agent Skills, и так делают Pi и Codex.

- **Как работает:** в system prompt одна секция `## Skills` с `<available_skills>`, где у каждого скилла name, description и путь к SKILL.md. Когда задача подходит под описание, модель делает `cat`, и тело приходит обычным `ToolResult` в хвост истории.
- **Объём кода:** `skills.py` на ~50 строк (`Skill`, `load_skills`, `skills_prompt`) и ~6 строк в CLI (`--skills DIR`, `--skills-mode lazy|eager`). `Agent`, `Toolbox` и `build_context` не меняются. Добавляется зависимость `pyyaml`.
- **Prompt cache:** секция собирается один раз на старте и сортируется по имени, так что байты стабильны. Массив tools не меняется, тело скилла дописывается в хвост. Сквозной тест это подтверждает: system prompt и tools в запросах до и после `cat` совпадают байт-в-байт.
- **Compaction:** system prompt она не трогает, поэтому каталог остаётся всегда. Если тело скилла ушло в summary, модель перечитывает файл. Для этого в секции есть статичная фраза «перечитай скилл, если его больше нет в разговоре», а в промпт суммаризатора нужно добавить пункт «какие скиллы используются». Повторное чтение стоит ~300 токенов. Claude Code вместо этого сам заново прикладывает тела после summary. Это стоит добавлять, только если замер покажет, что модель не перечитывает скилл.
- **Замер «до/после»:** `--skills-mode eager` кладёт все тела в system prompt, `lazy` — только каталог. Это симметрично существующему `--catalog-mode`.

Сколько prompt-токенов уходит на каждый запрос:

| Набор | lazy (каталог) | eager (все тела) |
|---|---|---|
| 3 демо-скилла | 408 | 974 |
| 18 скиллов из `anthropics/skills` | 2 944 | 43 309 |

Почему не два других варианта:
- **Отдельный тул `load_skill`** (как в Claude Code) даёт точный учёт загруженных скиллов, но это лишний тул при работающем `bash` и дополнительная логика в compaction.
- **Скиллы в `tool_search`** нарушают главный принцип спеки: каталог должен быть виден всегда. Модель чаще не догадается загрузить нужный скилл, а без `--catalog` скиллы вообще не работают.

**Демо-скиллы.** Все три описывают GitHub-задачи поверх уже существующих deferred-тулов; имена тулов и параметров сверены с `github_tools.json`.
- `fix-github-issue`: от issue до PR с `Fixes #n`.
- `ci-failure-triage`: разбор упавшего CI, с готовым скриптом `first_error.sh`, который находит первую ошибку в логе.
- `review-pull-request`: review одним пакетом комментариев плюс вердикт, с чеклистом в `references/checklist.md`.

**Что всплыло при проверке:**
- **Обрезка длинных файлов.** Bash-тул отдаёт максимум 10 КБ вывода, а у 7 из 19 скиллов Anthropic SKILL.md больше. Обрезка видна модели (маркер подсказывает `sed -n`), и в секцию я добавил фразу «если вывод обрезан, дочитай через `sed -n`». Свои скиллы держим меньше 10 КБ.
- **Строгая проверка вместо мягкой.** Спека советует грузить кривые скиллы с предупреждением, но мы грузим только свои, поэтому невалидный SKILL.md — ошибка старта с путём к файлу. На `anthropics/skills/claude-api` это сработало: description длиннее 1024 символов, и loader его отклонил.
- **Оговорка для итогового отчёта.** Когда кэш префикса работает, тела в eager-режиме тоже кэшируются, и разница в деньгах сжимается до цены закэшированных токенов. Основной выигрыш lazy — в бюджете контекстного окна и внимании модели. Поэтому в замере показываем prompt- и cached-токены рядом с успешностью.

<details><summary>Как это устроено в Claude Code, Codex и Pi (проверено по докам и исходникам)</summary>

- **Agent Skills (спека):** три уровня загрузки: каталог (~50–100 токенов на скилл), тело (меньше 5k токенов), файлы рядом. Каталог можно положить в system prompt или в описание тула активации. Активировать скилл можно чтением файла или отдельным тулом. При compaction спека советует защищать содержимое скиллов от удаления.
- **Claude Code:** листинг скиллов приходит отдельным сообщением, его бюджет ~1% окна. Тело загружается тулом `Skill` одним сообщением и не перечитывается. После compaction Claude Code заново прикладывает тела скиллов: до 5k токенов на каждый и до 25k суммарно.
- **Codex:** секция `## Skills` (name, description, путь) в developer-сообщении, бюджет 2% окна. Модель сама читает SKILL.md до конца файла. Явное упоминание `$skill` вставляет тело user-сообщением `<skill>`. При compaction (по `compact.rs`) каталог вставляется заново, тела скиллов отдельно не сохраняются.
- **Pi:** `<available_skills>` в system prompt, тело читается тулами `read`/`bash`. После compaction в summary попадает список прочитанных файлов `<read-files>`, но только для `read`-тула.

</details>

<details><summary>Тесты в прототипе</summary>

1. Демо-скиллы загружаются отсортированными, тело без frontmatter, путь абсолютный.
2. Невалидный SKILL.md падает с `ValueError`, в сообщении путь к файлу.
3. Секция lazy содержит каталог без тел, eager — все тела.
4. Сквозной тест с fake LLM и настоящим `Bash`: `cat SKILL.md` не меняет system prompt и tools, история только дописывается, тело приходит в `role: tool`.
5. Когда появится compaction, к её тестам стоит добавить проверку, что system prompt, а значит и каталог, одинаков до и после события.

</details>
