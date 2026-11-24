# AGENTS.md

Instructions for coding agents working on this repo. The development session that produced it is in [docs/session-log.md](docs/session-log.md).

## What this is

A minimalist showcase, not a product: an async coding-agent SDK over OpenAI-compatible `/v1/chat/completions` with deferred tools, lazy skills and context compaction. Readability in minutes beats completeness. See [README.md](README.md) for the design and the decisions behind it.

## Rules

- **One explicit path, fail fast.** No fallback branches, degraded modes, spare parsers or silent retries. Model mistakes (bad arguments, unknown tool, non-zero exit) go back to the model as tool results; infrastructure failures and harness bugs raise and end the run at the CLI boundary.
- **Keep the prompt prefix stable.** The declared tool list and the system prompt never change during a session. New context only goes to the tail (tool results, user messages); compaction is the only deliberate prefix change.
- **The session is an append-only event list** (`events.py`); the LLM context is a pure projection (`build_context`). Add behaviour as new event types or projection rules, not as mutable state.
- **No frameworks, no `openai` SDK**: `httpx` and the wire format stay visible.
- **Out of scope** unless the owner asks: MCP client, strict/guided decoding, Responses API, streaming, session resume, sandbox/approvals, TUI/web shells.
- Do not add features or abstractions "just in case"; prefer deleting code.

## Workflow

- Python 3.13 + `uv`. Run `uv run pytest -q` (deterministic: fake LLM, fake `gh`, no network) before committing; `uv run pytest -m live` hits real GitHub through `gh`.
- Bug fixes come with a regression test; check that the test fails without the fix.
- Conventional commits in English, focused on why.
- Live runs need `.env` (see `.env.example`); never print or commit secrets.
- Benchmark: `uv run --env-file .env python bench/run.py` (before/after arms, same enforced window).
