# Sub-agent: review of the original task code

Full bb session log, converted from the raw event stream: inputs, agent messages, reasoning, commands with output, file changes and tool calls (long outputs truncated to 4000 characters). Local paths, thread ids and emails are redacted; outputs that came from the developer's private projects are replaced with a placeholder.

---

## [input]

Контекст: тестовое задание — минимальный coding-agent harness на Python в ~/projects/loola-test-task. Задание: TASK.md. Код: agent.py. Коммит 44f5083 — оригинальный код из задания как есть; 1d6d373 — единственная наша правка: LLM_* конфиг читается из env (запуск: uv run --env-file .env agent.py "задача").

Твоя задача — ревью текущего кода (read-only: файлы не меняй, не коммить). Ничего больше не делай.
- Найди качественные ошибки и проблемы: баги, нарушения протокола OpenAI chat completions / tool calling, падения на реальных ответах моделей, проблемы надёжности и безопасности, вещи, которые сломают длинную многошаговую задачу. Каждую — с конкретным сценарием, где она стреляет. Где дёшево — подтверди экспериментом (например фейковый OpenAI-compatible сервер на localhost или прямой вызов функций), реального LLM endpoint нет.
- Предложи, что важно улучшить, сохраняя минималистичный showcase-формат: один небольшой файл, читаемый за пару минут, без фреймворков и оверинжиниринга. Для каждого предложения: зачем, цена в строках/сложности, приоритет (must / should / skip). Явно перечисли то, что улучшать НЕ стоит, и почему.
- Динамическую подгрузку тулов и context compaction не проектируй — это отдельные задачи. Но если какая-то структура текущего кода будет мешать их добавить (или мешать prompt cache), отметь это одной-двумя строками.
- Учитывай мандатные инженерные стандарты пользователя (скилл code-guidelines), но применяй их соразмерно размеру showcase.

Результат: отчёт на русском в <local path> (Markdown, абзацы без hard-wrap): сначала ошибки по severity, потом улучшения, потом «не трогать». В финальном ответе — краткая выжимка и путь к отчёту.

<details><summary>reasoning</summary>

````
I'm going to read the relevant files first, and I also need to load the code-guidelines skill as the user asked.
````
</details>

**[agent]**

Начинаю: читаю задание, код и историю коммитов.

**[command]** exit=0

````
cd ~/projects/loola-test-task && git log --oneline -5 && git status --porcelain && ls -la && cat TASK.md && echo ---- && cat -n agent.py && echo ---- && git show 1d6d373 --stat && git show 1d6d373 | head -60
````

