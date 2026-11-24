"""Live backend for part of the GitHub example catalog: a read-only proxy to the user's `gh` CLI.

Each proxied tool turns its (already schema-validated) arguments into one `gh api` call: REST with
`--method GET`, or GraphQL with a query fixed in this module, so nothing here can mutate GitHub.
The arguments a mapping supports are its Python parameters; anything else the schema allows is reported
to the model as not implemented instead of being silently ignored. Other catalog tools answer with an error.
gh authenticates itself: the token never passes through this process."""
import asyncio, inspect, json, subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from urllib.parse import quote, urlencode

from .tools import Tool

type Argv = list[str]  # arguments after `gh`


@dataclass(frozen=True)
class Unsupported:
    reason: str


def _repo(owner: str, repo: str) -> str:
    return f"repos/{quote(owner, safe='')}/{quote(repo, safe='')}"


def _rest(path: str, query: dict[str, object], jq: str | None = None, accept: str | None = None) -> Argv:
    params = urlencode({k: v for k, v in query.items() if v is not None})
    argv = ["api", "--method", "GET", f"{path}?{params}" if params else path]
    if accept:
        argv += ["--header", f"Accept: {accept}"]
    return argv + ["--jq", jq] if jq else argv


def _pages(page: float | None, per_page: float | None) -> dict[str, object]:
    return {"page": None if page is None else int(page), "per_page": None if per_page is None else int(per_page)}


def _each(fields: list[str] | None) -> str | None:
    """jq that keeps only `fields` of every list element (field names come from schema enums)."""
    return None if fields is None else f"map({{{', '.join(fields)}}})"


def _items(fields: list[str] | None) -> str | None:
    return None if fields is None else f".items |= {_each(fields)}"


def get_file_contents(owner: str, repo: str, path: str = "/", ref: str | None = None, sha: str | None = None,
                      fields: list[str] | None = None) -> Argv:
    entry = "{" + ", ".join(fields) + "}" if fields else "."
    return _rest(f"{_repo(owner, repo)}/contents/{quote(path.strip('/'))}".rstrip("/"), {"ref": sha or ref},
                 jq=f'if type == "array" then map({entry}) elif .type == "file" then .content | @base64d else . end')


def get_repository_tree(owner: str, repo: str, tree_sha: str | None = None, recursive: bool = False,
                        path_filter: str | None = None) -> Argv:
    prefix = json.dumps(path_filter or "")  # a JSON string is a valid jq string literal: no jq injection
    return _rest(f"{_repo(owner, repo)}/git/trees/{quote(tree_sha or 'HEAD', safe='')}",
                 {"recursive": 1 if recursive else None},
                 jq=f"{{truncated, tree: [.tree[] | select(.path | startswith({prefix})) | {{path, type, size}}]}}")


def list_commits(owner: str, repo: str, sha: str | None = None, path: str | None = None, author: str | None = None,
                 since: str | None = None, until: str | None = None, page: float | None = None,
                 perPage: float | None = None, fields: list[str] | None = None) -> Argv:
    return _rest(f"{_repo(owner, repo)}/commits", {"sha": sha, "path": path, "author": author, "since": since,
                                                    "until": until, **_pages(page, perPage)}, jq=_each(fields))


_COMMIT_DETAIL = {"none": "del(.files, .stats)", "stats": ".files |= map(del(.patch))", "full_patch": None}


def get_commit(owner: str, repo: str, sha: str, detail: str = "stats", page: float | None = None,
               perPage: float | None = None) -> Argv:
    return _rest(f"{_repo(owner, repo)}/commits/{quote(sha, safe='')}", _pages(page, perPage),
                 jq=_COMMIT_DETAIL[detail])


_ISSUE_FIELDS = {"number": "number", "title": "title", "body": "body", "state": "state", "user": "author { login }",
                 "labels": "labels(first: 20) { nodes { name } }", "assignees": "assignees(first: 10) { nodes { login } }",
                 "comments": "comments { totalCount }", "created_at": "createdAt", "updated_at": "updatedAt"}
_LIST_ISSUES = """\
query($owner: String!, $repo: String!, $first: Int!, $after: String, $states: [IssueState!], $labels: [String!],
      $orderBy: IssueOrder, $since: DateTime) {
  repository(owner: $owner, name: $repo) {
    issues(first: $first, after: $after, states: $states, labels: $labels, orderBy: $orderBy,
           filterBy: {since: $since}) {
      totalCount pageInfo { hasNextPage endCursor } nodes { %s }
    }
  }
}"""


