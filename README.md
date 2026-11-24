# loola-agent

Минимальный async coding-agent harness поверх OpenAI-compatible `/v1/chat/completions`: решение тестового задания из [TASK.md](TASK.md). Исходник — ~100 строк, один тул `bash`, синхронный `requests`. Результат — небольшой SDK (~1050 строк в `src/`, из них ~270 — тестовая обвязка `gh_proxy.py`) с двумя механизмами из задания:

- **динамическая подгрузка тулов и скиллов**: в промпте фиксированный маленький набор тулов, остальное модель находит сама; массив `tools` и system prompt не меняются всю сессию;
- **context compaction с гарантией окна**: следующий запрос никогда не превышает `LLM_CONTEXT_WINDOW`, summary-запрос попадает в KV-cache.

Рамка, в которой принимались решения: это showcase, а не продукт. Читается за минуты, без фреймворков (даже без `openai` SDK — только `httpx` и wire format), один явный путь выполнения, fail fast вместо fallback-веток.

## Быстрый старт

```bash
uv sync
cp .env.example .env          # LLM_BASE_URL, LLM_API_KEY, LLM_MODEL (+ опции ниже)

# только bash
uv run --env-file .env loola-agent "find TODOs in this repo and summarize them"

# + 91 GitHub-тул (deferred), живой read-only backend через `gh`, скиллы, компакшен
LLM_CONTEXT_WINDOW=64000 uv run --env-file .env loola-agent \
  --catalog examples/github_tools.json --catalog-backend gh \
  --skills skills \
  "Review PR #3519 in encode/httpx"

uv run pytest           # 158 детерминированных тестов: fake LLM, fake gh, без сети
uv run pytest -m live   # smoke против реального GitHub через ваш `gh` (нужен `gh auth login`)
```

