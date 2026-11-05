#!/usr/bin/env python3
# generated from system: edit there
"""Component router, run by the PreToolUse hook on the file-writing tools (Edit, Write, MultiEdit, NotebookEdit).

The owner's rule of 3 November 2026: every component item (a rule, skill, hook, mod, check, routine, template,
setting, prompt) is built only in `system`, for one repository or for all. The chat where the idea arises writes a
brief and routes it to `system` (the Route mode of the repository's handoff skill). A rule alone did not hold, so
this hook stops the write itself. One general rule decides, read from each repository's own files (its identity file's
`kind:` and its branch), never a list of repository names (the owner's rule of 5 November 2026: every repository, not
one or two). The owner's words behind both rules are quoted in `system`'s hooks README, never here.

It stops (exit 2, the reason on stderr, which Claude reads as the denial):
  - a write whose target, relative to the root of the repository that holds it, is under `.agents/skills/`,
    `.claude/skills/`, `.claude/hooks/`, `.claude/agents/`, `.agents/prompts/`, `.agents/instructions/`, `mods/` or
    `routines/`, matches `scripts/check_*`, or is `.claude/settings.json`, `.claude/settings.local.json`, or the
    root's `AGENTS.md` or `CLAUDE.md` (copies from `system`, its `Local` section included: a rule about how a
    repository works is a row of its `requirements.md`, where its instructions name one, or is routed to `system`);
  - a write into the user's own Claude Code and Codex folders (`~/.claude/` settings, `CLAUDE.md`, skills, commands,
    hooks, agents, mods, plugins; `~/.claude.json`; `~/.codex/`), which act in every repository and which `system`
    delivers to the laptop, unless the session's own repository (`CLAUDE_PROJECT_DIR`) is `system`;
  - a write to any path of `system` itself from a session whose own repository is another repository of ours, except
    its three records: `requirements.md` (a machinery finding is a row there), `docs/later.md` (a later idea about
    the machinery is a line there) and `tasks.md`, as the repository instructions and the handing-off-work and
    capturing-knowledge skills send them. Every other path there (its machinery, and its processes, architecture,
    maps, registries, decisions, plan and intake too) is written only by a `system` session: the item is routed
    there, never written there from outside. It is an allow list, so a new folder of `system` is stopped too.
GAP: paths not stopped, outside `system`: templates kept in a repository (no one path holds them),
`.github/workflows/`, `.codex/config.toml`, `.mcp.json`, `.pre-commit-config.yaml` and `.claude/commands/`. The
protected-file list of the commit check (`Owner-yes:`) still covers some of them.
GAP: Codex sessions are outside this hook. Codex runs no Claude Code hook, and `.agents/skills/` is Codex's own skill
folder, so a Codex session's write there is not stopped here. Only the commit check catches a Codex commit, and only
when its shell sets `CODEX_SANDBOX` (UNVERIFIED) or its message says `Made-by: agent` (task S224 verifies the marker).
A repository is a folder above the target with a `.git` entry and an identity file (`.agents/repository.yml`); every
such folder that holds the target is judged, so a `.git` or an identity file planted inside a repository changes
nothing. `git switch --orphan` empties the tree, so until an identity file is written there the folder is no
repository of ours to this hook; the commit check refuses the orphan branch's commit all the same. Of the folders
judged, the first that is `system` decides the write into `system`, so a repository nested inside `system` (a clone
in its folder) does not open `system`'s paths.
Letter case is ignored, and the path is resolved first (Windows paths, forward slashes, `/d/...` and `/mnt/d/...`
forms, `..`, links, the trailing dots and spaces and the `:stream` names Windows drops), so another spelling of the
same file is caught too.

It lets the write through:
  - in a repository whose identity file says `kind: system`, on disk and in its last commit (one Write of the identity
    file cannot open the paths, unless the git program is missing, when the commit check is the net; the commit
    check refuses a commit that turns the kind to `system`), from a session of `system` itself or of no repository
    of ours: the control plane builds them. When git does not answer in time, a repository whose file on disk says
    `system` is a doubt, which opens no path: `system`'s allow list applies to it, and neither it nor the session
    passes as `system`;
  - on a sync branch: the current branch of the repository holding the target starts with `chore/sync-` (the
    delivery branch of the reviewing-repositories skill, step 10). The name alone decides: any `chore/sync-*` branch
    passes, here and in the commit check, and the reviewers of its pull request check that it came from `system`'s
    sync. During a rebase the branch is the one being rebased (git's `rebase-merge/head-name` or
    `rebase-apply/head-name`), so a conflict in a `chore/sync-*` rebase is resolved as on the branch itself. GAP: no
    origin proof on a chore/sync-* branch (a delivery marker, as check_views uses);
  - for a path git holds as unmerged (a conflict to resolve, `git diff --name-only --diff-filter=U`) while git has
    a merge or a revert in progress in the repository holding the target (its `MERGE_HEAD` or `REVERT_HEAD` exists):
    a merge of `main` brings items already reviewed, and its conflicts must be resolved by hand. Every other path is
    judged as usual during the merge. This hook passes only those unmerged paths, for a merge of one branch, an
    octopus merge and a revert alike; the commit check then judges the commit when `git commit` makes it (git runs
    the commit-msg hook for `git commit` and `git merge`, the githooks manual, so also for a command that runs `git
    commit`: `git revert --continue`, a `reword` in `git rebase -i` and an `exec git commit` line of one (git's
    source; UNVERIFIED by test)): a merge of one branch against git's own merge of the two sides, while a revert or
    an octopus merge that stages a component item is refused off a sync branch, as an ordinary commit is. GAP:
    commits made without the commit-msg hook (git's source; UNVERIFIED by test), such as a clean `git revert` or
    `git cherry-pick`, `git am`, the picks a rebase replays, `git commit-tree` with `git update-ref`, `git
    fast-import`, `git filter-branch` or `git filter-repo`, a commit made on GitHub itself (the API or a web edit),
    and any commit in a clone where the hooks were never installed, write no file through a tool, so neither this
    hook nor the commit check judges them; the planned net is a pull-request check on GitHub that refuses component
    paths on a branch that is not `chore/sync-*` and protected files without `Owner-yes:` (task S226); until then
    protected files rest on the merger's `Owner-yes:` check (global instructions, Safety). GAP: a `MERGE_HEAD`
    written by hand passes the conflicted paths too; the commit check judges the commit, and the reviewers of the
    pull request see it;
  - for a target in no repository of ours (no git, or no identity file: the scratch folder, an outside clone);
  - into `system` from another repository's session, for its three records above;
  - for any other tool, such as a read.

It fails open: when it cannot read its input, or meets any error of its own, it allows the write and prints one
NOTICE line on stderr (and as a systemMessage the owner sees). A missing hook file is open too: the settings entry
runs `if [ -f "<file>" ]; then python3 "<file>"; else echo "NOTICE component-router missing" >&2; echo
'{"systemMessage":"NOTICE component-router missing"}'; fi`, so a session that keeps the entry on a branch made before
the delivery, where the file does not exist, writes freely and says so on stderr and as a systemMessage on stdout,
since Claude Code may not show stderr at exit 0 (plain `python3` would exit 2 there, and Claude Code would stop every
file write). The remedy is to merge
`origin/main` into the branch, which brings the file. Claude Code runs a hook command in a POSIX shell, Git Bash on
Windows, which `$CLAUDE_PROJECT_DIR` in every hook entry needs already.
The last net is the commit check (`scripts/check_commit_message.py`), which refuses a commit that adds or changes a
file under the repository paths above outside `system` unless the branch is a sync branch (a new repository and one
that joins the library get their machinery on one too, by `system`'s create-a-repository process). A branch with no
commit yet (`git switch --orphan`, or a new repository before its first commit) is judged like any other branch: no
pass for it. A write through the shell (a script, a redirect) is not seen here; the commit check catches it at
commit for a file git tracks. Git ignores `.claude/settings.local.json`, so a shell write to it is never committed and
never caught there; it stays in both lists because a file tool's write to it is stopped here, and a forced
`git add -f` of it is refused at commit.
Standard library only.
"""
import json
import os
import re
import subprocess
import sys

