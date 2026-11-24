# Sub-agent: recall prior research on dynamic tools in Codex and Claude Code

Full bb session log, converted from the raw event stream: inputs, agent messages, reasoning, commands with output, file changes and tool calls (long outputs truncated to 4000 characters). Local paths, thread ids and emails are redacted; outputs that came from the developer's private projects are replaced with a placeholder.

---

## [input]

Контекст: делаем тестовое задание — минимальный coding-agent harness на Python (~/projects/loola-test-task, задание в TASK.md). Нужно реализовать динамическую подгрузку тулов, чтобы не держать десятки описаний инструментов в промпте, и не инвалидировать prompt cache (KV-cache префикса). LLM в задании — произвольный OpenAI-compatible /v1/chat/completions endpoint (вероятно self-hosted, типа vLLM).

Твоя задача (read-only, код не пиши, в проекте ничего не меняй):
1. Через скилл session-recall найди наш прошлый ресерч по динамической подгрузке тулов (tool search / deferred tools / lazy tool loading) в Codex и Claude Code. Codex мы точно ресерчили, по Claude Code не уверены. Скиллы не трогай — только тулы.
2. Собери из найденного: как механизм устроен в каждом харнессе (что лежит в промпте изначально, как модель находит и подгружает тул, куда в контекст попадает схема), какая поддержка нужна на стороне API провайдера (например Anthropic tool search tool / defer_loading / tool_reference, аналоги у OpenAI Responses API), как сохраняется prompt cache.
3. Пробелы (особенно Claude Code, если в прошлых сессиях не было) закрой свежей проверкой: официальные доки, исходники, наблюдаемое поведение. Помечай, что взято из прошлых сессий (со ссылкой @thread:...), а что проверено сейчас. Доки могут врать/устареть — где цена ошибки высокая, проверяй.
4. Отдельно ответь на гипотезу пользователя: «для динамической подгрузки на стороне провайдера моделей должна быть поддержка в API». Верно ли это? Разведи: что даёт нативная поддержка API, и как это делается чисто на стороне харнесса поверх голого OpenAI-compatible chat completions (например стабильный набор мета-тулов search/describe/call vs мутация массива tools) — и что каждый вариант делает с KV-кешем префикса (учти, что в chat templates open-source моделей tools обычно рендерятся в начало промпта).

Результат: отчёт на русском в <local path> (Markdown, абзацы без hard-wrap), в финальном ответе — краткая выжимка 10–15 строк и путь к отчёту.

<details><summary>reasoning</summary>

````
I'm starting by invoking the session-recall skill.
````
</details>

**[agent]**

Начинаю с session-recall: ищу прошлый ресерч по tool search / deferred tools.

**[tool: Skill]**

````
{
 "skill": "session-recall"
}
````

````
Launching skill: session-recall
````

**[command]** exit=0

````
cd ~; for q in "tool search" "deferred" "defer_loading" "ToolSearch" "tool_search" "динамическ тул" "lazy tool"; do echo "=== $q"; bb thread search "$q" 2>&1 | head -15; done
````

