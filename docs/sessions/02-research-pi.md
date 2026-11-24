# Sub-agent: dynamic tools in the Pi coding agent

Full bb session log, converted from the raw event stream: inputs, agent messages, reasoning, commands with output, file changes and tool calls (long outputs truncated to 4000 characters). Local paths, thread ids and emails are redacted; outputs that came from the developer's private projects are replaced with a placeholder.

---

## [input]

Контекст: делаем тестовое задание — минимальный coding-agent harness на Python (~/projects/loola-test-task, задание в TASK.md). Нужно реализовать динамическую подгрузку тулов, чтобы не держать десятки описаний инструментов в промпте, и не инвалидировать prompt cache (KV-cache префикса). LLM в задании — произвольный OpenAI-compatible /v1/chat/completions endpoint.

Твоя задача (read-only, в проекте ничего не меняй): разобраться, как это сделано в Pi coding agent. Локально установлен @earendil-works/pi-coding-agent 1.5.0 (<local path> бандл в dist, ищи и исходники/типы/доки/CHANGELOG рядом). Сверься с upstream-репо на GitHub — там может быть новее.
1. Есть ли в Pi динамическая/ленивая подгрузка тулов (tool search, deferred tools, подгрузка тулов из extensions/MCP по требованию)? Если есть — как устроена: что в промпте изначально, как модель находит и активирует тул, куда попадает схема, меняется ли массив tools между запросами.
2. Pi мультипровайдерный — как они решают это поверх провайдеров без нативной поддержки (OpenAI-compatible chat completions), используют ли нативные API-фичи там, где они есть (Anthropic tool search / defer_loading и т.п.).
3. Как это взаимодействует с prompt cache: что инвалидирует префикс, что нет.
4. Коротко: как в Pi грузятся скиллы (progressive disclosure) — только как контраст, глубоко не копай.
Если динамической подгрузки тулов нет — так и скажи, с доказательствами (что искал и где), и опиши, что есть вместо неё.

Ссылайся на конкретные файлы/строки/коммиты. Результат: отчёт на русском в <local path> (Markdown, абзацы без hard-wrap), в финальном ответе — краткая выжимка 10–15 строк и путь к отчёту.

<details><summary>reasoning</summary>

````
I'm going to start by looking through the local install to see what's there.
````
</details>

**[agent]**

Начинаю с локального пакета Pi: структура, доки, CHANGELOG, поиск по ключевым словам.

**[command]** exit=0

````
cd <local path> && ls && cat package.json | head -60 && ls dist | head -50 && ls docs 2>/dev/null | head -50
````