WRITE_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
FOLDERS = (".agents/skills/", ".claude/skills/", ".claude/hooks/", ".claude/agents/", ".agents/prompts/",
           ".agents/instructions/", "mods/", "routines/")
FILES = (".claude/settings.json", ".claude/settings.local.json", "agents.md", "claude.md")
# The repository's instruction files: a stop there also names where a rule about the repository goes.
INSTRUCTION_FILES = ("agents.md", "claude.md")
CHECK = re.compile(r"scripts/check_[^/]*")
# Under the user's home folder: what `system` delivers to the laptop and what acts in every repository.
HOME_FOLDERS = (".claude/skills/", ".claude/commands/", ".claude/hooks/", ".claude/agents/", ".claude/mods/",
                ".claude/plugins/", ".codex/")
HOME_FILES = (".claude/settings.json", ".claude/settings.local.json", ".claude/claude.md", ".claude.json")
# In `system`, from another repository's session: only these three records pass (an allow list, lower case).
SYSTEM_RECORDS = ("requirements.md", "docs/later.md", "tasks.md")
SYNC_BRANCH = "chore/sync-"
MESSAGE = ("component item: route it to `system`. `{path}` is machinery (a rule, skill, hook, mod, check, routine, "
           "template, setting or prompt), built only in `system` (the owner's rule of 3 November 2026). Do not write "
           "it here: write a brief (what, why, his words as he typed them, example files) and route it.\n"
           "1. A `system` session runs on the same topic: send it the brief by message.\n"
           "2. Else start a `system` session with the brief.\n"
           "3. Else (no session can start) write a change record, change-records/<YYYY-MM-DD>-<slug>.md, for the "
           "weekly review. A public repository writes no file for it, neither in itself nor in the private main "
           "repository named in this repository's instructions: its last step is the brief in the reply to the "
           "owner, with one task line in that reply for him to add to his own task list; no file here.\n"
           "The repository's handoff skill does these steps in its Route mode (handing-off-work, or session-handoff "
           "where that is the repository's own), where the repository has one.")
