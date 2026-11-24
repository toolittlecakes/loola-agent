"""gh backend: argument -> `gh` argv mapping (no network), the runner against a fake gh, and live smoke tests."""
import inspect, json
from pathlib import Path

import pytest

from loola_agent import Toolbox, load_catalog
from loola_agent.gh_proxy import PROXIED, Gh, GhUnavailable, Unsupported, gh_argv, gh_tools

CATALOG = Path(__file__).parent.parent / "examples" / "github_tools.json"
SPECS = {t["name"]: t for t in json.loads(CATALOG.read_text())["tools"]}
GET = ["api", "--method", "GET"]


@pytest.mark.parametrize("name, args, argv", [
    ("get_file_contents", {"owner": "o", "repo": "r", "path": "/src/a b.py", "ref": "refs/heads/dev"},
     [*GET, "repos/o/r/contents/src/a%20b.py?ref=refs%2Fheads%2Fdev", "--jq",
      'if type == "array" then map(.) elif .type == "file" then .content | @base64d else . end']),
    ("get_file_contents", {"owner": "o", "repo": "r", "ref": "main", "sha": "abc", "fields": ["name", "type"]},
     [*GET, "repos/o/r/contents?ref=abc", "--jq",
      'if type == "array" then map({name, type}) elif .type == "file" then .content | @base64d else . end']),
    ("get_repository_tree", {"owner": "o", "repo": "r", "recursive": True, "path_filter": 'src/"x'},
     [*GET, "repos/o/r/git/trees/HEAD?recursive=1", "--jq",
      '{truncated, tree: [.tree[] | select(.path | startswith("src/\\"x")) | {path, type, size}]}']),
    ("list_commits", {"owner": "o", "repo": "r", "sha": "main", "perPage": 5, "page": 2, "fields": ["sha"]},
     [*GET, "repos/o/r/commits?sha=main&page=2&per_page=5", "--jq", "map({sha})"]),
    ("get_commit", {"owner": "o", "repo": "r", "sha": "abc"},
     [*GET, "repos/o/r/commits/abc", "--jq", ".files |= map(del(.patch))"]),
    ("get_commit", {"owner": "o", "repo": "r", "sha": "abc", "detail": "full_patch"}, [*GET, "repos/o/r/commits/abc"]),
    ("issue_read", {"method": "get_comments", "owner": "o", "repo": "r", "issue_number": 7, "perPage": 10},
     [*GET, "repos/o/r/issues/7/comments?per_page=10"]),
    ("issue_read", {"method": "get", "owner": "o", "repo": "r", "issue_number": 7.0}, [*GET, "repos/o/r/issues/7"]),
    ("search_issues", {"query": "memory leak", "owner": "o", "repo": "r", "sort": "updated"},
     [*GET, "search/issues?q=memory+leak+is%3Aissue+repo%3Ao%2Fr&sort=updated"]),
    ("search_pull_requests", {"query": "fix", "fields": ["number", "title"]},
     [*GET, "search/issues?q=fix+is%3Apr", "--jq", ".items |= map({number, title})"]),
    ("list_pull_requests", {"owner": "o", "repo": "r", "state": "closed", "base": "main"},
     [*GET, "repos/o/r/pulls?state=closed&base=main"]),
    ("pull_request_read", {"method": "get_diff", "owner": "o", "repo": "r", "pullNumber": 3},
     [*GET, "repos/o/r/pulls/3", "--header", "Accept: application/vnd.github.diff"]),
    ("pull_request_read", {"method": "get_check_runs", "owner": "o", "repo": "r", "pullNumber": 3},
     [*GET, "repos/o/r/commits/refs/pull/3/head/check-runs"]),
    ("pull_request_read", {"method": "get_comments", "owner": "o", "repo": "r", "pullNumber": 3},
     [*GET, "repos/o/r/issues/3/comments"]),
    ("search_code", {"query": "Client repo:o/r", "fields": ["path"]},
     [*GET, "search/code?q=Client+repo%3Ao%2Fr", "--header", "Accept: application/vnd.github.text-match+json",
      "--jq", ".items |= map({path})"]),
    ("search_repositories", {"query": "http client", "minimal_output": False}, [*GET, "search/repositories?q=http+client"]),
    ("list_releases", {"owner": "o", "repo": "r", "perPage": 3}, [*GET, "repos/o/r/releases?per_page=3"]),
    ("list_branches", {"owner": "../..", "repo": "r"}, [*GET, "repos/..%2F../r/branches"]),
])
def test_rest_mapping(name, args, argv):
    assert gh_argv(name, args) == argv


def test_list_issues_uses_graphql_with_schema_semantics():
    argv = gh_argv("list_issues", {"owner": "o", "repo": "r", "state": "OPEN", "labels": ["bug", "@x"],
                                   "orderBy": "CREATED_AT", "direction": "DESC", "after": "cur",
                                   "perPage": 5, "fields": ["number", "user"]})
    assert isinstance(argv, list) and argv[:3] == ["api", "graphql", "-f"]
    assert argv[3].startswith("query=query(") and "nodes { number author { login } }" in argv[3]
    assert argv[4:] == ["-F", "first=5", "-f", "owner=o", "-f", "repo=r", "-f", "after=cur", "-f", "states[]=OPEN",
                        "-f", "orderBy[field]=CREATED_AT", "-f", "orderBy[direction]=DESC",
                        "-f", "labels[]=bug", "-f", "labels[]=@x", "--jq", ".data.repository.issues"]