````
1d6d373 chore: read LLM endpoint config from env so the agent can run without editing code
44f5083 chore: import original test task code as baseline
total 84
drwxrwxr-x  4 bb bb  4096 Nov 24 09:54 .
drwxrwxr-x 17 bb bb  4096 Nov 24 09:53 ..
-rw-rw-r--  1 bb bb   115 Nov 24 09:54 .env.example
drwxrwxr-x  8 bb bb  4096 Nov 24 09:55 .git
-rw-rw-r--  1 bb bb   114 Nov 24 09:54 .gitignore
-rw-rw-r--  1 bb bb     5 Nov 24 09:53 .python-version
drwxrwxr-x  4 bb bb  4096 Nov 24 09:54 .venv
-rw-rw-r--  1 bb bb  5476 Nov 24 09:54 TASK.md
-rw-rw-r--  1 bb bb  4050 Nov 24 09:54 agent.py
-rw-rw-r--  1 bb bb   179 Nov 24 09:54 pyproject.toml
-rw-rw-r--  1 bb bb 39635 Nov 24 09:54 uv.lock
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
    payload = {"model": LLM_MODEL, "messages": messages, "tools": LLM_TOOLS, "tool_choice": "auto",
               "temperature": 0.1, "max_tokens": 4096}
    llm_http_response = requests.post(f"{LLM_BASE_URL}/chat/completions", json=payload, headers=LLM_HEADERS)
    llm_http_response.raise_for_status()
    msg = llm_http_response.json()["choices"][0]["message"]
    content = (msg.get("content") or "").strip()
    tool_calls = msg.get("tool
… [7734 more characters truncated]
````

**[tool: Skill]**

````
{
 "skill": "code-guidelines"
}
````

````
Launching skill: code-guidelines
````

<details><summary>reasoning</summary>

````
I'm going through the code to list its problems, and the first one I'm looking at is the parallel tool call handling: each tool call gets appended as its own assistant message, which duplicates content. I'm weighing whether the OpenAI protocol actually accepts that split, since one assistant message with several tool calls followed by their results might be the valid form, and I'm trying to settle that question.

Next I'm checking whether the provider actually tolerates the split, and I'm also noticing that each split message duplicates the content and changes the rendered prompt from what the model originally generated. I'm also thinking about whether the dropped reasoning fields matter for thinking models.

I'm checking whether the rebuilt assistant message drops fields the provider needs, like reasoning content for thinking models, and I'm thinking about just appending the original message once, unchanged.

I'm checking the error handling on the tool arguments now: a non-dict payload or a missing `command` key gets caught and returned to the model, so those cases are fine. The real crash is the bare `json.loads` on arguments, since a `JSONDecodeError` there kills the whole agent and loses its progress, so the fix is to send that error back to the model as a tool result.

I'm moving on to the finish reason, which the code never checks: a `length` truncation can leave a half-written answer that the agent treats as complete, and a truncated tool call produces the invalid JSON that crashes it. With thinking models the reasoning may count against max_tokens, so that truncation could be common. I'm also noting that the HTTP call has no timeout or retry, and that raise_for_status drops the server's error body.

Now I'm looking at how the agent handles output size: unbounded tool results go straight into the messages, so a big `cat` or `find` could push the next request over the context limit and crash it. The fix is to truncate tool output at the harness level.

I'm checking the subprocess timeout path now: on a timeout only the shell gets killed, so any grandchild processes can keep the captured pipes open and hang the call.

I'm checking the subprocess timeout behavior next: killing the shell on timeout may leave grandchild processes running, like a dev server started with `npm run dev`, which would keep holding its port. I want to verify that experimentally.

I'm checking whether background processes started with `&` keep the captured pipes open, so the call hangs until timeout even though the command itself finished. I'm also noting that on timeout the partial output is thrown away, so the model can't see how far the command got, and that stdin is inherited, so commands like `git commit` or a REPL could block waiting for input.

I'm now checking how the subprocess handles stdin: with it inherited, a command like `git commit` with no `-m` can open an editor on the terminal and block until the timeout. I'm also looking at text decoding, since a binary output would raise a UnicodeDecodeError that discards the exit code and all output even though the command already ran, and I'm considering `errors="replace"` as the fix.

I'm now looking at security: the subprocess inherits the full environment, including the LLM API key, so the model could read it with `env` or `printenv`, and a malicious file could prompt-inject it out. I'm thinking about stripping LLM_* variables from the child environment and documenting that this should run in a container.

I'm noting that the agent never records token usage, even though the task asks me to measure it, and that a loop with a 1000-turn cap and no budget could keep spinning. I'm also seeing that it exits with code 0 even when it fails, so the success rate couldn't be measured from the exit status.

I'm looking at the empty response case now: if the model returns no content and no tool calls, the agent prints "(no text output)" and reports finished, which ends the run silently. I'd rather fail t
… [4731 more characters truncated]
````
</details>

<details><summary>reasoning</summary>

````
Код маленький, и багов видно много. Подтверждаю их экспериментами с фейковым сервером и прямыми вызовами `run_bash`, сначала смотрю окружение проекта.
````
</details>

**[command]** exit=0

````
cd ~/projects/loola-test-task && cat pyproject.toml .python-version .gitignore && .venv/bin/python -V && .venv/bin/python -c "import requests;print(requests.__version__)"; echo "BB_THREAD_STORAGE=$BB_THREAD_STORAGE"
````

````
[project]
name = "loola-agent"
version = "0.1.0"
description = "Minimal coding agent loop (Loola test task)"
requires-python = ">=3.13"
dependencies = [
    "requests>=2.34.2",
]
3.13
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv
.env
Python 3.13.17
2.34.2
BB_THREAD_STORAGE=<local path>
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
The thread storage variable points somewhere else, but the user named the report path thr_…, so I'll keep the experiments under that thread's reports/exp folder and put the scripts in a separate directory. Next, I'm writing the fake server.
````
</details>

<details><summary>reasoning</summary>

````
Пишу фейковый сервер, который отдаёт заранее заданные ответы и логирует каждый запрос, чтобы видеть, что агент реально отправляет в API.
````
</details>

**[command]** exit=0

````
mkdir -p <local path> && cd $_ && cat > fake_server.py <<'PY'
"""Scripted OpenAI-compatible /chat/completions server. Usage: fake_server.py PORT SCENARIO LOGFILE"""
import json, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT, SCENARIO, LOG = int(sys.argv[1]), sys.argv[2], sys.argv[3]

def tc(id_, cmd, raw=None):
    return {"id": id_, "type": "function",
            "function": {"name": "bash", "arguments": raw if raw is not None else json.dumps({"command": cmd})}}

def choice(msg, finish="stop"):
    return {"id": "x", "object": "chat.completion", "choices": [{"index": 0, "message": {"role": "assistant", **msg}, "finish_reason": finish}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}

DONE = choice({"content": "done"})
SCRIPTS = {
    "parallel": [choice({"content": "I will check two things.", "reasoning_content": "secret plan",
                         "tool_calls": [tc("call_a", "echo A"), tc("call_b", "echo B")]}, "tool_calls"), DONE],
    "badjson": [choice({"content": None, "tool_calls": [tc("call_a", None, raw='{"command": "echo hi"')]}, "tool_calls"), DONE],
    "emptyargs": [choice({"content": None, "tool_calls": [{"id": "c", "type": "function", "function": {"name": "bash", "arguments": ""}}]}, "tool_calls"), DONE],
    "length": [choice({"content": "Here is the full refactoring plan:\n1. Move"}, "length")],
    "empty": [choice({"content": "", "reasoning_content": "I should now run the tests..."})],
    "error200": [{"error": {"message": "upstream overloaded", "code": 503}}],
    "err400": ["HTTP400"],
    "bigout": [choice({"content": None, "tool_calls": [tc("c1", "seq 1 300000")]}, "tool_calls"), DONE],
    "env": [choice({"content": None, "tool_calls": [tc("c1", "env | grep ^LLM_")]}, "tool_calls"), DONE],
    "stdin": [choice({"content": None, "tool_calls": [tc("c1", "cat")]}, "tool_calls"), DONE],
    "hang": ["HANG"],
}
script = SCRIPTS[SCENARIO]
n = 0

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        global n
        body = self.rfile.read(int(self.headers["Content-Length"]))
        with open(LOG, "a") as f:
            f.write(json.dumps({"n": n, "bytes": len(body), "body": json.loads(body)}) + "\n")
        resp = script[min(n, len(script) - 1)]; n += 1
        if resp == "HANG":
            time.sleep(3600); return
        if resp == "HTTP400":
            data = json.dumps({"error": {"message": "This model's maximum context length is 32768 tokens. However, you requested 51234 tokens.", "type": "BadRequestError"}}).encode()
            self.send_response(400)
        else:
            data = json.dumps(resp).encode(); self.send_response(200)
        self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data))); self.end_headers()
        self.wfile.write(data)