````
CHANGELOG.md
README.md
dist
docs
examples
node_modules
package.json
schemas
{
	"name": "@earendil-works/pi-coding-agent",
	"version": "1.5.0",
	"description": "Coding agent CLI with read, bash, edit, write tools and session management",
	"type": "module",
	"piConfig": {
		"configDir": ".pi"
	},
	"bin": {
		"pi": "dist/bundle/cli.js"
	},
	"main": "./dist/index.js",
	"types": "./dist/index.d.ts",
	"exports": {
		".": {
			"types": "./dist/index.d.ts",
			"import": "./dist/index.js"
		},
		"./rpc-entry": {
			"import": "./dist/bundle/rpc-entry.js"
		}
	},
	"files": [
		"dist",
		"docs",
		"examples",
		"schemas",
		"containerization.md",
		"CHANGELOG.md"
	],
	"scripts": {
		"clean": "node ../../scripts/package-files.mjs clean dist",
		"build": "npm run build:unbundled && node ../../scripts/build-coding-agent-bundle.mjs",
		"build:unbundled": "tsc -p tsconfig.build.json && node ../../scripts/package-files.mjs executable dist/cli.js dist/rpc-entry.js && npm run copy-assets",
		"build:binary": "npm --prefix ../tui run build && npm --prefix ../telemetry run build && npm --prefix ../ai run build && npm --prefix ../agent run build && npm run build && bun build --compile --no-compile-autoload-bunfig --no-compile-autoload-dotenv ./dist/bun/cli.js ./src/utils/image-resize-worker.ts ./src/extensions/codemode/worker.ts --outfile dist/pi && npm run copy-binary-assets",
		"copy-assets": "node ../../scripts/package-files.mjs copy \"src/modes/interactive/theme/*.json\" dist/modes/interactive/theme && node ../../scripts/package-files.mjs copy \"src/modes/interactive/assets/*.png\" dist/modes/interactive/assets && node ../../scripts/package-files.mjs copy src/core/export-html/template.html src/core/export-html/template.css src/core/export-html/template.js dist/core/export-html && node ../../scripts/package-files.mjs copy \"src/core/export-html/vendor/*.js\" dist/core/export-html/vendor",
		"copy-binary-assets": "node ../../scripts/package-files.mjs copy package.json README.md CHANGELOG.md docs examples ../../node_modules/@silvia-odwyer/photon-node/photon_rs_bg.wasm dist && node ../../scripts/package-files.mjs copy \"src/modes/interactive/theme/*.json\" dist/theme && node ../../scripts/package-files.mjs copy \"src/modes/interactive/assets/*.png\" dist/assets && node ../../scripts/package-files.mjs copy src/core/export-html/template.html dist/export-html && node ../../scripts/package-files.mjs copy \"src/core/export-html/vendor/*.js\" dist/export-html/vendor",
		"test": "vitest --run",
		"generate:schemas": "node --import ./src/experimental/source-resolver.ts scripts/generate-schemas.ts",
		"generate:references": "node --import ./src/experimental/source-resolver.ts scripts/generate-references.ts",
		"prepublishOnly": "npm run clean && npm run build"
	},
	"dependencies": {
		"@earendil-works/pi-agent-core": "1.5.0",
		"@earendil-works/pi-ai": "1.5.0",
		"@earendil-works/pi-codemode": "1.5.0",
		"@earendil-works/pi-mcp": "1.5.0",
		"@earendil-works/pi-tui": "1.5.0",
		"@silvia-odwyer/photon-node": "0.3.4",
		"brace-expansion": "5.0.12",
		"chalk": "6.0.0",
		"cross-spawn": "7.0.6",
		"diff": "8.0.4",
		"grok-mermaid": "0.2.3",
		"highlight.js": "10.7.3",
		"hosted-git-info": "9.0.3",
		"ignore": "7.0.8",
		"jiti": "2.7.0",
		"minimatch": "11.0.3",
		"proper-lockfile": "4.1.2",
bun
bundle
cli
cli.d.ts
cli.d.ts.map
cli.js
cli.js.map
config.d.ts
config.d.ts.map
config.js
config.js.map
core
extensions
index.d.ts
index.d.ts.map
index.js
index.js.map
main.d.ts
main.d.ts.map
main.js
main.js.map
migrations.d.ts
migrations.d.ts.map
migrations.js
migrations.js.map
modes
package-manager-cli.d.ts
package-manager-cli.d.ts.map
package-manager-cli.js
package-manager-cli.js.map
rpc-entry.d.ts
rpc-entry.d.ts.map
rpc-entry.js
rpc-entry.js.map
utils
cli-integration.md
cli.md
codemode.md
compaction.md
configuration.md
containerization.md
custom-provider.md
docs.json
environment-variables.md
extensions.md
how-pi-works.md
images
index.md
json.md
keybindings.md
llama-cpp.m
… [520 more characters truncated]
````

<details><summary>reasoning</summary>

````
I noticed the codemode and MCP packages, so I'm going to grep the codebase to see where they're referenced.
````
</details>

**[agent]**

Интересно: в зависимостях есть `pi-codemode` и `pi-mcp`, а в docs — `codemode.md` и `mcp.md`. Смотрю их и грепаю по ключевым словам.

**[command]** exit=0

````
cd <local path> && wc -l docs/codemode.md docs/mcp.md docs/skills.md docs/extensions.md CHANGELOG.md && grep -rniE "defer|lazy|tool.?search|search_tools|activeTools|setActiveTools|on.?demand|tool_reference|cache" docs/*.md | head -80
````

````
230 docs/codemode.md
   274 docs/mcp.md
    93 docs/skills.md
  3347 docs/extensions.md
  6481 CHANGELOG.md
 10425 total
docs/cli.md:132:`--tools` selects the tools declared to the model. It does not remove MCP tools, whose reach is set by their [exposure](mcp.md#control-tool-exposure): `pi --tools read,codemode` keeps every MCP tool callable from codemode scripts. An MCP tool that no entry names or matches is never declared directly, whatever its exposure; only `tool_search`, if listed, can load it. Once an entry starts with `mcp__`, `--tools` filters MCP tools too, so this keeps only the tools of the `radius` server:
docs/cli.md:156:| `tool_search` | Search tools that are not declared to the model (`codemode` and `deferred` exposure, such as MCP tools) and declare the matches for the next call |
docs/cli.md:180:### Tool search
docs/cli.md:182:`tool_search` is off by default; enable it with `"defaultTools": ["+tool_search"]` or `--tools`. It uses the same ranking as `searchTools()` over tools that are not declared yet and declares the matches for the next model call. Loaded tools are recorded in the session like other tool changes, so they stay declared on that branch.
docs/codemode.md:50:The `codemode` description lists tools with their TypeScript declarations, grouped by namespace (for example one MCP server). Tools with `deferred` exposure, which includes MCP tools with the default `codemode` exposure, are not listed, so the description stays the same while MCP servers connect. Listed declarations share a budget of 3000 estimated tokens (`codemode.inlineBudget` in [settings](settings.md#tools)). Scripts find the other tools with `searchTools()`, `describeTool()`, `describeNamespace()`, or by filtering `ALL_TOOLS`.
docs/compaction.md:23:Both use closely related structured formats and track file operations cumulatively. Summarization requests disable prompt-cache writes because these one-off prompts are unlikely to be reused.
docs/custom-provider.md:71:        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
docs/custom-provider.md:98:      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
docs/custom-provider.md:107:      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
docs/custom-provider.md:149:Set `promptCache.short` or `promptCache.long` to the provider's best-effort cache lifetime in seconds when Pi should keep an idle prompt cache warm. Leave them unset to disable cache warming for that retention tier.
docs/custom-provider.md:204:Set a concrete terminal stop reason. Error and aborted messages need an `errorMessage`; successful messages need accurate input, output, cache, total-token, and cost values.
docs/environment-variables.md:89:| `PI_CACHE_RETENTION` | Set to `long` for extended provider prompt caching where supported |
docs/extensions.md:242:      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
docs/extensions.md:256:Defer background resource startup until `session_start` or the command/tool/event that needs the resource. Register an idempotent `session_shutdown` handler to close any session-scoped resources you start.
docs/extensions.md:406:| Idle prompt-cache refresh | `cache_warming_decision` |
docs/extensions.md:423:| Last override | The last `cache_warming_decision` handler that returns an action wins. |
docs/extensions.md:657:The `systemPromptOptions` field gives extensions access to the same structured data Pi uses to build the system prompt. Collections are mutable. Prefer changing `sections`, `selectedTools`, or `promptGuidelines`: Pi diffs the resulting prompt sections against what the model already has and appends one system message patching only the changed sections. Returning `systemPrompt`, or setting `forceSystemPrompt`, replaces the whole prompt for the run: every provider receives the forced text as its leading system prompt (a cache miss when it changes), and the session transcript keeps recording the structured sections. Tool selection changes updat
… [14374 more characters truncated]
````

<details><summary>reasoning</summary>

````
I've got the relevant pieces now: a tool search exists, tools can be exposed deferred, and transcripts carry system messages with tool deltas. Next I'll read the extension, MCP, and CLI docs plus the message and session format details, then trace how tool and prompt deltas get serialized for providers. The open question is how providers that can't represent a transition get a full transcript checkpoint instead.

Now I'm checking the pi-ai and pi-agent-core sources to see how that checkpoint gets built.
````
</details>

<details><summary>reasoning</summary>

````
Pi поддерживает динамическую подгрузку инструментов (`tool_search`, `exposure: "deferred"`, дельты в транскрипте); сейчас читаю ключевые разделы документации.
````
</details>

**[command]** exit=0

````
cd <local path> && sed -n 2625,2790p extensions.md
````

````
#### Fallback

If a slot renderer is not defined or throws:
- `renderCall`: Shows the tool name
- `renderResult`: Shows raw text from `content`

### Dynamic Tool Loading

Extensions can register many tools while keeping only a small initial set active. A tool can then change the active set with `pi.setActiveTools()` during execution. Pi stores the initial prompt and tool loadout in the transcript's first system message, then appends tool and prompt deltas before the next model request. Providers that cannot represent a transition receive a complete transcript checkpoint, which may invalidate the cached prefix.

The lifecycle is:

1. Register every tool with `pi.registerTool()` so it appears in `pi.getAllTools()`. Register searchable tools with `defaultActive: false` so they start inactive.
2. Keep loader tools, such as `search_tools`, active.
3. During loader execution, call `pi.setActiveTools()` with the desired active tool names. Names must already be registered; unknown and `hidden` names are ignored.

Pi also ships a built-in `tool_search` tool. Register tools with `exposure: "deferred"` to make them findable by it instead of writing your own loader; see [Tool Exposure](#tool-exposure).

#### Search tool example

The following extension registers two inactive searchable tools and keeps `search_tools` active as their loader. The example uses simple keyword matching, but the search implementation could use BM25, embeddings, a remote catalog, or project-specific routing.

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

const SEARCHABLE_TOOL_NAMES = new Set(["lookup_weather", "search_issues"]);

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "lookup_weather",
    label: "Lookup Weather",
    defaultActive: false,
    description: "Look up the current weather for a city",
    parameters: Type.Object({ city: Type.String() }),
    async execute(_toolCallId, params) {
      return {
        content: [{ type: "text", text: `Weather for ${params.city}: sunny` }],
        details: {},
      };
    },
  });

  pi.registerTool({
    name: "search_issues",
    label: "Search Issues",
    defaultActive: false,
    description: "Search project issues by keyword",
    parameters: Type.Object({ query: Type.String() }),
    async execute(_toolCallId, params) {
      return {
        content: [{ type: "text", text: `No open issues matching ${params.query}` }],
        details: {},
      };
    },
  });

  pi.registerTool({
    name: "search_tools",
    label: "Search Tools",
    description: "Search for and enable tools relevant to a task",
    promptSnippet: "Search for additional tools when the active tools cannot perform the task",
    promptGuidelines: [
      "Use search_tools when a task requires a capability that is not currently available.",
    ],
    parameters: Type.Object({
      query: Type.String({ description: "Capability or task to search for" }),
      limit: Type.Optional(Type.Integer({ minimum: 1, maximum: 10 })),
    }),
    async execute(_toolCallId, params) {
      const terms = params.query.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
      const matches = pi.getAllTools()
        .filter((tool) => SEARCHABLE_TOOL_NAMES.has(tool.name))
        .map((tool) => ({
          tool,
          score: terms.reduce(
            (score, term) =>
              score + (`${tool.name} ${tool.description}`.toLowerCase().includes(term) ? 1 : 0),
            0,
          ),
        }))
        .filter((match) => match.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, params.limit ?? 3)
        .map((match) => match.tool.name);

      if (matches.length === 0) {
        return {
          content: [{ type: "text", text: `No tools found for: ${params.query}` }],
          details: { matches: [] as string[], added: [] as string[] },
        };
      }

      const active = pi.getActiveTools();
      const added = mat
… [7372 more characters truncated]
````

**[command]** exit=0

````
cd <local path> && sed -n 120,200p cli.md && echo ------ && sed -n 180,274p mcp.md
````

````
Replaces the default selection with a comma-separated allowlist of built-in, extension, or custom tools. Entries are tool names or patterns where `*` matches any characters. MCP tools are kept unless an entry starts with `mcp__` (see [MCP tools](#mcp-tools)). A list of only `+name` and `-name` entries is not an allowlist; it changes the default selection instead.
- `-xt`, `--exclude-tools <list>`<br>
  Disables comma-separated tool names or patterns after all other selection options, MCP tools included.
- `-nbt`, `--no-builtin-tools`<br>
  Disables default built-in tools while retaining extension and custom tools.
- `-nt`, `--no-tools`<br>
  Starts with all built-in, extension, custom, and MCP tools disabled.

Default enabled tools are `read`, `bash`, `edit`, and `write`, unless `defaultTools` changes them. `--tools` with plain names replaces the whole selection, so name every tool you want. Like `defaultTools`, it also accepts a list of only `+name` and `-name` entries, which adds tools to or removes them from the default selection: `pi --tools +codemode,-write` keeps the other default tools, enables `codemode`, and disables `write`. These entries take exact tool names, not `*` patterns; use `--exclude-tools` to disable tools by pattern. Plain names and `+name`/`-name` entries cannot be mixed. `/reload` enables tools newly added to `defaultTools`, but a tool removed with `-name` stays removed.

<a id="mcp-tools"></a>

`--tools` selects the tools declared to the model. It does not remove MCP tools, whose reach is set by their [exposure](mcp.md#control-tool-exposure): `pi --tools read,codemode` keeps every MCP tool callable from codemode scripts. An MCP tool that no entry names or matches is never declared directly, whatever its exposure; only `tool_search`, if listed, can load it. Once an entry starts with `mcp__`, `--tools` filters MCP tools too, so this keeps only the tools of the `radius` server:

```sh
pi --tools read,bash,codemode,'mcp__radius__*'
```

The MCP resource tools (`list_mcp_resources`, `list_mcp_resource_templates`, `read_mcp_resource`) count as MCP tools. To remove MCP tools, use `--exclude-tools 'mcp__*'` or [`--no-mcp`](#resource-options).

| Built-in | Purpose |
|---|---|
| `read` | Read text files and supported images |
| `bash` | Run shell commands |
| `powershell` | Run PowerShell commands on Windows |
| `edit` | Apply exact text replacements to an existing file |
| `write` | Create or overwrite a file |
| `grep` | Search file contents |
| `find` | Find paths using glob patterns |
| `ls` | List directory contents |

Built-in extensions add two more tools. They are off by default; the MCP extension turns them on when an MCP server needs them (see [MCP](mcp.md#control-tool-exposure)). To enable them yourself, name them in `--tools` or `defaultTools`.

| Built-in extension | Purpose |
|---|---|
| `codemode` | Run JavaScript that calls the other tools, for example in parallel with `Promise.allSettled`; only the script's output reaches the model |
| `tool_search` | Search tools that are not declared to the model (`codemode` and `deferred` exposure, such as MCP tools) and declare the matches for the next call |

### Enable codemode

To turn on `codemode` for every session, add it to the default tools in `~/.pi/agent/settings.json` or a project's `.pi/settings.json`:

```json
{
  "defaultTools": ["+codemode"]
}
```

This keeps `read`, `bash`, `edit`, and `write` and adds `codemode`. For one invocation, add it with `--tools`:

```sh
pi --tools +codemode
```

Codemode is useful without MCP: scripts can run several tool calls in parallel, filter large output before it reaches the model, call classifier models such as TypeSafe's Jev through `models.classify()` (see [Classifier models](models.md#use-classifier-models)), and generate images through `models.generateImages()` (see [Image models](models.md#use-image-models)).

### How codemode works

Scripts run in a QuickJS sandbox and reach the other tools through `t
… [9843 more characters truncated]
````

<details><summary>reasoning</summary>

````
Next I'm working out how tool and prompt deltas get serialized for the providers. I'll check the session-format and message-types docs, the pi-ai package, and grep the docs and dist for "loadout", "checkpoint", and "system message".
````
</details>

<details><summary>reasoning</summary>

````
Сейчас посмотрю, как дельты инструментов и промпта сериализуются провайдерам: файлы session-format, message-types и providers, а также пакеты pi-ai и pi-agent-core.
````
</details>

**[command]** exit=0

````
cd <local path> && grep -rniE "loadout|checkpoint|tool delta|toolsDelta|tool_delta|mid-conversation|systemMessage|system message" docs/*.md | grep -v "^docs/extensions.md:26[3-9][0-9]" | head -60; ls node_modules/@earendil-works 2>/dev/null; ls <local path>
````

````
docs/compaction.md:83:On repeated compactions, the summarized span starts at the previous compaction's kept boundary (`firstKeptEntryId`), not at the compaction entry itself, falling back to the entry after the previous compaction if that kept entry cannot be found in the path. A retain-none compaction records its own ID as `firstKeptEntryId`; repeated compaction starts after that entry. This preserves messages that survived the earlier compaction by including them in the next summarization pass as well. Pi also recalculates `tokensBefore` from the rebuilt, context-edited session projection before writing the new `CompactionEntry`, so the token count reflects the actual pre-compaction context being replaced. Omitted raw entries remain stored but do not affect cut selection, summaries, checkpoints, or token estimates.
docs/llama-cpp.md:116:- Hybrid models such as Qwen3.5 cannot rewind a partially cached prompt without context checkpoints. If each question reprocesses the whole state, start the router with `--ctx-checkpoints 32 --checkpoint-min-step 0`.
docs/message-types.md:94:### SystemMessage
docs/message-types.md:97:interface SystemMessage {
docs/message-types.md:107:The leading system message declares the initial prompt and tools. Later system messages can append instructions, replace or remove named prompt sections, and add or remove tools. Replaying them in order yields the current state.
docs/message-types.md:269:  | SystemMessage
docs/custom-provider.md:178:The stream receives a normalized `TranscriptContext`. System prompts and tool declarations live in transcript system messages, so read them with `getCurrentSystemPrompt(context.messages)` and `getCurrentTools(context.messages)` rather than expecting `context.systemPrompt` or `context.tools`. A model that supports mid-conversation system messages can receive them in place; otherwise call `collapseSystemMessages(context)` to fold later system messages into the leading one.
docs/extensions.md:23:- Git checkpointing (stash at each turn, restore on branch)
docs/extensions.md:657:The `systemPromptOptions` field gives extensions access to the same structured data Pi uses to build the system prompt. Collections are mutable. Prefer changing `sections`, `selectedTools`, or `promptGuidelines`: Pi diffs the resulting prompt sections against what the model already has and appends one system message patching only the changed sections. Returning `systemPrompt`, or setting `forceSystemPrompt`, replaces the whole prompt for the run: every provider receives the forced text as its leading system prompt (a cache miss when it changes), and the session transcript keeps recording the structured sections. Tool selection changes update both the prompt contributions and executable provider tools; calling `pi.setActiveTools()` inside the handler has the same effect as editing `selectedTools`. Models that accept system messages mid-conversation receive the patch in place and keep their cached prefix; other models get the replayed prompt as their system prompt, which is a cache miss once per change.
docs/extensions.md:821:  // event.messages - deep copy without system messages, safe to modify
docs/extensions.md:827:`event.messages` holds the conversation without system messages. The prompt and tool declarations belong to Pi and are not part of this hook: when the handler returns a changed list, Pi replays the current prompt sections and tool declarations into one leading system message ahead of the returned messages. Filtering, windowing, or slicing from a compaction summary therefore cannot drop the prompt or the tools. An unchanged list keeps mid-conversation system messages in place, so models that accept them retain their cached prefix. System messages a handler adds are kept after Pi's head. To change the prompt or the tool set durably, use [`before_agent_start`](#before_agent_start) or `pi.setActiveTools()`; to edit system messages for one request, use [`context_with_system`](#context_with
… [7275 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm wondering which provider those mid-conversation tool addition and removal flags belong to, since it might be a newer feature. I'll check the provider sections in models-configuration.md, plus the relevant parts of message-types.md and session-format.md.
````
</details>

<details><summary>reasoning</summary>

````
В транскрипте системные сообщения с `toolsAdded`/`toolsRemoved`, а у моделей есть флаги поддержки таких изменений; сейчас выясняю, каким провайдерам они соответствуют.
````
</details>

**[command]** exit=0

````
cd <local path> && sed -n 90,125p message-types.md && echo ----- && sed -n 100,195p models-configuration.md && echo ---- && sed -n 76,90p session-format.md && sed -n 170,185p custom-provider.md
````

````
When present, `reasoning` is already included in `output`; do not add it again. `cacheWrite1h` is the subset of `cacheWrite` written with one-hour retention.

## Base messages

### SystemMessage

```typescript
interface SystemMessage {
  role: "system";
  content: string | TextContent[];
  sections?: Record<string, string | null>;
  toolsAdded?: Tool[];
  toolsRemoved?: ToolReference[];
  timestamp: number;
}
```

The leading system message declares the initial prompt and tools. Later system messages can append instructions, replace or remove named prompt sections, and add or remove tools. Replaying them in order yields the current state.

### UserMessage

```typescript
interface UserMessage {
  role: "user";
  content: string | (TextContent | ImageContent)[];
  timestamp: number;
}
```

### AssistantMessage

```typescript
interface AssistantMessage {
  role: "assistant";
  content: (TextContent | ThinkingContent | ToolCall)[];
  api: string;
-----
| `images.resize.maxBytes` | integer |  | Maximum base64-encoded payload size in bytes. |
| `images.resize.jpegQuality` | integer |  |  |
| `images.maxPerMessage` | integer |  | Maximum images accepted in one provider message. |
| `images.maxPerRequest` | integer |  | Maximum images accepted across one provider request. |

## Compatibility

`compat` describes verified differences from an API's standard request and response behavior. Model values override provider values per field. The fields that apply depend on the model's `api`.

### `openai-completions`

| Field | Type | Default | Description |
|---|---|---|---|
| `supportsStore` | boolean |  | Whether the provider supports the store field. Default: auto-detected from URL. |
| `supportsDeveloperRole` | boolean |  | Whether the provider supports the developer role instead of system. Default: auto-detected from URL. |
| `supportsReasoningEffort` | boolean |  | Whether the provider supports reasoning_effort. Default: auto-detected from URL. |
| `supportsUsageInStreaming` | boolean | `true` | Whether the provider supports stream_options.include_usage for token usage in streaming responses. |
| `supportsFinishReason` | boolean | `true` | Whether streamed responses include finish_reason. When false, pi infers stop or toolUse when the stream ends. |
| `maxTokensField` | `"max_completion_tokens" \| "max_tokens"` |  | Which field to use for max tokens. Default: auto-detected from URL. |
| `requiresToolResultName` | boolean |  | Whether tool results require the name field. Default: auto-detected from URL. |
| `requiresAssistantAfterToolResult` | boolean |  | Whether a user message after tool results requires an assistant message in between. Default: auto-detected from URL. |
| `requiresThinkingAsText` | boolean |  | Whether thinking blocks must be converted to text blocks with &lt;thinking> delimiters. Default: auto-detected from URL. |
| `requiresReasoningContentOnAssistantMessages` | boolean |  | Whether all replayed assistant messages must include an empty reasoning_content field when reasoning is enabled. Default: auto-detected from URL. |
| `thinkingFormat` | `"openai" \| "openrouter" \| "deepseek" \| "together" \| "baseten" \| "zai" \| "qwen" \| "chat-template" \| "qwen-chat-template" \| "string-thinking" \| "ant-ling"` |  | Format for reasoning or thinking parameters. When omitted, Pi auto-detects the format from the provider URL. "openai" uses reasoning_effort, "openrouter" uses reasoning.effort, "deepseek" uses thinking.type plus reasoning_effort when supported, "together" uses reasoning.enabled plus reasoning_effort when supported, "baseten" uses configurable chat_template_args plus reasoning_effort when supported, "zai" uses thinking.type, "qwen" uses top-level enable_thinking, "qwen-chat-template" uses chat_template_kwargs.enable_thinking and preserve_thinking, "chat-template" uses configurable chat_template_kwargs, "string-thinking" uses top-level thinking, and "ant-ling" uses reasoning.effort only when the mapped effort is no
… [13560 more characters truncated]
````

<details><summary>reasoning</summary>

````
Next I'm going to look at the real implementation in pi-ai, specifically the openai-completions provider and how it deals with tools being added partway through a conversation. I'll need to track down the source files, likely the dist JS.
````
</details>

<details><summary>reasoning</summary>

````
Документация в порядке. Теперь смотрю, как реализация `pi-ai` сериализует mid-conversation system-сообщения и `toolsAdded`.
````
</details>

**[command]** exit=0

````
cd <local path> && cat package.json | grep -E '"version"|"repository"' ; ls dist dist/api 2>/dev/null | head -80; grep -rlE "supportsMidConvoToolAdditions|toolsAdded|collapseSystemMessages" dist --include=*.js | head -30
````

````
"version": "1.5.0",
	"repository": {
dist:
api
auth
bedrock-provider.d.ts
bedrock-provider.d.ts.map
bedrock-provider.js
bedrock-provider.js.map
bun-oauth.d.ts
bun-oauth.d.ts.map
bun-oauth.js
bun-oauth.js.map
cli.d.ts
cli.d.ts.map
cli.js
cli.js.map
compat
compat.d.ts
compat.d.ts.map
compat.js
compat.js.map
env-api-keys.d.ts
env-api-keys.d.ts.map
env-api-keys.js
env-api-keys.js.map
image-models.d.ts
image-models.d.ts.map
image-models.js
image-models.js.map
images-api-registry.d.ts
images-api-registry.d.ts.map
images-api-registry.js
images-api-registry.js.map
images.d.ts
images.d.ts.map
images.js
images.js.map
index.d.ts
index.d.ts.map
index.js
index.js.map
legacy-api-aliases.d.ts
legacy-api-aliases.d.ts.map
legacy-api-aliases.js
legacy-api-aliases.js.map
model-catalog.d.ts
model-catalog.d.ts.map
model-catalog.js
model-catalog.js.map
models-store.d.ts
models-store.d.ts.map
models-store.js
models-store.js.map
models.d.ts
models.d.ts.map
models.generated.d.ts
models.generated.d.ts.map
models.generated.js
models.generated.js.map
models.js
models.js.map
oauth.d.ts
oauth.d.ts.map
oauth.js
oauth.js.map
providers
session-resources.d.ts
session-resources.d.ts.map
session-resources.js
session-resources.js.map
telemetry.d.ts
telemetry.d.ts.map
telemetry.js
telemetry.js.map
types.d.ts
types.d.ts.map
types.js
types.js.map
utils

dist/api:
dist/providers/compat-schema.js
dist/utils/estimate.js
dist/utils/transcript.js
dist/providers/faux.js
dist/api/bedrock-converse-stream.js
dist/api/google-generative-ai.js
dist/api/google-shared.js
dist/api/anthropic-messages.js
dist/api/google-vertex.js
dist/api/openai-completions.js
dist/api/openai-responses-shared.js
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd <local path> && wc -l utils/transcript.js api/openai-completions.js api/anthropic-messages.js api/openai-responses-shared.js && grep -nE "^export function|^function" utils/transcript.js
````

````
217 utils/transcript.js
  1340 api/openai-completions.js
  1340 api/anthropic-messages.js
   769 api/openai-responses-shared.js
  3666 total
6:export function createInitialSystemMessage(systemPrompt, tools) {
23:export function normalizeContext(context) {
28:function isSystemMessage(message) {
32:export function getInitialSystemMessage(messages) {
37:export function withoutInitialSystemMessage(messages) {
41:export function getCurrentTools(messages) {
58:export function getCurrentSystemMessage(messages) {
88:export function getCurrentSystemPrompt(messages) {
96:export function collapseSystemMessages(context) {
102:export function resolveTranscript(context, supportsMidConvoSystemMessages) {
106:export function toToolDeclaration(tool) {
122:export function declarationsEqual(left, right) {
126:export function getToolStateChanges(previous, current) {
145:export function getDeclaredTools(messages) {
162:export function hasToolRedefinitions(messages) {
177:export function hasNonAdditiveToolChanges(messages) {
181:function findLastNonAdditiveToolChange(systemMessages) {
208:export function resolveTranscriptTools(messages, support) {
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd <local path> && cat -n utils/transcript.js
````

````
1	import { contentText, getSystemMessageText } from "./text.js";
     2	/**
     3	 * Build the leading system message for a prompt and tool set. Returns undefined when
     4	 * both are empty, so an empty transcript stays empty.
     5	 */
     6	export function createInitialSystemMessage(systemPrompt, tools) {
     7	    const hasSystemPrompt = systemPrompt !== undefined && systemPrompt.length > 0;
     8	    const hasTools = tools !== undefined && tools.length > 0;
     9	    if (!hasSystemPrompt && !hasTools)
    10	        return undefined;
    11	    return {
    12	        role: "system",
    13	        content: systemPrompt ?? "",
    14	        ...(hasTools ? { toolsAdded: tools } : {}),
    15	        timestamp: 0,
    16	    };
    17	}
    18	/**
    19	 * Fold `Context.systemPrompt` and `Context.tools` into a leading system message.
    20	 * This is the only entry point that produces a {@link TranscriptContext}; every
    21	 * provider-facing function expects the result.
    22	 */
    23	export function normalizeContext(context) {
    24	    const initialMessage = createInitialSystemMessage(context.systemPrompt, context.tools);
    25	    const messages = initialMessage ? [initialMessage, ...context.messages] : context.messages;
    26	    return { messages };
    27	}
    28	function isSystemMessage(message) {
    29	    return message.role === "system";
    30	}
    31	/** Return the leading system message, if the transcript starts with one. */
    32	export function getInitialSystemMessage(messages) {
    33	    const first = messages[0];
    34	    return first && isSystemMessage(first) ? first : undefined;
    35	}
    36	/** Drop the leading system message for APIs that carry the prompt outside the message list. */
    37	export function withoutInitialSystemMessage(messages) {
    38	    return getInitialSystemMessage(messages) ? messages.slice(1) : messages;
    39	}
    40	/** Resolve the tools available after applying every transcript delta in order. */
    41	export function getCurrentTools(messages) {
    42	    const tools = new Map();
    43	    for (const message of messages) {
    44	        if (!isSystemMessage(message))
    45	            continue;
    46	        for (const tool of message.toolsRemoved ?? [])
    47	            tools.delete(tool.name);
    48	        for (const tool of message.toolsAdded ?? [])
    49	            tools.set(tool.name, tool);
    50	    }
    51	    return [...tools.values()];
    52	}
    53	/**
    54	 * Replay every system message into one leading system message holding the current
    55	 * prompt and tools. Later `content` is appended to the base prompt, `sections` are
    56	 * patched by name, and tools are resolved with {@link getCurrentTools}.
    57	 */
    58	export function getCurrentSystemMessage(messages) {
    59	    const content = [];
    60	    const sections = new Map();
    61	    let timestamp;
    62	    for (const message of messages) {
    63	        if (!isSystemMessage(message))
    64	            continue;
    65	        timestamp ??= message.timestamp;
    66	        const text = contentText(message.content);
    67	        if (text.length > 0)
    68	            content.push(text);
    69	        for (const [name, value] of Object.entries(message.sections ?? {})) {
    70	            if (value === null)
    71	                sections.delete(name);
    72	            else
    73	                sections.set(name, value);
    74	        }
    75	    }
    76	    const tools = getCurrentTools(messages);
    77	    if (timestamp === undefined && tools.length === 0)
    78	        return undefined;
    79	    return {
    80	        role: "system",
    81	        content: content.join("\n\n"),
    82	        ...(sections.size > 0 ? { sections: Object.fromEntries(sections) } : {}),
    83	        ...(tools.length > 0 ? { toolsAdded: tools } : {}),
    84	        timestamp: timestamp ?? 0,
    85	    };
    86	}
    87	/** Render the curre
… [7446 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm opening openai-completions.js next to see how it calls into this code, so I'll grep for the relevant usages.
````
</details>

<details><summary>reasoning</summary>

````
Ядро — `resolveTranscriptTools` с режимами `none`/`additions`/`changes`; сейчас смотрю, как openai-completions их применяет.
````
</details>

**[command]** exit=0

````
cd <local path> && grep -nE "resolveTranscript|MidConvo|toolsAdded|toolsRemoved|collapseSystem|foldedSystemMessages|requestTools|role: \"system\"|role: \"developer\"|cache_control|prompt_cache_key|additional_tools|tool_search" openai-completions.js | head -60
````

````
14:import { getDeclaredTools, resolveTranscript, resolveTranscriptTools, } from "../utils/transcript.js";
154:    const normalizedContext = resolveTranscript(context, getCompat(model).supportsMidConvoSystemMessages);
551:    const transcriptTools = resolveTranscriptTools(context.messages, compat.supportsMidConvoSystemMessages === true && compat.supportsMidConvoToolAdditions === true
562:        prompt_cache_key: (model.baseUrl.includes("api.openai.com") && cacheRetention !== "none") ||
586:    if (transcriptTools.requestTools.length > 0) {
587:        params.tools = convertTools(transcriptTools.requestTools, compat);
816:    lastTool.cache_control = cacheControl;
837:                cache_control: cacheControl,
849:            textPart.cache_control = cacheControl;
856:    const normalizedContext = resolveTranscript(context, compat.supportsMidConvoSystemMessages);
884:    const transcriptTools = resolveTranscriptTools(normalizedContext.messages, compat.supportsMidConvoSystemMessages === true && compat.supportsMidConvoToolAdditions === true
902:            const addedTools = systemIndex++ >= transcriptTools.foldedSystemMessages ? (msg.toolsAdded ?? []) : [];
905:                    role: "system",
1290:        supportsMidConvoSystemMessages: false,
1291:        supportsMidConvoToolAdditions: false,
1332:        supportsMidConvoSystemMessages: model.compat.supportsMidConvoSystemMessages ?? detected.supportsMidConvoSystemMessages,
1333:        supportsMidConvoToolAdditions: model.compat.supportsMidConvoToolAdditions ?? detected.supportsMidConvoToolAdditions,
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd <local path> && sed -n 545,600p openai-completions.js && echo ---- && sed -n 800,960p openai-completions.js && echo ---- && sed -n 1270,1340p openai-completions.js
````

````
dangerouslyAllowBrowser: true,
        fetch,
        defaultHeaders: headers,
    });
}
function buildParams(model, context, options, compat = getCompat(model), cacheRetention = resolveCacheRetention(options?.cacheRetention, options?.env), grammarToolInputProperties = createGrammarToolInputProperties(getDeclaredTools(context.messages), compat.supportsOpenAIGrammarTools)) {
    const transcriptTools = resolveTranscriptTools(context.messages, compat.supportsMidConvoSystemMessages === true && compat.supportsMidConvoToolAdditions === true
        ? "additions"
        : "none");
    const messages = convertMessages(model, context, compat, {
        grammarToolInputProperties,
    });
    const cacheControl = getCompatCacheControl(compat, cacheRetention);
    const params = {
        model: model.id,
        messages,
        stream: true,
        prompt_cache_key: (model.baseUrl.includes("api.openai.com") && cacheRetention !== "none") ||
            (cacheRetention === "long" && compat.supportsLongCacheRetention)
            ? clampOpenAIPromptCacheKey(options?.sessionId)
            : undefined,
        prompt_cache_retention: cacheRetention === "long" && compat.supportsLongCacheRetention ? "24h" : undefined,
    };
    if (compat.supportsUsageInStreaming !== false) {
        params.stream_options = { include_usage: true };
    }
    if (compat.supportsStore) {
        params.store = false;
    }
    if (options?.maxTokens) {
        if (compat.maxTokensField === "max_tokens") {
            // Deprecated by OpenAI, but some OpenAI-compatible providers only accept max_tokens.
            params.max_tokens = options.maxTokens;
        }
        else {
            params.max_completion_tokens = options.maxTokens;
        }
    }
    if (options?.temperature !== undefined) {
        params.temperature = options.temperature;
    }
    if (transcriptTools.requestTools.length > 0) {
        params.tools = convertTools(transcriptTools.requestTools, compat);
        if (compat.zaiToolStream) {
            params.tool_stream = true;
        }
    }
    else if (hasToolHistory(context.messages)) {
        // Anthropic (via LiteLLM/proxy) requires tools param when conversation has tool_calls/tool_results
        params.tools = [];
    }
    if (cacheControl) {
        applyAnthropicCacheControl(messages, params.tools, cacheControl);
    }
    if (options?.toolChoice) {
        params.tool_choice = options.toolChoice;
----
}
function addCacheControlToLastConversationMessage(messages, cacheControl) {
    for (let i = messages.length - 1; i >= 0; i--) {
        const message = messages[i];
        if (message.role === "user" || message.role === "assistant" || message.role === "tool") {
            if (addCacheControlToMessage(message, cacheControl)) {
                return;
            }
        }
    }
}
function addCacheControlToLastTool(tools, cacheControl) {
    if (!tools || tools.length === 0) {
        return;
    }
    const lastTool = tools[tools.length - 1];
    lastTool.cache_control = cacheControl;
}
function addCacheControlToInstructionMessage(message, cacheControl) {
    return addCacheControlToTextContent(message, cacheControl);
}
function addCacheControlToMessage(message, cacheControl) {
    if (message.role === "user" || message.role === "assistant" || message.role === "tool") {
        return addCacheControlToTextContent(message, cacheControl);
    }
    return false;
}
function addCacheControlToTextContent(message, cacheControl) {
    const content = message.content;
    if (typeof content === "string") {
        if (content.length === 0) {
            return false;
        }
        message.content = [
            {
                type: "text",
                text: content,
                cache_control: cacheControl,
            },
        ];
        return true;
    }
    if (!Array.isArray(content)) {
        return false;
    }
    for (let i = content.length - 1; i >= 0; i--) {
        const part = content[i];
     
… [9613 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking how Kimi's mid-conversation tool additions work in chat completions, where a system message carries a tools array. Next I want to see which models are flagged for that in the generated catalog, and look at the system message update renderer. I'm also wondering whether Anthropic's tool addition, removal, and definition blocks are a new addition.

I'm also checking whether Anthropic's API has gained a similar feature by November 2026, along with OpenAI's Responses tool additions and client-executed tool search.
````
</details>

<details><summary>reasoning</summary>

````
В chat completions нашёлся нестандартный `{role:"system", tools:[...]}`; сейчас проверяю, какие модели получают `supportsMidConvoToolAdditions` и как рендерится дельта.
````
</details>

**[command]** exit=0

````
cd <local path> && uv run - <<'PY'
# /// script
# requires-python = ">=3.13,<3.14"
# ///
import re,collections
s=open("models.generated.js").read()
# crude: find each model object by "id:" and compat flags following
for flag in ["supportsMidConvoToolAdditions","supportsMidConvoToolChanges","supportsMidConvoSystemMessages","supportsAdditionalTools","supportsToolSearch"]:
    cnt=collections.Counter()
    ex=[]
    for m in re.finditer(flag+r'"?\s*:\s*true',s):
        start=s.rfind('id:',0,m.start()); start2=s.rfind('"id"',0,m.start()); st=max(start,start2)
        seg=s[st:st+120]
        idm=re.search(r'id"?\s*:\s*"([^"]+)"',seg)
        api=re.search(r'api"?\s*:\s*"([^"]+)"',s[st:m.start()])
        prov=re.search(r'provider"?\s*:\s*"([^"]+)"',s[st:m.start()])
        key=(api.group(1) if api else "?",prov.group(1) if prov else "?")
        cnt[key]+=1
        if len(ex)<200 and idm: ex.append((key,idm.group(1)))
    print("==",flag,sum(cnt.values()))
    for k,v in cnt.most_common(15): print("  ",k,v)
    if flag in("supportsMidConvoToolAdditions","supportsToolSearch","supportsAdditionalTools","supportsMidConvoToolChanges"):
        print("   examples:",sorted(set(e[1] for e in ex))[:40])
PY
grep -n "function renderSystemMessageUpdate" -A30 utils/*.js api/*.js | head -45
````

````
== supportsMidConvoToolAdditions 0
   examples: []
== supportsMidConvoToolChanges 0
   examples: []
== supportsMidConvoSystemMessages 0
== supportsAdditionalTools 0
   examples: []
== supportsToolSearch 0
   examples: []
utils/text.js:24:export function renderSystemMessageUpdate(message) {
utils/text.js-25-    const parts = [];
utils/text.js-26-    const text = contentText(message.content);
utils/text.js-27-    if (text.length > 0)
utils/text.js-28-        parts.push(text);
utils/text.js-29-    for (const [name, value] of Object.entries(message.sections ?? {})) {
utils/text.js-30-        parts.push(value === null
utils/text.js-31-            ? `Removed system prompt section "${name}".`
utils/text.js-32-            : `Updated system prompt section "${name}":\n\n${value}`);
utils/text.js-33-    }
utils/text.js-34-    return parts.join("\n\n");
utils/text.js-35-}
utils/text.js-36-/**
utils/text.js-37- * `text.slice(start, end)` as a string of its own. V8 represents a slice of 13 or more characters as a view that keeps
utils/text.js-38- * all of `text` alive, so a short excerpt kept from a large text (a 500-character error message cut from a megabyte
utils/text.js-39- * response body) would keep the whole text alive as long as the excerpt lives. Appending a character and slicing it off
utils/text.js-40- * again makes V8 copy just the slice.
utils/text.js-41- */
utils/text.js-42-export function ownedSlice(text, start, end = text.length) {
utils/text.js-43-    return `${text.slice(start, end)} `.slice(0, -1);
utils/text.js-44-}
utils/text.js-45-//# sourceMappingURL=text.js.map
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd <local path> && grep -c "" models.generated.js; grep -n -m5 "MidConvo" models.generated.js; grep -o "supportsMidConvo[A-Za-z]*" models.generated.js | sort | uniq -c; grep -rn "MidConvoToolAdditions\|kimi" model-catalog.js models.js providers/*.js 2>/dev/null | head -20
````

````
177
providers/all.js:19:import { kimiCodingProvider } from "./kimi-coding.js";
providers/all.js:100:        kimiCodingProvider(),
providers/compat-schema.js:186:    supportsMidConvoToolAdditions: opt(bool({
providers/kimi-coding.js:5:import { KIMI_CODING_MODELS } from "./kimi-coding.models.js";
providers/kimi-coding.js:6:export function kimiCodingProvider() {
providers/kimi-coding.js:8:        id: "kimi-coding",
providers/kimi-coding.js:10:        baseUrl: "https://api.kimi.com/coding/v1",
providers/kimi-coding.js:24://# sourceMappingURL=kimi-coding.js.map
providers/kimi-coding.models.js:3:import values from "./data/kimi-coding.json" with { type: "json" };
providers/kimi-coding.models.js:5:export const KIMI_CODING_MODELS = flattenChatModelCatalog("kimi-coding", values);
providers/kimi-coding.models.js:6:export const KIMI_CODING_IMAGE_MODELS = flattenImageModelCatalog("kimi-coding", values);
providers/kimi-coding.models.js:7:export const KIMI_CODING_CLASSIFIER_MODELS = flattenClassifierModelCatalog("kimi-coding", values);
providers/kimi-coding.models.js:8://# sourceMappingURL=kimi-coding.models.js.map
Shell cwd was reset to <local path>
````

**[agent]**

Каталог моделей лежит в `providers/data/*.json` — считаю флаги там.

**[command]** exit=0

````
cd <local path> && ls | head -80; for f in supportsMidConvoToolAdditions supportsMidConvoToolChanges supportsMidConvoSystemMessages supportsAdditionalTools supportsToolSearch; do echo "== $f"; grep -l "\"$f\": *true\|\"$f\":true" *.json | tr '\n' ' '; echo; done
````

````
amazon-bedrock.json
ant-ling.json
anthropic.json
azure.json
baseten.json
cerebras.json
cloudflare-ai-gateway.json
cloudflare-workers-ai.json
deepseek.json
fireworks.json
github-copilot.json
google-vertex.json
google.json
groq.json
huggingface.json
kimi-coding.json
meta.json
minimax-cn.json
minimax.json
mistral.json
moonshotai-cn.json
moonshotai.json
nvidia.json
openai-codex.json
openai.json
opencode-go.json
opencode.json
openrouter.json
qwen-token-plan-cn.json
qwen-token-plan-individual.json
qwen-token-plan.json
radius.json
together.json
typesafe.json
vercel-ai-gateway.json
xai.json
xiaomi-token-plan-ams.json
xiaomi-token-plan-cn.json
xiaomi-token-plan-sgp.json
xiaomi.json
zai-coding-cn.json
zai.json
== supportsMidConvoToolAdditions
fireworks.json kimi-coding.json moonshotai.json opencode-go.json moonshotai-cn.json opencode.json 
== supportsMidConvoToolChanges
anthropic.json 
== supportsMidConvoSystemMessages
anthropic.json deepseek.json github-copilot.json moonshotai-cn.json openai.json opencode.json azure.json fireworks.json kimi-coding.json moonshotai.json openai-codex.json opencode-go.json openrouter.json 
== supportsAdditionalTools
github-copilot.json openai.json opencode.json openai-codex.json opencode-go.json 
== supportsToolSearch
openai-codex.json openai.json
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd <local path> && bun --install=force run - <<'TS'
import { readdirSync, readFileSync } from "fs";
const flags = ["supportsMidConvoToolAdditions","supportsMidConvoToolChanges","supportsAdditionalTools","supportsToolSearch","supportsMidConvoSystemMessages"];
const out: Record<string, Set<string>> = Object.fromEntries(flags.map(f => [f, new Set<string>()]));
function walk(o: any, file: string, path: string[]) {
  if (o && typeof o === "object") {
    for (const f of flags) if (o.compat?.[f] === true) out[f].add(`${file}:${o.id ?? path.at(-1)}`);
    for (const [k, v] of Object.entries(o)) walk(v, file, [...path, k]);
  }
}
for (const f of readdirSync(".")) walk(JSON.parse(readFileSync(f, "utf8")), f.replace(".json",""), []);
for (const f of flags) { const a=[...out[f]]; console.log(`== ${f} (${a.length})`); console.log(a.slice(0,25).join(", ")); }
TS
````

````
== supportsMidConvoToolAdditions (17)
moonshotai-cn:kimi-k3, moonshotai-cn:kimi-k3.1-pro, moonshotai-cn:kimi-k3.1-pro-highspeed, kimi-coding:k3, kimi-coding:k3-256k, kimi-coding:k3.1-pro, kimi-coding:k3.1-pro-highspeed, kimi-coding:kimi-for-coding, opencode-go:kimi-k3, opencode-go:kimi-k3.1-pro, fireworks:accounts/fireworks/models/kimi-k3, fireworks:accounts/fireworks/routers/kimi-k3-fast, fireworks:accounts/fireworks/routers/kimi-k3-spot, opencode:kimi-k3, moonshotai:kimi-k3, moonshotai:kimi-k3.1-pro, moonshotai:kimi-k3.1-pro-highspeed
== supportsMidConvoToolChanges (7)
anthropic:claude-fable-5, anthropic:claude-fable-5-1, anthropic:claude-haiku-5-5, anthropic:claude-opus-4-8, anthropic:claude-opus-5, anthropic:claude-opus-5-5, anthropic:claude-sonnet-5-5
== supportsAdditionalTools (33)
github-copilot:gpt-5.6-luna, github-copilot:gpt-5.6-sol, github-copilot:gpt-5.6-terra, github-copilot:gpt-6-astra, github-copilot:gpt-6-luna, github-copilot:gpt-6-sol, github-copilot:gpt-6.1-sol, github-copilot:gpt-6.1-terra, openai:gpt-5.6-luna, openai:gpt-5.6-sol, openai:gpt-5.6-terra, openai:gpt-6-astra, openai:gpt-6-luna, openai:gpt-6-sol, openai:gpt-6.1-sol, openai:gpt-6.1-terra, opencode-go:gpt-5.6-luna, opencode-go:gpt-6-luna, openai-codex:gpt-5.6-luna, openai-codex:gpt-5.6-sol, openai-codex:gpt-5.6-terra, openai-codex:gpt-6-astra, openai-codex:gpt-6-luna, openai-codex:gpt-6-sol, openai-codex:gpt-6.1-sol
== supportsToolSearch (16)
openai:gpt-5.6-luna, openai:gpt-5.6-sol, openai:gpt-5.6-terra, openai:gpt-6-astra, openai:gpt-6-luna, openai:gpt-6-sol, openai:gpt-6.1-sol, openai:gpt-6.1-terra, openai-codex:gpt-5.6-luna, openai-codex:gpt-5.6-sol, openai-codex:gpt-5.6-terra, openai-codex:gpt-6-astra, openai-codex:gpt-6-luna, openai-codex:gpt-6-sol, openai-codex:gpt-6.1-sol, openai-codex:gpt-6.1-terra
== supportsMidConvoSystemMessages (101)
github-copilot:claude-fable-5, github-copilot:claude-fable-5.1, github-copilot:claude-haiku-5.5, github-copilot:claude-opus-4.8, github-copilot:claude-opus-5, github-copilot:claude-opus-5.5, github-copilot:claude-sonnet-5.5, github-copilot:kimi-k3, github-copilot:gpt-5.6-luna, github-copilot:gpt-5.6-sol, github-copilot:gpt-5.6-terra, github-copilot:gpt-6-astra, github-copilot:gpt-6-luna, github-copilot:gpt-6-sol, github-copilot:gpt-6.1-sol, github-copilot:gpt-6.1-terra, moonshotai-cn:kimi-k2.6, moonshotai-cn:kimi-k2.7-code, moonshotai-cn:kimi-k2.7-code-highspeed, moonshotai-cn:kimi-k3, moonshotai-cn:kimi-k3.1-pro, moonshotai-cn:kimi-k3.1-pro-highspeed, openai:gpt-5.4, openai:gpt-5.4-mini, openai:gpt-5.4-pro
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
Next I'm searching the anthropic-messages and openai-responses code for the tool-related identifiers: tool_addition, tool_definition, additional_tools, tool_search, defer_loading, and tool_reference.
````
</details>

<details><summary>reasoning</summary>

````
Сейчас проверю нативные пути у Anthropic и OpenAI Responses, включая использование `defer_loading` и `tool_reference`.
````
</details>

**[command]** exit=0

````
cd <local path> && grep -rnE "defer_loading|tool_reference|tool_search_tool|advanced-tool-use|tool-search" . --include=*.js | head; echo ===ANTH; grep -nE "tool_addition|tool_removal|tool_definition|MidConvoToolChanges|MidConvoSystem|resolveTranscriptTools|cache_control" api/anthropic-messages.js | head -50
````

````
api/openai-responses-shared.js:353:                ...(options?.toolSearchResult ? { defer_loading: true } : {}),
api/openai-responses-shared.js:363:            ...(options?.toolSearchResult ? { defer_loading: true } : {}),
api/anthropic-messages.js:136:    defer_loading: true,
api/anthropic-messages.js:1064:                        tool: { type: "tool_reference", name: isOAuthToken ? toClaudeCodeName(tool.name) : tool.name },
===ANTH
152:        supportsMidConvoSystemMessages: model.compat?.supportsMidConvoSystemMessages ?? false,
153:        supportsMidConvoToolChanges: model.compat?.supportsMidConvoToolChanges ?? false,
380:    const normalizedContext = resolveTranscript(context, getAnthropicCompat(model).supportsMidConvoSystemMessages);
885:    // by value in a `tool_addition` block, which also expresses same-name redefinitions.
897:    const nativeToolChanges = compat.supportsMidConvoSystemMessages && compat.supportsMidConvoToolChanges && initialTools.length > 0;
917:                ...(cacheControl ? { cache_control: cacheControl } : {}),
924:                ...(cacheControl ? { cache_control: cacheControl } : {}),
934:                ...(cacheControl ? { cache_control: cacheControl } : {}),
949:        // `tool_addition` blocks and withdrawn by `tool_removal`, so the cached prefix survives
1030:/** Converts tool definitions for native `tool_addition` blocks; undefined when tool changes are not native. */
1063:                        type: "tool_removal",
1068:                    blocks.push({ type: "tool_addition", tool: { type: "tool_definition", definition } });
1205:    // Add cache_control to the last user or system message to cache conversation history
1215:                        lastBlock.type === "tool_addition" ||
1216:                        lastBlock.type === "tool_removal")) {
1217:                    lastBlock.cache_control = cacheControl;
1225:                        cache_control: cacheControl,
1313:            ...(cacheControl && index === tools.length - 1 ? { cache_control: cacheControl } : {}),
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd <local path> && sed -n 120,160p anthropic-messages.js && echo ---- && sed -n 875,1080p anthropic-messages.js
````

````
const INTERLEAVED_THINKING_BETA = "interleaved-thinking-2025-05-14";
const SERVER_SIDE_FALLBACK_BETA = "server-side-fallback-2026-07-01";
const MID_CONVERSATION_OUTPUT_CONFIG_BETA = "mid-conversation-output-config-2026-07-01";
const THINKING_BINDING_CONTROLS_BETA = "thinking-binding-controls-2026-08-01";
const INLINE_TOOLS_BETA = "inline-tools-2026-09-15";
/**
 * Stable deferred tool declared whenever native tool changes are in use. Anthropic adds
 * hidden prompt scaffolding for mid-conversation tool changes; declaring this placeholder
 * from the first request keeps that scaffolding in the cached prefix, so the first tool
 * change does not invalidate the cache (measured: full miss without it). It is never
 * activated and the model cannot see it.
 */
const DEFERRED_TOOL_PLACEHOLDER = {
    name: "__pi_deferred_placeholder__",
    description: "Reserved placeholder. Never available. Never call this.",
    input_schema: { type: "object", properties: {}, required: [] },
    defer_loading: true,
};
function shouldUseServerSideFallbackBeta(model) {
    return (model.compat?.allowedFallbackModels?.length ?? 0) > 0;
}
function getAnthropicCompat(model) {
    const isOpenRouter = model.provider === "openrouter" || model.baseUrl.includes("openrouter.ai");
    return {
        supportsEagerToolInputStreaming: model.compat?.supportsEagerToolInputStreaming ?? true,
        supportsLongCacheRetention: model.compat?.supportsLongCacheRetention ?? true,
        sendSessionAffinityHeaders: model.compat?.sendSessionAffinityHeaders ?? isOpenRouter,
        sessionAffinityFormat: model.compat?.sessionAffinityFormat ?? (isOpenRouter ? "openrouter" : undefined),
        supportsCacheControlOnTools: model.compat?.supportsCacheControlOnTools ?? true,
        supportsTemperature: model.compat?.supportsTemperature ?? true,
        allowEmptySignature: model.compat?.allowEmptySignature ?? false,
        supportsStrictTools: model.compat?.supportsStrictTools ?? false,
        supportsMidConvoSystemMessages: model.compat?.supportsMidConvoSystemMessages ?? false,
        supportsMidConvoToolChanges: model.compat?.supportsMidConvoToolChanges ?? false,
    };
}
function mergeHeaders(...headerSources) {
    const merged = {};
    for (const headers of headerSources) {
        if (headers) {
            Object.assign(merged, headers);
----
    return [...new Set(features)];
}
function buildParams(model, context, isOAuthToken, options, disablePreferredStrictTools = false) {
    const { cacheControl } = getCacheControl(model, options?.cacheRetention, options?.env);
    const compat = getAnthropicCompat(model);
    const initialSystemMessage = getInitialSystemMessage(context.messages);
    const initialSystemText = initialSystemMessage ? getSystemMessageText(initialSystemMessage) : "";
    const transformedMessages = transformMessages(context.messages, model, normalizeToolCallId);
    const conversationMessages = initialSystemMessage ? transformedMessages.slice(1) : transformedMessages;
    // Native tool changes keep the request-level tool list fixed and define every later tool
    // by value in a `tool_addition` block, which also expresses same-name redefinitions.
    // Anthropic rejects a tool list where every tool is deferred, so there must be an initial
    // active tool to anchor the placeholder. Otherwise the current tool list is sent.
    let hasPreferredStrictTools = false;
    const convertToolDefinitions = (tools, toolCacheControl) => {
        const definitions = convertTools(tools, isOAuthToken, compat.supportsEagerToolInputStreaming, compat.supportsStrictTools, toolCacheControl, disablePreferredStrictTools);
        if (definitions.some((definition, index) => definition.strict === true && prefersJsonSchemaStrictSampling(tools[index]))) {
            hasPreferredStrictTools = true;
        }
        return definitions;
    };
    const initialTools = initialSystemMessage?.toolsAdded ?? [];
    const nativeToolChanges = compat.supportsMidConvoSy
… [9163 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm looking at how Anthropic's inline-tools beta works, where tool changes get slipped into system messages mid-conversation, and noting that it doesn't use the usual regex tool search, only a defer_loading placeholder. Next I'll turn to OpenAI's responses API and its additional_tools and tool_search options.
````
</details>

<details><summary>reasoning</summary>

````
Anthropic-путём беру бету inline-tools с фиксированным tools[] и defer_loading, а изменения инструментов передаю через блоки в системных сообщениях; сейчас смотрю OpenAI Responses.
````
</details>

**[command]** exit=0

````
cd <local path> && grep -nE "additional_tools|tool_search|toolSearch|defer_loading|supportsAdditionalTools|supportsToolSearch|resolveTranscriptTools|MidConvo" openai-responses-shared.js openai-responses.js openai-codex-responses.js 2>/dev/null | head -50
````

````
openai-responses.js:9:import { getDeclaredTools, resolveTranscript, resolveTranscriptTools } from "../utils/transcript.js";
openai-responses.js:68:        supportsMidConvoSystemMessages: model.compat?.supportsMidConvoSystemMessages ?? false,
openai-responses.js:73:        supportsAdditionalTools: model.compat?.supportsAdditionalTools ?? false,
openai-responses.js:74:        supportsToolSearch: model.compat?.supportsToolSearch ?? false,
openai-responses.js:77:        supportsMidConvoEffort: model.compat?.supportsMidConvoEffort ?? false,
openai-responses.js:82:    if (!compat.supportsMidConvoEffort ||
openai-responses.js:109:    const normalizedContext = resolveTranscript(context, getCompat(model).supportsMidConvoSystemMessages);
openai-responses.js:242:    const transcriptTools = resolveTranscriptTools(context.messages, getResponsesToolSupport(compat));
openai-responses.js:245:        supportsMidConvoSystemMessages: compat.supportsMidConvoSystemMessages,
openai-responses.js:246:        supportsAdditionalTools: compat.supportsAdditionalTools,
openai-responses.js:247:        supportsToolSearch: compat.supportsToolSearch,
openai-responses-shared.js:6:import { resolveTranscript, resolveTranscriptTools } from "../utils/transcript.js";
openai-responses-shared.js:66: * `additional_tools` items accumulate: a later item adds tools and replaces same-name
openai-responses-shared.js:69: * Like Codex, every tool is therefore declared in `additional_tools` items, starting with one
openai-responses-shared.js:74:    if (options.supportsMidConvoSystemMessages && options.supportsAdditionalTools)
openai-responses-shared.js:76:    return options.supportsToolSearch ? "additions" : "none";
openai-responses-shared.js:79: * Precedes every additional_tools item after the first. Without it, models read the latest item as
openai-responses-shared.js:92:    const normalizedContext = resolveTranscript(context, options?.supportsMidConvoSystemMessages);
openai-responses-shared.js:120:    const transcriptTools = resolveTranscriptTools(normalizedContext.messages, toolSupport);
openai-responses-shared.js:136:                type: "additional_tools",
openai-responses-shared.js:147:            type: "tool_search_call",
openai-responses-shared.js:154:            type: "tool_search_output",
openai-responses-shared.js:158:            tools: convertResponsesTools(tools, { ...options?.toolOptions, toolSearchResult: true }),
openai-responses-shared.js:353:                ...(options?.toolSearchResult ? { defer_loading: true } : {}),
openai-responses-shared.js:363:            ...(options?.toolSearchResult ? { defer_loading: true } : {}),
openai-codex-responses.js:11:import { getDeclaredTools, getInitialSystemMessage, normalizeContext, resolveTranscript, resolveTranscriptTools, } from "../utils/transcript.js";
openai-codex-responses.js:146:    const normalizedContext = resolveTranscript(context, model.compat?.supportsMidConvoSystemMessages);
openai-codex-responses.js:374:    const supportsAdditionalTools = model.compat?.supportsAdditionalTools ?? false;
openai-codex-responses.js:375:    const supportsToolSearch = model.compat?.supportsToolSearch ?? false;
openai-codex-responses.js:376:    const transcriptTools = resolveTranscriptTools(context.messages, getResponsesToolSupport({
openai-codex-responses.js:377:        supportsMidConvoSystemMessages: model.compat?.supportsMidConvoSystemMessages ?? false,
openai-codex-responses.js:378:        supportsAdditionalTools,
openai-codex-responses.js:379:        supportsToolSearch,
openai-codex-responses.js:384:        supportsMidConvoSystemMessages: model.compat?.supportsMidConvoSystemMessages ?? false,
openai-codex-responses.js:385:        supportsAdditionalTools,
openai-codex-responses.js:386:        supportsToolSearch,
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd <local path> && sed -n 55,200p openai-responses-shared.js
````

````
image_url: `data:${image.mimeType};base64,${image.data}`,
        });
    }
    return output;
}
// =============================================================================
// Message conversion
// =============================================================================
/**
 * How a Responses transport expresses tool changes.
 *
 * `additional_tools` items accumulate: a later item adds tools and replaces same-name
 * definitions from earlier items, but it cannot replace a top-level tool and cannot remove any
 * tool (verified with strict schemas on the OpenAI, Codex, and Copilot backends, October 2026).
 * Like Codex, every tool is therefore declared in `additional_tools` items, starting with one
 * at the head of the input, and removals are announced as text. Synthetic tool search can
 * only add tools. Without mid-conversation system messages there is nothing to anchor.
 */
export function getResponsesToolSupport(options) {
    if (options.supportsMidConvoSystemMessages && options.supportsAdditionalTools)
        return "changes";
    return options.supportsToolSearch ? "additions" : "none";
}
/**
 * Precedes every additional_tools item after the first. Without it, models read the latest item as
 * the complete tool set once a removal was announced; Codex precedes its incremental tool batches
 * with the same guidance. Restating the tools that are still unavailable keeps smaller models
 * (gpt-5.6-luna, gpt-6-luna) from calling them again after later loads (verified October 2026).
 */
function renderIncrementalToolsNotice(unavailable) {
    const notice = "This is an incremental tools update. Previously declared tools remain available unless explicitly marked unavailable. A tool declared again here is available again, and its latest definition replaces the earlier one.";
    return unavailable.size > 0 ? `${notice}\nStill unavailable: ${[...unavailable].join(", ")}.` : notice;
}
function renderToolRemovalNotice(names) {
    return `The following tools are no longer available. Do not call them:\n${names.map((name) => `- ${name}`).join("\n")}`;
}
export function convertResponsesMessages(model, context, allowedToolCallProviders, options) {
    const normalizedContext = resolveTranscript(context, options?.supportsMidConvoSystemMessages);
    const messages = [];
    const normalizeIdPart = (part) => {
        const sanitized = part.replace(/[^a-zA-Z0-9_-]/g, "_");
        const normalized = sanitized.length > 64 ? sanitized.slice(0, 64) : sanitized;
        return normalized.replace(/_+$/, "");
    };
    const buildForeignResponsesItemId = (itemId) => {
        const normalized = `fc_${shortHash(itemId)}`;
        return normalized.length > 64 ? normalized.slice(0, 64) : normalized;
    };
    const normalizeToolCallId = (id, _targetModel, source) => {
        if (!allowedToolCallProviders.has(model.provider))
            return normalizeIdPart(id);
        if (!id.includes("|"))
            return normalizeIdPart(id);
        const [callId, itemId] = id.split("|");
        const normalizedCallId = normalizeIdPart(callId);
        const isForeignToolCall = source.provider !== model.provider || source.api !== model.api;
        let normalizedItemId = isForeignToolCall ? buildForeignResponsesItemId(itemId) : normalizeIdPart(itemId);
        // OpenAI Responses API requires item id to start with "fc"
        if (!normalizedItemId.startsWith("fc_")) {
            normalizedItemId = normalizeIdPart(`fc_${normalizedItemId}`);
        }
        return `${normalizedCallId}|${normalizedItemId}`;
    };
    const transformedMessages = transformMessages(normalizedContext.messages, model, normalizeToolCallId);
    const toolSupport = getResponsesToolSupport(options ?? {});
    const transcriptTools = resolveTranscriptTools(normalizedContext.messages, toolSupport);
    let declaredAdditionalTools = false;
    /** Tools announced as removed and not declared again since. */
    const unavailableTools = new Set();
    const appendSys
… [3798 more characters truncated]
````

<details><summary>reasoning</summary>

````
I've got a "synthetic tool search" mechanism here: when OpenAI responses support tool search but no additional tools are given, Pi fakes a client-executed tool_search call and output in the input to inject tools marked with defer_loading. Next I want to track down the tool_search extension in the pi-coding-agent dist/extensions, and also find where setActiveTools turns into a system message delta.

I'm checking how the "activated" tool state carries over: the search result says the matches are declared for the next model call, so the next request should include the delta. Next I'll look at the tool-search extension itself.
````
</details>

<details><summary>reasoning</summary>

````
Тут же синтетический tool search для Responses-моделей. Далее разберу встроенный `tool_search` и место, где `setActiveTools` становится system-дельтой.
````
</details>

**[command]** exit=0

````
cd <local path> && ls extensions extensions/* | head -60; grep -rlE "tool_search" --include=*.js . | grep -v bundle | head -20
````

````
extensions/index.d.ts
extensions/index.d.ts.map
extensions/index.js
extensions/index.js.map

extensions:
codemode
index.d.ts
index.d.ts.map
index.js
index.js.map
llama
mcp
tool-search

extensions/codemode:
execute.d.ts
execute.d.ts.map
execute.js
execute.js.map
execute.lazy.d.ts
execute.lazy.d.ts.map
execute.lazy.js
execute.lazy.js.map
index.d.ts
index.d.ts.map
index.js
index.js.map
renderer.d.ts
renderer.d.ts.map
renderer.js
renderer.js.map
tool.d.ts
tool.d.ts.map
tool.js
tool.js.map
worker.d.ts
worker.d.ts.map
worker.js
worker.js.map

extensions/llama:
client.d.ts
client.d.ts.map
client.js
client.js.map
huggingface.d.ts
huggingface.d.ts.map
huggingface.js
huggingface.js.map
index.d.ts
index.d.ts.map
index.js
index.js.map
provider.d.ts
provider.d.ts.map
provider.js
provider.js.map
ui.d.ts
ui.d.ts.map
core/agent-session.js
extensions/codemode/tool.js
extensions/index.js
extensions/mcp/index.js
extensions/tool-search/index.js
extensions/tool-search/tool.js
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd <local path> && wc -l *.js && cat -n index.js && cat -n tool.js
````

````
14 index.js
  254 tool.js
  268 total
     1	/**
     2	 * The `tool_search` tool as an extension. The CLI loads it as a built-in extension; SDK users add
     3	 * `createToolSearchExtension()` to their extension factories.
     4	 *
     5	 * `tool_search` is registered inactive. Activate it with `--tools`, the `defaultTools` setting, or
     6	 * `setActiveTools()`.
     7	 */
     8	import { createToolSearchToolDefinition } from "./tool.js";
     9	export function createToolSearchExtension() {
    10	    return (pi) => {
    11	        pi.registerTool({ ...createToolSearchToolDefinition({ tools: pi }), defaultActive: false });
    12	    };
    13	}
    14	export default createToolSearchExtension();
    15	//# sourceMappingURL=index.js.map     1	/**
     2	 * Tool discovery: a BM25 ranker over tool metadata, shared by `searchTools()` in codemode scripts and
     3	 * the optional `tool_search` tool.
     4	 *
     5	 * `tool_search` searches tools that are not declared to
     6	 * the model (`codemode` and `deferred` exposure) and loads the matches, so they are declared for the
     7	 * next model call. Loading goes through the active tool set, so it is recorded in the transcript
     8	 * like any other tool change and survives `/tree`, resume, and fork on that branch.
     9	 */
    10	import { Type } from "typebox";
    11	export const TOOL_SEARCH_TOOL_NAME = "tool_search";
    12	export const DEFAULT_TOOL_SEARCH_LIMIT = 8;
    13	const wordSegmenter = new Intl.Segmenter(undefined, { granularity: "word" });
    14	const STOP_WORDS = new Set([
    15	    "a",
    16	    "an",
    17	    "and",
    18	    "are",
    19	    "as",
    20	    "at",
    21	    "be",
    22	    "by",
    23	    "for",
    24	    "from",
    25	    "in",
    26	    "is",
    27	    "it",
    28	    "of",
    29	    "on",
    30	    "or",
    31	    "that",
    32	    "the",
    33	    "this",
    34	    "to",
    35	    "with",
    36	]);
    37	/** Naive singular form, so `issues` matches `issue` and `searches` matches `search`. */
    38	function stem(term) {
    39	    if (term.length > 4 && term.endsWith("ies"))
    40	        return `${term.slice(0, -3)}y`;
    41	    if (term.length > 4 && /(ches|shes|sses|xes|zes)$/.test(term))
    42	        return term.slice(0, -2);
    43	    if (term.length > 3 && term.endsWith("s") && !term.endsWith("ss"))
    44	        return term.slice(0, -1);
    45	    return term;
    46	}
    47	/** Unicode word segmentation with identifier boundaries and English stop words/singular forms. */
    48	export function tokenize(text) {
    49	    const normalized = text
    50	        .normalize("NFC")
    51	        .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    52	        .replace(/([A-Z]+)([A-Z][a-z])/g, "$1 $2")
    53	        .toLowerCase()
    54	        .replace(/[^\p{L}\p{M}\p{N}]+/gu, " ");
    55	    // The segmenter costs about 15 times a split. Plain ASCII splits into the same words at spaces, so only other
    56	    // text, such as Chinese written without spaces, goes through it.
    57	    const words = /^[a-z0-9 ]*$/.test(normalized)
    58	        ? normalized.split(" ")
    59	        : Array.from(wordSegmenter.segment(normalized), (segment) => (segment.isWordLike ? segment.segment : ""));
    60	    return words
    61	        .filter((word) => word.length > 0 && !STOP_WORDS.has(word))
    62	        .map((word) => (/^[a-z0-9]+$/.test(word) ? stem(word) : word));
    63	}
    64	function isObject(value) {
    65	    return typeof value === "object" && value !== null && !Array.isArray(value);
    66	}
    67	/** Schema descriptions and property names, recursively. */
    68	function schemaText(schema, parts) {
    69	    if (!isObject(schema))
    70	        return;
    71	    if (typeof schema.description === "string")
    72	        parts.push(schema.description);
    73	    if (isObject(schema.properties)) {
    74	        for (const [name, property] of Object.entries(schema.properties)) {
  
… [10536 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm moving to agent-session.js to find where the system message delta gets appended, and searching core for getToolStateChanges and toolsAdded to trace it.
````
</details>

**[agent]**

Теперь — где `setActiveTools` превращается в персистентное system-сообщение с дельтой (agent-session / pi-agent-core).

**[command]** exit=0

````
cd <local path> && grep -rnE "getToolStateChanges|toolsAdded|toolsRemoved|diffSections|sectionsChanged|createInitialSystemMessage" dist/core/*.js dist/core/**/*.js node_modules/@earendil-works/pi-agent-core/dist/*.js 2>/dev/null | grep -v "\.map:" | head -30
````

````
dist/core/compaction/compaction.js:213:            if (system.toolsAdded)
dist/core/compaction/compaction.js:214:                chars += JSON.stringify(system.toolsAdded).length;
dist/core/agent-session.js:1371:                if (message.role !== "system" || (!message.toolsAdded && !message.toolsRemoved))
dist/core/agent-session.js:1373:                const { toolsAdded, toolsRemoved, ...rest } = message;
dist/core/agent-session.js:1374:                const added = toolsAdded?.filter((tool) => !hidden.has(tool.name)) ?? [];
dist/core/agent-session.js:1375:                const removed = toolsRemoved?.filter((tool) => !hidden.has(tool.name)) ?? [];
dist/core/agent-session.js:1378:                    ...(added.length > 0 ? { toolsAdded: added } : {}),
dist/core/agent-session.js:1379:                    ...(removed.length > 0 ? { toolsRemoved: removed } : {}),
dist/core/agent-session.js:1395:                ...(current?.toolsAdded ? { toolsAdded: current.toolsAdded } : {}),
dist/core/agent-session.js:1419:            .flatMap((message) => [...(message.toolsAdded ?? []), ...(message.toolsRemoved ?? [])])
dist/core/export-html/template.js:381:          ...(msg.toolsAdded || []).map(t => `+${t.name}`),
dist/core/export-html/template.js:382:          ...(msg.toolsRemoved || []).map(t => `-${t.name}`),
dist/core/export-html/template.js:418:              for (const tool of [...(msg.toolsAdded || []), ...(msg.toolsRemoved || [])]) parts.push(tool.name);
dist/core/export-html/template.js:1408:              html += renderToolsList('Available Tools', msg.toolsAdded);
dist/core/export-html/template.js:1413:              html += renderToolsList('Tools Added', msg.toolsAdded);
dist/core/export-html/template.js:1414:              if (msg.toolsRemoved && msg.toolsRemoved.length > 0) {
dist/core/export-html/template.js:1415:                html += `<div class="tools-list"><div class="tools-header">Tools Removed</div><div class="tools-content">${msg.toolsRemoved.map(t => `<div class="tool-item"><span class="tool-item-name">${escapeHtml(t.name)}</span></div>`).join('')}</div></div>`;
node_modules/@earendil-works/pi-agent-core/dist/agent.js:1:import { createInitialSystemMessage, getCurrentSystemMessage, getCurrentSystemPrompt, toToolDeclaration, } from "@earendil-works/pi-ai";
node_modules/@earendil-works/pi-agent-core/dist/agent.js:33:    const initialMessage = createInitialSystemMessage(initialState?.systemPrompt, tools.map(toToolDeclaration));
node_modules/@earendil-works/pi-agent-core/dist/agent-loop.js:5:import { EventStream, getCurrentTools, getToolStateChanges, mergeClientIdentity, normalizeContext, PI_ATTRIBUTION, toToolDeclaration, validateToolArguments, } from "@earendil-works/pi-ai";
node_modules/@earendil-works/pi-agent-core/dist/agent-loop.js:218: * what the model may call. Before each request the difference becomes `toolsAdded` and
node_modules/@earendil-works/pi-agent-core/dist/agent-loop.js:219: * `toolsRemoved` on a system message. When a pending system message exists, its tool fields
node_modules/@earendil-works/pi-agent-core/dist/agent-loop.js:236:    const changes = getToolStateChanges(getCurrentTools([...context.messages, ...baseline]), (context.tools ?? []).map(toToolDeclaration));
node_modules/@earendil-works/pi-agent-core/dist/agent-loop.js:237:    const unchanged = changes.toolsAdded.length === 0 && changes.toolsRemoved.length === 0;
node_modules/@earendil-works/pi-agent-core/dist/agent-loop.js:240:        if (unchanged && !pending.toolsAdded?.length && !pending.toolsRemoved?.length)
node_modules/@earendil-works/pi-agent-core/dist/agent-loop.js:251:const NO_CHANGES = { toolsAdded: [], toolsRemoved: [] };
node_modules/@earendil-works/pi-agent-core/dist/agent-loop.js:253:function withToolChanges(message, { toolsAdded, toolsRemoved }) {
node_modules/@earendil-works/pi-agent-core/dist/agent-loop.js:254:    const { toolsAdded: _added, toolsRemoved: _removed, ...rest } = message;
node_modules/@earendil-works/pi-agent-core/dis
… [343 more characters truncated]
````

**[command]** exit=0

````
cd <local path> && sed -n 150,262p agent-loop.js; grep -n "syncToolState\|appendToolState\|function.*[Tt]oolState" agent-loop.js | head
````

````
message,
                    toolResults: [],
                    context: currentContext,
                    newMessages,
                };
                await config.finishTurn?.(lastCompletedTurn, signal);
                await emit({ type: "turn_end", message, toolResults: [] });
                await emit({ type: "agent_end", messages: newMessages });
                return;
            }
            // Check for tool calls
            const toolCalls = message.content.filter((c) => c.type === "toolCall");
            const toolResults = [];
            hasMoreToolCalls = false;
            if (toolCalls.length > 0) {
                // A "length" stop means the output was cut off by the token limit, so
                // every tool call in the message may carry truncated arguments. Fail
                // them all instead of executing potentially borked calls.
                const executedToolBatch = message.stopReason === "length"
                    ? await failToolCallsFromTruncatedMessage(toolCalls, emit)
                    : await executeToolCalls(currentContext, message, config, signal, emit);
                toolResults.push(...executedToolBatch.messages);
                hasMoreToolCalls = !executedToolBatch.terminate;
                for (const result of toolResults) {
                    currentContext.messages.push(result);
                    newMessages.push(result);
                }
            }
            lastCompletedTurn = {
                message,
                toolResults,
                context: currentContext,
                newMessages,
            };
            const decision = await config.finishTurn?.(lastCompletedTurn, signal);
            await emit({ type: "turn_end", message, toolResults });
            if (decision?.action === "end") {
                await emit({ type: "agent_end", messages: newMessages });
                return;
            }
            explicitContinuation = decision?.action === "continue";
            pendingMessages = (await config.getSteeringMessages?.()) || [];
            if (hasMoreToolCalls || pendingMessages.length > 0) {
                explicitContinuation = false;
            }
        }
        // Agent would stop here. Check for follow-up messages.
        const followUpMessages = (await config.getFollowUpMessages?.()) || [];
        if (followUpMessages.length > 0) {
            // Set as pending so inner loop processes them
            explicitContinuation = false;
            pendingMessages = followUpMessages;
            continue;
        }
        // No natural request was selected, so fulfill the continuation decision with one context-only turn.
        if (explicitContinuation) {
            explicitContinuation = false;
            continue;
        }
        // No more messages, exit
        break;
    }
    await emit({ type: "agent_end", messages: newMessages });
}
/**
 * Declare tool loadout changes to the model.
 *
 * `context.tools` is what the runtime can execute; the transcript's system messages declare
 * what the model may call. Before each request the difference becomes `toolsAdded` and
 * `toolsRemoved` on a system message. When a pending system message exists, its tool fields
 * are treated as intent and replaced with the delta between the committed transcript and
 * the executable set, so replay always yields exactly `context.tools`. Otherwise a new
 * system message is inserted before the first non-system pending message.
 */
function declareToolChanges(context, pendingMessages) {
    let systemIndex = -1;
    for (let i = pendingMessages.length - 1; i >= 0; i--) {
        if (pendingMessages[i].role === "system") {
            systemIndex = i;
            break;
        }
    }
    const pending = pendingMessages[systemIndex];
    const baseline = pending
        ? pendingMessages.map((message, index) => index === systemIndex ? withToolChanges(pending, NO_CHANGES) : message)
        : pendingMessages;
    const change
… [1629 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking where declareToolChanges gets called, since it fires after tool results when the active tools have changed. Then I'll look at the mcp_servers prompt section, the codemode description where deferred tools aren't listed, the CHANGELOG history for these features, and skills, before checking upstream on GitHub.
````
</details>

**[command]** exit=0

````
cd <local path> && grep -n "declareToolChanges" agent-loop.js && sed -n "$(grep -n 'declareToolChanges(' agent-loop.js | sed -n 1p | cut -d: -f1),+3p" agent-loop.js; grep -n "pendingMessages = \|const pending" agent-loop.js | head; sed -n 95,135p agent-loop.js
````

````
49:    const initialMessages = declareToolChanges(context, prompts);
121:            for (const message of declareToolChanges(currentContext, [...preparedMessages, ...pendingMessages])) {
224:function declareToolChanges(context, pendingMessages) {
    const initialMessages = declareToolChanges(context, prompts);
    const newMessages = [...initialMessages];
    const currentContext = {
        ...context,
90:    let pendingMessages = (await config.getSteeringMessages?.()) || [];
116:                    pendingMessages = (await config.getSteeringMessages?.()) || [];
127:            pendingMessages = [];
191:            pendingMessages = (await config.getSteeringMessages?.()) || [];
201:            pendingMessages = followUpMessages;
232:    const pending = pendingMessages[systemIndex];
        while (hasMoreToolCalls || pendingMessages.length > 0) {
            let preparedMessages = [];
            if (lastCompletedTurn) {
                const nextTurnSnapshot = await config.prepareNextTurn?.(lastCompletedTurn);
                if (nextTurnSnapshot) {
                    currentContext = nextTurnSnapshot.context ?? currentContext;
                    preparedMessages = nextTurnSnapshot.messages ?? [];
                    config = {
                        ...config,
                        model: nextTurnSnapshot.model ?? config.model,
                        reasoning: nextTurnSnapshot.thinkingLevel === undefined
                            ? config.reasoning
                            : nextTurnSnapshot.thinkingLevel === "off"
                                ? undefined
                                : nextTurnSnapshot.thinkingLevel,
                    };
                }
                // Preparation can be long-running (for example, compaction). Pick up steering
                // queued while it ran. Only poll again if the earlier poll returned nothing;
                // otherwise one-at-a-time mode would deliver two messages in this turn.
                if (pendingMessages.length === 0) {
                    pendingMessages = (await config.getSteeringMessages?.()) || [];
                }
                await emit({ type: "turn_start" });
            }
            // Process prepared and queued messages before the next assistant response.
            for (const message of declareToolChanges(currentContext, [...preparedMessages, ...pendingMessages])) {
                await emit({ type: "message_start", message });
                await emit({ type: "message_end", message });
                currentContext.messages.push(message);
                newMessages.push(message);
            }
            pendingMessages = [];
            const requestUpdate = await config.prepareRequest?.({
                context: currentContext,
                model: config.model,
                thinkingLevel: config.reasoning ?? "off",
            }, signal);
            if (requestUpdate) {
                currentContext = requestUpdate.context ?? currentContext;
                config = {
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
Next I'm writing the CHANGELOG entries for tool_search, deferred tools, mid-conversation changes, and inline tools. After that comes the skills doc, and then the upstream GitHub work.
````
</details>

**[agent]**

Механика в рантайме понятна. Смотрю CHANGELOG (когда и почему появилось) и коротко — скиллы.

**[command]** exit=0

````
cd <local path> && grep -nE "^## " CHANGELOG.md | head -30; grep -nE "tool_search|deferred|Dynamic Tool|setActiveTools|mid-conversation|toolsAdded|tool_addition|additional_tools|prompt cache|cached prefix|codemode" CHANGELOG.md | head -70
````

````
3:## [1.5.0] - 2026-11-02
119:## [1.4.0] - 2026-10-21
175:## [1.3.0] - 2026-10-15
221:## [1.2.0] - 2026-10-12
284:## [1.1.0] - 2026-10-07
336:## [1.0.4] - 2026-10-05
359:## [1.0.3] - 2026-10-05
386:## [1.0.2] - 2026-10-04
396:## [1.0.1] - 2026-10-03
440:## [1.0.0] - 2026-10-01
486:## [0.99.2] - 2026-09-30
526:## [0.99.1] - 2026-09-29
544:## [0.99.0] - 2026-09-29
623:## [0.87.1] - 2026-09-22
647:## [0.87.0] - 2026-09-21
685:## [0.86.1] - 2026-09-20
707:## [0.86.0] - 2026-09-19
794:## [0.85.1] - 2026-09-05
812:## [0.85.0] - 2026-09-04
861:## [0.84.4] - 2026-08-28
908:## [0.84.3] - 2026-08-24
989:## [0.84.2] - 2026-08-14
1048:## [0.84.1] - 2026-08-07
1079:## [0.84.0] - 2026-08-06
1275:## [0.83.0] - 2026-07-29
1320:## [0.82.1] - 2026-07-25
1347:## [0.82.0] - 2026-07-24
1388:## [0.81.1] - 2026-07-21
1406:## [0.81.0] - 2026-07-21
1448:## [0.80.10] - 2026-07-16
10:- **GPT-6.1 Terra**: available through OpenAI, Azure OpenAI Responses, and OpenAI Codex, with tool search, mid-conversation thinking-level changes, and thinking `off`. Codex offers a 500K context window. See [Models](docs/cli.md#models).
27:- Added GPT-6.1 Terra for OpenAI, Azure OpenAI Responses, and OpenAI Codex, with tool search and mid-conversation thinking-level changes. It supports thinking `off`; Codex offers a 500K context window
46:- Fixed a redundant system prompt update (tools, rules) when an extension set the same active tools in a different order, for example a reversed `pi.setActiveTools()` list. Tools that stay active now keep their order and newly activated tools are appended ([#11495](https://github.com/earendil-works/pi/issues/11495))
68:- Fixed `tool_search` and codemode `searchTools()` ranking a tool below tools that only mention its name in their descriptions, for example `peekaboo app` ranking `mcp__peekaboo__app` 14th. A tool matching more of the query's words now ranks above one matching fewer, a query word in a tool's name scores more than any number of mentions in its description, a tool whose whole name is in the query gets a large bonus, and long server instructions no longer lower the scores of that server's tools ([#11331](https://github.com/earendil-works/pi/issues/11331))
69:- Fixed `tool_search` and codemode `searchTools()` finding nothing for Chinese, Japanese, Thai, and other non-ASCII queries, because the tokenizer kept only ASCII letters and digits. Words in any script now match, text without spaces between words such as `搜索记录` is split into words, and canonically equivalent text such as `café` and `cafe\u0301` matches ([#10816](https://github.com/earendil-works/pi/issues/10816), [#11037](https://github.com/earendil-works/pi/pull/11037) by [@haoqixu](https://github.com/haoqixu))
71:- Fixed tool rows and streamed answers highlighting the same code again on every redraw. A running codemode row highlighted its whole script on every progress update and timer tick, a complete `write` row its whole file on every update and expand toggle, a streamed `write` its first 50 lines on every delta, and a streamed answer every earlier code block on every delta. Rows now reuse their last highlighting until the code, theme, or loaded grammars change, and assistant messages keep their rendered Markdown blocks while streaming ([#10971](https://github.com/earendil-works/pi/issues/10971))
75:- Fixed codemode tool descriptions including entire union and multi-line output types in every request. Object unions now summarize their fields and discriminators; other multi-line types point to `describeTool()` for the full declaration ([#11501](https://github.com/earendil-works/pi/issues/11501))
103:- Fixed Claude mid-conversation thinking-level changes failing with `Invalid effort level` on accounts whose organization caps effort below `high` ([#10063](https://github.com/earendil-works/pi/issues/10063))
104:- Fixed Kimi K3.1 Pro models using Kimi K2 request settings on Kimi Coding, Moonshot, and OpenCode Go. They now send the correct reasoning effort, preserve earli
… [16972 more characters truncated]
````

<details><summary>reasoning</summary>

````
I want to find out when the transcript system-message architecture was introduced, so I'll search the CHANGELOG for "system message" and look at the older entries.
````
</details>

**[command]** exit=0

````
cd <local path> && grep -nE "system messages|SystemMessage|supportsMidConvo|Dynamic tool|dynamic tool|cache miss|invalidat" CHANGELOG.md | head -40
````

````
55:- Fixed HTML export not showing system messages: the system prompt and tools, and later section updates such as after `/reload`. `pi --export` now includes the system prompt and tools too ([#11261](https://github.com/earendil-works/pi/issues/11261), [#3464](https://github.com/earendil-works/pi/issues/3464), [#11290](https://github.com/earendil-works/pi/pull/11290))
181:- **Kimi Code over Chat Completions**: tools added mid-conversation no longer invalidate the prompt cache. `models.json` base URL overrides must now include `/v1`. See [Providers](docs/providers.md).
192:- Changed the `kimi-coding` provider to use OpenAI Chat Completions at `https://api.kimi.com/coding/v1`, the protocol used by the official Kimi Code client. K3, K3-256K, and Kimi For Coding now accept tools added mid-conversation without invalidating the prompt cache. `models.json` overrides of the `kimi-coding` base URL must now include `/v1` ([#10720](https://github.com/earendil-works/pi/issues/10720))
382:- Fixed subscription logins such as Sign in with ChatGPT failing with `refresh_token_invalidated` after a request was cancelled during an OAuth token refresh
668:- Added the `context_with_system` extension event, which runs after `context` handlers on the full transcript including system messages and sends its result verbatim. See [`context_with_system`](docs/extensions.md#context_with_system).
677:- Fixed `context` handlers that filter or slice messages dropping the prompt and tool declarations, which after extension-driven compaction left requests without built-in tools or made Codex emit raw tool-call text. Handlers no longer see system messages; Pi restores the prompt and tool state after they run. See [`context`](docs/extensions.md#context) ([#9789](https://github.com/earendil-works/pi/issues/9789), [#9822](https://github.com/earendil-works/pi/issues/9822)).
781:- Fixed `before_agent_start` handlers returning `systemPrompt` (and `forceSystemPrompt`) on models with mid-conversation system messages: the forced prompt is now sent as the provider's leading system prompt instead of being appended as a section patch after the original prompt.
873:- Added `supportsMidConvoEffort` to custom Anthropic Messages model compatibility settings.
874:- Added transcript notices for Anthropic thinking blocks dropped during provider recovery when cache miss notices are enabled.
878:- Added transcript usage notices for compaction and branch summaries when cache miss notices are enabled.
925:- Added transcript usage notices for compaction and branch summaries when cache miss notices are enabled.
1533:- **Cache-friendly dynamic tool loading** - Extensions can add tools during execution while supported Anthropic and OpenAI Responses models preserve prompt-cache prefixes. See [Dynamic Tool Loading](docs/extensions.md#dynamic-tool-loading).
1539:- Added cache-friendly dynamic tool loading for extension tools activated by tool results. Supported Anthropic and OpenAI Responses models load definitions where they become available, preserving the cached prompt prefix. See [Dynamic Tool Loading](docs/extensions.md#dynamic-tool-loading) ([#6474](https://github.com/earendil-works/pi-mono/pull/6474)).
1560:- Fixed system prompt cache invalidation across dates by removing the current date from the default prompt ([#6621](https://github.com/earendil-works/pi/issues/6621)).
1588:- **Prompt cache miss visibility** - Significant cache misses can be shown in transcripts via `showCacheMissNotices`. See [Model & Thinking](docs/settings.md#model--thinking).
1607:- Added a `showCacheMissNotices` setting and `/settings` toggle for significant prompt-cache miss transcript notices.
2617:- Fixed session replacement and `/quit` teardown ordering to run host-owned extension UI cleanup synchronously after `session_shutdown` handlers complete but before invalidating the old extension context, preventing stale extension UI from rendering against a disposed session ([#3597](https://github.com/badlogic/p
… [1730 more characters truncated]
````

**[command]** exit=0

````
cd <local path> && awk 'NR<1533 && /^## /{h=$0} NR==1533{print h}' CHANGELOG.md; awk 'NR<4730 && /^## /{h=$0} NR==4730{print h}' CHANGELOG.md; awk 'NR<556 && /^## /{h=$0} NR==556{print h}' CHANGELOG.md; awk 'NR<418 && /^## /{h=$0} NR==418{print h}' CHANGELOG.md; awk 'NR<169 && /^## /{h=$0} NR==169{print h}' CHANGELOG.md; awk 'NR<506 && /^## /{h=$0} NR==506{print h}' CHANGELOG.md; sed -n 1,93p docs/skills.md | head -60
````

````
## [0.80.7] - 2026-07-14
## [0.39.0] - 2026-01-08
## [0.99.0] - 2026-09-29
## [1.0.1] - 2026-10-03
## [1.4.0] - 2026-10-21
## [0.99.2] - 2026-09-30
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
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
Next I'm checking the 0.80.7 changelog for details on #6474, then the matching PR in the pi-mono upstream. I'll also look at the earendil-works/pi repo on GitHub. First I need to see whether `gh` is available, so I can use `gh api` to pull the releases, the latest version, and the relevant files. Nothing private is involved, since these are public repo names.
````
</details>

**[agent]**

Локальная картина собрана. Сверяюсь с upstream на GitHub: последняя версия и изменения после 1.5.0 по этой теме.

**[command]** exit=0

````
gh api repos/earendil-works/pi --jq '{full_name,default_branch,pushed_at}' 2>&1 | head; gh api repos/earendil-works/pi/releases --jq '.[0:5][] | {tag_name,published_at}' 2>&1 | head -20; gh api 'repos/earendil-works/pi/commits?per_page=1' --jq '.[0] | {sha, date: .commit.author.date, msg: .commit.message[0:100]}'
````

````
{"default_branch":"main","full_name":"earendil-works/pi","pushed_at":"2026-11-23T23:55:45Z"}
{"published_at":"2026-11-20T11:35:03Z","tag_name":"v1.6.0"}
{"published_at":"2026-11-10T12:25:43Z","tag_name":"v1.5.2"}
{"published_at":"2026-11-09T23:47:44Z","tag_name":"v1.5.1"}
{"published_at":"2026-11-02T11:05:31Z","tag_name":"v1.5.0"}
{"published_at":"2026-10-21T22:49:48Z","tag_name":"v1.4.0"}
{"date":"2026-11-23T23:55:42Z","msg":"fix(coding-agent): correct the fallbacks for unsaved bash output files (#12461)\n\nFollow-up to #12452","sha":"8209929fb553e7a8c91dc0894569f9ec43dd201f"}
````

**[agent]**

Upstream ушёл вперёд до v1.6.0 + коммиты main. Смотрю CHANGELOG main выше 1.5.0 по релевантным словам.

**[command]** exit=0

````
mkdir -p /tmp/pi-upstream && cd /tmp/pi-upstream && gh api repos/earendil-works/pi/contents/packages/coding-agent/CHANGELOG.md -H "Accept: application/vnd.github.raw" > CHANGELOG.md && grep -nE "^## " CHANGELOG.md | head -6 && L=$(grep -n "^## \[1.5.0\]" CHANGELOG.md | cut -d: -f1) && head -n $L CHANGELOG.md | grep -niE "tool_search|deferred|tool search|mid-conversation|toolsAdded|tool_addition|additional_tools|cache|setActiveTools|exposure|loadout|codemode" | head -40
````

````
3:## [Unreleased]
30:## [1.6.0] - 2026-11-20
112:## [1.5.2] - 2026-11-10
127:## [1.5.1] - 2026-11-09
243:## [1.5.0] - 2026-11-02
360:## [1.4.0] - 2026-10-21
26:- Fixed `/login` showing a provider as configured when its stored `auth.json` key is a `!command` that fails, while requests failed with `No API key found`. `/login` now shows `stored key did not resolve`, `getProviderAuthStatus()` returns `{ configured: false, source: "stored" }`, and entering the same `!command` again in `/login` runs it again instead of reusing the cached failure ([#12164](https://github.com/earendil-works/pi/issues/12164))
38:- Extension components: `render()` now returns `readonly string[]`, and `Container` returns the same cached array while its children are unchanged. Extensions that modify render output in place, including `super.render()` in a `Container` subclass or an embedded component's output, must copy it first ([#9549](https://github.com/earendil-works/pi/issues/9549))
45:- Added a transcript notice when OpenAI drops reasoning items from a request, such as `OpenAI dropped 2 reasoning items: prefix_mismatch (details in session)` after compaction on GPT-6.2. Like the Anthropic thinking notice, it is shown when `showCacheMissNotices` is on and only when more items are dropped than in the previous response. Both notices now name the reasons
60:- Fixed MCP tools loaded by `tool_search` being dropped on resume and `/reload` when an extension deactivates only its own tool at `session_start`, as pi-web-access and pi-subagents do in `toolActivation: "auto"` mode ([#11996](https://github.com/earendil-works/pi/issues/11996))
71:- Fixed Groq Qwen models failing with `400 Unexpected message role`; OpenAI-compatible providers other than OpenAI now receive system messages (the system prompt and mid-conversation system messages) with the `system` role ([#10741](https://github.com/earendil-works/pi/issues/10741))
90:- Fixed changing the thinking level on the `openai-codex` provider invalidating the prompt cache on GPT-6 models ([#12269](https://github.com/earendil-works/pi/issues/12269))
101:- Fixed the `openai-codex` provider getting almost no prompt cache hits for the system prompt on GPT-6.2 models ([#12273](https://github.com/earendil-works/pi/issues/12273))
132:- **Idle prompt cache warming**: eligible caches now stay warm for up to 30 minutes between runs when a refresh is expected to pay for itself. See [`cacheWarming`](docs/settings.md#model-and-thinking).
135:- **GitHub Copilot classifiers**: call Microsoft-Decision-1 through codemode `models.classify()` for typed decisions and probabilities. See [Use classifier models](docs/models.md#use-classifier-models).
146:- Anthropic sessions now use message threads: each request sends only the new messages and the server continues from the previous reply, falling back to the full request when the conversation changed (for example after compaction or a tool list change). On by default for the `anthropic` provider on `api.anthropic.com`; set `compat.supportsMessageThreads` in `models.json` to enable it for gateways that forward the `thread` field, or to turn it off. Cache warming does not touch the session's thread ([#11545](https://github.com/earendil-works/pi/pull/11545))
151:- Added Microsoft-Decision-1 classifier support through GitHub Copilot, including codemode `models.classify()` ([#11679](https://github.com/earendil-works/pi/pull/11679) by [@Marvae](https://github.com/Marvae))
152:- Added `compat.promptCacheKeyMode` (`"auto"`, `"enabled"`, or `"disabled"`) to enable prompt cache keys for compatible proxies or omit them for endpoints that reject them. Set it in `models.json` when using pi ([#9442](https://github.com/earendil-works/pi/pull/9442) by [@dannote](https://github.com/dannote))
156:- Added Claude Fable 5.2 (`claude-fable-5-2`) to the `anthropic` provider ($8/$40 per million input/output tokens, 1M context, 128K output). Like Fable 5.1 it uses per-message effort and mid-conversation system m
… [2366 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking upstream main's transcript.ts and openai-completions.ts against the local 1.5.0 copy, especially the system role change for non-OpenAI providers. I also want to note the Anthropic thread about falling back to a full request when the tool list changes. Then I'll fetch the upstream transcript.ts and grep openai-completions.ts for the kimi tool message, so I can cite exact source lines and permalinks at a fixed commit SHA.
````
</details>

<details><summary>reasoning</summary>

````
Апстрим-изменения по теме мелкие. Сейчас скачиваю исходники TS с main на нужном коммите, чтобы сослаться на строки.
````
</details>

**[command]** exit=0

````
cd /tmp/pi-upstream && SHA=8209929fb553e7a8c91dc0894569f9ec43dd201f && for p in packages/ai/src/utils/transcript.ts packages/ai/src/api/openai-completions.ts packages/ai/src/api/anthropic-messages.ts packages/ai/src/api/openai-responses-shared.ts packages/agent/src/agent-loop.ts packages/coding-agent/src/extensions/tool-search/tool.ts; do f=$(echo $p | tr / _); gh api "repos/earendil-works/pi/contents/$p?ref=$SHA" -H "Accept: application/vnd.github.raw" > $f 2>/dev/null; echo "$p $(wc -l < $f)"; done
````

````
packages/ai/src/utils/transcript.ts 263
packages/ai/src/api/openai-completions.ts 1742
packages/ai/src/api/anthropic-messages.ts 1969
packages/ai/src/api/openai-responses-shared.ts 963
packages/agent/src/agent-loop.ts 952
packages/coding-agent/src/extensions/tool-search/tool.ts 349
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd /tmp/pi-upstream && grep -nE "^export function (resolveTranscriptTools|getCurrentTools|collapseSystemMessages|resolveTranscript|getToolStateChanges)|findLastNonAdditiveToolChange\(" packages_ai_src_utils_transcript.ts; echo ---; grep -nE "resolveTranscriptTools\(|kimiToolMessage|tools: convertTools\(addedTools|supportsMidConvoToolAdditions: false|params.tools = convertTools\(transcriptTools|const instructionRole|renderSystemMessageUpdate\(msg\)|thread" packages_ai_src_api_openai-completions.ts | head -20; echo ---; grep -nE "DEFERRED_TOOL_PLACEHOLDER =|INLINE_TOOLS_BETA =|const nativeToolChanges|params.tools = \[\.\.\.convertToolDefinitions|type: \"tool_removal\"|type: \"tool_addition\"|supportsMessageThreads" packages_ai_src_api_anthropic-messages.ts | head -20; echo ---; grep -nE "export function getResponsesToolSupport|type: \"additional_tools\"|type: \"tool_search_call\"|type: \"tool_search_output\"|defer_loading|function renderIncrementalToolsNotice" packages_ai_src_api_openai-responses-shared.ts; echo ---; grep -nE "^function declareToolChanges|declareToolChanges\(" packages_agent_src_agent-loop.ts; echo ---; grep -nE "function searchAndLoad|setActiveTools|TOOL_SEARCH_DESCRIPTION =|exposure: \"model-only\"|class Bm25Ranker|They are available from your next call" packages_coding-agent_src_extensions_tool-search_tool.ts
````

````
58:export function getCurrentTools(messages: TranscriptMessages): Tool[] {
108:export function collapseSystemMessages(context: TranscriptContext): TranscriptContext {
115:export function resolveTranscript(
150:export function getToolStateChanges(previous: readonly Tool[], current: readonly Tool[]): ToolStateChanges {
201:	return findLastNonAdditiveToolChange(messages.filter(isSystemMessage)) >= 0;
205:function findLastNonAdditiveToolChange(systemMessages: readonly SystemMessage[]): number {
252:export function resolveTranscriptTools(messages: TranscriptMessages, support: TranscriptToolSupport): TranscriptTools {
260:		findLastNonAdditiveToolChange(systemMessages) + 1,
---
798:	const transcriptTools = resolveTranscriptTools(
848:		params.tools = convertTools(transcriptTools.requestTools, compat);
1220:	const transcriptTools = resolveTranscriptTools(
1226:	const instructionRole = model.reasoning && compat.supportsDeveloperRole ? "developer" : "system";
1246:				const kimiToolMessage: KimiToolSystemMessageParam = {
1248:					tools: convertTools(addedTools, compat),
1250:				params.push(kimiToolMessage as unknown as ChatCompletionMessageParam);
1252:			const text = i === 0 ? getSystemMessageText(msg) : renderSystemMessageUpdate(msg);
1682:		supportsMidConvoToolAdditions: false,
---
212:const INLINE_TOOLS_BETA = "inline-tools-2026-09-15";
249:		supportsMessageThreads: model.compat?.supportsMessageThreads ?? model.baseUrl.includes("api.anthropic.com"),
847:			const threadSessionId = compat.supportsMessageThreads ? cacheSessionId : undefined;
1460:	const nativeToolChanges =
1531:		params.tools = [...convertToolDefinitions(initialTools, toolCacheControl), DEFERRED_TOOL_PLACEHOLDER];
1657:						type: "tool_removal",
1662:					blocks.push({ type: "tool_addition", tool: { type: "tool_definition", definition } });
---
168:export function getResponsesToolSupport(options: {
183:function renderIncrementalToolsNotice(unavailable: ReadonlySet<string>): string {
269:				type: "additional_tools",
279:			type: "tool_search_call",
286:			type: "tool_search_output",
498:				...(options?.toolSearchResult ? { defer_loading: true } : {}),
511:			...(options?.toolSearchResult ? { defer_loading: true } : {}),
---
119:	const initialMessages = declareToolChanges(context, prompts);
220:			for (const message of declareToolChanges(currentContext, [...preparedMessages, ...pendingMessages])) {
342:function declareToolChanges(context: AgentContext, pendingMessages: AgentMessage[]): AgentMessage[] {
---
213:export class Bm25Ranker implements ToolRanker {
288:	tools?: Pick<ExtensionAPI, "getAllTools" | "getActiveTools" | "setActiveTools">;
300:function searchAndLoad(
309:	if (matches.length > 0) tools.setActiveTools([...active, ...matches.map((match) => match.name)]);
320:export const TOOL_SEARCH_DESCRIPTION = `# Tool discovery\n\nSearches over deferred tool metadata with BM25 and exposes matching tools for the next model call.\n\nSome of the tools, such as tools of MCP servers, may not have been provided to you upfront, and you should use this tool (\`${TOOL_SEARCH_TOOL_NAME}\`) to search for the required tools. For MCP tool discovery, always use \`${TOOL_SEARCH_TOOL_NAME}\`.`;
332:		exposure: "model-only",
343:					: `Loaded ${tools.length} tool${tools.length === 1 ? "" : "s"}. They are available from your next call:\n${tools
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm checking the upstream openai-completions code around lines 790-850 for any differences, like promptCacheKeyMode or how the system role is handled. I also want to look at the Anthropic message-thread fallback for when the tool list changes. And I'm wondering whether the "none" fallback for generic OpenAI-compatible endpoints causes a cache miss when the tools array changes, since chat templates often render tools before or inside the system prompt.

Now I'm checking whether the "none" fallback for generic OpenAI-compatible endpoints causes a full cache miss whenever the tools array changes, since chat templates often render tools into the system message at the start, which shifts the prefix. Next I'll look at how the system prompt's tools section gets patched when active tools change, and whether the collapse mode rebuilds the whole prompt.
````
</details>

<details><summary>reasoning</summary>

````
Проверяю, как системный промпт делится на секции (tools, skills, mcp_servers), и upstream-изменения в openai-completions вокруг `tools` и system role.
````
</details>

**[command]** exit=0

````
cd /tmp/pi-upstream && sed -n 790,860p packages_ai_src_api_openai-completions.ts; sed -n 1236,1258p packages_ai_src_api_openai-completions.ts
````

````
options?: OpenAICompletionsOptions,
	compat: ResolvedOpenAICompletionsCompat = getCompat(model),
	cacheRetention: CacheRetention = resolveCacheRetention(options?.cacheRetention, options?.env),
	grammarToolInputProperties: ReadonlyMap<string, string> = createGrammarToolInputProperties(
		getDeclaredTools(context.messages),
		compat.supportsOpenAIGrammarTools,
	),
) {
	const transcriptTools = resolveTranscriptTools(
		context.messages,
		compat.supportsMidConvoSystemMessages === true && compat.supportsMidConvoToolAdditions === true
			? "additions"
			: "none",
	);
	const messages = convertMessages(model, context, compat, {
		grammarToolInputProperties,
	});
	const cacheControl = getCompatCacheControl(compat, cacheRetention);
	const promptCacheKeyMode = compat.promptCacheKeyMode ?? "auto";
	const supportsPromptCacheKey =
		promptCacheKeyMode === "enabled" ||
		(promptCacheKeyMode === "auto" &&
			(model.baseUrl.includes("api.openai.com") ||
				(cacheRetention === "long" && compat.supportsLongCacheRetention)));

	const params: OpenAI.Chat.Completions.ChatCompletionCreateParamsStreaming = {
		model: model.id,
		messages,
		stream: true,
		prompt_cache_key:
			cacheRetention !== "none" && supportsPromptCacheKey
				? clampOpenAIPromptCacheKey(options?.sessionId)
				: undefined,
		prompt_cache_retention: cacheRetention === "long" && compat.supportsLongCacheRetention ? "24h" : undefined,
	};

	if (compat.supportsUsageInStreaming !== false) {
		params.stream_options = { include_usage: true };
	}

	if (compat.supportsStore) {
		params.store = false;
	}

	if (options?.maxTokens) {
		if (compat.maxTokensField === "max_tokens") {
			// Deprecated by OpenAI, but some OpenAI-compatible providers only accept max_tokens.
			(params as { max_tokens?: number }).max_tokens = options.maxTokens;
		} else {
			params.max_completion_tokens = options.maxTokens;
		}
	}

	if (options?.temperature !== undefined) {
		params.temperature = options.temperature;
	}

	if (transcriptTools.requestTools.length > 0) {
		params.tools = convertTools(transcriptTools.requestTools, compat);
		if (compat.zaiToolStream) {
			(params as any).tool_stream = true;
		}
	} else if (compat.requiresToolsWithToolHistory && hasToolHistory(context.messages)) {
		params.tools = [];
	}

	if (cacheControl) {
		applyAnthropicCacheControl(messages, params.tools, cacheControl);
	}

	if (options?.toolChoice) {
			params.push({
				role: "assistant",
				content: "I have processed the tool results.",
			});
		}

		if (msg.role === "system") {
			// transformMessages keeps system messages in order, so their position matches the transcript.
			const addedTools = systemIndex++ >= transcriptTools.foldedSystemMessages ? (msg.toolsAdded ?? []) : [];
			if (addedTools.length > 0) {
				const kimiToolMessage: KimiToolSystemMessageParam = {
					role: "system",
					tools: convertTools(addedTools, compat),
				};
				params.push(kimiToolMessage as unknown as ChatCompletionMessageParam);
			}
			const text = i === 0 ? getSystemMessageText(msg) : renderSystemMessageUpdate(msg);
			if (text.length > 0) {
				params.push({ role: instructionRole, content: sanitizeSurrogates(text) });
			}
		} else if (msg.role === "user") {
			if (typeof msg.content === "string") {
				params.push({
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd <local path> && ls | grep -i prompt; grep -nE "sections\.|<tools>|<skills>|mcp_servers|available_skills|name: \"(tools|skills|rules|mcp_servers|preamble|cwd)\"" system-prompt.js 2>/dev/null | head -30
````

````
prompt-templates.d.ts
prompt-templates.d.ts.map
prompt-templates.js
prompt-templates.js.map
system-prompt.d.ts
system-prompt.d.ts.map
system-prompt.js
system-prompt.js.map
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd <local path> && wc -l system-prompt.js && grep -nE "tools|skills|mcp|section" system-prompt.js | head -50
````

````
150 system-prompt.js
6:import { formatSkillsForPrompt } from "./skills.js";
19:        sections: { ...(input.sections ?? {}) },
22:        skills: (input.skills ?? []).map((skill) => ({ ...skill })),
67:/** Build the ordered, independently replaceable sections of the structured system prompt. */
70:    const { customPrompt, selectedTools, hiddenTools, toolSnippets, toolGuidelines, promptGuidelines, appendSystemPrompt, sections: customSections, cwd, contextFiles, skills, } = options;
73:            throw new Error(`Invalid system prompt section name: ${name}`);
85:        const tools = visibleTools.length > 0 ? visibleTools.map((name) => `- ${name}: ${toolSnippets[name]}`).join("\n") : "(none)";
86:        promptSections.tools = `${tools}\n\nAdditional tools may be available.`;
88:        promptSections.docs = `Pi documentation (read only when the user asks about the harness itself, its SDK, extensions, themes, skills, or TUI):
91:- Examples: ${getExamplesPath()} (extensions, custom tools, SDK)
93:- When asked about: extensions (docs/extensions.md, examples/extensions/), themes (docs/themes.md), skills (docs/skills.md), prompt templates (docs/prompt-templates.md), TUI components (docs/tui.md), keybindings (docs/keybindings.md), SDK integrations (docs/sdk.md), custom providers (docs/custom-provider.md), adding models (docs/models.md), packages (docs/packages.md), environment variables (docs/environment-variables.md), MCP servers (docs/mcp.md), codemode scripts and non-LLM models such as classifiers and image models (docs/codemode.md)
100:    // A hidden reader is still reachable through another tool, so skills stay but the hint names no tool.
104:    if (skillFileReadTool && skills.length > 0) {
105:        const skillsPrompt = formatSkillsForPrompt(skills, skillFileReadTool).trim();
106:        if (skillsPrompt)
107:            promptSections.skills = skillsPrompt;
114:    const sections = { preamble: promptSections.preamble };
117:            sections[name] = `<${name}>\n${content}\n</${name}>`;
119:    return sections;
123: * with no sections; otherwise `content` is empty and the structured sections carry the prompt.
128:    return { content: "", sections: buildSystemPromptSections(input) };
135: * Diff the sections the model currently has (replayed from the transcript, so never null)
136: * against the desired ones. Returns a `SystemMessage.sections` patch, or undefined when
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm checking how the tools section of the system prompt changes when tool_search activates a deferred tool, since that change gets patched in as an updated system message and affects caching. Now I'm wondering whether each loaded tool actually shows up in that section, or only the ones that are visible after hidden tools are filtered out.

I'm going to check lines 75 to 90 to confirm whether a loaded tool with a snippet really appears in the tools section.
````
</details>

**[command]** exit=0

````
cd <local path> && sed -n 67,150p system-prompt.js; grep -n "function formatSkillsForPrompt" -A30 skills.js | head -40
````

````
/** Build the ordered, independently replaceable sections of the structured system prompt. */
export function buildSystemPromptSections(input) {
    const options = normalizeBuildSystemPromptOptions(input);
    const { customPrompt, selectedTools, hiddenTools, toolSnippets, toolGuidelines, promptGuidelines, appendSystemPrompt, sections: customSections, cwd, contextFiles, skills, } = options;
    for (const name of Object.keys(customSections)) {
        if (!SYSTEM_PROMPT_SECTION_NAME.test(name) || name === "preamble") {
            throw new Error(`Invalid system prompt section name: ${name}`);
        }
    }
    const declaredTools = selectedTools.filter((name) => !hiddenTools.includes(name));
    const promptSections = {};
    if (customPrompt) {
        promptSections.preamble = customPrompt;
    }
    else {
        promptSections.preamble =
            "You are a coding assistant running inside pi, a coding agent harness. Help users inspect files, run commands, and modify code.";
        const visibleTools = declaredTools.filter((name) => !!toolSnippets[name]);
        const tools = visibleTools.length > 0 ? visibleTools.map((name) => `- ${name}: ${toolSnippets[name]}`).join("\n") : "(none)";
        promptSections.tools = `${tools}\n\nAdditional tools may be available.`;
        promptSections.rules = buildRules(declaredTools, toolGuidelines, promptGuidelines);
        promptSections.docs = `Pi documentation (read only when the user asks about the harness itself, its SDK, extensions, themes, skills, or TUI):
- Main documentation: ${getReadmePath()}
- Additional docs: ${getDocsPath()}
- Examples: ${getExamplesPath()} (extensions, custom tools, SDK)
- When reading pi docs or examples, resolve docs/... under Additional docs and examples/... under Examples, not the current working directory
- When asked about: extensions (docs/extensions.md, examples/extensions/), themes (docs/themes.md), skills (docs/skills.md), prompt templates (docs/prompt-templates.md), TUI components (docs/tui.md), keybindings (docs/keybindings.md), SDK integrations (docs/sdk.md), custom providers (docs/custom-provider.md), adding models (docs/models.md), packages (docs/packages.md), environment variables (docs/environment-variables.md), MCP servers (docs/mcp.md), codemode scripts and non-LLM models such as classifiers and image models (docs/codemode.md)
- Before implementing harness changes, read the relevant docs and examples in full, following related cross-references.`;
    }
    if (appendSystemPrompt)
        promptSections.addendum = appendSystemPrompt;
    if (contextFiles.length > 0)
        promptSections.project_context = renderProjectContext(contextFiles);
    // A hidden reader is still reachable through another tool, so skills stay but the hint names no tool.
    const readers = ["read", "bash"];
    const skillFileReadTool = readers.find((tool) => declaredTools.includes(tool)) ??
        (readers.some((tool) => selectedTools.includes(tool)) ? "indirect" : undefined);
    if (skillFileReadTool && skills.length > 0) {
        const skillsPrompt = formatSkillsForPrompt(skills, skillFileReadTool).trim();
        if (skillsPrompt)
            promptSections.skills = skillsPrompt;
    }
    promptSections.cwd = cwd.replace(/\\/g, "/");
    for (const [name, content] of Object.entries(customSections)) {
        if (content)
            promptSections[name] = content;
    }
    const sections = { preamble: promptSections.preamble };
    for (const [name, content] of Object.entries(promptSections)) {
        if (name !== "preamble")
            sections[name] = `<${name}>\n${content}\n</${name}>`;
    }
    return sections;
}
/**
 * The complete prompt state for `input`. A forced prompt is opaque and lives in `content`
 * with no sections; otherwise `content` is empty and the structured sections carry the prompt.
 */
export function buildSystemPromptState(input) {
    if (input.forceSystemPrompt !== undefined)
        return { content: input.forc
… [2586 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking whether loaded tools get a promptSnippet that lands in the tools section and guidelines that go into the rules section, and whether MCP tools have one at all, since they probably don't unless one is defined. I'm also going to look up the title and date of PR #6474 in the old pi-mono repo, the original cache-friendly dynamic tool loading change, so I can cite it.

Next I'll check whether there's a system prompt "mcp_servers" section, then pull PR #6474's metadata from earendil-works/pi-mono so I can cite its title and date.
````
</details>

**[agent]**

Последний штрих — исходный PR про cache-friendly dynamic tool loading (#6474 в pi-mono), чтобы сослаться на него.

**[command]** exit=0

````
gh api repos/earendil-works/pi-mono/pulls/6474 --jq '{title, merged_at, html_url, merge_commit_sha, body: .body[0:1500]}' 2>&1 | head -40
````

````
{"body":"This PR adds dynamic tool loading via `addedTools` in messages which allows tools to be introduced mid-conversation instead of requiring every tool to be present in the initial request tool list on supported backends.\r\n\r\nFor Anthropic models with tool-reference support:\r\n\r\n- Tools introduced by `ToolResultMessage.addedToolNames` are sent as deferred tool definitions.\r\n- The introducing tool result includes `tool_reference` blocks, making that point in the transcript the tool load point.\r\n- This keeps late-added tools out of the cached prompt prefix where possible.\r\n- Tools introduced from user messages, repeated tool redefinitions, or name collisions with existing context tools are folded into the prefix to preserve replay validity.\r\n\r\nHere is an example of how this can work.  You use a small stable loader tool, then register the real tool from inside that loader’s execution. Do not add prompt snippets/guidelines to the late tool.\r\n\r\n```ts\r\nimport type { ExtensionAPI } from \"@earendil-works/pi-coding-agent\";\r\nimport { Type } from \"typebox\";\r\n\r\nexport default function (pi: ExtensionAPI) {\r\n  let dbToolsLoaded = false;\r\n\r\n  pi.registerTool({\r\n    name: \"load_db_tools\",\r\n    label: \"Load DB Tools\",\r\n    description: \"Load database tools when database access is needed.\",\r\n    parameters: Type.Object({}),\r\n\r\n    async execute() {\r\n      if (!dbToolsLoaded) {\r\n        dbToolsLoaded = true;\r\n\r\n        pi.registerTool({\r\n          name: \"db_query\",\r\n          label: \"DB Query\",\r\n    ","html_url":"https://github.com/earendil-works/pi/pull/6474","merge_commit_sha":"3d8f74357c169d24f996a1611ecc4be72b7744bd","merged_at":"2026-07-10T21:52:54Z","title":"feat(ai): support message-anchored tool loading"}
````

<details><summary>reasoning</summary>

````
I'm noting that the original design in 0.80.7 used Anthropic's tool_reference with defer_loading in tool results, tracked through addedToolNames. That was later replaced by system messages carrying toolsAdded, along with the Anthropic inline-tools beta. I want to find when that switch happened, so I'll grep the CHANGELOG for addedToolNames.
````
</details>

<details><summary>reasoning</summary>

````
Первая версия (PR #6474) использовала `defer_loading` и `tool_reference` в tool_result; сейчас проверяю, когда её заменили на system-сообщения.
````
</details>

**[command]** exit=0

````
cd <local path> && for n in $(grep -nE "addedToolNames|addedTools|tool_reference|tool references|leading system message|system messages carry|transcript system messages" CHANGELOG.md | cut -d: -f1 | head -15); do v=$(awk -v n=$n 'NR<=n && /^## /{h=$0} NR==n{print h}' CHANGELOG.md); echo "$v :: $(sed -n ${n}p CHANGELOG.md | cut -c1-400)"; done; grep -rnE "addedToolNames|addedTools" ../pi-coding-agent/node_modules/@earendil-works/pi-ai/CHANGELOG.md 2>/dev/null | head; ls node_modules/@earendil-works/pi-ai/
````

````
README.md
dist
package.json
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
cd /tmp/pi-upstream && gh api repos/earendil-works/pi/contents/packages/ai/CHANGELOG.md -H "Accept: application/vnd.github.raw" > ai-CHANGELOG.md && for n in $(grep -nE "addedToolNames|addedTools|tool_reference|toolsAdded|mid-conversation system|inline tool|tool_addition|SystemMessage|additional_tools|synthetic tool search|tool_search_call" ai-CHANGELOG.md | cut -d: -f1 | head -25); do v=$(awk -v n=$n 'NR<=n && /^## /{h=$0} NR==n{print h}' ai-CHANGELOG.md); echo "$v :: $(sed -n ${n}p ai-CHANGELOG.md | cut -c1-330)"; done
````

````
## [1.6.0] - 2026-11-20 :: - `openai-completions` now sends system messages of reasoning models (the system prompt and mid-conversation system messages) with the `developer` role only to `api.openai.com`; all other hosts, including Azure and OpenRouter, get `system`. Set `compat.supportsDeveloperRole` to override ([#10741](https://github.com/earendil-work
## [1.5.1] - 2026-11-09 :: - Added Claude Fable 5.2 (`claude-fable-5-2`) to the `anthropic` provider ($8/$40 per million input/output tokens, 1M context, 128K output). Like Fable 5.1 it uses per-message effort and mid-conversation system messages; requests its safety classifiers refuse before any output are answered by Claude Opus 5 through server-side fa
## [1.5.0] - 2026-11-02 :: - Fixed Claude models that accept mid-conversation system messages rejecting a session with a 400 (`role 'system' must precede an 'assistant' message`) when a system update was followed by an assistant reply with nothing to send to Anthropic, such as an empty reply or another model's reasoning-only reply ([#11091](https://github
## [1.5.0] - 2026-11-02 :: - Fixed GPT-5.4 and GPT-5.5 failing with `Missing namespace for function_call` after switching from another model that called tools. On the OpenAI and OpenCode providers they now declare their tools in the top-level tool list instead of loading them through `additional_tools` or tool search ([#11415](https://github.com/earendil-
## [1.4.0] - 2026-10-21 :: - `resolveTranscriptTools()` now takes a `TranscriptToolSupport` (`"none"`, `"additions"`, or `"changes"`) instead of a boolean, and `TranscriptTools.anchorsAdditions` is replaced by `foldedSystemMessages`, the number of leading system messages folded into `requestTools` ([#10940](https://github.com/earendil-works/pi/issues/1094
## [1.4.0] - 2026-10-21 :: - Fixed OpenAI Responses deferred tool loads rewriting the top-level tool list, and losing the prompt cache, on every load after a tool removal. Models with `additional_tools` now declare all tools in `additional_tools` items, starting with one at the head of the input, so removals (announced as text) and redefinitions no longer
## [1.1.0] - 2026-10-07 :: - Added Claude Haiku 5.5 (`claude-haiku-5-5`) to the `anthropic` provider with its prompt-length pricing tier, adaptive thinking with `xhigh`/`max` effort, per-message effort, and mid-conversation system messages and tool changes. Bedrock requests for Haiku 5.5 use adaptive thinking, native `xhigh`, and prompt caching
## [1.0.1] - 2026-10-03 :: - Anthropic models with native mid-conversation tool changes now use the `inline-tools-2026-09-15` beta: later tools are defined by value in `tool_addition` blocks instead of being appended to the top-level tool list, and redefining a tool under the same name no longer falls back to resending the full tool list, so the prompt ca
## [0.86.0] - 2026-09-19 :: - Added transcript-backed mid-conversation system prompt and tool changes, with native replay on supported models and automatic collapse for other providers. See [System Messages](README.md#system-messages) ([#9548](https://github.com/earendil-works/pi/pull/9548)).
## [0.84.2] - 2026-08-14 :: - Changed OpenAI Responses deferred tool loading to prefer message-anchored `additional_tools` where supported while retaining tool-search and top-level fallbacks ([#7709](https://github.com/earendil-works/pi/issues/7709)).
## [0.80.7] - 2026-07-14 :: - Added cache-friendly dynamic tool loading. `ToolResultMessage.addedToolNames` marks where tools from `Context.tools` became available; Anthropic and OpenAI Responses use native deferred loading so late tools stay out of the cached prefix, while other providers continue using `Context.tools` normally ([#6474](https://github.com
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I've got enough material now, so I'm moving on to writing the report. It needs a TL;DR, the architecture covering exposure, tool_search, setActiveTools, the transcript system messages and section patches, and declareToolChanges, plus a mermaid sequence diagram of the flow and a provider matrix comparing how openai-completions, anthropic, and responses each handle the changes.

I'm now working out the cache section: a change to the none-mode tools array likely forces a full miss, since I'm inferring that tools render at the start of the prompt, which I'll flag as a guess. I'm also noting that collapsing system messages and removing tools in additions mode each cause a one-time refold, and that stable tool descriptions, the date removal, and compaction as a full checkpoint all matter.

I'm settling on the recommendation for our harness: a fixed `call_tool(name, args)` meta-tool keeps the tools array constant, with schemas returned in tool results and living in the append-only conversation tail. Pi's codemode works this way, with deferred tools called via `ctx.executeTool` rather than declared up front. The alternative is Pi-style tool deltas that accept one cache miss per load. I'd lean toward the meta-tool approach if strict no-invalidation is a requirement, possibly validating arguments against the schema on the harness side.

Now I'm checking the upstream line numbers for the code references, starting with the transcript utility and the placeholder constant in the Anthropic messages file. The grep didn't find the constant under that exact form, so it's probably declared with a type annotation, and I'll search for that instead.

I still need the line numbers for the placeholder constant, the responses tool resolver, and the codemode description, so I'll pull those from upstream as well.
````
</details>

**[agent]**

Данных достаточно. Добираю пару номеров строк в upstream и пишу отчёт.

**[command]** exit=0

````
cd /tmp/pi-upstream && grep -nE "DEFERRED_TOOL_PLACEHOLDER" packages_ai_src_api_anthropic-messages.ts | head -3; grep -nE "resolveTranscriptTools\(" packages_ai_src_api_openai-responses-shared.ts; grep -nE "^export function getCurrentSystemMessage|^export function resolveTranscript\b" packages_ai_src_utils_transcript.ts; mkdir -p <local path>
````

````
222:const DEFERRED_TOOL_PLACEHOLDER: BetaTool = {
1531:		params.tools = [...convertToolDefinitions(initialTools, toolCacheControl), DEFERRED_TOOL_PLACEHOLDER];
255:	const transcriptTools = resolveTranscriptTools(normalizedContext.messages, toolSupport);
73:export function getCurrentSystemMessage(messages: TranscriptMessages): SystemMessage | undefined {
115:export function resolveTranscript(
Shell cwd was reset to <local path>
````

<details><summary>reasoning</summary>

````
I'm putting together the report now, keeping it dense but complete. I'm noting the local package location and the dist folder for pi-ai, plus the upstream permalink base to reference against.
````
</details>

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+# Pi coding agent: динамическая подгрузка тулов и prompt cache
+
+Исследовано: локальный `@earendil-works/pi-coding-agent` 1.5.0 (2026-11-02) с зависимостями `pi-ai`, `pi-agent-core` 1.5.0 и upstream `earendil-works/pi` на `main` @ [`8209929`](https://github.com/earendil-works/pi/commit/8209929fb553e7a8c91dc0894569f9ec43dd201f) (2026-11-23, после v1.6.0). По этой теме между 1.5.0 и main архитектурных изменений нет, только фиксы (перечислены в конце).
+
+Обозначения путей:
+
+- `CA` = `<local path>`
+- `AI` = `CA/node_modules/@earendil-works/pi-ai/dist`
+- `AG` = `CA/node_modules/@earendil-works/pi-agent-core/dist`
+- `U/…` = permalink на upstream `https://github.com/earendil-works/pi/blob/8209929fb553e7a8c91dc0894569f9ec43dd201f/…`
+
+## TL;DR
+
+1. **Да, динамическая подгрузка есть, и это first-class фича.** У каждого тула есть `exposure` (`direct` / `model-only` / `codemode` / `deferred` / `hidden`). Встроенный тул `tool_search` (BM25 по name/description/схеме) ищет среди тулов, которые модели ещё не объявлены, и активирует найденные через `setActiveTools()`. Модель видит их **со следующего запроса**. Второй механизм, `codemode`: модель пишет JS-скрипт, который зовёт тулы через `tools.<name>()`, и схемы этих тулов вообще не объявляются модели.
+2. **Состояние тулов живёт в транскрипте, а не в request-поле.** Первый `system`-message несёт промпт по секциям и начальный набор тулов. Каждое изменение дописывается в историю отдельным `system`-message с `toolsAdded` / `toolsRemoved` (+ патчи секций промпта). Текущее состояние получается проигрыванием этих сообщений по порядку. История append-only, поэтому префикс не трогается.
+3. **Как дельта уходит на провод, решает транспорт, по флагам совместимости модели.** Там, где у провайдера есть нативное API, Pi его использует: Anthropic inline-tools beta (`tool_addition` / `tool_removal`), OpenAI Responses `additional_tools` или синтетический client-side `tool_search_call` / `tool_search_output` с `defer_loading`, Kimi-расширение `{"role":"system","tools":[…]}` в Chat Completions. **Generic OpenAI-compatible `/v1/chat/completions` нативной поддержки не имеет. Там Pi честно пересобирает top-level `tools[]` и сворачивает все system-дельты в начальный system prompt, то есть каждая подгрузка = cache miss.** Pi это не скрывает, а документирует.
+4. Скиллы работают отдельно и по-простому: в промпте только `<available_skills>` (name / description / location), модель сама читает `SKILL.md` через `read`/`bash`. Отдельного механизма активации у скиллов нет.
+
+## 1. Что есть в Pi
+
+### 1.1 Exposure и активный набор
+
+Каждый тул регистрируется через `pi.registerTool()` и получает `exposure` ([CA/docs/extensions.md:2738-2770](<local path>)):
+
+| exposure | Объявлен модели | Вызывается из других тулов (`ctx.executeTool`) | Как модель до него добирается |
+|---|---|---|---|
+| `direct` (default) | пока активен | пока активен | сразу виден |
+| `model-only` | пока активен | никогда | сразу виден (так устроены `tool_search` и `codemode`) |
+| `codemode` | нет (пока явно не активирован) | всегда | скрипт `codemode` (`searchTools()`, `describeTool()`, `ALL_TOOLS`); также `tool_search` |
+| `deferred` | нет | всегда | `tool_search` грузит его в активный набор; codemode его не листит, но может вызвать |
+| `hidden` | нет | нет | никак (так «разрегистрируют» тул) |
+
+«Активный набор» (`getActiveTools` / `setActiveTools`) и есть список тулов, объявленных модели. `setActiveTools` игнорирует неизвестные и `hidden` имена ([CA/docs/extensions.md:1892-1922](<local path>)). Для MCP exposure задаётся на сервер и переопределяется по тулу через `toolExposure` (`"get_*": "codemode"` и т.п.), имена тулов вида
… [23542 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm double-checking the line references I cited loosely, and most of them hold up. One range needs a tighter cite, since the actual lines are 902-909 rather than 900-910. Next I'll look at docs/extensions.md.

I'm confirming the remaining line references against the files, with the Tool Exposure section near line 2738 and the skills.js range checked out.
````
</details>

**[agent]**

Сделал, в проекте ничего не трогал. Отчёт: [pi-dynamic-tools.md](<local path>). Сверял локальную 1.5.0 с upstream `main` @ `8209929` (уже после v1.6.0), по этой теме там только фиксы.

- **Динамическая подгрузка в Pi есть.** Каждый тул получает `exposure`: `direct`, `model-only`, `codemode`, `deferred` или `hidden`. Встроенный `tool_search` (по умолчанию выключен) ищет BM25 по ещё не объявленным тулам и включает найденные. Модель видит их только со следующего запроса: в ответе поиска приходят имена и одна строка описания, а полная схема приезжает следующим запросом как обычное объявление тула. Описание `tool_search` намеренно статично и не перечисляет тулы.
- **Набор тулов хранится в истории, а не в запросе.** Первое `system`-сообщение несёт промпт по секциям и начальные тулы. Каждое изменение дописывается в историю отдельным `system`-сообщением со списком добавленных и удалённых тулов. Текущий набор получается проигрыванием этих сообщений по порядку, история только дописывается.
- **Как изменение уходит провайдеру, решают флаги модели.** Где есть нативное API, Pi его использует:
  - Anthropic: бета `inline-tools-2026-09-15`. Список `tools[]` фиксирован и включает пустой тул-заглушку с `defer_loading`, объявленный с первого запроса; без неё первая же подгрузка давала полный промах (по их замеру). Новые тулы приходят блоками `tool_addition` / `tool_removal`.
  - OpenAI Responses: `additional_tools`, либо Pi сам вставляет в историю пару `tool_search_call` / `tool_search_output`.
  - Kimi: нестандартное `{"role":"system","tools":[…]}` прямо в Chat Completions.
- **Официальный Anthropic tool search Pi не использует**, поиск всегда свой, на клиенте. В июльской версии (PR #6474) было `defer_loading` + `tool_reference`, но потом от этого отказались: переопределение тула с тем же именем ломало кэш.
- **Generic `/v1/chat/completions`, то есть наш случай, нативной поддержки не имеет.** Pi там честно пересобирает полный `tools[]` и вклеивает все изменения промпта в первое сообщение. Каждая подгрузка = промах кэша, и Pi это прямо пишет в своих доках. Механизм экономит размер промпта, но кэш не бережёт.
- **Кэш не трогают:** подгрузка через нативные транспорты, обновления секций промпта, дописанные в хвост, и вызовы через `codemode`. В `codemode` модель пишет JS-скрипт, который зовёт тулы, и их схемы вообще не объявляются, поэтому это работает на любом провайдере.
- **Кэш сбрасывают:** любая смена тулов на generic-транспорте, удаление или переопределение тула в режиме «только добавления» (один раз), полная замена промпта и компакция.
- **Скиллы для контраста:** в промпте только имя, описание и путь каждого скилла; модель сама читает `SKILL.md` через `read`, текст ложится в хвост истории. Отдельной активации у скиллов нет.

**Что это значит для нас:** их транспорт для generic chat completions копировать бессмысленно, он кэш не сохраняет. Брать стоит три вещи: хранение набора тулов как дописываемых событий в истории, стабильный `tool_search` на BM25 и правило ничего не менять в префиксе. Сам префикс лучше держать неизменным: фиксированный набор `core + tool_search + call_tool(name, args)`, схема найденного тула возвращается в ответе поиска, а аргументы проверяет наш harness. Цена — для отложенных тулов теряется строгая генерация аргументов по схеме (constrained decoding / strict). Сам Pi так не делает, это моя рекомендация, она расписана в §5 отчёта.
