#!/usr/bin/env python3
# generated from system: edit there
"""Merge check, run by the PreToolUse hook on the shell tools (Bash, PowerShell) and a connector's merge tool.

The merge rules (global instructions, Safety; decision 0033 in `system`) rested on each chat remembering them, and
GitHub's free plan has no branch protection or rulesets for a private repository, so nothing on GitHub can stop a merge.
This hook stops it in the chat: it reads the pull request from GitHub and refuses (exit 2, the reason on stderr, which
Claude reads as the denial) a `gh pr merge` when:
  - it names `--admin` (a bypass of the checks) or `--auto` (a later merge could land a head the review did not pass);
  - GitHub's checks on the head failed or are still running, or the head holds a workflow and no check has started,
    unless the text holds a line `Local checks: PASS <head>`, which stands in when GitHub starts no run
    (`handing-off-work` step 6 e; a repository with no workflow has no checks here, and passes);
  - no line in the pull request's text names its current head in this form (a moved head needs a new line):
    `Review: <reviewer|sceptic> round <1|2> head <sha>: <n> high, <n> medium, <n> low; follow-up <task id>`
    (the follow-up part only when a finding is left), or a line of that kind leaves a high; round 1 leaves a medium
    (round 1's findings are fixed; a low may go to the follow-up at once, a chosen reading: no second round for a low
    alone); or a finding below high is left with no follow-up task. At most two rounds, so a third is not a form it
    reads: a high left after round 2 goes to the owner, and the change does not merge;
  - the change is risky by what a tool can read, and no such line says `sceptic`: a protected file (the commit check's
    lists, by the kind in the identity file on the base branch), a file deleted outside `working-files/` (a close-out
    removes its working file), or a repository that may publish a live site (GitHub Pages is on, or its identity file
    says `kind: product`). Secrets, money and any other risk only the chat can judge;
  - it is larger than the limit below, on a branch that does not deliver copies (`chore/sync-*`, `chore/mirror-*`),
    with no line `Large-pull-request: <why it cannot be split>`. One piece each is the chat's and the reviewer's
    judgement; the size is what a tool can read;
  - a commit that is not git's own merge and that changes a protected file left in the pull request has no
    `Owner-yes:` line, unless it says `Made-by: owner` (the merger's check of the Reviewed Agent Merge rule, and the
    commit check's net for a commit made without the commit-msg hook; task S226);
  - outside `system`, off a sync branch (`chore/sync-*`), such a commit adds or changes a component item (the same
    net: every component item is built only in `system`).
Another tool's merge (`gh api`, a connector) and a `gh pr merge` named by any command but `gh` and the text commands
below, or inside `$( )`, backticks or `( )`, are refused outright, since this check cannot read them: use a plain
`gh pr merge`. So is a merge in one command with `git push`, `gh pr edit` or `gh pr checks`: the check reads
the pull request before any part runs, so it would judge the state before them. A merge it lets through prints, as context for the chat, any
added line with the words "pending", "not yet" or "TODO" (the final audit's words left, by script instead of AI): it
passes, since such a word can be right.

GAP: these lines are typed by the agent they limit, and nothing here proves them. `Review:` says a review ran, and
`Local checks:` says they passed and lifts any failure, a real one too, since the rollup does not show that a run never
started. They stop a chat that forgot, not one that lies; the Auto mode rule on the merge reads the chat as a second net.
GAP: routes this hook does not see: Codex, which runs no Claude Code hook (task S224); a chat outside any repository's
folder, which loads no project hook; a person's own terminal, which stays his; a merge in a script file, through a
shell variable or a `git` alias; a line ending in a comment and a backslash; PowerShell's backtick continuation; a push
to `main` (a settings ask, and the branch check). A `gh` that fails on a cloud session's missing
sign-in refuses the merge, which then waits for a laptop session (`handing-off-work` step 6).

It fails closed on a merge: when it cannot read the command or GitHub, or meets any error of its own while the input
speaks of a merge, it refuses, since a check that cannot run does not pass. It keeps its calls within a total deadline
below the settings entry's timeout. On anything else it does nothing. The settings entry passes when the hook file is
missing (a branch made before the delivery) and says so on stderr only, with no `systemMessage` as the component
router's has, so a chat may not show it (on the follow-up list); merge `origin/main`
into the branch, which brings the file. GAP: a missing `python3` passes too, as for every hook here.
Standard library only, plus the commit check (its lists, one home).
"""
import sys