INSTRUCTION_NOTE = ("\n`AGENTS.md` and `CLAUDE.md` are copies from `system`, their `Local` section included. A rule "
                    "about how this repository works is a row of its `requirements.md`, where its instructions name "
                    "one; else, or for a rule for every repository, route it to `system` as above.")


def notice(text):
    """Allow the write, and say why the hook could not judge it."""
    line = f"NOTICE component-router: {text}; the write is allowed (the hook fails open)."
    print(line, file=sys.stderr)
    print(json.dumps({"systemMessage": line}))
    return 0


def resolved(raw, cwd):
    """The target as one absolute, normalised path: the Git Bash and WSL forms of a Windows drive turned into the drive,
    a relative path joined to the session's folder, links resolved, and on Windows each part without the trailing dots
    and spaces and the `:stream` name Windows drops."""
    path = raw.strip()
    if os.name == "nt":
        found = re.match(r"^/(?:mnt/)?([a-zA-Z])(?=/|$)", path)
        if found:
            path = found.group(1) + ":" + (path[found.end():] or "/")
    if not os.path.isabs(path):
        path = os.path.join(cwd or os.getcwd(), path)
    path = os.path.realpath(os.path.abspath(path))
    if os.name == "nt":
        drive, rest = os.path.splitdrive(path)
        parts = []
        for part in re.split(r"[\\/]", rest):
            part = part.split(":")[0]  # `file::$DATA` and `file:stream` write `file`
            parts.append(part.rstrip(" .") if part not in (".", "..") else part)
        path = drive + "\\".join(parts)
    return path