HTTPServer(("127.0.0.1", PORT), H).serve_forever()
PY
cat > run_scenario.sh <<'SH'
#!/usr/bin/env bash
# run_scenario.sh SCENARIO PORT [stdin-text]
set -u
EXP=$(cd "$(dirname "$0")" && pwd); S=$1; P=$2
LOG=$EXP/$S.requests.jsonl; rm -f "$LOG"
REPO=~/projects/loola-test-task
"$REPO/.venv/bin/python" "$EXP/fake_server.py" "$P" "$S" "$LOG" & SRV=$!
sleep 0.5
WORK=$(mktemp -d); cd "$WORK"
start=$(date +%s.%N)
LLM_BASE_URL=http://127.0.0.1:$P/v1 LLM_API_KEY=sk-FAKE-SECRET-123 LLM_MODEL=fake \
  timeout 15 "$REPO/.venv/bin/python" "$REPO/agent.py" "do the task" < "${3:-/dev/null}" > "$EXP/$S.out" 2>&1
echo "agent exit code: $? ; elapsed: $(echo "$(date +%s.%N) - $start" | bc)s" >> "$EXP/$S.out"
kill $SRV; rm -rf "$WORK"
SH
chmod +x run_scenario.sh && echo ok
````

````
ok
````

**[command]** exit=0

````
echo "SECRET-FROM-PARENT-STDIN" > stdin.txt && p=18700; for s in parallel badjson emptyargs length empty error200 err400 bigout env hang; do p=$((p+1)); ./run_scenario.sh $s $p; done; ./run_scenario.sh stdin 18799 stdin.txt; for s in parallel badjson emptyargs length empty error200 err400 bigout env hang stdin; do echo "######## $s"; tail -c 1500 $s.out; done
````

````
./run_scenario.sh: line 11: stdin.txt: No such file or directory
######## parallel

============================================================
🔄 Turn 1
============================================================

🤖 I will check two things.

🔧 Tool: bash({"command": "echo A"})
   → Exit code: 0
A


🔧 Tool: bash({"command": "echo B"})
   → Exit code: 0
B


============================================================
🔄 Turn 2
============================================================

🤖 done

✅ Agent finished
agent exit code: 0 ; elapsed: .754193968s
######## badjson

============================================================
🔄 Turn 1
============================================================
Traceback (most recent call last):
  File "<local path>", line 99, in <module>
    agent_loop(prompt)
    ~~~~~~~~~~^^^^^^^^
  File "<local path>", line 84, in agent_loop
    arguments = json.loads(tool_call["function"]["arguments"])
  File "<local path>", line 352, in loads
    return _default_decoder.decode(s)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^
  File "<local path>", line 345, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "<local path>", line 361, in raw_decode
    obj, end = self.scan_once(s, idx)
               ~~~~~~~~~~~~~~^^^^^^^^
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 1 column 22 (char 21)
agent exit code: 1 ; elapsed: .558648812s
######## emptyargs

============================================================
🔄 Turn 1
============================================================
Traceback (most recent call last):
  File "<local path>", line 99, in <module>
    agent_loop(prompt)
    ~~~~~~~~~~^^^^^^^^
  File "<local path>", line 84, in agent_loop
    arguments = json.loads(tool_call["function"]["arguments"])
  File "<local path>", line 352, in loads
    return _default_decoder.decode(s)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^
  File "<local path>", line 345, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "<local path>", line 363, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
agent exit code: 1 ; elapsed: .763947557s
######## length

============================================================
🔄 Turn 1
============================================================

🤖 Here is the full refactoring plan:
1. Move

✅ Agent finished
agent exit code: 0 ; elapsed: .538640797s
######## empty

============================================================
🔄 Turn 1
============================================================
(no text output)
✅ Agent finished
agent exit code: 0 ; elapsed: .646747504s
######## error200

============================================================
🔄 Turn 1
============================================================
Traceback (most recent call last):
  File "<local path>", line 99, in <module>
    agent_loop(prompt)
    ~~~~~~~~~~^^^^^^^^
  File "<local path>", line 74, in agent_loop
    content, tool_calls = call_llm(messages)
                          ~~~~~~~~^^^^^^^^^^
  File "<local path>", line 62, in call_llm
    msg = llm_ht
… [2622 more characters truncated]
````

<details><summary>reasoning</summary>

````
The stdin path looks wrong because run_scenario changes into WORK before it reads, so I'll pass an absolute path to fix that. I also want to check the parallel requests log and the bigout byte count.
````
</details>

<details><summary>reasoning</summary>

````
Почти всё подтвердилось, кроме одного сбоя: в сценарии stdin путь был относительным. Перезапускаю с абсолютным путём и проверяю, что агент отправил на второй запрос после parallel и bigout.
````
</details>

**[command]** exit=0

````
./run_scenario.sh stdin 18798 $PWD/stdin.txt; tail -c 600 stdin.out; echo "#### parallel req2 messages"; sed -n 2p parallel.requests.jsonl | jq -c '.body.messages[2:]'; echo "#### bigout req sizes"; jq -c '{n,bytes}' bigout.requests.jsonl; echo "#### payload keys"; head -1 parallel.requests.jsonl | jq -c '.body | del(.messages)'
````

````
============================================================
🔄 Turn 1
============================================================
🔧 Tool: bash({"command": "cat"})
   → Exit code: 0
SECRET-FROM-PARENT-STDIN


============================================================
🔄 Turn 2
============================================================

🤖 done

✅ Agent finished
agent exit code: 0 ; elapsed: .480215712s
#### parallel req2 messages
[{"role":"assistant","content":"I will check two things.","tool_calls":[{"id":"call_a","type":"function","function":{"name":"bash","arguments":"{\"command\": \"echo A\"}"}}]},{"role":"tool","tool_call_id":"call_a","content":"Exit code: 0\nA\n"},{"role":"assistant","content":"I will check two things.","tool_calls":[{"id":"call_b","type":"function","function":{"name":"bash","arguments":"{\"command\": \"echo B\"}"}}]},{"role":"tool","tool_call_id":"call_b","content":"Exit code: 0\nB\n"}]
#### bigout req sizes
{"n":0,"bytes":968}
{"n":1,"bytes":2290100}
#### payload keys
{"model":"fake","tools":[{"type":"function","function":{"name":"bash","description":"Execute a shell command and return the output.","parameters":{"type":"object","properties":{"command":{"type":"string","description":"The bash command to execute."}},"required":["command"]}}}],"tool_choice":"auto","temperature":0.1,"max_tokens":4096}
````