def list_issues(owner: str, repo: str, state: str | None = None, labels: list[str] | None = None,
                orderBy: str | None = None, direction: str | None = None, since: str | None = None,
                after: str | None = None, perPage: float | None = None,
                fields: list[str] | None = None) -> Argv | Unsupported:
    # GraphQL like the original server: REST would mix in pull requests and has no `after` cursor.
    if (orderBy is None) != (direction is None):
        return Unsupported("list_issues needs orderBy and direction together")
    if fields and "field_values" in fields:
        return Unsupported("field 'field_values' of list_issues is not implemented in the gh backend")
    selection = " ".join(_ISSUE_FIELDS[f] for f in fields or _ISSUE_FIELDS)
    # -f passes values verbatim; -F would read a file for a value starting with "@", so it gets only our integer.
    strings = [("owner", owner), ("repo", repo), ("after", after), ("since", since), ("states[]", state),
               ("orderBy[field]", orderBy), ("orderBy[direction]", direction),
               *(("labels[]", label) for label in labels or ())]
    return ["api", "graphql", "-f", f"query={_LIST_ISSUES % selection}", "-F", f"first={int(perPage or 30)}",
            *(arg for key, value in strings if value is not None for arg in ("-f", f"{key}={value}")),
            "--jq", ".data.repository.issues"]


_ISSUE_PATHS = {"get": "", "get_comments": "/comments", "get_sub_issues": "/sub_issues", "get_parent": "/parent",
                "get_labels": "/labels"}


def issue_read(method: str, owner: str, repo: str, issue_number: float, page: float | None = None,
               perPage: float | None = None) -> Argv:
    return _rest(f"{_repo(owner, repo)}/issues/{int(issue_number)}{_ISSUE_PATHS[method]}", _pages(page, perPage))


def _search_query(query: str, kind: str, owner: str | None, repo: str | None) -> str:
    return f"{query} {kind}" + (f" repo:{owner}/{repo}" if owner and repo else "")


def search_issues(query: str, owner: str | None = None, repo: str | None = None, sort: str | None = None,
                  order: str | None = None, page: float | None = None, perPage: float | None = None,
                  fields: list[str] | None = None) -> Argv:
    return _rest("search/issues", {"q": _search_query(query, "is:issue", owner, repo), "sort": sort, "order": order,
                                   **_pages(page, perPage)}, jq=_items(fields))


def search_pull_requests(query: str, owner: str | None = None, repo: str | None = None, sort: str | None = None,
                         order: str | None = None, page: float | None = None, perPage: float | None = None,
                         fields: list[str] | None = None) -> Argv:
    return _rest("search/issues", {"q": _search_query(query, "is:pr", owner, repo), "sort": sort, "order": order,
                                   **_pages(page, perPage)}, jq=_items(fields))


def list_pull_requests(owner: str, repo: str, state: str | None = None, head: str | None = None,
                       base: str | None = None, sort: str | None = None, direction: str | None = None,
                       page: float | None = None, perPage: float | None = None,
                       fields: list[str] | None = None) -> Argv:
    return _rest(f"{_repo(owner, repo)}/pulls", {"state": state, "head": head, "base": base, "sort": sort,
                                                  "direction": direction, **_pages(page, perPage)}, jq=_each(fields))


_PR_PATHS = {"get": "pulls/{n}", "get_diff": "pulls/{n}", "get_status": "commits/refs/pull/{n}/head/status",
             "get_files": "pulls/{n}/files", "get_commits": "pulls/{n}/commits",
             "get_review_comments": "pulls/{n}/comments", "get_reviews": "pulls/{n}/reviews",
             "get_comments": "issues/{n}/comments", "get_check_runs": "commits/refs/pull/{n}/head/check-runs"}


def pull_request_read(method: str, owner: str, repo: str, pullNumber: float, page: float | None = None,
                      perPage: float | None = None) -> Argv:
    return _rest(f"{_repo(owner, repo)}/{_PR_PATHS[method].format(n=int(pullNumber))}", _pages(page, perPage),
                 accept="application/vnd.github.diff" if method == "get_diff" else None)


def search_code(query: str, sort: str | None = None, order: str | None = None, page: float | None = None,
                perPage: float | None = None, fields: list[str] | None = None) -> Argv:
    return _rest("search/code", {"q": query, "sort": sort, "order": order, **_pages(page, perPage)},
                 jq=_items(fields), accept="application/vnd.github.text-match+json")


