#!/usr/bin/env python3
# generated from system: edit there
"""Commit message check: blocks a protected file changed without the owner's yes; reports the subject form, the
Made-by line and the order of the trailers. Run by git at the commit-msg stage.

Blocks one thing: an agent's or a routine's commit that changes a protected file without the line
`Owner-yes: "<the owner's words>"`, quoting his yes from the session (guardrail 6). The protected files are the ones
only the owner may approve a change to:
  - in the hub and in the control plane (the identity file .agents/repository.yml says `kind: workspace` or
    `kind: system`; `system` added on the owner's correction of 2026-10-21): the HUB list below (workspace's
    AGENTS.md list, and system's AGENTS.md list, which adds its own paths); in `system` it also holds the standing
    approvals, the blocked paths and the library originals of every protected file (2026-10-22), and the nexego-core
    trial plugin's store
    (`.claude-plugin/`) and everything in `library/plugins-and-mods/` (the trial plugin's build, parts, store and
    plugin manifest originals, test, generated plugin and managed draft, the laptop's plugin record, the index page),
    2026-10-31;
  - in every other repository: the EVERYWHERE list below (the shared instructions, the secret-scan exceptions, this
    check, the views check and the hooks), so a sync from `system` that changes one of them carries the owner's yes too;
  - in every repository, both lists: `mods/`, where a repository has its own local mods (a mod's code runs inside
    every Claude Code session there, like a hook; 2026-11-03, task S204). A repository without the folder never stages
    a path in it.
The staged files are read with `git diff --cached --name-only --no-renames -z`, so a deletion counts too, a file
moved away counts under its old path as well as its new one, and a name git would quote (a quotation mark, a
backslash, a tab or a newline in it) is read unquoted and unstripped (text mode turns a carriage return in a name
into a newline, which the path rules match all the same). Paths are matched without regard to letter case. When git
cannot list the staged files, or lists a name that is not UTF-8, the check prints `BLOCKED ...` and refuses: a check
that cannot run does not pass.

Blocks a second thing, the last net of the component router (the owner's rule of 3 November 2026: every
component item is built only in `system`): outside `system` (unless the identity file, and the committed one when a
commit holds one, both say `kind: system`), an agent's or a routine's commit that adds or changes a file under
`.agents/skills/`, `.claude/skills/`, `.claude/hooks/`, `.claude/agents/`, `.agents/prompts/`,
`.agents/instructions/`, `mods/` or `routines/`, a `scripts/check_*` file, `.claude/settings.json`,
`.claude/settings.local.json`, or the root's `AGENTS.md` or `CLAUDE.md` (copies from `system`, their `Local` section
included), unless the current branch is a sync branch (`chore/sync-*`: the delivery branch of the
reviewing-repositories skill, step 10, and the branch on which the create-a-repository process gives a new repository
its machinery and an existing one joins the library). A commit with no HEAD yet (a new repository's first commit, or
the first commit of a branch made with `git switch --orphan`) gets no pass of its own: it is judged like any other.
Its message starts "component item: route it to `system`", as the PreToolUse hook `.claude/hooks/component-router.py`
says when it stops the write. A deletion alone is not refused (a moved file counts under its new path), and an
`Owner-yes:` line does not lift it: the item goes to `system`. `system` is a repository whose identity file says
`kind: system` on disk and in HEAD; there nothing changes. An agent's commit that stages an identity file saying
`kind: system` while HEAD's says another kind or holds none (a first commit, an orphan branch) is refused too, in
every state, a merge or a revert git has in progress included, so a second commit cannot pass as `system`. A
repository with no identity file counts as not `system` here (the hook passes such a folder as no repository of ours,
but every repository that runs this check has one). The branch name alone decides the sync pass: any `chore/sync-*`
branch passes, and the reviewers of its pull request check that it came from `system`'s sync (GAP: no origin proof on
a chore/sync-* branch, a delivery marker as check_views uses). During a rebase (this check runs there for a `git
commit` made while the rebase is stopped, a `reword` of `git rebase -i` and an `exec git commit` line of one, git's
source; UNVERIFIED by test; the replayed picks: GAP below), the branch is the one being rebased (git's
`rebase-merge/head-name` or `rebase-apply/head-name`), so a `chore/sync-*` rebase passes as the branch does.
Git ignores `.claude/settings.local.json`, so it reaches a commit only by a forced `git add -f`; it stays in the list
to refuse that.
During a merge of one branch git has in progress (MERGE_HEAD names one commit; a single MERGE_HEAD written by hand is
judged as a merge of the commit it names), the net runs on the component items whose staged content differs from
git's own default merge of HEAD and MERGE_HEAD (`git merge-tree --write-tree --allow-unrelated-histories`, git 2.38 or
later) and that were not a conflict there: an edit slipped into the merge is refused, while what the two sides bring
and a resolved conflict pass. The option for unrelated histories is always
given, since git writes MERGE_HEAD for them only when the merge allowed them; such a merge is judged like any other. A
merge made with `-s ours` stages nothing beyond HEAD, so it passes. A merge made with another strategy or strategy
option that leaves a component item different from git's default merge, and not a conflict there, is refused as an
edit slipped in. When git cannot compute that merge (an older git, a broken repository), a merge that stages a
component item is refused: a check that cannot run does not pass. GAP: a merge of a branch that holds a component
item lands unrefused, since its items are part of git's own merge; only a merge of `main`, which holds only reviewed
items, is the case meant. During a revert git has in progress (REVERT_HEAD) and a merge of several branches at once
(MERGE_HEAD names several, an octopus merge, or several written by hand), the net runs as on an ordinary commit:
every component item the commit adds or changes is refused off a sync branch.
Git runs this check (the commit-msg hook) for `git commit` and `git merge` (the githooks manual), so also for a
command that runs `git commit`: a `reword` in `git rebase -i` and an `exec git commit` line of one (git's source;
UNVERIFIED by test). So a revert or a cherry-pick is judged when `git commit` finishes it: after `git revert -n` or
`git cherry-pick -n`, or after a conflict (`git revert --continue` and `git cherry-pick --continue` run `git commit`
for the stopped commit; git's source; UNVERIFIED by test). GAP: commits made without the commit-msg hook (git's
source; UNVERIFIED by test), such as a clean `git revert` or `git cherry-pick` (and the later commits of a range
after `--continue`), `git am`, the commits a rebase replays or makes on `git rebase --continue`, `git commit-tree`
with `git update-ref`, `git fast-import`, `git filter-branch` or `git filter-repo`, a commit made on GitHub itself
(the API or a web edit), and any commit in a clone where the hooks were never installed: the PreToolUse hook sees no
file write, so their component items and protected files land unjudged. The planned net is a pull-request check on
GitHub that refuses component paths on a branch that is not `chore/sync-*` and protected files without `Owner-yes:`
(task S226); until then protected files rest on the merger's `Owner-yes:` check (global instructions, Safety).
GAP: a conflict's resolution is not judged; the reviewers of the pull request see it.

Blocks a third thing, the part of the standing yes a tool can read (guardrail 6, decision 0033 in `system`): an agent's
or a routine's commit that weakens a guard in one of these readable ways needs a second line, `Owner-yes-weaker: "<his
words naming this change>"`, beside `Owner-yes:`, holding other words than that line and not those of the standing yes.
The readable ways, compared file by file between HEAD and the staged file, so an entry moved or edited counts: in a
Claude settings file (`.claude/settings.json`, `.claude/settings.local.json`, `library/settings/**.json`) a deny or ask
entry, a hook (its event, matcher and command together) or an Auto mode list entry other than an allow or environment
line gone, or an allow entry, an additional directory, an Auto mode allow or environment line, a `defaultMode` or
`disableAllHooks` added; in a pre-commit file a hook id gone; in a workflow file a step name gone; in a secret-scan
exceptions file a line added; and a check or hook file gone (`scripts/check_*`, `.claude/hooks/*`, `library/checks/*`,
`library/hooks/*`, counted by file name, so a moved file is no change). A settings file that HEAD holds as valid JSON
and that is staged as anything else counts too, since it may guard nothing now. A file HEAD does not hold counts as an
added one, except on a commit with no HEAD or on a sync branch outside `library/`, where a repository takes its first
copy. During a merge of one branch git has in progress, it reads only the paths edited beyond git's own merge of the two
sides, against that merge: a merge brings approved changes (GAP: a conflict's resolution is not judged, as above). GAP:
the line is typed by the agent it limits, and nothing here proves the words are his: it stops an honest mistake and
leaves a record, not a lie. GAP: any other weakening (a hook that blocks less, a check that tests less, another settings
key such as `env`, a connector file) is not read here: the `reviewer` pass that confirms "no weaker" (guardrail 6) stays
the net for it.

Reports only (prints a NOTICE and passes, because format is not harm): a subject that is not in the form
`type(scope): summary` (or `type: summary`), a missing `Made-by: agent | program <tool>` line (or `job` or
`owner`), and trailers out of their one order: `Owner-yes:`, then any `Owner-yes-weaker:`, then `Made-by:`, then any
`Co-authored-by:` lines (in any letter case; the commit template in system:docs/rules/reference.md).

A commit the owner makes by hand is never checked (the owner's rule, 2026-09-29: freedom, not new blocks). A merge or
a revert that git itself has in progress (MERGE_HEAD or REVERT_HEAD exists) gets no format report. During a merge of
one branch the protected-file check runs only on the staged paths whose content differs from git's own merge of the
two sides and that were not a conflict there, as the component net does: a merge of main into a work branch brings
changes to protected files that were already approved, while a protected file edited on top of the merge needs the
`Owner-yes:` line. When git cannot compute that merge, every protected file the merge stages needs it. During a
revert or a merge of several branches the protected-file check runs as on an ordinary commit. The component net and
the kind refusal above run on a merge and a revert too. A subject that only starts with "Merge" or "Revert" earns
nothing: such a commit is checked like any other.
A commit counts as an agent's when an AI tool's shell made it or its message says `Made-by: agent` or
`Made-by: job`. GAP: Codex sessions are outside the component router's hook (Codex runs no Claude Code hook, and
`.agents/skills/` is Codex's skill folder), so for Codex this net is the only guard, and it sees a Codex commit only
when Codex's shell sets `CODEX_SANDBOX` (UNVERIFIED, `by_agent()` below) or the message says `Made-by: agent`
(task S224 verifies the marker). Standard library only.

Usage (by pre-commit): python3 scripts/check_commit_message.py <message file>
"""
import collections
import fnmatch
import json
import os
import re
import subprocess
import sys