<details><summary>reasoning</summary>

````
Confirmed the parallel split is duplicating content and dropping reasoning_content, and the big output is already about 2.29MB in context. Next I'll test run_bash directly: background processes, orphans after a timeout, partial output getting lost, and binary output, with the TTY stdin issue already confirmed. I'll import the agent with the env vars set and monkeypatch subprocess.run with a 2-second timeout for the timeout cases.
````
</details>

<details><summary>reasoning</summary>

````
Протокол уровня подтверждён; далее проверю прямые вызовы `run_bash` (фоновые процессы, осиротевшие после таймаута, потерю частичного вывода, бинарный вывод), подменив 120s на 2s через обёртку над `subprocess.run`.
````
</details>

**[command]** exit=1

````
cd /tmp && W=$(mktemp -d) && cd $W && LLM_BASE_URL=x LLM_API_KEY=x LLM_MODEL=x ~/projects/loola-test-task/.venv/bin/python -I - <<'PY'
import sys, time, subprocess, functools
sys.path.insert(0, "<local path>")
import agent

def t(label, cmd):
    s = time.time(); r = agent.run_bash(cmd); print(f"--- {label}: {time.time()-s:.1f}s\n{r[:300]!r}")

t("background server (sleep 6 &)", "sleep 6 & echo started")
t("binary output", "printf 'ok\\n'; head -c 64 /bin/ls; exit 3")
real = subprocess.run
agent.subprocess.run = lambda *a, **k: real(*a, **{**k, "timeout": 2})
t("timeout w/ partial output", "echo 'test_1 PASSED'; echo 'test_2 started'; sleep 30")
t("timeout orphan", "sleep 77 ; echo after")
time.sleep(0.5)
print("orphan sleep 77 alive:", subprocess.run("pgrep -f 'sleep 77'", shell=True, capture_output=True, text=True).stdout.strip() or "no")
subprocess.run("pkill -f 'sleep 77'", shell=True)
t("timeout w/ background child holding pipe", "sleep 88 & sleep 30")
print("orphan sleep 88 alive:", subprocess.run("pgrep -f 'sleep 88'", shell=True, capture_output=True, text=True).stdout.strip() or "no")
subprocess.run("pkill -f 'sleep 88'", shell=True)
PY
rm -rf $W
````

````
Exit code 144
````

<details><summary>reasoning</summary>

````
I'm wondering whether exit code 144 (128+16) could point to a signal, and whether `pkill -f 'sleep 77'` might have matched the shell running it, since the shell's own command line contains that pattern.

I'm now wondering whether pkill's pattern matched the outer bash process, since its command line contains the heredoc text with 'sleep 77', and that would explain the 144 exit code. I'll switch to anchored patterns like '^sleep 77' and write the script to a file instead.
````
</details>

<details><summary>reasoning</summary>

````
Мой pkill убил и собственный шелл, потому что паттерн совпал с его командной строкой. Переписываю скрипт и привязываю паттерн к `^sleep 77`.
````
</details>

**[command]** exit=1

````
cat > bash_edge.py <<'PY'
import sys, time, subprocess
sys.path.insert(0, "<local path>")
import agent

def t(label, cmd):
    s = time.time(); r = agent.run_bash(cmd); print(f"--- {label}: {time.time()-s:.1f}s\n{r[:300]!r}", flush=True)

def alive(pat):
    return subprocess.run(["pgrep", "-f", pat], capture_output=True, text=True).stdout.strip() or "no"

t("background server (sleep 6 &)", "sleep 6 & echo started")
t("binary output", "printf 'ok\\n'; head -c 64 /bin/ls; exit 3")
real = subprocess.run
agent.subprocess.run = lambda *a, **k: real(*a, **{**k, "timeout": 2})
t("timeout w/ partial output", "echo 'test_1 PASSED'; echo 'test_2 started'; sleep 30")
t("timeout orphan", "sleep 77 ; echo after")
time.sleep(0.5); print("orphan '^sleep 77' alive pid:", alive("^sleep 77"))
subprocess.run(["pkill", "-f", "^sleep 77"])
PY
W=$(mktemp -d) && cd $W && LLM_BASE_URL=x LLM_API_KEY=x LLM_MODEL=x ~/projects/loola-test-task/.venv/bin/python -I <local path> 2>&1 | tee <local path> rm -rf $W
````

````
Exit code 1
--- background server (sleep 6 &): 6.0s
'Exit code: 0\nstarted\n'
--- binary output: 0.0s
'Exit code: 3\nok\n\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00>\x00\x01\x00\x00\x000m\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00($\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x008\x00\n\x00@\x00\x1f\x00\x1e\x00'
--- timeout w/ partial output: 2.0s
'Error: command timed out after 120s'
--- timeout orphan: 2.0s
'Error: command timed out after 120s'
orphan '^sleep 77' alive pid: 2735494
pwd: error retrieving current directory: getcwd: cannot access parent directories: No such file or directory
````

<details><summary>reasoning</summary>

````
I'm checking whether the first 64 bytes held invalid UTF-8, and they apparently didn't, so I'll test with bytes like 0xff using printf. I also confirmed that the 6-second sleep blocked until it finished, so running the dev server with an ampersand would have hit the timeout and left an orphan process.
````
</details>

<details><summary>reasoning</summary>

````
Бинарник оказался валидным UTF-8 по первым 64 байтам, поэтому теперь отдельно проверяю его на заведомо невалидных байтах `\xff`.
````
</details>

**[command]** exit=0

