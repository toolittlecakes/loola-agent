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
