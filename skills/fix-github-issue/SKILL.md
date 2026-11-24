---
name: fix-github-issue
description: Fix a bug reported in a GitHub issue and open a pull request for it. Use when the task references an issue number or URL and asks to fix, resolve, or implement it.
---

# Fix a GitHub issue

If the GitHub tools below are not in your tool list, find their schemas with `tool_search` and run them with `tool_call`.

1. Read the issue and its discussion: `issue_read` with `method: "get"`, then `method: "get_comments"`. Write down the expected and the actual behaviour in one line each.
2. Reproduce locally before changing code. Prefer a failing test next to the existing tests for that module; if the bug cannot be reproduced, stop and report what you tried instead of guessing a fix.
3. Make the smallest change that makes the test pass. Do not refactor unrelated code in the same PR.
4. Run the full test suite. A PR with failing tests is not done.
5. Branch `fix/<issue-number>-<short-slug>`, one commit with a conventional message (`fix: <what was wrong>`).
6. Open the PR with `create_pull_request`:
   - title: the commit message;
   - body: `Fixes #<issue-number>`, then the root cause in 1-2 sentences, then how it was verified (test name, command).
7. Answer with the PR URL and the root cause.
