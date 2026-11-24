# Review checklist

- Does the change do what the PR description says, and nothing else?
- Are error paths handled where they can actually happen (I/O, network, user input), and not invented elsewhere?
- Is changed behaviour covered by a test that would fail without the change?
- Public API, CLI flags, config or data formats: backwards compatible, or the break is stated in the description?
- Secrets, tokens, or personal data in code, logs, or fixtures?
- Concurrency: shared state, missing awaits, resources not closed on error?