````
cd /tmp && LLM_BASE_URL=x LLM_API_KEY=x LLM_MODEL=x ~/projects/loola-test-task/.venv/bin/python -I -c '
import sys; sys.path.insert(0, "<local path>"); import agent
print(repr(agent.call_tool("bash", {"command": "echo created > /tmp/side_effect_marker; printf \"line1\\n\\xff\\xfe\\n\"; exit 3"})))
print(repr(agent.call_tool("bash", {"cmd": "ls"})))
print(repr(agent.call_tool("bash", {"command": ["ls", "-la"]})))
' 2>&1 | tee -a <local path> ls -la /tmp/side_effect_marker && rm /tmp/side_effect_marker
````

````
<persisted-output>
Output too large (201.4KB). Full output saved to: <local path>

Preview (first 2KB):
'Exit code: 3\nline1\n\\xff\\xfe\n'
"Error calling bash: run_bash() got an unexpected keyword argument 'cmd'"
'Exit code: 0\n01_transcribe.py\n02_blocks.py\n02b_blocks.py\n03_translate.py\n03b_translate.py\n03c_translate.py\n04_tts.py\n05_sent_tts.py\n06_assemble.py\n06b_assemble.py\n06c_assemble.py\n07_refit.py\n07b_blockfix.py\n08_qa.py\n09_review.py\n0a16cc73.html\n11439331.html\n568bfa50.html\n677.txt\n71ed9888.html\n9d571563.html\n9ed92050.html\nD\nOSL_PIPE_1000_SingleOfficeIPC_25697b963ab548e565b75a6de2b4ab\nT\n__pycache__\na297.json\na3.html\na677.txt\na718.txt\na_current.b64\nab-agg.ts\nab-bad\nab-bad.log\nab-dev-term\nab-dev.log\nab-dl\nab-dl.log\nab-f10.png\nab-f13.png\nab-f15.png\nab-f16.png\nab-f17.png\nab-f18.png\nab-f19.png\nab-f2.png\nab-f20.png\nab-f21.png\nab-f22.png\nab-f3.png\nab-f4.png\nab-f5.png\nab-f6.png\nab-f7.png\nab-f8.png\nab-g2.png\nab-ok\nab-ok.log\nab-wake.md\nab-wake2.md\nab-wake3.md\nab_before.js\nab_loop.js\nab_state.js\nabw-cache\nabw-cache2\nabw-mem.txt\nabw-term\nabw2.log\nacc-commit.sh\nacc2.sh\naccountant-build-webinars-20261118.py\naccountant-playwriter-skill.txt\naccountant-uv-cache\naccountant-webinar-20261118-granola.json\naccountant-webinar-20261118-granola.txt\naccountant-webinars-lo\naccountant-webinars-render\nact.swift\nadc.pdf\nadmin-chat.txt\nadminchat\nads.html\nae2.ts\nae3.ts\naf32ab73.html\nagent-build.tour.js\nagent-route.ts\nagent_final.md\nagy-acp-1795267238173.zip\nagy_acp_server.par.ERROR\nagy_acp_server.par.INFO\nagy_acp_server.par.WARNING\nagy_acp_server.par.bb-single-sin.bb.log.ERROR.20261121-162152.2446515\nagy_acp_server.par.bb-single-sin.bb.log.ERROR.20261121-162222.2446729\nagy_acp_server.par.bb-single-sin.bb.log.ERROR.20261121-162238.2446914\nagy_acp_server.par.bb-single-sin.bb.log.ERROR.20261121-164054.2450749\nagy_acp_server.par.bb-single-sin.bb.log.ERROR.20261121-164231.2451379\nagy_acp_server.par.bb-single-sin.bb.log.ERROR.20261121-164259.2451491\nagy_acp_server.par.bb-single-sin.bb.log.ERROR.20261
...
</persisted-output>
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
The printf test came back wrong: dash doesn't expand \x escapes, so \xff showed up as the literal text "\\xff". I'll switch to emitting the bytes with Python or with octal printf. The list-form ["ls","-la"] with shell=True also went wrong: only the first element ran as the command and "-la" became $0, so ls ran without its flag and nothing complained. I should clean up bash_edge.out before going further, and I

I need to clean up the bash_edge.out file, since I appended a 200KB listing of /tmp into it and that's private-ish data sitting in the report directory. Then I'll rerun the octal test in an empty directory without teeing the list.
````
</details>

<details><summary>reasoning</summary>

````
Дашь `printf` с octal-escape в пустой директории, повторю тест, потому что dash не понял `\x`-escape. Ещё уберу из лога случайно попавший туда листинг `/tmp`.
````
</details>

**[command]** exit=0

````
EXP=<local path> && head -c 2000 $EXP/bash_edge.out | head -12 > $EXP/bash_edge.tmp && mv $EXP/bash_edge.tmp $EXP/bash_edge.out && W=$(mktemp -d) && cd $W && touch file_a && LLM_BASE_URL=x LLM_API_KEY=x LLM_MODEL=x ~/projects/loola-test-task/.venv/bin/python -I -c '
import sys; sys.path.insert(0, "<local path>"); import agent
print(repr(agent.call_tool("bash", {"command": "echo created > side_effect_marker; printf \"line1\\n\\377\\376\\n\"; exit 3"})))
print(repr(agent.call_tool("bash", {"cmd": "ls"})))
print(repr(agent.call_tool("bash", {"command": ["ls", "-la"]})))
' 2>&1 | tee -a $EXP/bash_edge.out; ls; cd /; rm -rf $W; cat $EXP/bash_edge.out | cut -c1-200
````