# Most shell calls name no merge: they leave here, before the imports below, which cost most of the hook's time.
RAW = None
if __name__ == "__main__":
    RAW = sys.stdin.buffer.read().decode("utf-8", "replace")
    if "merge" not in RAW.lower():
        sys.exit(0)

import fnmatch
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import time

MAX_LINES = 1000
MAX_FILES = 40
SYNC_BRANCH = "chore/sync-"
COPY_BRANCHES = (SYNC_BRANCH, "chore/mirror-")
DEADLINE_SECONDS = 150  # below the settings entry's timeout of 180
STARTED = time.monotonic()
API_MERGE = r"/merges?\b|mergePullRequest|enablePullRequestAutoMerge|mergeBranch"
MENTION = re.compile(r"\bgh(\.exe)?\b[^\n]*\b(pr\b[^\n]*\bmerge\b|api\b[^\n]*(" + API_MERGE + "))", re.I)
# Words that run the next word as a command: `gh` after them is still at command position.
PREFIXES = {"env", "timeout", "command", "nohup", "time", "sudo", "exec", "then", "do", "else", "if", "elif", "while",
            "until", "{", "!"}
# Commands that only read or print text, so a merge named in their words is no merge. Any other command naming one is
# refused as a form this check cannot read (`nice`, `winpty`, `bash -c`, `( ... )`, `case`).
TEXT_COMMANDS = {"echo", "printf", "grep", "egrep", "rg", "cat", "git", "head", "tail", "wc", "sed", "awk", "less", "more",
                 "sort", "uniq", "cut", "diff", "ls", "findstr", "select-string", "write-output", "write-host",
                 "get-content"}
# What makes `gh api` write; with none it reads, so `gh api repos/o/r/pulls/7/merge` (was it merged?) is no merge.
API_WRITES = {"-X", "--method", "-f", "--raw-field", "-F", "--field", "--input"}
SUBSTITUTED = re.compile(r"(\$\(|`)\s*\S*\bgh(\.exe)?\b", re.I)
CONTINUED = re.compile(r"(?<!\\)(\\\\)*\\$")
HERE_DOC = re.compile(r"<<-?\s*(?:'([^']+)'|\"([^\"]+)\"|\\?([^\s;&|<>()'\"]+))")
# The flags of `gh pr merge` that take a value, so the value is never read as the pull request.
VALUE_FLAGS = {"-A", "--author-email", "-b", "--body", "-F", "--body-file", "--match-head-commit", "-t", "--subject"}
REVIEW = re.compile(r"^Review: (reviewer|sceptic) round ([12]) head ([0-9a-f]{7,40}): (\d+) high, (\d+) medium, "
                    r"(\d+) low(?:; follow-up ([A-Z]+\d+))?[ \t\r]*$", re.M)
LARGE = re.compile(r"^Large-pull-request: \S.*$", re.M)
OWNER_COMMIT = re.compile(r"^Made-by: owner\b", re.M)
LOCAL_CHECKS = re.compile(r"^Local checks: PASS ([0-9a-f]{7,40})\b", re.M)
WORDS_LEFT = re.compile(r"\b(pending|not yet|TODO)\b", re.I)
FORM = ("`Review: <reviewer|sceptic> round <1|2> head <head>: <n> high, <n> medium, <n> low; follow-up <task id>`, with "
        "the follow-up only when a finding is left. Copy the numbers from the review's `Findings:` line; a line with no "
        "review behind it is a false record.")
REVIEW_HOW = ("Run the review (the global instructions, Safety: one `reviewer` subagent on a saved diff, or the sceptic "
              "instead for a risky change, at most two rounds), fix round 1's findings, then put this line in the pull "
              "request's text (`gh pr edit <number> --body-file <file>`, with the whole text in the file): ")
NEW_PULL = ("A later commit cannot clear it, since every commit is read and history is not rewritten. Open a new branch "
            "from `origin/main`, with one commit of the net change that carries what is missing, open its pull request, "
            "and close this one with `gh pr close <number> --comment` naming the new one.")


class Unreadable(Exception):
    """GitHub or the command could not be read, so a merge is refused."""