TYPES = "feat|fix|docs|chore|refactor|test|build|ci|perf|style|revert"
SUBJECT = re.compile(rf"^({TYPES})(\([a-z0-9-]+\))?!?: \S")
TRAILER = re.compile(r"^Made-by: (agent|job|owner) \| program \S+", re.M)
OWNER_YES = re.compile(r"^Owner-yes: [\"“][^\"”]*\S[^\"”]*[\"”]\s*$", re.M)
OWNER_YES_WEAKER = re.compile(r"^Owner-yes-weaker: [\"“]([^\"”]*\S[^\"”]*)[\"”]\s*$", re.M)
# Words that mark his general yeses, which never cover a weakening (decision 0033 in `system`).
GENERAL_YES = ("all four", "standing yes", "one yes line")
OWNER_YES_WORDS = re.compile(r"^Owner-yes: [\"“]([^\"”]*)[\"”]\s*$", re.M)
# The trailers in their one order: a line of a later kind before a line of an earlier kind is out of order.
TRAILER_ORDER = tuple(re.compile(rf"^{name}:", re.I) for name in ("Owner-yes", "Owner-yes-weaker", "Made-by",
                                                                  "Co-authored-by"))
AGENT_MARKERS = ("AI_AGENT", "CLAUDECODE", "CLAUDE_CODE_REMOTE", "CODEX_SANDBOX")
HUB = ("AGENTS.md", ".agents/instructions/global-instructions.md", "system/permissions.md",
       # workspace's copy of the blocked-paths list, protected as its original in system is (2026-10-30)
       "system/blocked-paths.md", ".claude/settings.json",
       ".claude/hooks/*", ".claude/agents/reviewer.md", ".pre-commit-config.yaml", ".gitleaksignore",
       "scripts/check_*.py", "routines/*", ".github/workflows/*", ".mcp.json", ".codex/config.toml",
       "scripts/mcp_github_headers.py",
       ".pre-commit-hooks.yaml",  # the hook source: it decides what code the repositories using it run (S149)
       # the nexego-core trial plugin: its store, its build and parts, and the generated plugin whose hooks and agents a
       # session runs; and plugin-list@laptop, a record of the laptop's plugin state (Claude Code writes those files),
       # protected so it moves only with the owner's yes; it does not decide installs (2026-10-31, system PR 98)
       ".claude-plugin/*", "library/plugins-and-mods/*",
       # in system: the standing approvals and the library originals of protected files (2026-10-22)
       "docs/rules/permissions.md", "docs/rules/blocked-paths.md",
       "library/instructions/*", "library/settings/*", "library/hooks/*", "library/checks/*",
       "library/subagents/reviewer/*", "library/repository-files/gitleaksignore*",
       # the identity file's originals, which the sync places as the protected .agents/repository.yml (2026-10-30)
       "library/repository-files/identity*", "library/connectors/*",
       "library/routines/*", "library/scripts/mcp-github-headers/*",
       # the installer the cloud-setup hook runs (it installs the git hooks) and the sync, with their originals
       "scripts/install.py", "scripts/sync.py", "library/scripts/install/*", "library/scripts/sync/*",
       # the manifest and the blueprints: a row can place any file on any path of a repository (2026-10-22)
       "manifest/*", "blueprints/*",
       # the identity file: its kind decides which list applies, so changing it is protected too (2026-10-22)
       ".agents/repository.yml",
       # a repository's local mods: their code runs inside every session there, like a hook (2026-11-03, S204)
       "mods/*")
