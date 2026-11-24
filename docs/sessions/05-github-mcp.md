# Sub-agent: GitHub MCP server as an example tool catalog

Full bb session log, converted from the raw event stream: inputs, agent messages, reasoning, commands with output, file changes and tool calls (long outputs truncated to 4000 characters). Local paths, thread ids and emails are redacted; outputs that came from the developer's private projects are replaced with a placeholder.

---

## [input]

Контекст: тестовое задание — минимальный async coding-agent harness на Python (~/projects/loola-test-task, TASK.md). Показываем динамическую подгрузку тулов: в контексте всегда bash + мета-тулы (tool_search / tool_call), остальные десятки тулов deferred — модель находит их поиском, harness валидирует аргументы по JSON Schema (jsonschema) и вызывает. Showcase-каталогом deferred-тулов решили взять тулы GitHub MCP server. Замер «до/после»: «до» — все тулы GitHub MCP прямо в tools, «после» — deferred.

Твоя задача — ресерч и маленький спайк, в репо задания ничего не меняй (параллельно там идёт рефакторинг). Скрэтч-файлы — только в <local path>
1. Актуальное состояние официального github/github-mcp-server (проверь по репо/релизам, не по памяти): сколько тулов всего и по toolsets, какие toolsets по умолчанию, суммарный размер описаний+схем в токенах (оценка, например tiktoken o200k или chars/4 — укажи метод). Есть ли у них свои механизмы против раздувания промпта (dynamic toolsets, tool search, read-only и т.п.) — как устроены, это пригодится как сравнение.
2. Как получить полный каталог (name, description, inputSchema) локально: есть ли команда/флаг для дампа, либо через MCP tools/list по stdio. Способы запуска: бинарь из релизов, docker, remote endpoint. Попробуй реально получить каталог (бинарь в <local path> без глобальной установки), сохрани catalog.json.
3. Аутентификация: что нужно для tools/list и для реальных вызовов (PAT, scopes). У пользователя есть gh CLI с логином — можно ли использовать gh auth token в рантайме (НЕ печатай токен, не клади его в аргументы команд/файлы; только env внутри процесса). Для реальных вызовов в демо — только read-only тулы на публичных репо.
4. Интеграция в Python: минимальный путь — официальный Python SDK mcp (ClientSession + stdio_client) или свой тонкий stdio JSON-RPC клиент. Оцени сложность обоих, учти, что harness async. Проверь спайком вызов одного read-only тула (например get_file_contents/search_repositories на публичном репо) и форму результата (content blocks, isError, размер).
5. Подводные камни для нашего случая: схемы, которые jsonschema не переварит; огромные результаты тулов (нужна обрезка?); тулы, опасные для мутаций (как держать read-only); rate limits.

Результат: отчёт на русском в <local path> (абзацы без hard-wrap), в финальном ответе — выжимка 10–15 строк, путь к отчёту и к catalog.json, и рекомендация как подключать.

<details><summary>reasoning</summary>

````
I'm setting up the working directory first, then checking the GitHub repo's releases through the gh CLI.
````
</details>

**[agent]**

Начинаю: проверю актуальный релиз github-mcp-server через gh, скачаю бинарь в scratch-папку и сниму каталог через MCP tools/list.

**[command]** exit=0

````
D=<local path> mkdir -p $D && cd $D && gh release list -R github/github-mcp-server -L 5 && gh release view -R github/github-mcp-server --json tagName,publishedAt,assets -q '.tagName, .publishedAt, (.assets[].name)' | head -30; which uv bun docker; uname -m
````

````
GitHub MCP Server 2.2.0	Latest	v2.2.0	2026-11-16T23:30:46Z
GitHub MCP Server 2.1.0		v2.1.0	2026-11-03T11:11:41Z
GitHub MCP Server 2.0.3		v2.0.3	2026-10-21T09:52:29Z
GitHub MCP Server 2.0.2		v2.0.2	2026-10-08T11:33:15Z
GitHub MCP Server 2.0.1		v2.0.1	2026-10-07T08:13:24Z
v2.2.0
2026-11-16T23:30:46Z
github-mcp-server_2.2.0_checksums.txt
github-mcp-server_Darwin_arm64.tar.gz
github-mcp-server_Darwin_x86_64.tar.gz
github-mcp-server_Linux_arm64.tar.gz
github-mcp-server_Linux_i386.tar.gz
github-mcp-server_Linux_x86_64.tar.gz
github-mcp-server_Windows_arm64.zip
github-mcp-server_Windows_i386.zip
github-mcp-server_Windows_x86_64.zip
<local path>
<local path>
/usr/bin/docker
x86_64
````

<details><summary>reasoning</summary>

````
I'm going to download the binary into its own separate directory, since it's untrusted. The bin directory will be $D/bin, and once it's there I'll verify the checksum.
````
</details>

<details><summary>reasoning</summary>

````
Релиз v2.2.0 вышел 16.11.2026; сейчас скачиваю Linux x86_64 бинарник с проверкой checksum и сверяюсь с README и документацией репозитория через gh api.
````
</details>

**[command]** exit=0

````
mkdir -p bin dl && cd dl && gh release download v2.2.0 -R github/github-mcp-server -p 'github-mcp-server_Linux_x86_64.tar.gz' -p '*checksums.txt' --clobber && sha256sum -c --ignore-missing github-mcp-server_2.2.0_checksums.txt && tar -xzf github-mcp-server_Linux_x86_64.tar.gz -C ../bin && ls -la ../bin && ../bin/github-mcp-server --version; ../bin/github-mcp-server --help; ../bin/github-mcp-server stdio --help
````

````
github-mcp-server_Linux_x86_64.tar.gz: OK
total 29488
drwxrwxr-x 2 bb bb     4096 Nov 24 10:32 .
drwxrwxr-x 4 bb bb     4096 Nov 24 10:32 ..
-rw-r--r-- 1 bb bb     1063 Nov 17 02:14 LICENSE
-rw-r--r-- 1 bb bb   127689 Nov 17 02:14 README.md
-rwxr-xr-x 1 bb bb 30048416 Nov 17 02:15 github-mcp-server
GitHub MCP Server
Version: 2.2.0
Commit: 67d4dc489700ec955ad255d098396dd86c729523
Build Date: 2026-11-16T23:14:14Z
A GitHub MCP server that handles various tools and resources.

Usage:
  github-mcp-server [command]

Available Commands:
  completion    Generate the autocompletion script for the specified shell
  generate-docs Generate documentation for tools and toolsets
  help          Help about any command
  http          Start HTTP server
  list-scopes   List OAuth scope policies for enabled tools
  stdio         Start stdio server

Flags:
      --content-window-size int          Specify the content window size (default 5000)
      --enable-command-logging           When enabled, the server will log all command requests and responses to the log file
      --exclude-tools strings            Comma-separated list of tool names to disable regardless of other settings
      --export-translations              Save translations to a JSON file
      --features strings                 Comma-separated list of feature flags to enable
      --gh-host string                   Specify the GitHub hostname (for GitHub Enterprise etc.)
  -h, --help                             help for github-mcp-server
      --insiders                         Enable insiders features
      --lockdown-mode                    Enable lockdown mode
      --log-file string                  Path to log file
      --read-only                        Restrict the server to read-only operations
      --repo-access-cache-ttl duration   Override the repo access cache TTL (e.g. 1m, 0s to disable) (default 5m0s)
      --tools strings                    Comma-separated list of specific tools to enable
      --toolsets strings                 Comma-separated list of tool groups to enable (no spaces).
                                         Available: actions, code_quality, code_security, copilot, copilot_automations,
                                         	     copilot_issue_intents, dependabot, discussions, gists, git, governance,
                                         	     issues, labels, notifications, orgs, projects, pull_requests, repos,
                                         	     secret_protection, security_advisories, stargazers, users
                                         Special toolset keywords:
                                           - all: Enables all available toolsets
                                           - default: Enables the default toolset configuration of:
                                         	     context, copilot, issues, pull_requests, repos, users
                                         Examples:
                                           - --toolsets=actions,gists,notifications
                                           - Default + additional: --toolsets=default,actions,gists
                                           - All tools: --toolsets=all
  -v, --version                          version for github-mcp-server

Use "github-mcp-server [command] --help" for more information about a command.
Start a server that communicates via standard input/output streams using JSON-RPC messages.

Usage:
  github-mcp-server stdio [flags]

Flags:
      --app-id string                 GitHub App ID or client ID, enabling non-interactive server-to-server authentication
      --app-installation-id string    GitHub App installation ID to mint installation access tokens for
      --app-private-key-path string   Path to the GitHub App private key (PEM). Preferred over GITHUB_APP_PRIVATE_KEY: keeps the key off the command line and out of the environment
  -h, --help                          help for stdio
      --oauth-callback-port int       Fixed lo