````
"Error calling bash: 'utf-8' codec can't decode byte 0xff in position 6: invalid start byte"
"Error calling bash: run_bash() got an unexpected keyword argument 'cmd'"
'Exit code: 0\nfile_a\nside_effect_marker\n'
file_a
side_effect_marker
--- background server (sleep 6 &): 6.0s
'Exit code: 0\nstarted\n'
--- binary output: 0.0s
'Exit code: 3\nok\n\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00>\x00\x01\x00\x00\x000m\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00($\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00
--- timeout w/ partial output: 2.0s
'Error: command timed out after 120s'
--- timeout orphan: 2.0s
'Error: command timed out after 120s'
orphan '^sleep 77' alive pid: 2735494
'Exit code: 3\nline1\n\\xff\\xfe\n'
"Error calling bash: run_bash() got an unexpected keyword argument 'cmd'"
'Exit code: 0\n01_transcribe.py\n02_blocks.py\n02b_blocks.py\n03_translate.py\n03b_translate.py\n03c_translate.py\n04_tts.py\n05_sent_tts.py\n06_assemble.py\n06b_assemble.py\n06c_assemble.py\n07_refit
"Error calling bash: run_bash() got an unexpected keyword argument 'cmd'"
'Exit code: 0\nfile_a\nside_effect_marker\n'
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm checking whether the first line of the UTF-8 test made it into the final file, and it did, since the "Error calling bash" message printed first. The leftover junk at the end is from the earlier head -12 call keeping old lines, so I'll rewrite the file cleanly. I also noticed the marker file got created even though the model only received the decode error, and the list argument ran plain `ls` without `-la`.

I'll rewrite the bash_edge.out file with only the important lines, dropping the junk ones containing the \xff bytes and the /tmp listing.
````
</details>

<details><summary>reasoning</summary>

````
Подтвердил: при невалидном UTF-8 команда всё же выполнилась (маркер `side_effect_marker` создан), но модель видит только ошибку `codec can't decode`, без exit code и вывода. Теперь чищу лог от старых мусорных строк.
````
</details>

**[command]** exit=0

````
EXP=<local path> && grep -v -e '\\\\xff' -e '01_transcribe' $EXP/bash_edge.out | awk '!seen[$0]++' > $EXP/t && mv $EXP/t $EXP/bash_edge.out && cut -c1-160 $EXP/bash_edge.out && ls $EXP && pgrep -f '^sleep 77' || echo "no orphans left"
````

````
--- background server (sleep 6 &): 6.0s
'Exit code: 0\nstarted\n'
--- binary output: 0.0s
'Exit code: 3\nok\n\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00>\x00\x01\x00\x00\x000m\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00($
--- timeout w/ partial output: 2.0s
'Error: command timed out after 120s'
--- timeout orphan: 2.0s
orphan '^sleep 77' alive pid: 2735494
"Error calling bash: run_bash() got an unexpected keyword argument 'cmd'"
'Exit code: 0\nfile_a\nside_effect_marker\n'
badjson.out
badjson.requests.jsonl
bash_edge.out
bash_edge.py
bigout.out
bigout.requests.jsonl
empty.out
empty.requests.jsonl
emptyargs.out
emptyargs.requests.jsonl
env.out
env.requests.jsonl
err400.out
err400.requests.jsonl
error200.out
error200.requests.jsonl
fake_server.py
hang.out
hang.requests.jsonl
length.out
length.requests.jsonl
parallel.out
parallel.requests.jsonl
run_scenario.sh
stdin.out
stdin.requests.jsonl
stdin.txt
no orphans left
````

<details><summary>reasoning</summary>

````
The awk dedupe seems to have dropped the second "Error: timed out" line, and the utf-8 line may be gone too, since "codec can't decode" isn't showing up. The experiments log is secondary, so I'll cite the evidence directly in the report, but I'll still append the utf-8 line by hand to keep things accurate. The 2.3MB requests file is fine. Next I want to quickly check a few protocol claims via web search, starting with how DeepSeek returns reasoning_content.

I'm weighing whether to search for DeepSeek's reasoning_content behavior or just hedge the claim. Since the parallel-split item already stands on its own, I'll lean toward running a quick search to get the DeepSeek detail right.
````
</details>

<details><summary>reasoning</summary>

````
Дописываю пропущенную строку про UTF-8 в лог, затем сверяю с документацией требование возвращать `reasoning_content` в цикле tool-call для thinking-моделей.
````
</details>

**[command]** exit=0

````
EXP=<local path> && printf '%s\n' "--- invalid utf-8 (printf '\\377\\376'; exit 3) — side effect file was created:" "\"Error calling bash: 'utf-8' codec can't decode byte 0xff in position 6: invalid start byte\"" "--- list instead of str ({'command': ['ls','-la']}): ran plain ls, -la silently became \$0" >> $EXP/bash_edge.out
````

**[tool: ToolSearch]**

````
{
 "query": "select:WebSearch",
 "max_results": 1
}
````

````
Matched tools: WebSearch
````

**[tool: webSearch]**

````

````

<details><summary>reasoning</summary>

````
Now I'm laying out the review report: a short context section, then the errors grouped by severity, starting with the critical ones.

Now I'm going through the critical errors in more detail: the JSON arguments that can break the whole agent, the unbounded tool output that blows up the context, and the parallel tool calls that get split and duplicated.

Rethinking the third critical issue: the assistant message is rebuilt by hand, so its reasoning field gets dropped. That would break DeepSeek even on single, non-parallel calls, so it belongs in the critical tier. I'll rename it to cover both the parallel split and the lost reasoning.

Next is the network and HTTP error handling. Requests can hang with no timeout, there's no retry on 429, 5xx, or connection errors, and a 200 response carrying an error body raises a KeyError. On top of that, `raise_for_status` hides the error text, so the "maximum context length" message never shows up. One 502 from the proxy during a 200-step task would wipe out the whole run, since history lives only in memory. I'm leaning toward High severity, with timeout and retry as the essential fixes.

Now I'm going through the high-severity issues: the agent ignores `finish_reason`, so a response cut off at the length limit gets treated as a finished answer, and the fix is to fail explicitly or have the model retry with smaller output instead.

Now I'm listing the high-severity items: the harness reports success on an empty response, and a tool call that the vLLM parser fails on can come through as plain text in `content`, so the agent treats it as a final answer. The fix is to stop reporting success from the harness, return the final text with an exit code, and fail on empty output. I'm also noting that the run returns no result or metrics, so token usage and success can't be measured.