def refuse(lines):
    """Stop the merge: each reason on its own line."""
    print("merge check: this merge is refused.\n- " + "\n- ".join(lines) + "\nWhen the owner decides this merge goes as "
          "it is, it is his own click on GitHub's merge button on the pull request's page: tell him in one line and "
          "stop. An agent has no other route. Doing what this names and merging again is not a retry.\nFAIL", file=sys.stderr)
    return 2


def here_doc(line):
    """The stop word of a here-document this line opens, or None. A `<<` in quotes and a here-string `<<<` open none; a
    `"$(cat <<'EOF'` does, since `$(` starts a new command inside the quotes."""
    stack, index = [], 0
    while index < len(line):
        char, top = line[index], stack[-1] if stack else ""
        if top == "'":
            if char == "'":
                stack.pop()
        elif char == "\\":
            index += 1
        elif line.startswith("$(", index):
            stack.append("(")
            index += 1
        elif char == ")" and top == "(":
            stack.pop()
        elif char == '"' and top == '"':
            stack.pop()
        elif char == '"':
            stack.append('"')
        elif top != '"':
            if char == "'":
                stack.append("'")
            elif line.startswith("<<<", index):
                index += 2
            elif line.startswith("<<", index):
                found = HERE_DOC.match(line, index)
                if found:
                    return found.group(1) or found.group(2) or found.group(3)
        index += 1
    return None


def plain(text):
    """The shell text without what never runs: the bodies of here-documents and comment lines dropped, continued lines
    joined. A here-document left open that hid a merge is Unreadable, since the misread may be this reader's."""
    out, stop, hidden, lines, index = [], None, False, text.split("\n"), 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if stop:
            stop = None if line.strip() == stop else stop
            hidden = (hidden or bool(MENTION.search(line))) if stop else False
            continue
        if line.lstrip().startswith("#"):  # a comment does not continue on the next line, even ending in a backslash
            continue
        while CONTINUED.search(line.rstrip("\r")) and index < len(lines):  # an odd count: `\\` at the end is no join
            line = line.rstrip("\r")[:-1] + " " + lines[index]
            index += 1
        stop = here_doc(line)
        out.append(line)
    if stop and hidden:
        raise Unreadable("a here-document that never closes hides a merge")
    return "\n".join(out)