# The component router's paths (the hook's own list): an item under them is built only in `system` (2026-11-03).
COMPONENT_FOLDERS = (".agents/skills/", ".claude/skills/", ".claude/hooks/", ".claude/agents/", ".agents/prompts/",
                     ".agents/instructions/", "mods/", "routines/")
COMPONENT_FILES = (".claude/settings.json", ".claude/settings.local.json", "agents.md", "claude.md")
COMPONENT_CHECK = re.compile(r"scripts/check_[^/]*")
SYNC_BRANCH = "chore/sync-"
ROUTE = ("component item: route it to `system`. This commit adds or changes machinery ({paths}), which is built only "
         "in `system` (the owner's rule of 3 November 2026). Take the change out of this commit, write a brief (what, "
         "why, his words as he typed them, example files) and route it (the Route mode of the repository's handoff "
         "skill, handing-off-work or session-handoff, where the repository has one): a running `system` session on "
         "the same topic by message; else a new `system` session; else a change record, "
         "change-records/<YYYY-MM-DD>-<slug>.md, for the weekly review (a public repository writes no file for it, "
         "neither in itself nor in the private main repository named in this repository's instructions: its last "
         "step is the brief in the reply to the owner, with one task line in that reply for him to add to his own "
         "task list; no file here). A rule about how this repository works, which `AGENTS.md` or `CLAUDE.md` would "
         "hold, is a row of its `requirements.md` where its instructions name one, else routed the same way. A "
         "`system` session that delivers the machinery here (the sync, a new repository's machinery, or this "
         "repository joining the library) commits on a `chore/sync-*` branch. FAIL")