… [2842 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking whether the 2.2.0 README mentions a dynamic-toolsets flag at all, so I'll search it for terms like dynamic, tool search, read-only, toolsets, and auth.
````
</details>

**[agent]**

Интересно: в v2.2.0 нет флага `--dynamic-toolsets` (в старых версиях был). Проверяю README из релиза на dynamic/tool search/auth/features.

**[command]** exit=0

````
cd <local path> && grep -n -i -E 'dynamic|tool.?search|discover|read-only|readonly|lockdown|insiders|features|GITHUB_PERSONAL_ACCESS_TOKEN|scope|content-window|remote|api.githubcopilot|X-MCP|^#' bin/README.md | head -150
````

````
3:# GitHub MCP Server
7:### Use Cases
17:### Using the Go module
31:## Remote GitHub MCP Server
33:[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=github&config=%7B%22type%22%3A%20%22http%22%2C%22url%22%3A%20%22https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2F%22%7D) [![Install in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-Install_Server-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=github&config=%7B%22type%22%3A%20%22http%22%2C%22url%22%3A%20%22https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2F%22%7D&quality=insiders) [![Install in Visual Studio](https://img.shields.io/badge/Visual_Studio-Install_Server-C16FDE?style=flat-square&logo=visualstudio&logoColor=white)](https://aka.ms/vs/mcp-install?%7B%22name%22%3A%22github%22%2C%22gallery%22%3Atrue%2C%22url%22%3A%22https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2F%22%7D)
35:The remote GitHub MCP Server is hosted by GitHub and provides the easiest method for getting up and running. If your MCP host does not support remote MCP servers, don't worry! You can use the [local version of the GitHub MCP Server](https://github.com/github/github-mcp-server?tab=readme-ov-file#local-github-mcp-server) instead.
37:### Prerequisites
39:1. A compatible MCP host with remote server support (VS Code 1.101+, Claude Desktop, Cursor, Windsurf, etc.)
42:### Install in VS Code
44:For quick installation, use one of the one-click install buttons above. Once you complete that flow, toggle Agent mode (located by the Copilot Chat text input) and the server will start. Make sure you're using [VS Code 1.101](https://code.visualstudio.com/updates/v1_101) or [later](https://code.visualstudio.com/updates) for remote MCP and OAuth support.
59:      "url": "https://api.githubcopilot.com/mcp/"
73:      "url": "https://api.githubcopilot.com/mcp/",
94:### Install in other MCP hosts
106:> **Note:** Each MCP host application needs to configure a GitHub App or OAuth App to support remote access via OAuth. Any host application that supports remote MCP servers should support the remote GitHub server with PAT authentication. Configuration details and support levels vary by host. Make sure to refer to the host application's documentation for more info.
108:### Configuration
110:#### Toolset configuration
112:See [Remote Server Documentation](docs/remote-server.md) for full details on remote server configuration, toolsets, headers, and advanced usage. This file provides comprehensive instructions and examples for connecting, customizing, and installing the remote GitHub MCP Server in VS Code and other MCP hosts.
116:#### Insiders Mode
118:> **Try new features early!** The remote server offers an insiders version with early access to new features and experimental tools.
130:      "url": "https://api.githubcopilot.com/mcp/insiders"
144:      "url": "https://api.githubcopilot.com/mcp/",
146:        "X-MCP-Insiders": "true"
157:See [Remote Server Documentation](docs/remote-server.md#insiders-mode) for more details and examples, [Insiders Features](docs/insiders-features.md) for a full list of what's available, and [Feature Flags](docs/feature-flags.md) for user-opt-in tools such as repository automations.
159:#### GitHub Enterprise
161:##### GitHub Enterprise Cloud with data residency (ghe.com)
163:GitHub Enterprise Cloud can also make use of the remote server.
183:##### GitHub Enterprise Server
185:GitHub Enterprise Server does not support remote server hosting. Please refer to [GitHub Enterprise Server and Enterprise Cloud with data residency (ghe.com)](#github-enterprise-server-and-enterprise-cloud-with-data-residency-ghecom) from the local server configuration.
189:## Local GitHub MCP Server
191:[![Install with Docker in VS Code](https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&l
… [9443 more characters truncated]
````

**[command]** exit=0

````
sed -n 442,660p bin/README.md
````

````
## Tool Configuration

The GitHub MCP Server supports enabling or disabling specific groups of functionalities via the `--toolsets` flag. This allows you to control which GitHub API capabilities are available to your AI tools. Enabling only the toolsets that you need can help the LLM with tool choice and reduce the context size.

_Toolsets are not limited to Tools. Relevant MCP Resources and Prompts are also included where applicable._

When no toolsets are specified, [default toolsets](#default-toolset) are used.

> **Looking for examples?** See the [Server Configuration Guide](./docs/server-configuration.md) for common recipes like minimal setups, read-only mode, and combining tools with toolsets.

#### Specifying Toolsets

To specify toolsets you want available to the LLM, you can pass an allow-list in two ways:

1. **Using Command Line Argument**:

   ```bash
   github-mcp-server --toolsets repos,issues,pull_requests,actions,code_security
   ```

2. **Using Environment Variable**:

   ```bash
   GITHUB_TOOLSETS="repos,issues,pull_requests,actions,code_security" ./github-mcp-server
   ```

The environment variable `GITHUB_TOOLSETS` takes precedence over the command line argument if both are provided.

#### Specifying Individual Tools

You can also configure specific tools using the `--tools` flag. Tools can be used independently or combined with toolsets for fine-grained control.

1. **Using Command Line Argument**:

   ```bash
   github-mcp-server --tools get_file_contents,issue_read,create_pull_request
   ```

2. **Using Environment Variable**:

   ```bash
   GITHUB_TOOLS="get_file_contents,issue_read,create_pull_request" ./github-mcp-server
   ```

3. **Combining with Toolsets** (additive):

   ```bash
   github-mcp-server --toolsets repos,issues --tools get_gist
   ```

   This registers all tools from `repos` and `issues` toolsets, plus `get_gist`.

**Important Notes:**

- Tools and toolsets can be used together
- Read-only mode takes priority: write tools are skipped if `--read-only` is set, even if explicitly requested via `--tools`
- Tool names must match exactly (e.g., `get_file_contents`, not `getFileContents`). Invalid tool names will cause the server to fail at startup with an error message
- When tools are renamed, old names are preserved as aliases for backward compatibility. See [Tool Renaming](docs/tool-renaming.md) for details.

### Using Toolsets With Docker

When using Docker, you can pass the toolsets as environment variables:

```bash
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<your-token> \
  -e GITHUB_TOOLSETS="repos,issues,pull_requests,actions,code_security" \
  ghcr.io/github/github-mcp-server
```

### Using Tools With Docker

When using Docker, you can pass specific tools as environment variables. You can also combine tools with toolsets:

```bash
# Tools only
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<your-token> \
  -e GITHUB_TOOLS="get_file_contents,issue_read,create_pull_request" \
  ghcr.io/github/github-mcp-server

# Tools combined with toolsets (additive)
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<your-token> \
  -e GITHUB_TOOLSETS="repos,issues" \
  -e GITHUB_TOOLS="get_gist" \
  ghcr.io/github/github-mcp-server
```

### Special toolsets

#### "all" toolset

The special toolset `all` can be provided to enable all available toolsets regardless of any other configuration:

```bash
./github-mcp-server --toolsets all
```

Or using the environment variable:

```bash
GITHUB_TOOLSETS="all" ./github-mcp-server
```

#### "default" toolset

The default toolset `default` is the configuration that gets passed to the server if no toolsets are specified.

The default configuration is:

- context
- repos
- issues
- pull_requests
- users

To keep the default configuration and add additional toolsets:

```bash
GITHUB_TOOLSETS="default,stargazers" ./github-mcp-server
```

### Insiders Mode

The local GitHub MCP Server offers an insiders version with early access to new 
… [16749 more characters truncated]
````

<details><summary>reasoning</summary>

````
The README contradicts the help text on whether copilot is in the default set. I'm going to check the repo's docs (feature flags, insiders features, server configuration) and search them for anything about dynamic or tool search, pulling the docs from the v2.2.0 tag with gh api.
````
</details>

<details><summary>reasoning</summary>

````
Расхождение видно: `--help` перечисляет copilot среди дефолтных наборов, а README его не упоминает. Сверю это через tools/list и посмотрю в доках v2.2.0, есть ли dynamic toolsets.
````
</details>

**[command]** exit=0

````
mkdir -p docs && gh api 'repos/github/github-mcp-server/contents/docs?ref=v2.2.0' -q '.[].name' && for f in feature-flags.md insiders-features.md remote-server.md server-configuration.md; do gh api "repos/github/github-mcp-server/contents/docs/$f?ref=v2.2.0" -H 'Accept: application/vnd.github.raw' > docs/$f; done; wc -c docs/*; grep -n -i -E 'dynamic|tool.?search|discover|defer|lazy|progressive|enable_toolset|list_available' docs/*.md | head -60
````

````
error-handling.md
feature-flags.md
github-app-auth.md
host-integration.md
insiders-features.md
installation-guides
oauth-login.md
policies-and-governance.md
remote-server.md
scope-filtering.md
server-configuration.md
streamable-http.md
testing.md
tool-renaming.md
toolsets-and-icons.md
typed-tool-schemas.md
36836 docs/feature-flags.md
 9475 docs/insiders-features.md
30871 docs/remote-server.md
13562 docs/server-configuration.md
90744 total
docs/server-configuration.md:409:`mcp_apps_disable_form_deferral` feature flag. For the remote server, send the
docs/server-configuration.md:413:X-MCP-Features: mcp_apps_disable_form_deferral
docs/feature-flags.md:27:discovery because it is part of the canonical resource identifier. Query
docs/feature-flags.md:50:When enabled, both initialization and `server/discover` omit instructions entirely.
docs/feature-flags.md:51:There is no discovery blurb or fallback instructions for clients without skills
docs/feature-flags.md:55:Clients discover skills with paginated `skills/list`, resolve one with
docs/feature-flags.md:77:In the CLI, use `/skills list` and invoke the discovered server-qualified skill
docs/feature-flags.md:84:consent even with `/allow-all` or `--yolo`. Discovery, command naming and consent
docs/feature-flags.md:588:- **list_available_automation_tools** - List available automation tools
docs/feature-flags.md:593:- **list_available_automation_triggers** - List available automation triggers
````

<details><summary>reasoning</summary>

````
I'm guessing dynamic toolsets were dropped in the 2.x line, so I want to find the release where that happened. I'll search the release notes for mentions of "dynamic."
````
</details>

<details><summary>reasoning</summary>

````
В документации v2.2.0 dynamic toolsets и tool search не упоминаются; сейчас проверю release notes, когда и почему их убрали.
````
</details>

**[command]** exit=0

````
gh api 'repos/github/github-mcp-server/releases?per_page=100' --paginate -q '.[] | select(.body | test("(?i)dynamic|tool search|tool_search")) | "=== \(.tag_name) \(.published_at)\n" + ([.body | split("\n")[] | select(test("(?i)dynamic|tool search|tool_search"))] | join("\n"))' | head -60
````

````
=== v1.1.0 2026-05-28T12:14:43Z
* refactor: remove dynamic toolsets and deprecated closure constructor by @SamMorrowDrums in https://github.com/github/github-mcp-server/pull/2512
=== v0.29.0 2026-01-19T15:20:33Z
* Add tool search CLI by @JoannaaKL in https://github.com/github/github-mcp-server/pull/1839
=== v0.25.0 2025-12-16T10:27:22Z
* Turn off default toolset when in dynamic mode by @tommaso-moro in https://github.com/github/github-mcp-server/pull/1401
=== v0.23.0-gosdk 2025-11-25T09:58:34Z
* Migrate dynamic toolset to modelcontextprotocol/go-sdk by @Copilot in https://github.com/github/github-mcp-server/pull/1450
=== v0.21.0 2025-11-17T15:32:01Z
* Update docs to state that dynamic mode is not available in Remote Server by @tommaso-moro in https://github.com/github/github-mcp-server/pull/1399
=== v0.2.0 2025-04-17T13:55:06Z
- **Experimental** [Dynamic Tool Discovery](https://github.com/github/github-mcp-server?tab=readme-ov-file#tool-configuration) and [provide feedback](https://github.com/github/github-mcp-server/issues/275) if you love it ❤️ , hate 😭 it or encountered any issues 👾.
````

**[command]** exit=0

````
gh pr view 2512 -R github/github-mcp-server --json title,body,mergedAt -q '.title, .mergedAt, .body' | head -60; echo ======; gh pr view 1839 -R github/github-mcp-server --json title,body -q '.title, .body' | head -40
````

````
refactor: remove dynamic toolsets and deprecated closure constructor
2026-05-20T08:51:48Z
## What & why

Removes the dynamic toolset discovery feature (the `--dynamic-toolsets` / `GITHUB_DYNAMIC_TOOLSETS` switch and the meta-tools `enable_toolset`, `list_available_toolsets`, `get_toolset_tools`) along with the deprecated closure-based `NewServerToolWithDeps` constructor that only existed to support it.

This is **tech debt cleanup**:

- Dynamic mode was local-only — never offered by the remote server.
- It carried real complexity: a separate config flag plumbed through stdio + http configs, a parallel registration path, four inventory methods (`ToolsForToolset`, `IsToolsetEnabled`, `EnableToolset`, `EnabledToolsetIDs`), an extra branch in `ResolvedEnabledToolsets`, three meta-tools, and a chunk of conformance/CI matrix.
- After this PR there are exactly **two** server-tool constructors:
  - `NewServerTool` — raw `mcp.ToolHandler`, no closure, no unmarshalling
  - `NewServerToolWithContextHandler[In, Out]` — typed handler, deps via context
- This repo isn't published as a stable library; downstream consumers can pin a version if they need the dynamic feature.

## Diff highlights

- `pkg/github/dynamic_tools.go` + test → deleted
- `pkg/inventory/server_tool.go` — `NewServerToolWithDeps` removed
- `pkg/inventory/filters.go` — `ToolsForToolset`, `IsToolsetEnabled`, `EnableToolset`, `EnabledToolsetIDs` removed
- `ResolvedEnabledToolsets(dynamic, toolsets, tools)` → `ResolvedEnabledToolsets(toolsets, tools)`
- `DynamicToolsets` field removed from `MCPServerConfig`, `StdioServerConfig`, http `ServerConfig`
- `--dynamic-toolsets` flag removed
- `ToolsetMetadataDynamic` removed; `AvailableToolsets("context", "dynamic")` → `AvailableToolsets("context")`
- README, server-configuration.md, toolsets-and-icons.md, copilot-instructions.md, conformance-test script — dynamic refs stripped
- The `.github/workflows/mcp-diff.yml` change that drops the dynamic test matrix isn't included in this PR (OAuth scope) — please apply it as a follow-up

## Verification

- ✅ `script/lint` clean
- ✅ `script/test` passes
- ✅ `script/generate-docs` produces no extra diff after this commit

Stacks on (now merged) #2511.
======
Add tool search CLI
## Summary
<!-- In 1–2 sentences: what does this PR do? -->

## What changed
<!-- Bullet list of concrete changes. -->
- Added new CLI tool to search for a tool with given name / prefix
- Added dependency on https://github.com/humanlogio/humanlog for coloured command results
- Updated docs

<img width="3050" height="736" alt="CleanShot 2026-01-19 at 13 23 20@2x" src="https://github.com/user-attachments/assets/04a823b0-10d6-4854-9211-85ae68fb524d" />
<img width="2816" height="454" alt="CleanShot 2026-01-19 at 13 23 46@2x" src="https://github.com/user-attachments/assets/0a236862-6f78-4c98-be63-a59a2a605194" />


## MCP impact
<!-- Select one or more. If selected, add 1–2 sentences. -->
- [x] No tool or API changes
- [ ] Tool schema or behavior changed
- [ ] New tool added

## Prompts tested (tool changes only)
<!-- If you changed or added tools, list example prompts you tested. -->
<!-- Include prompts that trigger the tool and describe the use case. -->
<!-- Example: "List all open issues in the repo assigned to me" -->
- N/A

## Security / limits
<!-- Select if relevant. Add a short note if checked. -->
- [x] No security or limits impact
- [ ] Auth / permissions considered
- [ ] Data exposure, filtering, or token/size limits considered

## Tool renaming
- [ ] I am renaming tools as part of this PR (e.g. a part of a consolidation effort)
   - [ ] I have added the new tool aliases in `deprecated_tool_aliases.go` 
- [x] I am not renaming tools as part of this PR

Note: if you're renaming tools, you *must* add the tool aliases. For more information on how to do so, please refer to the [official docs](https://github.com/github/github-mcp-server/blob/main/docs/tool-renaming.md).

## Lint
… [8 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking whether a tool search command still exists in the CLI. It's absent from `--help` and the 2.2.0 build, so it has probably been removed. That's not critical right now, so I'll come back to it. I also want to look at `remote-server.md` for the header mechanisms like the toolsets, readonly, and tools headers.

I'm also weighing whether tool consolidation, where several operations get folded into one tool with a method parameter, counts as another way to limit bloat. Scope filtering by token permissions might matter too, along with the content window size flag. Next I'll grep the remote-server docs for the header settings.
````
</details>

<details><summary>reasoning</summary>

````
Флаг `--dynamic-toolsets` с мета-тулами удалён в v1.1.0 как техдолг, а CLI-поиск из v0.29 в v2.2.0 уже нет. Дальше проверю, что осталось у remote-сервера и scope-фильтрация.
````
</details>

**[command]** exit=0

````
grep -n -E 'X-MCP-[A-Za-z-]+' -o docs/remote-server.md | sort -t: -k2 -u | head; grep -n -i -E 'readonly|read-only|lockdown' docs/remote-server.md | head -10; gh api "repos/github/github-mcp-server/contents/docs/scope-filtering.md?ref=v2.2.0" -H 'Accept: application/vnd.github.raw' > docs/scope-filtering.md; sed -n 1,60p docs/scope-filtering.md
````

````
76:X-MCP-Insiders
72:X-MCP-Lockdown
69:X-MCP-Readonly
66:X-MCP-Tools
63:X-MCP-Toolsets
17:Below is a table of available toolsets for the remote GitHub MCP Server. Each toolset is provided as a distinct URL so you can mix and match to create the perfect combination of tools for your use-case. Add `/readonly` to the end of any URL to restrict the tools in the toolset to only those that enable read access. We also provide the option to use [headers](#headers) instead.
20:| Name | Description | API URL | 1-Click Install (VS Code) | Read-only Link | 1-Click Read-only Install (VS Code) |
22:| <picture><source media="(prefers-color-scheme: dark)" srcset="../pkg/octicons/icons/apps-dark.png"><source media="(prefers-color-scheme: light)" srcset="../pkg/octicons/icons/apps-light.png"><img src="../pkg/octicons/icons/apps-light.png" width="20" height="20" alt="apps"></picture><br>`default` | Default toolset | https://api.githubcopilot.com/mcp/ | [Install](https://insiders.vscode.dev/redirect/mcp/install?name=github&config=%7B%22type%22%3A%20%22http%22%2C%22url%22%3A%20%22https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2F%22%7D) | [read-only](https://api.githubcopilot.com/mcp/readonly) | [Install read-only](https://insiders.vscode.dev/redirect/mcp/install?name=github&config=%7B%22type%22%3A%20%22http%22%2C%22url%22%3A%20%22https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2Freadonly%22%7D) |
23:| <picture><source media="(prefers-color-scheme: dark)" srcset="../pkg/octicons/icons/apps-dark.png"><source media="(prefers-color-scheme: light)" srcset="../pkg/octicons/icons/apps-light.png"><img src="../pkg/octicons/icons/apps-light.png" width="20" height="20" alt="apps"></picture><br>`all` | All available GitHub MCP tools | https://api.githubcopilot.com/mcp/x/all | [Install](https://insiders.vscode.dev/redirect/mcp/install?name=gh-all&config=%7B%22type%22%3A%20%22http%22%2C%22url%22%3A%20%22https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2Fx%2Fall%22%7D) | [read-only](https://api.githubcopilot.com/mcp/x/all/readonly) | [Install read-only](https://insiders.vscode.dev/redirect/mcp/install?name=gh-all&config=%7B%22type%22%3A%20%22http%22%2C%22url%22%3A%20%22https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2Fx%2Fall%2Freadonly%22%7D) |
24:| <picture><source media="(prefers-color-scheme: dark)" srcset="../pkg/octicons/icons/workflow-dark.png"><source media="(prefers-color-scheme: light)" srcset="../pkg/octicons/icons/workflow-light.png"><img src="../pkg/octicons/icons/workflow-light.png" width="20" height="20" alt="workflow"></picture><br>`actions` | GitHub Actions workflows and CI/CD operations | https://api.githubcopilot.com/mcp/x/actions | [Install](https://insiders.vscode.dev/redirect/mcp/install?name=gh-actions&config=%7B%22type%22%3A%20%22http%22%2C%22url%22%3A%20%22https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2Fx%2Factions%22%7D) | [read-only](https://api.githubcopilot.com/mcp/x/actions/readonly) | [Install read-only](https://insiders.vscode.dev/redirect/mcp/install?name=gh-actions&config=%7B%22type%22%3A%20%22http%22%2C%22url%22%3A%20%22https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2Fx%2Factions%2Freadonly%22%7D) |
25:| <picture><source media="(prefers-color-scheme: dark)" srcset="../pkg/octicons/icons/code-square-dark.png"><source media="(prefers-color-scheme: light)" srcset="../pkg/octicons/icons/code-square-light.png"><img src="../pkg/octicons/icons/code-square-light.png" width="20" height="20" alt="code-square"></picture><br>`code_quality` | GitHub Code Quality related tools | https://api.githubcopilot.com/mcp/x/code_quality | [Install](https://insiders.vscode.dev/redirect/mcp/install?name=gh-code_quality&config=%7B%22type%22%3A%20%22http%22%2C%22url%22%3A%20%22https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2Fx%2Fcode_quality%22%7D) | [read-only](https://api.githubcopilot.com/mcp/x/code_quality/readonly) | [Install read-only](https://insiders.vscode.dev/redirect/mcp/install?name=gh-code_quality&config=%7B%22type%22%3A%20%22http%22%2C%22url%22%3A%20%22https%3A%2F%2Fapi.githubco
… [7355 more characters truncated]
````

<details><summary>reasoning</summary>

````
I need to know whether the catalog depends on the token type, so I'll check what kind of token `gh` is using and which scopes it has, without printing the token itself. Then I'll see whether `tools/list` works without a token at all, and try a minimal raw JSON-RPC client before reaching for the MCP SDK.

I'm going to check whether the server will list its tools without a token, starting with a quick raw request from a small script in a separate spike directory.
````
</details>

<details><summary>reasoning</summary>

````
Каталог инструментов зависит от токена: classic PAT (`ghp_`) фильтрует их по scopes, а остальные показывают всё. Сейчас проверю, какой токен у gh, не выводя значение, и стартует ли сервер без токена для tools/list.
````
</details>

**[command]** exit=0

````
gh auth status 2>&1 | grep -v -i 'token:' ; gh auth token | cut -c1-4; cd <local path> && printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"spike","version":"0"}}}' '{"jsonrpc":"2.0","method":"notifications/initialized"}' '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | env -u GITHUB_PERSONAL_ACCESS_TOKEN -u GH_TOKEN -u GITHUB_TOKEN timeout 10 bin/github-mcp-server stdio --toolsets all 2>err.log | head -c 600; echo; head -5 err.log
````

````
github.com
  ✓ Logged in to github.com account toolittlecakes (<local path>)
  - Active account: true
  - Git operations protocol: https
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
gho_
{"jsonrpc":"2.0","id":1,"result":{"capabilities":{"completions":{},"prompts":{},"resources":{},"tools":{}},"instructions":"The GitHub MCP Server provides tools to interact with GitHub platform.\n\nTool selection guidance:\n\t1. Use 'list_*' tools for broad, simple retrieval and pagination of all items of a type (e.g., all issues, all PRs, all branches) with basic filtering.\n\t2. Use 'search_*' tools for targeted queries with specific criteria, keywords, or complex filters (e.g., issues with certain text, PRs by author, code containing functions).\n\nContext management:\n\t1. Use pagination wh
time=2026-11-24T10:33:05.964+03:00 level=INFO msg="starting server" version=2.2.0 host="" readOnly=false lockdownEnabled=false
time=2026-11-24T10:33:05.964+03:00 level=INFO msg="using requested OAuth scopes for tool filtering" scopes="[repo read:org read:user user:email read:packages write:packages read:project project gist notifications]"
GitHub MCP Server running on stdio
time=2026-11-24T10:33:06.247+03:00 level=INFO msg="server run start"
time=2026-11-24T10:33:06.248+03:00 level=INFO msg="server connecting"
````

<details><summary>reasoning</summary>

````
Without a token the server starts in OAuth mode, where tool listing is filtered by requested scopes. Since the default OAuth scopes might exclude some admin and security tools, the no-token list could be incomplete. I'll write a Python spike that sends raw JSON-RPC and dumps the full tools/list output across several configurations, starting with no token on the default setting and no token with everything enabled.

I'm going to write the spike script at `$D/spike/dump_catalog.py`, driving the server over raw JSON-RPC with asyncio so it doubles as a check on the thin client. The token comes from `gh auth token` and gets passed to the child through its environment. I'll compare tool counts across the configurations, and also count tokens per tool using tiktoken's o200k_base and a chars/4 estimate, while handling `nextCursor` pagination.
````
</details>

<details><summary>reasoning</summary>

````
Без токена сервер отдаёт tools/list, но по умолчанию фильтрует тулы по запрошенным OAuth scopes, так что каталог может быть неполным. Сейчас напишу спайк-дампер и сниму каталог в нескольких конфигурациях для сравнения.
````
</details>

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+# /// script
+# requires-python = ">=3.13,<3.14"
+# dependencies = ["tiktoken"]
+# ///
+"""Thin async stdio JSON-RPC client: dump tools/list of github-mcp-server under several configs."""
+
+import asyncio
+import json
+import os
+import subprocess
+import sys
+from pathlib import Path
+
+import tiktoken
+
+BASE = Path(__file__).resolve().parent.parent
+BIN = BASE / "bin" / "github-mcp-server"
+ENC = tiktoken.get_encoding("o200k_base")
+
+
+class StdioRpc:
+    def __init__(self, proc: asyncio.subprocess.Process) -> None:
+        self.proc = proc
+        self.next_id = 0
+
+    async def send(self, method: str, params: dict | None = None, notify: bool = False) -> dict | None:
+        msg: dict = {"jsonrpc": "2.0", "method": method}
+        if params is not None:
+            msg["params"] = params
+        if not notify:
+            self.next_id += 1
+            msg["id"] = self.next_id
+        assert self.proc.stdin and self.proc.stdout
+        self.proc.stdin.write((json.dumps(msg) + "\n").encode())
+        await self.proc.stdin.drain()
+        if notify:
+            return None
+        while True:
+            line = await self.proc.stdout.readline()
+            if not line:
+                raise RuntimeError("server closed stdout")
+            resp = json.loads(line)
+            if resp.get("id") == msg["id"]:
+                if "error" in resp:
+                    raise RuntimeError(resp["error"])
+                return resp["result"]
+
+
+async def list_tools(args: list[str], env: dict[str, str]) -> tuple[dict, list[dict]]:
+    proc = await asyncio.create_subprocess_exec(
+        str(BIN), "stdio", *args,
+        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
+        env=env, limit=2**24,
+    )
+    rpc = StdioRpc(proc)
+    init = await rpc.send("initialize", {
+        "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "spike", "version": "0"},
+    })
+    await rpc.send("notifications/initialized", notify=True)
+    tools: list[dict] = []
+    cursor = None
+    while True:
+        res = await rpc.send("tools/list", {"cursor": cursor} if cursor else {})
+        tools += res["tools"]
+        cursor = res.get("nextCursor")
+        if not cursor:
+            break
+    proc.stdin.close()
+    await proc.wait()
+    return init, tools
+
+
+def api_shape(t: dict) -> str:
+    return json.dumps({"name": t["name"], "description": t.get("description", ""), "input_schema": t["inputSchema"]}, ensure_ascii=False)
+
+
+def stats(tools: list[dict]) -> dict:
+    texts = [api_shape(t) for t in tools]
+    return {
+        "tools": len(tools),
+        "chars": sum(map(len, texts)),
+        "tokens_o200k": sum(len(ENC.encode(s)) for s in texts),
+        "read_only": sum(1 for t in tools if t.get("annotations", {}).get("readOnlyHint")),
+    }
+
+
+async def main() -> None:
+    base_env = {k: v for k, v in os.environ.items() if k not in {"GITHUB_PERSONAL_ACCESS_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"}}
+    token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
+    tok_env = base_env | {"GITHUB_PERSONAL_ACCESS_TOKEN": token}
+    configs = {
+        "notoken_default": ([], base_env),
+        "notoken_all": (["--toolsets", "all"], base_env),
+        "ghtoken_default": ([], tok_env),
+        "ghtoken_all": (["--toolsets", "all"], tok_env),
+        "ghtoken_all_readonly": (["--toolsets", "all", "--read-only"], tok_env),
+        "ghtoken_all_insiders": (["--toolsets", "all", "--insiders"], tok_env),
+    }
+    out = {}
+    catalogs = {}
+    for name, (args, env) in configs.items():
+        init, tools = await list_tools(args, env)
+        catalogs[name] = tools
+        out[name] = stats(tools)
+        if name == "ghtoken_all":
+            o
… [654 more characters truncated]
````

**[command]** exit=0

````
uv run -q spike/dump_catalog.py 2>&1 | tail -40
````

````
"tools": 46,
    "chars": 51852,
    "tokens_o200k": 13381,
    "read_only": 27
  },
  "notoken_all": {
    "tools": 91,
    "chars": 109539,
    "tokens_o200k": 27814,
    "read_only": 57
  },
  "ghtoken_default": {
    "tools": 46,
    "chars": 51852,
    "tokens_o200k": 13381,
    "read_only": 27
  },
  "ghtoken_all": {
    "tools": 91,
    "chars": 109539,
    "tokens_o200k": 27814,
    "read_only": 57
  },
  "instructions_tokens": 1559,
  "server_protocol": "2025-06-18",
  "ghtoken_all_readonly": {
    "tools": 57,
    "chars": 62027,
    "tokens_o200k": 16049,
    "read_only": 57
  },
  "ghtoken_all_insiders": {
    "tools": 94,
    "chars": 114024,
    "tokens_o200k": 28946,
    "read_only": 59
  }
}
notoken_all minus others: []
ghtoken_all minus others: []
````

<details><summary>reasoning</summary>

````
The token-based and no-token runs both come back with 91 tools, so the token type isn't what's filtering anything. I'm wondering whether tools needing admin:org are hidden in both cases, so I'll check the README's tool list against that count and also break the tools down by toolset.

I'm checking whether a tool object carries a toolset field, and I'm also looking at whether `list-scopes` or `generate-docs` gives me a tool-to-toolset mapping. I want to compare the README's tool count against 91 to see if some security_events-scoped tools are being hidden, since the no-token scope list didn't include that scope.
````
</details>

<details><summary>reasoning</summary>

````
С токеном и без — цифры одинаковые: при `--toolsets all` 91 тул (~27.8k токенов), по умолчанию 46, а с `--read-only` 57. Фильтр по scopes ничего не срезал, поэтому сверю это с README и полями тулов.
````
</details>

**[command]** exit=0

````
jq -r '.[0] | keys, (._meta // {} | tostring), (.annotations|tostring)' raw/ghtoken_all.json; jq -r '[.[]|.name]|length' raw/ghtoken_all.json; awk '/^## Tools/{f=1} f && /^- \*\*[a-z_]+\*\* - /' bin/README.md | sed -E 's/^- \*\*([a-z_]+)\*\*.*/\1/' | sort -u > /tmp/readme_tools.txt; wc -l < /tmp/readme_tools.txt; jq -r '.[].name' raw/ghtoken_all.json | sort > /tmp/cat_tools.txt; echo "in README not in catalog:"; comm -23 /tmp/readme_tools.txt /tmp/cat_tools.txt | tr '\n' ' '; echo; echo "in catalog not README:"; comm -13 /tmp/readme_tools.txt /tmp/cat_tools.txt | tr '\n' ' '; echo; bin/github-mcp-server list-scopes --help | head -20
````

````
[
  "annotations",
  "description",
  "icons",
  "inputSchema",
  "name"
]
{}
{"idempotentHint":false,"readOnlyHint":true,"title":"Get details of GitHub Actions resources (workflows, workflow runs, jobs, and artifacts)"}
91
96
in README not in catalog:
create_pull_request_with_copilot delete_repository get_copilot_space github_support_docs_search list_copilot_spaces 
in catalog not README:

List the OAuth challenge scopes for all enabled tools.

This command creates an inventory based on the same flags as the stdio command
and outputs the scopes each enabled tool may request in an OAuth challenge.

The output format can be controlled with the --output flag:
  - text (default): Human-readable text output
  - json: JSON output for programmatic use
  - summary: Just the unique scopes needed

Examples:
  # List scopes for default toolsets
  github-mcp-server list-scopes

  # List scopes for specific toolsets
  github-mcp-server list-scopes --toolsets=repos,issues,pull_requests

  # List scopes for all toolsets
  github-mcp-server list-scopes --toolsets=all
````

<details><summary>reasoning</summary>

````
I'm checking the README count: 96 entries, with four remote-only tools accounting for some of them, and delete_repository isn't showing up. I suspect it needs the delete_repo scope, though the token should already cover that, so I want to see whether the stderr log shows any feature-flag filtering.

I'm also pulling the toolset mapping with the list-scopes command in JSON output to see how the scopes group the tools.
````
</details>

<details><summary>reasoning</summary>

````
README называет 96 инструментов, а в каталоге их 91: разница в 4 remote-only инструментах плюс `delete_repository`, причину скрытия которого я сейчас выясняю по маппингу tool→toolset из `list-scopes --output json`.
````
</details>

**[command]** exit=0

````
grep -n -B2 -A8 '\*\*delete_repository\*\*' bin/README.md | head -20; grep -n -i -B2 -A6 'delete_repository' docs/feature-flags.md | head -20; bin/github-mcp-server list-scopes --toolsets=all --output json > raw/list-scopes-all.json 2>/dev/null; jq 'keys' raw/list-scopes-all.json | head; jq -c '.tools[0]' raw/list-scopes-all.json 2>/dev/null | head -3
````

````
1446-  - `repo`: Repository name (string, required)
1447-
1448:- **delete_repository** - Delete repository
1449-  - **OAuth Challenge Scopes**: `delete_repo`, `repo`
1450-  - `owner`: Repository owner (username or organization) (string, required)
1451-  - `repo`: Repository name (string, required)
1452-
1453-- **fork_repository** - Fork repository
1454-  - **OAuth Challenge Scopes**: `repo`
1455-  - `organization`: Organization to fork to (string, optional)
1456-  - `owner`: Repository owner (string, required)
[
  "enabled_toolsets",
  "read_only",
  "scopes_by_tool",
  "tools",
  "tools_by_scope",
  "unique_scopes"
]
{"name":"actions_get","toolset":"actions","read_only":true,"challenge_scopes":["repo"]}
````

<details><summary>reasoning</summary>

````
I'm figuring out why delete_repository is being filtered out: it needs the delete_repo scope, which isn't in the default requested OAuth scopes list. I want to check whether a gho token changes that, and whether list-scopes is just not applying the filter. After that I'll compute per-toolset counts and token totals against the catalog, then build catalog.json.

I'm going to build the catalog by joining the ghtoken_all data with toolset and read_only fields. I also want to check the log again, this time using a token, to see whether the scope filtering behaves differently.
````
</details>

**[command]** exit=0

````
jq '.tools|length' raw/list-scopes-all.json; jq -r '.tools[]|select(.name=="delete_repository")' raw/list-scopes-all.json; jq -r '.unique_scopes|join(",")' raw/list-scopes-all.json; uv run -q - <<'PY'
# /// script
# requires-python = ">=3.13,<3.14"
# ///
import os, subprocess, json, time
tok = subprocess.run(["gh","auth","token"],capture_output=True,text=True,check=True).stdout.strip()
env = {k:v for k,v in os.environ.items()} | {"GITHUB_PERSONAL_ACCESS_TOKEN": tok}
p = subprocess.Popen(["bin/github-mcp-server","stdio","--toolsets","all"],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,env=env,text=True)
time.sleep(2); p.stdin.close(); p.wait(timeout=10)
print("\n".join(l for l in p.stderr.read().splitlines() if "scope" in l.lower() or "WARN" in l or "ERROR" in l))
PY
````

````
147
{
  "name": "delete_repository",
  "toolset": "repos",
  "read_only": false,
  "challenge_scopes": [
    "delete_repo",
    "repo"
  ]
}
admin:enterprise,admin:org,delete_repo,gist,notifications,project,read:enterprise,read:org,read:project,repo,security_events,workflow
````

<details><summary>reasoning</summary>

````
The list-scopes run reports 147 tools with toolsets=all, while tools/list returns only 91, which is a big gap. I suspect list-scopes includes feature-flagged or insiders-only tools, so I'll diff the two lists against the catalog. The delete_repository tool is still missing even with the token, so that needs checking too.
````
</details>

<details><summary>reasoning</summary>

````
Тулов в `list-scopes --toolsets=all` — 147, а tools/list отдаёт только 91. Разбираюсь, что скрывает остальные 56.
````
</details>

**[command]** exit=0

````
jq -r '.tools[].name' raw/list-scopes-all.json | sort > /tmp/ls.txt; comm -23 /tmp/ls.txt /tmp/cat_tools.txt > /tmp/hidden.txt; wc -l < /tmp/hidden.txt; jq -r --rawfile h /tmp/hidden.txt '($h|split("\n")) as $hs | .tools[] | select(.name as $n | $hs|index($n)) | "\(.toolset)\t\(.name)\t\(.challenge_scopes|join(","))"' raw/list-scopes-all.json | sort | column -t | head -70; jq -r '.tools[].name' raw/list-scopes-all.json | sort | uniq -d | head
````

````
56
copilot_automations  create_automation                             repo
copilot_automations  delete_automation                             repo
copilot_automations  get_automation                                repo
copilot_automations  get_automation_revision                       repo
copilot_automations  get_automations_configuration_for_repository  repo
copilot_automations  list_automation_revisions                     repo
copilot_automations  list_automations                              repo
copilot_automations  list_available_automation_tools               repo
copilot_automations  list_available_automation_triggers            repo
copilot_automations  run_automation                                repo
copilot_automations  update_automation                             repo
issues               add_issue_comment_reaction                    repo
issues               add_issue_reaction                            repo
issues               add_sub_issue                                 repo
issues               create_issue                                  repo
issues               find_duplicate                                repo
issues               get_label                                     repo
issues               hide_issue_comment                            repo
issues               issue_artifact_read                           repo
issues               issue_artifact_write                          repo
issues               issue_dependency_read                         repo
issues               issue_dependency_write                        repo
issues               remove_issue_comment_reaction                 repo
issues               remove_issue_reaction                         repo
issues               remove_sub_issue                              repo
issues               reprioritize_sub_issue                        repo
issues               set_issue_fields                              repo
issues               unhide_issue_comment                          repo
issues               update_issue_assignees                        repo
issues               update_issue_body                             repo
issues               update_issue_labels                           repo
issues               update_issue_milestone                        repo
issues               update_issue_state                            repo
issues               update_issue_title                            repo
issues               update_issue_type                             repo
labels               get_label                                     repo
pull_requests        add_pull_request_review_comment               repo
pull_requests        add_pull_request_review_comment_reaction      repo
pull_requests        create_pull_request_review                    repo
pull_requests        delete_pending_pull_request_review            repo
pull_requests        hide_pull_request_review                      repo
pull_requests        hide_pull_request_review_comment              repo
pull_requests        pull_request_review_write                     repo
pull_requests        pull_request_review_write                     repo
pull_requests        remove_pull_request_review_comment_reaction   repo
pull_requests        request_pull_request_reviewers                repo
pull_requests        resolve_review_thread                         repo
pull_requests        resolve_review_thread                         repo
pull_requests        submit_pending_pull_request_review            repo
pull_requests        unhide_pull_request_review                    repo
pull_requests        unhide_pull_request_review_comment            repo
pull_requests        unresolve_review_thread                       repo
pull_requests        update_pull_request_body                      repo
pull_requests        update_pull_request_draft_state               repo
pull_requests        update_pull_request_state                     repo
pull_requests        update_pull_requ
… [248 more characters truncated]
````

<details><summary>reasoning</summary>

````
The flagged variants, like granular tools and copilot automations, show up in list-scopes even when their flags are off, so the true stock catalog for --toolsets all is 91. I suspect delete_repository is gated behind a flag too, so I'll check feature-flags.md for the list of flag headings.
````
</details>

<details><summary>reasoning</summary>

````
Это варианты с флагами (гранулярные `update_issue_*`, copilot_automations и др.), которые `list-scopes` не показывает. Сверю, какие флаги существуют, по `docs/feature-flags.md`.
````
</details>

**[command]** exit=0

````
grep -n -E '^#{1,4} ' docs/feature-flags.md | head -50; grep -n -i -B3 -A3 'delete_repository\|get_file_blame' docs/*.md | head -20
````

````
1:# Feature Flags
11:## Enabling a flag
38:## MCP skills
46:# Equivalent opt-in: GITHUB_FEATURES=skills
100:## Declaring tool availability
102:### Agent automations
112:### Issue artifacts
189:## Tools affected by each flag
198:### `issues_granular`
339:### `pull_requests_granular`
462:### `file_blame`
475:### `issue_dependencies`
507:### `issue_artifacts`
531:### `agent_automations`
621:### `duplicate_detection`
632:### `thread_resolution_reason`
docs/feature-flags.md-461-
docs/feature-flags.md-462-### `file_blame`
docs/feature-flags.md-463-
docs/feature-flags.md:464:- **get_file_blame** - Get file blame information
docs/feature-flags.md-465-  - **OAuth Challenge Scopes**: `repo`
docs/feature-flags.md-466-  - `after`: Cursor for pagination. Use the cursor from the previous response. (string, optional)
docs/feature-flags.md-467-  - `end_line`: Optional 1-based ending line of the window of interest. Must be >= start_line when both are provided. (number, optional)
docs/insiders-features.md-28-
docs/insiders-features.md-29-### `file_blame`
docs/insiders-features.md-30-
docs/insiders-features.md:31:- **get_file_blame** - Get file blame information
docs/insiders-features.md-32-  - **OAuth Challenge Scopes**: `repo`
docs/insiders-features.md-33-  - `after`: Cursor for pagination. Use the cursor from the previous response. (string, optional)
docs/insiders-features.md-34-  - `end_line`: Optional 1-based ending line of the window of interest. Must be >= start_line when both are provided. (number, optional)
````

<details><summary>reasoning</summary>

````
I'm checking why delete_repository stays hidden. My guess is an OAuth scope filter, since delete_repo isn't among the default requested scopes. The gho token I have also lacks delete_repo, so the server may be doing scope detection for that token type too, which doesn't matter much for now.

I'm going to build the catalog from the full stock toolset list, which gives 91 tools, and also check whether all the feature flags change that count. For each toolset, I'll map the tool names from list-scopes, keeping in mind that a few names like get_label appear under more than one toolset.
````
</details>

<details><summary>reasoning</summary>

````
`delete_repository` скрыт scope-фильтром: нужного `delete_repo` нет ни в gh-токене, ни в дефолтном OAuth-наборе. Дальше собираю финальный catalog.json (91 тул) и считаю разбивку по toolsets, плюс «максимальный» вариант со всеми feature flags.
````
</details>

**[command]** exit=0

````
uv run -q - <<'PY'
# /// script
# requires-python = ">=3.13,<3.14"
# dependencies = ["tiktoken"]
# ///
import json, asyncio, os, sys, collections
sys.path.insert(0, "spike")
import tiktoken
from dump_catalog import list_tools, api_shape
enc = tiktoken.get_encoding("o200k_base")
ls = json.load(open("raw/list-scopes-all.json"))
ts = {}
for t in ls["tools"]:
    ts.setdefault(t["name"], t["toolset"])
cat = json.load(open("raw/ghtoken_all.json"))
default = {t["name"] for t in json.load(open("raw/ghtoken_default.json"))}
rows = []
for t in cat:
    rows.append({"name": t["name"], "toolset": ts.get(t["name"], "?"), "in_default": t["name"] in default,
                 "read_only": bool(t.get("annotations", {}).get("readOnlyHint")),
                 "description": t.get("description", ""), "inputSchema": t["inputSchema"], "annotations": t.get("annotations", {}),
                 "tokens_o200k": len(enc.encode(api_shape(t)))})
json.dump({"server": "github/github-mcp-server", "version": "2.2.0", "command": "github-mcp-server stdio --toolsets all",
           "token_method": "tiktoken o200k_base over json.dumps({name, description, input_schema}) per tool",
           "tools": rows}, open("catalog.json", "w"), indent=1, ensure_ascii=False)
agg = collections.defaultdict(lambda: [0, 0, 0, False])
for r in rows:
    a = agg[r["toolset"]]; a[0] += 1; a[1] += r["read_only"]; a[2] += r["tokens_o200k"]; a[3] |= r["in_default"]
print("| toolset | tools | read-only | tokens | default |")
for k, (n, ro, tk, d) in sorted(agg.items(), key=lambda x: -x[1][2]):
    print(f"| {k} | {n} | {ro} | {tk} | {'✓' if d else ''} |")
print("total", len(rows), sum(r["tokens_o200k"] for r in rows))
top = sorted(rows, key=lambda r: -r["tokens_o200k"])[:8]
print("top:", [(r["name"], r["tokens_o200k"]) for r in top])
print("min/median:", min(r["tokens_o200k"] for r in rows), sorted(r["tokens_o200k"] for r in rows)[len(rows)//2])
feats = "issues_granular,pull_requests_granular,file_blame,issue_dependencies,issue_artifacts,agent_automations,duplicate_detection,thread_resolution_reason"
env = {k: v for k, v in os.environ.items() if k not in {"GITHUB_PERSONAL_ACCESS_TOKEN","GH_TOKEN","GITHUB_TOKEN"}}
init, tools = asyncio.run(list_tools(["--toolsets", "all", "--features", feats], env))
print("all+features:", len(tools), sum(len(enc.encode(api_shape(t))) for t in tools))
PY
````

````
| toolset | tools | read-only | tokens | default |
| repos | 19 | 13 | 4702 | ✓ |
| issues | 9 | 5 | 3756 | ✓ |
| pull_requests | 10 | 3 | 3741 | ✓ |
| governance | 4 | 2 | 3057 |  |
| projects | 3 | 2 | 2929 |  |
| actions | 4 | 3 | 1656 |  |
| discussions | 5 | 4 | 1158 |  |
| notifications | 6 | 2 | 1028 |  |
| security_advisories | 4 | 4 | 867 |  |
| labels | 3 | 2 | 614 | ✓ |
| secret_protection | 2 | 2 | 484 |  |
| copilot_issue_intents | 1 | 0 | 468 |  |
| gists | 4 | 2 | 466 |  |
| code_security | 2 | 2 | 447 |  |
| context | 4 | 4 | 418 | ✓ |
| copilot | 2 | 0 | 408 | ✓ |
| stargazers | 3 | 1 | 398 |  |
| dependabot | 2 | 2 | 387 |  |
| users | 1 | 1 | 238 | ✓ |
| orgs | 1 | 1 | 233 |  |
| git | 1 | 1 | 226 |  |
| code_quality | 1 | 1 | 133 |  |
total 91 27814
top: [('projects_write', 1829), ('custom_properties_write', 971), ('issue_write', 940), ('repository_ruleset_read', 920), ('create_repository_ruleset', 864), ('actions_list', 715), ('list_issues', 654), ('pull_request_read', 620)]
min/median: 62 236
all+features: 134 36372
````

<details><summary>reasoning</summary>

````
I'm checking whether the labels toolset shows up in the default list. The labels toolset seems to be marked default, and a labels tool, probably list_label, may be registered under issues as well. The ts mapping takes the first toolset, so the shared label tools are fine. I'll note it as a minor point and move on to the next step.

Next I'm moving to step 4 with the official Python SDK for mcp. I'll check the latest SDK version on PyPI, then write a quick spike that uses ClientSession and stdio_client to call search_repositories and get_file_contents on a public repo in read-only mode. I also want to check JSON Schema validation across all 91 schemas, confirm each has a $schema key, and measure the raw JSON-RPC client on a call as well, then look at the rate limits afterward.
````
</details>

<details><summary>reasoning</summary>

````
Каталог содержит 91 тулу (27 814 токенов) или 134 (36 372 токена) с feature flags; catalog.json сохранён. Далее спайк на официальном Python SDK mcp с `--read-only` и проверка всех 91 схемы через jsonschema.
````
</details>

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+# /// script
+# requires-python = ">=3.13,<3.14"
+# dependencies = ["mcp", "jsonschema"]
+# ///
+"""Official MCP Python SDK spike: list + validate schemas + call read-only tools on public repos."""
+
+import asyncio
+import json
+import os
+import subprocess
+import time
+from importlib.metadata import version
+from pathlib import Path
+
+import jsonschema
+from jsonschema.validators import validator_for
+from mcp import ClientSession, StdioServerParameters
+from mcp.client.stdio import stdio_client
+
+BASE = Path(__file__).resolve().parent.parent
+BIN = BASE / "bin" / "github-mcp-server"
+
+CALLS = [
+    ("search_repositories", {"query": "mcp server language:python stars:>5000", "perPage": 3}),
+    ("get_file_contents", {"owner": "modelcontextprotocol", "repo": "python-sdk", "path": "README.md"}),
+    ("get_file_contents", {"owner": "modelcontextprotocol", "repo": "python-sdk", "path": "src/mcp"}),
+    ("list_commits", {"owner": "modelcontextprotocol", "repo": "python-sdk", "perPage": 30}),
+    ("search_code", {"query": "ClientSession repo:modelcontextprotocol/python-sdk"}),
+    ("get_file_contents", {"owner": "modelcontextprotocol", "repo": "python-sdk", "path": "no/such/file.md"}),
+    ("create_issue", {"owner": "x", "repo": "y", "title": "z"}),
+]
+
+
+def summarize(res) -> dict:
+    blocks = []
+    for b in res.content:
+        d = b.model_dump(exclude_none=True)
+        if d.get("type") == "text":
+            blocks.append({"type": "text", "chars": len(d["text"]), "head": d["text"][:160]})
+        elif d.get("type") == "resource":
+            r = d["resource"]
+            blocks.append({"type": "resource", "uri": r.get("uri"), "mimeType": r.get("mimeType"),
+                           "chars": len(r.get("text") or r.get("blob") or "")})
+        else:
+            blocks.append({"type": d.get("type"), "keys": sorted(d)})
+    return {"isError": res.isError, "blocks": blocks,
+            "structuredContent": None if res.structuredContent is None else len(json.dumps(res.structuredContent)),
+            "total_chars": len(res.model_dump_json())}
+
+
+async def main() -> None:
+    token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
+    env = {k: v for k, v in os.environ.items() if k not in {"GH_TOKEN", "GITHUB_TOKEN"}} | {"GITHUB_PERSONAL_ACCESS_TOKEN": token}
+    params = StdioServerParameters(command=str(BIN), args=["stdio", "--toolsets", "all", "--read-only"], env=env)
+    print("mcp sdk", version("mcp"), "jsonschema", version("jsonschema"))
+    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
+        init = await session.initialize()
+        print("negotiated protocol", init.protocolVersion)
+        tools = (await session.list_tools()).tools
+        bad, drafts = [], set()
+        for t in tools:
+            s = t.inputSchema
+            drafts.add(s.get("$schema", "<none>"))
+            try:
+                validator_for(s, default=jsonschema.Draft202012Validator).check_schema(s)
+            except jsonschema.SchemaError as e:
+                bad.append((t.name, e.message))
+        print(f"{len(tools)} tools; $schema values: {drafts}; invalid schemas: {bad}")
+        validator = jsonschema.Draft202012Validator(next(t.inputSchema for t in tools if t.name == "get_file_contents"))
+        print("validation of bad args:", [e.message for e in validator.iter_errors({"owner": 1, "extra": True})])
+        for name, args in CALLS:
+            t0 = time.monotonic()
+            try:
+                res = await session.call_tool(name, args)
+                print(name, json.dumps(args)[:80], f"{time.monotonic()-t0:.2f}s", json.dumps(summarize(res), ensure_ascii=False))
+            except Exception as e:
+                print(name, "EXC", type(e).__name__, str(e)[:200])
+
+
… [54 more characters truncated]
````

**[command]** exit=0

````
uv run -q spike/sdk_call.py 2>&1 | tail -30
````

````
|                ~~~~~~~~~~~~~~~~~~~~~~~^^
  |   File "<local path>", line 871, in __aexit__
  |     raise BaseExceptionGroup(
  |         "unhandled errors in a TaskGroup", self._exceptions
  |     ) from None
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Exception Group Traceback (most recent call last):
    |   File "<local path>", line 205, in stdio_client
    |     yield read_stream, write_stream
    |   File "<local path>", line 56, in main
    |     async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
    |                                                       ~~~~~~~~~~~~~^^^^^^^^^^^^^
    |   File "<local path>", line 514, in __aexit__
    |     result = await self._task_group.__aexit__(exc_type, exc_val, exc_tb)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "<local path>", line 871, in __aexit__
    |     raise BaseExceptionGroup(
    |         "unhandled errors in a TaskGroup", self._exceptions
    |     ) from None
    | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
    +-+---------------- 1 ----------------
      | Traceback (most recent call last):
      |   File "<local path>", line 58, in main
      |     print("negotiated protocol", init.protocolVersion)
      |                                  ^^^^^^^^^^^^^^^^^^^^
      |   File "<local path>", line 1110, in __getattr__
      |     raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')
      | AttributeError: 'InitializeResult' object has no attribute 'protocolVersion'. Did you mean: 'protocol_version'?
      +------------------------------------
````

<details><summary>reasoning</summary>

````
The SDK v2 seems to use snake_case field names, so I need to check the version and the API surface. This looks like a breaking change worth noting as an SDK breaking-changes pitfall, so I'll confirm the version and which fields are affected.
````
</details>

<details><summary>reasoning</summary>

````
Официальный SDK уже на новой мажорной версии с полями в snake_case, поэтому мой код, написанный по памяти, не заработал. Сейчас смотрю актуальную версию и её API.
````
</details>

**[command]** exit=0

````
cd <local path> && ls -d mcp-*.dist-info jsonschema-*.dist-info; grep -n -E '^\s+(protocol_version|input_schema|is_error|structured_content|content)\b|^class (InitializeResult|Tool|CallToolResult)\b' mcp/types*.py mcp/types/*.py 2>/dev/null | head -20; grep -n 'def call_tool\|def list_tools\|def initialize' -A6 mcp/client/session.py | head -40
````

````
jsonschema-4.26.0.dist-info
mcp-2.3.0.dist-info
651:    async def initialize(self) -> types.InitializeResult:
652-        if self._initialize_result is not None:
653-            return self._initialize_result
654-        result = await self.send_request(
655-            types.InitializeRequest(
656-                params=types.InitializeRequestParams(
657-                    protocol_version=LATEST_HANDSHAKE_VERSION,
--
796:    def initialize_result(self) -> types.InitializeResult | None:
797-        """The server's InitializeResult. None unless `initialize()` ran (or was adopted)."""
798-        return self._initialize_result
799-
800-    @property
801-    def discover_result(self) -> types.DiscoverResult | None:
802-        """The server's DiscoverResult. None unless `discover()` ran (or was adopted).
--
993:    async def call_tool(
994-        self,
995-        name: str,
996-        arguments: dict[str, Any] | None = None,
997-        read_timeout_seconds: float | None = None,
998-        progress_callback: ProgressFnT | None = None,
999-        *,
--
1008:    async def call_tool(
1009-        self,
1010-        name: str,
1011-        arguments: dict[str, Any] | None = None,
1012-        read_timeout_seconds: float | None = None,
1013-        progress_callback: ProgressFnT | None = None,
1014-        *,
--
1023:    async def call_tool(
1024-        self,
1025-        name: str,
1026-        arguments: dict[str, Any] | None = None,
1027-        read_timeout_seconds: float | None = None,
1028-        progress_callback: ProgressFnT | None = None,
1029-        *,
--
Shell cwd was reset to <local path>
````

**[command]** exit=0

````
P=<local path> ls $P $P/types 2>/dev/null | head -40; grep -rn -E 'class (CallToolResult|Tool|InitializeResult)\(' $P | head; grep -rn -E '^\s+(input_schema|is_error|structured_content|protocol_version):' $P/types* -r | head
````

````
<local path>
__init__.py
__pycache__
cli
client
os
py.typed
server
shared
types

<local path>
__init__.py
__pycache__
jsonrpc.py
methods.py
version.py
<local path> Tool(BaseModel):
````

**[command]** exit=0

````
P=<local path> head -40 $P/mcp/types/__init__.py; ls $P | grep -i -E 'mcp|types' 
````

````
"""The MCP protocol wire types, as the `mcp.types` namespace.

This module mirrors the standalone `mcp_types` package exactly (every name is the
same object), so SDK users can keep the familiar v1 spelling:

    import mcp.types as types

    types.TextContent(type="text", text="hi")

The `mcp.types.jsonrpc`, `mcp.types.methods`, and `mcp.types.version`
submodules mirror `mcp_types.jsonrpc`, `mcp_types.methods`, and
`mcp_types.version` the same way, so every supported `mcp_types` import has
an `mcp.types` spelling.

Depend on and import `mcp_types` directly instead when you only need to
(de)serialize MCP traffic and don't want the SDK's transport stack: its only
runtime dependencies are `pydantic` and `typing-extensions`.
"""

# A wildcard mirror of the mcp_types namespace is the whole point of this module.
# pyright: reportWildcardImportFromLibrary=false

from mcp_types import *
from mcp_types import __all__ as __all__

# Bind the mirror submodules on the package, so `mcp.types.version.X` is as
# reachable by attribute access as `mcp_types.version.X` (whose `__init__`
# binds `.version` by importing from it), not only via `from ... import`.
from . import jsonrpc as jsonrpc
from . import methods as methods
from . import version as version
annotated_types
annotated_types-0.8.0.dist-info
mcp
mcp-2.3.0.dist-info
mcp_types
mcp_types-2.3.0.dist-info
````

**[command]** exit=0

````
P=<local path> grep -rn -E '^class (CallToolResult|Tool|InitializeResult|TextContent|EmbeddedResource)\b' -A25 $P | grep -E 'class |: ' | grep -v '"""' | head -50
````

````
<local path> InitializeResult(Result):
<local path>    protocol_version: str
<local path>    capabilities: ServerCapabilities
<local path>    server_info: Implementation
<local path>    instructions: str | None = None
<local path> InitializedNotification(Notification[NotificationParams | None, Literal["notifications/initialized"]]):
<local path> TextContent(MCPModel):
<local path>    type: Literal["text"] = "text"
<local path>    text: str
<local path>    annotations: Annotations | None = None
<local path>    meta: Meta | None = Field(alias="_meta", default=None)
<local path> ImageContent(MCPModel):
<local path>    type: Literal["image"] = "image"
<local path>    data: str
<local path>    mime_type: str
<local path> EmbeddedResource(MCPModel):
<local path>    type: Literal["resource"] = "resource"
<local path>    resource: TextResourceContents | BlobResourceContents
<local path>    annotations: Annotations | None = None
<local path>    meta: Meta | None = Field(alias="_meta", default=None)
<local path> ResourceLink(Resource):
<local path>    Note: resource links returned by tools are not guaranteed to appear in the results of `resources/list` requests.
<local path>    type: Literal["resource_link"] = "resource_link"
<local path> Tool(BaseMetadata):
<local path>    description: str | None = None
<local path>
… [4106 more characters truncated]
````

<details><summary>reasoning</summary>

````
The SDK is on 2.3.0, which uses snake_case, so the update script needs protocol_version, input_schema, is_error, and structured_content renamed. The server may also negotiate the 2026-07-28 protocol, which would mean typed structuredContent for the repository tools. I'll fix the names with sed.
````
</details>

**[agent]**

mcp SDK 2.3.0 (+ отдельный пакет `mcp_types`), поля snake_case: `protocol_version`, `input_schema`, `is_error`, `structured_content`. Правлю спайк.

**[command]** exit=0

````
cd <local path> && sed -i -e 's/init\.protocolVersion/init.protocol_version/' -e 's/t\.inputSchema/t.input_schema/g' -e 's/res\.isError/res.is_error/' -e 's/res\.structuredContent/res.structured_content/g' -e 's/r.get("mimeType")/r.get("mime_type")/' spike/sdk_call.py && uv run -q spike/sdk_call.py 2>&1 | tail -30
````

````
time=2026-11-24T10:35:49.027+03:00 level=INFO msg="starting server" version=2.2.0 host="" readOnly=true lockdownEnabled=false
GitHub MCP Server running on stdio
time=2026-11-24T10:35:49.224+03:00 level=INFO msg="server run start"
time=2026-11-24T10:35:49.224+03:00 level=INFO msg="server connecting"
time=2026-11-24T10:35:49.225+03:00 level=INFO msg="server session connected" session_id=""
time=2026-11-24T10:35:49.235+03:00 level=INFO msg="session initialized"
time=2026-11-24T10:35:56.021+03:00 level=INFO msg="server session disconnected" session_id=""
time=2026-11-24T10:35:56.021+03:00 level=INFO msg="server session ended"
mcp sdk 2.3.0 jsonschema 4.26.0
negotiated protocol 2025-11-25
57 tools; $schema values: {'<none>'}; invalid schemas: []
validation of bad args: ["1 is not of type 'string'", "'repo' is a required property"]
search_repositories {"query": "mcp server language:python stars:>5000", "perPage": 3} 0.76s {"isError": false, "blocks": [{"type": "text", "chars": 1598, "head": "{\"total_count\":19,\"incomplete_results\":false,\"items\":[{\"id\":952238700,\"name\":\"mcp\",\"full_name\":\"awslabs/mcp\",\"description\":\"Open source MCP Servers for AWS\",\"ht"}], "structuredContent": null, "total_chars": 1926}
get_file_contents {"owner": "modelcontextprotocol", "repo": "python-sdk", "path": "README.md"} 1.28s {"isError": false, "blocks": [{"type": "text", "chars": 81, "head": "successfully downloaded text file (SHA: 50ea0ed227b72de82917d67d678d1d24783ab2e9)"}, {"type": "resource", "uri": "repo://modelcontextprotocol/python-sdk/sha/77001c96f9507be0f4d009b83210a384a5e08bda/contents/README.md", "mimeType": "text/plain; charset=utf-8", "chars": 4561}], "structuredContent": null, "total_chars": 5189}
get_file_contents {"owner": "modelcontextprotocol", "repo": "python-sdk", "path": "src/mcp"} 1.27s {"isError": false, "blocks": [{"type": "text", "chars": 4287, "head": "[{\"type\":\"file\",\"size\":3719,\"name\":\"__init__.py\",\"path\":\"src/mcp/__init__.py\",\"sha\":\"28bc4703edeae63396eddd08415b254a45b871b2\",\"url\":\"https://api.github.com/rep"}], "structuredContent": null, "total_chars": 4685}
list_commits {"owner": "modelcontextprotocol", "repo": "python-sdk", "perPage": 30} 0.68s {"isError": false, "blocks": [{"type": "text", "chars": 23750, "head": "[{\"sha\":\"77001c96f9507be0f4d009b83210a384a5e08bda\",\"html_url\":\"https://github.com/modelcontextprotocol/python-sdk/commit/77001c96f9507be0f4d009b83210a384a5e08bd"}], "structuredContent": null, "total_chars": 26165}
search_code {"query": "ClientSession repo:modelcontextprotocol/python-sdk"} 0.84s {"isError": false, "blocks": [{"type": "text", "chars": 33954, "head": "{\"total_count\":126,\"incomplete_results\":false,\"items\":[{\"name\":\"session.py\",\"path\":\"src/mcp/client/session.py\",\"sha\":\"35cae2d314e5c68959309911486d8c02f57412cc\","}], "structuredContent": null, "total_chars": 36195}
get_file_contents {"owner": "modelcontextprotocol", "repo": "python-sdk", "path": "no/such/file.md 1.70s {"isError": true, "blocks": [{"type": "text", "chars": 122, "head": "Failed to get file contents. The path does not point to a file or directory, or the file does not exist in the repository."}], "structuredContent": null, "total_chars": 271}
create_issue EXC MCPError unknown tool "create_issue"
[This command modified 1 file you've previously read: spike/sdk_call.py. Call Read before editing.]
````

<details><summary>reasoning</summary>

````
I've confirmed the server works. Server stderr is leaking into our own stderr because the SDK's stdio_client defaults errlog to sys.stderr, so I need to pass an errlog parameter. The negotiated protocol version is 2025-11-25, and there's no structuredContent in the response. Sending an extra property didn't fail, so additionalProperties doesn't seem to be set to false; I'll check how many catalog schemas use that and which other schema features (enums, items, anyOf, oneOf, $ref, format) appear.

Next I'm checking the remaining schema features against the full catalog of 91 tools, not just the 57 read-only ones the spike covered. I also want to see whether any of them use constructs that LLM APIs tend to reject, like strict-mode additionalProperties or a non-object root type. On the size side, the search and commit-listing results are large, so I'll measure their token cost and look up what the content-window setting controls.

Next I'm checking the remote endpoint too, since an OAuth token from the gh CLI might authenticate a streamable HTTP request to the hosted server. Running the schema analysis, token counts, rate limits, and that remote test together should be cheap.
````
</details>

<details><summary>reasoning</summary>

````
SDK-путь работает: все 57 read-only тулов проходят валидацию, а вызовы занимают 0.7–1.7 с. Дальше проверю схемы на всех 134 тулах, токены больших результатов, rate limits и remote endpoint.
````
</details>

**[command]** exit=0

````
grep -n -i -B2 -A12 '^#* *lockdown\|content-window-size\|content_window' bin/README.md docs/server-configuration.md | grep -v '^--$' | head -50
````

````
bin/README.md-1731-```
bin/README.md-1732-
bin/README.md:1733:## Lockdown Mode
bin/README.md-1734-
bin/README.md:1735:Lockdown mode limits the content that the server will surface from public repositories. When enabled, the server checks whether the author of each item has push access to the repository. Private repositories are unaffected, and collaborators keep full access to their own content.
bin/README.md-1736-
bin/README.md:1737:Lockdown mode is a best-effort content filter intended to reduce the risk of prompt injection from untrusted repository content (issues, pull requests, comments, commits, etc.). It is **not** an authorization boundary: it does not change what the underlying GitHub credential can read or write, and content withheld from a filtered tool response may still be reachable through other tools or direct GitHub API access with the same credential.
bin/README.md-1738-
bin/README.md-1739-As an intentional exception, content authored by a small set of trusted bot accounts (currently `github-actions[bot]` and `copilot`) is always treated as safe, regardless of push access. This avoids filtering routine automation output (e.g. CI-generated commits or comments) that would otherwise be withheld under lockdown mode.
bin/README.md-1740-
bin/README.md-1741-```bash
bin/README.md-1742-./github-mcp-server --lockdown-mode
bin/README.md-1743-```
bin/README.md-1744-
bin/README.md-1745-When running with Docker, set the corresponding environment variable:
bin/README.md-1746-
bin/README.md-1747-```bash
bin/README.md-1748-docker run -i --rm \
bin/README.md-1749-  -e GITHUB_PERSONAL_ACCESS_TOKEN=<your-token> \
docs/server-configuration.md-289----
docs/server-configuration.md-290-
docs/server-configuration.md:291:### Lockdown Mode
docs/server-configuration.md-292-
docs/server-configuration.md-293-**Best for:** Public repositories where you want to limit content from users without push access.
docs/server-configuration.md-294-
docs/server-configuration.md:295:Lockdown mode ensures the server only surfaces content in public repositories from users with push access to that repository. Private repositories are unaffected, and collaborators retain full access to their own content.
docs/server-configuration.md-296-
docs/server-configuration.md-297-> In HTTP mode, server-side lockdown mode (`--lockdown-mode` / `GITHUB_LOCKDOWN_MODE`) is an upper bound: the `X-MCP-Lockdown` header can enable lockdown mode for a request when the operator has not enabled it server-wide, but it cannot disable lockdown mode the operator has already enabled.
docs/server-configuration.md-298-
docs/server-configuration.md:299:Lockdown mode is a best-effort content filter meant to reduce prompt-injection risk from untrusted repository content; it is not an authorization boundary. It does not restrict what the underlying credential can otherwise read or write, and content withheld from a filtered tool response may still be reachable through other tools or direct GitHub API access with the same credential.
docs/server-configuration.md-300-
docs/server-configuration.md-301-As an intentional exception, content authored by trusted bot accounts (currently `github-actions[bot]` and `copilot`) is always treated as safe, regardless of push access, so routine automation output isn't filtered.
docs/server-configuration.md-302-
docs/server-configuration.md-303-**Example:**
docs/server-configuration.md-304-<table>
docs/server-configuration.md-305-<tr><th>Remote Server</th><th>Local Server</th></tr>
docs/server-configuration.md-306-<tr valign="top">
docs/server-configuration.md-307-<td>
docs/server-configuration.md-308-
docs/server-configuration.md-309-```json
docs/server-configuration.md-310-{
docs/server-configuration.md-311-  "type": "http",
````

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+# /// script
+# requires-python = ">=3.13,<3.14"
+# dependencies = ["jsonschema", "tiktoken", "httpx"]
+# ///
+"""Schema feature census over catalogs, result-size tokens, rate limits, remote endpoint probe."""
+
+import collections
+import json
+import subprocess
+from pathlib import Path
+
+import httpx
+import jsonschema
+import tiktoken
+
+BASE = Path(__file__).resolve().parent.parent
+ENC = tiktoken.get_encoding("o200k_base")
+KEYWORDS = {"anyOf", "oneOf", "allOf", "$ref", "$defs", "definitions", "format", "pattern", "enum", "const",
+            "minimum", "maximum", "items", "additionalProperties", "default", "not", "if", "type"}
+
+
+def walk(node, counter: collections.Counter, path=""):
+    if isinstance(node, dict):
+        for k, v in node.items():
+            if k in KEYWORDS and path.split("/")[-1] != "properties":
+                counter[k] += 1
+                if k == "type" and isinstance(v, list):
+                    counter["type:list"] += 1
+            walk(v, counter, f"{path}/{k}")
+    elif isinstance(node, list):
+        for v in node:
+            walk(v, counter, path)
+
+
+def census(tools: list[dict], key: str) -> None:
+    kw = collections.Counter()
+    root_ap_false, root_not_object, invalid = 0, 0, []
+    for t in tools:
+        s = t[key]
+        walk(s, kw)
+        root_ap_false += s.get("additionalProperties") is False
+        root_not_object += s.get("type") != "object"
+        try:
+            jsonschema.Draft202012Validator.check_schema(s)
+        except jsonschema.SchemaError as e:
+            invalid.append((t["name"], e.message))
+    print(f"{len(tools)} tools: root additionalProperties=false: {root_ap_false}, root type!=object: {root_not_object}, invalid: {invalid}")
+    print("  keyword usage:", dict(kw.most_common()))
+
+
+def main() -> None:
+    census(json.loads((BASE / "catalog.json").read_text())["tools"], "inputSchema")
+
+    token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
+    h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
+    rl = httpx.get("https://api.github.com/rate_limit", headers=h).json()["resources"]
+    print("rate limits:", {k: (v["limit"], v["remaining"]) for k, v in rl.items() if k in {"core", "search", "code_search", "graphql"}})
+
+    body = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
+            "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "spike", "version": "0"}}}
+    hh = {"Authorization": f"Bearer {token}", "Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
+    for url, extra in [("https://api.githubcopilot.com/mcp/readonly", {}), ("https://api.githubcopilot.com/mcp/x/all/readonly", {})]:
+        with httpx.Client(timeout=20) as c:
+            r = c.post(url, headers=hh | extra, json=body)
+            print("remote", url, r.status_code, r.headers.get("content-type"), r.text[:200].replace("\n", " "))
+            if r.status_code != 200:
+                continue
+            sid = r.headers.get("mcp-session-id")
+            h2 = hh | ({"Mcp-Session-Id": sid} if sid else {})
+            c.post(url, headers=h2, json={"jsonrpc": "2.0", "method": "notifications/initialized"})
+            r2 = c.post(url, headers=h2, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
+            txt = r2.text
+            data = json.loads(txt.split("data: ", 1)[1]) if txt.startswith(("event:", "data:")) else r2.json()
+            names = [t["name"] for t in data["result"]["tools"]]
+            print("  remote tools:", len(names), "tokens:", sum(len(ENC.encode(json.dumps({"name": t["name"], "description": t.get("description", ""), "input_schema": t["inputSchema"]}))) for t in data["result"]["tools"]))
+            (BASE / "raw" / f
… [163 more characters truncated]
````

**[command]** exit=0

````
uv run -q spike/schema_and_limits.py 2>&1 | tail -20
````

````
91 tools: root additionalProperties=false: 1, root type!=object: 0, invalid: []
  keyword usage: {'type': 696, 'enum': 99, 'minimum': 55, 'items': 30, 'maximum': 28, 'additionalProperties': 13, 'default': 11, 'oneOf': 5, 'anyOf': 5, 'type:list': 1}
rate limits: {'core': (5000, 4962), 'search': (30, 29), 'graphql': (5000, 4996), 'code_search': (10, 9)}
remote https://api.githubcopilot.com/mcp/readonly 200 text/event-stream event: message data: {"jsonrpc":"2.0","id":1,"result":{"capabilities":{"completions":{},"prompts":{},"resources":{},"tools":{}},"instructions":"The GitHub MCP Server provides tools to interact with Gi
  remote tools: 29 tokens: 8261
remote https://api.githubcopilot.com/mcp/x/all/readonly 200 text/event-stream event: message data: {"jsonrpc":"2.0","id":1,"result":{"capabilities":{"completions":{},"prompts":{},"resources":{},"tools":{}},"instructions":"The GitHub MCP Server provides tools to interact with Gi
  remote tools: 75 tokens: 19407
````

<details><summary>reasoning</summary>

````
I've confirmed remote access works with the gho token, and the remote set has 75 read-only tools against 57 locally, including a few remote-only extras. I want to diff the two read-only lists, check how the oneOf/anyOf schemas are used, and estimate token counts for the large search_code result.

I'm going to estimate the token counts for the large search results. Rather than guess at a chars-per-token ratio, I'll write a small script against the raw client from the catalog dump and measure it directly.
````
</details>

<details><summary>reasoning</summary>

````
Удалённый endpoint отвечает и на `gho_`-токен из gh: `/mcp/readonly` даёт 29 тулов, `/mcp/x/all/readonly` — 75 (около 19.4k токенов). Далее сравню дифф remote и local по схемам oneOf/anyOf и сниму точные токены больших результатов.
````
</details>

**[command]** exit=0

````
echo "remote-only (all/readonly vs local all/readonly):"; comm -23 <(jq -r '.[].name' raw/remote_x_all_readonly.json | sort) <(jq -r '.[].name' raw/ghtoken_all_readonly.json | sort) | tr '\n' ' '; echo; echo "local-only:"; comm -13 <(jq -r '.[].name' raw/remote_x_all_readonly.json | sort) <(jq -r '.[].name' raw/ghtoken_all_readonly.json | sort) | tr '\n' ' '; echo; jq -r '.tools[] | select((.inputSchema|tostring)|test("\"(oneOf|anyOf)\"")) | .name' catalog.json | tr '\n' ' '; echo; jq -c '.tools[] | select(.name=="projects_write") | .inputSchema | [paths(type=="object" and (has("oneOf") or has("anyOf")))] ' catalog.json | head -c 400; echo; uv run -q - <<'PY'
# /// script
# requires-python = ">=3.13,<3.14"
# dependencies = ["tiktoken"]
# ///
import asyncio, json, os, subprocess, sys
sys.path.insert(0, "spike")
import tiktoken
from dump_catalog import StdioRpc, BIN
enc = tiktoken.get_encoding("o200k_base")
async def main():
    tok = subprocess.run(["gh","auth","token"],capture_output=True,text=True,check=True).stdout.strip()
    env = dict(os.environ) | {"GITHUB_PERSONAL_ACCESS_TOKEN": tok}
    p = await asyncio.create_subprocess_exec(str(BIN),"stdio","--toolsets","all","--read-only",stdin=-1,stdout=-1,stderr=-3,env=env,limit=2**26)
    rpc = StdioRpc(p)
    await rpc.send("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"s","version":"0"}})
    await rpc.send("notifications/initialized",notify=True)
    for name,args in [("search_code",{"query":"ClientSession repo:modelcontextprotocol/python-sdk"}),
                      ("list_commits",{"owner":"modelcontextprotocol","repo":"python-sdk","perPage":30}),
                      ("list_issues",{"owner":"modelcontextprotocol","repo":"python-sdk","perPage":30}),
                      ("get_file_contents",{"owner":"python","repo":"cpython","path":"Lib/typing.py"}),
                      ("get_me",{})]:
        r = await rpc.send("tools/call",{"name":name,"arguments":args})
        txt = "".join(b.get("text","") or b.get("resource",{}).get("text","") for b in r["content"])
        print(name, "isError" if r.get("isError") else "ok", "chars", len(txt), "tokens", len(enc.encode(txt)), "blocks", [b["type"] for b in r["content"]])
    p.stdin.close(); await p.wait()
asyncio.run(main())
PY
````

````
remote-only (all/readonly vs local all/readonly):
check_dependency_vulnerabilities get_automation get_automation_group get_automation_revision get_automations_configuration_for_repository get_copilot_job_status get_copilot_session_events get_copilot_space get_copilot_task_status github_support_docs_search list_automation_groups list_automation_revisions list_automations list_available_automation_tools list_available_automation_triggers list_copilot_spaces run_secret_scanning semantic_issue_similarity_search 
local-only:

custom_properties_write issue_write projects_write 
[["properties","filter"],["properties","items","items"],["properties","updated_field"]]

search_code ok chars 33954 tokens 9903 blocks ['text']
list_commits ok chars 23750 tokens 7705 blocks ['text']
list_issues ok chars 102727 tokens 27851 blocks ['text']
get_file_contents ok chars 139837 tokens 32021 blocks ['text', 'resource']
get_me ok chars 419 tokens 130 blocks ['text']
````

<details><summary>reasoning</summary>

````
Token costs are high: listing issues runs about 28k tokens and fetching typing.py about 32k, so truncating output is clearly needed. Calls to the remote server need a token, and tools/list works without one for the local server. I'm also weighing whether a call without a token errors out.

I'm wondering whether calling get_file_contents without a token kicks off an interactive OAuth login that could hang or open a browser. I'll run a quick test through the thin client with a 15-second timeout, since the harness needs to fail fast.
````
</details>

<details><summary>reasoning</summary>

````
Большие результаты подтверждены: list_issues при perPage=30 дает около 27.9k токенов, get_file_contents по typing.py около 32k. Дальше проверю, что происходит при вызове тула без токена, чтобы harness не завис на интерактивном логине.
````
</details>

**[command]** exit=0

````
timeout 40 uv run -q - <<'PY'
# /// script
# requires-python = ">=3.13,<3.14"
# dependencies = ["tiktoken"]
# ///
import asyncio, json, os, sys, time
sys.path.insert(0, "spike")
from dump_catalog import StdioRpc, BIN
async def main():
    env = {k:v for k,v in os.environ.items() if k not in {"GITHUB_PERSONAL_ACCESS_TOKEN","GH_TOKEN","GITHUB_TOKEN"}}
    p = await asyncio.create_subprocess_exec(str(BIN),"stdio","--read-only",stdin=-1,stdout=-1,stderr=-1,env=env)
    rpc = StdioRpc(p)
    await rpc.send("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"s","version":"0"}})
    await rpc.send("notifications/initialized",notify=True)
    t0=time.monotonic()
    try:
        r = await asyncio.wait_for(rpc.send("tools/call",{"name":"get_me","arguments":{}}), 20)
        print(f"{time.monotonic()-t0:.1f}s", json.dumps(r)[:400])
    except Exception as e:
        print(f"{time.monotonic()-t0:.1f}s EXC", type(e).__name__, str(e)[:300])
    p.kill()
    err = (await p.stderr.read()).decode()
    print("\n".join(l[:200] for l in err.splitlines() if "oauth" in l.lower() or "auth" in l.lower() or "ERROR" in l)[:1500])
asyncio.run(main())
PY
````

````
0.4s {"content": [{"type": "text", "text": "Visit https://github.com/login/device and enter the code 6F26-B41A to authorize the GitHub MCP Server.\n\nAfter authorizing, retry your request.\n\nNote: your MCP client does not appear to support secure URL elicitation. For improved security, consider asking your agent, CLI, or IDE to add it (for example, by opening an issue)."}]}
time=2026-11-24T10:37:06.839+03:00 level=INFO msg="using requested OAuth scopes for tool filtering" scopes="[repo read:org read:user user:email read:packages write:packages read:project project gist n
time=2026-11-24T10:37:07.376+03:00 level=INFO msg="surfacing github authorization instructions to user"
````

<details><summary>reasoning</summary>

````
Without a token, the tool starts a device flow and returns plain text asking for a visit to a URL, not an error, which could confuse a harness into showing that text to the model. The device code is harmless since it expires, and I haven't authorized anything. Next I want to confirm a few details: the Docker image name, and what the `generate-docs` command does.

Next I'm checking the remaining details: whether the output schemas fit protocol version 2026-07-28, given the SDK negotiated 2025-11-25. I also want to look at the stderr handling in `stdio_client`, specifically the errlog parameter and its signature. The SDK is anyio-based, so it should work under asyncio, though its ExceptionGroup tracebacks are noisy and worth noting.
````
</details>

<details><summary>reasoning</summary>

````
Без токена сервер запускает GitHub device flow и отдаёт инструкцию «Visit github.com/login/device» как обычный успешный ответ, что для harness является ловушкой. Сейчас проверю сигнатуру `stdio_client`, чтобы понять, куда направить stderr сервера, и затем напишу отчёт.
````
</details>

**[command]** exit=0

````
P=<local path> grep -n 'async def stdio_client' -A4 $P/client/stdio.py; grep -n 'LATEST_HANDSHAKE_VERSION\s*=' -r $P ../mcp_types 2>/dev/null | head -3; grep -rn 'LATEST_HANDSHAKE_VERSION *=' $P/../mcp_types | head -2; wc -l $P/client/session.py $P/client/stdio.py
````

````
115:async def stdio_client(
116-    server: StdioServerParameters, errlog: TextIO = sys.stderr
117-) -> AsyncGenerator[TransportStreams, None]:
118-    """Spawns an MCP server subprocess and connects to it over stdin/stdout.
119-
 1506 <local path>
  355 <local path>
 1861 total
````

<details><summary>reasoning</summary>

````
Docker is the other piece: the README points to the `ghcr.io/github/github-mcp-server` image, so I'll mention that. Before relying on it, I want to confirm the tagged `v2.2.0` image actually exists, so I'm checking its manifest with `docker manifest inspect`.
````
</details>

**[command]** exit=0

````
timeout 30 docker manifest inspect ghcr.io/github/github-mcp-server:2.2.0 2>&1 | head -5 || true; timeout 30 docker manifest inspect ghcr.io/github/github-mcp-server:v2.2.0 2>&1 | grep -c mediaType
````

````
{
   "schemaVersion": 2,
   "mediaType": "application/vnd.oci.image.index.v1+json",
   "manifests": [
      {
5
````

<details><summary>reasoning</summary>

````
Now I'm putting the report together: a summary, a numbers table, the mechanisms, how to obtain the catalog, auth, an integration comparison, pitfalls, a recommendation, and the artifacts. I also need to settle which configuration the "before" measurement should use, since the demo is read-only, the read-only toolset at 57 tools and about 16k tokens looks like the better baseline compared with all 91 tools at 27.8k.

Now I'm weighing a thin hand-rolled client against the official SDK. The thin version is roughly 60 lines and skips notifications, concurrent requests, and server-initiated calls, while the SDK covers all of that at the cost of heavier dependencies and API churn. I'm leaning toward the SDK, pinned to `mcp>=2.3,<3`, since it is less code for me to maintain.

I'm considering how to handle harness-side filtering: since the server only registers read-only tools when `--read-only` is set, the client's catalog can't reach write tools anyway, so the read-only flag alone is enough. I'm also noting that tool names and descriptions act as the search index, and that `title` annotations would help there. Finally, I'm weighing lockdown mode against rate limits and result truncation, plus the difference between remote and local catalogs.

I'm noting that the server returns roughly 1.5k tokens of instructions during initialize, so I need to decide whether those belong in the prompt for the "before" measurement. I also want to check the token method: counting with tiktoken's o200k_base over the serialized name, description, and schema is only an approximation, since Anthropic's tokenizer differs and the API adds its own tool-use overhead, so exact figures would need the count_tokens endpoint.

Next I'm checking which tools fall in both the default set and the read-only set, so I can count them with a quick jq filter over the catalog.
````
</details>

**[agent]**

Все данные собраны, docker-образ `ghcr.io/github/github-mcp-server:v2.2.0` тоже существует. Досчитаю default+read-only и пишу отчёт.

**[command]** exit=0

````
jq -r '[.tools[]|select(.in_default and .read_only)] | "\(length) \(map(.tokens_o200k)|add)"' catalog.json; jq -r '[.tools[]|.description|length]|add/length' catalog.json; jq -r '.tools[]|select(.inputSchema.additionalProperties==false)|.name' catalog.json; ls raw spike
````

````
27 7722
133.25274725274724
create_repository_ruleset
raw:
ghtoken_all.json
ghtoken_all_insiders.json
ghtoken_all_readonly.json
ghtoken_default.json
list-scopes-all.json
notoken_all.json
notoken_default.json
remote_readonly.json
remote_x_all_readonly.json

spike:
__pycache__
dump_catalog.py
schema_and_limits.py
sdk_call.py
````

**[file change]**

`<local path>` (add)

````
--- /dev/null
+++ b<local path>
+# GitHub MCP server как каталог deferred-тулов: ресерч и спайк
+
+Дата: 2026-11-24. Всё ниже проверено на релизе **github/github-mcp-server v2.2.0** (16.11.2026, commit `67d4dc4`), а не по памяти. Скрэтч, бинарь, спайк-скрипты и сырые дампы лежат в `reports/github-mcp/`.
+
+## TL;DR
+
+- Локально `--toolsets all` даёт **91 тул ≈ 27.8k токенов** (o200k) на описания и схемы. Default даёт 46 тулов ≈ 13.4k, `--toolsets all --read-only` даёт 57 тулов ≈ 16.0k. Со всеми feature flags получается 134 тула ≈ 36.4k.
+- Своих механизмов «подгружать тулы по требованию» у сервера **больше нет**: `--dynamic-toolsets` (мета-тулы `enable_toolset` / `list_available_toolsets` / `get_toolset_tools`) удалили в v1.1.0 (PR #2512, май 2026) как техдолг. Остались только статические фильтры: toolsets, отдельные tools, `--read-only`, scope-фильтр, lockdown. Наш tool_search поэтому не дублирует то, что уже есть в апстриме: апстрим от такого подхода отказался.
+- Каталог снимается обычным MCP `tools/list` по stdio. Токен для этого **не нужен**. Отдельной команды для JSON-дампа нет: `generate-docs` пишет markdown, а `list-scopes --output json` выдаёт инвентарь без учёта feature flags (147 записей), это не реальный набор тулов.
+- `gh auth token` (OAuth-токен с префиксом `gho_`, scopes `gist, read:org, repo, workflow`) работает и с локальным бинарём (через env `GITHUB_PERSONAL_ACCESS_TOKEN`), и с remote `api.githubcopilot.com/mcp/...`.
+- Официальный Python SDK `mcp` 2.3.0 (`ClientSession` + `stdio_client`) заработал после правки атрибутов: API v2 перешло на snake_case. Все 91 схема проходят `Draft202012Validator.check_schema`.
+- Главные риски: **размер результатов** (до 28–32k токенов на один вызов), отсутствие `additionalProperties:false` (лишние аргументы валидацию проходят) и device-flow текст вместо ошибки, если токена нет.
+
+## 1. Состояние сервера, тулы и токены
+
+Метод подсчёта токенов: `tiktoken` `o200k_base` по `json.dumps({name, description, input_schema})` для каждого тула, примерно в той форме, в какой тул уходит в `tools` API. Это приближение: у Anthropic другой токенизатор, и API добавляет свой оверхед на tool use. Для точной цифры в замере «до/после» нужен `count_tokens` того провайдера, с которым работает harness. Отдельно сервер отдаёт в `initialize` поле `instructions` на ≈1.6k токенов, и если harness кладёт его в system prompt, это тоже часть «до».
+
+| Конфигурация (local stdio, v2.2.0) | Тулов | read-only | Токены o200k | Символы |
+|---|---|---|---|---|
+| default (без `--toolsets`) | 46 | 27 | 13 381 | 51 852 |
+| default, только read-only тулы | 27 | 27 | 7 722 | — |
+| `--toolsets all` | **91** | 57 | **27 814** | 109 539 |
+| `--toolsets all --read-only` | 57 | 57 | 16 049 | 62 027 |
+| `--toolsets all --insiders` | 94 | 59 | 28 946 | 114 024 |
+| `--toolsets all --features <все 8 флагов>` | 134 | — | 36 372 | — |
+| remote `/mcp/readonly` | 29 | 29 | 8 261 | — |
+| remote `/mcp/x/all/readonly` | 75 | 75 | 19 407 | — |
+
+Default toolsets фактически такие: `context, copilot, issues, pull_requests, repos, users` (так пишет `--help`, и это совпадает с tools/list). Раздел README «default toolset» устарел: там нет `copilot`.
+
+Разбивка `--toolsets all` (91 тул) по toolsets, отсортировано по токенам:
+
+| toolset | тулов | read-only | токены | в default |
+|---|---|---|---|---|
+| repos | 19 | 13 | 4 702 | ✓ |
+| issues | 9 | 5 | 3 756 | ✓ |
+| pull_requests | 10 | 3 | 3 741 | ✓ |
+| governance | 4 | 2 | 3 057 | |
+| projects | 3 | 2 | 2 929 | |
+| actions | 4 | 3 | 1 656 | |
+| discussions | 5 | 4 | 1 158 | |
+| notifications | 6 | 2 | 1 028 | |
+| security_advisories | 4 | 4 | 867 | |
+| labels | 3 | 2 | 614 | ✓ (один label-тул есть в default) |
+| secret_protection | 2 | 2 | 484 | |
+| copilot_issue_intents | 1 | 0 | 468 | |
+| gists | 4 | 2 | 466 | |
+| code_security | 2 | 2 | 447 | |
+| context | 4 | 4 | 418 | ✓ |
+|
… [14629 more characters truncated]
````

<details><summary>reasoning</summary>

````
I'm checking the claim that every tool has a readOnlyHint matching --read-only: the readOnlyHint count of 57 matches the read-only config. I'm also checking whether all 91 tools have annotations, which looks roughly fine, and noting that the pycache cleanup is harmless. Nothing in the repo changed, so I'm ready to give the final answer.
````
</details>

**[agent]**

Ресерч и спайк сделаны. Каталог реально снят, read-only вызовы на публичных репо проходят через официальный SDK. В репо задания ничего не трогал.

**Выжимка (github-mcp-server v2.2.0 от 16.11.2026):**
- **Размер каталога:** `--toolsets all` даёт 91 тул, ≈27.8k токенов. По умолчанию 46 тулов (≈13.4k), с `--read-only` 57 тулов (≈16k), со всеми feature flags 134 (≈36.4k). Считал tiktoken o200k по `{name, description, input_schema}` каждого тула, это порядок величины. Точную цифру для замера «до/после» лучше снять `count_tokens` провайдера. Ещё ≈1.6k токенов сервер отдаёт в `instructions` при старте.
- **Какие toolsets включены по умолчанию:** context, copilot, issues, pull_requests, repos, users. Так пишет `--help` и так выходит по факту; в README список устарел, там нет copilot.
- **Своей подгрузки тулов по требованию у сервера больше нет.** `--dynamic-toolsets` удалили в v1.1.0 (PR #2512) как техдолг. Он включал toolset целиком через мета-тулы, без поиска и только в локальном режиме. Остались статические фильтры: toolsets, отдельные tools, `--read-only`, фильтр по scopes токена, lockdown. Для нашего отчёта это хороший тезис для сравнения.
- **Как достать каталог:** отдельной команды для JSON-дампа нет. Работает обычный `tools/list` по stdio, токен для него не нужен. Бинарь из релиза (30 MB, проверен checksum) лежит в scratch-папке.
- **Токен:** `gh auth token` подходит, это OAuth-токен со scopes `gist, read:org, repo, workflow`. Читается внутри процесса и передаётся серверу через env, нигде не печатается. Работает и локально, и с remote `api.githubcopilot.com/mcp/...`. Но у remote другой набор тулов: в `x/all/readonly` 75 тулов, 18 из них есть только там.
- **SDK:** официальный `mcp` 2.3.0 работает. API в v2 перешло на snake_case (`input_schema`, `is_error`), мой первый код по памяти на этом упал, так что версию надо пинить.
- **Схемы:** все проходят jsonschema Draft 2020-12, `$ref` нет. Но `additionalProperties:false` стоит только у 1 тула из 91, поэтому аргументы с опечатками проходят валидацию, и сервер их просто игнорирует.
- **Результаты бывают огромные:** `list_issues` с perPage=30 весит ≈28k токенов, файл `typing.py` ≈32k. Сам сервер ничего не обрезает, так что обрезка с явным маркером нужна обязательно.
- **Ловушка без токена:** сервер не падает, а возвращает текст device-flow «Visit github.com/login/device…» как успешный результат. Harness должен сразу падать, если токен не получен.
- **Мутации:** `--read-only` не регистрирует write-тулы вообще. Вызов `create_issue` в таком режиме приходит как JSON-RPC ошибка `unknown tool`, а не как `isError`.
- **Rate limits:** обычные запросы 5000/ч, search 30/мин, `search_code` всего 10/мин.

**Рекомендация, как подключать:** локальный бинарь v2.2.0 по stdio через официальный SDK `mcp>=2.3,<3` (`ClientSession` + `stdio_client`, stderr сервера направить в лог через `errlog=`).
- Рабочий каталог для демо: `stdio --toolsets all --read-only`.
- Для замера «до» можно дополнительно снять `--toolsets all` (91 тул) без вызовов и подписать, что это другой конфиг.
- Цикл в harness: `tool_search` по каталогу → `tool_call` → валидация `Draft202012Validator` → `call_tool` → склейка text- и resource-блоков → обрезка с маркером.

Свой тонкий JSON-RPC клиент тоже работает (≈30 строк), но с параллельными запросами, ping и elicitation разрастётся до 100–150 строк протокольного кода, который придётся защищать на ревью.

**Артефакты:**
- Отчёт: [github-mcp.md](<local path>)
- Каталог: [catalog.json](<local path>) (91 тул, к каждому добавлены toolset, read_only, in_default, tokens_o200k)
- Спайки и сырые дампы других конфигураций: в `reports/github-mcp/spike/` и `reports/github-mcp/raw/`

<details><summary>Почему в справочнике 147 тулов, а не 91</summary>

`list-scopes --toolsets=all --output json` показывает весь список тулов, не глядя на feature flags. Поэтому туда попадают отдельные `update_issue_*` и `update_pull_request_*` (вместо них по умолчанию работают общие `issue_write` и `pull_request_review_write`), copilot_automations и т.д. Реально видимый набор даёт только `tools/list`. Плюс `delete_repository` скрыт фильтром по scopes: ему нужен `delete_repo`, которого нет в токене.

</details>

<details><summary>Как выглядит ответ get_file_contents</summary>

Приходит два блока: text «successfully downloaded text file (SHA: …)» и embedded `resource` с uri `repo://owner/repo/sha/<sha>/contents/<path>`, mimeType и самим текстом файла в `resource.text`. Если взять только text-блоки, содержимое файла потеряется. `structuredContent` сервер отдаёт только на протоколе 2026-07-28, а SDK 2.3.0 договорился на 2025-11-25.

</details>