def repository_roots(path):
    """Every folder above the path that is a repository of ours: a `.git` entry (a folder, or a worktree's file) and
    an identity file, nearest first. Every one is judged, so a `.git` and an identity file planted inside a repository
    change nothing."""
    roots = []
    folder = os.path.dirname(path)
    while True:
        if os.path.exists(os.path.join(folder, ".git")) and \
                os.path.isfile(os.path.join(folder, ".agents", "repository.yml")):
            roots.append(folder)
        parent = os.path.dirname(folder)
        if parent == folder:
            return roots
        folder = parent


def repository_root(path):
    """The nearest repository of ours that holds the path, or None."""
    roots = repository_roots(path)
    return roots[0] if roots else None


def git_folder(root):
    """The git folder of the repository at root (a worktree's `.git` file names its own), or None."""
    git = os.path.join(root, ".git")
    try:
        if os.path.isfile(git):
            with open(git, encoding="utf-8") as handle:
                line = handle.read().strip()
            if not line.startswith("gitdir:"):
                return None
            git = os.path.normpath(os.path.join(root, line[len("gitdir:"):].strip()))
    except (OSError, ValueError):  # ValueError: a file that is not UTF-8
        return None
    return git


def branch(root):
    """The current branch of the repository at root, read from its HEAD; '' on a detached HEAD or when it cannot be
    read. During a rebase HEAD is detached, so the branch being rebased is read from git's own record of it
    (`rebase-merge/head-name`, or `rebase-apply/head-name`, in the git folder of that worktree)."""
    git = git_folder(root)
    if git is None:
        return ""
    try:
        with open(os.path.join(git, "HEAD"), encoding="utf-8") as handle:
            head = handle.read().strip()
    except (OSError, ValueError):
        return ""
    if head.startswith("ref: refs/heads/"):
        return head[len("ref: refs/heads/"):]
    for record in ("rebase-merge", "rebase-apply"):
        try:
            with open(os.path.join(git, record, "head-name"), encoding="utf-8") as handle:
                name = handle.read().strip()
        except (OSError, ValueError):
            continue
        if name.startswith("refs/heads/"):
            return name[len("refs/heads/"):]
    return ""


def unmerged(root):
    """The paths (relative to root, forward slashes, lower case) git holds as unmerged while a merge or a revert is in
    progress in the repository at root (MERGE_HEAD or REVERT_HEAD in its git folder); an empty set otherwise, or when
    git cannot say, so a doubt never opens a path."""
    git = git_folder(root)
    if git is None or not any(os.path.isfile(os.path.join(git, ref)) for ref in ("MERGE_HEAD", "REVERT_HEAD")):
        return set()
    try:
        done = subprocess.run(["git", "-C", root, "diff", "--name-only", "--diff-filter=U", "-z"], capture_output=True,
                              text=True, encoding="utf-8", timeout=10)
    except (OSError, ValueError, subprocess.TimeoutExpired):  # ValueError: a name that is not UTF-8
        return set()
    if done.returncode != 0 or done.stdout is None:  # None: a name that is not UTF-8, on Windows
        return set()
    return {name.replace("\\", "/").lower() for name in done.stdout.split("\0") if name}


def kind_in(text):
    """The `kind:` value of an identity file's text, or ''."""
    for line in text.splitlines():
        key, _, value = line.split("#")[0].partition(":")
        if key.strip() == "kind":
            return value.strip()
    return ""


def is_system(root):
    """True when the identity file says `kind: system` on disk and in the last commit (git run at that root shows it
    from its HEAD); False when either says another kind, or there is no commit; None on a doubt: the file on disk says
    `system` but git did not answer (a timeout, a refused start, output it cannot decode). Each caller takes the doubt
    the way that opens nothing: as `system` where `system`'s allow list then applies to the target, and as not
    `system` where the session or the target's repository would be passed for being `system`."""
    try:
        with open(os.path.join(root, ".agents", "repository.yml"), encoding="utf-8") as handle:
            if kind_in(handle.read()) != "system":
                return False
    except (OSError, ValueError):
        return False
    try:
        done = subprocess.run(["git", "-C", root, "show", "HEAD:.agents/repository.yml"], capture_output=True,
                              text=True, encoding="utf-8", timeout=10)
    except FileNotFoundError:
        return True  # the git program is not on this machine at all: the identity file on disk decides
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None  # git is there but did not answer: a doubt, which never opens a path at any caller
    if done.stdout is None:  # on Windows, output that is not UTF-8 fails in subprocess's reader thread: a doubt too
        return None
    return done.returncode == 0 and kind_in(done.stdout) == "system"