| Флаг / переменная | Значения | Смысл |
|---|---|---|
| `--catalog PATH` | JSON-каталог | Дополнительные тулы (имя, описание, JSON Schema). Пример: [examples/github_tools.json](examples/github_tools.json) |
| `--catalog-mode` | `deferred` (default) / `direct` | `deferred`: через `tool_search`/`tool_call`; `direct`: все схемы в каждом запросе (baseline для замера) |
| `--catalog-backend` | `dummy` (default) / `gh` | `dummy`: детерминированный ответ-заглушка; `gh`: 14 read-only тулов через `gh api`, остальные честно отвечают «not implemented» |
| `--skills DIR` | `DIR/<name>/SKILL.md` | Скиллы в формате [Agent Skills](https://agentskills.io) |
| `--skills-mode` | `lazy` (default) / `eager` | `lazy`: в промпте только каталог; `eager`: все тела SKILL.md inline (baseline) |
| `--transcript PATH` | | JSONL-лог событий (default `~/.loola-agent/runs/<timestamp>.jsonl`) |
| `LLM_CONTEXT_WINDOW` | токены | Включает компакшен; ни один запрос не выйдет за окно |
| `LLM_COMPACT_AT` | токены | Опциональный более ранний триггер компакшена |
| `LLM_MAX_TOKENS` | default 8192 | Лимит ответа модели |
| `LLM_SESSION_HEADER` | имя заголовка | Стабильный id разговора в заголовке (OpenCode Go роутит и кэширует по нему) |

Финальный ответ идёт в stdout, ход работы — в stderr. Exit code 0 только при статусе `done`.

Живые прогоны делались на `deepseek-v4.1-flash` через OpenCode Go (значения по умолчанию в [.env.example](.env.example)); подойдёт любой OpenAI-compatible сервер, например vLLM.

## Архитектура

```mermaid
flowchart LR
    Shell["CLI / TUI / web<br/>(есть только CLI)"] -->|"send(text)"| Agent
    Agent -->|"AsyncIterator[Event]"| Shell
    Agent -->|"build_context(events)"| LLM["LLM.complete<br/>(httpx, wire format)"]
    Agent -->|"tool calls"| Toolbox["Toolbox<br/>JSON Schema validation"]
    Toolbox --> Bash & TS["tool_search (BM25)"] & TC["tool_call → deferred tools<br/>(dummy / gh)"]
    Agent -.->|"перед каждым запросом"| Comp["compaction:<br/>bound → cut → summary"]
```

| Модуль | Ответственность |
|---|---|
| [llm.py](src/loola_agent/llm.py) | Протокол `LLM` и `OpenAICompatibleLLM`: timeout, retry только на 429/5xx/transport, 4xx → сразу ошибка с телом ответа, `usage` с `cached_tokens` |
| [events.py](src/loola_agent/events.py) | События сессии (append-only список) и `build_context` — чистая проекция событий в `messages` |
| [agent.py](src/loola_agent/agent.py) | `Agent.send()`: цикл, закрытие прерванных tool calls, вызов компакшена |
| [tools.py](src/loola_agent/tools.py) | Протокол `Tool`, `Toolbox` (валидация, direct/deferred), `tool_search` (свой BM25), `tool_call` |
| [compaction.py](src/loola_agent/compaction.py) | Политика, верхняя граница размера запроса, выбор среза, summary-запрос |
| [skills.py](src/loola_agent/skills.py) | Загрузка и валидация SKILL.md, секция system prompt |
| [bash.py](src/loola_agent/bash.py) | bash-тул: вывод в temp-файл, head+tail обрезка, kill process group |
| [catalog.py](src/loola_agent/catalog.py), [gh_proxy.py](src/loola_agent/gh_proxy.py) | Пример каталога + `DummyTool`; read-only прокси к `gh` для живых прогонов (тестовая обвязка) |
| [cli.py](src/loola_agent/cli.py) | Оболочка: env-конфиг, рендер в stderr, JSONL-транскрипт, exit code |

**Событийная модель.** Сессия — append-only список событий `UserMessage | AssistantMessage | ToolStarted | ToolResult | Compaction | RunFinished`. Контекст для LLM не хранится отдельно, а каждый раз проецируется из событий ([events.py](src/loola_agent/events.py#L69)). `AssistantMessage` хранит сообщение сервера как есть, поэтому параллельные tool calls и `reasoning_content` возвращаются серверу байт-в-байт. Любая оболочка просто итерирует события:

```python
async with OpenAICompatibleLLM(base_url, api_key, model) as llm, Bash() as bash:
    agent = Agent(llm, Toolbox([bash], deferred=github_tools), compaction=CompactionPolicy(64_000))
    async for event in agent.send("fix the failing test"):
        match event:
            case ToolStarted(_, name, args): ui.show_call(name, args)
            case Compaction(): ui.notice("context compacted")
            case RunFinished(status, answer, turns, usage): ui.done(status, answer, usage)
```

CLI — ровно такая оболочка (~100 строк): рендерит события в stderr и пишет их в JSONL. TUI или web делаются так же: подписка на тот же итератор. Отмена — обычный `asyncio` cancel: bash убивает process group, а в начале следующего `send()` каждый незакрытый tool call получает синтетический результат «interrupted, may have partial side effects, check state and re-run if needed» ([agent.py](src/loola_agent/agent.py#L42)). Не перезапуск (повторит побочные эффекты) и не удаление (соврёт модели).

## Динамические тулы

У open-source chat templates (Qwen3, gpt-oss и т.п.) массив `tools` рендерится в самое начало промпта. Любое его изменение посреди диалога — полный промах KV-cache по всей истории. Поэтому `tools` **не меняется никогда**:

- в каждом запросе: direct-тулы (`bash`) + `tool_search(query, limit)` + `tool_call(name, arguments)`;
- `tool_search` — BM25 по имени, описанию и именам параметров. Возвращает найденные тулы **вместе с JSON Schema** как обычный tool result, то есть в хвост истории;
- `tool_call` диспатчит в тот же реестр, с той же валидацией.

Каталог для демонстрации — 91 тул из GitHub MCP server v2.2.0 (MIT), взятый **только как данные**: имя, описание, схема. В `direct`-режиме это ≈ 27.8k токенов в каждом запросе (o200k), в `deferred` — три схемы (`bash`, `tool_search`, `tool_call`).

Валидация ([tools.py](src/loola_agent/tools.py#L47)): `jsonschema` Draft 2020-12 поверх схемы тула плюс `additionalProperties: false`. Почти все реальные схемы молча принимают лишние ключи, и опечатка в имени аргумента иначе тихо игнорировалась бы. Ошибка возвращается модели вместе с ожидаемой схемой, поэтому и после компакшена модель восстанавливает тул «бесплатно».

## Скиллы

[Agent Skills](https://agentskills.io) с progressive disclosure. В system prompt — только каталог `<available_skills>` (name, description, путь к SKILL.md), отсортированный по имени, чтобы промпт был байт-стабилен между запусками. Тело модель читает сама через `bash cat`, и оно ложится в историю обычным tool result. Отдельного тула активации нет: `bash` уже умеет читать файлы, а лишний тул — лишняя сущность. Невалидный SKILL.md — ошибка старта, а не тихий пропуск.

В [skills/](skills) три демо-скилла под GitHub-каталог: `review-pull-request`, `fix-github-issue`, `ci-failure-triage`, с `references/` и `scripts/`. Lazy-каталог для них ≈ 408 токенов, eager ≈ 974. На 18 скиллах из `anthropics/skills` разница 2.9k vs 43k токенов в каждом запросе.

## Компакшен

Цель — **гарантия**, а не эвристика «на 80% окна» ([compaction.py](src/loola_agent/compaction.py)).

1. **Верхняя граница следующего запроса** ([`context_bound`](src/loola_agent/compaction.py#L61)): `prompt + completion` из `usage` последнего ответа (точные числа сервера) + UTF-8 байты всего, что добавилось после него. Допущение: токен ≥ 1 байт, что верно для BPE. Ни tiktoken, ни знание токенизатора модели не нужны.
2. **Резерв.** Обычный запрос уходит, только если `bound + max(reply, instruction + summary) ≤ window`, то есть место под будущий summary-запрос есть всегда. `LLM_COMPACT_AT` — лишь опциональный более ранний триггер.
3. **Summary-запрос** ([`summary_request`](src/loola_agent/compaction.py#L94)) = точный контекст ранее отправленного запроса + инструкция в конце. Его размер уже измерен, поэтому он влезает по построению и совпадает по префиксу с закэшированным запросом. `tools` и `tool_choice: auto` те же (почему не `none` — см. «Находки»).
4. **Срез** ([`choose_cut`](src/loola_agent/compaction.py#L83)) — только по границе запроса, где все tool calls отвечены; хвост ≈ 1/5 триггера сохраняется дословно.
5. **Новый контекст:** system prompt → одно user-сообщение (все сообщения пользователя дословно + summary; строгие шаблоны не любят два user подряд) → дословный хвост. Инструкция суммаризатора просит сохранить идентификаторы verbatim и упомянуть активные скиллы, чтобы модель их перечитала.
6. **Явные исходы.** Если сжатие не может уменьшить контекст (весь объём — в последнем ходе), компакшен пропускается, когда запрос влезает, и падает с `CompactionError`, когда нет. Если модель вместо summary вызвала тул или упёрлась в лимит — тоже ошибка. Повторных попыток и «обрежем как-нибудь» нет.

Стоимость summary-запросов входит в `usage` прогона.

## Ответы на вопросы задания

### 1. Как не инвалидировать prompt cache при компакшене и подгрузке

Prefix cache переиспользуется, только если запрос — побайтовое продолжение предыдущего. Отсюда одно правило: **всё переменное — в хвост, префикс только дописывается.**

- **`tools` фиксирован на сессию**: подгрузка идёт через `tool_search`/`tool_call`, схемы приходят tool result'ом в хвост ([tools.py](src/loola_agent/tools.py#L1)). После компакшена найденные тулы в `tools` тоже не добавляются: модель найдёт их заново.
- **System prompt фиксирован**: каталог скиллов статичен и отсортирован, тела читаются в хвост.
- **История воспроизводится байт-в-байт**: assistant message хранится в wire format как вернул сервер; контекст — чистая функция от событий.
- **Summary-запрос = предыдущий запрос + инструкция в конце**: попадает в кэш. На живых прогонах cached 4864/5020 и 9984/10229 (~97%).
- **Тот же `tool_choice`** в summary-запросе: смена на `none` у части провайдеров меняет отрендеренный промпт (см. «Находки»).
- **Компакшен редкий и цельный**: один промах кэша на компакшен (новый префикс), дальше снова только дописываем. Поэтому не делаем micro-compaction (вычистка старых tool outputs посреди истории): каждый такой шаг переписывает середину и ломает кэш после неё.
- **Привязка к реплике**: опциональный `LLM_SESSION_HEADER` со стабильным id разговора — по нему провайдер роутит запросы на реплику с тёплым кэшем.

Доля cached prompt tokens за живой прогон: 80–85% без компакшена, 51% и 78% в прогонах с компакшеном (каждый компакшен — один промах по новому префиксу).

### 2. Какие ошибки тулов отдавать модели, а какие перехватывать в harness

Критерий: **может ли модель исправить это своим следующим действием?** Да — текст в tool result. Нет (инфраструктура, конфиг, баг harness) — исключение или явный статус на границе (CLI), без попыток «уговорить» модель.

| Модели (tool result, текстом) | Harness (исключение / статус прогона) |
|---|---|
| Аргументы — невалидный JSON ([tools.py#L40](src/loola_agent/tools.py#L40)) | HTTP 4xx от LLM → `LLMError` сразу, с телом ответа ([llm.py#L67](src/loola_agent/llm.py#L67)) |
| Неизвестный тул (+ подсказка: список тулов или `tool_search`) | 429/5xx/обрыв соединения → до 3 попыток с backoff, затем `LLMError` ([llm.py#L76](src/loola_agent/llm.py#L76)) |
| Нарушение схемы, включая лишний ключ, + ожидаемая схема ([tools.py#L47](src/loola_agent/tools.py#L47)) | `finish_reason=length` → статус `truncated`; пустой ответ → `empty_reply` (не «успех», как в исходнике) |
| Ненулевой exit code, таймаут команды (с частичным выводом), обрезка вывода с маркером «как читать дальше» ([bash.py](src/loola_agent/bash.py#L32)) | Контекст не влезает даже после сжатия → `CompactionError` |
| `gh` вернул 404 / rate limit / ошибку запроса; аргумент, который backend не поддерживает | `gh` не установлен или не залогинен → `GhUnavailable` на старте |
| Тул каталога не реализован в backend | Невалидный SKILL.md, невалидная схема тула, дубли имён, окно меньше system prompt + тулов → ошибка при создании |
| Прерванный tool call → синтетический «interrupted» | Исключение внутри `Tool.run` (баг тула) не ловится: исходный `except Exception` отправлял баги harness модели как «ошибку тула» |

Ретраи на уровне harness — только для транзиентных сетевых ошибок LLM. Ошибки тулов не ретраятся: решать, повторять ли команду с побочными эффектами, должна модель.

## Решения на развилках

| Развилка | Решение | Почему |
|---|---|---|
| Нативный deferred-API (Anthropic `tool_reference`, OpenAI `tool_search`) или свой | Свой: `tool_search` + `tool_call` в фиксированном `tools` | У голого chat completions / vLLM нативного API нет; так работает на любом сервере, не трогая префикс |
| Constrained decoding / `strict` | Не используем совсем | Не поддерживать два пути; у vLLM при `tool_choice=auto` без strict его и так нет. Компенсация — валидация в harness с ошибкой модели |
| Неизвестные аргументы | Отклоняем (`additionalProperties: false` при валидации) | Иначе опечатки молча игнорируются |
| Вызов deferred-тула напрямую по имени | Разрешён | Следствие одного реестра для диспатча; совпадает с нативными API. Основной путь — `tool_call` |
| BM25 | Свои ~15 строк | `rank-bm25`/`bm25s` тянут numpy ради 91 документа и прячут механику |
| GitHub-тулы | Каталог из GitHub MCP server **как данные**, без MCP-клиента | MCP-протокол вне задания; для детерминизма — `DummyTool`, для живых прогонов — read-only `gh api` (14 тулов, мутаций нет по построению) |
| Скиллы | Каталог в system prompt + `bash cat` | Как в спеке Agent Skills, Pi, Codex; ни одного нового тула |
| Подсчёт токенов | `usage` сервера + байты как верхняя граница | Токенизатор модели неизвестен; tiktoken даст точное, но неверное число |
| Summary и пользовательские сообщения | Сообщения пользователя дословно, остальное — в summary | Задачу формулирует пользователь, её нельзя пересказывать |
| Фоновые процессы в bash | Только правило в описании тула (`cmd > log 2>&1 &`) | Отдельные `bash_output`/`kill` — оверкилл для showcase |
| Обход тулов через shell | Правило в system prompt: «предпочитай выделенный тул; нет подходящего — сначала `tool_search`» | Модель однажды обошла GitHub-тулы через `gh api`; ограничивать bash ради тестового тулсета не стали |

## Сознательно вне scope

- MCP-клиент, Responses API, streaming, `strict`/guided decoding.
- Resume сессии: JSONL-транскрипт пишется, но не загружается.
- Approval и sandbox для bash: запуск в контейнере — ответственность оператора. Из защиты только закрытый stdin и скрытые от команд переменные `LLM_*`.
- TUI/web-оболочки: SDK под них готов, построен только CLI.
- Общий лимит вывода в `Toolbox`: каждый тул режет сам (bash — head+tail, gh — с подсказкой, как сузить запрос).
- Micro-compaction и tiktoken (см. выше).
- `gh_proxy.py` — тестовая обвязка для живых прогонов. Лежит в пакете ради простоты запуска, к SDK не относится.

Известная цена гарантии: для свежих tool outputs байтовая граница пессимистична в ~3–4× (байты vs токены), поэтому компакшен срабатывает раньше необходимого. С искусственно маленьким окном 40k один прогон упал явной ошибкой («even after compaction the context may need 37001 tokens…») — это поведение по дизайну, а не баг.

## Как это у других (кратко)

Claude Code и Codex делают то же самое: в промпте каталог + тул поиска, найденные схемы — в хвост истории. Только «развернуть схему в настоящий тул» им помогает нативный API провайдера (`tool_reference` у Anthropic, `tool_search_output` в OpenAI Responses). Pi на generic chat completions честно пересобирает `tools[]`, то есть каждая подгрузка = cache miss. GitHub MCP server свои `--dynamic-toolsets` в v1.1.0 удалил, остались статические фильтры. Скиллы везде устроены одинаково: статичный каталог + тело в хвост.

## Замеры (план; результаты будут добавлены)

Сравниваем один и тот же harness с выключенными и включёнными механизмами (у исходника нет ни каталога, ни скиллов, сравнивать с ним напрямую бессмысленно):

| | «До» | «После» |
|---|---|---|
| Тулы | все 91 в `tools` (`--catalog-mode direct`) | `deferred` |
| Скиллы | `--skills-mode eager` | `lazy` |
| Компакшен | выключен | `LLM_CONTEXT_WINDOW=64000` |

- **Задачи:** 2 длинные многошаговые задачи на реальном GitHub-репозитории (backend `gh`), × до/после × 2 повтора = 8 прогонов.
- **Окно:** 64k токенов для обоих вариантов: «до» без компакшена может упереться в окно, и это тоже результат.
- **Метрики:** успешность (статус + ручная проверка ответа), число ходов, prompt / cached / completion tokens за прогон (summary-запросы включены), число компакшенов, ошибки переполнения.

_Таблица результатов — TBD._

## Находки на живых прогонах

5 прогонов на `encode/httpx` через `gh`-backend (поиск последнего PR по файлу, ревью PR по скиллу, changelog по последним merged PR с компакшеном). Deferred-поиск и вызов работают; скилл ревью прочитан и выполнен, а шаг записи честно получил «not implemented». После ошибки валидации модель сама исправила аргумент. В прогонах с компакшеном он срабатывал 1–2 раза. Пример: 9 ходов, prompt 208k токенов, из них 167k cached.

- **`tool_choice: none` ломает кэш у OpenCode Go.** При `none` провайдер выкидывает tools из промпта: другой префикс, cached = 0. С `auto` у того же summary-запроса cached 8704/8776. Поэтому summary-запрос идёт с `auto`, а вызов тула вместо summary — явная ошибка.
- **gpt-6-luna не умеет tools + reasoning в chat completions**: тулы работают только с `reasoning_effort=none`. Перешли на `deepseek-v4.1-flash`.
- **DeepSeek требует вернуть `reasoning_content`**, иначе 400. Отсюда решение хранить assistant message как есть, а не пересобирать его из `content` + `tool_calls`, как делал исходник.
- **Модель обходила тулы через shell**: в одном прогоне после нескольких `tool_call` она перешла на `gh api …` в bash. Помогла одна фраза в system prompt; bash не ограничивали.
- **OpenCode Go требует `x-opencode-session` и собственный User-Agent**: стабильный session id нужен и для роутинга, и для кэша. Отсюда `LLM_SESSION_HEADER`.

## Путь в истории коммитов

`git log --oneline` читается как журнал работы: импорт исходника как baseline → фиксы базового цикла (история tool calls, `reasoning_content`, невалидный JSON, обрезка вывода, timeout/retry, `finish_reason=length`, process groups в bash) → async SDK + тонкий CLI → закрытие прерванных tool calls → deferred tools → `gh`-backend для живых прогонов → скиллы → компакшен → правило «тул важнее shell». AGENTS.md и лог сессии с агентом будут добавлены отдельно.