Now I'm weighing the run_bash problem: background processes keep the pipe open, so `sleep 6 &` holds the call until it finishes, and `npm run dev &` ends in a timeout even though the server started. Redirecting the background output to a file would fix the hang, and I'm considering adding that hint to the tool description so the model does it.

Still working through the partial output issue: when the timeout fires, the stdout captured so far may be lost, so I'm checking how `TimeoutExpired` exposes it.

Now I'm checking the stdin handling: the child process inherits the parent's stdin, so a command like `git commit` without `-m` or an `npx` prompt can hang for the full timeout and swallow keystrokes, and setting stdin to DEVNULL fixes it. I'm also noting that invalid UTF-8 output currently crashes the call and loses the exit code, which `errors="replace"` would prevent.

Next I'm looking at the API key exposure: the tool environment inherits the LLM_* variables, so a simple `env` call prints the key into the context and logs, and a prompt injection in a file could get the model to send it out. Stripping those variables from the subprocess environment would close that off. I'm also noting that the shell runs with the user's full privileges and no confirmation step, so for a showcase I'd skip building an approval system and instead document running it in a container or disposable directory.

Next I'm checking the medium-priority items: the tool-call error handling that mixes model mistakes with harness bugs, and the hardcoded sampling parameters that would break on other providers.

Now I'm going through the low-priority items: the duplicated tool list in the system prompt, the missing token budget that lets a failing loop keep burning tokens, and a few cosmetic and edge-case problems I'm leaving out.

Now I'm looking at the structure against compaction and dynamic tools: `call_llm` returns only the content and tool calls, which hides the usage and finish reason that the compaction trigger and cache metrics both depend on, so it should return the whole response. I'm also noting that the message list should stay as one lis
… [2555 more characters truncated]
````
</details>

**[agent]**