EVERYWHERE = (".agents/instructions/global-instructions.md", ".gitleaksignore", "scripts/check_commit_message.py",
              ".claude/hooks/*", "scripts/install.py",
              "scripts/check_views.py",  # the views check: only the mirror writes views/ (decision 0029, S072)
              "mods/*")  # a repository's local mods: their code runs inside every session there (2026-11-03, S204)


def trailers_in_order(lines):
    """True when the trailer lines keep the order Owner-yes:, Owner-yes-weaker:, Made-by:, then any Co-authored-by:."""
    last = -1
    for line in lines:
        rank = next((n for n, pattern in enumerate(TRAILER_ORDER) if pattern.match(line)), None)
        if rank is None:
            continue
        if rank < last:
            return False
        last = rank
    return True


def by_agent():
    """True in a shell an AI tool started: it sets one of these names (AI_AGENT and CLAUDECODE seen in Claude Code,
    2026-09-29; CODEX_SANDBOX for Codex is UNVERIFIED). A person's own terminal sets none of them.
    GAP: a Codex session runs no Claude Code hook, so the component router's net here is its only guard, and it holds
    only if Codex sets CODEX_SANDBOX or the message says `Made-by: agent` (task S224 verifies Codex's marker)."""
    return any(os.environ.get(name) for name in AGENT_MARKERS)


def names(out):
    """The paths of git's NUL-separated (`-z`) list: never quoted, never stripped. The readers decode git's output in
    text mode, which turns a carriage return in a name into a newline; the path rules match such a name all the same.
    None when there is no output to read: on Windows a name that is not UTF-8 fails in subprocess's reader thread,
    which leaves the output None instead of raising (on other systems the ValueError is caught by the reader)."""
    if out is None:
        return None
    return [name for name in out.split("\0") if name]


def staged_files():
    """The paths this commit changes, or None when git cannot say (the check then refuses: it could not run).
    `--no-renames` lists a moved file under both its old and its new path, so a protected file renamed away counts.
    `-z` keeps a name git would quote (a quotation mark, a backslash, a tab, a newline) unquoted. A name that is not
    UTF-8 (ValueError) gives None too."""
    try:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--no-renames", "-z"], capture_output=True,
                             text=True, encoding="utf-8", check=True).stdout
    except (subprocess.CalledProcessError, OSError, ValueError):
        return None
    return names(out)


