---
name: ci-failure-triage
description: Find why a GitHub Actions run failed and fix it. Use when CI, a workflow run, a check, or a build is red, or when asked why tests fail on GitHub but not locally.
---

# Triage a failed CI run

If the GitHub tools below are not in your tool list, find their schemas with `tool_search` and run them with `tool_call`.

1. Find the failed run: `actions_list` with `method: "list_workflow_runs"`; take the newest run with conclusion `failure` on the branch in question.
2. Fetch only the failed jobs' logs: `get_job_logs` with `run_id`, `failed_only: true`, `return_content: true`, `tail_lines: 300`.
3. Save the logs to a file and run `scripts/first_error.sh <file>`: it prints the first error with context. The first error is the cause; later ones are usually fallout.
4. Classify before fixing:
   - code or test bug: reproduce locally with the same command the job ran, then fix;
   - environment difference (versions, missing service, secrets): compare the workflow file with the local setup and fix the workflow, not the code;
   - flaky (passes on re-run, timing-dependent): say so and do not "fix" it with retries or sleeps.
5. Answer with the failing step, the root cause, and the fix (or why no code change is needed).