@pytest.mark.parametrize("name, args, reason", [
    ("create_branch", {"owner": "o", "repo": "r", "branch": "b"}, "'create_branch' is not implemented"),
    ("list_issues", {"owner": "o", "repo": "r", "field_filters": []}, "field_filters of 'list_issues' are not"),
    ("pull_request_read", {"method": "get_review_comments", "owner": "o", "repo": "r", "pullNumber": 1,
                           "after": "c"}, "after of 'pull_request_read'"),
    ("list_issues", {"owner": "o", "repo": "r", "orderBy": "CREATED_AT"}, "orderBy and direction together"),
    ("list_issues", {"owner": "o", "repo": "r", "fields": ["field_values"]}, "'field_values'"),
])
def test_unsupported_calls_are_explained_not_faked(name, args, reason):
    result = gh_argv(name, args)
    assert isinstance(result, Unsupported) and reason in result.reason


@pytest.mark.parametrize("name", PROXIED)
def test_proxied_tools_are_read_only_and_match_the_catalog_schema(name):
    spec, params = SPECS[name], inspect.signature(PROXIED[name]).parameters
    assert spec["read_only"]
    assert set(params) <= set(spec["parameters"]["properties"])  # no misspelled argument names
    assert {p for p, v in params.items() if v.default is inspect.Parameter.empty} == \
        set(spec["parameters"].get("required", []))


@pytest.mark.parametrize("name", PROXIED)
def test_every_proxied_call_is_a_get_or_a_graphql_query(name):
    schema = SPECS[name]["parameters"]
    props = schema["properties"]
    for method in props.get("method", {}).get("enum", [None]):
        args = {p: 1 if props[p]["type"] == "number" else "x" for p in schema["required"]} | \
            ({"method": method} if method else {})
        argv = gh_argv(name, args)
        assert isinstance(argv, list)
        assert argv[:3] == GET or (argv[:2] == ["api", "graphql"] and argv[3].startswith("query=query("))


def fake_gh(tmp_path, script: str) -> Gh:
    path = tmp_path / "gh"
    path.write_text(f"#!/bin/sh\n{script}\n")
    path.chmod(0o755)
    return Gh(executable=str(path), timeout=1, max_output=100)


async def test_gh_errors_go_back_to_the_model_as_text(tmp_path):
    gh = fake_gh(tmp_path, "echo '{\"message\": \"Not Found\"}'; echo 'gh: Not Found (HTTP 404)' >&2; exit 1")
    assert await gh.run(["api", "x"]) == 'Error: gh exited with code 1: gh: Not Found (HTTP 404)\n{"message": "Not Found"}'


async def test_gh_gets_exact_argv_and_no_stdin(tmp_path):
    gh = fake_gh(tmp_path, 'cat; printf "%s|" "$@"')
    assert await gh.run(["api", "a b", "--jq", "."]) == "api|a b|--jq|.|"


async def test_gh_timeout_is_an_infrastructure_failure(tmp_path):
    with pytest.raises(GhUnavailable, match="timed out"):
        await fake_gh(tmp_path, "sleep 5").run([])


@pytest.mark.parametrize("stderr", ["error connecting to api.github.com", "gh: Bad credentials (HTTP 401)",
                                    "gh: Server Error (HTTP 502)", "gh: API rate limit exceeded (HTTP 403)"])
async def test_infrastructure_failures_raise_instead_of_reaching_the_model(tmp_path, stderr):
    with pytest.raises(GhUnavailable, match="gh failed"):
        await fake_gh(tmp_path, f"echo '{stderr}' >&2; exit 1").run(["api", "x"])


async def test_huge_output_is_truncated_with_a_marker(tmp_path):
    output = await fake_gh(tmp_path, "seq 1 10000").run([])
    assert output.startswith("1\n2\n") and "truncated: showing 100 of 48894 characters" in output


async def test_check_fails_fast_when_gh_is_missing_or_logged_out(tmp_path):
    with pytest.raises(GhUnavailable, match="not found"):
        await Gh(executable=str(tmp_path / "nope")).check()
    with pytest.raises(GhUnavailable, match="not logged in"):
        await fake_gh(tmp_path, "echo 'You are not logged into any GitHub hosts' >&2; exit 1").check()


async def test_unimplemented_catalog_tool_returns_an_error_through_the_toolbox(tmp_path):
    tools, hint = gh_tools(load_catalog(CATALOG)[0], fake_gh(tmp_path, "echo should-not-run"))
    result = await Toolbox([], deferred=tools).call(
        "tool_call", json.dumps({"name": "merge_pull_request", "arguments": {"owner": "o", "repo": "r", "pullNumber": 1}}))
    assert result.startswith("Error: 'merge_pull_request' is not implemented in the gh backend")
    assert "list_issues" in hint


@pytest.mark.live
async def test_live_file_contents_and_issue_listing():
    gh = Gh()
    await gh.check()
    tools, _ = gh_tools(load_catalog(CATALOG)[0], gh)
    toolbox = Toolbox([], deferred=tools)

    async def call(name, arguments):
        return await toolbox.call("tool_call", json.dumps({"name": name, "arguments": arguments}))

    assert (await call("get_file_contents", {"owner": "octocat", "repo": "Hello-World", "path": "README"})) \
        .startswith("Hello World!")
    issues = json.loads(await call("list_issues", {"owner": "encode", "repo": "httpx", "state": "CLOSED",
                                                   "perPage": 2, "fields": ["number", "title"]}))
    assert len(issues["nodes"]) == 2 and issues["pageInfo"]["hasNextPage"]
    missing = await call("issue_read", {"method": "get", "owner": "octocat", "repo": "Hello-World",
                                        "issue_number": 999999999})
    assert missing.startswith("Error: gh exited with code 1") and "404" in missing