def merge_state():
    """'merge' while git itself is in the middle of a merge of one branch (MERGE_HEAD names one commit), 'other'
    during a revert (REVERT_HEAD) or a merge of several branches at once (MERGE_HEAD names several), None otherwise.
    A MERGE_HEAD file that cannot be read gives 'other', the stricter net (judged as an ordinary commit).
    The subject line is never trusted for this, because anyone can start a subject with the word Merge."""
    try:
        if subprocess.run(["git", "rev-parse", "-q", "--verify", "REVERT_HEAD"], capture_output=True).returncode == 0:
            return "other"
        if subprocess.run(["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"], capture_output=True).returncode != 0:
            return None
        where = subprocess.run(["git", "rev-parse", "--git-path", "MERGE_HEAD"], capture_output=True, text=True,
                               encoding="utf-8").stdout.strip()
    except OSError:
        return None
    try:
        with open(where, encoding="utf-8") as handle:
            heads = [line for line in handle.read().splitlines() if line.strip()]
    except OSError:
        return "other"
    return "merge" if len(heads) <= 1 else "other"


def own_merge():
    """(tree, conflicted paths) of git's own merge of HEAD and MERGE_HEAD, or None when git cannot compute it."""
    try:
        done = subprocess.run(["git", "merge-tree", "--write-tree", "--name-only", "--no-messages", "-z",
                               "--allow-unrelated-histories", "HEAD", "MERGE_HEAD"], capture_output=True, text=True,
                              encoding="utf-8")
    except (OSError, ValueError):  # ValueError: a name that is not UTF-8
        return None
    if done.stdout is None:  # a name that is not UTF-8, on Windows (names() above)
        return None
    names = done.stdout.split("\0")
    if done.returncode not in (0, 1) or not names[0].strip():
        return None
    return names[0].strip(), {name for name in names[1:] if name}


def slipped_into_merge(paths):
    """The paths among these whose staged content differs from git's own merge of HEAD and MERGE_HEAD and that were not
    a conflict there: an edit slipped into a merge. None when git cannot compute that merge (git older than 2.38 has
    no `merge-tree --write-tree`). `--allow-unrelated-histories` is always passed: git writes MERGE_HEAD for two
    unrelated histories only when the merge itself allowed them, and for related ones the option changes nothing.
    Two git calls whatever the number of paths: the merge, then one comparison of the index with its tree."""
    merged = own_merge()
    if merged is None:
        return None
    tree, conflicted = merged
    try:
        differ = subprocess.run(["git", "diff", "--cached", "--name-only", "--no-renames", "-z", tree],
                                capture_output=True, text=True, encoding="utf-8")
    except (OSError, ValueError):
        return None
    if differ.returncode != 0 or differ.stdout is None:
        return None
    changed = {name for name in differ.stdout.split("\0") if name}
    return [path for path in paths if path in changed and path not in conflicted]


def is_hub():
    """True when the identity file says this repository is the hub or the control plane (`kind: workspace` or
    `kind: system`): both are guarded by the HUB list."""
    hub = ("kind: workspace", "kind: system")
    try:
        with open(".agents/repository.yml", encoding="utf-8") as identity:
            if any(line.split("#")[0].strip() in hub for line in identity):
                return True
    except OSError:
        pass
    try:  # the committed identity counts too, so one commit cannot change the kind and a protected file together
        head = subprocess.run(["git", "show", "HEAD:.agents/repository.yml"], capture_output=True, text=True,
                              encoding="utf-8").stdout
    except OSError:
        return False
    return any(line.split("#")[0].strip() in hub for line in head.splitlines())


def kind_in(text):
    """The `kind:` value of an identity file's text, or ''."""
    values = [line.split("#")[0].partition(":")[2].strip() for line in text.splitlines()
              if line.split("#")[0].partition(":")[0].strip() == "kind"]
    return values[0] if values else ""


