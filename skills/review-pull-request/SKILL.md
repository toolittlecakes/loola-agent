---
name: review-pull-request
description: Review a GitHub pull request and leave line comments plus a verdict. Use when asked to review, check, or approve a PR.
---

# Review a pull request

If the GitHub tools below are not in your tool list, find their schemas with `tool_search` and run them with `tool_call`.

1. Read the PR description and the diff: `pull_request_read` with `method: "get"`, then `method: "get_diff"`. Check `method: "get_check_runs"`: if CI is red, say so first.
2. Go through `references/checklist.md` for every changed file. Report only real problems: a bug, a missing test for changed behaviour, a broken contract. Skip style nits that a linter would catch.
3. Leave comments as one review, not as separate comments:
   - `pull_request_review_write` with `method: "create"` (no `event`) opens a pending review;
   - `add_comment_to_pending_review` for each problem, `subjectType: "LINE"`, on the line of the new code (`side: "RIGHT"`), with what is wrong and a concrete fix;
   - `pull_request_review_write` with `method: "submit_pending"` and `event`: `REQUEST_CHANGES` if any comment is a bug, otherwise `APPROVE` or `COMMENT`.
4. Answer with the verdict and the list of problems by severity.