````
=== tool search
{
  "active": {
    "total": 109,
    "results": [
      {
        "thread": {
          "id": "thr_…",
          "projectId": "proj_personal",
          "environmentId": "env_fsritini2x",
          "providerId": "claude-code",
          "title": "Ресерч: dynamic tools в Pi",
          "titleFallback": "Контекст: делаем тестовое задание — минимальный coding-agent harness на Pytho...",
          "sectionId": null,
          "status": "active",
          "parentThreadId": "thr_…",
=== deferred
{
  "active": {
    "total": 48,
    "results": [
      {
        "thread": {
          "id": "thr_…",
          "projectId": "proj_personal",
          "environmentId": "env_fsritini2x",
          "providerId": "claude-code",
          "title": "Ресерч: dynamic tools в Pi",
          "titleFallback": "Контекст: делаем тестовое задание — минимальный coding-agent harness на Pytho...",
          "sectionId": null,
          "status": "active",
          "parentThreadId": "thr_…",
=== defer_loading
{
  "active": {
    "total": 19,
    "results": [
      {
        "thread": {
          "id": "thr_…",
          "projectId": "proj_personal",
          "environmentId": "env_fsritini2x",
          "providerId": "claude-code",
          "title": "Ресерч: dynamic tools в Pi",
          "titleFallback": "Контекст: делаем тестовое задание — минимальный coding-agent harness на Pytho...",
          "sectionId": null,
          "status": "active",
          "parentThreadId": "thr_…",
=== ToolSearch
{
  "active": {
    "total": 5,
    "results": [
      {
        "thread": {
          "id": "thr_…",
          "projectId": "proj_personal",
          "environmentId": "env_69kdawangu",
          "providerId": "claude-code",
          "title": "Найти и сравнить сессии в Claude и Codex",
          "titleFallback": "Найди у нас либо в клоде, либо в кодексе, сессиях, возможно в старых, сравнен...",
          "sectionId": null,
          "status": "idle",
          "parentThreadId": null,
=== tool_search
{
  "active": {
    "total": 109,
    "results": [
      {
        "thread": {
          "id": "thr_…",
          "projectId": "proj_personal",
          "environmentId": "env_fsritini2x",
          "providerId": "claude-code",
          "title": "Ресерч: dynamic tools в Pi",
          "titleFallback": "Контекст: делаем тестовое задание — минимальный coding-agent harness на Pytho...",
          "sectionId": null,
          "status": "active",
          "parentThreadId": "thr_…",
=== динамическ тул
{
  "active": {
    "total": 17,
    "results": [
      {
        "thread": {
          "id": "thr_…",
          "projectId": "proj_personal",
          "environmentId": "env_fsritini2x",
          "providerId": "claude-code",
          "title": "Ревью agent.py (Loola)",
          "titleFallback": "Контекст: тестовое задание — минимальный coding-agent harness на Python в ~/p...",
          "sectionId": null,
          "status": "active",
          "parentThreadId": "thr_…",
=== lazy tool
{
  "active": {
    "total": 16,
    "results": [
      {
        "thread": {
          "id": "thr_…",
          "projectId": "proj_personal",
          "environmentId": "env_fsritini2x",
          "providerId": "claude-code",
          "title": "Ресерч: dynamic tools в Codex и Claude Code (recall)",
          "titleFallback": "Контекст: делаем тестовое задание — минимальный coding-agent harness на Pytho...",
          "sectionId": null,
          "status": "active",
          "parentThreadId": "thr_…",
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm going to pull a compact listing of the sibling threads from the results, keeping just the id, title, updated time, and parent, and I'll use jq to shape it.
````
</details>

<details><summary>reasoning</summary>

````
Выдача заполнена свежими сиблингами этой же задачи, поэтому я составлю компактный список (id, название, дата) без детей текущего родителя.
````
</details>

**[command]** exit=0

````
cd ~; echo "self=$BB_THREAD_ID"; bb status 2>&1 | head -20; for q in "tool search" "defer_loading" "ToolSearch" "deferred tool" "lazy tool" "tool_reference" "dynamic tools" "Codex tool"; do echo "=== $q"; bb thread search "$q" --json 2>/dev/null | jq -r '(.active.results // [])[] + (.archived.results // [])[]? | [.thread.id, (.thread.updatedAt // .thread.createdAt // ""), (.thread.parentThreadId // "-"), .thread.title] | @tsv' 2>/dev/null | head -25; done
````

````
self=thr_…
Project: Personal (proj_personal)

Thread: thr_…
  Status: active
  Title: Ресерч: dynamic tools в Codex и Claude Code (recall)
  Parent: thr_…
  Parent notifications: auto
  Environment: Personal workspace (env_fsritini2x)

Data dir: <local path>
=== tool search
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793886000410	thr_…	Дизайн памяти из сессий с нуля (Fable)
thr_…	1793885999246	thr_…	Ревью дизайна session-recall (Astra)
thr_…	1793885999246	thr_…	Ревью дизайна session-recall (Astra)
thr_…	1793885999246	thr_…	Ревью дизайна session-recall (Astra)
thr_…	1793885999246	thr_…	Ревью дизайна session-recall (Astra)
thr_…	1793885999246	thr_…	Ревью дизайна session-recall (Astra)
=== defer_loading
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
=== ToolSearch
=== deferred tool
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
thr_…	1789575995513	-	
=== lazy tool
=== tool_reference
thr_…	1793885999246	thr_…	Ревью дизайна session-recall (Astra)
thr_…	1793885999246	thr_…	Ревью дизайна session-recall (Astra)
thr_…	1793885999246	thr_…	Ревью дизайна session-recall (Astra)
thr_…	1793885999246	th
… [5581 more characters truncated]
````

<details><summary>reasoning</summary>

````
The jq output doesn't match what I expected, so the results may have nested hits. I'll look at the raw JSON structure directly to see where the matches actually sit.
````
</details>

**[agent]**

jq-выражение дублирует строки — посмотрю структуру JSON и дедуплицирую.

**[command]** exit=0

````
cd ~; bb thread search "defer_loading" --json | jq 'keys, (.active|keys), (.active.results[0]|keys)'; for q in "tool search" "defer_loading" "ToolSearch" "deferred" "tool_reference" "search_tool" "dynamic tool" "Codex" ; do echo "=== $q"; bb thread search "$q" --json 2>/dev/null | jq -r '[.active.results[]?, .archived.results[]?] | map([.thread.id, (.thread.updatedAt|tostring), (.thread.parentThreadId // "-"), (.thread.title // .thread.titleFallback)] | @tsv) | unique | .[]' | grep -v thr_… | head -20; done
````

````
[redacted: output from a private project]
````

<details><summary>reasoning</summary>

````
I'm weighing a handful of candidate threads now. The strongest is the one on pi versus codex, covering skills and dynamically loading MCP. Other options I'm considering are the MCP standards retrospective, a comparison of the Agent SDK with the Anthropic SDK, and an open-source code read of hermes-agent.

I'm going to read the pi-versus-codex thread first, since it's the strongest candidate.
````
</details>

<details><summary>reasoning</summary>

````
Главный кандидат — тред «pi vs codex: скиллы и динамическая загрузка MCP» (thr_…). Затем проверю ещё четыре треда, включая thr_…, и сразу начну с основного.
````
</details>

**[command]** exit=0

````
cd ~; mkdir -p /tmp/recall && bb thread log thr_… --format minimal --all > /tmp/recall/a9az.txt; wc -c /tmp/recall/a9az.txt; head -c 6000 /tmp/recall/a9az.txt
````

````
22177 /tmp/recall/a9az.txt
── User ────────────────────────────────────────────────────
Склонируй pi и codex куда-нибудь, если их ещё нет и посмотри на отличие в реализации скиллов и мсп

── Provisioned thread ──────────────────────────────────────
  Preparing workspace
  Generating title
  Generated title (2s)
  Preparing Personal workspace…
  Preparing personal workspace…
  Using workspace: <local path>
  Provisioned thread (2s)

── Thought for 114ms ───────────────────────────────────────
  I'm going to check whether pi-mono and openai/codex are already on disk, and if not, clone them so I can compare how each one handles skills and MCP.

── Assistant ───────────────────────────────────────────────
Проверяю, есть ли уже клоны pi и codex на машине.

── Explored 1 list ─────────────────────────────────────────

── Assistant ───────────────────────────────────────────────
Есть `/tmp/codex-src/codex` (в /tmp — эфемерно), pi-клона нет. Клоню оба shallow в `~/src`.

── Ran git -C /tmp/codex-src/codex log -1 --format='%h %cd' 2>&1 | head -2; mkdir -p ~/src && cd ~/src && git clone --depth 1 https://github.com/openai/codex.git 2>&1 | tail -1 && git clone --depth 1 https://github.com/badlogic/pi-mono.git 2>&1 | tail -1; ls ~/src; git -C ~/src/codex log -1 --format='%h %cd'; git -C ~/src/pi-mono log -1 --format='%h %cd' (12s)
  $ git -C /tmp/codex-src/codex log -1 --format='%h %cd' 2>&1 | head -2; mkdir -p ~/src && cd ~/src && git clone --depth 1 https://github.com/openai/codex.git 2>&1 | tail -1 && git clone --depth 1 https://github.com/badlogic/pi-mono.git 2>&1 | tail -1; ls ~/src; git -C ~/src/codex log -1 --format='%h %cd'; git -C ~/src/pi-mono log -1 --format='%h %cd'

── Assistant ───────────────────────────────────────────────
Склонировано. Ищу, где в каждом живут skills и MCP.

── Explored 2 lists ────────────────────────────────────────

── Assistant ───────────────────────────────────────────────
Интересно: в pi появился пакет `packages/mcp` (раньше Марио принципиально был против MCP). Читаю доки и код pi.

── Ran 1 command, explored 1 file ──────────────────────────

── Assistant ───────────────────────────────────────────────
pi: собственный MCP-клиент (~4.7k строк), codemode по умолчанию. Смотрю ядро skills в pi: discovery и что попадает в промпт.

── Explored 1 search, 1 file ───────────────────────────────

── Assistant ───────────────────────────────────────────────
pi понятен. Теперь codex: crate `skills`, `core-skills`?, и MCP (`codex-mcp`, `rmcp-client`).

── Explored 1 list, 1 file ─────────────────────────────────

── Assistant ───────────────────────────────────────────────
codex skills — ~19k строк в `ext/skills` + 2.8k в `skills`: есть отдельные tools, dynamic selector с BM25, каталог-дельты. Копаю в детали.

── Explored 1 list, 3 files, 2 searches ────────────────────

── Assistant ───────────────────────────────────────────────
Skills в codex понятны. Проверяю explicit `$skill`-инъекцию и перехожу к MCP codex.

── Explored 5 searches, 1 file ─────────────────────────────

── Assistant ───────────────────────────────────────────────
Ключевое различие по exposure ясно. Последняя проверка: elicitation/sampling/prompts/approvals в обоих.

── Ran 1 command, explored 1 search ────────────────────────

── Assistant ───────────────────────────────────────────────
Склонировал в `~/src/codex` (`b1573f1`, 14.11) и `~/src/pi-mono` (`8636e21`, 14.11). Старый клон в `/tmp/codex-src` не трогал. Главное: pi сделан минималистично, всё описано в 1–2 доках и читается за вечер. Codex — платформа с телеметрией, A/B-экспер�
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
tail -c +6000 /tmp/recall/a9az.txt
````

````
иментами, облачными и enterprise-ветками.

## Skills

| | **pi** | **codex** |
|---|---|---|
| Объём кода | ~500 строк ([skills.ts](<local path>)) | ~2.8k строк в `codex-rs/skills` и ~19k в `codex-rs/ext/skills` |
| Как загружается | В системный промпт идут name, description и путь. Модель сама читает файл обычным `read` или `bash` | Тот же список, но пути сокращены через таблицу «Skill roots». Есть отдельные тулы `skills.list`, `skills.read` и `skills.installations` |
| Явный вызов | `/skill:name args`: текст SKILL.md подставляется в сообщение | `$SkillName`: SKILL.md инжектится фрагментом `<skill><name><path>…</skill>` |
| Где ищет | `~/.pi/agent/skills`, `.pi/skills`, `~/.agents/skills`, `.agents/skills` от cwd вверх до корня репо, плюс pi packages | Уровни User, Repo, System и Admin: `~/.agents/skills`, `$CODEX_HOME/skills` (устаревший путь), `.agents/skills` между корнем проекта и cwd, системные и `/etc`-скиллы, плагины, облачные скиллы через MCP-ресурсы `mcp/skill` |
| Метаданные | Только frontmatter по спеке agentskills.io, включая `disable-model-invocation` | Плюс `agents/openai.yaml`: иконки, `brand_color`, `default_prompt`, зависимости от MCP-тулов с OAuth, политика `allow_implicit_invocation` и ограничение по продуктам |
| Инструкции модели | 3 строки | Длинный регламент: «обязан использовать при совпадении», дочитать до конца, не поручать чтение субагенту, объявить, какой скилл используешь |
| Лимит на контекст | Нет | Каталог урезается по бюджету (около 8k символов): сначала описания, потом сами скиллы, с предупреждением |
| Прочее | Скиллы-дубли через симлинки отсекаются, учитывает `.gitignore` | Распознаёт «неявный вызов», когда модель сама сделала `cat SKILL.md` или запустила `scripts/`, и шлёт это в аналитику. В shadow-режиме гоняет около 10 отборщиков скиллов (BM25, n-gram, LRU, RRF): на модель пока не влияют |

## MCP

| | **pi** | **codex** |
|---|---|---|
| Реализация | Свой клиент, около 4.7k строк, из зависимостей только `cross-spawn` (пакет `@earendil-works/pi-mcp`) | Официальный Rust SDK `rmcp` и около 38k строк сверху (`codex-mcp`, `rmcp-client`) |
| Конфиг | `mcp.json` в формате Claude Code: `~/.pi/agent/` и `.pi/` (проектный читается только если проекту выдано доверие) | TOML `[mcp_servers.x]`, наложение слоёв, включая MDM и enterprise-managed |
| Транспорты | stdio и streamable HTTP. SSE отклоняется | stdio, HTTP, запуск внутри sandbox или executor, in-process |
| **Как тулы попадают к модели** | Явно и по добавлению: `exposure` = `codemode` (дефолт) / `deferred` / `direct` / `hidden`, плюс `toolExposure` по glob-маскам | По вычитанию: всё доступно, `omit_tools_from` убирает поверхности. Если модель умеет `tool_search`, тулы по умолчанию отложенные (поиск BM25), иначе отдаются сразу |
| Подтверждения (approvals) | В ядре их нет: только хуки `tool_call` у расширений. Аннотации `readOnlyHint` и подобные отдаются расширениям | Встроены: `approval_mode` = `auto` / `prompt` / `writes` / `approve`. В режиме `writes` решение принимается по аннотациям тула |
| Elicitation | Не поддерживает: по умолчанию объявляет только `roots` | Поддерживает, включая OAuth через elicitation и проверку пользователя |
| OAuth | Есть: DCR, CIMD, PRM и RFC 8414 | Есть плюс enterprise-ветка (EMA, client credentials) |
| Устойчивость | Тулы появляются по мере подключения серверов. Изменение списка серверов дописывается в конец переписки, чтобы не сбить prompt cache | Кэш каталога тулов, `startup_readiness: catalog`, флаг `required` для серверов |
| Ресурсы | `list_mcp_resources`, `list_mcp_resource_templates` и `read_mcp_resource`: имена взяты у Codex и OpenCode | Те же, но модель явно направляют искать тулы через `tool_search` |
| Своя замена | Расширение, регистрирующее `/mcp`, полностью заменяет встроенный MCP | Нет |

**Вывод:** обе системы пришли к одной схеме: тулы прямо в промпте, отложенные через `tool_search` и вызываемые из скриптов code-mode. Отличаются умолчания. pi п
… [7163 more characters truncated]
````

<details><summary>reasoning</summary>

````
Now I'm getting into the Codex specifics, starting with spec_plan.rs. I'm wondering how tool_search works in Codex alongside the Responses API, and whether it's a tool type with a defer_loading option that was added recently. I also want to check the other threads it mentions.

I'm going to check the remaining threads, starting with the ones the spec mentions, and also look for "tool_search" in the a9az thread's tool outputs. That thread is probably older than seven days, so its outputs may be cut short. There's also a parallel Pi research thread to look at, and I'll pull its contents with a search scoped to each thread.
````
</details>

<details><summary>reasoning</summary>

````
Основной прошлый ресерч по Codex и Pi найден, но деталей о том, как Codex передаёт tool_search в Responses API, там мало. Сейчас проверю остальные кандидаты.
````
</details>

**[command]** exit=0

````
cd ~; R="bun run $HOME/agent_config/skills/session-recall/recall.ts"; for t in thr_… thr_… thr_… thr_… thr_… thr_…; do echo "=== $t"; bb thread show $t --json 2>/dev/null | jq -r '.title // .titleFallback // .thread.title // .thread.titleFallback' ; $R search "defer_loading|tool_search|ToolSearch|tool_reference|deferred" --thread $t --limit 8 2>&1 | cut -c1-300 | head -20; done
````

````
=== thr_…
null
thr_…  null
  #9925 output/commandExecution 2026-08-30 13:19: … console.error(JSON.stringify({ event: "remote.client_terminal_ack_deferred", accountId: client.accountId, serverId: client.serverId, clientId: client.clientId, …
  #9706 output/commandExecution 2026-08-30 13:12: … readConsistent<T>(operation: () => T): T { assertOpen(); db.run("BEGIN DEFERRED"); try { const value = operation(); db.run("COMMIT"); return value; } catch (error) {…
  #9660 output/commandExecution 2026-08-30 13:11: … console.error(JSON.stringify({ event: "remote.client_terminal_ack_deferred", accountId: client.accountId, serverId: client.serverId, clientId: client.clientId, …
open: messages/* — bb thread log <id> --message <seq> --context 3; others — bb thread log <id> --json --after-seq <seq-1> --limit 1
=== thr_…
bb и Claude: Agent SDK vs Anthropic SDK
no matches in args,output,errors of thr_… (times UTC)
=== thr_…
MCP: что выпилили из стандарта за год
thr_…  MCP: что выпилили из стандарта за год
  #55 output/webFetch 2026-11-14 07:00: …/basic/utilities/tasks.md) to enable tracking durable requests with polling and deferred result retrieval ([SEP-1686](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686)). ## Mi…
  #35 args/toolCall 2026-11-14 07:00: …ToolSearch…
open: messages/* — bb thread log <id> --message <seq> --context 3; others — bb thread log <id> --json --after-seq <seq-1> --limit 1
=== thr_…
OSS code-read: hermes-agent
thr_…  OSS code-read: hermes-agent
  #686 output/fileChange 2026-11-14 08:44: …gent/AGENTS.md:52-54`).\n+- **Progressive disclosure для тулов [code].** `tools/tool_search.py:1-7`: MCP и плагинные тулы заменяются тремя bridge-тулами `tool_search` / `tool_describe` / `tool_call`. …
  #396 args/commandExecution 2026-11-14 08:38: …aging\"" toolsets.py | head -12; ls tools/connectors | head; sed -n 1,25p tools/tool_search.py | grep -v "^import\|^from"…
  #382 output/commandExecution 2026-11-14 08:38: …, 19- "browser_vault", # rides with the browser; deferred by default (tools.tool_search.defer) 20- "text_to_speech", 21- "todo_list", "memory", 22- "session_search", 23- "clarify", 24-…
open: messages/* — bb thread log <id> --message <seq> --context 3; others — bb thread log <id> --json --after-seq <seq-1> --limit 1
=== thr_…
Марафон: чтение ссылок агентом без Bash (PR #86)
no matches in args,output,errors of thr_… (times UTC)
=== thr_…
Найти и сравнить сессии в Claude и Codex
thr_…  Найти и сравнить сессии в Claude и Codex
  #2943 output/commandExecution 2026-09-29 21:46: …ion: MCP server `claude-in-chrome` + `claude-in-chrome` skill. Tools loaded via ToolSearch: `tabs_context_mcp`, `tabs_create_mcp`, `tabs_close_mcp`, `navigate` (+ undocumented `force`), `computer` (le…
  #2549 output/commandExecution 2026-09-29 21:00: …he `mcp__claude-in-chrome__*` tools; they may be deferred, so look them up with ToolSearch, e.g. query "chrome"). The user says it was just enabled. Do NOT use playwriter, the chrome-devtools skill, b…
  #1981 output/commandExecution 2026-09-29 14:47: …s":11551,"thinkChars":72884,"thinkBlocks":239,"toolOutChars":2106561,"byTool":{"ToolSearch":7,"Bash":16,"Write:playwriter":1,"Skill":1,"mcp__claude-in-chrome__tabs_context_mcp":7,"mcp__claude-in-chrom…
open: messages/* — bb thread log <id> --message <seq> --context 3; others — bb thread log <id> --json --after-seq <seq-1> --limit 1
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm checking how the hermes tool_search/tool_describe/tool_call bridge works, since it's relevant as a harness-only approach. I'll also look up thr_…, then run a global search for Claude Code specifics like defer_loading, tool_reference, ENABLE_TOOL_SEARCH, and tst-auto over the last 30 days.
````
</details>

<details><summary>reasoning</summary>

````
Hermes-agent — полезный пример чисто харнессного подхода с bridge-тулами search/describe/call, поэтому сейчас изучаю его находку и запускаю глобальный поиск по специфике Claude Code.
````
</details>

**[command]** exit=0

````
cd ~; bb thread log thr_… --format minimal --all > /tmp/recall/hermes.txt; grep -n -i -B2 -A8 "tool_search\|progressive disclosure для тулов\|prompt cache\|кеш\|cache" /tmp/recall/hermes.txt | head -120
````

````
152-
153-── Assistant ───────────────────────────────────────────────
154:Webhook — урезанный набор тулов (интересно для п.7). Смотрю send_message, tool_search (deferred) и connectors.
155-
156-── Explored 1 search, 1 file ───────────────────────────────
157-
158-── Assistant ───────────────────────────────────────────────
159-`send_message_tool.py` существует, а toolsets говорит «нет send_message». Проверяю регистрацию.
160-
161-── Explored 1 search, 1 file ───────────────────────────────
162-
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd ~; bb thread log thr_… --json --after-seq 685 --limit 1 | jq -r '.[0].data | tostring' | grep -o 'Progressive disclosure для тулов.\{0,1500\}' | head -5; ls ~/src 2>/dev/null; find / -maxdepth 4 -type d -name "hermes-agent" 2>/dev/null | head
````

````
Showing the oldest 1 events after seq 685; more exist. Use --after-seq 686 for the next page or --all for the whole thread.
Progressive disclosure для тулов [code].** `tools/tool_search.py:1-7`: MCP и плагинные тулы заменяются тремя bridge-тулами `tool_search` / `tool_describe` / `tool_call`. Core-тулы не откладываются.\n+- **MCP [code].** Полноценный клиент `tools/mcp_tool*.py`: OAuth, sampling, health, discovery. Есть и обратный MCP-сервер (`optional-mcps/`).\n+- **Скиллы [code].** Формат agentskills.io: `<skills>/[category/]<skill>/SKILL.md` + `references/ templates/ scripts/ assets/` (`tools/skill_manager_tool.py:4-7`). В репо 44 bundled и 141 optional `SKILL.md`. Источники — hub/marketplaces: `tools/skills_hub_github.py`, `skills_hub_clawhub.py`, `skills_hub_skillssh.py`, `skills_hub_official.py`.\n+- **Как скиллы попадают в промпт [code].** В системном промпте — индекс «name: description»: показывается 60 символов описания, по словам `agent/curator.py:288-290`. Описания вне текущего контекста схлопываются до одних имён (`agent/prompt_builder.py:1311-1330`). Полный текст подгружается тулом `skill_view` — классический progressive disclosure, как в Claude Code skills. Pinned skills грузятся целиком в stable-тир (`agent/system_prompt.py:777`).\n+- **Агент сам пишет и улучшает скиллы: да [code].**\n+  - `skill_manage` умеет create/edit/patch/delete/write_file (`tools/skill_manager_tool.py:508-596`). Read-before-write guard: патч требует свежего `skill_view` (`:560`).\n+  - Вызывается тремя путями: (1) главным агентом по guidance; (2) фоновым ревью-форком каждые ~10 tool-итераций с промптом «Be ACTIVE»; (3) curator — `agent/cura
codex
pi-mono
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm running a global search for Claude Code-specific research, matching the tool-search identifiers like ENABLE_TOOL_SEARCH, tool_reference, and defer_loading. I'll start with a 30-day window, maybe widen to 120 days, and do it all in one call.
````
</details>

**[agent]**

Теперь глобальный поиск по Claude Code-специфичным строкам (последние 30 дней, потом шире если пусто).

**[command]** exit=0

````
cd ~; R="bun run $HOME/agent_config/skills/session-recall/recall.ts"; $R search "ENABLE_TOOL_SEARCH|tool_reference|tool_search_tool|defer_loading|advanced-tool-use|tool-search-tool" --limit 30 2>&1 | cut -c1-260 | head -80
````

````
thr_…  Ресерч: dynamic tools в Pi
  #180 output/commandExecution 2026-11-24 06:57: …t branch. 9 */ 10 import { Type } from "typebox"; 11 export const TOOL_SEARCH_TOOL_NAME = "tool_search"; 12 export const DEFAULT_TOOL_SEARCH_LIMIT = 8; 13 const wordSegmenter = n…
  #158 args/commandExecution 2026-11-24 06:56: …endil-works/pi-ai/dist/api && grep -nE "additional_tools|tool_search|toolSearch|defer_loading|supportsAdditionalTools|supportsToolSearch|resolveTranscriptTools|MidConvo" openai-responses-shared.js ope…
  #147 output/commandExecution 2026-11-24 06:56: … type: "tool_removal", tool: { type: "tool_reference", name: isOAuthToken ? toClaudeCodeName(tool.name) : tool.name }, }); …
thr_…  Настройка проекта и анализ динамической
  #451 args/commandExecution 2026-11-24 06:55: …а стороне API провайдера (например Anthropic tool search tool / defer_loading / tool_reference, аналоги у OpenAI Responses API), как сохраняется prompt cache. 3. 
thr_…  Codex CLI: подписка, API-ключ и History Notes
  #786 output/commandExecution 2026-11-21 03:47: …t environment state.".to_string(), 14 strict: false, 15 defer_loading: None, 16 parameters: JsonSchema::object(BTreeMap::new(), /*required*/ None, Some(false.into()…
  #637 output/commandExecution 2026-11-20 16:52: … parameters, 137 output_schema: S::output_schema(), 138 defer_loading: None, 139 }; 140 let tool = S::with_catalog_message(tool, message); 141 ToolSpec::Na…
thr_…  pi vs codex: скиллы и динамическая загрузка MCP
  #163 output/commandExecution 2026-11-14 13:01: …ools may not have been provided to you upfront, and you should use this tool (`{TOOL_SEARCH_TOOL_NAME}`) to search for the required tools. For MCP tool discovery, always use `{TOOL_SEARCH_TOOL_NAME}` …
  #159 args/commandExecution 2026-11-14 13:01: …cd ~/src/codex/codex-rs && grep -rn 'tool_search\|ToolSearch\|defer_loading\|deferred' --include=*.rs codex-mcp/src core/src/tools 2>/dev/null | grep -v _test | head -20; echo ===NAM…
thr_…  Как устроен OpenAI dots и OSS-аналоги
  #2453 output/commandExecution 2026-11-14 11:11: …e"], "additionalProperties": false, }), defer_loading: true, }]; let mcp_tools = [ tool_info("calendar", "create_event", "Create eve…
  #2308 output/commandExecution 2026-11-14 11:09: … description: self.description.clone(), strict: false, defer_loading: None, parameters, output_schema: None, }) } fn handle<'a>(&'a sel…
  #918 output/commandExecution 2026-11-14 08:55: …s-202- strict: false, tools/src/tool_search_tests.rs-203- defer_loading: None, core/src/tools/handlers/tool_search.rs tools/src/tool_search_tests.rs core/tests/suite/search_tool.…
thr_…  Анализ сетевых задержек запросов
  #56 output/commandExecution 2026-11-02 06:27: …n-tool-changes-2026-07-01","inline-tools-2026-09-15","advisor-tool-2026-03-01","advanced-tool-use-2025-11-20","mid-conversation-system-clear-at-2026-08-21","effort-2025-11-24","dangerous-tool-use-2026…
open: messages/* — bb thread log <id> --message <seq> --context 3; others — bb thread log <id> --json --after-seq <seq-1> --limit 1
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I've spotted a few beta header names in thread thr_…, including one I'm not sure about, so I'll check those. Thread thr_…, about OpenAI dots and OSS alternatives, seems to cover Codex tool_search tests. I also want to look at the pi sibling thread, which has a "tool_removal" type.

I'm also noticing the pi sibling thread has a "tool_removal" type tied to tool_reference, which could be a new Anthropic API feature. Another thread, thr_…, is already running on this, so I won't duplicate it. Next I'll pull up event #56 in thread vvfh253nxa to get the full beta header list.
````
</details>

<details><summary>reasoning</summary>

````
В @thread:thr_… нашёл список beta-хедеров Claude Code, а в @thread:thr_… — тесты tool_search в Codex; сейчас смотрю их подробнее.
````
</details>

**[command]** exit=0

````
cd ~; bb thread log thr_… --json --after-seq 55 --limit 1 2>/dev/null | jq -r '.[0].data | tostring' | grep -o '.\{600\}advanced-tool-use.\{900\}' | head -3; echo; echo ====; bb thread log thr_… --format minimal --all 2>/dev/null | head -40
````

````
",\"id\":\"d2332c8c-95ca-41b1-9f60-38f36968a4a3\",\"timestamp\":\"2026-10-28T05:38:04.433Z\",\"version\":\"2.1.310\",\"querySource\":\"sdk\",\"shapeHash\":\"602a47c107990286ae4ed950fa4332add7c90ca5df119f67e7569de32e66a4e8\",\"params\":{\"model\":\"claude-opus-5-5\",\"betas\":[\"claude-code-20250219\",\"oauth-2025-04-20\",\"interleaved-thinking-2025-05-14\",\"thinking-token-count-2026-05-13\",\"context-management-2025-06-27\",\"prompt-caching-scope-2026-01-05\",\"per-turn-control-2026-07-01\",\"mid-conversation-tool-changes-2026-07-01\",\"inline-tools-2026-09-15\",\"advisor-tool-2026-03-01\",\"advanced-tool-use-2025-11-20\",\"mid-conversation-system-clear-at-2026-08-21\",\"effort-2025-11-24\",\"dangerous-tool-use-2026-09-03\",\"thinking-binding-controls-2026-08-01\",\"afk-mode-2026-01-31\",\"extended-cache-ttl-2025-04-11\",\"cache-diagnosis-2026-04-07\",\"message-threads-2026-08-12\"],\"max_tokens\":128000,\"thinking\":{\"type\":\"adaptive\",\"display\":\"summarized\"},\"context_management\":{\"edits\":[{\"type\":\"clear_thinking_20251015\",\"keep\":\"all\"}]},\"output_config\":{\"effort\":\"high\"}},\"base\":\"cf726a18-acac-413f-b3b8-0d77a50e25c4\",\"keep\":261,\"tail\":[\"dc4965ff1a44599d1c54f34ae58056f13d6540a28ce22d4cf0bc727796e611ef\",\"0955018e79a600e0981f7e737eb5296fd5161e043abbd14e012b56bb9ba54619\"],\"cacheControl\":[{\"path\":[\"system\",1],\"value\":{\"type\":\"ephemeral\",\"ttl\":\"1h\",\"scope\":\"global\"}},{\"path\":[\"system\",2],\"value\":{\"type\":\"ephemeral\",\"ttl\":\"1h\"
",\"id\":\"32ff9daf-d5d3-4adf-b8e6-765b56c652a7\",\"timestamp\":\"2026-10-28T05:38:09.861Z\",\"version\":\"2.1.310\",\"querySource\":\"sdk\",\"shapeHash\":\"602a47c107990286ae4ed950fa4332add7c90ca5df119f67e7569de32e66a4e8\",\"params\":{\"model\":\"claude-opus-5-5\",\"betas\":[\"claude-code-20250219\",\"oauth-2025-04-20\",\"interleaved-thinking-2025-05-14\",\"thinking-token-count-2026-05-13\",\"context-management-2025-06-27\",\"prompt-caching-scope-2026-01-05\",\"per-turn-control-2026-07-01\",\"mid-conversation-tool-changes-2026-07-01\",\"inline-tools-2026-09-15\",\"advisor-tool-2026-03-01\",\"advanced-tool-use-2025-11-20\",\"mid-conversation-system-clear-at-2026-08-21\",\"effort-2025-11-24\",\"dangerous-tool-use-2026-09-03\",\"thinking-binding-controls-2026-08-01\",\"afk-mode-2026-01-31\",\"extended-cache-ttl-2025-04-11\",\"cache-diagnosis-2026-04-07\",\"message-threads-2026-08-12\"],\"max_tokens\":128000,\"thinking\":{\"type\":\"adaptive\",\"display\":\"summarized\"},\"context_management\":{\"edits\":[{\"type\":\"clear_thinking_20251015\",\"keep\":\"all\"}]},\"output_config\":{\"effort\":\"high\"}},\"base\":\"d2332c8c-95ca-41b1-9f60-38f36968a4a3\",\"keep\":263,\"tail\":[\"54ac2f8644605c22f40287c87aefd21228b013afc13326d029fc289d8aa4d1f2\",\"36cd35aa7e5be0b63b02ab71427587a637115111f0391aefaaa2350f1c781646\"],\"cacheControl\":[{\"path\":[\"system\",1],\"value\":{\"type\":\"ephemeral\",\"ttl\":\"1h\",\"scope\":\"global\"}},{\"path\":[\"system\",2],\"value\":{\"type\":\"ephemeral\",\"ttl\":\"1h\"

====
── User ────────────────────────────────────────────────────
Слушай, есть гипотеза, что в наших агентных циклах, что кодексе, что код-кода, есть задержка не из-за того, что модель долго генерирует токены, а есть просто сетевая задержка запросов. Особенно когда контекст разрастается, да, там, например, ближе к миллиону токенов, то сам запрос именно дольше идёт, сетевой. Вот скажи, пожалуйста, есть ли у нас какие-то логи по предыдущим сессиям, которые могли бы подтвердить или опровергнуть эту гипотезу? Возможно, мы могли посмотреть, сколько именно latency у такого запроса.

── Provisioned thread ──────────────────────────────────────
  Preparing workspace
  Generating title
  Generated title (1s)
  Preparing Personal workspace…
  Preparing personal workspace…
  Using workspace: <local path>
  Provisioned thread (2s)

── Thought for 100ms ────────
… [1978 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm wondering where this data actually comes from, maybe a Claude Code request log or some cache-diagnosis telemetry from past sessions. The beta headers it shows are the interesting part: `advanced-tool-use-2025-11-20` for tool search, plus two newer ones, `mid-conversation-tool-changes-2026-07-01` and `inline-tools-2026-09-15`, which I'm still trying to place.

Still not sure about the newer betas, so I'll need to verify them. Next I'll check the OpenAI thread thr_… for how Codex and the Responses API handle tool_search.
````
</details>

<details><summary>reasoning</summary>

````
Claude Code v2.1.310 отправляет бету `advanced-tool-use-2025-11-20` (tool search / defer_loading), а две незнакомые беты, `mid-conversation-tool-changes-2026-07-01` и `inline-tools-2026-09-15`, нужно перепроверить; сейчас смотрю тред про Codex tool_search.
````
</details>

**[command]** exit=0

````
cd ~; bb thread log thr_… --format minimal --all > /tmp/recall/dots.txt; wc -c /tmp/recall/dots.txt; grep -n -i "tool_search\|defer\|tool search\|search_tool\|deferred" /tmp/recall/dots.txt | head -40
````

````
100994 /tmp/recall/dots.txt
481:  I'm checking how the final channel is handled in persistent mode, and whether there's any output-deferred setting that changes where it goes. I also need to see how the subthread and cloud thread tools fit into the picture.
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
Next I'm going to check the Codex source directly, since ~/src/codex is there and pinned to 14.11. I want to find the tool_search handler and spec_plan, and see how the tool gets serialized for the Responses API, especially whether it uses a "tool_search" type or a "defer_loading" flag on a function tool.
````
</details>

<details><summary>reasoning</summary>

````
Проверю в Codex-исходниках (клон от 14.11), как tool_search сериализуется в Responses API.
````
</details>

**[command]** exit=0

````
cd ~/src/codex && git log -1 --format='%h %cd' && cd codex-rs && grep -rln 'tool_search\|defer_loading' --include=*.rs . | grep -v test | head -40
````

````
b1573f1 Sat Nov 14 09:43:57 2026 +0000
core/src/tools/router.rs
core/src/tools/handlers/tool_search_spec.rs
core/src/tools/handlers/mcp_resource_spec.rs
core/src/tools/handlers/request_plugin_install_spec.rs
core/src/tools/handlers/multi_agents.rs
core/src/tools/handlers/extension_tools.rs
core/src/tools/handlers/request_user_input_spec.rs
core/src/tools/handlers/view_image_spec.rs
core/src/tools/context.rs
core/src/tools/parallel.rs
core/src/tools/handlers/shell_spec.rs
core/src/tools/spec_plan.rs
core/src/tools/handlers/plan_spec.rs
core/src/tools/handlers/sleep.rs
core/src/tools/handlers/send_message_to_user_async.rs
core/src/tools/tool_namespaces_info.rs
core/src/tools/handlers/multi_agents_spec.rs
core/src/tools/handlers/tool_search.rs
core/src/tools/handlers/get_context_remaining_spec.rs
core/src/tools/handlers/multi_agents/spawn.rs
core/src/tools/code_mode/wait_spec.rs
core/src/tools/handlers/multi_agents/close_agent.rs
core/src/tools/handlers/multi_agents/resume_agent.rs
core/src/tools/code_mode/execute_spec.rs
core/src/tools/handlers/request_user_input_async.rs
core/src/tools/handlers/apply_patch_spec.rs
core/src/tools/handlers/new_context_window_spec.rs
core/src/tools/handlers/wait_for_environment.rs
core/src/tools/handlers/mod.rs
core/src/tools/handlers/current_time.rs
core/src/tools/handlers/dynamic.rs
core/src/tools/handlers/list_available_plugins_to_install_spec.rs
core/src/config/mod.rs
core/src/tools/handlers/multi_agents/send_input.rs
core/src/tools/handlers/multi_agents/wait.rs
core/src/state/service.rs
core/src/session/session.rs
core/src/context_manager/normalize.rs
tools/src/lib.rs
tools/src/dynamic_tool.rs
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd ~/src/codex/codex-rs && wc -l core/src/tools/handlers/tool_search.rs core/src/tools/handlers/tool_search_spec.rs && cat core/src/tools/handlers/tool_search_spec.rs | head -120
````

````
612 core/src/tools/handlers/tool_search.rs
  221 core/src/tools/handlers/tool_search_spec.rs
  833 total
use codex_tools::JsonSchema;
use codex_tools::TOOL_SEARCH_TOOL_NAME;
use codex_tools::ToolSearchSourceInfo;
use codex_tools::ToolSpec;
use codex_utils_string::take_bytes_at_char_boundary;
use std::collections::BTreeMap;

const MAX_TOOL_SEARCH_SOURCE_DESCRIPTION_BYTES: usize = 512 * 1024;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum ToolSearchSourceListing {
    Include,
    Omit,
}

pub(crate) fn create_tool_search_tool(
    searchable_sources: &[ToolSearchSourceInfo],
    default_limit: usize,
    source_listing: ToolSearchSourceListing,
) -> ToolSpec {
    let properties = BTreeMap::from([
        (
            "query".to_string(),
            JsonSchema::string(Some("Search query for deferred tools.".to_string())),
        ),
        (
            "limit".to_string(),
            JsonSchema::number(Some(format!(
                "Maximum number of tools to return. Defaults to {default_limit}."
            ))),
        ),
    ]);

    let source_section = match source_listing {
        ToolSearchSourceListing::Include => {
            let mut source_descriptions = BTreeMap::new();
            for source in searchable_sources {
                source_descriptions
                    .entry(source.name.clone())
                    .and_modify(|existing: &mut Option<String>| {
                        if existing.is_none() {
                            *existing = source.description.clone();
                        }
                    })
                    .or_insert(source.description.clone());
            }

            let source_descriptions = if source_descriptions.is_empty() {
                "None currently enabled.".to_string()
            } else {
                let reserved_name_bytes = source_descriptions.keys().fold(
                    source_descriptions.len().saturating_sub(1),
                    |reserved, name| reserved.saturating_add(2).saturating_add(name.len()),
                );
                let mut description_budget =
                    MAX_TOOL_SEARCH_SOURCE_DESCRIPTION_BYTES.saturating_sub(reserved_name_bytes);
                let mut rendered = String::new();
                for (name, description) in source_descriptions {
                    let separator_bytes = usize::from(!rendered.is_empty());
                    let required = separator_bytes.saturating_add(2).saturating_add(name.len());
                    if required
                        > MAX_TOOL_SEARCH_SOURCE_DESCRIPTION_BYTES.saturating_sub(rendered.len())
                    {
                        continue;
                    }

                    if !rendered.is_empty() {
                        rendered.push('\n');
                    }
                    rendered.push_str("- ");
                    rendered.push_str(&name);

                    if let Some(description) = description
                        && description_budget >= 2
                    {
                        rendered.push_str(": ");
                        description_budget -= 2;
                        let bounded_description =
                            take_bytes_at_char_boundary(&description, description_budget);
                        rendered.push_str(bounded_description);
                        description_budget -= bounded_description.len();
                    }
                }
                rendered
            };
            format!(
                "\n\nYou have access to tools from the following sources:\n{source_descriptions}\n"
            )
        }
        ToolSearchSourceListing::Omit => "\n\n".to_string(),
    };

    let description = format!(
        "# Tool discovery\n\nSearches over deferred tool metadata with BM25 and exposes matching tools for the next model call.{source_section}Some of the tools may not have been provided to you upfront, and you should use this tool (`{TOOL_SEARCH_TOOL_NAME}`) to
… [913 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm noting that the ToolSearch tool uses client execution, which maps to the Responses API's tool_search type. Next I want to see how the result comes back, so I'm checking whether tool_search.rs returns a tool_search_output with a list of tools.
````
</details>

<details><summary>reasoning</summary>

````
`ToolSearch` с `execution: "client"` — нативный тул Responses API, поиск выполняет клиент через BM25. Сейчас смотрю, в каком виде возвращается результат и куда попадают схемы.
````
</details>

**[command]** exit=0

````
cd ~/src/codex/codex-rs && sed -n 1,200p core/src/tools/handlers/tool_search.rs | grep -v '^use ' | head -170
````

````
#[derive(Serialize)]
struct CodeModeSearchResult {
    name: String,
    description: String,
}

pub struct ToolSearchHandler {
    search_infos: Vec<ToolSearchInfo>,
    source_listing: ToolSearchSourceListing,
    spec: ToolSpec,
    search_embedder: Embedder,
    search_scorer: Scorer<usize>,
}

#[derive(Default)]
pub(crate) struct ToolSearchHandlerCache {
    cached: Mutex<Option<CachedToolSearchHandler>>,
}

struct CachedToolSearchHandler {
    handler: Arc<ToolSearchHandler>,
    sources: Vec<ToolSearchSource>,
}

enum ToolSearchSource {
    Immutable(Weak<dyn CoreToolRuntime>),
    Dynamic(Box<ToolSearchInfo>),
}

impl ToolSearchHandlerCache {
    #[instrument(level = "trace", skip_all)]
    pub(crate) fn get_or_build(
        &self,
        registry: &ToolRegistry,
        source_listing: ToolSearchSourceListing,
    ) -> Arc<ToolSearchHandler> {
        let sources = registry
            .entries()
            .filter(|tool| tool.exposure.is_deferred())
            .filter_map(|tool| {
                if let Some(runtime) = tool.cached_runtime() {
                    Some(ToolSearchSource::Immutable(Arc::downgrade(runtime)))
                } else {
                    registry
                        .search_info(tool)
                        .map(Box::new)
                        .map(ToolSearchSource::Dynamic)
                }
            })
            .collect::<Vec<_>>();

        {
            let cached = self.cached();
            if let Some(cached) = cached.as_ref()
                && cached.handler.source_listing == source_listing
                && Self::sources_match(&cached.sources, &sources)
            {
                return Arc::clone(&cached.handler);
            }
        }

        let search_infos = sources
            .iter()
            .filter_map(|source| match source {
                ToolSearchSource::Immutable(runtime) => {
                    runtime.upgrade().and_then(|runtime| runtime.search_info())
                }
                ToolSearchSource::Dynamic(search_info) => Some(search_info.as_ref().clone()),
            })
            .collect();

        let handler = Arc::new(ToolSearchHandler::new(search_infos, source_listing));
        let mut cached = self.cached();
        if let Some(cached) = cached.as_ref()
            && cached.handler.source_listing == source_listing
            && Self::sources_match(&cached.sources, &sources)
        {
            return Arc::clone(&cached.handler);
        }
        *cached = Some(CachedToolSearchHandler {
            handler: Arc::clone(&handler),
            sources,
        });
        handler
    }

    fn sources_match(cached_sources: &[ToolSearchSource], sources: &[ToolSearchSource]) -> bool {
        cached_sources.len() == sources.len()
            && cached_sources
                .iter()
                .zip(sources)
                .all(|(cached, current)| match (cached, current) {
                    (ToolSearchSource::Immutable(cached), ToolSearchSource::Immutable(current)) => {
                        Weak::ptr_eq(cached, current)
                    }
                    (ToolSearchSource::Dynamic(cached), ToolSearchSource::Dynamic(current)) => {
                        cached == current
                    }
                    (ToolSearchSource::Immutable(_), ToolSearchSource::Dynamic(_))
                    | (ToolSearchSource::Dynamic(_), ToolSearchSource::Immutable(_)) => false,
                })
    }

    fn cached(&self) -> std::sync::MutexGuard<'_, Option<CachedToolSearchHandler>> {
        match self.cached.lock() {
            Ok(cached) => cached,
            Err(poisoned) => poisoned.into_inner(),
        }
    }
}

impl ToolSearchHandler {
    #[instrument(
        level = "trace",
        skip_all,
        fields(search_info_count = search_infos.len())
    )]
    pub(crate) fn new(
        search_infos: Vec<ToolSearchInfo>,
        source_listing: ToolSearchSourceListing,
    ) -> Self {
        let searc
… [1453 more characters truncated]
````

**[command]** exit=0

````
cd ~/src/codex/codex-rs && grep -rn 'ToolSearch\b\|"tool_search"\|tool_search_output\|ToolSearchOutput\|ToolSearchCall\|defer_loading' --include=*.rs protocol/src tools/src codex-api/src 2>/dev/null | grep -v _test | head -40
````

````
protocol/src/models.rs:936:    ToolSearchOutput {
protocol/src/models.rs:1237:    ToolSearchCall {
protocol/src/models.rs:1323:    ToolSearchOutput {
protocol/src/models.rs:1463:            | Self::ToolSearchCall {
protocol/src/models.rs:1485:            | Self::ToolSearchOutput { .. }
protocol/src/models.rs:1501:            Self::ToolSearchCall { .. } => "tool_search_call",
protocol/src/models.rs:1505:            Self::ToolSearchOutput { .. } => "tool_search_output",
protocol/src/models.rs:1529:            | Self::ToolSearchCall { id, .. }
protocol/src/models.rs:1533:            | Self::ToolSearchOutput { id, .. }
protocol/src/models.rs:1551:            | Self::ToolSearchCall { id, .. }
protocol/src/models.rs:1555:            | Self::ToolSearchOutput { id, .. }
protocol/src/models.rs:1574:            Self::ToolSearchCall { .. } => Some("tsc"),
protocol/src/models.rs:1578:            Self::ToolSearchOutput { .. } => Some("tso"),
protocol/src/models.rs:1621:            | Self::ToolSearchOutput {
protocol/src/models.rs:1694:            | Self::ToolSearchCall {
protocol/src/models.rs:1710:            | Self::ToolSearchOutput {
protocol/src/models.rs:1761:            | Self::ToolSearchCall {
protocol/src/models.rs:1777:            | Self::ToolSearchOutput {
protocol/src/models.rs:2209:            ResponseInputItem::ToolSearchOutput {
protocol/src/models.rs:2214:            } => Self::ToolSearchOutput {
protocol/src/models.rs:4408:            ResponseItem::ToolSearchCall {
protocol/src/models.rs:4439:    fn tool_search_output_roundtrips() -> Result<()> {
protocol/src/models.rs:4440:        let input = ResponseInputItem::ToolSearchOutput {
protocol/src/models.rs:4448:                "defer_loading": true,
protocol/src/models.rs:4461:            ResponseItem::ToolSearchOutput {
protocol/src/models.rs:4470:                    "defer_loading": true,
protocol/src/models.rs:4487:                "type": "tool_search_output",
protocol/src/models.rs:4495:                    "defer_loading": true,
protocol/src/models.rs:4526:            ResponseItem::ToolSearchCall {
protocol/src/models.rs:4541:                "type": "tool_search_output",
protocol/src/models.rs:4550:            ResponseItem::ToolSearchOutput {
tools/src/tool_spec.rs:27:    #[serde(rename = "tool_search")]
tools/src/tool_spec.rs:28:    ToolSearch {
tools/src/tool_spec.rs:63:            ToolSpec::ToolSearch { .. } => "tool_search",
tools/src/tool_payload.rs:9:    ToolSearch { arguments: SearchToolCallParams },
tools/src/tool_payload.rs:17:            ToolPayload::ToolSearch { arguments } => Cow::Owned(arguments.query.clone()),
tools/src/tool_search.rs:29:                ToolSpec::ToolSearch { .. } | ToolSpec::WebSearch { .. } => {
tools/src/tool_search.rs:68:            ToolSpec::ToolSearch { .. } | ToolSpec::WebSearch { .. } => None,
tools/src/tool_search.rs:111:        ToolSpec::ToolSearch { .. } | ToolSpec::WebSearch { .. } => {
tools/src/tool_search.rs:122:                tool.defer_loading = Some(true);
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd ~/src/codex/codex-rs && sed -n 1225,1250p protocol/src/models.rs; echo ----; sed -n 1318,1335p protocol/src/models.rs; echo ----; sed -n 4435,4560p protocol/src/models.rs; echo ---; sed -n 95,135p tools/src/tool_search.rs
````

````
// The Responses API returns the function call arguments as a *string* that contains
        // JSON, not as an already‑parsed object. We keep it as a raw string here and let
        // Session::handle_function_call parse it into a Value.
        arguments: String,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        #[ts(optional)]
        encrypted_function_args: Option<Vec<String>>,
        call_id: String,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        #[ts(optional)]
        internal_chat_message_metadata_passthrough: Option<InternalChatMessageMetadataPassthrough>,
    },
    ToolSearchCall {
        #[serde(default, skip_serializing_if = "Option::is_none")]
        #[ts(optional)]
        encrypted_content: Option<String>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        #[serde(with = "OptionalWireItemId")]
        #[ts(optional, as = "Option<ResponseItemId>")]
        id: Option<ResponseItemId>,
        call_id: Option<String>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        #[ts(optional)]
        status: Option<String>,
        execution: String,
        #[ts(type = "unknown")]
----
        output: FunctionCallOutputPayload,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        #[ts(optional)]
        internal_chat_message_metadata_passthrough: Option<InternalChatMessageMetadataPassthrough>,
    },
    ToolSearchOutput {
        #[serde(default, skip_serializing_if = "Option::is_none")]
        #[serde(with = "OptionalWireItemId")]
        #[ts(optional, as = "Option<ResponseItemId>")]
        id: Option<ResponseItemId>,
        call_id: Option<String>,
        status: String,
        execution: String,
        #[ts(type = "unknown[]")]
        tools: Vec<serde_json::Value>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        #[ts(optional)]
        internal_chat_message_metadata_passthrough: Option<InternalChatMessageMetadataPassthrough>,
----
        Ok(())
    }

    #[test]
    fn tool_search_output_roundtrips() -> Result<()> {
        let input = ResponseInputItem::ToolSearchOutput {
            call_id: "search-1".to_string(),
            status: "completed".to_string(),
            execution: "client".to_string(),
            tools: vec![serde_json::json!({
                "type": "function",
                "name": "mcp__codex_apps__calendar_create_event",
                "description": "Create a calendar event.",
                "defer_loading": true,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"}
                    },
                    "required": ["title"],
                    "additionalProperties": false,
                }
            })],
        };
        assert_eq!(
            ResponseItem::from(input.clone()),
            ResponseItem::ToolSearchOutput {
                id: None,
                call_id: Some("search-1".to_string()),
                status: "completed".to_string(),
                execution: "client".to_string(),
                tools: vec![serde_json::json!({
                    "type": "function",
                    "name": "mcp__codex_apps__calendar_create_event",
                    "description": "Create a calendar event.",
                    "defer_loading": true,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"}
                        },
                        "required": ["title"],
                        "additionalProperties": false,
                    }
                })],
                internal_chat_message_metadata_passthrough: None,
            }
        );

        assert_eq!(
            serde_json::to_value(input)?,
            serde_json::json!({
                "type": "tool_se
… [4053 more characters truncated]
````

<details><summary>reasoning</summary>

````
Codex's tool search works like this: the model emits a tool_search_call, the client runs BM25 over the deferred tools, and the matching full schemas come back in a tool_search_output item that lands at the end of the conversation history, keeping the tools array and its prefix stable. I'm now checking whether deferred tools also appear in the tools array flagged with defer_loading:true, as OpenAI's docs describe it.

I'm now checking whether hosted tool search differs from the client-executed version: with server execution, all tools go in the `tools` array with `defer_loading:true` and the server does the searching. Next I want to see whether the spec plan drops deferred tools from the tools list when tool_search is on, and which models have the `supports_search_tool` capability flag.
````
</details>

<details><summary>reasoning</summary>

````
Схема Codex такая: клиент получает `tool_search_call`, делает BM25 и возвращает `tool_search_output` с полными схемами, которые попадают в историю, а не в префикс. Теперь проверю, остаются ли отложенные тулы в `tools` и как они гейтятся по модели.
````
</details>

**[command]** exit=0

````
cd ~/src/codex/codex-rs && sed -n 240,330p core/src/tools/spec_plan.rs; grep -rn 'supports_search_tool\|search_tool' --include=*.rs models-manager/src protocol/src/openai_models.rs core/src/tools/spec_plan.rs 2>/dev/null | head -15
````

````
// Disabled, denied, app-only and over-budget MCP tools are absent from this set.
        if !registered_mcp_tools.contains(&tool_name) {
            continue;
        }
        let Some(server) = mcp.config().mcp_server_catalog.server(tool.server_key()) else {
            continue;
        };
        omitted_exposures_by_tool
            .entry(tool_name)
            .or_insert_with(|| {
                let connector_omissions = (tool.server_name() == CODEX_APPS_MCP_SERVER_NAME)
                    .then_some(tool.connector_id.as_deref())
                    .flatten()
                    .and_then(|id| apps_config.as_ref()?.apps.get(id))
                    .and_then(|app| app.omit_tools_from.as_deref())
                    .unwrap_or_default();
                server
                    .config()
                    .omit_tools_from
                    .as_deref()
                    .unwrap_or_default()
                    .iter()
                    .chain(connector_omissions)
                    .copied()
                    .collect::<ToolExposures>()
            });
    }

    for tool in registry.entries_mut() {
        let tool_name = tool.runtime.tool_name();
        let Some(omitted_exposures) = omitted_exposures_by_tool.get(&tool_name) else {
            continue;
        };
        if code_mode_only_strict_3p_tools(turn_context, model_info) {
            // Ignore MCP/app omit_tools_from; eligible tools must stay deferred in exec.
            // Log conflicts without adding a warning to the model's prompt.
            if omitted_exposures.intersects(ToolExposures::DEFERRED | ToolExposures::CODE_MODE) {
                tracing::warn!(
                    tool_name = %tool_name,
                    "Ignoring MCP/app omit_tools_from because code_mode_only_strict_3p_tools is enabled"
                );
            }
            continue;
        }
        let tool_name = tool_name.with_default_namespace();

        let mut exposures = ToolExposures::ALL.difference(*omitted_exposures);
        if tool_name.namespace.as_ref().is_some_and(|namespace| {
            turn_context
                .config
                .code_mode
                .direct_only_tool_namespaces
                .contains(namespace)
        }) {
            exposures = exposures.difference(ToolExposures::DEFERRED | ToolExposures::CODE_MODE);
        }

        exposures = if model_info.supports_search_tool
            && exposures.contains(ToolExposures::DEFERRED)
            && (effective_tool_mode(turn_context, model_info) != ToolMode::CodeModeOnly
                || exposures.contains(ToolExposures::CODE_MODE))
        {
            exposures.difference(ToolExposures::DIRECT)
        } else {
            exposures.difference(ToolExposures::DEFERRED)
        };

        tool.exposure = match (
            exposures.contains(ToolExposures::DIRECT),
            exposures.contains(ToolExposures::DEFERRED),
            exposures.contains(ToolExposures::CODE_MODE),
        ) {
            (false, false, false) => ToolExposure::Hidden,
            (false, false, true) => ToolExposure::CodeModeOnly,
            (true, false, false) => ToolExposure::DirectModelOnly,
            (true, false, true) => ToolExposure::Direct,
            (false, true, false) => ToolExposure::DeferredModelOnly,
            (false, true, true) => ToolExposure::Deferred,
            (true, true, _) => unreachable!("direct and deferred exposure are mutually exclusive"),
        };
    }
}

#[cfg(test)]
#[instrument(level = "trace", skip_all)]
pub(crate) fn build_core_tool_registry(
    turn_context: &TurnContext,
    model_info: &ModelInfo,
    environments: &TurnEnvironmentSnapshot,
    mcp: &codex_mcp::McpBinding,
    tool_suggest_candidates: Option<&crate::tools::router::ToolSuggestCandidates>,
core/src/tools/spec_plan.rs:55:use crate::tools::hosted_spec::create_web_search_tool;
core/src/tools/spec_plan.rs:158:        model_info.supports_search_tool,
core/src/tools/spec_pl
… [1343 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking whether deferred tools get included in the `tools` array sent to the API, so I'll look at how tools are rendered for the request and whether they get filtered by `exposure.is_direct`. I'll also grep for `is_deferred` and `model_visible` to trace it.
````
</details>

**[command]** exit=0

````
cd ~/src/codex/codex-rs && grep -rn 'is_deferred()\|fn is_direct\|fn is_model_visible\|DeferredModelOnly' --include=*.rs core/src | grep -v test | head -20; grep -rn 'supports_search_tool' --include=*.json --include=*.rs -l . | head; grep -rn '"supports_search_tool": true' -r . 2>/dev/null | head -5
````

````
core/src/tools/router.rs:232:                tool.exposure.is_deferred()
core/src/tools/router.rs:455:            ToolExposure::DeferredModelOnly => deferred_model_only += 1,
core/src/tools/spec_plan.rs:316:            (false, true, false) => ToolExposure::DeferredModelOnly,
core/src/tools/spec_plan.rs:429:                && tool.exposure.is_deferred()
core/src/tools/spec_plan.rs:901:fn is_directly_visible(
core/src/tools/spec_plan.rs:960:                            && tool.exposure.is_deferred()
core/src/tools/registry.rs:677:            if !tool.exposure.is_deferred() || name.is_default_namespace() {
core/src/tools/tool_namespaces_info.rs:80:        let deferred = exposure.is_deferred()
core/src/tools/handlers/tool_search.rs:74:            .filter(|tool| tool.exposure.is_deferred())
core/src/thread_manager_tests.rs
core/src/tools/spec_plan.rs
core/src/tools/spec_plan_tests.rs
core/src/tools/spec_plan_strict_third_party_tests.rs
core/tests/suite/scenarios_mcp_ema.rs
core/tests/suite/auto_review.rs
core/tests/suite/scenarios_web_search.rs
core/tests/suite/tool_registration_metrics.rs
core/tests/suite/guardian_mcp_elicitation.rs
core/tests/suite/view_image.rs
models-manager/models.json:160:      "supports_search_tool": true,
models-manager/models.json:335:      "supports_search_tool": true,
models-manager/models.json:511:      "supports_search_tool": true,
models-manager/models.json:683:      "supports_search_tool": true,
models-manager/models.json:850:      "supports_search_tool": true,
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd ~/src/codex/codex-rs && sed -n 895,975p core/src/tools/spec_plan.rs; jq -r '.models[]? | [.slug, (.supports_search_tool|tostring)] | @tsv' models-manager/models.json 2>/dev/null | head -20 || grep -n '"slug"\|supports_search_tool' models-manager/models.json | head -30
````

````
&& exposure.is_available_in_code_mode()
        && codex_code_mode::is_code_mode_nested_tool(&codex_tools::code_mode_name_for_tool_name(
            tool_name,
        ))
}

fn is_directly_visible(
    turn_context: &TurnContext,
    model_info: &ModelInfo,
    tool: &RegisteredTool,
) -> bool {
    tool.exposure.is_direct()
        && !is_hidden_by_code_mode_only(
            turn_context,
            model_info,
            &tool.runtime.tool_name(),
            tool.exposure,
        )
}

fn is_excluded_from_code_mode(turn_context: &TurnContext, tool_name: &ToolName) -> bool {
    let tool_name = tool_name.clone().with_default_namespace();
    tool_name.namespace.as_ref().is_some_and(|namespace| {
        turn_context
            .config
            .code_mode
            .excluded_tool_namespaces
            .contains(namespace)
    })
}

fn prepare_function_description_prefixes(
    turn_context: &TurnContext,
    model_info: &ModelInfo,
    registry: &mut ToolRegistry,
    search_exposure: Option<ToolExposure>,
) -> CodexResult<()> {
    let model_messages = ResolvedModelMessages::from_model(model_info);
    let prefixes = model_messages.functions_namespace_functions_description_prefixes();
    let mut available_tools = Vec::new();
    if prefixes.is_some_and(|prefixes| !prefixes.is_empty()) {
        let code_mode_enabled = matches!(
            effective_tool_mode(turn_context, model_info),
            ToolMode::CodeMode | ToolMode::CodeModeOnly
        );
        let search_name = ToolName::plain(TOOL_SEARCH_TOOL_NAME);
        let search_visible = search_exposure.is_some_and(|exposure| {
            !is_hidden_by_code_mode_only(turn_context, model_info, &search_name, exposure)
                || (code_mode_enabled
                    && registry
                        .tool_policy
                        .allows(&ToolName::plain(codex_code_mode::PUBLIC_TOOL_NAME))
                    && turn_context
                        .config
                        .features
                        .enabled(Feature::CodeModeToolSearch)
                    && exposure.is_available_in_code_mode()
                    && !is_excluded_from_code_mode(turn_context, &search_name))
        });
        available_tools.extend(
            registry
                .entries()
                .filter(|tool| {
                    is_directly_visible(turn_context, model_info, tool)
                        || (search_visible
                            && tool.exposure.is_deferred()
                            && tool.runtime.search_info().is_some())
                })
                .map(|tool| tool.runtime.tool_name()),
        );
        available_tools.extend(
            code_mode_tools(turn_context, model_info, registry)
                .map(|(_, _, tool)| tool.runtime.tool_name()),
        );
        // These wrappers are generated after their inner descriptions are ready.
        if code_mode_enabled {
            available_tools.extend(
                [
                    codex_code_mode::PUBLIC_TOOL_NAME,
                    codex_code_mode::WAIT_TOOL_NAME,
                ]
gpt-6-astra	true
gpt-6.1-sol	true
gpt-6.1-terra	true
gpt-6-sol	true
gpt-6-luna	true
gpt-5.6-sol	true
gpt-5.6-terra	true
gpt-5.6-luna	true
gpt-daybreak-blue-latest	true
gpt-daybreak-red-latest	true
gpt-5.5	true
codex-auto-review	true
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm going through what the client sees: tools sent directly are only the direct ones, while deferred tools are left out of the `tools` array and handled on the client side. The model only learns which deferred tools exist from the server listing in the tool_search description, and the schemas get appended to history in the tool_search_output.

Next I'm checking how Codex handles models without `supports_search_tool`: they get all tools directly, so open-source models over chat completions just receive the full list. I also want to confirm whether Codex still supports the chat completions wire API, since I recall it being dropped.
````
</details>

<details><summary>reasoning</summary>

````
Подтверждено: в `tools` идут только direct-тулы, deferred в массиве нет, и без `supports_search_tool` Codex отдаёт всё напрямую. Далее проверю, поддерживает ли Codex chat completions для OSS-моделей.
````
</details>

**[command]** exit=0

````
cd ~/src/codex/codex-rs && grep -rn 'WireApi\b' --include=*.rs model-provider-info/src core/src/model_provider_info.rs 2>/dev/null | head -5; grep -rn 'enum WireApi' -A12 --include=*.rs . | head -20; grep -rn 'mid-conversation\|tool_reference\|defer_loading' ../docs 2>/dev/null | head
````

````
model-provider-info/src/lib.rs:117:pub enum WireApi {
model-provider-info/src/lib.rs:123:impl fmt::Display for WireApi {
model-provider-info/src/lib.rs:132:impl<'de> Deserialize<'de> for WireApi {
model-provider-info/src/lib.rs:195:    pub wire_api: WireApi,
model-provider-info/src/lib.rs:582:            wire_api: WireApi::Responses,
config/src/thread_config/proto/codex.thread_config.v1.rs:117:pub enum WireApi {
config/src/thread_config/proto/codex.thread_config.v1.rs-118-    Unspecified = 0,
config/src/thread_config/proto/codex.thread_config.v1.rs-119-    Responses = 1,
config/src/thread_config/proto/codex.thread_config.v1.rs-120-}
config/src/thread_config/proto/codex.thread_config.v1.rs-121-impl WireApi {
config/src/thread_config/proto/codex.thread_config.v1.rs-122-    /// String value of the enum field names used in the ProtoBuf definition.
config/src/thread_config/proto/codex.thread_config.v1.rs-123-    ///
config/src/thread_config/proto/codex.thread_config.v1.rs-124-    /// The values are not transformed in any way and thus are considered stable
config/src/thread_config/proto/codex.thread_config.v1.rs-125-    /// (if the ProtoBuf definition does not change) and safe for programmatic use.
config/src/thread_config/proto/codex.thread_config.v1.rs-126-    pub fn as_str_name(&self) -> &'static str {
config/src/thread_config/proto/codex.thread_config.v1.rs-127-        match self {
config/src/thread_config/proto/codex.thread_config.v1.rs-128-            Self::Unspecified => "WIRE_API_UNSPECIFIED",
config/src/thread_config/proto/codex.thread_config.v1.rs-129-            Self::Responses => "WIRE_API_RESPONSES",
model-provider-info/src/lib.rs:117:pub enum WireApi {
model-provider-info/src/lib.rs-118-    /// The Responses API exposed by OpenAI at `/v1/responses`.
model-provider-info/src/lib.rs-119-    #[default]
model-provider-info/src/lib.rs-120-    Responses,
model-provider-info/src/lib.rs-121-}
model-provider-info/src/lib.rs-122-
model-provider-info/src/lib.rs-123-impl fmt::Display for WireApi {
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
Codex only supports Responses, so that's settled. Next I'm turning to Claude Code and want to re-verify the tool search details against the official docs, including the Anthropic tool search tool and its defer_loading setting, plus the Claude Code notes on MCP tool search.

Next I want to check how Claude Code handles deferred tools. I'm actually running inside Claude Code now, and I can see a ToolSearch tool and a list of deferred tools in my own context, so I can compare what the docs say with how it works here.

Now I'm reading the part of the tool search mechanism that covers how deferred tool schemas reach the model. The tool_reference blocks get expanded into full definitions on the server side, and deferred tools sit in the tools array flagged for deferred loading, which keeps them out of the cached system prompt prefix.

Next I'm going to look at Pi's sibling research output, #147, for the API shape, since it's read-only. Then I'll check whether the local Claude Code bundle contains the relevant strings like defer_loading, tool_reference, and ENABLE_TOOL_SEARCH, so I can find the installed binary first.
````
</details>

<details><summary>reasoning</summary>

````
Codex теперь использует только Responses API, chat completions удалён. Для свежей проверки Claude Code смотрю бандл на этой машине, официальные доки и собственный опыт работы в Claude Code, а сначала ищу бандл и сверяюсь с найденным у сиблинга по Pi `tool_removal`.
````
</details>

**[command]** exit=0

````
which claude; readlink -f "$(which claude)"; claude --version 2>/dev/null; ls ~/.local/share/claude/versions 2>/dev/null | tail -3; cd ~; bb thread log thr_… --json --after-seq 146 --limit 1 2>/dev/null | jq -r '.[0].data | tostring' | grep -o '.\{1500\}tool_removal.\{1500\}' | head -c 3500
````

````
<local path>
<local path>
2.1.321 (Claude Code)
2.1.310
2.1.321
text: \"You are Claude Code, Anthropic's official CLI for Claude.\",\n                ...(cacheControl ? { cache_control: cacheControl } : {}),\n            },\n        ];\n        if (initialSystemText) {\n            params.system.push({\n                type: \"text\",\n                text: sanitizeSurrogates(initialSystemText),\n                ...(cacheControl ? { cache_control: cacheControl } : {}),\n            });\n        }\n    }\n    else if (initialSystemText) {\n        // Add cache control to system prompt for non-OAuth tokens\n        params.system = [\n            {\n                type: \"text\",\n                text: sanitizeSurrogates(initialSystemText),\n                ...(cacheControl ? { cache_control: cacheControl } : {}),\n            },\n        ];\n    }\n    // Temperature is incompatible with extended thinking and unsupported on Claude Opus 4.7+.\n    if (options?.temperature !== undefined &&\n        !options?.thinkingEnabled &&\n        model.compat?.supportsMidConvoEffort !== true &&\n        compat.supportsTemperature) {\n        params.temperature = options.temperature;\n    }\n    const toolCacheControl = compat.supportsCacheControlOnTools ? cacheControl : undefined;\n    if (nativeToolChanges) {\n        // Initial tools stay active with the cache breakpoint on the last one, followed by the\n        // placeholder. The list never changes afterwards: later tools are defined by value in\n        // `tool_addition` blocks and withdrawn by `tool_removal`, so the cached prefix survives\n        // every tool change.\n        params.tools = [...convertToolDefinitions(initialTools, toolCacheControl), DEFERRED_TOOL_PLACEHOLDER];\n    }\n    else {\n        const tools = getCurrentTools(context.messages);\n        if (tools.length > 0) {\n            params.tools = convertToolDefinitions(tools, toolCacheControl);\n        }\n    }\n    if (thinkingDisabled) {\n        // No effort is sent, so the model default applies. Anthropic rejects `block_binding`\n        // with disabled thinking.\n        params.thinking = { type: \"disabled\" };\n    }\n    else if (effortMessages) {\n        // Managed effort models use adaptive thinking so prefix mismatches can\n        // be dropped instead of surfacing as persistent 400 responses.\n        params.thinking = {\n            type: \"adaptive\",\n            display: options?.thinkingDisplay ?? \"summarized\",\n            block_binding: { prefix_mismatch_behavior: \"drop_block\" },\n        };\n        // Effort markers set the level for every reply. The top-level effort is part of the cached\n        // prompt, so it stays fixed. It is \"low\" because organizations can cap effort and reject\n        // requests containing any level above the cap.\n        params.output_config = { effort: \"low\" };\n    }\n    else if (model.reasoning && options?.thinkingEnabled) {\n        // Default to \"summarized\" so Opus 4.7 and Mythos Preview behave like\n        // older Claude 4 models (whose
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm noticing that the pi-ai Anthropic provider has a "nativeToolChanges" mode where the tool list is fixed with a deferred placeholder, and later tools get defined inline through tool_addition blocks and removed via tool_removal in messages. This is probably what the mid-conversation-tool-changes beta flag covers. It belongs to the Pi side of things, but since it's Anthropic's API, it still matters here.

Next I'm grepping the Claude Code binary, which is a compiled bun binary, so strings should work on it.
````
</details>

<details><summary>reasoning</summary>

````
Сиблинг (pi-ai, Anthropic-провайдер) использует фиксированный `tools` с `DEFERRED_TOOL_PLACEHOLDER`, а новые инструменты передаются блоками `tool_addition`/`tool_removal`, что похоже на бету `mid-conversation-tool-changes-2026-07-01`. Сейчас проверю это по бандлу Claude Code 2.1.321.
````
</details>

**[command]** exit=0

````
B=$(readlink -f ~/.local/bin/claude); ls -la $B; file $B | cut -c1-150; mkdir -p /tmp/recall/cc && strings -n 6 $B > /tmp/recall/cc/strings.txt; wc -l /tmp/recall/cc/strings.txt; grep -c 'defer_loading' /tmp/recall/cc/strings.txt; grep -o 'mid-conversation-tool-changes[-0-9]*\|inline-tools-[0-9-]*\|advanced-tool-use-[0-9-]*\|tool_search_tool_[a-z0-9_]*\|tool_addition\|tool_removal\|tool_reference\|ENABLE_TOOL_SEARCH\|DEFERRED_TOOL_PLACEHOLDER\|deferred_tool[a-z_]*' /tmp/recall/cc/strings.txt | sort | uniq -c
````

````
-rwxr-xr-x 1 bb bb 341910032 Nov  9 22:19 <local path>
<local path> ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x8
702673 /tmp/recall/cc/strings.txt
20
     27 ENABLE_TOOL_SEARCH
      2 advanced-tool-use-2025-11-20
     16 deferred_tool
      4 deferred_tool_schema_not_sent
     14 deferred_tool_use
     14 deferred_tools
     30 deferred_tools_delta
      3 deferred_tools_pool_change
      2 deferred_tools_pool_change_by_owner
     13 deferred_tools_record
      2 inline-tools-
      2 inline-tools-2026-09-15
      2 mid-conversation-tool-changes-2026-07-01
     28 tool_addition
     37 tool_reference
      6 tool_removal
      3 tool_search_tool_bm25
      3 tool_search_tool_regex
      8 tool_search_tool_result
````

<details><summary>reasoning</summary>

````
I'm going through the minified bundle now, pulling out the JavaScript around the tool-change, tool-addition, tool-search, and deferred-tools markers. The lines are very long, so I'll use grep -o with some surrounding characters to get readable fragments.
````
</details>

<details><summary>reasoning</summary>

````
Все маркеры найдены в бандле; сейчас разбираю, как включается ENABLE_TOOL_SEARCH и чем различаются `tool_addition`, `tool_reference` и `deferred_tools_delta`.
````
</details>

**[command]** exit=0

````
cd /tmp/recall/cc; grep -o '.\{400\}mid-conversation-tool-changes-2026-07-01.\{400\}' strings.txt | head -2; echo; echo =====INLINE; grep -o '.\{300\}inline-tools-2026-09-15.\{300\}' strings.txt | head -2
````

````
Command did not complete within its 120s timeout and was moved to the background (ID: bvz9ta7w1). Output is being written to: <local path> You will be notified when it completes. If it is still running after 30m in the background, it will be stopped and you will be notified. It is running now: do not start a second copy while it runs. If it is no longer needed, stop it with TaskStop. No output had been read from it when it was moved. A program that buffers its output, or a pipe into one such as tail, can keep the output file empty until the command finishes. To check interim output, use Read on that file path.
Session cwd remains <local path> directory changes made by the backgrounded command do not apply to subsequent commands.
````

<details><summary>reasoning</summary>

````
I'm thinking the regex approach with .{400} will be slow on huge lines, so a small bun or python script that finds the indices and slices the text would be better. I also need to stop the background task.
````
</details>

**[agent]**

Регексп `.{400}` на мегабайтных строках тормозит. Останавливаю и режу контекст скриптом по индексам.

**[tool: ToolSearch]**

````
{
 "query": "select:TaskStop",
 "max_results": 1
}
````

````
Matched tools: TaskStop
````

**[tool: TaskStop]**

````
{
 "task_id": "bvz9ta7w1"
}
````

````
{"message":"Successfully stopped task: bvz9ta7w1 (cd /tmp/recall/cc; grep -o '.\\{400\\}mid-conversation-tool-changes-2026-07-01.\\{400\\}' strings.txt | head -2; echo; echo =====INLINE; grep -o '.\\{300\\}inline-tools-2026-09-15.\\{300\\}' strings.txt | head -2)","task_id":"bvz9ta7w1","task_type":"local_bash","command":"cd /tmp/recall/cc; grep -o '.\\{400\\}mid-conversation-tool-changes-2026-07-01.\\{400\\}' strings.txt | head -2; echo; echo =====INLINE; grep -o '.\\{300\\}inline-tools-2026-09-15.\\{300\\}' strings.txt | head -2"}
````

**[command]** exit=0

````
mkdir -p /tmp/recall/scripts && cat > /tmp/recall/scripts/ctx.ts <<'TS'
const [file, before, after, ...needles] = Bun.argv.slice(2);
const text = await Bun.file(file).text();
for (const n of needles) {
  let i = 0, k = 0;
  const seen: number[] = [];
  while ((i = text.indexOf(n, i)) !== -1 && k < 6) {
    if (!seen.some(s => Math.abs(s - i) < 600)) {
      console.log(`\n##### ${n} @${i}\n` + text.slice(Math.max(0, i - +before), i + +after));
      seen.push(i); k++;
    }
    i += n.length;
  }
}
TS
cd /tmp/recall && timeout 100 bun run scripts/ctx.ts cc/strings.txt 500 500 'mid-conversation-tool-changes-2026-07-01' 'inline-tools-2026-09-15' | head -c 6000
````

````
##### mid-conversation-tool-changes-2026-07-01 @9382362
1-31
advisor_tool
advisor-tool-2026-03-01
cache_diagnosis
cache-diagnosis-2026-04-07
context_hint
context-hint-2026-04-09
mcp_servers
mcp-servers-2025-12-04
files_api
files-api-2025-04-14
environments
environments-2025-11-01
ccr_byoc
ccr-byoc-2025-07-29
ccr_tool_provenance
tool-provenance-2026-10-26
tool_provenance_server_url_latch(
x-cc-internal-tool-provenance-server-url
mid_conversation_system
mid-conversation-system-2026-04-07
per_message_effort
per-turn-control-2026-07-01
timing-2026-09-09
mid-conversation-tool-changes-2026-07-01
inline_tools
inline-tools-2026-09-15
server_side_fallback
server-side-fallback-2026-06-01
program_use_case_ids
program-use-case-ids-2026-09-17
server_side_fallback_category
server-side-fallback-2026-07-01
fallback_credit
fallback-credit-2026-06-01
mid_conv_cache_promotion_latch
x-cc-internal-mid-conv-cache-promotion
mid_conv_cache_promotion_ok_latch
x-cc-internal-mid-conv-cache-promotion-ok
auto_mode_classifier
auto-mode-classifier-2026-07-16
claude_code_

##### mid-conversation-tool-changes-2026-07-01 @20332452
mcp-servers-2025-12-04"),$z=P("files_api","files-api-2025-04-14"),pFs=P("environments","environments-2025-11-01"),Odn=P("ccr_byoc","ccr-byoc-2025-07-29"),EL=P("ccr_tool_provenance","tool-provenance-2026-10-26"),mFs=P("tool_provenance_server_url_latch","x-cc-internal-tool-provenance-server-url"),kL=Od("mid_conversation_system"),tnt="mid-conversation-system-2026-04-07",cV=P("per_message_effort","per-turn-control-2026-07-01"),L3=P("per_turn_timing","timing-2026-09-09"),nw=P("mid_conv_tool_change","mid-conversation-tool-changes-2026-07-01"),bS=P("inline_tools","inline-tools-2026-09-15"),Uz=P("server_side_fallback","server-side-fallback-2026-06-01"),ex=P("program_use_case_ids","program-use-case-ids-2026-09-17"),hk=P("server_side_fallback_category","server-side-fallback-2026-07-01"),uV=P("fallback_credit","fallback-credit-2026-06-01"),oNr=P("mid_conv_cache_promotion_latch","x-cc-internal-mid-conv-cache-promotion"),hFs=P("mid_conv_cache_promotion_ok_latch","x-cc-internal-mid-conv-cache-promot

##### inline-tools-2026-09-15 @9382416
sis
cache-diagnosis-2026-04-07
context_hint
context-hint-2026-04-09
mcp_servers
mcp-servers-2025-12-04
files_api
files-api-2025-04-14
environments
environments-2025-11-01
ccr_byoc
ccr-byoc-2025-07-29
ccr_tool_provenance
tool-provenance-2026-10-26
tool_provenance_server_url_latch(
x-cc-internal-tool-provenance-server-url
mid_conversation_system
mid-conversation-system-2026-04-07
per_message_effort
per-turn-control-2026-07-01
timing-2026-09-09
mid-conversation-tool-changes-2026-07-01
inline_tools
inline-tools-2026-09-15
server_side_fallback
server-side-fallback-2026-06-01
program_use_case_ids
program-use-case-ids-2026-09-17
server_side_fallback_category
server-side-fallback-2026-07-01
fallback_credit
fallback-credit-2026-06-01
mid_conv_cache_promotion_latch
x-cc-internal-mid-conv-cache-promotion
mid_conv_cache_promotion_ok_latch
x-cc-internal-mid-conv-cache-promotion-ok
auto_mode_classifier
auto-mode-classifier-2026-07-16
claude_code_side_query
claude-code-side-query-2026-09-29
dangerous

##### inline-tools-2026-09-15 @20332516
),pFs=P("environments","environments-2025-11-01"),Odn=P("ccr_byoc","ccr-byoc-2025-07-29"),EL=P("ccr_tool_provenance","tool-provenance-2026-10-26"),mFs=P("tool_provenance_server_url_latch","x-cc-internal-tool-provenance-server-url"),kL=Od("mid_conversation_system"),tnt="mid-conversation-system-2026-04-07",cV=P("per_message_effort","per-turn-control-2026-07-01"),L3=P("per_turn_timing","timing-2026-09-09"),nw=P("mid_conv_tool_change","mid-conversation-tool-changes-2026-07-01"),bS=P("inline_tools","inline-tools-2026-09-15"),Uz=P("server_side_fallback","server-side-fallback-2026-06-01"),ex=P("program_use_case_ids","program-use-case-ids-2026-09-17"),hk=P("server_side_fallback_category","server-side-fallback-2026-07-01"),uV=P("fallback_credit","fallback-credit-2026-06-01"),oNr=P("mid_conv_cache_pro
… [336 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm pinning down the variables involved here: nw tracks the mid-conversation tool change, and bS holds the inline tools. Next I'll search for where "tool_addition", "deferred_tools_delta", and the ENABLE_TOOL_SEARCH logic get used.
````
</details>

**[agent]**

Хедеры в бандле: `nw` = mid_conv_tool_change, `bS` = inline_tools. Смотрю, где формируются `tool_addition` / `tool_reference` и логику `ENABLE_TOOL_SEARCH`.

**[command]** exit=0

````
cd /tmp/recall && timeout 100 bun run scripts/ctx.ts cc/strings.txt 700 700 'type:"tool_addition"' 'type:"tool_removal"' > /tmp/recall/cc/addition.txt; wc -c cc/addition.txt; head -c 9000 cc/addition.txt
````

````
5754 cc/addition.txt

##### type:"tool_addition" @23506907
ld*xe(this,$e,"m",hl).call(this,xe(this,ht,"f").config)},bl=async function(r,s=xe(this,rt,"f").signal){if(xe(this,Wt,"f")!==void 0)return xe(this,Wt,"f");return nr(this,Wt,$y(xe(this,$e,"m",Ei).call(this),xe(this,$e,"m",gl).call(this),r,{...xe(this,rt,"f"),signal:s}),"f"),xe(this,Wt,"f")},Wc=function(){if(xe(this,Tn,"f")==="pause_turn"||xe(this,Mn,"f").length===0)return;xe(this,Re,"f").params.messages.push(xe(this,$e,"m",Sl).call(this)),nr(this,Mn,[],"f")},Sl=function(){let r=[];for(let s of xe(this,Mn,"f")){if(s.type==="removal"){r.push({type:"tool_removal",tool:{type:"tool_reference",name:s.name}});continue}let h=s.tool;if("run"in s.tool){let{run:y,parse:w,close:S,...v}=s.tool;h=v}r.push({type:"tool_addition",tool:{type:"tool_definition",definition:h}})}return{role:"system",content:r}},e})();function zc(e){if("compaction"in e&&e.compaction!=null)throw new Mr("`compaction` cannot be set on a tool runner: every request in the loop would compact again. Call `runner.compactBeforeNextTurn()` when the conversation should be compacted instead.")}function El(e){if(e.context_management?.edits?.some((n)=>n.type.startsWith("compact_")))throw new Mr("`compactBeforeNextTurn()` can't be used while `context_management` has a compaction edit, because the API doesn't accept a compaction block together with one. Remove the edit first.")}function Hy(e){let{context_management:n,stop_sequences:r,

##### type:"tool_addition" @27623947
(e,nw))yh(e,nw);q(e),e.surfacedOnWire.clear()}function q(e){if(eb(e,bS))W4s(e,bS);e.definedByValue.clear()}function OUi(e,n){if(q(e),n==="header_rejected"||n==="unsupported_on_platform"){if(rNo(),n==="header_rejected")JYe(bS)}t(`[inline-tools] tool_definition rejected (${n}) \u2014 falling back to declaring late tools in tools[] and showing them by reference, off for the rest of this conversation (carried through a compaction; /clear starts afresh)`,{level:"warn"}),c("mcp_inline_tools",`rejected_${n}`)}function MUi(e,n,o,r=[],s={}){let i=[...e?[{type:"text",text:e}]:[],...r.map((d)=>({type:"tool_removal",tool:{type:"tool_reference",name:d}})),...n.map((d)=>{let u=H0t(s,d);return u===void 0?{type:"tool_addition",tool:{type:"tool_reference",name:d}}:{type:"tool_addition",tool:{type:"tool_definition",definition:u}}})];if(o!==void 0&&i.length>0)i.push({...i.pop(),cache_control:o});return i}
export{mmo,lHn,uUi,FHe,dHn,fUi,f4,Cw,abs,pUi,mUi,cHn,lkr,hmo,MG,pen,ZJe,IHt,men,hen,gmo,lbs,ymo,JAe,hUi,QAe,wse,dbs,G_e,uHn,cbs,ubs,gUi,yUi,e7e,UHe,fHn,_Ui,gen,_mo,dkr,bUi,SUi,wUi,ckr,EUi,fbs,kUi,vUi,TUi,yen,Rmt,z_e,AUi,ukr,pHn,bmo,CUi,RUi,xUi,PUi,pbs,IUi,mbs,OUi,MUi};
// @bun @bytecode
// (c) Anthropic PBC. All rights reserved. Use is subject to the Legal Agreements outlined here: https://code.claude.com/docs/en/legal-and-compliance.
// Version: 2.1.321
import{Le}from"/$bunfs/root/chunk-xy26p6v

##### type:"tool_removal" @23506752
nded with tool calls that were not run. Call `compactBeforeNextTurn()` again if you continue the conversation."),nr(this,ht,{status:"idle"},"f");return}yield*xe(this,$e,"m",hl).call(this,xe(this,ht,"f").config)},bl=async function(r,s=xe(this,rt,"f").signal){if(xe(this,Wt,"f")!==void 0)return xe(this,Wt,"f");return nr(this,Wt,$y(xe(this,$e,"m",Ei).call(this),xe(this,$e,"m",gl).call(this),r,{...xe(this,rt,"f"),signal:s}),"f"),xe(this,Wt,"f")},Wc=function(){if(xe(this,Tn,"f")==="pause_turn"||xe(this,Mn,"f").length===0)return;xe(this,Re,"f").params.messages.push(xe(this,$e,"m",Sl).call(this)),nr(this,Mn,[],"f")},Sl=function(){let r=[];for(let s of xe(this,Mn,"f")){if(s.type==="removal"){r.push({type:"tool_removal",tool:{type:"tool_reference",name:s.name}});continue}let h=s.tool;if("run"in s.tool){let{run:y,parse:w,close:S,...v}=s.tool;h=v}r.push({type:"tool_addition",tool:{type:"tool_definition",definition:h}})}return{role:"system",content:r}},e})();function zc(e){if("compaction"in e&&e.compaction!=null)throw new Mr("`compaction` cannot be set on a too
… [1912 more characters truncated]
````

<details><summary>reasoning</summary>

````
Now I'm looking at how Claude Code 2.1.321 handles mid-conversation system messages, which can carry text blocks plus tool_removal and tool_addition entries. A tool_addition that references a tool by name means that tool is already declared in the tools list with deferred loading.

Next I'm checking how ToolSearch returns its results, specifically whether `tool_reference` blocks come back inside `tool_result`. I'm also looking at how the deferred tools list gets announced through `deferred_tools_delta` attachments, and searching around the `ENABLE_TOOL_SEARCH` and `tool_search_tool_bm25` references.
````
</details>

<details><summary>reasoning</summary>

````
Код Claude Code 2.1.321 вставляет в `messages` системные блоки `tool_addition` и `tool_removal`, а при отказе API от inline-определений переходит на объявление поздних инструментов в `tools[]` по ссылке. Дальше я разберу, как ToolSearch возвращает результат и как включается `ENABLE_TOOL_SEARCH`.
````
</details>

**[command]** exit=0

````
cd /tmp/recall && timeout 100 bun run scripts/ctx.ts cc/strings.txt 400 900 'ENABLE_TOOL_SEARCH' > cc/ets.txt; grep -c '#####' cc/ets.txt; head -c 7000 cc/ets.txt
````

````
6

##### ENABLE_TOOL_SEARCH @9146415
ACHING_SONNET
DISABLE_TELEMETRY
DISABLE_UPDATES
DISABLE_UPGRADE_COMMAND
EMBEDDED_SEARCH_TOOLS
ENABLE_BETA_TRACING_DETAILED
ENABLE_CLAUDEAI_MCP_SERVERS
ENABLE_ENHANCED_TELEMETRY_BETA
ENABLE_LOCKLESS_UPDATES
ENABLE_LSP_TOOL
ENABLE_MCP_LARGE_OUTPUT_FILES
ENABLE_PID_BASED_VERSION_LOCKING
ENABLE_PROMPT_CACHING_1H 
ENABLE_PROMPT_CACHING_1H_BEDROCK
ENABLE_SESSION_BACKGROUNDING
ENABLE_SESSION_PERSISTENCE
ENABLE_TOOL_SEARCH
FORCE_AUTOUPDATE_PLUGINS
FORCE_CODE_TERMINAL
FORCE_PROMPT_CACHING_5M
FORCE_VCR
INK_SCREEN_READER
USE_API_CONTEXT_MANAGEMENT
ALACRITTY_LOG
ALACRITTY_WINDOW_ID
ALLUSERSPROFILE
ANDROID_HOME
ANDROID_SDK_ROOT
APPDATA
APP_URL
AWS_CA_BUNDLE
AWS_EXECUTION_ENV
AWS_LAMBDA_FUNCTION_NAME
AZURE_FUNCTIONS_ENVIRONMENT
BAT_THEME
BROWSER
BUILDKITE
BUN_CHROME_PATH
BUN_INSTALL
CARGO_HTTP_CAINFO
CDPATH
CF_PAGES
CIRCLECI
CLOUDSDK_ACTIVE_CONFIG_NAME
CLOUDSDK_CONFIG
CLOUDSDK_CORE_CUSTOM_CA_CERTS_FILE
CODER_WORKSPACE_NAME
CODESPACES
COLORFGBG
COLORTERM
COMPUTERNAME
COMSPEC
CONTAINER_SANDBOX_MOUNT_POINT
CURL_CA_BUNDLE
CURSOR_TRACE_ID
ComSpec
ConEmuANSI
ConEmuPID
ConEmuTask
DAYTONA_WS_ID
DEMO_VERSION	
DENO_CERT
DENO_DEPLOYMENT_ID
DISPLAY
DO_NOT_TRACK
EDITOR
FORCE_COLOR
GCLOUD_PROJECT
GCM_INTERACTIVE
GH_CONFIG_DIR
GH_ENTERPRISE_TOKEN
GH_HOST
GH_REPO
GH_TOKEN
GITHUB_ACTIONS
GITHUB_ACTION_INPUTS
G

##### ENABLE_TOOL_SEARCH @10730881
osesInFlight
lastExecutedTabUrlByScope
resolvedUrlByToolUseId
browserRosterVersion
browserRosterChanged
noBrowserFound
relayConnectFailed
disconnectedAnswerCount
disconnectedAnswerTexts
notConnectedSeenByPriorWorker
notConnectedMirrored
chromeSetupOfferArm
chromeSetupOfferArmMirrored
chromeSetupOfferStateUnread
lastTurnClientPlatform
tool_search_optimistic_decision
[ToolSearch:optimistic] mode=
, ENABLE_TOOL_SEARCH=
, result=false
, result=true
tst-auto1
isToolSearchForceOverride: settings read failed: 
hostToolSearchEnv
lastBellAt
tengu_tranquil_starlightO
Cannot destructure property 'permissionPromptTool' from null or undefined value
--setting-sources=
Cannot destructure property 'dynamicMcpConfig' from null or undefined value
You cannot use --strict-mcp-config when an enterprise MCP config is present
You cannot dynamically configure MCP servers when an enterprise MCP config is present
allowedToolsCli
disallowedToolsCli
baseToolsCli
bgSessionPermissionRules
relaunchSessionAddDirs
dangerousPermissions
inheritedSessionDirectories
prePlanMode
Cannot destructure property 'allowedToolsCli' from null or undefined value
tengu_bg_allow_bypass_unconsented_ignored
Denying 
 also turns off the %
 tool, so Claude has neither. To use 
, set CLAUDE_CODE_USE_POWERSHELL_TOOL=1.$
tengu_ant_over

##### ENABLE_TOOL_SEARCH @11262364
on Vertex: this model's Vertex serving stack rejects the tool-search beta header (pre-4.5 generation)..
Tool search disabled: Foundry deployment for '
' does not support tool search.
Tool search disabled: ToolSearchTool is not available (may have been disallowed via disallowedTools).
Tool search disabled: this conversation has run without ToolSearch, and stays so until it is compacted or cleared. ENABLE_TOOL_SEARCH=true overrides this.
Tool search is off for this conversation: the endpoint refused it earlier in this process.
tst_enabled
Auto tool search enabled: this conversation already declared ToolSearch
auto_held
Auto tool search enabled: 
 [source: 
auto_above_threshold
Auto tool search disabled: 
auto_below_threshold
standard_mode
debugDescription
tengu_tool_search_mode_decision
checkedModel
mcpToolCount#
tengu_wire_tool_input_echo_replayed
configuredServers
ArtifactTool
/$bunfs/root/chunk-yszvd4r8.js
/$bunfs/root/chunk-kgwd6v7n.js
/$bunfs/root/chunk-5cm1gedy.js
/$bunfs/root/chunk-ba308znh.js
/$bunfs/root/chunk-ed8ps846.js
/$bunfs/root/chunk-nwm632b7.js
/$bunfs/root/chunk-r4ek29xy.js
/$bunfs/root/chunk-mqm972p6.js
/$bunfs/root/chunk-6z3hnrbs.js
/$bunfs/root/chunk-gfasgrtm.js
/$bunfs/root/chunk-dwedwjtc.js
/$bunfs/root/chunk-smvv3nk6.js
/$bunfs/root/chunk-erqs4q25
… [3139 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking the tool-search modes, which are auto (with a threshold), true, and false. On an HTTP refusal it falls back to resending the request without deferred tools. A Vertex serving stack built before 4.5 also rejects the tool-search beta. And with a custom base URL proxy, tool search is off by default, which matters here.

I'm going to check the official Claude Code and Anthropic API docs on tool search: defer_loading, tool_reference, and how mid-conversation tool changes and inline tools behave. A WebFetch should do it, and the claude-api skill might point to a reference file I can read quickly instead.
````
</details>

<details><summary>reasoning</summary>

````
ENABLE_TOOL_SEARCH уже разобран по коду: режимы auto, auto:N, true и false, отказ на Vertex до 4.5 и на Foundry, повтор без deferred-тулов при HTTP-отказе. Теперь сверяю это с официальной документацией.
````
</details>

**[tool: Skill]**

````
{
 "skill": "claude-api",
 "args": "reference lookup only: tool search tool, defer_loading, tool_reference, mid-conversation tool changes / tool_addition, inline tools, prompt caching interplay"
}
````

````
Launching skill: claude-api
````

<details><summary>reasoning</summary>

````
I'm searching through the skill files for references to tool search, tool addition, inline tools, and defer loading.
````
</details>

**[agent]**

Скилл — справочник; ищу в его файлах tool search, `tool_addition`, inline-tools и их связь с кешем.

**[command]** exit=0

````
cd <local path> && grep -rln 'defer_loading\|tool_addition\|inline-tools\|mid-conversation-tool-changes\|tool_reference' . ; echo; grep -rn 'tool_addition\|mid-conversation-tool-changes\|inline-tools-2026' shared/*.md | cut -c1-400 | head -30
````

````
shared/tool-use-concepts.md
shared/preserved-thinking-migration.md
shared/prompt-caching.md
shared/platform-availability.md
shared/model-migration.md
shared/preserved-thinking-migration/prefix_diff.py
shared/preserved-thinking-migration/causes.md
shared/cost-optimization.md
shared/latency-optimization/latency_probe.py

shared/cost-optimization.md:110:- **Not breakers, and where to put a change that is one**: setting effort explicitly to the model's default is the same as omitting it; a per-message effort change (beta) keeps the cache only where the model and the `thinking` setting the code sends both accept it, and returns a 400 otherwise (which: the per-message section of the **Effort Parameter** URL in `shared
shared/platform-availability.md:50:| &nbsp;&nbsp;Mid-conversation tool changes | beta | beta | beta | beta | No | Same models as mid-conversation system messages. By reference: beta `mid-conversation-tool-changes-2026-07-01`. By value or by reference, on the Claude API, Claude Platform on AWS and Claude Models on Google Cloud (Anthropic managed): beta `inline-tools-2026-09-15`. Bedrock: not throug
shared/preserved-thinking-migration.md:26:| 2 | Fixable | The tool set changed mid-conversation; a same-name tool's description or schema rebuilt; a per-turn reminder injected then stripped; tail state re-rendered every turn | Apply the append-only recipe (Step 3). Adding or withdrawing a tool has an append-only form (`tool_addition` / `tool_removal`, with the entry left in `tools`). A same-name d
shared/preserved-thinking-migration.md:88:The comparison ignores what the API ignores: `cache_control` markers, string content versus a single text block, leading and trailing whitespace of a text block, whitespace-only text blocks, key order, the order of tools in the array (they are compared as a name-keyed set), a `defer_loading` tool that no tool result, tool-search result, or `tool_addition` 
shared/preserved-thinking-migration.md:104:- **Modes**: does entering a mode (plan, read-only) swap the tool list or the system prompt in place? Withdraw and re-offer tools with `tool_removal` / `tool_addition`, and deliver the mode's instructions as an appended message.
shared/preserved-thinking-migration.md:179:- **Same-name tool definition changes and tools that re-list.** Under `mid-conversation-tool-changes-2026-07-01`, `tool_addition` is by reference, so it cannot express "the same tool, now with a different description", and a connector whose tool list changes on reconnect has no natural append-only form. Strictly, one exists - declare the revised tool unde
shared/preserved-thinking-migration.md:197:**Declare the initial tool set at the start; never edit an entry; surface late tools and withdrawals by reference.** For a small fixed set, build the full `tools` array before the first request, with `defer_loading: true` on tools that may not be ready; store the array as sent and replay it. For a large catalogue the model will mostly never use, leave not
shared/preserved-thinking-migration.md:199:**With the tool search tool in the request, keep a tool out of `tools` until it is available.** Search can find and call a deferred tool (the Tool search page), so append the tool with `defer_loading: true` and a `tool_addition` block on the turn it becomes available.
shared/preserved-thinking-migration.md:209:**Where the product can use one of two newer betas, its append-only form is one more scheme to measure**: `compact-2026-09-04` (on-demand compaction; the docs don't list this form for Amazon Bedrock, so treat it as not available there - the Compaction and preserved thinking page names its models and platforms) for background and keep-tail compaction, `inl
shared/preserved-thinking-migration.md:215:**When no natural append-only form exists for a shape** - keep-tail or background compaction without the `compact-2026-09-04` beta, a same-name tool definition change or a connector that re-lists without the `inline-tools-2026-09-15` beta (the r
… [7334 more characters truncated]
````

**[command]** exit=0

````
cd <local path> && grep -n -i 'tool search\|defer_loading\|tool_reference' shared/tool-use-concepts.md shared/prompt-caching.md shared/agent-design.md | cut -c1-300 | head -30; echo ======; sed -n 280,320p shared/tool-use-concepts.md
````

````
shared/tool-use-concepts.md:273:## Server-Side Tools: Tool Search
shared/tool-use-concepts.md:275:The tool search tool lets Claude dynamically discover tools from large libraries without loading all definitions into the context window. Use it when you have many tools but only a few are relevant to any given request. Discovered tool schemas are appended to the requ
shared/tool-use-concepts.md:287:Both operations are content blocks on a `{"role": "system", ...}` message appended to `messages[]`. On the Claude API, Claude Platform on AWS and Claude Models on Google Cloud (Anthropic managed), `inline-tools-2026-09-15` covers these changes too, and a `tool_additio
shared/tool-use-concepts.md:292:    {"type": "tool_removal", "tool": {"type": "tool_reference", "name": "get_weather"}},
shared/tool-use-concepts.md:295:# Addition - surfaces a tool declared up front with defer_loading.
shared/tool-use-concepts.md:297:    {"type": "tool_addition", "tool": {"type": "tool_reference", "name": "get_forecast"}},
shared/tool-use-concepts.md:301:**A tool you add by reference must already be declared in `tools[]`, with `"defer_loading": True` if it starts hidden.** Deferred tools are known to the request but not loaded into the model's context until a `tool_addition` surfaces them:
shared/tool-use-concepts.md:309:     "defer_loading": True},
shared/tool-use-concepts.md:319:**Choosing between this and tool search:** tool search is for *discovery* - Claude finds what it needs from a large library on its own. Mid-conversation tool changes are for *control* - your application decides the tool set has changed (a mode switch, a resource that 
shared/agent-design.md:68:| **Tool search** | Many tools available, but only a few relevant per request. Don't want all schemas in context upfront. | Claude searches the tool set and loads only relevant schemas. Tool definitions are appended, not swapped - preserves cache (see Caching below). |
shared/agent-design.md:95:| Adding/removing tools mid-session invalidates the cache. | Use **tool search** for dynamic discovery - it appends tool schemas rather than swapping them, so the existing prefix is preserved. |
======

---

## Mid-conversation tool changes (Beta)

**Beta header `inline-tools-2026-09-15` (by value or by reference) or `mid-conversation-tool-changes-2026-07-01` (by reference; the only one on Bedrock and Vertex); Claude Opus 5, Claude Opus 5.5, Claude Opus 4.8, Claude Fable 5, Claude Fable 5.1, Claude Fable 5.2, Claude Mythos 5, Claude Mythos 5.1, Claude Mythos 5.2, Claude Sonnet 5.5, and Claude Haiku 5.5 - not Claude Sonnet 5; not available on Microsoft Foundry (availability: `shared/platform-availability.md`).** Normally `tools` is fixed for a conversation's lifetime - editing it changes the very front of the prompt prefix and invalidates the entire cache (see `prompt-caching.md` § Invalidation hierarchy). This feature lets you add and remove tools between turns while the cached prefix survives.

Both operations are content blocks on a `{"role": "system", ...}` message appended to `messages[]`. On the Claude API, Claude Platform on AWS and Claude Models on Google Cloud (Anthropic managed), `inline-tools-2026-09-15` covers these changes too, and a `tool_addition` can carry a full definition instead (below). These examples name a tool with a `tool_reference`:

```python
# Removal - must sit immediately before an assistant message, or last in messages.
{"role": "system", "content": [
    {"type": "tool_removal", "tool": {"type": "tool_reference", "name": "get_weather"}},
]}

# Addition - surfaces a tool declared up front with defer_loading.
{"role": "system", "content": [
    {"type": "tool_addition", "tool": {"type": "tool_reference", "name": "get_forecast"}},
]}
```

**A tool you add by reference must already be declared in `tools[]`, with `"defer_loading": True` if it starts hidden.** Deferred tools are known to the request but not loaded into the model's context until a `tool_addition` surfaces the
… [2000 more characters truncated]
````

**[command]** exit=0

````
cd <local path> && sed -n 270,279p shared/tool-use-concepts.md; echo ====; sed -n 85,100p shared/agent-design.md; grep -n -i 'tool search\|Tool search' shared/live-sources.md | head
````

````
---

## Server-Side Tools: Tool Search

The tool search tool lets Claude dynamically discover tools from large libraries without loading all definitions into the context window. Use it when you have many tools but only a few are relevant to any given request. Discovered tool schemas are appended to the request, not swapped in - this preserves the prompt cache (see `agent-design.md` §Caching for Agents).

For full documentation, fetch:

- URL: `https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool`
====
---

## Caching for Agents

**Read `prompt-caching.md` first.** It covers the prefix-match invariant, breakpoint placement, the silent-invalidator audit, and why changing tools or models mid-session breaks the cache. This section covers only the agent-specific workarounds for those constraints.

| Constraint (from `prompt-caching.md`) | Agent-specific workaround |
| --- | --- |
| Editing the system prompt mid-session invalidates the cache. | Append a `{"role": "system", ...}` message to `messages[]` instead (no beta header; on supporting models - see `prompt-caching.md` § Mid-conversation system messages). The cached prefix stays intact, and the model treats it as an operator-authority instruction rather than user text. On models that don't support it, fall back to a `<system-reminder>` text block in the user turn. |
| Switching models mid-session invalidates the cache. | Spawn a **subagent** with the cheaper model for the sub-task; keep the main loop on one model. On Managed Agents that is a `multiagent` roster entry - see `managed-agents-multiagent.md`. |
| Adding/removing tools mid-session invalidates the cache. | Use **tool search** for dynamic discovery - it appends tool schemas rather than swapping them, so the existing prefix is preserved. |

For multi-turn breakpoint placement, use the combination in `prompt-caching.md` § Automatic vs explicit breakpoints: one explicit breakpoint on the static system prefix plus top-level automatic caching for the conversation tail (where automatic caching is available).

---

99:| Tool Search | `https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool.md` | "Extract tool search setup, when to use, and cache interaction" |
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm pulling up the live docs now: the tool-search-tool page, which covers the custom client-side tool search that returns tool_reference in tool_result, and the tool search section of the Claude Code MCP docs. I'll load WebFetch so I can retrieve them.
````
</details>

<details><summary>reasoning</summary>

````
Справка по скиллу подтверждает механику; сверяюсь с живой документацией по Tool search tool и разделом о tool search в Claude Code.
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
https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool.md
````

**[tool: webFetch]**

````
https://code.claude.com/docs/en/mcp
````

**[tool: webFetch]**

````
https://code.claude.com/docs/en/mcp
````

**[command]** exit=0

````
F=<local path> grep -n -i '^#.*tool search\|ENABLE_TOOL_SEARCH\|defer\|cache' $F | head -40
````

````
4:Claude Code runs the helper fresh on each connection, at session start and on reconnect, once the [trust rule for project and local-scope servers](#trust-a-folder-before-its-headershelper-runs) lets it run. It doesn't cache the result, so your script is responsible for any token reuse.
84:claude mcp add-json local-weather '{"type":"stdio","command":"/path/to/weather-cli","args":["--api-key","abc123"],"env":{"CACHE_DIR":"/tmp"}}'
532:## Scale with MCP tool search
534:Tool search keeps MCP context usage low by deferring tool definitions until Claude needs them. Only tool names and server instructions load at session start, so adding more MCP servers has minimal impact on your context window. Claude Code doesn't impose a fixed per-server tool cap; the practical limit is your context window budget.
538:> Tool search isn't supported on Microsoft Foundry [deployments hosted on Azure](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options), which reject it server-side: Claude Code detects the rejection and loads MCP tools upfront for that deployment instead. [`ENABLE_TOOL_SEARCH`](#configure-tool-search) can't override this, since the rejection comes from the deployment itself.
540:### Tool search for MCP server authors
555:Keep descriptions and instructions concise, and put critical details near the start. When tool search matches Claude's query against a tool's description, it reads only the part within the shorter limit, so put the words Claude would search for near the start too. A tool loads upfront and keeps the shorter limit whenever it isn't deferred, for example when [tool search is off](#configure-tool-search), when the tool is [marked to load upfront](#per-tool-alwaysload), or when its server is [exempt from deferral](#exempt-a-server-from-deferral).
565:#### Mark a tool to load upfront or stay deferred
567:To control how one of your server's tools loads, set `"anthropic/alwaysLoad"` in that tool's `_meta` object. The person who adds your server to Claude Code can also set [`alwaysLoad`](#exempt-a-server-from-deferral) for the whole server in their configuration, and their setting can override yours:
571:| `true` | The tool loads upfront. Startup doesn't wait for your server because of this value. The person configuring your server can still [defer all of its tools](#defer-a-servers-tools) |
572:| `false` | The tool stays deferred when their configuration sets `"alwaysLoad": true`. This applies when your server is passed with [`--mcp-config`](https://code.claude.com/docs/en/cli-reference#cli-flags), supplied by an [Agent SDK application](https://code.claude.com/docs/en/agent-sdk/mcp.md#in-code), or provided by a [plugin](#plugin-provided-mcp-servers). On other servers the tool loads upfront. Requires Claude Code v2.1.285 or later |
586:### Configure tool search
588:Tool search is enabled by default: MCP tools are deferred and discovered on demand.
590:Setting [`CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`](https://code.claude.com/docs/en/env-vars) keeps tool search off. You can't override it by setting `ENABLE_TOOL_SEARCH` yourself. On Claude Code v2.1.227 or later, your organization can keep tool search on under this variable through [managed settings](https://code.claude.com/docs/en/managed-settings.md). In a session that [gets the HIPAA configuration](https://code.claude.com/docs/en/hipaa-setup.md#check-how-developers-sign-in-and-connect), tool search is off, and neither `ENABLE_TOOL_SEARCH` nor managed settings turns it back on. [Disable pre-release capabilities](https://code.claude.com/docs/en/llm-gateway-protocol.md#disable-pre-release-capabilities) covers where the override applies and what the variable strips.
592:Claude Code uses tool search on Claude Opus 4, Claude Sonnet 4, Claude Haiku 4.5, and later models, or Opus 4.5, Sonnet 4.5, Haiku 4.5, and later models on Google Cloud's Agent Platform. On earlier models, Claude Code loads all MCP tools upfront, and `ENABLE_TOOL_SE
… [3786 more characters truncated]
````

**[command]** exit=0

````
F=<local path> sed -n 532,560p $F; sed -n 592,640p $F; sed -n 670,700p $F
````

````
## Scale with MCP tool search

Tool search keeps MCP context usage low by deferring tool definitions until Claude needs them. Only tool names and server instructions load at session start, so adding more MCP servers has minimal impact on your context window. Claude Code doesn't impose a fixed per-server tool cap; the practical limit is your context window budget.

> [!NOTE]
>
> Tool search isn't supported on Microsoft Foundry [deployments hosted on Azure](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options), which reject it server-side: Claude Code detects the rejection and loads MCP tools upfront for that deployment instead. [`ENABLE_TOOL_SEARCH`](#configure-tool-search) can't override this, since the rejection comes from the deployment itself.

### Tool search for MCP server authors

If you're building an MCP server, the server instructions field becomes more useful with tool search enabled. Server instructions help Claude understand when to search for your tools, similar to how [skills](https://code.claude.com/docs/en/skills.md) work.

Add clear, descriptive server instructions that explain:

* What category of tasks your tools handle
* When Claude should search for your tools
* Key capabilities your server provides

Claude Code cuts a tool description or server instructions that run past these default limits, and Claude sees only the text before the cut:

* **Server instructions, and the description of a tool that loads upfront**: 4,096 characters
* **The description of a tool that Claude loads through tool search**: 16,384 characters

Keep descriptions and instructions concise, and put critical details near the start. When tool search matches Claude's query against a tool's description, it reads only the part within the shorter limit, so put the words Claude would search for near the start too. A tool loads upfront and keeps the shorter limit whenever it isn't deferred, for example when [tool search is off](#configure-tool-search), when the tool is [marked to load upfront](#per-tool-alwaysload), or when its server is [exempt from deferral](#exempt-a-server-from-deferral).

Before v2.1.296, the shorter limit was 2,048 characters, and before v2.1.295 it applied to every tool description, including one loaded through tool search.

#### Change the description length limits

Claude Code uses tool search on Claude Opus 4, Claude Sonnet 4, Claude Haiku 4.5, and later models, or Opus 4.5, Sonnet 4.5, Haiku 4.5, and later models on Google Cloud's Agent Platform. On earlier models, Claude Code loads all MCP tools upfront, and `ENABLE_TOOL_SEARCH=true` doesn't override this.

On Google Cloud's Agent Platform, Claude Code decides by model generation:

* **Claude Opus 4.5, Sonnet 4.5, Haiku 4.5, and later**: tool search is on by default, the same as on the Anthropic API.
* **Earlier Agent Platform models**: Claude Code loads all MCP tools upfront, because their serving stacks reject the required beta header. `ENABLE_TOOL_SEARCH=true` doesn't override this.

Control tool search behavior with the `ENABLE_TOOL_SEARCH` environment variable:

| Value | Behavior |
| :- | :- |
| (unset) | All MCP tools deferred and loaded on demand. Loaded upfront on models earlier than Opus 4 and Sonnet 4, on the [earlier Agent Platform models](#configure-tool-search), and on Microsoft Foundry deployments hosted on Azure |
| `true` | MCP tools deferred, with the same fallbacks as (unset) |
| `auto` | Threshold mode. Tools that would otherwise be deferred load upfront while their definitions total under 10% of the context window. At 10% or more, tool search turns on, and those tools can [stay deferred](#tools-that-stay-deferred-below-the-threshold) even if the total falls under 10% |
| `auto:N` | Threshold mode with a custom percentage, where `N` is 0-100. For example, `auto:5` for 5% |
| `false` | All MCP tools loaded upfront, no deferral |

```bash theme={null}
# Use a custom 5% threshold
ENABLE_TOOL_SEARCH=aut
… [3027 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking whether Claude Code relies on its own client-side ToolSearch tool rather than the server-side tool search. I can see it's a custom tool that returns tool references inside tool results, and I want to confirm that by looking at how the bundle maps those results.

I'm now checking how the bundle maps ToolSearch results into `tool_reference` blocks. I also see that the deferred tool list gets announced mid-conversation as an appended attachment rather than in the system prompt, which keeps the cache intact. Built-in tools like WebFetch and TaskStop appear deferred in this session too, not only MCP tools.
````
</details>

<details><summary>reasoning</summary>

````
Claude Code-доки описывают MCP tool search (на старте видны только имена и server instructions, включается через `ENABLE_TOOL_SEARCH`, с v2.1.304 работает через гейтвей). Сейчас посмотрю в бандле, как клиентский `ToolSearch` формирует результат и что такое `deferred_tools_delta`.
````
</details>

**[command]** exit=0

````
cd /tmp/recall && timeout 100 bun run scripts/ctx.ts cc/strings.txt 600 600 'type:"tool_reference",tool_name' 'deferred_tools_delta"' 'The following deferred tools are now available' > cc/ts.txt; grep -c '#####' cc/ts.txt; head -c 9000 cc/ts.txt
````

````
9

##### type:"tool_reference",tool_name @29959509
ator manages this setting.`}if(y.length>0){let H=y.slice(0,Zm).map((Y)=>Y.name).join("; "),K=y.length>Zm?`; \u2026and ${y.length-Zm} more`:"";r+=`${r.endsWith(".")?"":"."} Note: Claude Code itself refuses these configured MCP servers because it reserves their address for its own use, so their tools are unavailable: ${H}${K}. This is not a connection failure or an administrator's setting, so retrying will not help; whoever added the entry can remove it or change its address.`}return{type:"tool_result",tool_use_id:n,content:r}}return{type:"tool_result",tool_use_id:n,content:e.matches.map((r)=>({type:"tool_reference",tool_name:r}))}}});function Gxe(e,n,r){if(!e.some(c1s))return e;let s=xNn(r);return L([...e,...n.map((h)=>h.name).filter((h)=>c1s(h)&&!s.has(h))])}function wgn(e,n){try{return e.map((r)=>{if(r.type!=="deferred_tools_delta"||r.toolSearchAbsent===!0)return r;let s=new Set([...r.loadedNames??[],...r.surfacedNames??[],...r.replacedNames??[]]),h=r.addedNames.filter((y)=>n.has(y)&&!s.has(y));if(h.length===0)return r;if(!E("tengu_radiant_lemur",!1))return c("compact_names_loaded_tools","flag_off",{count:h.length}),r;return g("compact_names_loaded_tools",{count:h.length}),{...r,l

##### deferred_tools_delta" @23909837
return`${e}
${o}`}function Vht(e){return aQe(e)&&"tool_name"in e&&typeof e.tool_name==="string"}function qht(e){return typeof e==="object"&&e!==null&&"type"in e&&e.type==="tool_result"&&"content"in e&&Array.isArray(e.content)}var u=Object.freeze([]),c=new WeakMap;function Hvs(e){let o=c.get(e);if(o===void 0){let t=[];for(let n of e){if(!qht(n))continue;for(let r of n.content)if(Vht(r))t.push({toolUseId:n.tool_use_id,toolName:r.tool_name})}o=t.length===0?u:t,c.set(e,o)}return o}function ECe(e,o){let t=[];for(let n of e){if(o?.surfacedOnWire!==void 0&&n.type==="attachment"&&n.attachment.type==="deferred_tools_delta"){let s=n.attachment.surfacedNames;for(let l of Array.isArray(s)?s:[])if(typeof l==="string"&&o.surfacedOnWire.has(l))t.push({toolUseId:n.uuid,toolName:l});continue}if(n.type!=="user")continue;let r=n.message?.content;if(!Array.isArray(r))continue;for(let{toolUseId:s,toolName:l}of Hvs(r))if(typeof s==="string")t.push({toolUseId:s,toolName:l})}return t}
export{aQe,rCr,Vht,qht,Hvs,ECe};
// @bun @bytecode
// (c) Anthropic PBC. All rights reserved. Use is subject to the Legal Agreements outlined here: https://code.claude.com/docs/en/legal-and-compliance.
// Version: 2.1.321
im

##### deferred_tools_delta" @26557720
:o,...f}=d;d=f}if(!s&&"citations"in d){let{citations:o,...f}=d;d=f}return d}function z(e){return typeof e==="object"&&e!==null&&!Array.isArray(e)&&f$(e,"type")==="object"}function W(e){return{__proto__:null,...e}}function DGi(e){return rt(_(V0(e))).slice(0,16)}function ie(e){if(!Array.isArray(e))return[];return e.filter((n)=>typeof n==="object"&&n!==null&&typeof n.name==="string"&&typeof n.listing==="string"&&(typeof n.definition==="object"&&n.definition!==null||typeof n.sameAs==="string"))}function v2e(e,n=new Set){let r=new Map;for(let s of e){if(s.type!=="attachment"||s.attachment?.type!=="deferred_tools_delta"||typeof s.uuid!=="string"||n.has(s.uuid))continue;let d=new Map;for(let o of ie(s.attachment.surfacedDefinitions)){if("definition"in o){d.set(o.name,{definition:o.definition,listing:o.listing,definedIn:s.uuid});continue}let f=r.get(o.sameAs)?.get(o.name);if(f!==void 0)d.set(o.name,f)}if(d.size>0)r.set(s.uuid,d)}return r}function LGi(e){let n=new Set;for(let r of e.values())for(let s of r.keys())n.add(s);return n}function _yo(e,n){let r=v2e(e,n),s=new Map,d=new Set,o=new Map;for(let f of e){if(f.type!=="attachment"||f.attachment?.type!=="deferred_tools_delta"||typeof f.uui

##### deferred_tools_delta" @26563838
get(b);if(e.kept.has(b)||!T||!("defer_loading"in T.schema)||T.schema.defer_loading!==!0)continue;let R=h.get(b);if(R===void 0)R={schema:T.schema,isMcp:T.isMcp},h.set(b,R);f.set(k,{kind:"sent",entry:R})}}catch(o){a(o),m("mcp_kept_
… [5140 more characters truncated]
````

<details><summary>reasoning</summary>

````
I've got the key facts nailed down now. Client-side ToolSearch hands back tool_reference entries for each matched name, and deferred tool announcements get appended to the conversation as reminders that those tools are now reachable through ToolSearch. Late additions also come through as tool_addition.

Now I'm checking how open-source chat templates place tool definitions. Qwen3 puts them inside the system message, Llama 3.1 in the system or first user turn, and gpt-oss in a developer message near the top. That means changing the tools list alters the prefix, which forces a full recompute under vLLM's prefix caching, since the block hash chain invalidates everything after the change point. I'm also wondering whether vLLM supports anything like defer_loading, and I'll fetch a Qwen3 template to confirm where the tools land.

I'm weighing the open-model route: keeping the `tools` array fixed and having a `describe_tool` / `call_tool` pair, which keeps the prefix stable but loses constrained decoding for the inner arguments and adds a hop. Adding tools to the array instead would re-render the system header and invalidate the cached conversation each time, and I'm not sure some templates support tools outside the start at all.

I'm thinking about whether vLLM's hermes-style tool-call parser checks parsed names against the `tools` list. If it doesn't, a late tool described only in the conversation tail might still come back as a structured tool call. That's unverified, so I'd want to spike it before relying on it.

I'm going to check a Qwen3 chat template directly to see where the tools definitions land, since the vLLM hermes parser behavior is still unverified and I'd rather confirm the template first.
````
</details>

<details><summary>reasoning</summary>

````
Код Claude Code подтверждён: ToolSearch возвращает tool_reference, а имена deferred-тулов приходят в deferred_tools_delta. Теперь проверю, как chat templates у Qwen3, Llama 3.1 и gpt-oss рендерят `tools`.
````
</details>

**[command]** exit=0

````
mkdir -p /tmp/recall/tpl && cd /tmp/recall/tpl && for m in Qwen/Qwen3-8B openai/gpt-oss-20b NousResearch/Hermes-3-Llama-3.1-8B; do n=$(echo $m | tr / _); curl -sfL "https://huggingface.co/$m/raw/main/tokenizer_config.json" -o $n.json || curl -sfL "https://huggingface.co/$m/raw/main/chat_template.jinja" -o $n.jinja; ls -la $n.* 2>/dev/null; done
````

````
-rw-rw-r-- 1 bb bb 9732 Nov 24 10:02 Qwen_Qwen3-8B.json
-rw-rw-r-- 1 bb bb 4200 Nov 24 10:02 openai_gpt-oss-20b.json
-rw-rw-r-- 1 bb bb 55803 Nov 24 10:02 NousResearch_Hermes-3-Llama-3.1-8B.json
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd /tmp/recall/tpl && jq -r '.chat_template | if type=="array" then .[0].template else . end' Qwen_Qwen3-8B.json | head -c 900; echo; echo =====GPTOSS; curl -sfL https://huggingface.co/openai/gpt-oss-20b/raw/main/chat_template.jinja -o gptoss.jinja; grep -n 'tools\|developer' gptoss.jinja | head -20; echo ====HERMES; jq -r '.chat_template | if type=="array" then (.[] | select(.name=="tool_use") | .template) else . end' NousResearch_Hermes-3-Llama-3.1-8B.json | head -c 600
````

````
{%- if tools %}
    {{- '<|im_start|>system\n' }}
    {%- if messages[0].role == 'system' %}
        {{- messages[0].content + '\n\n' }}
    {%- endif %}
    {{- "# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>" }}
    {%- for tool in tools %}
        {{- "\n" }}
        {{- tool | tojson }}
    {%- endfor %}
    {{- "\n</tools>\n\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{\"name\": <function-name>, \"arguments\": <args-json-object>}\n</tool_call><|im_end|>\n" }}
{%- else %}
    {%- if messages[0].role == 'system' %}
        {{- '<|im_start|>system\n' + messages[0].content + '<|im_end|>\n' }}
    {%- endif %}
{%- endif %}
{%- set ns = namespace(multi_step_tool=true, last_query_index=
=====GPTOSS
2:  In addition to the normal inputs of `messages` and `tools`, this template also accepts the
4:  - "builtin_tools": A list, can contain "browser" and/or "python".
108:{%- macro render_tool_namespace(namespace_name, tools) -%}
111:    {%- for tool in tools %}
150:{%- macro render_builtin_tools(browser_tool, python_tool) -%}
207:    {%- if builtin_tools %}
209:        {%- set available_builtin_tools = namespace(browser=false, python=false) %}
210:        {%- for tool in builtin_tools %}
212:                {%- set available_builtin_tools.browser = true %}
214:                {%- set available_builtin_tools.python = true %}
217:        {{- render_builtin_tools(available_builtin_tools.browser, available_builtin_tools.python) }}
220:    {%- if tools -%}
221:        {{- "\nCalls to these tools must go to the commentary channel: 'functions'." }}
233:{#- Extract developer message #}
234:{%- if messages[0].role == "developer" or messages[0].role == "system" %}
235:    {%- set developer_message = messages[0].content %}
238:    {%- set developer_message = "" %}
242:{#- Render developer message #}
243:{%- if developer_message or tools %}
244:    {{- "<|start|>developer<|message|>" }}
====HERMES
{%- macro json_to_python_type(json_spec) %}
{%- set basic_type_map = {
    "string": "str",
    "number": "float",
    "integer": "int",
    "boolean": "bool"
} %}

{%- if basic_type_map[json_spec.type] is defined %}
    {{- basic_type_map[json_spec.type] }}
{%- elif json_spec.type == "array" %}
    {{- "list[" +  json_to_python_type(json_spec|items) + "]"}}
{%- elif json_spec.type == "object" %}
    {%- if json_spec.additionalProperties is defined %}
        {{- "dict[str, " + json_to_python_type(json_spec.additionalProperties) + ']'}}
    {%- else %}
        {{- "dict" }}
    {%- endif %}
{%
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I've confirmed that Qwen3 and gpt-oss both place tool definitions at the start, in the system or developer message. Next I want to see whether vLLM's hermes tool parser checks the called tool name against the tools in the request, so I'll look at its source on GitHub. I'm treating that as an unverified hypothesis until I've read the code.

I'll try fetching the vLLM file directly with curl, since the path might have changed. If that fails, I'll fall back to searching GitHub.
````
</details>

<details><summary>reasoning</summary>

````
Подтвердил: Qwen3 кладёт `tools` в начало system-сообщения, gpt-oss — в developer-сообщение. Теперь проверю, фильтрует ли vLLM-парсер tool calls по именам из `tools`.
````
</details>

**[command]** exit=0

````
cd /tmp/recall && for p in vllm/tool_parsers/hermes_tool_parser.py vllm/entrypoints/openai/tool_parsers/hermes_tool_parser.py; do curl -sfL "https://raw.githubusercontent.com/vllm-project/vllm/main/$p" -o hermes_parser.py && echo "found $p" && break; done; wc -l hermes_parser.py 2>/dev/null; grep -n 'request.tools\|tools\b' hermes_parser.py | head -20
````

````
found vllm/tool_parsers/hermes_tool_parser.py
274 hermes_parser.py
43:    def __init__(self, tokenizer: TokenizerLike, tools: list[Tool] | None = None):
44:        super().__init__(tokenizer, tools)
63:        if request.tools and request.tool_choice != "none":
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd /tmp/recall && sed -n 55,130p hermes_parser.py
````

````
# Streaming state: what has been sent to the client.
        self._sent_content_idx: int = 0

    def adjust_request(
        self, request: ChatCompletionRequest | ResponsesRequest
    ) -> ChatCompletionRequest | ResponsesRequest:
        request = super().adjust_request(request)
        if request.tools and request.tool_choice != "none":
            # do not skip special tokens because the tool_call tokens are
            # marked "special" in some models. Since they are skipped
            # prior to the call to the tool parser, it breaks tool calling.
            request.skip_special_tokens = False
        return request

    def extract_tool_calls(
        self,
        model_output: str,
        request: ChatCompletionRequest,
    ) -> ExtractedToolCallInformation:
        # sanity check; avoid unnecessary processing
        if self.tool_call_start_token not in model_output:
            return ExtractedToolCallInformation(
                tools_called=False, tool_calls=[], content=model_output
            )

        else:
            try:
                # there are two possible captures - between tags, or between a
                # tag and end-of-string so the result of
                # findall is an array of tuples where one is a function call and
                # the other is None
                function_call_tuples = self.tool_call_regex.findall(model_output)

                # load the JSON, and then use it to build the Function and
                # Tool Call
                raw_function_calls = [
                    json.loads(match[0] if match[0] else match[1])
                    for match in function_call_tuples
                ]
                tool_calls = [
                    ToolCall(
                        type="function",
                        function=FunctionCall(
                            name=function_call["name"],
                            # function call args are JSON but as a string
                            arguments=json.dumps(
                                function_call["arguments"], ensure_ascii=False
                            ),
                        ),
                    )
                    for function_call in raw_function_calls
                ]

                content = model_output[: model_output.find(self.tool_call_start_token)]
                return ExtractedToolCallInformation(
                    tools_called=True,
                    tool_calls=tool_calls,
                    content=content if content else None,
                )

            except Exception:
                logger.exception("Error in extracting tool call from response.")
                return ExtractedToolCallInformation(
                    tools_called=False, tool_calls=[], content=model_output
                )

    def _extract_content(self, current_text: str) -> str | None:
        """Return unsent non-tool-call text, or None.

        Holds back any suffix that could be a partial <tool_call> tag.
        """
        if self.tool_call_start_token not in current_text:
            overlap_length = partial_tag_overlap(
                current_text, self.tool_call_start_token
            )
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I've confirmed the vLLM hermes parser doesn't check the tool name against the declared tools, so it would emit a tool call for any name as long as `tools` is non-empty and the tool-call parser is enabled. Whether the model actually calls a tool that's only described in the tail is a model-behavior question I haven't verified. I'm also noting that guided decoding with tool_choice set to required or named would constrain that, and that parser behavior varies, so I've only checked hermes. Next I'm turning to how Codex behaves in client mode after tool_search_

I'm checking whether the server renders the tool schemas at the end of the conversation after the tool_search_output, since the output item carrying the tools suggests they get appended there. I can't see the server-side rendering, so I'm considering a quick look at OpenAI's docs on tool search in the Responses API to confirm hosted versus client execution and the caching behavior.
````
</details>

<details><summary>reasoning</summary>

````
vLLM не проверяет имя вызванного тула по `tools` и распарсит любой `<tool_call>`. Теперь сверяю с официальной документацией OpenAI по `tool_search` в Responses API.
````
</details>

**[tool: webSearch]**

````

````

**[tool: webFetch]**

````
https://developers.openai.com/api/docs/guides/tools-tool-search.md
````

<details><summary>reasoning</summary>

````
I'm going to write the report now, starting with checking whether the reports directory exists under the parent thread-storage, since that's an allowed additional directory, and creating it if needed. The file goes at the recall-codex-claude-code.md path, with the planned sections: a TL;DR, then sources split between past sessions and what I've verified now, then the Codex mechanics.

Next I'm laying out the rest of the report: how Claude Code handles deferred tools across its three levels, the Pi and hermes notes, a comparison of provider APIs, and how prompt caching holds up under each approach. After that I'll weigh the user's hypothesis against the options for a bare chat completions harness.

Both native APIs, it seems, effectively append the schema to the tail of the context, which is what a harness can do with plain text too. The real difference is that the native path treats the schema as a true tool definition, so the server can enforce it and the tool stays callable by name. A harness-only setup has to choose between a `call_tool(name, args)` proxy that always works but loses typing at the API level, or calling by name if the parser permits it.

Now I'm noting a few observations from my own session: my context opens with a list of deferred tool names, including built-in tools as well as MCP ones, so Claude Code seems to defer rarely used built-ins too, though the docs only mention MCP. I'll also record the `select:<name>` ToolSearch form and the `<functions>` block it returns, which looks like how expanded tool references reach the model, and the later "MCP server still connecting" notice.

The next fragment is just a word ending a sentence, so there's no new step to summarize beyond what's already covered.
````
</details>

**[agent]**

Данных достаточно, пишу отчёт.

**[command]** exit=0

````
mkdir -p <local path> && ls <local path>
````

````
code-review.md
exp
pi-dynamic-tools.md
````

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+# Динамическая подгрузка тулов: Codex и Claude Code (recall + свежая проверка)
+
+Дата: 2026-11-24. Метки источников: **[past]** — из прошлых сессий (со ссылкой на тред), **[code-now]** — проверено сейчас по исходникам/бинарю, **[docs-now]** — официальные доки, прочитанные сейчас, **[obs-now]** — наблюдаемое поведение (в том числе изнутри этой сессии Claude Code), **[hypothesis]** — не проверено, нужен спайк.
+
+## TL;DR
+
+- Оба харнесса делают одно и то же: в промпте изначально только «каталог» (имена или список источников) плюс один тул поиска; модель ищет, найденные схемы **дописываются в хвост истории**, а не в массив `tools` в начале промпта. Поэтому префикс (и KV/prompt-кеш) не ломается.
+- В обоих случаях поиск **исполняется на клиенте** (BM25 в харнессе), но «развернуть найденную схему в настоящий тул посреди диалога» делает **API провайдера**: у OpenAI — item `tool_search_output` с полными схемами (Responses API, `execution: "client"`), у Anthropic — блоки `tool_reference` внутри обычного `tool_result`, которые сервер раскрывает в определения из `tools[]` с `defer_loading: true`.
+- Гипотеза «нужна поддержка в API» — **верна наполовину**. Нативная поддержка нужна, чтобы найденный тул стал *полноценным нативным тулом* (модель обучена на этом формате, сервер валидирует имя/схему, strict-грамматика), не ломая кеш. Но сама динамическая подгрузка без потери кеша делается **чисто в харнессе** поверх голого chat completions: стабильный набор мета-тулов (`search_tools` / `describe_tool` / `call_tool`), схемы приходят текстом в tool result. Этим путём идут hermes-agent и codemode в pi.
+- Для нашего тестового (OpenAI-compatible, скорее всего vLLM): массив `tools` **трогать нельзя**. В chat templates Qwen3 и gpt-oss тулы рендерятся в самое начало (system/developer), поэтому любое изменение `tools` = полный пересчёт префикса всего диалога. Рекомендация: фиксированный маленький набор core-тулов плюс мета-тулы, каталог и схемы идут через tool results.
+
+## Что нашлось в прошлых сессиях
+
+| Тред | Что там | Полезность |
+|---|---|---|
+| @thread:thr_… «pi vs codex: скиллы и динамическая загрузка MCP» (14.11) | Сравнение по исходникам `~/src/codex` (`b1573f1`) и `~/src/pi-mono`. Codex: при `supports_search_tool` MCP-тулы по умолчанию deferred, поиск BM25 через `tool_search`. Pi: `exposure` = `codemode`/`deferred`/`direct`/`hidden`, сервер, подключившийся по ходу сессии, дописывается в конец контекста, чтобы не сбить кеш | Основной источник по Codex и Pi. Wire-формат API там не разбирали |
+| @thread:thr_… «OSS code-read: hermes-agent» (14.11) | `tools/tool_search.py`: MCP и плагинные тулы заменяются тремя bridge-тулами `tool_search` / `tool_describe` / `tool_call`, core-тулы не откладываются | Готовый образец чисто харнессного подхода |
+| @thread:thr_… «Анализ сетевых задержек» (02.11) | В логах запросов Claude Code 2.1.310 видны бета-хедеры `advanced-tool-use-2025-11-20`, `mid-conversation-tool-changes-2026-07-01`, `inline-tools-2026-09-15`, `prompt-caching-scope-2026-01-05` | Подтверждение, что Claude Code реально шлёт эти беты |
+| @thread:thr_… (29.09) | Тулы `claude-in-chrome` грузились через `ToolSearch` (7 вызовов в сессии) | Наблюдение, что механизм работает в живых сессиях |
+| @thread:thr_… «Ресерч: dynamic tools в Pi» (сиблинг, идёт сейчас) | Нашёл в `pi-ai` Anthropic-провайдер с `nativeToolChanges`: `tools` фиксирован + `DEFERRED_TOOL_PLACEHOLDER`, поздние тулы через `tool_addition`/`tool_removal` | Пересекается с Claude Code. Pi подробно разбирается там, здесь не дублирую |
+
+**По Claude Code целевого ресерча в прошлых сессиях не было**: только косвенные следы (бета-хедеры, использование `ToolSearch`). Механизм ниже проверен сейчас.
+
+## Codex
+
+Все факты ниже — **[code-now]**, `~/src/codex/codex-rs` @ `b1573f1` (14.11.2026). Общая картина совпа
… [15746 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking whether /tmp needs cleaning up, and I'm deciding to leave it alone since that's fine. The final answer should run about 10 to 15 lines.
````
</details>

**[agent]**

Отчёт готов: [recall-codex-claude-code.md](<local path>)

- **Что нашлось в прошлых сессиях.** Codex и Pi разбирались в @thread:thr_…, пример bridge-тулов `tool_search`/`tool_describe`/`tool_call` из hermes-agent — в @thread:thr_…. Целевого ресерча по Claude Code не было, только следы бета-хедеров в @thread:thr_…. Поэтому Claude Code я проверил сейчас: по бинарю 2.1.321, по докам и по поведению этой сессии.
- **Codex** (исходники, клон от 14.11). В `tools` лежат только direct-тулы и один `{"type":"tool_search","execution":"client"}`. Отложенных тулов в массиве нет, модель видит только список источников. На `tool_search_call` Codex сам делает BM25-поиск и возвращает item `tool_search_output` с полными схемами. Схемы попадают в историю, а не в `tools`. Это фича Responses API (gpt-5.4+), а chat completions Codex больше не поддерживает.
- **Claude Code.** Все отложенные тулы лежат в `tools[]` с `defer_loading: true`, но сервер не рендерит их в префикс. Изначально модель видит только имена: анонсы `deferred_tools_delta` дописываются в хвост переписки. Откладываются не только MCP, но и редкие встроенные тулы. Свой клиентский `ToolSearch` возвращает `tool_result` с блоками `tool_reference`, и API раскрывает их в полные схемы прямо в этом месте.
- **Новое в API Anthropic.** В `messages` можно дописать `role:"system"` с блоками `tool_addition`/`tool_removal`: по ссылке (бета `mid-conversation-tool-changes`) или с полным определением (бета `inline-tools`). Так набор тулов меняется посреди диалога, а `tools[]` остаётся нетронутым.
- **Почему кеш цел.** В обоих API найденная схема дописывается в хвост контекста, префикс не меняется.
- **Гипотеза «нужна поддержка в API» верна наполовину.** API нужен, чтобы найденный тул стал настоящим нативным: модель обучена на этом формате, сервер проверяет имя и схему. Саму подгрузку без потери кеша можно сделать в харнессе.
- **Голый chat completions (vLLM).** В шаблонах Qwen3 и gpt-oss тулы стоят в самом начале промпта. Поэтому любое изменение `tools` заставляет заново считать KV-кеш всего диалога.
- **Рекомендация:** фиксированный `tools` из основных тулов плюс мета-тулы `search_tools`/`describe_tool`/`call_tool`. Схемы отдаём текстом в результатах тулов, аргументы `call_tool` проверяем по схеме в харнессе. По сути это то же самое, что нативные API делают внутри.
- **Гипотеза для спайка:** описать тул в хвосте и дать модели звать его напрямую по имени. Парсер hermes в vLLM имена по `tools` не фильтрует. Будет ли модель реально так делать, я не проверял.

<details><summary>Что не проверено</summary>

- Попадание в кеш у Claude Code после `ToolSearch` живым запросом не мерил: опираюсь на доки и старые логи.
- Как сервер OpenAI превращает `tool_search_output` в токены, не видно. Есть только формат запроса и формулировка доки.
- Парсеры vLLM кроме hermes (qwen3_coder, harmony) не смотрел.

</details>

Sources: [Anthropic: Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool), [Claude Code: MCP tool search](https://code.claude.com/docs/en/mcp), [OpenAI: Tool search](https://developers.openai.com/api/docs/guides/tools-tool-search), [OpenAI community: 500 on repeated tool_search](https://community.openai.com/t/responses-api-500-when-tool-search-is-used-again-after-loading-both-top-level-and-namespaced-tools/1376159)