def component_path(relative):
    """True when a path relative to a repository root (forward slashes, lower case) is a component item's."""
    return relative.startswith(FOLDERS) or relative in FILES or bool(CHECK.fullmatch(relative))


def system_record(relative):
    """True when a path relative to `system`'s root (forward slashes, lower case) is one of the three records a
    session of another repository may write there."""
    return relative in SYSTEM_RECORDS


def home_component(path):
    """The path relative to the user's home folder when it is one of the user-level component paths, else None."""
    home = os.path.realpath(os.path.expanduser("~"))
    try:
        relative = os.path.relpath(path, home).replace("\\", "/").lower()
    except ValueError:  # another drive
        return None
    if relative.startswith("../") or not (relative.startswith(HOME_FOLDERS) or relative in HOME_FILES):
        return None
    return relative


def session_root(event):
    """The session's own repository (`CLAUDE_PROJECT_DIR`, else the session's folder), or None."""
    start = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    return repository_root(os.path.join(resolved(start, None), "x"))


def session_is_system(event):
    """True when the session's own repository is `system`; a doubt (None from is_system) is not `system`."""
    root = session_root(event)
    return root is not None and is_system(root) is True


def stop(shown, relative=""):
    note = INSTRUCTION_NOTE if relative in INSTRUCTION_FILES else ""
    print(MESSAGE.format(path=shown) + note, file=sys.stderr)
    return 2


def judge(event):
    """0 to allow, 2 to stop; the stop's reason is printed on stderr."""
    if event.get("tool_name") not in WRITE_TOOLS:
        return 0
    tool_input = event.get("tool_input") or {}
    raw = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(raw, str) or not raw.strip():
        return notice(f"no target path in the {event.get('tool_name')} call")
    path = resolved(raw, event.get("cwd"))
    roots = repository_roots(path)
    if not roots:
        at_home = home_component(path)
        if at_home is not None and not session_is_system(event):
            return stop("~/" + at_home)
        return 0  # outside every repository of ours
    # A doubt counts as `system` here (only the three records pass), and as not `system` for the session below and
    # for the target's repository in the loop, so a slow git never opens a path.
    home = next((root for root in roots if is_system(root) is not False), None)
    if home is not None:
        # A session of another repository of ours writes only `system`'s three records; every other path is stopped,
        # a repository nested inside `system` included.
        relative = os.path.relpath(path, home).replace("\\", "/")
        if not system_record(relative.lower()):
            session = session_root(event)
            if session is not None and is_system(session) is not True:
                return stop(relative + " (in `system`, written only by a `system` session)")
    for root in roots:
        relative = os.path.relpath(path, root).replace("\\", "/").lower()
        if not component_path(relative) or is_system(root) is True or branch(root).startswith(SYNC_BRANCH):
            continue
        if relative in unmerged(root):
            continue
        return stop(os.path.relpath(path, root).replace("\\", "/"), relative)
    return 0


def main():
    try:
        event = json.loads(sys.stdin.read())
    except (ValueError, OSError, UnicodeDecodeError) as error:
        return notice(f"its input could not be read ({error.__class__.__name__})")
    if not isinstance(event, dict):
        return notice("its input is not a JSON object")
    try:
        return judge(event)
    except Exception as error:  # a broken hook never blocks all work
        return notice(f"it failed ({error.__class__.__name__}: {error})")


if __name__ == "__main__":
    sys.exit(main())
