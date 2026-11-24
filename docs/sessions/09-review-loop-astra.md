# Sub-agent: review loop (Codex, GPT-6.2 Astra)

Full bb session log, converted from the raw event stream: inputs, agent messages, reasoning, commands with output, file changes and tool calls (long outputs truncated to 4000 characters). Local paths, thread ids and emails are redacted; outputs that came from the developer's private projects are replaced with a placeholder.

---

## [input]

Review this artifact critically. Do it yourself and do not delegate. Focus on bugs, spec mismatches, runtime risks, invariants, test gaps, scope control, and overbuilding relative to the request. Return findings ordered by severity with concrete file:line references. Avoid long summaries.

Also review against the attached review contract (brief). Treat drift from the owner's goal, and unapproved loss of a requirement, as material issues.

Artifact: the whole repo ~/projects/loola-test-task at commit 63a090c (public: https://github.com/toolittlecakes/loola-agent). Read TASK.md, src/loola_agent/*.py, tests/*.py, skills/, pyproject.toml. Do not modify any files, do not commit (another agent is writing README.md there in parallel). You may run the test suite (uv run pytest -q) and small read-only experiments in /tmp.

Review contract (brief v1, the owner's framing — do not argue with its goals and approved decisions, judge the work through them): <local path>

What I want from you, specifically:
1. Real defects: correctness bugs, broken invariants (especially the compaction guarantee, prompt-cache stability of the declared tools/system prompt, protocol correctness of message history, cancellation), test gaps that hide bugs.
2. Places where the code is more complex than this minimalist showcase needs: what to cut or simplify, with the concrete simpler form. Approved decisions in the brief are not up for debate, but a simpler implementation of the same decision is welcome.
3. Anything we did not account for that matters for the task (TASK.md) — e.g. answers to its two questions, the before/after measurement plan.
Do NOT propose enterprise hardening, new abstractions, fallbacks, or features listed as out of scope in the brief.

Finish with a binary verdict: "fully approved" or "not approved" + remaining blockers only (blocker = materially affects correctness, the task requirements, or the owner's stated goal).

**[agent]**

I’ll review commit `63a090c` directly against the brief and `TASK.md`, using the committed files so the parallel README edit stays untouched. I’ll check the runtime invariants against the tests and use `/tmp` for any reproductions.

**[command]** exit=0

````
/bin/bash -lc "git -C ~/projects/loola-test-task rev-parse --verify '63a090c"'^{commit}'"' && git -C ~/projects/loola-test-task ls-tree -rl 63a090c"
````

````
63a090ce084171645dcc976136fa9b1b1b6c95c1
100644 blob 247f79f82e384492ca8171e5435800a3a4355d79     595	.env.example
100644 blob 110b0a608acee254173b876f4ce76f585c01a253     114	.gitignore
100644 blob 24ee5b1be9961e38a503c8e764b7385dbb6ba124       5	.python-version
100644 blob 026f8d164e33e15c2be59f93f402824c30a19893    5476	TASK.md
100644 blob 8d3be8b92df14ba9d9cd3cad896264a3ef869e9c  168509	examples/github_tools.json
100644 blob fee70ab3e8266458bfacc2d02129816e06eeb871     646	pyproject.toml
100644 blob e72322625ea9bff827fec86a119b946d0486e091    1265	skills/ci-failure-triage/SKILL.md
100755 blob 3741374c5920b4e75feea2821fd44d06f8b9c645     341	skills/ci-failure-triage/scripts/first_error.sh
100644 blob 666c6e855e62ef1929837ff2e275f18178b9a014    1244	skills/fix-github-issue/SKILL.md
100644 blob c53a6caea4379ece47681bfa00481c286be971b7    1222	skills/review-pull-request/SKILL.md
100644 blob 92ced5f8ebcb699d7788227c431e2d98c6b6f488     533	skills/review-pull-request/references/checklist.md
100644 blob 70328ec27773915785890ab51bd9126ed4159f40    1174	src/loola_agent/__init__.py
100644 blob 74169ccb3bb832f75901ef59f6643f90e9088036    6651	src/loola_agent/agent.py
100644 blob 88971f7490605fafbd0ffaadb94ea64ed2f47f37    3533	src/loola_agent/bash.py
100644 blob 837748311c7deef5b6ea3cb29ee48bf38e37e3ba     876	src/loola_agent/catalog.py
100644 blob ce4c39a98a4a7a924bc920bf0d446423e6811b27    5636	src/loola_agent/cli.py
100644 blob 9d7a8168052d551999eb6d29310f9a3f044022a2    5959	src/loola_agent/compaction.py
100644 blob ed4691bf6d972ce8b1faa5106793c76a64dc05f9    3393	src/loola_agent/events.py
100644 blob c3e4b1a9c753ca67229bca5e6c5c4ea437116ea5   13965	src/loola_agent/gh_proxy.py
100644 blob 36d6fdbcea25024ef82636b8bcfcfde595c57f86    4132	src/loola_agent/llm.py
100644 blob ebe309e3243e58656f5a02336015c71ae84416e3    3231	src/loola_agent/skills.py
100644 blob 5f0f769e7507b5ae848e2b6592ae7b8ee282b5d3    6109	src/loola_agent/tools.py
100644 blob 71799d299e639c5573387b132219e1b40c2cd95b    5292	tests/test_agent.py
100644 blob 2c2cca8ab46124aea2b5f5160bb59872efd69e02    7855	tests/test_compaction.py
100644 blob 97459c86cd5e230dc911211cdcbf0c1b5d356fea    5103	tests/test_deferred.py
100644 blob 11ba4d430d104b5c622ada4bb11a469608a1f455    9306	tests/test_gh_proxy.py
100644 blob 0b56d9cc4c3365b4d713ed516d23b978d09bba20    3104	tests/test_llm.py
100644 blob 8784ee440f551e94e4fcef2c04ef04ad6f1e387d    2992	tests/test_skills.py
100644 blob 16ee299fea6da54383c68bc364536f92fb326844    3535	tests/test_tools.py
100644 blob 17826eb43b42e2a5d9f916e062eaa04d8527283a   53389	uv.lock
````

**[command]** exit=0

````
/bin/bash -lc 'cat <local path>'
````

````
# Brief: loola-agent (контекст, цели, решения) — v1

Репо: https://github.com/toolittlecakes/loola-agent (локально `~/projects/loola-test-task`), состояние на коммите `63a090c`. Задание: `TASK.md` в репо.

## Задание (кратко)

Тестовое задание: минимальный coding-agent harness (исходно ~100 строк на Python, один тул `bash`, OpenAI-compatible `/v1/chat/completions`, вероятно self-hosted vLLM). Нужно: (1) динамическая подгрузка тулов/скиллов, чтобы не держать десятки описаний в промпте; (2) умный context compaction при переполнении окна; (3) замер на длинной многошаговой задаче до/после: токены и успешность; (4) улучшить код на свой вкус; (5) ответить на 2 вопроса: как делать compaction и подгрузку без инвалидации prompt cache (KV-cache префикса); какие ошибки тулов отдавать модели, а какие перехватывать детерминированно в harness. Если делали с агентом — оставить AGENTS.md и лог сессии.

## Цель и принципы владельца (это рамка, с ней не спорить)

- Это **минималистичный showcase**, а не продукт. Читаемость за минуты важнее полноты. Никакого enterprise-комбайна, никаких «на всякий случай».
- Оверинжиниринг — главный враг. Если можно проще без потери смысла — проще. Предлагать сокращения кода приветствуется.
- **Один явный путь, fail fast.** Никаких fallback-веток, деградированных режимов, запасных парсеров, тихих ретраев «чтобы заработало». Ошибка — видимая, с понятным сообщением.
- Ошибки модели (кривые аргументы, неизвестный тул, ненулевой exit code) возвращаются модели текстом для самоисправления; ошибки инфраструктуры и баги harness — исключения на границе (CLI).
- Протокол виден: без фреймворков и даже без `openai` SDK (httpx + wire format).
- Async by design + явное разделение слоёв, чтобы вокруг SDK можно было построить CLI/TUI/web (оболочки, кроме CLI, не строим).

## Архитектура (src/loola_agent)

- `llm.py` — протокол `LLM` + `OpenAICompatibleLLM` (httpx, timeout, retry только на 429/5xx/transport, 4xx fail fast с телом, `max_completion_tokens`, temperature опциональна, свой User-Agent, опциональный per-conversation session header).
- `events.py` — события сессии (append-only список) и `build_context` — чистая проекция событий в messages.
- `agent.py` — `Agent.send()` → AsyncIterator[Event]: цикл, закрытие прерванных tool calls, вызов компакшена.
- `tools.py` — протокол `Tool`, `Toolbox`: JSON Schema валидация (jsonschema), direct/deferred тулы, `tool_search` (свой BM25), `tool_call`.
- `bash.py` — bash-тул; `compaction.py` — политика/граница/выбор среза; `skills.py` — Agent Skills; `catalog.py` — каталог-пример + DummyTool; `gh_proxy.py` — read-only прокси к `gh` для живых прогонов; `cli.py` — оболочка.

## Решения на развилках (и почему) — одобрены владельцем

1. **Базовые фиксы исходного кода** (ревью нашло): assistant message кладём в историю как есть (параллельные tool calls, `reasoning_content` — DeepSeek без него 400); кривой JSON аргументов → ошибка модели; обрезка вывода head+tail; timeout/retry; `finish_reason=length` и пустой ответ = провал, а не успех; учёт usage; bash: stdin закрыт, `LLM_*` не видны командам, вывод в temp-файл (фон `cmd &` не блокирует, частичный вывод при таймауте), kill process group по таймауту/отмене/выходу.
2. **Фоновые процессы**: только правило в описании bash-тула (`cmd > log 2>&1 &`), никаких bash_output/kill тулов — оверкилл.
3. **Динамические тулы без нативного API**: массив `tools` никогда не меняется (у open-source chat templates tools рендерятся в начало промпта → любое изменение = полный промах KV-cache). В промпте: direct-тулы + `tool_search` + `tool_call(name, arguments)`. Схемы найденных тулов приходят как tool result (в хвост истории).
4. **Constrained decoding / `strict` не используем вообще** (владелец: не поддерживать несколько вариантов). У vLLM при `tool_choice=auto` без strict его и так нет. Компенсация — валидация по JSON Schema в harness, ошибка со схемой уходит модели.
5. **После компакшена найденные тулы НЕ добавляем в `tools`** и не «вспоминаем» тулы/скиллы яв
… [3935 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'reviewdir=$(mktemp -d /tmp/loola-review.XXXXXXXX) && git -C ~/projects/loola-test-task archive 63a090c | tar -x -C "$reviewdir" && realpath "$reviewdir"'
````

````
/tmp/loola-review.iTsTm7q4
````

**[command]** exit=0

````
/bin/bash -lc 'for f in src/loola_agent/{compaction,agent,events,llm}.py; do echo "$f"; nl -ba "$f"; done'
````

````
src/loola_agent/compaction.py
     1	"""Context compaction: when the next request might not fit, replace older history with a model-written summary.
     2	
     3	Guarantee (assuming a token is at least one UTF-8 byte, true for BPE tokenizers):
     4	- the size of the next request is bounded from above: exact server counts for what was already sent and
     5	  generated (prompt + completion of the last request), UTF-8 bytes for what was not measured yet;
     6	- a regular request is sent only if `bound + max(reply, instruction + summary) <= context_window`, so room for a
     7	  later summary request is always reserved, whatever optional `compact_at` threshold is set;
     8	- the summary request reuses the exact context of an earlier request (a measured size that passed this check)
     9	  plus the instruction, so it fits by construction and shares that request's cached prefix. It keeps the same
    10	  tools and tool_choice: `tool_choice: "none"` makes some providers drop the tools from the prompt, which
    11	  changes the prefix and misses the cache (observed with OpenCode Go);
    12	- right after compaction the bound is `head + (bound_before - prompt_at_cut)`: the kept tail is exactly what the
    13	  old bound counted beyond the measured prefix that was summarized;
    14	- if the compacted context still does not fit, compaction fails loudly instead of looping."""
    15	import json
    16	from dataclasses import dataclass
    17	
    18	from .events import AssistantMessage, Compaction, Event, build_context, to_message
    19	
    20	MESSAGE_OVERHEAD = 16  # tokens a chat template may add around one message (role markers, separators)
    21	
    22	SUMMARY_INSTRUCTION = """\
    23	Your context is about to be compacted: everything above, except the user's own messages, will be replaced \
    24	by the summary you write now. Write it so you can continue the task without the original messages:
    25	- the goal and constraints as you understand them;
    26	- what is done and verified (with the evidence), what is in progress, what is next;
    27	- exact identifiers verbatim: file paths, commands, repositories, issue/PR numbers, SHAs, tool names, errors;
    28	- approaches that failed and why, so you do not repeat them;
    29	- skills you are following (name and SKILL.md path): re-read them before continuing their procedure.
    30	Reply with the summary only, without tool calls."""
    31	
    32	
    33	class CompactionError(RuntimeError):
    34	    pass
    35	
    36	
    37	@dataclass(frozen=True)
    38	class CompactionPolicy:
    39	    context_window: int
    40	    compact_at: int | None = None  # optional earlier trigger; the hard limit applies regardless of it
    41	    keep_recent_tokens: int | None = None  # recent history kept verbatim; default: a fifth of the trigger level
    42	    summary_max_tokens: int = 4096
    43	
    44	    @property
    45	    def keep_recent(self) -> int:
    46	        # Well below the trigger, so the compacted context does not trigger compaction again right away.
    47	        return self.keep_recent_tokens if self.keep_recent_tokens is not None else \
    48	            (self.compact_at or self.context_window) // 5
    49	
    50	    def reserve(self, reply_max_tokens: int) -> int:
    51	        instruction = _bytes(SUMMARY_INSTRUCTION) + MESSAGE_OVERHEAD
    52	        return max(reply_max_tokens, instruction + self.summary_max_tokens)
    53	
    54	    def fits(self, bound: int, reply_max_tokens: int) -> bool:
    55	        return bound + self.reserve(reply_max_tokens) <= self.context_window
    56	
    57	    def wants_compaction(self, bound: int, reply_max_tokens: int) -> bool:
    58	        return not self.fits(bound, reply_max_tokens) or (self.compact_at is not None and bound > self.compact_at)
    59	
    60	
    61	def context_bound(system_prompt: str, events: list[Event], tools: list[dict]) -> int:
    62	    """Upper bound of the prompt tokens of th
… [18996 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'for f in TASK.md pyproject.toml .env.example; do echo "$f"; nl -ba "$f"; done'
````

````
TASK.md
     1	# Test Task _ Loola 
     2	
     3	Задача: Реализуйте в харнессе два механизма: динамическую подгрузку скиллов/тулов (чтобы не держать десятки описаний инструментов в системном промпте сразу) и умный Context Compaction при переполнении окна.Проверьте агента на длинной многошаговой задаче до и после изменений, замерьте расход токенов и успешность выполнения.Улучшите этот код (на ваш вкус).
     4	
     5	! Если вы разрабатываете с помощью агента, то оставьте в коде ваш AGENTS.md, и лог вашей сессии с агентом (в любом виде)
     6	
     7	Ответьте на вопросы при выполнении?
     8	
     9	1. Как сделать compaction и подгрузку скиллов так, чтобы не инвалидировать Prompt Cache (KV-cache префикса) на каждом шаге?
    10	1. Какие ошибки тулов нужно отдавать обратно модели для само-исправления, а какие — перехватывать детерминированно на уровне харнесса?
    11	Загрузите код на github, отправьте нам ссылку.
    12	
    13	```python
    14	"""Minimal coding agent loop — one tool: bash."""
    15	import json, sys, subprocess
    16	import requests
    17	
    18	
    19	LLM_BASE_URL = "http://ip:port/v1"
    20	LLM_API_KEY = "..."
    21	LLM_MODEL = "..."
    22	LLM_HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {LLM_API_KEY}"}
    23	MAX_TURNS = 1000
    24	
    25	SYSTEM_PROMPT = """\
    26	You are a coding agent. Your job is to help the user with programming tasks.
    27	
    28	You have access to ONE tool: `bash` — which executes shell commands and returns stdout/stderr.
    29	
    30	Workflow:
    31	1. Plan what needs to be done.
    32	2. Use `bash` to read files, run commands, write code, etc.
    33	3. After gathering enough information or completing the task, give your final answer in natural language.
    34	4. To finish, reply with a regular message (no tool call).
    35	
    36	Be concise. Explain what you're doing before each command."""
    37	
    38	LLM_TOOLS = [
    39	    {"type": "function",
    40	     "function": {"name": "bash",
    41	                  "description": "Execute a shell command and return the output.",
    42	                  "parameters": {"type": "object",
    43	                                 "properties": {
    44	                                     "command": {"type": "string", "description": "The bash command to execute."}
    45	                                 },
    46	                                 "required": ["command"]}
    47	                 }
    48	            }]
    49	
    50	
    51	def run_bash(command: str) -> str:
    52	    try:
    53	        command_result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
    54	        out = command_result.stdout + (f"\nSTDERR:\n{command_result.stderr}" if command_result.stderr else "")
    55	        return f"Exit code: {command_result.returncode}\n{out}"
    56	    except subprocess.TimeoutExpired:
    57	        return "Error: command timed out after 120s"
    58	
    59	
    60	def call_tool(name: str, arguments: dict) -> str:
    61	    func = {"bash": run_bash}.get(name)
    62	    if not func:
    63	        return f"Error: unknown tool '{name}'"
    64	    try:
    65	        return func(**arguments)
    66	    except Exception as e:
    67	        return f"Error calling {name}: {e}"
    68	
    69	
    70	def call_llm(messages):
    71	    payload = {"model": LLM_MODEL, "messages": messages, "tools": LLM_TOOLS, "tool_choice": "auto",
    72	               "temperature": 0.1, "max_tokens": 4096}
    73	    llm_http_response = requests.post(f"{LLM_BASE_URL}/chat/completions", json=payload, headers=LLM_HEADERS)
    74	    llm_http_response.raise_for_status()
    75	    msg = llm_http_response.json()["choices"][0]["message"]
    76	    content = (msg.get("content") or "").strip()
    77	    tool_calls = msg.get("tool_calls") or []
    78	    return content, tool_calls
    79	
    80	
    81	def agent_loop(user_message: str) -> None:
    82	    messag
… [3202 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'for f in src/loola_agent/{bash,tools,skills,cli,catalog,__init__}.py; do echo "$f"; nl -ba "$f"; done'
````

````
src/loola_agent/bash.py
     1	"""The bash tool: non-interactive shell commands with bounded output and process-group cleanup."""
     2	import asyncio, os, signal, subprocess, tempfile
     3	from typing import IO, Self
     4	
     5	
     6	class Bash:
     7	    """Runs non-interactive shell commands. Use as an async context manager:
     8	    on exit it kills background processes the commands left behind."""
     9	
    10	    name = "bash"
    11	    parameters = {"type": "object",
    12	                  "properties": {"command": {"type": "string", "description": "The bash command to execute."}},
    13	                  "required": ["command"]}
    14	
    15	    def __init__(self, timeout: float = 120, max_output: int = 10_000):
    16	        self.timeout, self.max_output = timeout, max_output
    17	        self.description = (
    18	            f"Execute a shell command and return its exit code and combined stdout/stderr (long output is truncated). "
    19	            f"stdin is closed, so commands must not wait for input. Timeout: {timeout:g}s. "
    20	            f"Run long-lived processes (servers, watchers) in the background with output redirected to a file, "
    21	            f"e.g. `cmd > /tmp/server.log 2>&1 &`, then read the file; they are killed when the agent exits.")
    22	        self._process_groups: set[int] = set()
    23	
    24	    async def __aenter__(self) -> Self:
    25	        return self
    26	
    27	    async def __aexit__(self, *exc: object) -> None:
    28	        for pgid in self._process_groups:
    29	            _kill_group(pgid)
    30	        self._process_groups.clear()
    31	
    32	    async def run(self, args: dict) -> str:
    33	        # Output goes to a file, not a pipe: background jobs don't block the call and partial output
    34	        # survives a timeout. Each command gets its own process group, so it can be killed as a whole.
    35	        env = {k: v for k, v in os.environ.items() if not k.startswith("LLM_")}
    36	        with tempfile.TemporaryFile() as out:
    37	            proc = await asyncio.create_subprocess_shell(
    38	                args["command"], stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, env=env,
    39	                start_new_session=True)
    40	            self._process_groups.add(proc.pid)
    41	            try:
    42	                status = f"Exit code: {await asyncio.wait_for(proc.wait(), self.timeout)}"
    43	            except TimeoutError:
    44	                _kill_group(proc.pid)
    45	                await proc.wait()
    46	                status = f"Error: command timed out after {self.timeout:g}s and was killed. Output so far:"
    47	            except asyncio.CancelledError:
    48	                _kill_group(proc.pid)
    49	                raise
    50	            if not _group_alive(proc.pid):  # nothing left in background: forget it to avoid PID reuse surprises
    51	                self._process_groups.discard(proc.pid)
    52	            return f"{status}\n{self._read_head_tail(out)}"
    53	
    54	    def _read_head_tail(self, f: IO[bytes]) -> str:
    55	        size = f.seek(0, os.SEEK_END)
    56	        f.seek(0)
    57	        if size <= self.max_output:
    58	            return f.read().decode(errors="replace")
    59	        half = self.max_output // 2
    60	        head = f.read(half)
    61	        f.seek(-half, os.SEEK_END)
    62	        tail = f.read()
    63	        marker = f"\n[... {size - 2 * half} bytes truncated; use head/tail/grep/sed -n to read specific parts ...]\n"
    64	        return head.decode(errors="replace") + marker + tail.decode(errors="replace")
    65	
    66	
    67	def _group_alive(pgid: int) -> bool:
    68	    try:
    69	        os.killpg(pgid, 0)
    70	    except ProcessLookupError:
    71	        return False
    72	    return True
    73	
    74	
    75	def _kill_group(pgid: int) -> None:
    76	    try:
    77	        os.killpg(pgid, si
… [19518 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'for f in src/loola_agent/gh_proxy.py; do echo "$f"; nl -ba "$f"; done'
````

````
src/loola_agent/gh_proxy.py
     1	"""Live backend for part of the GitHub example catalog: a read-only proxy to the user's `gh` CLI.
     2	
     3	Each proxied tool turns its (already schema-validated) arguments into one `gh api` call: REST with
     4	`--method GET`, or GraphQL with a query fixed in this module, so nothing here can mutate GitHub.
     5	The arguments a mapping supports are its Python parameters; anything else the schema allows is reported
     6	to the model as not implemented instead of being silently ignored. Other catalog tools answer with an error.
     7	gh authenticates itself: the token never passes through this process."""
     8	import asyncio, inspect, json, subprocess
     9	from collections.abc import Callable, Sequence
    10	from dataclasses import dataclass
    11	from urllib.parse import quote, urlencode
    12	
    13	from .tools import Tool
    14	
    15	type Argv = list[str]  # arguments after `gh`
    16	
    17	
    18	@dataclass(frozen=True)
    19	class Unsupported:
    20	    reason: str
    21	
    22	
    23	def _repo(owner: str, repo: str) -> str:
    24	    return f"repos/{quote(owner, safe='')}/{quote(repo, safe='')}"
    25	
    26	
    27	def _rest(path: str, query: dict[str, object], jq: str | None = None, accept: str | None = None) -> Argv:
    28	    params = urlencode({k: v for k, v in query.items() if v is not None})
    29	    argv = ["api", "--method", "GET", f"{path}?{params}" if params else path]
    30	    if accept:
    31	        argv += ["--header", f"Accept: {accept}"]
    32	    return argv + ["--jq", jq] if jq else argv
    33	
    34	
    35	def _pages(page: float | None, per_page: float | None) -> dict[str, object]:
    36	    return {"page": None if page is None else int(page), "per_page": None if per_page is None else int(per_page)}
    37	
    38	
    39	def _each(fields: list[str] | None) -> str | None:
    40	    """jq that keeps only `fields` of every list element (field names come from schema enums)."""
    41	    return None if fields is None else f"map({{{', '.join(fields)}}})"
    42	
    43	
    44	def _items(fields: list[str] | None) -> str | None:
    45	    return None if fields is None else f".items |= {_each(fields)}"
    46	
    47	
    48	def get_file_contents(owner: str, repo: str, path: str = "/", ref: str | None = None, sha: str | None = None,
    49	                      fields: list[str] | None = None) -> Argv:
    50	    entry = "{" + ", ".join(fields) + "}" if fields else "."
    51	    return _rest(f"{_repo(owner, repo)}/contents/{quote(path.strip('/'))}".rstrip("/"), {"ref": sha or ref},
    52	                 jq=f'if type == "array" then map({entry}) elif .type == "file" then .content | @base64d else . end')
    53	
    54	
    55	def get_repository_tree(owner: str, repo: str, tree_sha: str | None = None, recursive: bool = False,
    56	                        path_filter: str | None = None) -> Argv:
    57	    prefix = json.dumps(path_filter or "")  # a JSON string is a valid jq string literal: no jq injection
    58	    return _rest(f"{_repo(owner, repo)}/git/trees/{quote(tree_sha or 'HEAD', safe='')}",
    59	                 {"recursive": 1 if recursive else None},
    60	                 jq=f"{{truncated, tree: [.tree[] | select(.path | startswith({prefix})) | {{path, type, size}}]}}")
    61	
    62	
    63	def list_commits(owner: str, repo: str, sha: str | None = None, path: str | None = None, author: str | None = None,
    64	                 since: str | None = None, until: str | None = None, page: float | None = None,
    65	                 perPage: float | None = None, fields: list[str] | None = None) -> Argv:
    66	    return _rest(f"{_repo(owner, repo)}/commits", {"sha": sha, "path": path, "author": author, "since": since,
    67	                                                    "until": until, **_pages(page, perPage)}, jq=_each(fields))
    68	
    69	
    70	_COMMIT_DETAIL = {"none": "del(.files, .stats)", "stat
… [11861 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'for f in skills/*/SKILL.md skills/*/*/*; do echo "$f"; nl -ba "$f"; done'
````

````
skills/ci-failure-triage/SKILL.md
     1	---
     2	name: ci-failure-triage
     3	description: Find why a GitHub Actions run failed and fix it. Use when CI, a workflow run, a check, or a build is red, or when asked why tests fail on GitHub but not locally.
     4	---
     5	
     6	# Triage a failed CI run
     7	
     8	If the GitHub tools below are not in your tool list, find their schemas with `tool_search` and run them with `tool_call`.
     9	
    10	1. Find the failed run: `actions_list` with `method: "list_workflow_runs"`; take the newest run with conclusion `failure` on the branch in question.
    11	2. Fetch only the failed jobs' logs: `get_job_logs` with `run_id`, `failed_only: true`, `return_content: true`, `tail_lines: 300`.
    12	3. Save the logs to a file and run `scripts/first_error.sh <file>`: it prints the first error with context. The first error is the cause; later ones are usually fallout.
    13	4. Classify before fixing:
    14	   - code or test bug: reproduce locally with the same command the job ran, then fix;
    15	   - environment difference (versions, missing service, secrets): compare the workflow file with the local setup and fix the workflow, not the code;
    16	   - flaky (passes on re-run, timing-dependent): say so and do not "fix" it with retries or sleeps.
    17	5. Answer with the failing step, the root cause, and the fix (or why no code change is needed).
skills/fix-github-issue/SKILL.md
     1	---
     2	name: fix-github-issue
     3	description: Fix a bug reported in a GitHub issue and open a pull request for it. Use when the task references an issue number or URL and asks to fix, resolve, or implement it.
     4	---
     5	
     6	# Fix a GitHub issue
     7	
     8	If the GitHub tools below are not in your tool list, find their schemas with `tool_search` and run them with `tool_call`.
     9	
    10	1. Read the issue and its discussion: `issue_read` with `method: "get"`, then `method: "get_comments"`. Write down the expected and the actual behaviour in one line each.
    11	2. Reproduce locally before changing code. Prefer a failing test next to the existing tests for that module; if the bug cannot be reproduced, stop and report what you tried instead of guessing a fix.
    12	3. Make the smallest change that makes the test pass. Do not refactor unrelated code in the same PR.
    13	4. Run the full test suite. A PR with failing tests is not done.
    14	5. Branch `fix/<issue-number>-<short-slug>`, one commit with a conventional message (`fix: <what was wrong>`).
    15	6. Open the PR with `create_pull_request`:
    16	   - title: the commit message;
    17	   - body: `Fixes #<issue-number>`, then the root cause in 1-2 sentences, then how it was verified (test name, command).
    18	7. Answer with the PR URL and the root cause.
skills/review-pull-request/SKILL.md
     1	---
     2	name: review-pull-request
     3	description: Review a GitHub pull request and leave line comments plus a verdict. Use when asked to review, check, or approve a PR.
     4	---
     5	
     6	# Review a pull request
     7	
     8	If the GitHub tools below are not in your tool list, find their schemas with `tool_search` and run them with `tool_call`.
     9	
    10	1. Read the PR description and the diff: `pull_request_read` with `method: "get"`, then `method: "get_diff"`. Check `method: "get_check_runs"`: if CI is red, say so first.
    11	2. Go through `references/checklist.md` for every changed file. Report only real problems: a bug, a missing test for changed behaviour, a broken contract. Skip style nits that a linter would catch.
    12	3. Leave comments as one review, not as separate comments:
    13	   - `pull_request_review_write` with `method: "create"` (no `event`) opens a pending review;
    14	   - `add_comment_to_pending_review` for each problem, `subjectType: "LINE"`, on the line of the new code (`side: "RIGHT"`), with what is wrong and a concrete fix;
    15	   - `pull_request_review_write` wit
… [1261 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba src/loola_agent/agent.py | tail -41 && nl -ba src/loola_agent/events.py'
````

````
67	                yield self._append(ToolResult(call["id"], name, await self.toolbox.call(name, arguments)))
    68	        yield self._append(RunFinished("max_turns", "", self.max_turns, usage))
    69	
    70	    async def _compact_if_needed(self, policy: CompactionPolicy) -> Compaction | None:
    71	        tools, reply = self.toolbox.schemas(), self.llm.max_tokens
    72	        bound = context_bound(self.system_prompt, self.events, tools)
    73	        if not policy.wants_compaction(bound, reply):
    74	            return None
    75	        cut = choose_cut(self.events, bound, policy.keep_recent)
    76	        if cut is None:  # nothing sent since the last compaction: only the optional threshold can be over
    77	            if policy.fits(bound, reply):
    78	                return None
    79	            raise CompactionError(f"The next request may need {bound} tokens plus a reserved reply, which exceeds "
    80	                                  f"the {policy.context_window}-token window, and there is no history to compact.")
    81	        # When the bulk is the most recent turn (e.g. one huge tool output), summarizing the rest cannot help:
    82	        # skip the paid summary request if the context still fits, fail now if it does not.
    83	        empty = Compaction("", cut, bound, 0, Usage())
    84	        expected = bound_after_compaction(self.system_prompt, [*self.events, empty], tools, empty) \
    85	            + policy.summary_max_tokens
    86	        if expected >= bound:
    87	            if policy.fits(bound, reply):
    88	                return None
    89	            raise CompactionError(f"The next request may need {bound} tokens, and compaction cannot shrink it: "
    90	                                  f"the most recent turn alone does not fit the {policy.context_window}-token window.")
    91	        completion = await self.llm.complete(summary_request(self.system_prompt, self.events, cut), tools,
    92	                                             max_tokens=policy.summary_max_tokens)
    93	        summary = completion.message.get("content") or ""
    94	        if completion.finish_reason != "stop" or completion.message.get("tool_calls") or not summary.strip():
    95	            raise CompactionError(f"The summary request did not return a complete summary "
    96	                                  f"(finish_reason={completion.finish_reason!r}).")
    97	        compaction = Compaction(summary, cut, bound, 0, completion.usage)
    98	        after = bound_after_compaction(self.system_prompt, [*self.events, compaction], tools, compaction)
    99	        if not policy.fits(after, reply):
   100	            raise CompactionError(f"Even after compaction the context may need {after} tokens: the user's messages "
   101	                                  f"and the most recent turn do not fit the {policy.context_window}-token window.")
   102	        self._append(replace(compaction, tokens_after=after))
   103	        return self.events[-1]
   104	
   105	    def _append(self, event: Event) -> Event:
   106	        self.events.append(event)
   107	        return event
     1	"""Session events. The session is an append-only list of them; the LLM context is a pure projection of it."""
     2	from dataclasses import dataclass
     3	from typing import Literal
     4	
     5	from .llm import Usage
     6	
     7	INTERRUPTED = ("Error: this tool call was interrupted before it finished; it may have had partial side effects. "
     8	               "Check the current state and re-run it if it is still needed.")
     9	SUMMARY_HEADER = "\n\n[Earlier work in this conversation was compacted. Summary of it:]\n"
    10	
    11	
    12	@dataclass(frozen=True)
    13	class UserMessage:
    14	    content: str
    15	
    16	
    17	@dataclass(frozen=True)
    18	class AssistantMessage:
    19	    message: dict  # as returned by the LLM: parallel tool calls and reasoning fields stay intact
    20	    fin
… [3192 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba src/loola_agent/tools.py && nl -ba src/loola_agent/bash.py'
````

````
1	"""Tools: a minimal protocol and a toolbox that validates calls against JSON Schema.
     2	
     3	Direct tools are declared to the model in every request. Deferred tools are not: the model finds them with
     4	`tool_search` (BM25 over names and descriptions; matching schemas come back as the tool result) and runs them
     5	with `tool_call`. The declared tool list therefore never changes during a session, so the prompt prefix
     6	(and the server's KV cache for it) stays valid however many tools the model discovers."""
     7	import json, math, re
     8	from collections import Counter
     9	from collections.abc import Sequence
    10	from typing import Protocol
    11	
    12	from jsonschema import Draft202012Validator
    13	from jsonschema.exceptions import best_match
    14	
    15	
    16	class Tool(Protocol):
    17	    name: str
    18	    description: str
    19	    parameters: dict  # JSON Schema of the arguments object
    20	
    21	    async def run(self, args: dict) -> str: ...
    22	
    23	
    24	class Toolbox:
    25	    """Dispatches model tool calls. Mistakes of the model come back as text so it can fix the call itself."""
    26	
    27	    def __init__(self, direct: Sequence[Tool], deferred: Sequence[Tool] = (), deferred_hint: str = ""):
    28	        meta: list[Tool] = [ToolSearch(deferred, deferred_hint), ToolCall(self)] if deferred else []
    29	        self._declared = [*direct, *meta]
    30	        self._tools = {tool.name: tool for tool in [*self._declared, *deferred]}
    31	        if len(self._tools) != len(self._declared) + len(deferred):
    32	            raise ValueError("Duplicate tool names")
    33	        self._validators = {name: _validator(tool.parameters) for name, tool in self._tools.items()}
    34	        self._has_deferred = bool(deferred)
    35	
    36	    def schemas(self) -> list[dict]:
    37	        return [{"type": "function", "function": {"name": t.name, "description": t.description,
    38	                                                  "parameters": t.parameters}} for t in self._declared]
    39	
    40	    async def call(self, name: str, raw_arguments: str) -> str:
    41	        try:
    42	            args = json.loads(raw_arguments)
    43	        except json.JSONDecodeError as e:
    44	            return f"Error: arguments for '{name}' are not valid JSON ({e}). Re-issue the call with a JSON object."
    45	        return await self.dispatch(name, args)
    46	
    47	    async def dispatch(self, name: str, args: object) -> str:
    48	        tool = self._tools.get(name)
    49	        if tool is None:
    50	            hint = "Use tool_search to find tools." if self._has_deferred else \
    51	                f"Available tools: {', '.join(t.name for t in self._declared)}."
    52	            return f"Error: unknown tool '{name}'. {hint}"
    53	        if error := best_match(self._validators[name].iter_errors(args)):
    54	            where = "/".join(map(str, error.absolute_path)) or "<root>"
    55	            return (f"Error: invalid arguments for '{name}' at {where}: {error.message}. "
    56	                    f"Expected schema: {json.dumps(tool.parameters)}")
    57	        return await tool.run(args)
    58	
    59	
    60	def _validator(schema: dict) -> Draft202012Validator:
    61	    Draft202012Validator.check_schema(schema)
    62	    # Most real-world schemas allow unknown keys, so a misspelled argument would be silently ignored by the tool.
    63	    # Rejecting it lets the model see and fix the typo.
    64	    return Draft202012Validator({"additionalProperties": False, **schema})
    65	
    66	
    67	class ToolSearch:
    68	    name = "tool_search"
    69	    parameters = {"type": "object",
    70	                  "properties": {"query": {"type": "string", "description": "Keywords describing the action you need."},
    71	                                 "limit": {"type": "integer", "description": "Maximum number of tools (defa
… [7043 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba src/loola_agent/llm.py && nl -ba src/loola_agent/cli.py'
````

````
1	"""LLM boundary: a minimal protocol and an async adapter for OpenAI-compatible /v1/chat/completions."""
     2	import asyncio, logging
     3	from dataclasses import dataclass
     4	from typing import Protocol, Self
     5	
     6	import httpx
     7	
     8	log = logging.getLogger(__name__)
     9	
    10	TRANSIENT_STATUS = {429, 500, 502, 503, 504}
    11	
    12	
    13	@dataclass(frozen=True)
    14	class Usage:
    15	    prompt: int = 0
    16	    completion: int = 0
    17	    cached: int | None = None  # None: the server does not report cached prompt tokens
    18	
    19	    def __add__(self, other: "Usage") -> "Usage":
    20	        cached = None if self.cached is None and other.cached is None else (self.cached or 0) + (other.cached or 0)
    21	        return Usage(self.prompt + other.prompt, self.completion + other.completion, cached)
    22	
    23	
    24	@dataclass(frozen=True)
    25	class Completion:
    26	    message: dict  # assistant message exactly as the server returned it (wire format)
    27	    finish_reason: str | None
    28	    usage: Usage
    29	
    30	
    31	class LLMError(RuntimeError):
    32	    pass
    33	
    34	
    35	class LLM(Protocol):
    36	    max_tokens: int  # completion limit of a regular reply
    37	
    38	    async def complete(self, messages: list[dict], tools: list[dict], *,
    39	                       max_tokens: int | None = None) -> Completion: ...
    40	
    41	
    42	class OpenAICompatibleLLM:
    43	    def __init__(self, base_url: str, api_key: str, model: str, *, max_tokens: int = 8192,
    44	                 temperature: float | None = None, headers: dict[str, str] | None = None, retries: int = 3,
    45	                 retry_backoff: float = 2.0, transport: httpx.AsyncBaseTransport | None = None):
    46	        self.model, self.max_tokens, self.temperature = model, max_tokens, temperature
    47	        self.retries, self.retry_backoff = retries, retry_backoff
    48	        self._client = httpx.AsyncClient(
    49	            base_url=base_url.rstrip("/") + "/", transport=transport, timeout=httpx.Timeout(600, connect=10),
    50	            headers={"Authorization": f"Bearer {api_key}", "User-Agent": "loola-agent/0.1.0", **(headers or {})})
    51	
    52	    async def __aenter__(self) -> Self:
    53	        return self
    54	
    55	    async def __aexit__(self, *exc: object) -> None:
    56	        await self._client.aclose()
    57	
    58	    async def complete(self, messages: list[dict], tools: list[dict], *,
    59	                       max_tokens: int | None = None) -> Completion:
    60	        # max_completion_tokens: reasoning models reject max_tokens; vLLM and other servers accept both.
    61	        payload = {"model": self.model, "messages": messages, "tools": tools, "tool_choice": "auto",
    62	                   "max_completion_tokens": max_tokens or self.max_tokens}
    63	        if self.temperature is not None:  # many reasoning models accept only their default temperature
    64	            payload["temperature"] = self.temperature
    65	        response = await self._post_with_retry(payload)
    66	        if response.is_error:
    67	            raise LLMError(f"HTTP {response.status_code}: {response.text[:2000]}")
    68	        body = response.json()
    69	        if not body.get("choices") or "usage" not in body:
    70	            raise LLMError(f"Unexpected LLM response: {response.text[:2000]}")
    71	        choice, usage = body["choices"][0], body["usage"]
    72	        cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
    73	        return Completion(choice["message"], choice.get("finish_reason"),
    74	                          Usage(usage["prompt_tokens"], usage["completion_tokens"], cached))
    75	
    76	    async def _post_with_retry(self, payload: dict) -> httpx.Response:
    77	        error = ""
    78	        for attempt in range(1, self.retries + 1):
    79	            try:
   
… [7071 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba tests/test_compaction.py'
````

````
1	"""Compaction: every request (summary requests included) stays within the window, whatever the threshold."""
     2	import json
     3	
     4	import pytest
     5	
     6	from loola_agent import (Agent, AssistantMessage, Compaction, CompactionError, CompactionPolicy, Completion,
     7	                         RunFinished, Toolbox, Usage, UserMessage, build_context)
     8	from loola_agent.compaction import SUMMARY_INSTRUCTION, context_bound
     9	from loola_agent.events import SUMMARY_HEADER
    10	
    11	
    12	class Big:
    13	    name, description = "big", "Returns a large output."
    14	    parameters = {"type": "object", "properties": {}}
    15	
    16	    def __init__(self, size=3000):
    17	        self.size = size
    18	
    19	    async def run(self, args):
    20	        return "x" * self.size
    21	
    22	
    23	class SimulatedLLM:
    24	    """A server stand-in: counts `bytes_per_token` bytes as one token (1 is the worst case the bound allows),
    25	    rejects any request that would overflow the window, makes `turns` tool calls and then answers;
    26	    summary requests (ending with the summary instruction) get a summary. Completion counts are the real message sizes."""
    27	
    28	    def __init__(self, window, turns, max_tokens=500, summary=None, bytes_per_token=3):
    29	        self.window, self.turns, self.max_tokens, self.bpt = window, turns, max_tokens, bytes_per_token
    30	        self.summary = summary or Completion({"role": "assistant", "content": "SUMMARY " + "s" * 300}, "stop",
    31	                                             Usage(0, 0))
    32	        self.requests: list[dict] = []
    33	
    34	    def tokens(self, value) -> int:
    35	        return len(json.dumps(value).encode()) // self.bpt + 1
    36	
    37	    async def complete(self, messages, tools, *, max_tokens=None):
    38	        prompt = self.tokens([messages, tools])
    39	        assert prompt + (max_tokens or self.max_tokens) <= self.window, f"overflow: {prompt} prompt tokens"
    40	        is_summary = messages[-1] == {"role": "user", "content": SUMMARY_INSTRUCTION}
    41	        self.requests.append({"messages": messages, "tools": tools, "summary": is_summary, "prompt": prompt})
    42	        if is_summary:
    43	            message, finish = self.summary.message, self.summary.finish_reason
    44	        elif (turn := sum(not r["summary"] for r in self.requests)) <= self.turns:
    45	            call = {"id": f"c{turn}", "type": "function", "function": {"name": "big", "arguments": "{}"}}
    46	            message, finish = {"role": "assistant", "content": f"step {turn}", "tool_calls": [call]}, "tool_calls"
    47	        else:
    48	            message, finish = {"role": "assistant", "content": "all done"}, "stop"
    49	        return Completion(message, finish, Usage(prompt, self.tokens(message)))
    50	
    51	
    52	async def run(agent, task="long task"):
    53	    return [e async for e in agent.send(task)]
    54	
    55	
    56	@pytest.mark.parametrize("bytes_per_token", [1, 3])
    57	@pytest.mark.parametrize("keep_recent", [0, 3_000])
    58	@pytest.mark.parametrize("output_size", [800, 4_000])
    59	@pytest.mark.parametrize("compact_at", [None, 4_000, 12_000, 19_999, 10**9])
    60	async def test_requests_never_overflow_whatever_the_threshold(compact_at, output_size, keep_recent, bytes_per_token):
    61	    llm = SimulatedLLM(window=20_000, turns=40, bytes_per_token=bytes_per_token)
    62	    policy = CompactionPolicy(20_000, compact_at, keep_recent_tokens=keep_recent, summary_max_tokens=1_000)
    63	    events = await run(Agent(llm, Toolbox([Big(output_size)]), compaction=policy))
    64	    assert events[-1].status == "done"
    65	    compactions = [e for e in events if isinstance(e, Compaction)]
    66	    if 40 * output_size // bytes_per_token > 20_000:  # the outputs alone exceed the window
    67	        assert compactions
    68	    assert all(c.tokens_after < c.toke
… [4885 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba src/loola_agent/skills.py && nl -ba src/loola_agent/catalog.py && nl -ba src/loola_agent/__init__.py'
````

````
1	"""Agent Skills (agentskills.io): one directory per skill with a SKILL.md (YAML frontmatter `name` and `description`,
     2	then markdown instructions) and optional bundled files next to it.
     3	
     4	Only the catalog (name, description, location) goes into the system prompt. When a task matches, the model reads
     5	SKILL.md with bash, so the instructions land in the history as an ordinary tool result. The system prompt is fixed
     6	for the session: loading a skill never changes the prompt prefix, and the server's KV cache for it stays valid."""
     7	import re
     8	from dataclasses import dataclass
     9	from pathlib import Path
    10	
    11	import yaml
    12	
    13	NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
    14	FRONTMATTER = re.compile(r"---\n(.*?)\n---\n(.*)", re.DOTALL)
    15	
    16	
    17	@dataclass(frozen=True)
    18	class Skill:
    19	    name: str
    20	    description: str
    21	    location: Path  # absolute path to SKILL.md
    22	    body: str
    23	
    24	
    25	def load_skills(root: Path) -> list[Skill]:
    26	    """Skills of `root/*/SKILL.md`, sorted by name so the rendered prompt is byte-stable between runs."""
    27	    skills = [_parse(path.resolve()) for path in sorted(root.glob("*/SKILL.md"))]
    28	    if not skills:
    29	        raise ValueError(f"No skills in {root}: expected {root}/<name>/SKILL.md")
    30	    return skills
    31	
    32	
    33	def _parse(path: Path) -> Skill:
    34	    match = FRONTMATTER.fullmatch(path.read_text())
    35	    if match is None:
    36	        raise ValueError(f"{path}: expected YAML frontmatter between '---' lines")
    37	    meta = yaml.safe_load(match[1])
    38	    name, description = meta.get("name"), meta.get("description")
    39	    if name != path.parent.name or not NAME.fullmatch(name) or len(name) > 64:
    40	        raise ValueError(f"{path}: name must equal the directory name, lowercase-hyphenated, at most 64 chars")
    41	    if not isinstance(description, str) or not 0 < len(description) <= 1024:
    42	        raise ValueError(f"{path}: description must be 1-1024 chars")
    43	    return Skill(name, description.strip(), path, match[2].strip())
    44	
    45	
    46	def skills_prompt(skills: list[Skill], *, eager: bool = False) -> str:
    47	    """System prompt section. Lazy (default): catalog only, bodies are read on demand.
    48	    Eager: every body inline, the baseline for measuring what lazy loading saves."""
    49	    if eager:
    50	        bodies = "\n\n".join(f'<skill name="{s.name}" location="{s.location}">\n{s.body}\n</skill>' for s in skills)
    51	        return ("## Skills\nFollow a skill's instructions when the task matches it. Resolve relative paths in a skill "
    52	                f"against the directory of its SKILL.md.\n\n{bodies}")
    53	    catalog = "\n".join(f"<skill><name>{s.name}</name><description>{s.description}</description>"
    54	                        f"<location>{s.location}</location></skill>" for s in skills)
    55	    return ("## Skills\nSkills are instructions for specific kinds of tasks. When a task matches a skill's "
    56	            "description, read its whole SKILL.md with bash (`cat <location>`; if the output is truncated, read "
    57	            "the rest with `sed -n`) before acting and follow it. Resolve "
    58	            "relative paths in a skill against the directory of its SKILL.md. If a skill you are following is no "
    59	            "longer in the conversation (older messages get summarized), read it again.\n"
    60	            f"<available_skills>\n{catalog}\n</available_skills>")
     1	"""Example tool catalogs: real tool descriptions and schemas executed by dummy implementations."""
     2	import json
     3	from dataclasses import dataclass
     4	from pathlib import Path
     5	
     6	
     7	@dataclass(frozen=True)
     8	class DummyTool:
     9	    name: str
    10	    description: str
    11	    parameters: dict
    12	

… [1989 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba tests/test_deferred.py && nl -ba tests/test_llm.py && nl -ba tests/test_skills.py'
````

````
1	"""Deferred tools: discovery via tool_search, execution via tool_call, a stable declared tool list."""
     2	import json
     3	from pathlib import Path
     4	
     5	import pytest
     6	
     7	from loola_agent import Agent, Completion, DummyTool, Toolbox, Usage, load_catalog
     8	
     9	CATALOG = Path(__file__).parent.parent / "examples" / "github_tools.json"
    10	ISSUE = DummyTool("issue_read", "Get information about a specific issue in a GitHub repository.",
    11	                  {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"},
    12	                                                    "issue_number": {"type": "number"}},
    13	                   "required": ["owner", "repo", "issue_number"]})
    14	STARS = DummyTool("list_stargazers", "List users who starred a repository.",
    15	                  {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}}})
    16	
    17	
    18	class Direct:
    19	    name, description = "direct", "Always declared."
    20	    parameters = {"type": "object", "properties": {}}
    21	
    22	    async def run(self, args):
    23	        return "direct ok"
    24	
    25	
    26	def declared_names(toolbox):
    27	    return [t["function"]["name"] for t in toolbox.schemas()]
    28	
    29	
    30	def test_only_direct_and_meta_tools_are_declared():
    31	    assert declared_names(Toolbox([Direct()], deferred=[ISSUE, STARS])) == ["direct", "tool_search", "tool_call"]
    32	    assert declared_names(Toolbox([Direct()])) == ["direct"]
    33	
    34	
    35	async def test_search_returns_matching_tools_with_schemas():
    36	    result = json.loads(await Toolbox([Direct()], deferred=[ISSUE, STARS]).call("tool_search", '{"query": "issue"}'))
    37	    assert [t["name"] for t in result] == ["issue_read"]
    38	    assert result[0]["parameters"] == ISSUE.parameters
    39	
    40	
    41	async def test_search_without_matches_says_so():
    42	    result = await Toolbox([Direct()], deferred=[ISSUE]).call("tool_search", '{"query": "kubernetes"}')
    43	    assert result.startswith("No tools match")
    44	
    45	
    46	async def test_tool_call_runs_a_deferred_tool():
    47	    args = {"name": "issue_read", "arguments": {"owner": "o", "repo": "r", "issue_number": 1}}
    48	    result = json.loads(await Toolbox([Direct()], deferred=[ISSUE]).call("tool_call", json.dumps(args)))
    49	    assert (result["tool"], result["arguments"]) == ("issue_read", args["arguments"])
    50	
    51	
    52	@pytest.mark.parametrize("arguments, expected", [
    53	    ({"owner": "o", "repo": "r"}, "'issue_number' is a required property"),
    54	    ({"owner": "o", "repo": "r", "issue_number": "1"}, "at issue_number: '1' is not of type 'number'"),
    55	    ({"owner": "o", "repo": "r", "issue_number": 1, "repo_name": "r"}, "'repo_name' was unexpected"),
    56	])
    57	async def test_tool_call_validates_against_the_deferred_tool_schema(arguments, expected):
    58	    result = await Toolbox([Direct()], deferred=[ISSUE]).call(
    59	        "tool_call", json.dumps({"name": "issue_read", "arguments": arguments}))
    60	    assert result.startswith("Error: invalid arguments for 'issue_read'") and expected in result
    61	    assert json.dumps(ISSUE.parameters) in result
    62	
    63	
    64	async def test_unknown_tool_points_to_search():
    65	    result = await Toolbox([Direct()], deferred=[ISSUE]).call("tool_call", '{"name": "nope", "arguments": {}}')
    66	    assert result == "Error: unknown tool 'nope'. Use tool_search to find tools."
    67	
    68	
    69	def test_duplicate_names_across_direct_and_deferred_fail_fast():
    70	    with pytest.raises(ValueError, match="Duplicate"):
    71	        Toolbox([ISSUE], deferred=[ISSUE])
    72	
    73	
    74	def test_github_example_catalog_loads_and_its_schemas_are_valid():
    75	    tools, hint = load_catalog(CATALOG)
    76	    toolbox = Toolbox([Direct()], de
… [8971 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba src/loola_agent/tools.py'
````

````
1	"""Tools: a minimal protocol and a toolbox that validates calls against JSON Schema.
     2	
     3	Direct tools are declared to the model in every request. Deferred tools are not: the model finds them with
     4	`tool_search` (BM25 over names and descriptions; matching schemas come back as the tool result) and runs them
     5	with `tool_call`. The declared tool list therefore never changes during a session, so the prompt prefix
     6	(and the server's KV cache for it) stays valid however many tools the model discovers."""
     7	import json, math, re
     8	from collections import Counter
     9	from collections.abc import Sequence
    10	from typing import Protocol
    11	
    12	from jsonschema import Draft202012Validator
    13	from jsonschema.exceptions import best_match
    14	
    15	
    16	class Tool(Protocol):
    17	    name: str
    18	    description: str
    19	    parameters: dict  # JSON Schema of the arguments object
    20	
    21	    async def run(self, args: dict) -> str: ...
    22	
    23	
    24	class Toolbox:
    25	    """Dispatches model tool calls. Mistakes of the model come back as text so it can fix the call itself."""
    26	
    27	    def __init__(self, direct: Sequence[Tool], deferred: Sequence[Tool] = (), deferred_hint: str = ""):
    28	        meta: list[Tool] = [ToolSearch(deferred, deferred_hint), ToolCall(self)] if deferred else []
    29	        self._declared = [*direct, *meta]
    30	        self._tools = {tool.name: tool for tool in [*self._declared, *deferred]}
    31	        if len(self._tools) != len(self._declared) + len(deferred):
    32	            raise ValueError("Duplicate tool names")
    33	        self._validators = {name: _validator(tool.parameters) for name, tool in self._tools.items()}
    34	        self._has_deferred = bool(deferred)
    35	
    36	    def schemas(self) -> list[dict]:
    37	        return [{"type": "function", "function": {"name": t.name, "description": t.description,
    38	                                                  "parameters": t.parameters}} for t in self._declared]
    39	
    40	    async def call(self, name: str, raw_arguments: str) -> str:
    41	        try:
    42	            args = json.loads(raw_arguments)
    43	        except json.JSONDecodeError as e:
    44	            return f"Error: arguments for '{name}' are not valid JSON ({e}). Re-issue the call with a JSON object."
    45	        return await self.dispatch(name, args)
    46	
    47	    async def dispatch(self, name: str, args: object) -> str:
    48	        tool = self._tools.get(name)
    49	        if tool is None:
    50	            hint = "Use tool_search to find tools." if self._has_deferred else \
    51	                f"Available tools: {', '.join(t.name for t in self._declared)}."
    52	            return f"Error: unknown tool '{name}'. {hint}"
    53	        if error := best_match(self._validators[name].iter_errors(args)):
    54	            where = "/".join(map(str, error.absolute_path)) or "<root>"
    55	            return (f"Error: invalid arguments for '{name}' at {where}: {error.message}. "
    56	                    f"Expected schema: {json.dumps(tool.parameters)}")
    57	        return await tool.run(args)
    58	
    59	
    60	def _validator(schema: dict) -> Draft202012Validator:
    61	    Draft202012Validator.check_schema(schema)
    62	    # Most real-world schemas allow unknown keys, so a misspelled argument would be silently ignored by the tool.
    63	    # Rejecting it lets the model see and fix the typo.
    64	    return Draft202012Validator({"additionalProperties": False, **schema})
    65	
    66	
    67	class ToolSearch:
    68	    name = "tool_search"
    69	    parameters = {"type": "object",
    70	                  "properties": {"query": {"type": "string", "description": "Keywords describing the action you need."},
    71	                                 "limit": {"type": "integer", "description": "Maximum number of tools (defa
… [2957 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba tests/test_tools.py && nl -ba tests/test_agent.py'
````

````
1	"""Toolbox validation and bash tool behavior."""
     2	import asyncio, json, os, time
     3	
     4	import pytest
     5	from jsonschema.exceptions import SchemaError
     6	
     7	from loola_agent import Bash, Toolbox
     8	
     9	
    10	@pytest.fixture
    11	async def bash():
    12	    async with Bash(timeout=1) as tool:
    13	        yield tool
    14	
    15	
    16	async def run(bash, command):
    17	    return await bash.run({"command": command})
    18	
    19	
    20	@pytest.mark.parametrize("raw, expected", [
    21	    ('{"command": "echo hi"', "not valid JSON"),
    22	    ("", "not valid JSON"),
    23	    ('["ls", "-la"]', "at <root>: ['ls', '-la'] is not of type 'object'"),
    24	    ('{"command": ["ls", "-la"]}', "at command: ['ls', '-la'] is not of type 'string'"),
    25	    ("{}", "'command' is a required property"),
    26	])
    27	async def test_invalid_arguments_are_explained_to_the_model(bash, raw, expected):
    28	    result = await Toolbox([bash]).call("bash", raw)
    29	    assert result.startswith("Error:") and expected in result
    30	
    31	
    32	async def test_schema_error_includes_the_expected_schema(bash):
    33	    result = await Toolbox([bash]).call("bash", "{}")
    34	    assert json.dumps(bash.parameters) in result
    35	
    36	
    37	async def test_unknown_tool_lists_available_tools(bash):
    38	    assert await Toolbox([bash]).call("python", "{}") == "Error: unknown tool 'python'. Available tools: bash."
    39	
    40	
    41	async def test_valid_call_is_dispatched(bash):
    42	    assert await Toolbox([bash]).call("bash", '{"command": "echo hi"}') == "Exit code: 0\nhi\n"
    43	
    44	
    45	def test_invalid_tool_schema_fails_fast(bash):
    46	    class Broken:
    47	        name, description, parameters = "broken", "", {"type": "nope"}
    48	
    49	    with pytest.raises(SchemaError):
    50	        Toolbox([Broken()])
    51	
    52	
    53	async def test_huge_output_is_truncated_head_and_tail(bash):
    54	    output = await run(bash, "seq 1 300000")
    55	    assert len(output) < bash.max_output + 200
    56	    assert "\n1\n2\n" in output and "300000" in output and "bytes truncated" in output
    57	
    58	
    59	async def test_llm_secrets_are_not_visible_to_commands(bash, monkeypatch):
    60	    monkeypatch.setenv("LLM_API_KEY", "sk-secret")
    61	    assert "sk-secret" not in await run(bash, "env")
    62	
    63	
    64	async def test_stdin_is_closed(bash):
    65	    assert (await run(bash, "cat")).startswith("Exit code: 0")
    66	
    67	
    68	async def test_background_job_does_not_block(bash):
    69	    started = time.monotonic()
    70	    assert "started" in await run(bash, "sleep 5 > /dev/null 2>&1 & echo started")
    71	    assert time.monotonic() - started < 1
    72	
    73	
    74	async def test_timeout_kills_process_group_and_keeps_partial_output(bash, tmp_path):
    75	    marker = tmp_path / "after"
    76	    output = await run(bash, f"echo test_1 PASSED; (sleep 1.5; touch {marker}) & sleep 30")
    77	    assert "timed out" in output and "test_1 PASSED" in output
    78	    await asyncio.sleep(1)
    79	    assert not marker.exists()
    80	
    81	
    82	async def test_background_jobs_are_killed_on_exit(tmp_path):
    83	    marker = tmp_path / "after"
    84	    async with Bash() as bash:
    85	        await run(bash, f"(sleep 1; touch {marker}) > /dev/null 2>&1 &")
    86	    await asyncio.sleep(1.5)
    87	    assert not marker.exists()
    88	
    89	
    90	async def test_invalid_utf8_output_keeps_exit_code_and_side_effects(bash, tmp_path):
    91	    output = await run(bash, f"echo created > {tmp_path}/marker; printf '\\377\\376'; exit 3")
    92	    assert output.startswith("Exit code: 3") and (tmp_path / "marker").exists()
    93	
    94	
    95	async def test_cancelled_command_kills_its_process_group(bash, tmp_path):
    96	    marker = tmp_path / "after"
    97	    task = asyncio.create_task(run(bash, f"(sleep 
… [6459 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba tests/test_gh_proxy.py && head -22 src/loola_agent/gh_proxy.py && head -20 src/loola_agent/bash.py && head -25 examples/github_tools.json'
````

````
1	"""gh backend: argument -> `gh` argv mapping (no network), the runner against a fake gh, and live smoke tests."""
     2	import inspect, json
     3	from pathlib import Path
     4	
     5	import pytest
     6	
     7	from loola_agent import Toolbox, load_catalog
     8	from loola_agent.gh_proxy import PROXIED, Gh, GhUnavailable, Unsupported, gh_argv, gh_tools
     9	
    10	CATALOG = Path(__file__).parent.parent / "examples" / "github_tools.json"
    11	SPECS = {t["name"]: t for t in json.loads(CATALOG.read_text())["tools"]}
    12	GET = ["api", "--method", "GET"]
    13	
    14	
    15	@pytest.mark.parametrize("name, args, argv", [
    16	    ("get_file_contents", {"owner": "o", "repo": "r", "path": "/src/a b.py", "ref": "refs/heads/dev"},
    17	     [*GET, "repos/o/r/contents/src/a%20b.py?ref=refs%2Fheads%2Fdev", "--jq",
    18	      'if type == "array" then map(.) elif .type == "file" then .content | @base64d else . end']),
    19	    ("get_file_contents", {"owner": "o", "repo": "r", "ref": "main", "sha": "abc", "fields": ["name", "type"]},
    20	     [*GET, "repos/o/r/contents?ref=abc", "--jq",
    21	      'if type == "array" then map({name, type}) elif .type == "file" then .content | @base64d else . end']),
    22	    ("get_repository_tree", {"owner": "o", "repo": "r", "recursive": True, "path_filter": 'src/"x'},
    23	     [*GET, "repos/o/r/git/trees/HEAD?recursive=1", "--jq",
    24	      '{truncated, tree: [.tree[] | select(.path | startswith("src/\\"x")) | {path, type, size}]}']),
    25	    ("list_commits", {"owner": "o", "repo": "r", "sha": "main", "perPage": 5, "page": 2, "fields": ["sha"]},
    26	     [*GET, "repos/o/r/commits?sha=main&page=2&per_page=5", "--jq", "map({sha})"]),
    27	    ("get_commit", {"owner": "o", "repo": "r", "sha": "abc"},
    28	     [*GET, "repos/o/r/commits/abc", "--jq", ".files |= map(del(.patch))"]),
    29	    ("get_commit", {"owner": "o", "repo": "r", "sha": "abc", "detail": "full_patch"}, [*GET, "repos/o/r/commits/abc"]),
    30	    ("issue_read", {"method": "get_comments", "owner": "o", "repo": "r", "issue_number": 7, "perPage": 10},
    31	     [*GET, "repos/o/r/issues/7/comments?per_page=10"]),
    32	    ("issue_read", {"method": "get", "owner": "o", "repo": "r", "issue_number": 7.0}, [*GET, "repos/o/r/issues/7"]),
    33	    ("search_issues", {"query": "memory leak", "owner": "o", "repo": "r", "sort": "updated"},
    34	     [*GET, "search/issues?q=memory+leak+is%3Aissue+repo%3Ao%2Fr&sort=updated"]),
    35	    ("search_pull_requests", {"query": "fix", "fields": ["number", "title"]},
    36	     [*GET, "search/issues?q=fix+is%3Apr", "--jq", ".items |= map({number, title})"]),
    37	    ("list_pull_requests", {"owner": "o", "repo": "r", "state": "closed", "base": "main"},
    38	     [*GET, "repos/o/r/pulls?state=closed&base=main"]),
    39	    ("pull_request_read", {"method": "get_diff", "owner": "o", "repo": "r", "pullNumber": 3},
    40	     [*GET, "repos/o/r/pulls/3", "--header", "Accept: application/vnd.github.diff"]),
    41	    ("pull_request_read", {"method": "get_check_runs", "owner": "o", "repo": "r", "pullNumber": 3},
    42	     [*GET, "repos/o/r/commits/refs/pull/3/head/check-runs"]),
    43	    ("pull_request_read", {"method": "get_comments", "owner": "o", "repo": "r", "pullNumber": 3},
    44	     [*GET, "repos/o/r/issues/3/comments"]),
    45	    ("search_code", {"query": "Client repo:o/r", "fields": ["path"]},
    46	     [*GET, "search/code?q=Client+repo%3Ao%2Fr", "--header", "Accept: application/vnd.github.text-match+json",
    47	      "--jq", ".items |= map({path})"]),
    48	    ("search_repositories", {"query": "http client", "minimal_output": False}, [*GET, "search/repositories?q=http+client"]),
    49	    ("list_releases", {"owner": "o", "repo": "r", "perPage": 3}, [*GET, "repos/o/r/releases?per_page=3"]),
    50	    ("list_branches", {"owner": "../..", "repo": "r"}, [*GET, "repos/..%2F../r/branches"]),
    51	])
    52	def test_rest_mapping(nam
… [9301 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba <local path> | tail -29'
````

````
26	## Решения на развилках (и почему) — одобрены владельцем
    27	
    28	1. **Базовые фиксы исходного кода** (ревью нашло): assistant message кладём в историю как есть (параллельные tool calls, `reasoning_content` — DeepSeek без него 400); кривой JSON аргументов → ошибка модели; обрезка вывода head+tail; timeout/retry; `finish_reason=length` и пустой ответ = провал, а не успех; учёт usage; bash: stdin закрыт, `LLM_*` не видны командам, вывод в temp-файл (фон `cmd &` не блокирует, частичный вывод при таймауте), kill process group по таймауту/отмене/выходу.
    29	2. **Фоновые процессы**: только правило в описании bash-тула (`cmd > log 2>&1 &`), никаких bash_output/kill тулов — оверкилл.
    30	3. **Динамические тулы без нативного API**: массив `tools` никогда не меняется (у open-source chat templates tools рендерятся в начало промпта → любое изменение = полный промах KV-cache). В промпте: direct-тулы + `tool_search` + `tool_call(name, arguments)`. Схемы найденных тулов приходят как tool result (в хвост истории).
    31	4. **Constrained decoding / `strict` не используем вообще** (владелец: не поддерживать несколько вариантов). У vLLM при `tool_choice=auto` без strict его и так нет. Компенсация — валидация по JSON Schema в harness, ошибка со схемой уходит модели.
    32	5. **После компакшена найденные тулы НЕ добавляем в `tools`** и не «вспоминаем» тулы/скиллы явно: модель найдёт заново (ошибка валидации всё равно содержит схему).
    33	6. **Неизвестные аргументы отклоняем** (`additionalProperties: false` поверх схемы при валидации), т.к. почти все реальные схемы молча глотают опечатки. Опциональность на уровне тула — не делаем.
    34	7. **Deferred-тул можно вызвать и напрямую по имени** — следствие одного реестра для диспатча; совпадает с нативными API (Anthropic tool_reference, OpenAI tool_search). Основной путь — `tool_call`.
    35	8. **BM25 свой (~15 строк)**: зависимость (rank-bm25/bm25s) тянет numpy ради 91 документа и прячет механику.
    36	9. **Каталог тулов** — список из GitHub MCP server v2.2.0 (91 тул, MIT) **только как данные** (имя/описание/схема). MCP-протокол не подключаем — за рамками. Исполнение: `DummyTool` для детерминированных тестов; `gh_proxy` (14 read-only тулов через `gh api`) — только для живых прогонов, внутренняя тестовая обвязка, пока остаётся в пакете.
    37	10. **Прерванные tool calls** (отмена посреди тула): в начале следующего `send()` каждому незакрытому вызову — синтетический результат «interrupted, may have partial side effects, check state and re-run if needed». Не перезапуск (повтор побочных эффектов) и не удаление (ложь модели).
    38	11. **Скиллы** (Agent Skills): в system prompt только каталог (name/description/path), тело модель читает `bash cat`. `--skills-mode eager` — baseline для замера. Невалидный SKILL.md — ошибка старта.
    39	12. **Компакшен** (`compaction.py`): гарантия без процентов. Верхняя граница размера следующего запроса = точные `usage` сервера для измеренного + UTF-8 байты для неизмеренного (допущение: токен ≥ 1 байт, верно для BPE). Обычный запрос шлём, только если остаётся резерв под будущий summary-запрос; `compact_at` — лишь опциональный более ранний триггер. Summary-запрос = точный контекст ранее отправленного измеренного запроса + инструкция → влезает по построению и попадает в KV-cache. User-сообщения остаются дословно (склеены с summary в одно user-сообщение — строгие шаблоны не любят два user подряд). Срез только по границе запроса (все tool calls отвечены). Если сжатие не может уменьшить контекст — пропуск (если влезает) или явная ошибка. Стоимость summary входит в usage прогона.
    40	13. **Summary-запрос с тем же `tool_choice: auto`**, а не `none`: проверено живьём — OpenCode Go при `none` выкидывает tools из промпта → другой префикс, cached=0; с `auto` cached 8704/8776. Если модель вызовет тул вместо summary → явная ошибка.
    41	14. **Модель**: gpt-6-luna отпала (в chat completions tools работают только с `reasoning_effort=none`); используем `deeps
… [1473 more characters truncated]
````

**[command]** exit=2

````
/bin/bash -lc 'env UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run --frozen pytest -q'
````

````
Using CPython 3.13.17
Creating virtual environment at: .venv
   Building loola-agent @ file:///tmp/loola-review.iTsTm7q4
      Built loola-agent @ file:///tmp/loola-review.iTsTm7q4
Downloading pygments (1.2MiB)
 Downloaded pygments
Installed 20 packages in 112ms

==================================== ERRORS ====================================
_ ERROR collecting uv-cache/archive-v0/9Xt-BZYgXNVynQ0_/referencing/tests/test_referencing_suite.py _
<local path> in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1404: in _gcd_import
    ???
<frozen importlib._bootstrap>:1369: in _find_and_load
    ???
<frozen importlib._bootstrap>:1340: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:935: in _load_unlocked
    ???
.venv/lib/python3.13/site-packages/_pytest/assertion/rewrite.py:185: in exec_module
    exec(co, module.__dict__)
.venv/lib/python3.13/site-packages/referencing/tests/test_referencing_suite.py:27: in <module>
    raise SuiteNotFound()
E   referencing.tests.test_referencing_suite.SuiteNotFound: Cannot find the referencing suite. Set the REFERENCING_SUITE environment variable to the path to the suite, or run the test suite from alongside a full checkout of the git repository.
_ ERROR collecting uv-cache/archive-v0/ele3DKlRBZa5LMCM/jsonschema/tests/test_exceptions.py _
ImportError while importing test module '/tmp/loola-review.iTsTm7q4/uv-cache/archive-v0/ele3DKlRBZa5LMCM/jsonschema/tests/test_exceptions.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
<local path> in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/jsonschema/tests/test_exceptions.py:4: in <module>
    import jsonpath_ng
E   ModuleNotFoundError: No module named 'jsonpath_ng'
_ ERROR collecting uv-cache/archive-v0/ele3DKlRBZa5LMCM/jsonschema/tests/test_jsonschema_test_suite.py _
<local path> in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1404: in _gcd_import
    ???
<frozen importlib._bootstrap>:1369: in _find_and_load
    ???
<frozen importlib._bootstrap>:1340: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:935: in _load_unlocked
    ???
.venv/lib/python3.13/site-packages/_pytest/assertion/rewrite.py:185: in exec_module
    exec(co, module.__dict__)
.venv/lib/python3.13/site-packages/jsonschema/tests/test_jsonschema_test_suite.py:13: in <module>
    SUITE = Suite()
            ^^^^^^^
<attrs generated methods jsonschema.tests._suite.Suite>:32: in __init__
    _setattr('_root', __attr_factory__root())
                      ^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/jsonschema/tests/_suite.py:41: in _find_suite
    raise ValueError(
E   ValueError: Can't find the JSON-Schema-Test-Suite directory. Set the 'JSON_SCHEMA_TEST_SUITE' environment variable or run the tests from alongside a checkout of the suite.
_ ERROR collecting uv-cache/wheels-v7/pypi/jsonschema/4.26.0-py3-none-any/jsonschema/tests/test_exceptions.py _
ImportError while importing test module '/tmp/loola-review.iTsTm7q4/uv-cache/wheels-v7/pypi/jsonschema/4.26.0-py3-none-any/jsonschema/tests/test_exceptions.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
<local path> in import_module
    return _bootstrap._gcd_import(name[level:], package, leve
… [4736 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc "jq -r '.tools[]|select(.name|IN(\"list_commits\",\"get_file_contents\",\"get_repository_tree\",\"list_issues\",\"search_issues\",\"list_pull_requests\",\"list_releases\"))|[.name,.parameters.properties.fields,.parameters.properties.path_filter]|@json' examples/github_tools.json"
````

````
["get_file_contents",{"type":"array","items":{"type":"string","enum":["type","name","path","size","sha","url","git_url","html_url","download_url"]},"description":"Subset of fields to return for each entry when the path is a directory. If omitted, all fields are returned. Ignored when the path is a single file. Use this to reduce response size when listing directories and you only need specific fields, e.g. just 'name' and 'type'."},null]
["get_repository_tree",null,{"type":"string","description":"Optional path prefix to filter the tree results (e.g., 'src/' to only show files in the src directory)"}]
["list_commits",{"type":"array","items":{"type":"string","enum":["sha","html_url","commit","author","committer"]},"description":"Subset of fields to return for each commit. If omitted, all fields are returned. Use this to reduce response size when you only need specific fields, e.g. just 'sha' and 'html_url'."},null]
["list_issues",{"type":"array","items":{"type":"string","enum":["number","title","body","state","user","labels","assignees","comments","created_at","updated_at","field_values"]},"description":"Subset of fields to return for each issue. If omitted, all fields are returned. Use this to reduce response size when you only need specific fields; omitting 'body' and 'field_values' in particular drops the largest per-result data."},null]
["list_pull_requests",{"type":"array","items":{"type":"string","enum":["number","title","body","state","draft","merged","mergeable_state","html_url","user","labels","assignees","requested_reviewers","merged_by","head","base","additions","deletions","changed_files","commits","comments","created_at","updated_at","closed_at","merged_at","milestone"]},"description":"Subset of fields to return for each pull request. If omitted, all fields are returned. Use this to reduce response size when you only need specific fields; omitting 'body' in particular drops the largest per-result data."},null]
["list_releases",{"type":"array","items":{"type":"string","enum":["id","tag_name","name","body","html_url","published_at","prerelease","draft","author"]},"description":"Subset of fields to return for each release. If omitted, all fields are returned. Use this to reduce response size when you only need specific fields; omitting 'body' in particular drops the largest per-release data."},null]
["search_issues",{"type":"array","items":{"type":"string","enum":["number","title","body","state","state_reason","draft","locked","html_url","user","author_association","labels","assignee","assignees","milestone","comments","reactions","created_at","updated_at","closed_at","closed_by","type","repository_url","pull_request","field_values"]},"description":"Subset of fields to return for each issue result. If omitted, all fields are returned. Use this to reduce response size when you only need specific fields; omitting 'body', 'reactions', and 'labels' in particular drops the largest per-result data."},null]
````

**[command]** exit=1

````
/bin/bash -lc "realpath /bin/sh && command -v uv && rg -n 'summary|cached|direct' TASK.md"
````

````
/usr/bin/dash
<local path>
````

**[command]** exit=0

````
/bin/bash -lc "rg -n 'additionalProperties|total_count|field_values|path_filter' examples/github_tools.json | head -70"
````

````
765:              "additionalProperties": false
830:              "additionalProperties": false
851:        "additionalProperties": false
960:                  "additionalProperties": false
1050:                  "additionalProperties": false
1691:          "path_filter": {
1832:            "description": "The read operation to perform on a single issue.\nOptions are:\n1. get - Get issue details. Also returns best-effort hierarchy flags (`has_parent`, `has_children`); `parent` and `sub_issues_summary` are optional relationship summaries, and `closed_by_pull_requests` summarizes the pull requests configured to close the issue as `total_count` plus up to 5 `references`.\n2. get_comments - Get issue comments.\n3. get_sub_issues - Get sub-issues (children) of the issue.\n4. get_parent - Get the parent issue, if this issue is a sub-issue of another.\n5. get_labels - Get labels assigned to the issue.\n",
1923:              "additionalProperties": false
2593:                "field_values"
2596:            "description": "Subset of fields to return for each issue. If omitted, all fields are returned. Use this to reduce response size when you only need specific fields; omitting 'body' and 'field_values' in particular drops the largest per-result data."
3527:                  "additionalProperties": false
3540:                  "additionalProperties": false
3563:                  "additionalProperties": false
3596:              "additionalProperties": false
3692:                "additionalProperties": false
3709:                "additionalProperties": false
3892:              "additionalProperties": false
4207:                "field_values"
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba tests/test_llm.py && nl -ba tests/test_deferred.py | tail -64 && nl -ba tests/test_skills.py'
````

````
1	"""OpenAI-compatible adapter against a scripted httpx transport."""
     2	import json
     3	
     4	import httpx
     5	import pytest
     6	
     7	from loola_agent import LLMError, OpenAICompatibleLLM, Usage
     8	
     9	OK = {"choices": [{"message": {"role": "assistant", "content": "hi", "reasoning_content": "r"},
    10	                   "finish_reason": "stop"}],
    11	      "usage": {"prompt_tokens": 10, "completion_tokens": 2, "prompt_tokens_details": {"cached_tokens": 8}}}
    12	
    13	
    14	def llm_with(*responses):
    15	    requests, script = [], list(responses)
    16	
    17	    def handler(request: httpx.Request) -> httpx.Response:
    18	        requests.append(request)
    19	        item = script.pop(0)
    20	        if isinstance(item, Exception):
    21	            raise item
    22	        status, body = item if isinstance(item, tuple) else (200, item)
    23	        return httpx.Response(status, json=body)
    24	
    25	    llm = OpenAICompatibleLLM("http://llm/v1", "sk-test", "m", retry_backoff=0, transport=httpx.MockTransport(handler))
    26	    return llm, requests
    27	
    28	
    29	async def test_returns_message_as_is_and_parses_usage():
    30	    llm, requests = llm_with(OK)
    31	    completion = await llm.complete([{"role": "user", "content": "x"}], [])
    32	    assert completion.message == OK["choices"][0]["message"]
    33	    assert completion.usage == Usage(10, 2, 8)
    34	    assert str(requests[0].url) == "http://llm/v1/chat/completions"
    35	
    36	
    37	async def test_missing_cache_details_means_unknown_not_zero():
    38	    llm, _ = llm_with({**OK, "usage": {"prompt_tokens": 1, "completion_tokens": 1}})
    39	    assert (await llm.complete([], [])).usage.cached is None
    40	
    41	
    42	async def test_transient_errors_are_retried():
    43	    llm, requests = llm_with((503, {}), httpx.ConnectError("reset"), OK)
    44	    assert (await llm.complete([], [])).message["content"] == "hi"
    45	    assert len(requests) == 3
    46	
    47	
    48	async def test_gives_up_after_retries():
    49	    llm, _ = llm_with((502, {}), (502, {}), (502, {}))
    50	    with pytest.raises(LLMError, match="after 3 attempts"):
    51	        await llm.complete([], [])
    52	
    53	
    54	async def test_client_error_fails_fast_with_response_body():
    55	    llm, requests = llm_with((400, {"error": {"message": "maximum context length is 32768 tokens"}}))
    56	    with pytest.raises(LLMError, match="maximum context length"):
    57	        await llm.complete([], [])
    58	    assert len(requests) == 1
    59	
    60	
    61	async def test_error_body_with_200_fails_fast():
    62	    llm, _ = llm_with({"error": {"message": "upstream overloaded"}})
    63	    with pytest.raises(LLMError, match="Unexpected LLM response"):
    64	        await llm.complete([], [])
    65	
    66	
    67	async def test_sends_reasoning_model_compatible_payload_and_custom_headers():
    68	    requests = []
    69	
    70	    def handler(request):
    71	        requests.append(request)
    72	        return httpx.Response(200, json=OK)
    73	
    74	    llm = OpenAICompatibleLLM("http://llm/v1", "sk", "m", max_tokens=123, headers={"x-session": "s1"},
    75	                              transport=httpx.MockTransport(handler))
    76	    await llm.complete([], [])
    77	    body = json.loads(requests[0].content)
    78	    assert body["max_completion_tokens"] == 123 and "max_tokens" not in body and "temperature" not in body
    79	    assert requests[0].headers["x-session"] == "s1" and requests[0].headers["user-agent"].startswith("loola-agent/")
    41	async def test_search_without_matches_says_so():
    42	    result = await Toolbox([Direct()], deferred=[ISSUE]).call("tool_search", '{"query": "kubernetes"}')
    43	    assert result.startswith("No tools match")
    44	
    45	
    46	async def test_tool_call_runs_a_deferred_tool():
    47	    args = {"name": "issue_read", "arguments": {
… [7027 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run --frozen pytest -q tests'
````

````
........................................................................ [ 45%]
........................................................................ [ 91%]
..............                                                           [100%]
158 passed, 1 deselected in 9.20s
````

**[tool: webSearch]**

````

````

**[command]** exit=0

````
/bin/bash -lc "rg -n 'name\": \"(get_file_contents|list_issues|pull_request_read|search_issues)' examples/github_tools.json && sed -n '1575,1635p' examples/github_tools.json && cat .python-version"
````

````
1428:      "name": "get_file_contents",
2538:      "name": "list_issues",
3739:      "name": "pull_request_read",
4172:      "name": "search_issues",
            "description": "Label name."
          },
          "owner": {
            "type": "string",
            "description": "Repository owner (username or organization name)",
            "x-mcp-header": "owner"
          },
          "repo": {
            "type": "string",
            "description": "Repository name",
            "x-mcp-header": "repo"
          }
        },
        "required": [
          "owner",
          "repo",
          "name"
        ]
      }
    },
    {
      "name": "get_latest_release",
      "toolset": "repos",
      "read_only": true,
      "description": "Get the latest release in a GitHub repository",
      "parameters": {
        "type": "object",
        "properties": {
          "owner": {
            "type": "string",
            "description": "Repository owner",
            "x-mcp-header": "owner"
          },
          "repo": {
            "type": "string",
            "description": "Repository name",
            "x-mcp-header": "repo"
          }
        },
        "required": [
          "owner",
          "repo"
        ]
      }
    },
    {
      "name": "get_me",
      "toolset": "context",
      "read_only": true,
      "description": "Get details of the authenticated GitHub user. Use this when a request is about the user's own profile for GitHub. Or when information is missing to build other tool calls.",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    },
    {
      "name": "get_notification_details",
      "toolset": "notifications",
      "read_only": true,
      "description": "Get detailed information for a specific GitHub notification, always call this tool when the user asks for details about a specific notification, if you don't know the ID list notifications first.",
      "parameters": {
3.13
````

**[command]** exit=0

````
/bin/bash -lc "curl -fsSL 'https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4.1-Flash/tree/main/encoding' | jq -r '.[] | [.path,.size] | @tsv'"
````

````
encoding/tests	0
encoding/README.md	12164
encoding/encoding.py	37962
encoding/test_encoding.py	22449
````

**[command]** exit=0

````
/bin/bash -lc "curl -fsSL 'https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4.1-Flash/tree/main' | jq -r '.[]| select(.path|test(\"tokeniz|encoding\")) | [.path,.size] | @tsv'"
````

````
encoding	0
tokenizer.json	6367257
tokenizer_config.json	801
````

**[agent]**

The test suite passed with 158 tests and one live test deselected. The compaction tests count JSON bytes, while the server counts a rendered chat template. I’ll check that difference against the target model’s published encoder and reproduce the cancellation and tool-dispatch edge cases separately.

**[command]** exit=0

````
/bin/bash -lc "nl -ba examples/github_tools.json | sed -n '1428,1510p;4172,4255p'"
````

````
1428	      "name": "get_file_contents",
  1429	      "toolset": "repos",
  1430	      "read_only": true,
  1431	      "description": "Get the contents of a file or directory from a GitHub repository",
  1432	      "parameters": {
  1433	        "type": "object",
  1434	        "properties": {
  1435	          "fields": {
  1436	            "type": "array",
  1437	            "items": {
  1438	              "type": "string",
  1439	              "enum": [
  1440	                "type",
  1441	                "name",
  1442	                "path",
  1443	                "size",
  1444	                "sha",
  1445	                "url",
  1446	                "git_url",
  1447	                "html_url",
  1448	                "download_url"
  1449	              ]
  1450	            },
  1451	            "description": "Subset of fields to return for each entry when the path is a directory. If omitted, all fields are returned. Ignored when the path is a single file. Use this to reduce response size when listing directories and you only need specific fields, e.g. just 'name' and 'type'."
  1452	          },
  1453	          "owner": {
  1454	            "type": "string",
  1455	            "description": "Repository owner (username or organization)",
  1456	            "x-mcp-header": "owner"
  1457	          },
  1458	          "path": {
  1459	            "type": "string",
  1460	            "description": "Path to file/directory",
  1461	            "default": "/"
  1462	          },
  1463	          "ref": {
  1464	            "type": "string",
  1465	            "description": "Accepts optional git refs such as `refs/tags/{tag}`, `refs/heads/{branch}` or `refs/pull/{pr_number}/head`"
  1466	          },
  1467	          "repo": {
  1468	            "type": "string",
  1469	            "description": "Repository name",
  1470	            "x-mcp-header": "repo"
  1471	          },
  1472	          "sha": {
  1473	            "type": "string",
  1474	            "description": "Accepts optional commit SHA. If specified, it will be used instead of ref"
  1475	          }
  1476	        },
  1477	        "required": [
  1478	          "owner",
  1479	          "repo"
  1480	        ]
  1481	      }
  1482	    },
  1483	    {
  1484	      "name": "get_gist",
  1485	      "toolset": "gists",
  1486	      "read_only": true,
  1487	      "description": "Get gist content of a particular gist, by gist ID",
  1488	      "parameters": {
  1489	        "type": "object",
  1490	        "properties": {
  1491	          "gist_id": {
  1492	            "type": "string",
  1493	            "description": "The ID of the gist"
  1494	          }
  1495	        },
  1496	        "required": [
  1497	          "gist_id"
  1498	        ]
  1499	      }
  1500	    },
  1501	    {
  1502	      "name": "get_global_security_advisory",
  1503	      "toolset": "security_advisories",
  1504	      "read_only": true,
  1505	      "description": "Get a global security advisory",
  1506	      "parameters": {
  1507	        "type": "object",
  1508	        "properties": {
  1509	          "ghsaId": {
  1510	            "type": "string",
  4172	      "name": "search_issues",
  4173	      "toolset": "issues",
  4174	      "read_only": true,
  4175	      "description": "Search issues using natural-language semantic matching. Best for conceptual or paraphrased queries (e.g. \"login fails after password reset\"). Already scoped to is:issue.",
  4176	      "parameters": {
  4177	        "type": "object",
  4178	        "properties": {
  4179	          "fields": {
  4180	            "type": "array",
  4181	            "items": {
  4182	              "type": "string",
  4183	              "enum": [
  4184	                "number",
  4185	                "title",
  4186	                "body",
  4187	                "state",
  4188	                "state_reason",
  4189	                "draft",
  4190	                "locked",
  4191	                "html_url",
  4192	
… [2839 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc "curl -fsSL 'https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4.1-Flash' | jq -r .sha"
````

````
314113f8a7dadb388215396ba5fbee2c610a04d6
````

**[command]** exit=0

````
/bin/bash -lc "curl -fsSL 'https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/314113f8a7dadb388215396ba5fbee2c610a04d6/encoding/encoding.py' -o model_encoding.py && curl -fsSL 'https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/314113f8a7dadb388215396ba5fbee2c610a04d6/tokenizer.json' -o model_tokenizer.json && rg -n '"'^(import|from|[A-Za-z_]+ =|def encode_messages)|''^    (tools|thinking_mode)|raise |'"\\b(exec|eval|open|system|__import__)\\(' model_encoding.py | head -125"
````

````
20:from typing import Any, Dict, List, Union, Optional, Tuple
21:import copy
22:import json
23:import re
35:USER_SP_TOKEN = "<｜User｜>"
36:ASSISTANT_SP_TOKEN = "<｜Assistant｜>"
37:LATEST_REMINDER_SP_TOKEN = "<｜latest_reminder｜>"
39:IMAGE_PLACEHOLDER = "<｜deepseek_image｜>"
40:IMAGE_TAG_PATTERN = re.compile(r"<image>(.*?)</image>", re.DOTALL)
43:DS_TASK_SP_TOKENS = {
51:VALID_TASKS = set(DS_TASK_SP_TOKENS.keys())
278:        raise ValueError("Malformed <image>path</image> tag")
289:            raise ValueError("Image path must not be empty")
319:        raise ValueError("Image block does not contain a valid source")
345:                raise ValueError(
359:        raise ValueError(
365:        raise ValueError(
426:SYSTEM_SP_TOKEN = "<｜System｜>"
435:tool_calls_template = (
443:REASONING_EFFORT_TEMPLATE = (
453:DEFAULT_REASONING_EFFORT = "high"
458:    thinking_mode: str,
481:TOOLS_TEMPLATE = """## Tools
511:    tools_json = [to_json(t) for t in tools]
588:    thinking_mode: str,
603:    tools = msg.get("tools")
663:        raise NotImplementedError("deepseek_v41 merges tool messages into user; please preprocess with merge_tool_messages()")
710:        raise NotImplementedError(f"Unknown role: {role}")
772:    thinking_mode: str,
810:def encode_messages(
812:    thinking_mode: str,
849:    with open(input_file) as file:
861:                raise ValueError("A case with tools must contain at least one message")
908:            raise ValueError(f"Tool call format error: expected '>\\n' but got '{_}'")
914:            raise ValueError("Missing special token in tool calls")
920:            raise ValueError(f"Tool name format error: '{tool_name_content}'")
929:                raise ValueError(f"Parameter format error: '{param_content}'")
933:                raise ValueError(f"Duplicate parameter name: '{param_name}'")
938:                raise ValueError(f"Parameter format error: expected '>\\n' but got '{content}'")
````

**[command]** exit=0

````
/bin/bash -lc "sed -n '420,523p;810,878p' model_encoding.py"
````

````
return len(text), content, None

# ============================================================
# V4.1 Special Tokens and DSML Tag Names
# ============================================================

SYSTEM_SP_TOKEN = "<｜System｜>"

tool_calls_block_name: str = " calls"
tool_call_tag_name: str = " invoke"
tool_parameter_tag_name: str = " parameter"

tool_call_template: str = (
    "<{dsml_token}{tool_call_tag_name} name=\"{name}\">\n{arguments}\n</{dsml_token}{tool_call_tag_name}>"
)
tool_calls_template = (
    "<{dsml_token}{tc_block_name}>\n{tool_calls}\n</{dsml_token}{tc_block_name}>"
)

# ============================================================
# Reasoning Effort (numeric budget)
# ============================================================

REASONING_EFFORT_TEMPLATE = (
    "Reasoning Effort: {budget} "
    "(range 1-100, the higher the value, the more thorough the reasoning)\n\n"
)

REASONING_EFFORT_MAPPINGS: Dict[str, int] = {
    "low": 50,
    "high": 75,
    "max": 100,
}
DEFAULT_REASONING_EFFORT = "high"


def render_reasoning_effort(
    index: int,
    thinking_mode: str,
    effort: Union[str, int, None],
) -> str:
    """Render the V4.1 numeric reasoning effort prefix (thinking mode, index 0 only)."""
    if effort is None:
        effort = DEFAULT_REASONING_EFFORT
    assert (
        type(effort) is int and 1 <= effort <= 100
    ) or effort in REASONING_EFFORT_MAPPINGS, (
        "Invalid reasoning effort for deepseek_v41: "
        f"{effort}, should be int within [1,100] or {list(REASONING_EFFORT_MAPPINGS)}"
    )
    if type(effort) is str:
        effort = REASONING_EFFORT_MAPPINGS[effort]
    if index == 0 and thinking_mode == "thinking":
        return REASONING_EFFORT_TEMPLATE.format(budget=effort)
    return ""


# ============================================================
# Tools rendering
# ============================================================

TOOLS_TEMPLATE = """## Tools

You have access to a set of tools to help answer the user's question. You can invoke tools by writing a "<{dsml_token}{tc_block_name}>" block like the following:

<{dsml_token}{tc_block_name}>
<{dsml_token}{tool_call_tag_name} name="$TOOL_NAME">
<{dsml_token}{tool_parameter_tag_name} name="$PARAMETER_NAME" string="true|false">$PARAMETER_VALUE</{dsml_token}{tool_parameter_tag_name}>
...
</{dsml_token}{tool_call_tag_name}>
<{dsml_token}{tool_call_tag_name} name="$TOOL_NAME2">
...
</{dsml_token}{tool_call_tag_name}>
</{dsml_token}{tc_block_name}>

String parameters should be specified as is and set `string="true"`. For all other types (numbers, booleans, arrays, objects), pass the value in JSON format and set `string="false"`.

If thinking_mode is enabled (triggered by {thinking_start_token}), you MUST output your complete reasoning inside {thinking_start_token}...{thinking_end_token} BEFORE any tool calls or final response.

Otherwise, output directly after {thinking_end_token} with tool calls or final response.

### Available Tool Schemas

{tool_schemas}

You MUST strictly follow the above defined tool name and parameter schemas to invoke tool calls.
"""


def render_tools(tools: List[Dict[str, Union[str, Dict[str, Any]]]]) -> str:
    """Render tool schemas into the V4.1 system prompt format."""
    tools_json = [to_json(t) for t in tools]

    return TOOLS_TEMPLATE.format(
        tool_schemas="\n".join(tools_json),
        dsml_token=dsml_token,
        tc_block_name=tool_calls_block_name,
        tool_call_tag_name=tool_call_tag_name,
        tool_parameter_tag_name=tool_parameter_tag_name,
        thinking_start_token=thinking_start_token,
        thinking_end_token=thinking_end_token,
    )


def encode_messages(
    messages: List[Dict[str, Any]],
    thinking_mode: str,
    context: Optional[List[Dict[str, Any]]] = None,
    drop_thinking: bool = True,
    add_default_bos_token: bool = True,
    reasoning_effort: Union[str, int, None] = None,
    return_multi_modal_data: bool = False,
) -> Any:
    """Encode 
… [2355 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"httpx\", \"jsonschema\", \"pyyaml\", \"tokenizers\"]
# ///
from loola_agent import DummyTool, Toolbox, CompactionPolicy, build_context, UserMessage
from loola_agent.compaction import context_bound
from model_encoding import encode_messages
from tokenizers import Tokenizer
tok = Tokenizer.from_file(\"model_tokenizer.json\")
tb=Toolbox([DummyTool(\"x\",\"x\",{\"type\":\"object\"})])
events=[UserMessage(\"a\")]
m=build_context(\"s\",events)
b=context_bound(\"s\",events,tb.schemas())
m[0][\"tools\"]=tb.schemas()
for mode in (\"thinking\",\"chat\"):
    enc=tok.encode(encode_messages(m,mode),add_special_tokens=False)
    print(mode,b,len(enc.ids),CompactionPolicy(b+1024,summary_max_tokens=32).fits(b,1024), \"window\",b+1024)
PY"
````

````
Downloading tokenizers (3.2MiB)
Downloading hf-xet (4.1MiB)
 Downloaded tokenizers
 Downloaded hf-xet
Installed 24 packages in 28ms
thinking 201 266 True window 1225
chat 201 241 True window 1225
````

**[command]** exit=1

````
/bin/bash -lc "UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run --no-sync - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = []
# ///
import asyncio
from tests.test_compaction import SimulatedLLM, Big, run
from tests.test_agent import FakeLLM, reply, call, Echo
from loola_agent import *
async def main():
    t=Toolbox([Echo()])
    a=Agent(FakeLLM(reply(None,[call(\"a\",\"side-effect\")],finish=\"length\"),reply(\"done\")),t)
    print(\"truncated\",[(type(e).__name__,getattr(e,\"status\",\"\")) async for e in a.send(\"do\")])
    llm=FakeLLM(reply(\"done\"))
    a=Agent(llm,t)
    i=a.send(\"one\")
    await anext(i)
    await i.aclose()
    [e async for e in a.send(\"two\")]
    print(\"cancelled before response\", [m[\"role\"] for m in llm.calls[-1]])
    async with Bash() as shell:
        print(\"bash\",await shell.run({\"command\":\"set -o pipefail\"}))
    class Open(DummyTool):
        pass
    tb=Toolbox([Open(\"x\",\"\",{\"type\":\"object\",\"properties\":{},\"additionalProperties\":True})])
    print(\"extras\",await tb.call(\"x\",'{\"typo\": 1}'))
    for count in range(2,18):
        s=Completion({\"role\":\"assistant\",\"content\":\"S\"*2800},\"stop\",Usage())
        llm=SimulatedLLM(window=20000,turns=count,summary=s,bytes_per_token=3)
        a=Agent(llm,Toolbox([Big(1500)]),compaction=CompactionPolicy(20000,4500,0,1000))
        ev=await run(a)
        bad=[(e.tokens_before,e.tokens_after) for e in ev if isinstance(e,Compaction) and e.tokens_after >= e.tokens_before]
        if bad: 
            print(\"compaction grows\",count,bad);break
asyncio.run(main())
PY"
````

````
warning: `--no-sync` is a no-op for Python scripts with inline metadata, which always run in isolation
Traceback (most recent call last):
  File "<string>", line 6, in <module>
    from tests.test_compaction import SimulatedLLM, Big, run
  File "/tmp/loola-review.iTsTm7q4/tests/test_compaction.py", line 4, in <module>
    import pytest
ModuleNotFoundError: No module named 'pytest'
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"pytest\",\"httpx\",\"jsonschema\",\"pyyaml\"]
# ///
import asyncio
from tests.test_compaction import SimulatedLLM, Big, run
from tests.test_agent import FakeLLM, reply, call, Echo
from loola_agent import *
async def main():
    t=Toolbox([Echo()])
    a=Agent(FakeLLM(reply(None,[call(\"a\",\"side-effect\")],finish=\"length\"),reply(\"done\")),t)
    print(\"truncated\",[(type(e).__name__,getattr(e,\"status\",\"\")) async for e in a.send(\"do\")])
    llm=FakeLLM(reply(\"done\"))
    a=Agent(llm,t)
    i=a.send(\"one\")
    await anext(i)
    await i.aclose()
    [e async for e in a.send(\"two\")]
    print(\"cancelled before response\", [m[\"role\"] for m in llm.calls[-1]])
    async with Bash() as shell:
        print(\"bash\",await shell.run({\"command\":\"set -o pipefail\"}))
    tb=Toolbox([DummyTool(\"x\",\"\",{\"type\":\"object\",\"properties\":{},\"additionalProperties\":True})])
    print(\"extras\",await tb.call(\"x\",'{\"typo\": 1}'))
    for count in range(2,18):
        s=Completion({\"role\":\"assistant\",\"content\":\"S\"*2800},\"stop\",Usage())
        llm=SimulatedLLM(window=20000,turns=count,summary=s,bytes_per_token=3)
        a=Agent(llm,Toolbox([Big(1500)]),compaction=CompactionPolicy(20000,4500,0,1000))
        ev=await run(a)
        bad=[(e.tokens_before,e.tokens_after) for e in ev if isinstance(e,Compaction) and e.tokens_after >= e.tokens_before]
        if bad: 
            print(\"compaction grows\",count,bad);break
asyncio.run(main())
PY"
````

````
Installed 18 packages in 55ms
truncated [('UserMessage', ''), ('AssistantMessage', ''), ('ToolStarted', ''), ('ToolResult', ''), ('AssistantMessage', ''), ('RunFinished', 'done')]
cancelled before response ['system', 'user', 'user']
bash Exit code: 2
/bin/sh: 1: set: Illegal option -o pipefail

extras {"tool": "x", "arguments": {"typo": 1}, "result": "dummy implementation, no real call"}
compaction grows 6 [(4732, 5371)]
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"pytest\",\"httpx\",\"jsonschema\",\"pyyaml\"]
# ///
import asyncio
from tests.test_compaction import SimulatedLLM, Big, run
from tests.test_agent import FakeLLM, reply, call, Echo
from loola_agent import *
from loola_agent.compaction import SUMMARY_INSTRUCTION
async def main():
    llm=FakeLLM(reply(None,[call(\"a\",\"A\")],finish=\"tool_calls\"),reply(\"answered second\"),reply(\"answered first\"))
    a=Agent(llm,Toolbox([Echo()]))
    g=a.send(\"one\")
    for _ in range(3):
        print(type(await anext(g)).__name__)
    await run(a,\"two\")
    [e async for e in g]
    print(\"overlap\",[(m[\"role\"],m.get(\"tool_call_id\")) for m in llm.calls[-1]])
    llm=SimulatedLLM(50000,12)
    a=Agent(llm,Toolbox([Big(3000)]),compaction=CompactionPolicy(50000,22000,0,1000))
    await run(a)
    llm.turns=14
    await run(a,\"follow-up\")
    for r in llm.requests:
        if r[\"summary\"]:print(\"summary roles\",[m[\"role\"] for m in r[\"messages\"]][-5:])
    class Mutable(Echo):
        async def run(self,args):
            self.description=\"NEW\"
            return \"ok\"
    llm=FakeLLM(reply(None,[call(\"a\",\"A\")],finish=\"tool_calls\"),reply(\"done\"))
    class Record:
        def __init__(self): self.desc=[]
        async def complete(self,messages,tools):
            self.desc.append(tools[0][\"function\"][\"description\"])
            return await llm.complete(messages,tools)
    rec=Record(); await run(Agent(rec,Toolbox([Mutable()])))
    print(\"prefix\",rec.desc)
asyncio.run(main())
PY"
````

````
UserMessage
AssistantMessage
ToolStarted
overlap [('system', None), ('user', None), ('assistant', None), ('tool', 'a'), ('user', None), ('assistant', None), ('tool', 'a')]
prefix ['Echo the text back.', 'NEW']
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"pytest\",\"httpx\",\"jsonschema\",\"pyyaml\"]
# ///
import asyncio
from tests.test_compaction import SimulatedLLM, Big, run
from loola_agent import *
async def main():
    for threshold in range(5000,20000,100):
        llm=SimulatedLLM(50000,8)
        a=Agent(llm,Toolbox([Big(2400)]),compaction=CompactionPolicy(50000,threshold,0,1000))
        await run(a)
        llm.turns=11
        await run(a,\"follow-up\")
        if any(r[\"summary\"] and r[\"messages\"][-2][\"role\"]==\"user\" for r in llm.requests):
            print(\"threshold\",threshold, \"summary role suffix\", next([m[\"role\"] for m in r[\"messages\"]][-4:] for r in llm.requests if r[\"summary\"] and r[\"messages\"][-2][\"role\"]==\"user\"))
            break
asyncio.run(main())
PY"
````

````
threshold 5600 summary role suffix ['tool', 'assistant', 'user', 'user']
````

**[command]** exit=0

````
/bin/bash -lc "nl -ba src/loola_agent/gh_proxy.py | sed -n '208,246p' && nl -ba examples/github_tools.json | sed -n '1625,1710p' && git -C ~/projects/loola-test-task status --porcelain --untracked-files=normal"
````

````
208	    pass
   209	
   210	
   211	@dataclass(frozen=True)
   212	class Gh:
   213	    """Runs `gh` without stdin, with a timeout and bounded output. gh failures (404, rate limit, bad query)
   214	    come back as text for the model; only a missing or logged-out gh is fatal, checked once by `check`."""
   215	    executable: str = "gh"
   216	    timeout: float = 30
   217	    max_output: int = 20_000
   218	
   219	    async def check(self) -> None:
   220	        try:
   221	            code, _, err = await self._exec(["auth", "status", "--hostname", "github.com"])
   222	        except FileNotFoundError:
   223	            raise GhUnavailable(
   224	                f"'{self.executable}' not found: install the GitHub CLI (https://cli.github.com)") from None
   225	        if code != 0:
   226	            raise GhUnavailable(f"gh is not logged in to github.com (run `gh auth login`): {err.strip()}")
   227	
   228	    async def run(self, argv: Argv) -> str:
   229	        try:
   230	            code, out, err = await self._exec(argv)
   231	        except TimeoutError:
   232	            return f"Error: gh timed out after {self.timeout:g}s"
   233	        if code != 0:
   234	            return truncate(f"Error: gh exited with code {code}: {err.strip()}\n{out}".rstrip(), self.max_output)
   235	        return truncate(out, self.max_output)
   236	
   237	    async def _exec(self, argv: Argv) -> tuple[int, str, str]:
   238	        proc = await asyncio.create_subprocess_exec(self.executable, *argv, stdin=subprocess.DEVNULL,
   239	                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   240	        try:
   241	            out, err = await asyncio.wait_for(proc.communicate(), self.timeout)
   242	        finally:
   243	            if proc.returncode is None:  # timed out or cancelled
   244	                proc.kill()
   245	                await proc.wait()
   246	        assert proc.returncode is not None
  1625	      "parameters": {
  1626	        "type": "object",
  1627	        "properties": {}
  1628	      }
  1629	    },
  1630	    {
  1631	      "name": "get_notification_details",
  1632	      "toolset": "notifications",
  1633	      "read_only": true,
  1634	      "description": "Get detailed information for a specific GitHub notification, always call this tool when the user asks for details about a specific notification, if you don't know the ID list notifications first.",
  1635	      "parameters": {
  1636	        "type": "object",
  1637	        "properties": {
  1638	          "notificationID": {
  1639	            "type": "string",
  1640	            "description": "The ID of the notification"
  1641	          }
  1642	        },
  1643	        "required": [
  1644	          "notificationID"
  1645	        ]
  1646	      }
  1647	    },
  1648	    {
  1649	      "name": "get_release_by_tag",
  1650	      "toolset": "repos",
  1651	      "read_only": true,
  1652	      "description": "Get a specific release by its tag name in a GitHub repository",
  1653	      "parameters": {
  1654	        "type": "object",
  1655	        "properties": {
  1656	          "owner": {
  1657	            "type": "string",
  1658	            "description": "Repository owner",
  1659	            "x-mcp-header": "owner"
  1660	          },
  1661	          "repo": {
  1662	            "type": "string",
  1663	            "description": "Repository name",
  1664	            "x-mcp-header": "repo"
  1665	          },
  1666	          "tag": {
  1667	            "type": "string",
  1668	            "description": "Tag name (e.g., 'v1.0.0')"
  1669	          }
  1670	        },
  1671	        "required": [
  1672	          "owner",
  1673	          "repo",
  1674	          "tag"
  1675	        ]
  1676	      }
  1677	    },
  1678	    {
  1679	      "name": "get_repository_tree",
  1680	      "toolset": "git",
  1681	      "read_only": true,
  1682	      "description": "Get the tree structur
… [1336 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"pytest\",\"httpx\",\"jsonschema\",\"pyyaml\"]
# ///
import asyncio
from loola_agent import *
from loola_agent.compaction import choose_cut,context_bound,bound_after_compaction
from tests.test_compaction import SimulatedLLM, Big, run
class Sequence(Big):
    async def run(self,args):return \"x\"*self.sizes.pop(0)
async def main():
    for window in (7000,10000,14000):
        for size in range(500,3500,250):
            for second in range(3000,window,200):
                tool=Sequence()
                tool.sizes=[size,second]
                t=Toolbox([tool]); model=SimulatedLLM(window,2)
                policy=CompactionPolicy(window,keep_recent_tokens=0,summary_max_tokens=1000)
                a=Agent(model,t,compaction=policy)
                try:
                    await run(a)
                except CompactionError as exc:
                    if \"cannot shrink\" not in str(exc):continue
                    b=context_bound(a.system_prompt,a.events,t.schemas()); cut=choose_cut(a.events,b,0)
                    c=Compaction(\"short summary\",cut,b,0,Usage())
                    actual=bound_after_compaction(a.system_prompt,[*a.events,c],t.schemas(),c)
                    if policy.fits(actual,model.max_tokens):
                        print(\"false refusal\",str(exc),\"window\",window,\"outputs\",size,second,\"short after\",actual,\"reserve\",policy.reserve(model.max_tokens));return
asyncio.run(main())
PY"
````

````
false refusal The next request may need 5336 tokens, and compaction cannot shrink it: the most recent turn alone does not fit the 7000-token window. window 7000 outputs 2000 4200 short after 5284 reserve 1676
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"pytest\",\"httpx\",\"jsonschema\",\"pyyaml\"]
# ///
from tempfile import TemporaryDirectory
from pathlib import Path
import time, asyncio
from tests.test_gh_proxy import fake_gh
async def main():
    with TemporaryDirectory() as d:
        gh = fake_gh(Path(d), \"sleep 3\")
        t=time.monotonic()
        print(await gh.run([]),f\"(elapsed {time.monotonic()-t:.2f}s)\")
asyncio.run(main())
PY"
````

````
Error: gh timed out after 1s (elapsed 1.01s)
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"httpx\",\"jsonschema\",\"pyyaml\"]
# ///
import json, asyncio
from pathlib import Path
from loola_agent import Toolbox,load_catalog
async def main():
    t=Toolbox([], deferred=load_catalog(Path(\"examples/github_tools.json\"))[0]); s=await t.call(\"tool_search\",'{\"query\":\"repository\",\"limit\":-1}');print(len(json.loads(s)),len(s.encode()))
asyncio.run(main())
PY"
````

````
Installed 13 packages in 29ms
52 61892
````

**[agent]**

I reproduced an undercount with DeepSeek’s published encoder and a compaction that increased the harness’s own bound. I also confirmed that overlapping `send()` calls can produce two results for one tool-call ID. The checked-in benchmark controls have a separate issue: disabling compaction also disables the local window check.

**[agent]**

Reviewed `63a090c` from an isolated copy. **158 tests passed, one live test deselected.** The checkout and parallel README edit were untouched.

1. **High — The compaction bound can admit an oversized request.** With system prompt `s`, user message `a`, and one minimal tool, `context_bound()` returned **201**. DeepSeek V4.1 Flash’s published encoder counted **266** prompt tokens in thinking mode. With a 1,024-token reply allowance, the harness admits a 1,225-token window although the request needs 1,290. The template adds tool instructions that the JSON-byte calculation never counts. The test double counts serialized JSON and therefore misses this failure. The guarantee needs a justified bound for the supported template, including its fixed tool preamble and the cost of rendering a generated reply back into history. [compaction.py:66](<local path>), [compaction.py:69](<local path>), [test_compaction.py:35](<local path>), [DeepSeek encoder](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/314113f8a7dadb388215396ba5fbee2c610a04d6/encoding/encoding.py)

2. **High — Compaction rejects recoverable runs and accepts summaries that grow the context.** In a 7,000-token window, the harness reported that compaction could not shrink a bound of 5,336. A short summary at the same cut gave **5,284 + 1,676 reserve = 6,960**, which fits. In a separate run, it committed a compaction from **4,732 to 5,371**. Both follow from adding a *token* cap to a *byte*-based estimate, then checking only `fits` after the summary arrives. Simplify the preflight to what an empty summary can prove. Check the returned summary for both fit and strict reduction, and retain its paid usage even when discarded. [agent.py:83](<local path>), [agent.py:98](<local path>)

3. **High — A truncated tool batch still executes.** I supplied `finish_reason="length"` with one parseable tool call. The agent dispatched it, requested another completion, and finished `done`. A partial batch can therefore cause side effects and score as a successful run. Handle `length` before dispatch and leave a protocol-valid history for the next `send()`. The existing truncation test covers text only. [agent.py:53](<local path>), [test_agent.py:64](<local path>)

4. **High — Overlapping sends corrupt tool-call history.** I paused one iterator at `ToolStarted`, ran a second `send()`, then resumed the first. The second send recorded the still-live call as interrupted. The first then appended its real result **for the same ID, after an unrelated assistant message**. The next request contained both. One active-send guard, released in `finally`, preserves the approved cancellation behavior without adding a queue. [agent.py:39](<local path>), [agent.py:67](<local path>)

5. **High — The required before/after result is missing, and the two arms do not yet share an enforced window.** In this commit, setting `LLM_CONTEXT_WINDOW` enables compaction and unsetting it removes the local limit. On a larger-window endpoint, the baseline can continue beyond 64k. For the planned eight runs, enforce the same 64k limit in both arms, pin the task inputs, and score the requested outcome independently of `RunFinished("done")`. A model can finish normally after a required write returned “not implemented.” Include failed runs and summary costs. The explicit answers to both task questions, `AGENTS.md`, and the development-session log are also pending at this SHA. [cli.py:60](<local path>), [agent.py:62](<local path>), [TASK.md:3](<local path>), [TASK.md:5](<local path>), [TASK.md:9](<local path>)

6. **Medium — Strict templates can receive consecutive user messages through two ordinary paths.** Closing `send()` after its first `UserMessage` and sending again produced `system, user, user`. Separately, a follow-up turn selected for summarization produced a summary request ending `assistant, user, user`. The post-compaction projection already accounts for this constraint. Apply it to interrupted input as well, and select a summary boundary where appending the instruction is legal. [agent.py:44](<local path>), [compaction.py:94](<local path>), [events.py:69](<local path>)

7. **Medium — The declared tool prefix is only stable while tool objects remain unchanged.** `schemas()` rebuilds declarations from live attributes on every request. A direct tool that changed its description during `run()` changed the next request’s prefix and invalidated the previous sizing anchor. Snapshot the effective declarations once. The same normalization can fix another contract violation: an explicit `additionalProperties: true` currently overrides the harness rule, and I confirmed a misspelled argument reached the tool. Use the normalized schema for declaration, discovery, validation, and error text. [tools.py:36](<local path>), [tools.py:64](<local path>)

<details><summary>Other runtime defects and smaller cuts</summary>

- **Medium — `bash` launches `/bin/sh`.** On this host, `set -o pipefail` exited 2 under `dash`. Select Bash explicitly when creating the subprocess. [bash.py:37](<local path>)
- **Medium — GitHub infrastructure failures go back to the model.** After startup, `Gh.run()` converts every timeout and nonzero exit into tool text. An expired login or service outage can consume benchmark turns as if the model could correct its arguments. Keep actionable query errors as tool results and surface infrastructure failures at the CLI boundary, as the brief specifies. [gh_proxy.py:228](<local path>)
- **Low — The search `limit` knob undermines the purpose of discovery.** `{"query":"repository","limit":-1}` returned **52 schemas and 61,892 bytes** through Python’s negative slicing. Removing the knob and returning the existing top five is the smaller implementation. [tools.py:71](<local path>), [tools.py:83](<local path>)

</details>

**not approved** — Remaining blockers are request sizing and compaction progress, tool execution after truncation, invalid histories during interruption or overlapping sends, unenforced tool and shell contracts, infrastructure-error handling, and the missing comparable measurements and submission artifacts.

---

## [input]

[bb message from thread:thr_…]

Here is my remediation plan for your findings. Critique it hard. Tell me what is still wrong. Use only material unresolved issues as blockers. Same artifact (commit 63a090c) and the same brief v1; nothing is implemented yet.

F1 (bound misses template overhead) — PARTIALLY ACCEPT. Real gap, but it only concerns sizes that were never measured. Fix: calibrate from the session itself. `template_overhead = max(0, P_first - bytes_bound(context_first))`, where P_first is the server's prompt count of the first request and bytes_bound is the same byte estimate we use elsewhere; it is a pure function of the events (first AssistantMessage), no state. Add it to every byte-based bound (post-compaction head). The very first request is the only one sized without a measurement: if system+tools+task alone exceed the window, nothing can help, and the server's 400 surfaces as LLMError (fail loud). The README/docstring will state this precisely instead of "never exceeds". Re-rendering a generated reply: completion_tokens already counts the tool-call markup the model emitted; the per-message overhead (16) covers role wrapping. Test: the simulator gains a fixed template preamble (e.g. 300 tokens) not visible in JSON bytes.

F2 (compaction preflight mixes units; growth accepted) — ACCEPT. Preflight with an empty summary only: if `bound_after(empty) >= bound` → skip (fits) / CompactionError (doesn't). After the summary: apply only if `after < bound` and fits; if it fits but did not shrink → discard it (no event), log a warning, and still add its usage to the run (`_compact_if_needed` returns (compaction | None, paid_usage)). If it doesn't fit → CompactionError. Test: summary longer than the savings is discarded, cost still counted.

F3 (truncated tool batch executes) — ACCEPT. If finish_reason == "length" and there are tool calls: do not execute; append a ToolResult per call "Error: not executed: your reply was cut off by the token limit" (history stays protocol-valid), then RunFinished("truncated"). Test included.

F4 (overlapping sends) — ACCEPT. `send()` raises RuntimeError if another send is active; flag released in `finally`. Test.

F5 (measurements) — ACCEPT the method points, they are the next phase (not code in this commit): both arms run with the same 64k window enforced by the harness. Code change: `CompactionPolicy(context_window, compact=False)` for the baseline — same bound check, but instead of compacting it fails with CompactionError ("context window exceeded"), which the benchmark records as a failed run. Scoring by a script against ground truth captured via `gh` at run time (PR numbers; top changed files), independent of RunFinished. Failed runs and summary costs are in the table. AGENTS.md, session log are added before the final push; README (written in parallel) already contains the answers to both questions.

F6 (consecutive user messages) — ACCEPT with one unified rule instead of two special cases: `build_context` merges adjacent user messages into one (joined by a blank line). This covers the cancelled-send case, the post-compaction head (which then becomes just "user messages... + summary" through the same rule), and the summary request, which I will build as `build_context(events[:cut] + [UserMessage(SUMMARY_INSTRUCTION)])`. Cache: the merged last user message still shares the whole prefix before it.

F7 (tool declarations rebuilt per request; explicit additionalProperties:true wins) — PARTIALLY ACCEPT. Snapshot declarations once in Toolbox.__init__ (cheap, guarantees a byte-stable prefix). REJECT forcing additionalProperties:false over an explicit `true`: an explicit schema is the tool author's contract (free-form key/value tools exist); the harness default only fills the common omission. No catalog tool has a top-level `true`.

Bash runs /bin/sh — ACCEPT: `executable="/bin/bash"`. Test with `set -o pipefail`.

gh infra failures to the model — PARTIALLY ACCEPT (gh_proxy is internal test infra): timeout, `(HTTP 401)` and `(HTTP 5xx)` raise GhUnavailable → CLI boundary; 404/422/403-rate-limit and query errors stay tool results (the model can change its request or wait).

tool_search limit — ACCEPT: remove the knob, fixed top 5.

Anything still wrong in this plan? End with: fully approved / not approved + remaining blockers only.

**[agent]**

I’ll check the proposed sizing rule against the actual 91-tool baseline and trace what reaches the benchmark log when a summary is discarded or fails. Those two details determine whether the fixes preserve the guarantee and produce a fair comparison.

**[command]** exit=0

````
/bin/bash -lc "ls -ld /tmp/loola-review.iTsTm7q4 /tmp/loola-review.iTsTm7q4/model* && nl -ba <local path> | sed -n '11,15p;26,42p;48,54p'"
````

````
drwx------ 10 bb bb    4096 Nov 24 11:53 /tmp/loola-review.iTsTm7q4
-rw-rw-r--  1 bb bb   37962 Nov 24 11:53 /tmp/loola-review.iTsTm7q4/model_encoding.py
-rw-rw-r--  1 bb bb 6367257 Nov 24 11:53 /tmp/loola-review.iTsTm7q4/model_tokenizer.json
    11	- Это **минималистичный showcase**, а не продукт. Читаемость за минуты важнее полноты. Никакого enterprise-комбайна, никаких «на всякий случай».
    12	- Оверинжиниринг — главный враг. Если можно проще без потери смысла — проще. Предлагать сокращения кода приветствуется.
    13	- **Один явный путь, fail fast.** Никаких fallback-веток, деградированных режимов, запасных парсеров, тихих ретраев «чтобы заработало». Ошибка — видимая, с понятным сообщением.
    14	- Ошибки модели (кривые аргументы, неизвестный тул, ненулевой exit code) возвращаются модели текстом для самоисправления; ошибки инфраструктуры и баги harness — исключения на границе (CLI).
    15	- Протокол виден: без фреймворков и даже без `openai` SDK (httpx + wire format).
    26	## Решения на развилках (и почему) — одобрены владельцем
    27	
    28	1. **Базовые фиксы исходного кода** (ревью нашло): assistant message кладём в историю как есть (параллельные tool calls, `reasoning_content` — DeepSeek без него 400); кривой JSON аргументов → ошибка модели; обрезка вывода head+tail; timeout/retry; `finish_reason=length` и пустой ответ = провал, а не успех; учёт usage; bash: stdin закрыт, `LLM_*` не видны командам, вывод в temp-файл (фон `cmd &` не блокирует, частичный вывод при таймауте), kill process group по таймауту/отмене/выходу.
    29	2. **Фоновые процессы**: только правило в описании bash-тула (`cmd > log 2>&1 &`), никаких bash_output/kill тулов — оверкилл.
    30	3. **Динамические тулы без нативного API**: массив `tools` никогда не меняется (у open-source chat templates tools рендерятся в начало промпта → любое изменение = полный промах KV-cache). В промпте: direct-тулы + `tool_search` + `tool_call(name, arguments)`. Схемы найденных тулов приходят как tool result (в хвост истории).
    31	4. **Constrained decoding / `strict` не используем вообще** (владелец: не поддерживать несколько вариантов). У vLLM при `tool_choice=auto` без strict его и так нет. Компенсация — валидация по JSON Schema в harness, ошибка со схемой уходит модели.
    32	5. **После компакшена найденные тулы НЕ добавляем в `tools`** и не «вспоминаем» тулы/скиллы явно: модель найдёт заново (ошибка валидации всё равно содержит схему).
    33	6. **Неизвестные аргументы отклоняем** (`additionalProperties: false` поверх схемы при валидации), т.к. почти все реальные схемы молча глотают опечатки. Опциональность на уровне тула — не делаем.
    34	7. **Deferred-тул можно вызвать и напрямую по имени** — следствие одного реестра для диспатча; совпадает с нативными API (Anthropic tool_reference, OpenAI tool_search). Основной путь — `tool_call`.
    35	8. **BM25 свой (~15 строк)**: зависимость (rank-bm25/bm25s) тянет numpy ради 91 документа и прячет механику.
    36	9. **Каталог тулов** — список из GitHub MCP server v2.2.0 (91 тул, MIT) **только как данные** (имя/описание/схема). MCP-протокол не подключаем — за рамками. Исполнение: `DummyTool` для детерминированных тестов; `gh_proxy` (14 read-only тулов через `gh api`) — только для живых прогонов, внутренняя тестовая обвязка, пока остаётся в пакете.
    37	10. **Прерванные tool calls** (отмена посреди тула): в начале следующего `send()` каждому незакрытому вызову — синтетический результат «interrupted, may have partial side effects, check state and re-run if needed». Не перезапуск (повтор побочных эффектов) и не удаление (ложь модели).
    38	11. **Скиллы** (Agent Skills): в system prompt только каталог (name/description/path), тело модель читает `bash cat`. `--skills-mode eager` — baseline для замера. Невалидный SKILL.md — ошибка старта.
    39	12. **Компакшен** (`compaction.py`): гарантия без процентов. Верхняя граница размера следующего запроса = точные `usage` сервера для измеренного + UTF-8 байты для неизмеренно
… [2002 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc "rg -n 'MESSAGE_OVERHEAD|def reserve|known =|def bound_after|def summary_request|def context_bound|def build_context|async def _compact_if_needed|expected =|policy.fits\\(after|usage \\+=|self.compaction|transcript.open|class Toolbox|def schemas|Draft202012Validator\\(' src/loola_agent"
````

````
src/loola_agent/cli.py:65:        with transcript.open("a") as f:
src/loola_agent/events.py:69:def build_context(system_prompt: str, events: list[Event]) -> list[dict]:
src/loola_agent/tools.py:24:class Toolbox:
src/loola_agent/tools.py:36:    def schemas(self) -> list[dict]:
src/loola_agent/tools.py:64:    return Draft202012Validator({"additionalProperties": False, **schema})
src/loola_agent/compaction.py:20:MESSAGE_OVERHEAD = 16  # tokens a chat template may add around one message (role markers, separators)
src/loola_agent/compaction.py:50:    def reserve(self, reply_max_tokens: int) -> int:
src/loola_agent/compaction.py:51:        instruction = _bytes(SUMMARY_INSTRUCTION) + MESSAGE_OVERHEAD
src/loola_agent/compaction.py:61:def context_bound(system_prompt: str, events: list[Event], tools: list[dict]) -> int:
src/loola_agent/compaction.py:69:            known = usage.prompt + usage.completion
src/loola_agent/compaction.py:71:            known = tokens_after
src/loola_agent/compaction.py:76:def bound_after_compaction(system_prompt: str, events: list[Event], tools: list[dict], compaction: Compaction) -> int:
src/loola_agent/compaction.py:94:def summary_request(system_prompt: str, events: list[Event], cut: int) -> list[dict]:
src/loola_agent/compaction.py:103:    return _bytes(message) + MESSAGE_OVERHEAD
src/loola_agent/agent.py:34:        self.compaction = compaction
src/loola_agent/agent.py:47:            if self.compaction and (compaction := await self._compact_if_needed(self.compaction)):
src/loola_agent/agent.py:48:                usage += compaction.usage
src/loola_agent/agent.py:52:            usage += completion.usage
src/loola_agent/agent.py:70:    async def _compact_if_needed(self, policy: CompactionPolicy) -> Compaction | None:
src/loola_agent/agent.py:84:        expected = bound_after_compaction(self.system_prompt, [*self.events, empty], tools, empty) \
src/loola_agent/agent.py:99:        if not policy.fits(after, reply):
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"httpx\", \"jsonschema\", \"pyyaml\", \"tokenizers\"]
# ///
from pathlib import Path
from loola_agent import Bash,Toolbox,load_catalog,load_skills,skills_prompt,SYSTEM_PROMPT,UserMessage,build_context
from loola_agent.compaction import context_bound
from loola_agent.gh_proxy import Gh, gh_tools
from tokenizers import Tokenizer
from model_encoding import encode_messages
spec, hint=load_catalog(Path(\"examples/github_tools.json\"))
live, hint2=gh_tools(spec,Gh())
t=Toolbox([Bash(),*live]).schemas()
system=SYSTEM_PROMPT+\"\\n\\n\"+skills_prompt(load_skills(Path(\"skills\")),eager=True)
e=[UserMessage(\"Review this PR.\")]
m=build_context(system,e)
print(\"init\",context_bound(system,[],t),\"first\",context_bound(system,e,t))
m[0][\"tools\"]=t
print(\"rendered\",len(Tokenizer.from_file(\"model_tokenizer.json\").encode(encode_messages(m,\"thinking\"),add_special_tokens=False).ids))
PY"
````

````
init 117632 first 117694
rendered 29805
````

**[command]** exit=0

````
/bin/bash -lc "sed -n '518,586p;600,666p;710,810p;888,1010p' model_encoding.py"
````

````
tool_parameter_tag_name=tool_parameter_tag_name,
        thinking_start_token=thinking_start_token,
        thinking_end_token=thinking_end_token,
    )


def encode_arguments_to_dsml(tool_call: Dict[str, Any]) -> str:
    """Encode tool call arguments into V4.1 DSML parameter format."""
    p_dsml_template = (
        '<{dsml_token}{tool_parameter_tag_name} name="{key}" string="{is_str}">'
        '{value}</{dsml_token}{tool_parameter_tag_name}>'
    )
    P_dsml_strs = []

    arguments = tool_call["arguments"]
    if not isinstance(arguments, dict):
        # Tolerate JSON strings, including double-encoded ones.
        for _ in range(2):
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except Exception:
                    break
            else:
                break
        if not isinstance(arguments, dict):
            arguments = {"arguments": tool_call["arguments"]}

    for k, v in arguments.items():
        P_dsml_strs.append(p_dsml_template.format(
            dsml_token=dsml_token,
            tool_parameter_tag_name=tool_parameter_tag_name,
            key=k,
            is_str="true" if isinstance(v, str) else "false",
            value=v if isinstance(v, str) else to_json(v),
        ))

    return "\n".join(P_dsml_strs)


# ============================================================
# Message Rendering
# ============================================================

def find_last_user_index(messages: List[Dict[str, Any]]) -> int:
    """
    Find the index of the last user message.

    V4.1 supports mid-conversation system messages, which count as user
    messages for the purposes of the assistant generation header.
    User messages containing only tool results do not start a new turn.
    """
    last_user_index = -1
    for idx in range(len(messages) - 1, -1, -1):
        role = messages[idx].get("role")
        if role == "user" or (role == "system" and idx > 0):
            content_blocks = messages[idx].get("content_blocks")
            if content_blocks and not any(
                block.get("type") in ("text", "image", "image_url")
                for block in content_blocks
            ):
                continue
            last_user_index = idx
            break
    return last_user_index


def render_message(
    index: int,

    role = msg.get("role")
    content = msg.get("content")
    tools = msg.get("tools")
    response_format = msg.get("response_format")
    tool_calls = msg.get("tool_calls")
    reasoning_content = msg.get("reasoning_content")
    wo_eos = msg.get("wo_eos", False)

    if tools:
        tools = tools_from_openai_format(tools)
    if tool_calls:
        tool_calls = tool_calls_from_openai_format(tool_calls)

    # Reasoning effort prefix (thinking mode, index 0 only)
    reasoning_effort_prompt = render_reasoning_effort(index, thinking_mode, reasoning_effort)
    # System token leads the conversation when there is a reasoning effort prompt
    # or the first message is a system message.
    prompt = SYSTEM_SP_TOKEN if index == 0 and (reasoning_effort_prompt or role == "system") else ""
    prompt += reasoning_effort_prompt

    if role == "system":
        if index > 0:
            # Mid-conversation system message
            prompt += SYSTEM_SP_TOKEN
        prompt += system_msg_template.format(content=content or "")
        if tools:
            prompt += "\n\n" + render_tools(tools)
        if response_format:
            prompt += "\n\n" + response_format_template.format(schema=to_json(response_format))

    elif role == "user":
        prompt += USER_SP_TOKEN

        # Handle content blocks (tool results mixed with text)
        content_blocks = msg.get("content_blocks")
        if content_blocks:
            parts = []
            for block in content_blocks:
                block_type = block.get("type")
                if block_type == "text":
                    parts.append(bl
… [9542 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc "rg -A13 -n '"'^def to_json|''^def decode_dsml_to_arguments|''^def tool_calls_to_openai_format'"' model_encoding.py && sed -n '664,696p' model_encoding.py && rg -n 'def merge_tool_messages' model_encoding.py"
````

````
76:def to_json(value: Any) -> str:
77-    """Serialize a value to JSON string."""
78-    try:
79-        return json.dumps(value, ensure_ascii=False)
80-    except:
81-        return json.dumps(value, ensure_ascii=True)
82-
83-
84-def tools_from_openai_format(tools):
85-    """Extract function definitions with namespace-qualified names."""
86-    functions = []
87-    for tool in tools:
88-        function = dict(tool["function"])
89-        if tool.get("namespace") is not None:
--
139:def tool_calls_to_openai_format(tool_calls):
140-    """Convert internal tool calls to OpenAI format."""
141-    calls = []
142-    for tool_call in tool_calls:
143-        call = {
144-            "type": "function",
145-            "function": {
146-                "name": tool_call["name"],
147-                "arguments": tool_call["arguments"],
148-            }
149-        }
150-        if tool_call.get("namespace") is not None:
151-            call["namespace"] = tool_call["namespace"]
152-        calls.append(call)
--
156:def decode_dsml_to_arguments(tool_name: str, tool_args: Dict[str, Tuple[str, str]]) -> Dict[str, str]:
157-    """
158-    Decode DSML parameters back to a tool call dict.
159-
160-    Args:
161-        tool_name: Name of the tool.
162-        tool_args: Dict mapping param_name -> (value, is_string_flag).
163-
164-    Returns:
165-        Dict with "name", "arguments" (JSON string), and optional "namespace".
166-    """
167-    def _decode_value(key: str, value: str, string: str):
168-        if string == "true":
169-            value = to_json(value)

    elif role == "assistant":
        thinking_part = ""
        tc_content = ""

        if tool_calls:
            tc_list = [
                tool_call_template.format(
                    dsml_token=dsml_token,
                    tool_call_tag_name=tool_call_tag_name,
                    name=_tool_name_for_encoding(tc),
                    arguments=encode_arguments_to_dsml(tc)
                )
                for tc in tool_calls
            ]
            tc_content += '\n\n' + tool_calls_template.format(
                dsml_token=dsml_token,
                tool_calls="\n".join(tc_list),
                tc_block_name=tool_calls_block_name,
            )

        summary_content = content or ""
        rc = reasoning_content or ""

        # Check if previous message has a task - if so, this is a task output (no thinking)
        prev_has_task = index - 1 >= 0 and messages[index - 1].get("task") is not None

        if thinking_mode == "thinking" and not prev_has_task:
            if not drop_thinking or index > last_user_idx:
                thinking_part = thinking_template.format(reasoning_content=rc) + thinking_end_token
            else:
                thinking_part = ""

184:def merge_tool_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"httpx\",\"jsonschema\",\"pyyaml\",\"tokenizers\"]
# ///
import model_encoding as enc
from tokenizers import Tokenizer
from loola_agent import *
from loola_agent.compaction import context_bound
tok=Tokenizer.from_file(\"model_tokenizer.json\")
def n(s): return len(tok.encode(s,add_special_tokens=False).ids)
tool=DummyTool(\"x\",\"example\",{\"type\":\"object\",\"properties\":{\"ids\":{\"type\":\"array\",\"items\":{\"type\":\"integer\"}}}})
tools=Toolbox([tool]).schemas(); system=\"You are a helpful assistant. \"*30
e=[UserMessage(\"go\")]
def render(events):
    m=build_context(system,events);m[0][\"tools\"]=tools
    return enc.encode_messages(m,\"thinking\")
p=n(render(e))
args=\"[\"+\",\".join(\"0\" for _ in range(500))+\"]\"
d=enc.dsml_token
completion=f'</think>\\n\\n<{d} calls>\\n<{d} invoke name=\"x\">\\n<{d} parameter name=\"ids\" string=\"false\">{args}</{d} parameter>\\n</{d} invoke>\\n</{d} calls>'+enc.eos_token
msg=enc.parse_message_from_completion_text(completion,\"thinking\")
msg[\"tool_calls\"][0][\"id\"]=\"1\"
print(\"first\",p,\"bytes\",context_bound(system,e,tools),\"completion\",n(completion))
e+=[AssistantMessage(msg,\"tool_calls\",Usage(p,n(completion))),ToolResult(\"1\",\"x\",\"ok\")]
print(\"second bound\",context_bound(system,e,tools),\"rendered\",n(render(e)))
PY"
````

````
Installed 24 packages in 27ms
first 467 bytes 1149 completion 1038
second bound 1575 rendered 2016
````

**[agent]**

1. **High — F1 still undercounts the second request.** I reproduced this with DeepSeek V4.1 Flash’s published encoder. The first prompt measured 467 tokens against a byte estimate of 1,149, so calibration yielded **zero**. A valid tool call containing 500 integers took 1,038 generated tokens. When the encoder rendered that call back into history, it reserialized the array with spaces. After a two-character tool result, the harness bound was **1,575** and the rendered prompt was **2,016**. With a 2,800-token window and a 1,200-token reply allowance, the proposed check admits a request that exceeds the window by **416 tokens**. A fixed-preamble simulator misses this case. Use the measured **prompt** as the anchor and bound what the template replays for the assistant message. The first-request exception also relaxes brief v1’s guarantee and needs owner approval unless sizing is fixed there too. [compaction.py:69](<local path>), [brief.md:39](<local path>), [DeepSeek encoder](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/314113f8a7dadb388215396ba5fbee2c610a04d6/encoding/encoding.py)

2. **High — F5 can manufacture a baseline failure before turn one.** With the actual 91 direct tools, Bash, eager skills, and a short task, I measured a first-request byte bound of **117,694** against **29,805 rendered tokens**. The existing constructor rejects even the empty-history baseline at 64k. Bypassing that check and relying on a 400 has the opposite problem on an endpoint with a larger window. Both arms need the same effective 64k limit. Distinguish a conservative local rejection from an actual overflow, and reserve only the regular reply in the arm that cannot summarize. Capture ground truth **once per pinned task revision** and use it across all four runs for that task. [agent.py:36](<local path>), [compaction.py:50](<local path>), [brief.md:54](<local path>)

3. **High — F2 can turn a soft trigger into a failure and lose paid usage.** If the original context fits and the returned summary makes it exceed the window, the plan raises `CompactionError`. Discard that candidate and send the fitting original. Also, `(compaction, paid_usage)` returns nothing on exception. A paid invalid or oversized summary disappears from the failed-run total. A discarded summary held only in a local accumulator also disappears if a later request fails before `RunFinished`. Record summary usage when the response arrives, independently of whether the summary is applied, and verify the total from a failed run’s transcript. [agent.py:91](<local path>), [agent.py:99](<local path>), [cli.py:65](<local path>)

4. **Medium — F7 retains an explicit contract change.** Brief v1 requires rejection of unknown top-level arguments and rules out a per-tool exception. Keeping `additionalProperties: true` contradicts that decision even if the example catalog never exercises it. Normalize the effective top-level schema once, snapshot its nested data, and use it for validation, declaration, discovery, and error text. A free-form dictionary can still be a named argument. Preserving free-form *top-level* keys requires an owner-approved brief change. [tools.py:36](<local path>), [tools.py:64](<local path>), [brief.md:33](<local path>)

5. **Medium — The `gh` policy still sends infrastructure failures to the model.** A DNS or TLS failure matches neither the timeout nor the HTTP patterns. An exhausted account quota also persists across corrected queries. Return model-actionable errors such as an invalid query or a wrong resource identifier, and raise `GhUnavailable` for the remaining infrastructure failures. A fake `gh` that exits with a connection error is enough to test the distinction. [gh_proxy.py:228](<local path>), [brief.md:14](<local path>)

**not approved** — Remaining blockers are the replay-size bound and first-request guarantee, fair 64k benchmark enforcement, soft-trigger and failed-run accounting, the unapproved schema exception, and `gh` infrastructure-error routing.

---

## [input]

[bb message from thread:thr_…]

Round 3. The owner made two decisions on your round-2 points; they are now brief v2 (appended at the end of <local path> section "Revision v2"). Treat them as the contract, not as open issues:
1. Compaction sizing is explicitly practical (no strict guarantee, no tokenizer/template modelling); correctness = explicit errors when the server's own count shows the window was exceeded + documented assumptions.
2. Explicit additionalProperties:true is respected.

Implemented at commit 35180ff (diff vs 63a090c: `git diff 63a090c 35180ff -- src tests`; ignore README.md, it is updated separately after this loop). 170 tests pass; every change below was mutation-checked (removing it fails a test). One live run with a 40k window passed.
- F1: bound = last measured prompt + bytes(+16/msg) of everything after it, the last reply included (no completion-token anchor); first request not estimated; `_check_window` after every response raises CompactionError when prompt + max reply > window.
- F2/F3(r2): preflight with an empty summary; a returned summary is applied only if it is complete, shrinks the bound and fits; otherwise a SummaryDiscarded event (with usage) is yielded before anything is raised, so failed runs keep the cost in the transcript; raise only if the original context does not fit. Post-compaction bound = first request's measured prompt (system+tools+template) + bytes(user messages + summary) + (bound_before - prompt_at_cut).
- Baseline arm: CompactionPolicy(enabled=False) / CLI --no-compaction: reserve = reply only, no summary, CompactionError when the window would be exceeded; the first request is no longer pre-rejected by a byte estimate (direct 91 tools now start fine at 64k). Ground truth will be captured once per task and reused for all runs (benchmark phase).
- F3: finish_reason=length with tool calls -> no execution, NOT_EXECUTED result per call, RunFinished("truncated").
- F4: concurrent send() raises RuntimeError; flag released in finally.
- F6: build_context merges adjacent user messages (cancelled send, post-compaction head, summary request built as events[:cut] + UserMessage(instruction)).
- F7: declarations snapshotted (deep copy) in Toolbox.__init__.
- bash: executable=/bin/bash. tool_search: no limit knob, top 5 fixed.
- gh: only 4xx with an HTTP status (except 401/429/rate-limit) go to the model; no status (network/TLS), 401, 429, rate limit, 5xx, timeout raise GhUnavailable.

Critique hard; material unresolved issues only. End with: fully approved / not approved + remaining blockers only.

**[agent]**

I’ll check `35180ff` against the exact v2 wording, then trace failed responses, discarded summaries, and interrupted runs through the event log. I’ll use an isolated copy so the README work stays untouched.

**[command]** exit=0

````
/bin/bash -lc 'tail -26 <local path>'
````

````
7. **Deferred-тул можно вызвать и напрямую по имени** — следствие одного реестра для диспатча; совпадает с нативными API (Anthropic tool_reference, OpenAI tool_search). Основной путь — `tool_call`.
8. **BM25 свой (~15 строк)**: зависимость (rank-bm25/bm25s) тянет numpy ради 91 документа и прячет механику.
9. **Каталог тулов** — список из GitHub MCP server v2.2.0 (91 тул, MIT) **только как данные** (имя/описание/схема). MCP-протокол не подключаем — за рамками. Исполнение: `DummyTool` для детерминированных тестов; `gh_proxy` (14 read-only тулов через `gh api`) — только для живых прогонов, внутренняя тестовая обвязка, пока остаётся в пакете.
10. **Прерванные tool calls** (отмена посреди тула): в начале следующего `send()` каждому незакрытому вызову — синтетический результат «interrupted, may have partial side effects, check state and re-run if needed». Не перезапуск (повтор побочных эффектов) и не удаление (ложь модели).
11. **Скиллы** (Agent Skills): в system prompt только каталог (name/description/path), тело модель читает `bash cat`. `--skills-mode eager` — baseline для замера. Невалидный SKILL.md — ошибка старта.
12. **Компакшен** (`compaction.py`): гарантия без процентов. Верхняя граница размера следующего запроса = точные `usage` сервера для измеренного + UTF-8 байты для неизмеренного (допущение: токен ≥ 1 байт, верно для BPE). Обычный запрос шлём, только если остаётся резерв под будущий summary-запрос; `compact_at` — лишь опциональный более ранний триггер. Summary-запрос = точный контекст ранее отправленного измеренного запроса + инструкция → влезает по построению и попадает в KV-cache. User-сообщения остаются дословно (склеены с summary в одно user-сообщение — строгие шаблоны не любят два user подряд). Срез только по границе запроса (все tool calls отвечены). Если сжатие не может уменьшить контекст — пропуск (если влезает) или явная ошибка. Стоимость summary входит в usage прогона.
13. **Summary-запрос с тем же `tool_choice: auto`**, а не `none`: проверено живьём — OpenCode Go при `none` выкидывает tools из промпта → другой префикс, cached=0; с `auto` cached 8704/8776. Если модель вызовет тул вместо summary → явная ошибка.
14. **Модель**: gpt-6-luna отпала (в chat completions tools работают только с `reasoning_effort=none`); используем `deepseek-v4.1-flash` через OpenCode Go (требует `x-opencode-session` и свой User-Agent).
15. **System prompt**: правило «предпочитай выделенный тул shell-эквиваленту; если нет подходящего — сначала tool_search». Реализацию bash ради тестового тулсета не меняем (модель однажды обошла GitHub-тулы через `gh api`).

## Сознательно не делаем (out of scope)

MCP-клиент; strict/guided decoding; Responses API; streaming; resume сессии (JSONL-транскрипт пишется, но не загружается); approval/sandbox (запуск в контейнере — ответственность оператора); TUI/web оболочки; отдельные тулы для фоновых процессов; общий лимит вывода в Toolbox (каждый тул режет сам); tiktoken (берём usage сервера); микро-компакшен (вычистка старых tool outputs без LLM).

## Живые наблюдения

5 живых прогонов на реальном GitHub (encode/httpx): deferred-поиск и вызов работают; скилл review прочитан и выполнен, write-шаг честно получил «not implemented»; модель исправила аргумент после ошибки валидации; компакшен срабатывал 1–2 раза с кешем summary ~97%. Граница для свежих tool outputs пессимистична в ~3–4× (байты vs токены): с искусственно маленьким окном 40k прогон один раз упал явной ошибкой — по дизайну.

## Что ещё впереди

Замеры (2 задачи × до/после × 2 повтора, окно 64k): «до» = все 91 тул direct + eager skills + без компакшена; «после» = deferred + lazy + компакшен. README, AGENTS.md, лог сессии.

## Revision v2 (approved by the owner after review round 2)

- **Decision 12 amended — compaction sizing is practical, not a strict guarantee.** Owner: "строгую гарантию без токенизатора всё равно нормально не сделать — делаем самый простой вариант, который нормально работает на практике, с корректной обработкой ошибок, и пропи
… [539 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc "git -C ~/projects/loola-test-task diff --stat 63a090c 35180ff -- src tests && git -C ~/projects/loola-test-task rev-parse '35180ff"'^{commit}'"'"
````

````
src/loola_agent/__init__.py   |   6 +--
 src/loola_agent/agent.py      | 107 +++++++++++++++++++++++++-----------------
 src/loola_agent/bash.py       |   2 +-
 src/loola_agent/cli.py        |  14 ++++--
 src/loola_agent/compaction.py |  73 ++++++++++++++--------------
 src/loola_agent/events.py     |  34 ++++++++++----
 src/loola_agent/gh_proxy.py   |  18 ++++---
 src/loola_agent/tools.py      |  17 ++++---
 tests/test_agent.py           |  40 ++++++++++++++++
 tests/test_compaction.py      |  70 ++++++++++++++++++++-------
 tests/test_deferred.py        |   7 +++
 tests/test_gh_proxy.py        |  12 ++++-
 tests/test_tools.py           |  11 +++++
 13 files changed, 281 insertions(+), 130 deletions(-)
35180ff8a71c9717bc2fb62d56f5b77090d16a1a
````

**[command]** exit=0

````
/bin/bash -lc 'p=$(mktemp -d /tmp/loola-r3.XXXXXXXX) && git -C ~/projects/loola-test-task archive 35180ff | tar -xf - -C "$p" && realpath "$p"'
````

````
/tmp/loola-r3.1NDzQ2Zx
````

**[command]** exit=0

````
/bin/bash -lc 'git -C ~/projects/loola-test-task diff 63a090c 35180ff -- src/loola_agent/{tools,gh_proxy}.py tests/test_gh_proxy.py'
````

````
diff --git a/src/loola_agent/gh_proxy.py b/src/loola_agent/gh_proxy.py
index c3e4b1a..ff20d9b 100644
--- a/src/loola_agent/gh_proxy.py
+++ b/src/loola_agent/gh_proxy.py
@@ -5,7 +5,7 @@ Each proxied tool turns its (already schema-validated) arguments into one `gh ap
 The arguments a mapping supports are its Python parameters; anything else the schema allows is reported
 to the model as not implemented instead of being silently ignored. Other catalog tools answer with an error.
 gh authenticates itself: the token never passes through this process."""
-import asyncio, inspect, json, subprocess
+import asyncio, inspect, json, re, subprocess
 from collections.abc import Callable, Sequence
 from dataclasses import dataclass
 from urllib.parse import quote, urlencode
@@ -210,8 +210,9 @@ class GhUnavailable(Exception):
 
 @dataclass(frozen=True)
 class Gh:
-    """Runs `gh` without stdin, with a timeout and bounded output. gh failures (404, rate limit, bad query)
-    come back as text for the model; only a missing or logged-out gh is fatal, checked once by `check`."""
+    """Runs `gh` without stdin, with a timeout and bounded output. Errors the model can act on (a 4xx about its
+    request: wrong repo, number, query) come back as text; infrastructure failures (no HTTP status: network, TLS;
+    401; rate limits; 5xx; timeouts) raise GhUnavailable, which ends the run at the CLI boundary."""
     executable: str = "gh"
     timeout: float = 30
     max_output: int = 20_000
@@ -229,10 +230,13 @@ class Gh:
         try:
             code, out, err = await self._exec(argv)
         except TimeoutError:
-            return f"Error: gh timed out after {self.timeout:g}s"
-        if code != 0:
-            return truncate(f"Error: gh exited with code {code}: {err.strip()}\n{out}".rstrip(), self.max_output)
-        return truncate(out, self.max_output)
+            raise GhUnavailable(f"gh timed out after {self.timeout:g}s") from None
+        if code == 0:
+            return truncate(out, self.max_output)
+        status = re.search(r"\(HTTP (\d{3})\)", err)
+        if status is None or int(status[1]) in (401, 429) or int(status[1]) >= 500 or "rate limit" in err.lower():
+            raise GhUnavailable(f"gh failed (exit {code}): {err.strip()[:500]}")
+        return truncate(f"Error: gh exited with code {code}: {err.strip()}\n{out}".rstrip(), self.max_output)
 
     async def _exec(self, argv: Argv) -> tuple[int, str, str]:
         proc = await asyncio.create_subprocess_exec(self.executable, *argv, stdin=subprocess.DEVNULL,
diff --git a/src/loola_agent/tools.py b/src/loola_agent/tools.py
index 5f0f769..4ed14f4 100644
--- a/src/loola_agent/tools.py
+++ b/src/loola_agent/tools.py
@@ -32,10 +32,13 @@ class Toolbox:
             raise ValueError("Duplicate tool names")
         self._validators = {name: _validator(tool.parameters) for name, tool in self._tools.items()}
         self._has_deferred = bool(deferred)
+        # Snapshot: the declared tools are the start of the cached prompt prefix and must not change in a session.
+        self._schemas = json.loads(json.dumps([
+            {"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.parameters}}
+            for t in self._declared]))
 
     def schemas(self) -> list[dict]:
-        return [{"type": "function", "function": {"name": t.name, "description": t.description,
-                                                  "parameters": t.parameters}} for t in self._declared]
+        return self._schemas
 
     async def call(self, name: str, raw_arguments: str) -> str:
         try:
@@ -64,23 +67,25 @@ def _validator(schema: dict) -> Draft202012Validator:
     return Draft202012Validator({"additionalProperties": False, **schema})
 
 
+SEARCH_RESULTS = 5
+
+
 class ToolSearch:
     name = "tool_search"
     parameters = {"type": "object",
-                  "properties": {"query": {"type": "string", "description": "Keywords describing the act
… [2589 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba src/loola_agent/agent.py && nl -ba src/loola_agent/compaction.py'
````

````
1	"""Agent loop: streams events, keeps the session as an append-only event list (see events.py)."""
     2	from collections.abc import AsyncIterator
     3	from dataclasses import replace
     4	
     5	from .compaction import (CompactionError, CompactionPolicy, bound_after_compaction, choose_cut, context_bound,
     6	                         summary_request)
     7	from .events import (INTERRUPTED, NOT_EXECUTED, AssistantMessage, Compaction, Event, RunFinished, SummaryDiscarded,
     8	                     ToolResult, ToolStarted, UserMessage, build_context, unanswered_tool_calls)
     9	from .llm import LLM, Completion, Usage
    10	from .tools import Toolbox
    11	
    12	SYSTEM_PROMPT = """\
    13	You are a coding agent. Your job is to help the user with programming tasks.
    14	
    15	Workflow:
    16	1. Plan what needs to be done.
    17	2. Use the tools to read files, run commands, write code, etc.
    18	3. After gathering enough information or completing the task, give your final answer in natural language.
    19	4. To finish, reply with a regular message (no tool call).
    20	
    21	Prefer a dedicated tool over a shell command for the same action (e.g. a GitHub tool over `gh` or `curl`). \
    22	If no listed tool fits and `tool_search` is available, search for one first; use bash only when nothing fits.
    23	
    24	Be concise. Explain what you're doing before each command."""
    25	
    26	
    27	class Agent:
    28	    """One conversation. `send` runs the loop for a user message and streams events;
    29	    the caller (CLI, TUI, web) decides how to render and persist them. One `send` at a time."""
    30	
    31	    def __init__(self, llm: LLM, toolbox: Toolbox, system_prompt: str = SYSTEM_PROMPT, max_turns: int = 1000,
    32	                 compaction: CompactionPolicy | None = None):
    33	        self.llm, self.toolbox, self.system_prompt, self.max_turns = llm, toolbox, system_prompt, max_turns
    34	        self.compaction = compaction
    35	        self.events: list[Event] = []
    36	        self._sending = False
    37	
    38	    async def send(self, content: str) -> AsyncIterator[Event]:
    39	        if self._sending:
    40	            raise RuntimeError("send() is already running for this conversation")
    41	        self._sending = True
    42	        try:
    43	            async for event in self._run(content):
    44	                yield event
    45	        finally:
    46	            self._sending = False
    47	
    48	    async def _run(self, content: str) -> AsyncIterator[Event]:
    49	        # Close calls left open by a cancelled run: the protocol requires a result for every call, and the
    50	        # model must know the command may have partially run. Re-running or dropping them silently would lie.
    51	        for call in unanswered_tool_calls(self.events):
    52	            yield self._append(ToolResult(call["id"], call["function"]["name"], INTERRUPTED))
    53	        yield self._append(UserMessage(content))
    54	        usage = Usage()
    55	        for turn in range(1, self.max_turns + 1):
    56	            if self.compaction:
    57	                async for event in self._compact(self.compaction):
    58	                    usage += event.usage
    59	                    yield event
    60	            completion = await self.llm.complete(build_context(self.system_prompt, self.events),
    61	                                                 self.toolbox.schemas())
    62	            usage += completion.usage
    63	            yield self._append(AssistantMessage(completion.message, completion.finish_reason, completion.usage))
    64	            self._check_window(completion)
    65	            text = completion.message.get("content") or ""
    66	            tool_calls = completion.message.get("tool_calls") or []
    67	            if completion.finish_reason == "length":  # a cut-off reply may hold a partial batch: run none of it
    68	             
… [11168 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba src/loola_agent/events.py && nl -ba src/loola_agent/cli.py'
````

````
1	"""Session events. The session is an append-only list of them; the LLM context is a pure projection of it."""
     2	from dataclasses import dataclass
     3	from typing import Literal
     4	
     5	from .llm import Usage
     6	
     7	INTERRUPTED = ("Error: this tool call was interrupted before it finished; it may have had partial side effects. "
     8	               "Check the current state and re-run it if it is still needed.")
     9	NOT_EXECUTED = "Error: not executed: your reply was cut off by the token limit. Issue the call again if needed."
    10	SUMMARY_HEADER = "[Earlier work in this conversation was compacted. Summary of it:]\n"
    11	
    12	
    13	@dataclass(frozen=True)
    14	class UserMessage:
    15	    content: str
    16	
    17	
    18	@dataclass(frozen=True)
    19	class AssistantMessage:
    20	    message: dict  # as returned by the LLM: parallel tool calls and reasoning fields stay intact
    21	    finish_reason: str | None
    22	    usage: Usage  # usage.prompt is the exact size of the context this message was generated from
    23	
    24	
    25	@dataclass(frozen=True)
    26	class ToolStarted:
    27	    tool_call_id: str
    28	    name: str
    29	    arguments: str
    30	
    31	
    32	@dataclass(frozen=True)
    33	class ToolResult:
    34	    tool_call_id: str
    35	    name: str
    36	    content: str
    37	
    38	
    39	@dataclass(frozen=True)
    40	class Compaction:
    41	    summary: str
    42	    cut: int  # index of the first event kept verbatim (always an AssistantMessage)
    43	    tokens_before: int  # upper bound of the context that triggered compaction
    44	    tokens_after: int  # upper bound of the context right after it
    45	    usage: Usage  # of the summary request
    46	
    47	
    48	@dataclass(frozen=True)
    49	class SummaryDiscarded:
    50	    reason: str
    51	    usage: Usage  # a paid summary request whose result was not applied
    52	
    53	
    54	@dataclass(frozen=True)
    55	class RunFinished:
    56	    status: Literal["done", "truncated", "empty_reply", "max_turns"]
    57	    answer: str
    58	    turns: int
    59	    usage: Usage  # of this run only, summary requests included
    60	
    61	
    62	Event = UserMessage | AssistantMessage | ToolStarted | ToolResult | Compaction | SummaryDiscarded | RunFinished
    63	
    64	
    65	def to_message(event: Event) -> dict | None:
    66	    match event:
    67	        case UserMessage(content):
    68	            return {"role": "user", "content": content}
    69	        case AssistantMessage(message):
    70	            return message
    71	        case ToolResult(tool_call_id, _, content):
    72	            return {"role": "tool", "tool_call_id": tool_call_id, "content": content}
    73	    return None
    74	
    75	
    76	def build_context(system_prompt: str, events: list[Event]) -> list[dict]:
    77	    """System prompt, then either all events, or after a compaction: the user's own messages verbatim plus the
    78	    latest summary (it already covers earlier ones), followed by the events kept verbatim. Adjacent user messages
    79	    are merged into one: strict chat templates reject two user turns in a row (e.g. after a cancelled send)."""
    80	    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    81	    start = 0
    82	    compactions = [e for e in events if isinstance(e, Compaction)]
    83	    if compactions:
    84	        last = compactions[-1]
    85	        for event in events[:last.cut]:
    86	            if isinstance(event, UserMessage):
    87	                _add(messages, {"role": "user", "content": event.content})
    88	        _add(messages, {"role": "user", "content": SUMMARY_HEADER + last.summary})
    89	        start = last.cut
    90	    for event in events[start:]:
    91	        if (message := to_message(event)) is not None:
    92	            _add(messages, message)
    93	    return messages
    94	
    95	
    96	def 
… [7643 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc "nl -ba src/loola_agent/gh_proxy.py | sed -n '78,112p;215,241p' && nl -ba src/loola_agent/tools.py | sed -n '24,70p'"
````

````
78	
    79	_ISSUE_FIELDS = {"number": "number", "title": "title", "body": "body", "state": "state", "user": "author { login }",
    80	                 "labels": "labels(first: 20) { nodes { name } }", "assignees": "assignees(first: 10) { nodes { login } }",
    81	                 "comments": "comments { totalCount }", "created_at": "createdAt", "updated_at": "updatedAt"}
    82	_LIST_ISSUES = """\
    83	query($owner: String!, $repo: String!, $first: Int!, $after: String, $states: [IssueState!], $labels: [String!],
    84	      $orderBy: IssueOrder, $since: DateTime) {
    85	  repository(owner: $owner, name: $repo) {
    86	    issues(first: $first, after: $after, states: $states, labels: $labels, orderBy: $orderBy,
    87	           filterBy: {since: $since}) {
    88	      totalCount pageInfo { hasNextPage endCursor } nodes { %s }
    89	    }
    90	  }
    91	}"""
    92	
    93	
    94	def list_issues(owner: str, repo: str, state: str | None = None, labels: list[str] | None = None,
    95	                orderBy: str | None = None, direction: str | None = None, since: str | None = None,
    96	                after: str | None = None, perPage: float | None = None,
    97	                fields: list[str] | None = None) -> Argv | Unsupported:
    98	    # GraphQL like the original server: REST would mix in pull requests and has no `after` cursor.
    99	    if (orderBy is None) != (direction is None):
   100	        return Unsupported("list_issues needs orderBy and direction together")
   101	    if fields and "field_values" in fields:
   102	        return Unsupported("field 'field_values' of list_issues is not implemented in the gh backend")
   103	    selection = " ".join(_ISSUE_FIELDS[f] for f in fields or _ISSUE_FIELDS)
   104	    # -f passes values verbatim; -F would read a file for a value starting with "@", so it gets only our integer.
   105	    strings = [("owner", owner), ("repo", repo), ("after", after), ("since", since), ("states[]", state),
   106	               ("orderBy[field]", orderBy), ("orderBy[direction]", direction),
   107	               *(("labels[]", label) for label in labels or ())]
   108	    return ["api", "graphql", "-f", f"query={_LIST_ISSUES % selection}", "-F", f"first={int(perPage or 30)}",
   109	            *(arg for key, value in strings if value is not None for arg in ("-f", f"{key}={value}")),
   110	            "--jq", ".data.repository.issues"]
   111	
   112	
   215	    401; rate limits; 5xx; timeouts) raise GhUnavailable, which ends the run at the CLI boundary."""
   216	    executable: str = "gh"
   217	    timeout: float = 30
   218	    max_output: int = 20_000
   219	
   220	    async def check(self) -> None:
   221	        try:
   222	            code, _, err = await self._exec(["auth", "status", "--hostname", "github.com"])
   223	        except FileNotFoundError:
   224	            raise GhUnavailable(
   225	                f"'{self.executable}' not found: install the GitHub CLI (https://cli.github.com)") from None
   226	        if code != 0:
   227	            raise GhUnavailable(f"gh is not logged in to github.com (run `gh auth login`): {err.strip()}")
   228	
   229	    async def run(self, argv: Argv) -> str:
   230	        try:
   231	            code, out, err = await self._exec(argv)
   232	        except TimeoutError:
   233	            raise GhUnavailable(f"gh timed out after {self.timeout:g}s") from None
   234	        if code == 0:
   235	            return truncate(out, self.max_output)
   236	        status = re.search(r"\(HTTP (\d{3})\)", err)
   237	        if status is None or int(status[1]) in (401, 429) or int(status[1]) >= 500 or "rate limit" in err.lower():
   238	            raise GhUnavailable(f"gh failed (exit {code}): {err.strip()[:500]}")
   239	        return truncate(f"Error: gh exited with code {code}: {err.strip()}\n{out}".rstrip(), self.max_output)
   240	
   241	    async def _exec(self, argv: Argv) -> tuple[int, str, str]:
    24	class Too
… [2808 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'nl -ba tests/test_compaction.py'
````

````
1	"""Compaction: every request (summary requests included) stays within the window, whatever the threshold."""
     2	import json
     3	
     4	import pytest
     5	
     6	from loola_agent import (Agent, AssistantMessage, Compaction, CompactionError, CompactionPolicy, Completion,
     7	                         SummaryDiscarded, Toolbox, Usage, UserMessage, build_context)
     8	from loola_agent.compaction import SUMMARY_INSTRUCTION, context_bound
     9	from loola_agent.events import SUMMARY_HEADER
    10	
    11	
    12	class Big:
    13	    name, description = "big", "Returns a large output."
    14	    parameters = {"type": "object", "properties": {}}
    15	
    16	    def __init__(self, size=3000):
    17	        self.size = size
    18	
    19	    async def run(self, args):
    20	        return "x" * self.size
    21	
    22	
    23	class SimulatedLLM:
    24	    """A server stand-in: counts `bytes_per_token` bytes as one token (1 is the worst case the bound allows),
    25	    rejects any request that would overflow the window, makes `turns` tool calls and then answers;
    26	    summary requests (ending with the summary instruction) get a summary. Completion counts are the real message sizes."""
    27	
    28	    def __init__(self, window, turns, max_tokens=500, summary=None, bytes_per_token=3):
    29	        self.window, self.turns, self.max_tokens, self.bpt = window, turns, max_tokens, bytes_per_token
    30	        self.summary = summary or Completion({"role": "assistant", "content": "SUMMARY " + "s" * 300}, "stop",
    31	                                             Usage(0, 0))
    32	        self.requests: list[dict] = []
    33	
    34	    def tokens(self, value) -> int:
    35	        return len(json.dumps(value).encode()) // self.bpt + 1
    36	
    37	    async def complete(self, messages, tools, *, max_tokens=None):
    38	        prompt = self.tokens([messages, tools])
    39	        assert prompt + (max_tokens or self.max_tokens) <= self.window, f"overflow: {prompt} prompt tokens"
    40	        is_summary = messages[-1]["role"] == "user" and messages[-1]["content"].endswith(SUMMARY_INSTRUCTION)
    41	        self.requests.append({"messages": messages, "tools": tools, "summary": is_summary, "prompt": prompt})
    42	        if is_summary:
    43	            message, finish = self.summary.message, self.summary.finish_reason
    44	        elif (turn := sum(not r["summary"] for r in self.requests)) <= self.turns:
    45	            call = {"id": f"c{turn}", "type": "function", "function": {"name": "big", "arguments": "{}"}}
    46	            message, finish = {"role": "assistant", "content": f"step {turn}", "tool_calls": [call]}, "tool_calls"
    47	        else:
    48	            message, finish = {"role": "assistant", "content": "all done"}, "stop"
    49	        return Completion(message, finish, Usage(prompt, self.tokens(message)))
    50	
    51	
    52	async def run(agent, task="long task"):
    53	    return [e async for e in agent.send(task)]
    54	
    55	
    56	@pytest.mark.parametrize("bytes_per_token", [1, 3])
    57	@pytest.mark.parametrize("keep_recent", [0, 3_000])
    58	@pytest.mark.parametrize("output_size", [800, 4_000])
    59	@pytest.mark.parametrize("compact_at", [None, 4_000, 12_000, 19_999, 10**9])
    60	async def test_requests_never_overflow_whatever_the_threshold(compact_at, output_size, keep_recent, bytes_per_token):
    61	    llm = SimulatedLLM(window=20_000, turns=40, bytes_per_token=bytes_per_token)
    62	    policy = CompactionPolicy(20_000, compact_at, keep_recent_tokens=keep_recent, summary_max_tokens=1_000)
    63	    events = await run(Agent(llm, Toolbox([Big(output_size)]), compaction=policy))
    64	    assert events[-1].status == "done"
    65	    compactions = [e for e in events if isinstance(e, Compaction)]
    66	    if 40 * output_size // bytes_per_token > 20_000:  # the outputs alone exceed the window
    67	        assert compactions
    68	    asser
… [6868 more characters truncated]
````

**[command]** exit=0

````
/bin/bash -lc 'git -C ~/projects/loola-test-task diff 63a090c 35180ff -- tests/test_agent.py tests/test_deferred.py tests/test_tools.py && command -v gh && gh --version'
````

````
diff --git a/tests/test_agent.py b/tests/test_agent.py
index 71799d2..150feb0 100644
--- a/tests/test_agent.py
+++ b/tests/test_agent.py
@@ -129,3 +129,43 @@ async def test_cancelled_tool_call_is_closed_as_interrupted_on_next_send():
     assert [m["tool_call_id"] for m in context[3:5]] == ["h", "a"]
     assert all(m["content"] == INTERRUPTED for m in context[3:5])
     assert unanswered_tool_calls(agent.events) == []
+
+
+async def test_tool_calls_in_a_truncated_reply_are_not_executed():
+    executed = []
+
+    class Spy(Echo):
+        async def run(self, args):
+            executed.append(args)
+            return "ran"
+
+    llm = FakeLLM(reply("partial", [call("a", "x")], "length"), reply("ok"))
+    agent = Agent(llm, Toolbox([Spy()]))
+    _, events = await run(llm, agent=agent)
+    assert executed == [] and events[-1].status == "truncated"
+    _, events = await run(llm, "continue", agent)  # history stays valid: the call got a result
+    assert [m["role"] for m in llm.calls[1]] == ["system", "user", "assistant", "tool", "user"]
+    assert llm.calls[1][3]["content"].startswith("Error: not executed")
+
+
+async def test_a_second_concurrent_send_is_rejected():
+    hang = {"id": "h", "type": "function", "function": {"name": "hang", "arguments": "{}"}}
+    agent = Agent(FakeLLM(reply(None, [hang], "tool_calls")), Toolbox([Echo(), Hang()]))
+    first = agent.send("one")
+    async for event in first:
+        if isinstance(event, ToolStarted):
+            break
+    with pytest.raises(RuntimeError, match="already running"):
+        await anext(agent.send("two"))
+    await first.aclose()
+    assert not agent._sending
+
+
+async def test_a_send_cancelled_before_the_reply_leaves_no_two_user_turns_in_a_row():
+    llm = FakeLLM(reply("ok"))
+    agent = Agent(llm, Toolbox([Echo()]))
+    first = agent.send("one")
+    await anext(first)  # UserMessage recorded, then abandoned
+    await first.aclose()
+    await run(llm, "two", agent)
+    assert llm.calls[0][1:] == [{"role": "user", "content": "one\n\ntwo"}]
diff --git a/tests/test_deferred.py b/tests/test_deferred.py
index 97459c8..0ad6e4b 100644
--- a/tests/test_deferred.py
+++ b/tests/test_deferred.py
@@ -102,3 +102,10 @@ async def test_agent_discovers_and_calls_a_deferred_tool_with_a_stable_tool_list
     assert llm.tools[0] == llm.tools[1] == llm.tools[2]  # declared tools never change -> prefix cache stays valid
     assert '"issue_read"' in llm.contexts[1][-1]["content"]  # the schema arrived as a tool result
     assert json.loads(llm.contexts[2][-1]["content"])["arguments"]["issue_number"] == 7
+
+
+async def test_search_returns_at_most_five_tools_and_has_no_limit_knob():
+    tools, hint = load_catalog(CATALOG)
+    toolbox = Toolbox([Direct()], deferred=tools, deferred_hint=hint)
+    assert len(json.loads(await toolbox.call("tool_search", '{"query": "repository"}'))) == 5
+    assert "'limit' was unexpected" in await toolbox.call("tool_search", '{"query": "repository", "limit": -1}')
diff --git a/tests/test_tools.py b/tests/test_tools.py
index 16ee299..7cb2bd0 100644
--- a/tests/test_tools.py
+++ b/tests/test_tools.py
@@ -101,3 +101,14 @@ async def test_cancelled_command_kills_its_process_group(bash, tmp_path):
         await task
     await asyncio.sleep(0.8)
     assert not marker.exists()
+
+
+async def test_commands_run_in_bash(bash):
+    assert (await run(bash, "set -o pipefail; false | true; echo $?")).endswith("1\n")
+
+
+def test_declared_tools_are_a_snapshot(bash):
+    toolbox = Toolbox([bash])
+    before = toolbox.schemas()
+    bash.description = "changed at runtime"
+    assert toolbox.schemas() == before and "changed" not in json.dumps(toolbox.schemas())
/usr/bin/gh
gh version 2.45.0 (2025-07-18 Ubuntu 2.45.0-1ubuntu0.3)
https://github.com/cli/cli/releases/tag/v2.45.0
````

**[command]** exit=0

````
/bin/bash -lc 'UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run --frozen pytest -q'
````

````
Using CPython 3.13.17
Creating virtual environment at: .venv
   Building loola-agent @ file:///tmp/loola-r3.1NDzQ2Zx
      Built loola-agent @ file:///tmp/loola-r3.1NDzQ2Zx
Installed 20 packages in 54ms
........................................................................ [ 42%]
........................................................................ [ 84%]
..........................                                               [100%]
170 passed, 1 deselected in 9.50s
````

**[command]** exit=0

````
/bin/bash -lc "curl -fsSL 'https://raw.githubusercontent.com/cli/cli/v2.45.0/pkg/cmd/api/api.go' | rg -n -C 3 'HTTP %d|\\.Errors|GraphQL|serverError|extractError' | tail -120"
````

````
146-			$ gh api graphql -F owner='{owner}' -F name='{repo}' -f query='
147-			  query($name: String!, $owner: String!) {
148-			    repository(owner: $owner, name: $name) {
--
249-		return err
250-	}
251-
252:	isGraphQL := opts.RequestPath == "graphql"
253-	requestPath, err := fillPlaceholders(opts.RequestPath, opts)
254-	if err != nil {
255-		return fmt.Errorf("unable to expand placeholder in path: %w", err)
--
265-		method = "POST"
266-	}
267-
268:	if opts.Paginate && !isGraphQL {
269-		requestPath = addPerPage(requestPath, 100, params)
270-	}
271-
--
353-			return err
354-		}
355-
356:		if !isGraphQL {
357-			requestPath, hasNextPage = findNextPage(resp)
358-			requestBody = nil // prevent repeating GET parameters
359-		}
--
368-			break
369-		}
370-
371:		if isGraphQL {
372-			hasNextPage = endCursor != ""
373-			if hasNextPage {
374-				params["endCursor"] = endCursor
--
398-
399-	isJSON, _ := regexp.MatchString(`[/+]json(;|$)`, resp.Header.Get("Content-Type"))
400-
401:	var serverError string
402-	if isJSON && (opts.RequestPath == "graphql" || resp.StatusCode >= 400) {
403:		responseBody, serverError, err = parseErrorResponse(responseBody, resp.StatusCode)
404-		if err != nil {
405-			return
406-		}
407-	}
408-
409-	var bodyCopy *bytes.Buffer
410:	isGraphQLPaginate := isJSON && resp.StatusCode == 200 && opts.Paginate && opts.RequestPath == "graphql"
411:	if isGraphQLPaginate {
412-		bodyCopy = &bytes.Buffer{}
413-		responseBody = io.TeeReader(responseBody, bodyCopy)
414-	}
415-
416:	if opts.FilterOutput != "" && serverError == "" {
417-		// TODO: reuse parsed query across pagination invocations
418-		indent := ""
419-		if opts.IO.IsStdoutTTY() {
--
423-		if err != nil {
424-			return
425-		}
426:	} else if opts.Template != "" && serverError == "" {
427-		err = template.Execute(responseBody)
428-		if err != nil {
429-			return
--
431-	} else if isJSON && opts.IO.ColorEnabled() {
432-		err = jsoncolor.Write(bodyWriter, responseBody, "  ")
433-	} else {
434:		if isJSON && opts.Paginate && !isGraphQLPaginate && !opts.ShowResponseHeaders {
435-			responseBody = &paginatedArrayReader{
436-				Reader:      responseBody,
437-				isFirstPage: isFirstPage,
--
444-		return
445-	}
446-
447:	if serverError == "" && resp.StatusCode > 299 {
448:		serverError = fmt.Sprintf("HTTP %d", resp.StatusCode)
449-	}
450:	if serverError != "" {
451:		fmt.Fprintf(opts.IO.ErrOut, "gh: %s\n", serverError)
452-		if msg := api.ScopesSuggestion(resp); msg != "" {
453-			fmt.Fprintf(opts.IO.ErrOut, "gh: %s\n", msg)
454-		}
--
459-		return
460-	}
461-
462:	if isGraphQLPaginate {
463-		endCursor = findEndCursor(bodyCopy)
464-	}
465-
--
562-		return bodyCopy, "", err
563-	}
564-
565:	if len(parsedBody.Errors) > 0 && parsedBody.Errors[0] == '"' {
566-		var stringError string
567:		if err := json.Unmarshal(parsedBody.Errors, &stringError); err != nil {
568-			return bodyCopy, "", err
569-		}
570-		if stringError != "" {
--
576-	}
577-
578-	if parsedBody.Message != "" {
579:		return bodyCopy, fmt.Sprintf("%s (HTTP %d)", parsedBody.Message, statusCode), nil
580-	}
581-
582:	if len(parsedBody.Errors) == 0 || parsedBody.Errors[0] != '[' {
583-		return bodyCopy, "", nil
584-	}
585-
586-	var errorObjects []json.RawMessage
587:	if err := json.Unmarshal(parsedBody.Errors, &errorObjects); err != nil {
588-		return bodyCopy, "", err
589-	}
590-
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"pytest\",\"httpx\",\"jsonschema\",\"pyyaml\"]
# ///
import asyncio
from loola_agent import Agent, Toolbox, CompactionPolicy, CompactionError, Usage, Completion, Compaction, SummaryDiscarded, build_context
from loola_agent.compaction import bound_after_compaction, context_bound, choose_cut
from tests.test_compaction import SimulatedLLM, Big, run
class ReportOversizeSummary(SimulatedLLM):
    async def complete(self,messages,tools,*,max_tokens=None):
        c=await super().complete(messages,tools,max_tokens=max_tokens)
        if self.requests[-1][\"summary\"]:
            return Completion(c.message,c.finish_reason,Usage(19500,c.usage.completion))
        return c
async def main():
    llm=ReportOversizeSummary(20000,10)
    a=Agent(llm,Toolbox([Big()]),compaction=CompactionPolicy(20000,8000,3000,1000))
    e=await run(a)
    print(\"accepted over-limit summaries\", [(x.usage.prompt,x.usage.completion) for x in e if isinstance(x,Compaction)],\"status\",e[-1].status)
    llm=SimulatedLLM(20000,6,summary=Completion({\"role\":\"assistant\",\"content\":None,\"tool_calls\":[{\"id\":\"x\",\"type\":\"function\",\"function\":{\"name\":\"big\",\"arguments\":\"{}\"}}]},\"tool_calls\",Usage()))
    e=await run(Agent(llm,Toolbox([Big()]),compaction=CompactionPolicy(20000,6000,0,1000)))
    print(\"unexpected summary calls\",[(x.reason) for x in e if isinstance(x,SummaryDiscarded)],\"status\",e[-1].status)
    for size in [8000,9000,9500,10000]:
        llm=SimulatedLLM(20000,20,bytes_per_token=1)
        a=Agent(llm,Toolbox([Big(1000)]),compaction=CompactionPolicy(20000,keep_recent_tokens=0,summary_max_tokens=1000))
        try: await run(a,\"q\"*size)
        except CompactionError as ex:
            ev=a.events;b=context_bound(ev);cut=choose_cut(ev,b,0); c=Compaction(llm.summary.message[\"content\"],cut,b,0,Usage())
            print(\"initial\",size, \"first\",llm.requests[0][\"prompt\"],\"estimated\",bound_after_compaction([*ev,c],c),\"actual\",llm.tokens([build_context(a.system_prompt,[*ev,c]),a.toolbox.schemas()]),\"reserve\",a.compaction.reserve(llm.max_tokens), str(ex));break
asyncio.run(main())
PY"
````

````
accepted over-limit summaries [(19500, 115)] status done
unexpected summary calls ["no complete summary (finish_reason='tool_calls')", "no complete summary (finish_reason='tool_calls')", "no complete summary (finish_reason='tool_calls')"] status done
initial 8000 first 8852 estimated 18503 actual 10428 reserve 1676 Compaction failed: the summary does not shrink the context enough (~18456 -> ~18503 tokens), and the context does not fit the 20000-token window.
````

**[command]** exit=0

````
/bin/bash -lc "curl -fsSL 'https://raw.githubusercontent.com/cli/cli/v2.45.0/pkg/cmd/api/api.go' | sed -n '589,632p'"
````

````
}

	var objectError struct {
		Message string
	}
	var errors []string
	for _, rawErr := range errorObjects {
		if len(rawErr) == 0 {
			continue
		}
		if rawErr[0] == '{' {
			err := json.Unmarshal(rawErr, &objectError)
			if err != nil {
				return bodyCopy, "", err
			}
			errors = append(errors, objectError.Message)
		} else if rawErr[0] == '"' {
			var stringError string
			err := json.Unmarshal(rawErr, &stringError)
			if err != nil {
				return bodyCopy, "", err
			}
			errors = append(errors, stringError)
		}
	}

	if len(errors) > 0 {
		return bodyCopy, strings.Join(errors, "\n"), nil
	}

	return bodyCopy, "", nil
}

func previewNamesToMIMETypes(names []string) string {
	types := []string{fmt.Sprintf("application/vnd.github.%s-preview+json", names[0])}
	for _, p := range names[1:] {
		types = append(types, fmt.Sprintf("application/vnd.github.%s-preview", p))
	}
	return strings.Join(types, ", ")
}
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"pytest\",\"httpx\",\"jsonschema\",\"pyyaml\"]
# ///
import asyncio
from dataclasses import replace
from loola_agent import Agent,Toolbox,CompactionPolicy,Compaction,Usage,DummyTool
from tests.test_compaction import SimulatedLLM,Big,run
class Sim(SimulatedLLM):
    async def complete(self,messages,tools,*,max_tokens=None):
        c=await super().complete(messages,tools,max_tokens=max_tokens)
        return replace(c,usage=Usage(19950,c.usage.completion)) if self.requests[-1][\"summary\"] else c
async def main():
    seen=await run(Agent(Sim(20000,10),Toolbox([Big()]),compaction=CompactionPolicy(20000,8000,3000,1000)))
    print(\"summary\",[(x.usage.prompt,x.usage.completion) for x in seen if isinstance(x,Compaction)],seen[-1].status)
    t=DummyTool(\"x\",\"x\",{\"type\":\"object\",\"properties\":{\"v\":{\"type\":\"string\"}}}); box=Toolbox([t])
    t.parameters[\"properties\"][\"v\"][\"type\"]=\"integer\"
    print(\"declared\",box.schemas()[0][\"function\"][\"parameters\"],\"call\",await box.call(\"x\",'{\"v\":\"a\"}'))
    box.schemas().clear(); print(\"next declarations\",box.schemas())
asyncio.run(main())
PY"
````

````
summary [(19950, 115)] done
declared {'type': 'object', 'properties': {'v': {'type': 'string'}}} call Error: invalid arguments for 'x' at v: 'a' is not of type 'integer'. Expected schema: {"type": "object", "properties": {"v": {"type": "integer"}}}
next declarations []
````

**[command]** exit=0

````
/bin/bash -lc "PYTHONPATH=src:. UV_CACHE_DIR=/tmp/loola-review.iTsTm7q4/uv-cache uv run - <<'PY'
# /// script
# requires-python = \">=3.13,<3.14\"
# dependencies = [\"pytest\",\"httpx\",\"jsonschema\",\"pyyaml\"]
# ///
import asyncio
from loola_agent import Agent, Toolbox, RunFinished
from tests.test_agent import FakeLLM,reply,Echo
async def main():
    a=Agent(FakeLLM(reply(\"one\"),reply(\"two\")),Toolbox([Echo()]))
    async for ev in a.send(\"one\"):
        if isinstance(ev, RunFinished): break
    try: print(\"followup\",await anext(a.send(\"two\")))
    except Exception as e: print(ev.status,type(e).__name__,str(e))
asyncio.run(main())
PY"
````

````
done RuntimeError send() is already running for this conversation
````

**[agent]**

**170 tests passed, one live test deselected.** Six material issues remain in `35180ff` under brief v2.

1. **High — Summary responses bypass the required window check.** I supplied a summary reporting 19,950 prompt tokens and 115 completion tokens against a 20,000-token window. The agent applied it and finished `done`. `_check_window` runs only for regular responses and hardcodes the regular reply limit. Check summary responses with `summary_max_tokens`, record their paid usage, and raise on a measured violation. [agent.py:64](<local path>), [agent.py:84](<local path>), [agent.py:109](<local path>)

2. **High — Compaction counts the initial user message twice.** `first.usage.prompt` already includes the first task. `_message_bytes(head)` charges for that task again. With an 8,000-byte task and the repo’s one-byte-per-token simulator, the agent rejected a compacted prompt estimated at **18,503**. The simulator measured **10,428**, leaving ample room for the **1,676** reserve. Keep the first measured prompt and charge only for additions to its user content. This fixes duplicate accounting within the approved practical estimator. [compaction.py:78](<local path>), [events.py:85](<local path>)

3. **High — A tool call returned instead of a summary can still end in success.** At a soft threshold I reproduced three such responses, three `SummaryDiscarded` events, then `done`. Decision 13 still requires an explicit error for this outcome. Record the cost and raise. Continuing with the original context is appropriate for a **complete** summary that fails to shrink it. The current test exercises only the hard-limit path. [agent.py:114](<local path>), [test_compaction.py:168](<local path>), [brief.md:40](<local path>)

4. **Medium — `RunFinished` is observable before the conversation accepts a follow-up.** Breaking from `async for` on `RunFinished("done")` and immediately calling `send()` raised `RuntimeError: send() is already running`. Release the guard before yielding the terminal event, while keeping it held throughout active work. Add that exact two-send test. [agent.py:39](<local path>)

5. **Medium — The schema snapshot can diverge from validation or be overwritten by a caller.** After changing a tool’s nested parameter type, the cached declaration still advertised `string` while dispatch rejected strings and required `integer`. Separately, `toolbox.schemas().clear()` erased all subsequent declarations. Build validation and declarations from the same owned snapshot, and return a copy at the public boundary. This preserves v2’s explicit `additionalProperties: true` decision. [tools.py:33](<local path>), [tools.py:40](<local path>)

6. **Medium — A wrong repository can abort `list_issues` as an infrastructure failure.** This tool uses GraphQL. GitHub can return HTTP 200 with a `NOT_FOUND` error, and `gh` prints the GraphQL error message without an `(HTTP nnn)` suffix. The new classifier therefore raises `GhUnavailable` for a repository typo the model could correct. Recognize the structured GraphQL `NOT_FOUND` result while retaining fatal handling for transport, authentication, and quota failures. [gh_proxy.py:108](<local path>), [gh_proxy.py:236](<local path>), [GitHub CLI error formatting](https://github.com/cli/cli/blob/v2.45.0/pkg/cmd/api/api.go#L591-L616)

**not approved** — Remaining blockers are unchecked summary usage, duplicate first-task accounting, invalid summaries continuing, the terminal-event send guard, mutable schema contracts, and misclassified GraphQL lookup errors.
