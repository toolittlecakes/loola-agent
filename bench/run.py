"""Before/after benchmark: same harness, mechanisms off vs on, same enforced context window.

    uv run --env-file .env python bench/run.py

Runs every task x arm x repetition in parallel through the CLI, scores the final `ANSWER:` line against ground
truth captured once via `gh`, and prints a markdown table (raw results go to bench/results.json)."""
import asyncio, json, os, re, sys, time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
WINDOW = int(os.environ.get("BENCH_WINDOW", 96_000))
REPEATS, TIMEOUT = 2, 540
ONLY_TOOLS = "Use only the provided GitHub tools for GitHub data, not `gh`, `curl` or `git` in bash."
TASKS = {
    "changelog": "In the GitHub repo encode/httpx, find the 4 most recently merged pull requests (by merge time). "
                 "For each read its description and diff and write a short changelog entry. " + ONLY_TOOLS +
                 " End with one line: `ANSWER: #<n>, #<n>, #<n>, #<n>` (the 4 PR numbers).",
    "hot-files": "In the GitHub repo encode/httpx, look at every commit between the release tags 0.27.2 and 0.28.0 "
                 "and find the 3 files changed in the most commits. " + ONLY_TOOLS +
                 " End with one line: `ANSWER: <path>, <path>, <path>`.",
}
ARMS = {
    "before": ["--catalog-mode", "direct", "--skills-mode", "eager", "--no-compaction"],
    "after": ["--catalog-mode", "deferred", "--skills-mode", "lazy"],
}


async def gh(*args: str) -> object:
    proc = await asyncio.create_subprocess_exec("gh", "api", *args, stdout=asyncio.subprocess.PIPE)
    out, _ = await proc.communicate()
    assert proc.returncode == 0, args
    return json.loads(out)


async def ground_truth() -> dict:
    pulls = await gh("repos/encode/httpx/pulls?state=closed&per_page=50")
    merged = sorted((p for p in pulls if p["merged_at"]), key=lambda p: p["merged_at"], reverse=True)[:4]
    compare = await gh("repos/encode/httpx/compare/0.27.2...0.28.0")
    commits = await asyncio.gather(*(gh(f"repos/encode/httpx/commits/{c['sha']}") for c in compare["commits"]))
    counts = Counter(f["filename"] for c in commits for f in c["files"])
    third = sorted(counts.values(), reverse=True)[2]
    return {"changelog": {f"#{p['number']}" for p in merged},
            "hot-files": {path for path, n in counts.items() if n >= third}, "counts": counts.most_common(6)}


def score(task: str, answer: str, truth: dict) -> bool:
    line = next((l for l in reversed(answer.splitlines()) if l.strip().startswith("ANSWER:")), "")
    items = {i.strip(" `") for i in line.split(":", 1)[-1].split(",") if i.strip(" `")}
    if task == "changelog":
        return items == truth["changelog"]
    return len(items) == 3 and items <= truth["hot-files"]  # ties at the third place are all accepted


async def run(task: str, arm: str, rep: int, out_dir: Path) -> dict:
    transcript = out_dir / f"{task}-{arm}-{rep}.jsonl"
    env = {**os.environ, "LLM_CONTEXT_WINDOW": str(WINDOW)}
    cmd = ["uv", "run", "--project", str(ROOT), "loola-agent", "--catalog", str(ROOT / "examples/github_tools.json"),
           "--catalog-backend", "gh", "--skills", str(ROOT / "skills"), "--transcript", str(transcript),
           *ARMS[arm], TASKS[task]]
    started = time.monotonic()
    proc = await asyncio.create_subprocess_exec(*cmd, env=env, cwd="/tmp", stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    try:
        out, err = await asyncio.wait_for(proc.communicate(), TIMEOUT)
        error = "" if proc.returncode == 0 else err.decode().strip().splitlines()[-1][:160]
    except TimeoutError:
        proc.kill()
        out, error = b"", f"timeout after {TIMEOUT}s"
    events = [json.loads(l) for l in transcript.read_text().splitlines()] if transcript.exists() else []
    paid = [e["usage"] for e in events if e["type"] in ("AssistantMessage", "Compaction", "SummaryDiscarded")]
    return {"task": task, "arm": arm, "rep": rep, "answer": out.decode(), "error": error,
            "seconds": round(time.monotonic() - started),
            "turns": sum(e["type"] == "AssistantMessage" for e in events),
            "tool_calls": sum(e["type"] == "ToolStarted" for e in events),
            "bash_calls": sum(e["type"] == "ToolStarted" and e["name"] == "bash" for e in events),
            "compactions": sum(e["type"] == "Compaction" for e in events),
            "prompt": sum(u["prompt"] for u in paid), "cached": sum(u["cached"] or 0 for u in paid),
            "completion": sum(u["completion"] for u in paid)}


async def main() -> None:
    out_dir = ROOT / "bench" / "runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    truth = await ground_truth()
    print(f"ground truth: {sorted(truth['changelog'])}; hot files: {truth['counts']}", file=sys.stderr)
    results = await asyncio.gather(*(run(t, a, r, out_dir) for t in TASKS for a in ARMS for r in range(1, REPEATS + 1)))
    for r in results:
        r["success"] = not r["error"] and score(r["task"], r["answer"], truth)
    (ROOT / "bench" / "results.json").write_text(json.dumps(results, indent=1))
    print("| task | arm | run | success | turns | tool calls (bash) | compactions | prompt | cached | completion | s | error |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        print(f"| {r['task']} | {r['arm']} | {r['rep']} | {'✅' if r['success'] else '❌'} | {r['turns']} | "
              f"{r['tool_calls']} ({r['bash_calls']}) | {r['compactions']} | {r['prompt']} | {r['cached']} | "
              f"{r['completion']} | {r['seconds']} | {r['error']} |")


asyncio.run(main())