def kind_of(spec):
    """The `kind:` of the identity file git shows for spec (`HEAD:...` or `:...` for the staged one), or None when git
    shows none (no such file, no HEAD commit, or git cannot read the repository)."""
    try:
        done = subprocess.run(["git", "show", spec], capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return None
    return kind_in(done.stdout) if done.returncode == 0 else None


def kind_turned_to_system():
    """True when this commit stages an identity file that says `kind: system` while HEAD's says another kind or holds
    none (a first commit, an orphan branch): a later commit must not pass as `system` to open the component router's
    paths."""
    return kind_of(":.agents/repository.yml") == "system" and kind_of("HEAD:.agents/repository.yml") != "system"


def is_system():
    """True when the identity file says `kind: system` on disk and in HEAD, so neither an edit nor a commit with no HEAD
    (a first commit, an orphan branch) passes as `system`."""
    try:
        with open(".agents/repository.yml", encoding="utf-8") as identity:
            if kind_in(identity.read()) != "system":
                return False
    except OSError:
        return False
    return kind_of("HEAD:.agents/repository.yml") == "system"


def current_branch():
    """The current branch, or '' on a detached HEAD or when git cannot say. During a rebase HEAD is detached, so the
    branch being rebased is read from git's own record of it (`rebase-merge/head-name`, or `rebase-apply/head-name`):
    a rebase of a `chore/sync-*` branch passes as the branch itself does."""
    try:
        done = subprocess.run(["git", "symbolic-ref", "--short", "-q", "HEAD"], capture_output=True, text=True,
                              encoding="utf-8")
    except OSError:
        return ""
    if done.returncode == 0:
        return done.stdout.strip()
    for record in ("rebase-merge/head-name", "rebase-apply/head-name"):
        try:
            where = subprocess.run(["git", "rev-parse", "--git-path", record], capture_output=True, text=True,
                                   encoding="utf-8")
            with open(where.stdout.strip(), encoding="utf-8") as handle:
                name = handle.read().strip()
        except OSError:
            continue
        if where.returncode == 0 and name.startswith("refs/heads/"):
            return name[len("refs/heads/"):]
    return ""


def added_or_changed():
    """The paths this commit adds or changes (a deletion left out; a moved file counts under its new path), or None
    when git cannot say or lists a name that is not UTF-8. Read NUL-separated, as staged_files() is."""
    try:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--no-renames", "--diff-filter=d", "-z"],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
    except (subprocess.CalledProcessError, OSError, ValueError):
        return None
    return names(out)


def component_items(paths):
    """The component items among the paths, letter case ignored: the component router's own list."""
    found = []
    for path in paths:
        low = path.lower()
        if low.startswith(COMPONENT_FOLDERS) or low in COMPONENT_FILES or COMPONENT_CHECK.fullmatch(low):
            found.append(path)
    return found


def protected(paths):
    """The protected ones among the paths. Letter case is ignored: on Windows a file staged as `Routines/x.md` lands
    in `routines/`."""
    patterns = [pattern.lower() for pattern in (HUB if is_hub() else EVERYWHERE)]
    return [p for p in paths if any(fnmatch.fnmatchcase(p.lower(), pattern) for pattern in patterns)]


def kind_net():
    """The refusal of a commit that turns the identity file's kind to `system`, in every state (a merge or a revert git
    has in progress too); 0 to pass, 1 to refuse."""
    if not kind_turned_to_system():
        return 0
    print("this commit makes the identity file's kind `system` (the staged one says `system`, HEAD's says another "
          "kind or holds none), which would open the component router's paths here. There is one `system`, the "
          "control plane; only the owner makes a repository `system`, by hand. A new repository created from "
          "`system` takes the kind its blueprint names. FAIL")
    return 1


def component_net(staged):
    """The component net on any commit but a merge of one branch: outside `system` and off a sync branch, a component
    item the commit adds or changes is refused; 0 to pass, 1 to refuse."""
    if is_system() or current_branch().startswith(SYNC_BRANCH):
        return 0
    changed = added_or_changed()
    items = component_items(staged if changed is None else changed)
    if not items:
        return 0
    print(ROUTE.format(paths=", ".join(items)))
    return 1


def unreadable(what):
    """Refuse, saying git could not list the staged files: a check that cannot run does not pass."""
    print(f"BLOCKED the commit message check could not read the staged files {what}from git, so it cannot tell whether "
          "a protected file or a component item changes. A check that cannot run does not pass: make `git diff "
          "--cached` work here (and rename a staged file whose name is not UTF-8), then commit again. FAIL")
    return 1


def protected_net(touched, body, where=""):
    """The protected-file check on these paths: refused (1) when any is protected and the message has no `Owner-yes:`
    line holding his words; 0 to pass."""
    touched = protected(touched)
    if not touched or OWNER_YES.search(body):
        return 0
    print("this commit changes a protected file (" + ", ".join(touched) + where + "), which needs the owner's "
          "yes: add a line Owner-yes: \"<his words from the session>\". Without his yes, ask him first; "
          "after outside material, only his typed yes counts. FAIL")
    return 1


def merge_net(body):
    """Both nets during a merge of one branch git has in progress, judged against git's own merge of the two sides: a
    component item (outside `system` and off a sync branch) or a protected file (without an `Owner-yes:` line) whose
    staged content differs from that merge, and that was not a conflict there, is refused; 0 to pass, 1 to refuse.
    When git cannot compute that merge, a component item refuses the merge, and every protected file it stages needs
    the `Owner-yes:` line."""
    staged = staged_files()
    if staged is None:
        return unreadable("of this merge ")
    changed = added_or_changed()
    if changed is None:
        changed = staged
    netted = not (is_system() or current_branch().startswith(SYNC_BRANCH))
    items = component_items(changed) if netted else []
    guarded = protected(staged)
    if not items and not guarded:
        return 0
    beyond = slipped_into_merge(sorted(set(items) | set(guarded)))
    if beyond is None:
        refused = 0
        if items:
            print("BLOCKED the commit message check could not compute git's own merge of HEAD and MERGE_HEAD (`git "
                  "merge-tree --write-tree`, git 2.38 or later), so it cannot tell whether a component item of this "
                  "merge (" + ", ".join(items) + ") was edited beyond it. A check that cannot run does not pass: "
                  "update git to 2.38 or later (`git --version` shows it), then commit again. FAIL")
            refused = 1
        return max(refused, protected_net(guarded, body, "; git's own merge could not be computed, so every "
                                          "protected file of this merge counts"))
    refused = 0
    slipped = [path for path in items if path in beyond]
    if slipped:
        print(ROUTE.format(paths=", ".join(slipped) + "; in a merge: edited beyond git's own merge of the two sides, "
                           "and not a conflict there"))
        refused = 1
    return max(refused, protected_net([path for path in guarded if path in beyond], body,
                                      "; in a merge: edited beyond git's own merge of the two sides"))


def guard_kind(path):
    """Which kind of guard file a path is (letter case ignored), or '' when it is none."""
    low = path.lower()
    if low in (".claude/settings.json", ".claude/settings.local.json") or (
            low.startswith("library/settings/") and low.endswith(".json")):
        return "settings"
    if low == ".pre-commit-config.yaml" or fnmatch.fnmatchcase(low, "library/hooks/pre-commit*/*"):
        return "pre-commit"
    if fnmatch.fnmatchcase(low, ".github/workflows/*") or fnmatch.fnmatchcase(low, "library/checks/workflow-*/*"):
        return "workflow"
    if low == ".gitleaksignore" or fnmatch.fnmatchcase(low, "library/repository-files/gitleaksignore*"):
        return "secret-scan"
    return ""


def is_guard_code(path):
    """True for a check or hook file (letter case ignored); `__pycache__` and pages are not code."""
    low = path.lower()
    return (low.endswith(".py") and "__pycache__" not in low
            and any(fnmatch.fnmatchcase(low, name) for name in ("scripts/check_*", ".claude/hooks/*",
                                                                "library/checks/*", "library/hooks/*")))


def settings_entries(text):
    """(what must stay, what must not grow) in a settings file's text; None when it is not valid JSON."""
    try:
        data = json.loads(text)
        allowed = data.get("permissions", {})
        keep = {f"deny entry {entry}" for entry in allowed.get("deny", [])}
        keep |= {f"ask entry {entry}" for entry in allowed.get("ask", [])}
        keep |= {f"{event} hook {group.get('matcher', '')} {hook.get('command', '')}"
                 for event, groups in data.get("hooks", {}).items() for group in groups for hook in group.get("hooks", [])}
        grow = {f"allow entry {entry}" for entry in allowed.get("allow", [])}
        grow |= {f"additional directory {entry}" for entry in allowed.get("additionalDirectories", [])}
        for key, entries in data.get("autoMode", {}).items():
            if key in ("allow", "environment"):
                grow |= {f"Auto mode {key} {entry}" for entry in entries if entry != "$defaults"}
            elif isinstance(entries, list):
                keep |= {f"Auto mode {key} {entry}" for entry in entries if entry != "$defaults"}
    except (ValueError, AttributeError, TypeError):
        return None
    if allowed.get("defaultMode"):
        grow.add(f"defaultMode {allowed['defaultMode']}")
    if data.get("disableAllHooks"):
        grow.add("disableAllHooks")
    return keep, grow


def guard_entries(kind, text):
    """(what must stay, what must not grow) in a guard file's text, by its kind; None when it cannot be read."""
    if kind == "settings":
        return settings_entries(text)
    if kind == "pre-commit":
        return {f"pre-commit hook {name}" for name in re.findall(r"^\s*- id:\s*(\S+)", text, re.M)}, set()
    if kind == "workflow":
        return {f"workflow step {name.strip()}" for name in re.findall(r"^\s*- name:\s*(.+)$", text, re.M)}, set()
    return set(), {f"secret-scan exception {line.strip()}" for line in text.splitlines()
                   if line.strip() and not line.startswith("#")}


def blob(spec):
    """The text git shows for spec (`HEAD:<path>` or `:<path>`), or None when git shows none."""
    try:
        done = subprocess.run(["git", "show", spec], capture_output=True, text=True, encoding="utf-8",
                              errors="replace")
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None


def has_head():
    """True when the repository has a HEAD commit."""
    try:
        return subprocess.run(["git", "rev-parse", "-q", "--verify", "HEAD"], capture_output=True).returncode == 0
    except OSError:
        return False


def weakened(staged, base="HEAD"):
    """What this commit weakens in the ways a tool can read, each named in one short line, against `base`."""
    found, before, after = set(), collections.Counter(), collections.Counter()
    first_copy = not has_head() or current_branch().startswith(SYNC_BRANCH)
    for path in staged:
        old, new = blob(f"{base}:{path}"), blob(f":{path}")
        if is_guard_code(path):
            name = os.path.basename(path).lower()
            before[name] += old is not None
            after[name] += new is not None
        kind = guard_kind(path)
        if not kind:
            continue
        was = guard_entries(kind, old) if old is not None else (set(), set())
        now = guard_entries(kind, new) if new is not None else (set(), set())
        if now is None:  # a working file broken: it may guard nothing now, and the check cannot read it
            if old is not None and was is not None:
                found.add(f"{path} is not valid JSON")
            continue
        was = was or (set(), set())
        found |= {f"{entry} in {path}" for entry in was[0] - now[0]}
        if not (old is None and first_copy and not path.lower().startswith("library/")):
            found |= {f"{entry} in {path}" for entry in now[1] - was[1]}
    found |= {f"the file {name}" for name in before if after[name] < before[name]}
    return sorted(found)


def weaker_refused(items, body):
    """A readable weakening without an `Owner-yes-weaker:` line holding his own words for it is refused (1); 0 to pass."""
    if not items:
        return 0
    general = [one.lower() for one in OWNER_YES_WORDS.findall(body)]
    for words in OWNER_YES_WEAKER.findall(body):
        low = words.lower()
        if low not in general and not any(mark in low for mark in GENERAL_YES):
            return 0
    shown = "; ".join(item if len(item) < 120 else item[:117] + "..." for item in items)
    print(f"this commit weakens a guard ({shown}). The standing yes and a job's yes line do not cover that (guardrail "
          "6, decision 0033). Ask the owner; once he has typed his yes naming this change, add a line "
          "Owner-yes-weaker: \"<his words>\" beside Owner-yes:. That line holds other words than Owner-yes: and none "
          f"of the general yes's marks ({', '.join(GENERAL_YES)}): quote the standing yes in Owner-yes: and his words for "
          "this change here, and if his words hold a mark, ask him to retype them, never alter them. An entry that is "
          "only moved, edited or renamed counts too, since a tool cannot show it is no weaker. FAIL")
    return 1


def weaker_net(staged, body):
    """The standing yes's limit a tool can read, on an ordinary commit."""
    return weaker_refused(weakened([path for path in staged if guard_kind(path) or is_guard_code(path)]), body)


def merge_weaker_net(body):
    """The same limit during a merge of one branch: only on the guard files edited beyond git's own merge, against that
    merge. When git cannot compute it, on every guard file the merge stages, against HEAD."""
    staged = staged_files() or []
    guards = [path for path in staged if guard_kind(path) or is_guard_code(path)]
    if not guards:
        return 0
    merged = own_merge()
    beyond = slipped_into_merge(guards) if merged else None
    if beyond is None:
        return weaker_refused(weakened(guards), body)
    return weaker_refused(weakened(beyond, merged[0]), body)


def main(argv):
    if not argv:
        return 0
    text = open(argv[0], encoding="utf-8").read()
    lines = [line for line in text.split("\n") if not line.startswith("#")]
    subject = lines[0] if lines else ""
    if not by_agent() and not re.search(r"^Made-by: (agent|job)\b", text, re.M):
        return 0
    # The kind refusal runs first, in every state: a merge or a revert must not stage `kind: system` either.
    refused = kind_net()
    body = "\n".join(lines)
    state = merge_state()
    if state == "merge":
        return max(refused, merge_net(body), merge_weaker_net(body))
    if state == "other":
        staged = staged_files()
        if staged is None:
            return unreadable("of this revert or merge ")
        return max(refused, component_net(staged), protected_net(staged, body), weaker_net(staged, body))
    if not SUBJECT.match(subject):
        print(f"NOTICE subject '{subject}' is not in the form type(scope): summary, type one of {TYPES}")
    if not TRAILER.search(body):
        print("NOTICE no 'Made-by: agent | program <tool>' line")
    if not trailers_in_order(lines):
        print("NOTICE the trailers are out of order; keep Owner-yes:, Owner-yes-weaker:, Made-by:, then any Co-authored-by:")
    staged = staged_files()
    if staged is None:
        return unreadable("")
    return max(refused, component_net(staged), protected_net(staged, body), weaker_net(staged, body))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