def search_repositories(query: str, sort: str | None = None, order: str | None = None, page: float | None = None,
                        perPage: float | None = None, minimal_output: bool = True) -> Argv:
    minimal = ".items |= map({full_name, description, html_url, language, stargazers_count, updated_at, topics})"
    return _rest("search/repositories", {"q": query, "sort": sort, "order": order, **_pages(page, perPage)},
                 jq=minimal if minimal_output else None)


def list_releases(owner: str, repo: str, page: float | None = None, perPage: float | None = None,
                  fields: list[str] | None = None) -> Argv:
    return _rest(f"{_repo(owner, repo)}/releases", _pages(page, perPage), jq=_each(fields))


def list_branches(owner: str, repo: str, page: float | None = None, perPage: float | None = None) -> Argv:
    return _rest(f"{_repo(owner, repo)}/branches", _pages(page, perPage))


_MAPPINGS: list[Callable[..., Argv | Unsupported]] = [
    get_file_contents, get_repository_tree, list_commits, get_commit, list_issues, issue_read, search_issues,
    list_pull_requests, pull_request_read, search_pull_requests, search_code, search_repositories, list_releases,
    list_branches]
PROXIED = {f.__name__: f for f in _MAPPINGS}


def gh_argv(name: str, args: dict) -> Argv | Unsupported:
    mapping = PROXIED.get(name)
    if mapping is None:
        return Unsupported(f"'{name}' is not implemented in the gh backend (a read-only proxy). "
                           f"Implemented tools: {', '.join(PROXIED)}.")
    if extra := sorted(set(args) - set(inspect.signature(mapping).parameters)):
        return Unsupported(f"argument(s) {', '.join(extra)} of '{name}' are not implemented in the gh backend; "
                           f"call it without them.")
    return mapping(**args)


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return (text[:limit] + f"\n[... truncated: showing {limit} of {len(text)} characters. Narrow the request: "
            f"`fields`, a smaller `perPage` with `page`, a lighter `detail`, or a more specific path/query ...]")


class GhUnavailable(Exception):
    pass


@dataclass(frozen=True)
class Gh:
    """Runs `gh` without stdin, with a timeout and bounded output. gh failures (404, rate limit, bad query)
    come back as text for the model; only a missing or logged-out gh is fatal, checked once by `check`."""
    executable: str = "gh"
    timeout: float = 30
    max_output: int = 20_000

    async def check(self) -> None:
        try:
            code, _, err = await self._exec(["auth", "status", "--hostname", "github.com"])
        except FileNotFoundError:
            raise GhUnavailable(
                f"'{self.executable}' not found: install the GitHub CLI (https://cli.github.com)") from None
        if code != 0:
            raise GhUnavailable(f"gh is not logged in to github.com (run `gh auth login`): {err.strip()}")

    async def run(self, argv: Argv) -> str:
        try:
            code, out, err = await self._exec(argv)
        except TimeoutError:
            return f"Error: gh timed out after {self.timeout:g}s"
        if code != 0:
            return truncate(f"Error: gh exited with code {code}: {err.strip()}\n{out}".rstrip(), self.max_output)
        return truncate(out, self.max_output)

    async def _exec(self, argv: Argv) -> tuple[int, str, str]:
        proc = await asyncio.create_subprocess_exec(self.executable, *argv, stdin=subprocess.DEVNULL,
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            out, err = await asyncio.wait_for(proc.communicate(), self.timeout)
        finally:
            if proc.returncode is None:  # timed out or cancelled
                proc.kill()
                await proc.wait()
        assert proc.returncode is not None
        return proc.returncode, out.decode(errors="replace"), err.decode(errors="replace")


@dataclass(frozen=True)
class GhTool:
    name: str
    description: str
    parameters: dict
    gh: Gh

    async def run(self, args: dict) -> str:
        argv = gh_argv(self.name, args)
        if isinstance(argv, Unsupported):
            return f"Error: {argv.reason}"
        return await self.gh.run(argv)


def gh_tools(specs: Sequence[Tool], gh: Gh) -> tuple[list[GhTool], str]:
    """Catalog tools backed by gh, plus a hint for tool_search about which of them actually work."""
    hint = f"Live gh backend: only these read-only tools are implemented: {', '.join(PROXIED)}."
    return [GhTool(t.name, t.description, t.parameters, gh) for t in specs], hint