Документация DeepSeek подтверждает это требование. Пишу отчёт.

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+# Код-ревью `agent.py` (loola-test-task, HEAD 1d6d373)
+
+Ревью только для чтения: код в репо не менялся. Реального LLM нет, поэтому протокольные баги проверены фейковым OpenAI-compatible сервером со скриптованными ответами, а баги `run_bash` — прямыми вызовами функций. Артефакты: [exp/](<local path>) — [fake_server.py](<local path>), [run_scenario.sh](<local path>), `<scenario>.out` (вывод агента), `<scenario>.requests.jsonl` (что агент реально отправил в API), [bash_edge.out](<local path>).
+
+Пометки: ✅ — подтверждено экспериментом, 📄 — по документации провайдера, 🧠 — по чтению кода, без отдельного эксперимента.
+
+Общий вывод: каркас цикла правильный и для showcase хороший: история только дописывается, system prompt и tools статичны, а это уже дружелюбно к prefix cache. Но harness хрупкий ровно там, где длинная многошаговая задача неизбежно стреляет: один кривой ответ модели, один большой вывод команды или один сетевой сбой убивает всю сессию, а история в памяти теряется. Кроме того, harness не умеет отличать успех от провала и не считает токены, а без этого нельзя сделать замер «до/после», которого требует TASK.
+
+## 1. Ошибки по severity
+
+### Critical: убивают длинную задачу или ломают протокол
+
+**C1. Невалидный JSON в `arguments` роняет весь агент** — `agent.py:84` ✅
+
+`json.loads(tool_call["function"]["arguments"])` не обёрнут, исключение летит до `__main__`, и процесс падает с traceback (exit 1) после N шагов работы. Сценарии `badjson` (`'{"command": "echo hi"'`) и `emptyargs` (`arguments: ""`) оба падают на первом же ходу. Когда это стреляет в реальности: ответ обрезан по `max_tokens=4096` посреди tool call (длинный heredoc, которым модель пишет файл, — это типичный кейс для coding-агента); небольшие open-weight модели и tool-парсеры vLLM/llama.cpp иногда выдают одинарные кавычки, хвостовой мусор или пустую строку. Это ровно та ошибка, которую надо **возвращать модели** для самоисправления (вопрос 2 из TASK): записать assistant-сообщение, а в tool result отдать `Error: invalid JSON arguments: <msg>. Re-issue the call with valid JSON`. Туда же относится проверка, что после парсинга получился `dict`.
+
+**C2. Вывод тула ничем не ограничен, и контекст взрывается за один шаг** — `agent.py:41-42, 90` ✅
+
+Результат `run_bash` целиком попадает в `messages`, а обрезка до 500 символов есть только в `print`. Сценарий `bigout`: `seq 1 300000` → следующий запрос к LLM весит **2.29 MB** (сотни тысяч токенов). Дальше сервер отвечает 400 `maximum context length`, а `raise_for_status` роняет агент (сценарий `err400`). В реальной задаче это стреляет постоянно: `cat` лога или lock-файла, `npm install`, `pytest -v`, `find /`, `git log`. Даже без переполнения каждый жирный вывод навсегда остаётся в префиксе и оплачивается на каждом следующем шаге. Это не compaction, а базовая гигиена: детерминированно резать head+tail (например, по 10 KB) и ставить явный маркер `[... N bytes truncated; use head/grep/sed -n to read parts]`.
+
+**C3. Assistant-сообщение пересобирается вручную: теряются поля и дробятся параллельные вызовы** — `agent.py:63, 89` ✅ 📄
+
+Вместо того чтобы положить в историю исходный `msg`, код собирает `{"role":"assistant","content":content,"tool_calls":[tool_call]}` **на каждый** tool call. В сценарии `parallel` модель вернула одно сообщение с двумя вызовами и `reasoning_content`, а в следующем запросе ушло ([parallel.requests.jsonl](<local path>)):
+
+```
+assistant "I will check two things." tool_cal
… [13841 more characters truncated]
````

**[command]** exit=0

````
cd ~/projects/loola-test-task && git status --porcelain && git log --oneline -1; pgrep -f fake_server.py || echo "no fake servers left"
````

````
1d6d373 chore: read LLM endpoint config from env so the agent can run without editing code
2735952
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I suspect a fake server was left running, probably from a hang scenario. Its handler is sleeping, and I'd expect SIGTERM to kill it, so I'll check pid 2735952 and terminate it if it's still there.
````
</details>

**[agent]**

Репо не тронут. Один фейковый сервер остался висеть — проверяю, что это мой, и гашу.

**[command]** exit=0

````
ps -o pid,args -p 2735952; kill 2735952 2>/dev/null; sleep 0.3; pgrep -f fake_server.py || echo "clean"
````

````
PID COMMAND
2735966
````

<details><summary>reasoning</summary>

````
I'm checking whether pid 2735966 is real: ps shows it with empty args, which looks like pgrep matching its own shell, since that shell's command line contains fake_server.py. The earlier 2735952 was the same kind of self-match, so there's no leftover server process.
````
</details>

**[agent]**

Ложная тревога: `pgrep -f fake_server.py` находил мой собственный шелл, у которого эта строка есть в командной строке. Фейковых серверов не осталось.

Отчёт: [code-review.md](<local path>). Репозиторий не трогал (`git status` чистый, HEAD 1d6d373). Скрипты экспериментов и логи лежат рядом, в [exp/](<local path>).

Сам цикл устроен правильно, и prompt cache он не мешает. Но длинную задачу убивает любая мелочь: одна кривая генерация, один большой вывод команды или один сбой сети. История при этом теряется, и всё это я воспроизвёл. Плюс агент не отличает успех от провала и не считает токены, так что замерить «до/после», как требует задание, сейчас нечем.

**Critical:**
- **C1. Кривой JSON в аргументах роняет весь агент.** Если аргументы tool call — невалидный JSON или пустая строка, `json.loads` падает с traceback. Типичный случай: ответ обрезан по `max_tokens` посреди длинного heredoc.
- **C2. Вывод команды не обрезается.** После `seq 1 300000` следующий запрос весил 2.29 MB. Дальше сервер отвечает 400 из-за длины контекста, и агент падает.
- **C3. Ответ модели пересобирается вручную.** На каждый параллельный tool call создаётся отдельное сообщение, текст дублируется, а `reasoning_content` выбрасывается. DeepSeek в thinking mode из-за этого вернёт 400 уже на втором шаге: по их [документации](https://api-docs.deepseek.com/guides/thinking_mode) это поле обязательно возвращать. Исправление на самом деле упрощает код: одна строка `messages.append(msg)`.

**High:**
- **Сеть:** у запроса нет timeout (на зависшем сервере агент висит вечно), нет retry, а `raise_for_status` прячет тело ошибки — например, «maximum context length».
- **Ложный успех:** обрезанный ответ (`finish_reason=length`) и пустой ответ дают `✅ Agent finished` с exit 0.
- **Нет результата и метрик:** `usage` выбрасывается, exit code 0 даже после лимита ходов.
- **`run_bash`:**
  - stdin наследуется: `cat` прочитал stdin родителя, а `git commit` без `-m` повиснет на 120 с.
  - Команда с `server &` ждёт все 120 с и возвращает «timed out», хотя сервер запустился.
  - После таймаута дочерние процессы остаются жить.
  - Частичный вывод при таймауте теряется.
  - Невалидный UTF-8 в выводе превращается в исключение: команда успела что-то сделать, а модель не видит ни exit code, ни вывода.

**Medium:** `LLM_API_KEY` виден подпроцессу: `env` отдал ключ прямо в контекст. Широкий `except` смешивает ошибки модели с багами самого кода, а `{"command": ["ls","-la"]}` молча выполнил голый `ls`.

**Улучшения:** 7 обязательных и 6 желательных пунктов, в сумме около +40 строк. Файл вырастет примерно со 100 до 140 строк и останется в формате showcase. Самое важное — передавать сообщения модели как есть, отдавать ей ошибки аргументов как результат тула, обрезать вывод, добавить timeout и retry, явно обрабатывать провалы и считать `usage`.

**Не трогать:** фреймворки и даже `openai` SDK (сейчас видно протокол, в этом смысл showcase), Pydantic для сообщений, запасной парсер кривого JSON, approval и песочницу в коде, streaming и async, лишние тулы, разбиение на модули, tiktoken.

**Что помешает будущим задачам:**
- `call_llm` отдаёт только `(content, tool_calls)` и прячет `usage` и `cached_tokens`. Без них не будет ни триггера compaction, ни метрик кэша.
- Список `tools` нельзя менять по ходу сессии. У Qwen/vLLM он входит в system-префикс, и любое изменение — полный промах кэша. Динамическую подгрузку стоит строить так, чтобы список оставался прежним.

<details><summary>Как проверял</summary>

- Написал фейковый OpenAI-compatible сервер со скриптованными ответами, всего 11 сценариев. Он пишет каждый входящий запрос в jsonl, так что видно, что агент реально отправил в API.
- Агент запускал из venv проекта в пустой временной директории, с фейковыми `LLM_*`.
- Баги `run_bash` проверял прямыми вызовами функции, а таймаут подменил со 120 до 2 с.
- Два теста по ходу оказались ложными, их переделал:
  - dash не понимает `\x` в printf — заменил на octal-escape;
  - `pkill -f` убил мой собственный шелл — заменил на якорный паттерн `^sleep 77`.

</details>

Sources:
- [DeepSeek Thinking Mode docs](https://api-docs.deepseek.com/guides/thinking_mode)
- [n8n: DeepSeek 400 "reasoning_content must be passed back"](https://community.n8n.io/t/deepseek-ai-agent-fails-with-400-reasoning-content-must-be-passed-back-when-using-tools/299166)
- [Cursor forum: deepseek-v4-pro error report](https://forum.cursor.com/t/deepseek-v4-pro-error-report/159983)