def commands(text):
    """The shell text as (segments, readable), each segment a list of words, split at `;`, `&`, `|` and new lines."""
    lexer = shlex.shlex(text, posix=True, punctuation_chars=";&|\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    segments = [[]]
    try:
        for word in lexer:
            if word and set(word) <= set(";&|\n"):
                segments.append([])
            else:
                segments[-1].append(word)
    except ValueError:
        return [], False
    return [one for one in segments if one], True


def program(word):
    """A word as the bare name of a program: no folder, no `$(` or `(`, no `.exe`, in lower case."""
    return re.sub(r"\.exe$", "", word.lstrip("$(`").replace("\\", "/").rsplit("/", 1)[-1].lower())


def command_at(words):
    """The index of the segment's command: past assignments, the prefix words and their flags and numbers."""
    for index, word in enumerate(words):
        if re.fullmatch(r"\w+=.*", word) or program(word) in PREFIXES or word.startswith("-") \
                or re.fullmatch(r"\d+[smhd]?", word):
            continue
        return index
    return len(words)


def read_merge(rest):
    """What the words after `gh` ask, as a dict, or None when they are no merge. `kind` is `merge`, `api` (another
    route) or `pass` (`--help`, `--disable-auto`: not a merge)."""
    positional, flags, repo, index = [], [], None, 0
    while index < len(rest):
        item = rest[index]
        attached = re.fullmatch(r"-[dmrs]*R=?(.*)", item)
        if item == "--repo" or attached:
            if attached and attached.group(1):
                repo = attached.group(1)
            else:
                repo = rest[index + 1] if index + 1 < len(rest) else None
                index += 1
        elif item.startswith("--repo="):
            repo = item.partition("=")[2]
        elif item in VALUE_FLAGS:
            index += 1
        elif re.fullmatch(r"\d*(>>?|<)", item):  # a redirection, never the pull request
            index += 1
        elif re.match(r"\d*[<>]", item):
            pass
        elif item.startswith("-"):
            flags.append(item.partition("=")[0])
        else:
            positional.append(item)
        index += 1
    if positional[:1] == ["api"] and any(re.search(API_MERGE, item) for item in rest):
        reads = positional[1:2] != ["graphql"] and not any(flag.startswith(("-X", "-f", "-F")) or flag in API_WRITES for flag in flags)
        return {"kind": "pass" if reads else "api"}
    if positional[:2] != ["pr", "merge"]:
        return None
    if "--help" in flags or "-h" in flags or "--disable-auto" in flags:
        return {"kind": "pass"}
    return {"kind": "merge", "target": positional[2] if len(positional) > 2 else None, "repo": repo,
            "admin": "--admin" in flags, "auto": "--auto" in flags}


def followed(cwd, raw):
    """The folder after a `cd` to raw, the Git Bash form of a Windows drive turned into the drive."""
    if os.name == "nt":
        found = re.match(r"^/([a-zA-Z])(?=/|$)", raw)
        if found:
            raw = found.group(1) + ":" + (raw[found.end():] or "/")
    return os.path.join(cwd, raw)


def merges_in(text, cwd):
    """Each merge asked for in the shell text, with the folder it runs in and the repository named by `GH_REPO`."""
    clean = re.sub(r"\d*>&(\d+|-)", " ", plain(text))  # `2>&1`: a redirection, whose `&` is no end of a command
    segments, readable = commands(clean)
    if not readable:
        if MENTION.search(clean):
            raise Unreadable("the shell text could not be read as words (an unbalanced quote)")
        return []
    found, named, moves = [], None, False
    for words in segments:
        named = next((word.partition("=")[2] for word in words if word.startswith("GH_REPO=")), named)
        at = command_at(words)
        first = words[at] if at < len(words) else ""
        name = program(first)
        moves = moves or (name == "git" and "push" in words[at + 1:at + 4]) \
            or (name == "gh" and words[at + 1:at + 2] == ["pr"] and any(one in ("edit", "checks") for one in words[at + 2:at + 3]))
        mentioned = MENTION.search(" ".join(words))
        if mentioned and (first.startswith("(") or any(SUBSTITUTED.search(word) for word in words)):
            found.append({"kind": "wrapped"})
        elif name in ("cd", "pushd") and at + 1 < len(words):
            cwd = followed(cwd, words[at + 1])
        elif name == "gh":
            asked = read_merge(words[at + 1:])
            if asked and asked["kind"] == "merge":
                asked["repo"] = asked["repo"] or named
                asked["cwd"] = cwd
            if asked:
                found.append(asked)
        elif mentioned and name not in TEXT_COMMANDS:
            found.append({"kind": "wrapped"})
    if moves and any(asked["kind"] == "merge" for asked in found):
        return [{"kind": "chained"}]
    return found


def gh(args, cwd):
    """The text `gh` prints for these arguments; Unreadable when it fails or the total deadline has passed."""
    tool = shutil.which("gh")
    if not tool:
        raise Unreadable("the GitHub CLI `gh` is not on the path")
    left = DEADLINE_SECONDS - (time.monotonic() - STARTED)
    if left <= 0:
        raise Unreadable(f"GitHub did not answer within {DEADLINE_SECONDS} seconds")
    try:
        done = subprocess.run([tool] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=left)
    except (OSError, subprocess.SubprocessError) as error:
        raise Unreadable(f"`gh {args[0]} {args[1]}` could not run in {cwd}: {error}")
    if done.returncode != 0:
        raise Unreadable(f"`gh {' '.join(args[:3])}` failed: {(done.stderr or '').strip()[:300]}")
    return done.stdout


def gh_or_none(args, cwd):
    """`gh`'s text, or None when GitHub says the thing is not there (HTTP 404); any other failure is Unreadable."""
    try:
        return gh(args, cwd)
    except Unreadable as error:
        if "HTTP 404" in str(error):
            return None
        raise


def gh_lines(args, cwd):
    """`gh`'s output read as one JSON value per line."""
    try:
        return [json.loads(line) for line in gh(args, cwd).split("\n") if line.strip()]
    except ValueError as error:
        raise Unreadable(f"`gh {' '.join(args[:3])}` printed something that is not JSON: {error}")


def read_facts(asked):
    """The pull request's facts from GitHub, by the command's own target."""
    cwd = asked["cwd"]
    if not os.path.isdir(cwd):
        raise Unreadable(f"the folder {cwd} could not be found: run the merge from the repository's checkout, as a "
                         "command of its own")
    view = ["pr", "view"] + ([asked["target"]] if asked["target"] else []) + (
        ["--repo", asked["repo"]] if asked["repo"] else [])
    try:
        pr = json.loads(gh(view + ["--json", "number,url,body,headRefOid,headRefName,baseRefName,additions,deletions,"
                                   "changedFiles,statusCheckRollup"], cwd))
    except ValueError as error:
        raise Unreadable(f"`gh pr view` printed something that is not JSON: {error}")
    found = re.search(r"github\.com/([^/]+/[^/]+)/pull/", pr.get("url", ""))
    if not found:
        raise Unreadable("the pull request's address could not be read")
    repo, number = found.group(1), pr["number"]
    files = gh_lines(["api", "--paginate", f"repos/{repo}/pulls/{number}/files", "--jq",
                      ".[] | {filename, status, previous_filename, patch}"], cwd)
    commits = gh_lines(["api", "--paginate", f"repos/{repo}/pulls/{number}/commits", "--jq",
                        ".[] | {sha, message: .commit.message, parents: (.parents | length)}"], cwd)
    identity = gh_or_none(["api", f"repos/{repo}/contents/.agents/repository.yml?ref={pr['baseRefName']}", "-H",
                           "Accept: application/vnd.github.raw"], cwd) or ""
    kinds = [line.split("#")[0].partition(":")[2].strip() for line in identity.splitlines()
             if line.split("#")[0].partition(":")[0].strip() == "kind"]
    return {"pr": pr, "repo": repo, "files": files, "commits": commits, "kind": kinds[0] if kinds else ""}


def has_pages(repo, cwd):
    """True when GitHub Pages is on for the repository. The API says HTTP 404 when it is off, on private repositories on
    the free plan too (read 6 November 2026 on one private repository of each kind); any other failure refuses the
    merge."""
    return gh_or_none(["api", f"repos/{repo}/pages"], cwd) is not None


def has_workflow(repo, head, cwd):
    """True when the head holds a GitHub workflow, so checks are due."""
    return gh_or_none(["api", f"repos/{repo}/contents/.github/workflows?ref={head}"], cwd) is not None


def commit_check():
    """The commit check: `scripts/` of this repository when delivered, its element folder in the library; one home for
    the protected and component lists."""
    here = os.path.dirname(os.path.abspath(__file__))
    for path in (os.path.join(here, "..", "..", "scripts", "check_commit_message.py"),
                 os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", here), "scripts", "check_commit_message.py"),
                 os.path.join(here, "..", "..", "checks", "check-commit-message", "check_commit_message.py")):
        if os.path.isfile(path):
            spec = importlib.util.spec_from_file_location("check_commit_message", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise Unreadable("the commit check scripts/check_commit_message.py is missing, and it holds the protected lists")


def protected_paths(paths, kind, check):
    """The protected ones among the paths, by the repository's kind, letter case ignored (the commit check's rule)."""
    patterns = [one.lower() for one in (check.HUB if kind in ("workspace", "system") else check.EVERYWHERE)]
    return [path for path in paths if any(fnmatch.fnmatchcase(path.lower(), one) for one in patterns)]


def checks_refused(facts, cwd):
    """GitHub's checks on the head, when any failed or is still running, or none has started where a workflow is due,
    and the local checks do not stand in."""
    pr = facts["pr"]
    stand_in = ("When GitHub started no run, `python scripts/check_local.py` in the branch stands in (`handing-off-work` "
                "step 6 e): put its last line, `Local checks: PASS <head>`, in the pull request's text.")
    if any(pr["headRefOid"].startswith(line) for line in LOCAL_CHECKS.findall(pr.get("body") or "")):
        return []
    runs = pr.get("statusCheckRollup") or []
    if not runs:
        if has_workflow(facts["repo"], pr["headRefOid"], cwd):
            return ["no check has started on the head, and it holds a workflow. Wait with `gh pr checks <number> "
                    "--watch`. " + stand_in]
        return []
    bad = []
    for run in runs:
        state = (run.get("conclusion") or run.get("state") or run.get("status") or "").upper()
        if state not in ("SUCCESS", "SKIPPED", "NEUTRAL"):
            bad.append(f"{run.get('name') or run.get('context') or 'a check'} ({state or 'not finished'})")
    return [f"GitHub's checks on the head have not passed: {', '.join(bad)}. Wait for them, or fix the failure. "
            + stand_in] if bad else []


def review_refused(pr, risky):
    """The review the pull request's text carries for its current head."""
    head = pr["headRefOid"]
    lines = [one for one in REVIEW.finditer(pr.get("body") or "") if head.startswith(one.group(3))]
    if not lines:
        return [f"its text has no `Review:` line naming its current head {head[:7]}. " + REVIEW_HOW
                + FORM]
    reasons = []
    for line in lines:
        kind, round_, high, medium, low, follow = line.group(1), line.group(2), int(line.group(4)), \
            int(line.group(5)), int(line.group(6)), line.group(7)
        if high:
            reasons.append(f"the {kind}'s round {round_} left {high} high. "
                           + ("Fix it, then run round 2 on the fixes." if round_ == "1" else
                              "After round 2 a high goes to the owner and the change does not merge: stop, and tell "
                              "him in one line what it is."))
        if medium and round_ == "1":
            reasons.append(f"the {kind}'s round 1 left {medium} medium. Round 1's findings are fixed; then round 2 "
                           "checks the fixes on the new head.")
        if (medium or low) and not follow:
            reasons.append(f"the {kind}'s round {round_} leaves {medium} medium and {low} low with no follow-up task: "
                           "add one task row and name it, `; follow-up <task id>`.")
    if risky and not any(line.group(1) == "sceptic" for line in lines):
        reasons.append("this is a risky change (" + "; ".join(risky) + "), so its review is the sceptic (the strongest "
                       "case against), and no line says `sceptic`. " + REVIEW_HOW + FORM)
    return reasons


def commit_files(repo, sha, cwd):
    """The paths one commit touches, a renamed file under both names."""
    paths = []
    for item in gh_lines(["api", "--paginate", f"repos/{repo}/commits/{sha}", "--jq",
                          ".files[] | {filename, previous_filename}"], cwd):
        paths += [path for path in (item.get("filename"), item.get("previous_filename")) if path]
    return paths


def commits_refused(facts, cwd, check):
    """The commit check's two nets, read on each commit: for a commit made without the hook (task S226)."""
    in_pr = {path for item in facts["files"] for path in (item.get("filename"), item.get("previous_filename")) if path}
    guarded = set(protected_paths(sorted(in_pr), facts["kind"], check))
    system = facts["kind"] == "system"
    sync = facts["pr"]["headRefName"].startswith(SYNC_BRANCH)
    changed = {item["filename"] for item in facts["files"] if item.get("status") != "removed"}
    items = set() if system or sync else set(check.component_items(sorted(changed)))
    if not guarded and not items:
        return []
    reasons = []
    for commit in facts["commits"]:
        message = commit.get("message") or ""
        if commit.get("parents", 1) > 1 or OWNER_COMMIT.search(message):
            continue
        touched = set(commit_files(facts["repo"], commit["sha"], cwd))
        missing = sorted(touched & guarded)
        if missing and not check.OWNER_YES.search(message):
            reasons.append(f"commit {commit['sha'][:7]} changes a protected file ({', '.join(missing)}) with no "
                           "`Owner-yes:` line (a clean `git revert`, a web edit or a hand commit is made without the "
                           "commit check). " + NEW_PULL)
        built = sorted(touched & items)
        if built:
            reasons.append(f"commit {commit['sha'][:7]} changes a component item ({', '.join(built)}) off a sync branch: "
                           "component item: route it to `system`, where every component item is built.")
    return reasons


def judge(facts, cwd, check):
    """Every reason to refuse this merge, or an empty list."""
    pr = facts["pr"]
    body = pr.get("body") or ""
    reasons = checks_refused(facts, cwd) + commits_refused(facts, cwd, check)
    paths = [path for item in facts["files"] for path in (item.get("filename"), item.get("previous_filename")) if path]
    risky = []
    guarded = protected_paths(paths, facts["kind"], check)
    if guarded:
        risky.append("a protected file: " + ", ".join(guarded[:5]) + (" and more" if len(guarded) > 5 else ""))
    gone = [item["filename"] for item in facts["files"] if item.get("status") == "removed"
            and not item["filename"].lower().startswith("working-files/")]
    if gone:
        risky.append("a deleted file: " + ", ".join(gone[:5]) + (" and more" if len(gone) > 5 else ""))
    if facts["kind"] == "product" or (not risky and has_pages(facts["repo"], cwd)):
        risky.append("a merge here may publish a live site")
    reasons += review_refused(pr, risky)
    size = pr.get("additions", 0) + pr.get("deletions", 0)
    if (size > MAX_LINES or pr.get("changedFiles", 0) > MAX_FILES) and not pr["headRefName"].startswith(COPY_BRANCHES) \
            and not LARGE.search(body):
        reasons.append(f"it changes {size} lines in {pr.get('changedFiles', 0)} files, over the limit of {MAX_LINES} "
                       f"lines or {MAX_FILES} files: split it, one piece per pull request, or add a line "
                       "`Large-pull-request: <why it cannot be split>`.")
    return reasons


def words_left(facts):
    """The added lines with a word the final audit looks for, by script (`running-sessions` step 5)."""
    found = []
    for item in facts["files"]:
        for line in (item.get("patch") or "").splitlines():
            if line.startswith("+") and not line.startswith("+++") and WORDS_LEFT.search(line):
                found.append(f"{item['filename']}: {line[1:].strip()[:120]}")
    return found


def run(raw):
    """Judge the hook's input: 0 to pass, 2 to refuse."""
    data = json.loads(raw)
    tool = data.get("tool_name", "")
    if tool.startswith("mcp__") and "merge_pull" in tool:
        return refuse(["this merge tool cannot be read by the merge check: use a plain `gh pr merge` from the "
                       "repository's checkout."])
    text = (data.get("tool_input") or {}).get("command")
    if tool not in ("Bash", "PowerShell") or not isinstance(text, str):
        return 0
    joined = re.sub(r"\\\r?\n", " ", text)
    if not MENTION.search(joined):
        return 0
    cwd = data.get("cwd") or os.getcwd()
    context = []
    try:
        for asked in merges_in(text, cwd):
            if asked["kind"] == "pass":
                continue
            if asked["kind"] in ("api", "wrapped"):
                return refuse(["this form of merge cannot be read by the merge check: use a plain `gh pr merge` from "
                               "the repository's checkout, as a command of its own."])
            if asked["kind"] == "chained":
                return refuse(["this command also holds `git push`, `gh pr edit` or `gh pr checks`, and this check reads "
                               "the pull request before any part runs, so it would judge the state before them. Run them "
                               "first, then `gh pr merge` as a command of its own."])
            flags = [flag for flag, on in (("--admin", asked["admin"]), ("--auto", asked["auto"])) if on]
            if flags:
                return refuse([f"`{flags[0]}` is never used: `--admin` bypasses the checks, and with `--auto` a later "
                               "merge could land a head the review did not pass."])
            facts = read_facts(asked)
            reasons = judge(facts, asked["cwd"], commit_check())
            if reasons:
                return refuse(reasons)
            context += words_left(facts)
    except Unreadable as error:
        return refuse([f"it could not read what it needs ({error}). A check that cannot run does not pass: fix that, "
                       "then merge again."])
    if context:
        shown = context[:20] + ([f"and {len(context) - 20} more"] if len(context) > 20 else [])
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext":
                          "merge check, words left in the lines this pull request adds (no block; a word can be right; "
                          "a line that was meant to go gets a follow-up): " + "; ".join(shown)}}))
    return 0


def main():
    for stream in (sys.stdout, sys.stderr):  # a name or a message in any language, whatever the laptop's code page
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    raw = RAW if RAW is not None else sys.stdin.buffer.read().decode("utf-8", "replace")
    if "merge" not in raw.lower():
        return 0
    try:
        return run(raw)
    except Exception as error:  # a check that cannot run does not pass, whatever went wrong
        if "merge_pull" in raw or MENTION.search(raw):
            return refuse([f"the merge check met an error ({type(error).__name__}: {error}). A check that cannot run "
                           "does not pass: fix that, then merge again."])
        return 0


if __name__ == "__main__":
    sys.exit(main())
