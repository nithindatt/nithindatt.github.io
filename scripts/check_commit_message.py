#!/usr/bin/env python3
# generated from system: edit there
"""Commit message check: blocks a protected file changed without the owner's yes; reports the subject form and the
Made-by line. Run by git at the commit-msg stage.

Blocks one thing: an agent's or a routine's commit that changes a protected file without the line
`Owner-yes: "<the owner's words>"`, quoting his yes from the session (guardrail 6). The protected files are the ones
only the owner may approve a change to:
  - in the hub and in the control plane (the identity file .agents/repository.yml says `kind: workspace` or
    `kind: system`; `system` added on the owner's correction of 2026-10-21): the HUB list below (workspace's AGENTS.md list,
    and system's AGENTS.md list, which adds its own paths); in `system` it also holds the standing approvals, the blocked paths and
    the library originals of every protected file (2026-10-22);
  - in every other repository: the EVERYWHERE list below (the shared instructions, the secret-scan exceptions, this
    check and the hooks), so a sync from `system` that changes one of them carries the owner's yes too.
The staged files are read with `git diff --cached --name-only --no-renames`, so a deletion counts too, and a file
moved away counts under its old path as well as its new one. Paths are matched without regard to letter case. When
git cannot list the staged files, the check prints `BLOCKED ...` and refuses: a check that cannot run does not pass.

Reports only (prints a NOTICE and passes, because format is not harm): a subject that is not in the form
`type(scope): summary` (or `type: summary`), and a missing `Made-by: agent | program <tool>` line (or `job` or
`owner`).

A commit the owner makes by hand is never checked (the owner's rule, 2026-09-29: freedom, not new blocks). Nor is a
merge or a revert that git itself has in progress (MERGE_HEAD or REVERT_HEAD exists): a merge of main into a work
branch brings changes to protected files that were already approved. A subject that only starts with "Merge" or
"Revert" earns nothing: such a commit is checked like any other.
A commit counts as an agent's when an AI tool's shell made it or its message says `Made-by: agent` or
`Made-by: job`. Standard library only.

Usage (by pre-commit): python3 scripts/check_commit_message.py <message file>
"""
import fnmatch
import os
import re
import subprocess
import sys

TYPES = "feat|fix|docs|chore|refactor|test|build|ci|perf|style|revert"
SUBJECT = re.compile(rf"^({TYPES})(\([a-z0-9-]+\))?!?: \S")
TRAILER = re.compile(r"^Made-by: (agent|job|owner) \| program \S+", re.M)
OWNER_YES = re.compile(r"^Owner-yes: [\"“][^\"”]*\S[^\"”]*[\"”]\s*$", re.M)
AGENT_MARKERS = ("AI_AGENT", "CLAUDECODE", "CLAUDE_CODE_REMOTE", "CODEX_SANDBOX")
HUB = ("AGENTS.md", ".agents/instructions/global-instructions.md", "system/permissions.md", ".claude/settings.json",
       ".claude/hooks/*", ".claude/agents/reviewer.md", ".pre-commit-config.yaml", ".gitleaksignore",
       "scripts/check_*.py", "routines/*", ".github/workflows/*", ".mcp.json", ".codex/config.toml",
       "scripts/mcp_github_headers.py",
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
       ".agents/repository.yml")
EVERYWHERE = (".agents/instructions/global-instructions.md", ".gitleaksignore", "scripts/check_commit_message.py",
              ".claude/hooks/*", "scripts/install.py")


def by_agent():
    """True in a shell an AI tool started: it sets one of these names (AI_AGENT and CLAUDECODE seen in Claude Code,
    2026-09-29; CODEX_SANDBOX for Codex is UNVERIFIED). A person's own terminal sets none of them."""
    return any(os.environ.get(name) for name in AGENT_MARKERS)


def staged_files():
    """The paths this commit changes, or None when git cannot say (the check then refuses: it could not run).
    `--no-renames` lists a moved file under both its old and its new path, so a protected file renamed away counts."""
    try:
        out = subprocess.run(["git", "-c", "core.quotePath=false", "diff", "--cached", "--name-only", "--no-renames"],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
    except (subprocess.CalledProcessError, OSError):
        return None
    return [line.strip() for line in out.splitlines() if line.strip()]


def merging():
    """True only while git itself is in the middle of a merge or a revert: it has written MERGE_HEAD or REVERT_HEAD.
    The subject line is never trusted for this, because anyone can start a subject with the word Merge."""
    for ref in ("MERGE_HEAD", "REVERT_HEAD"):
        try:
            if subprocess.run(["git", "rev-parse", "-q", "--verify", ref], capture_output=True).returncode == 0:
                return True
        except OSError:
            return False
    return False


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


def protected(paths):
    """The protected ones among the paths. Letter case is ignored: on Windows a file staged as `Routines/x.md` lands
    in `routines/`."""
    patterns = [pattern.lower() for pattern in (HUB if is_hub() else EVERYWHERE)]
    return [p for p in paths if any(fnmatch.fnmatchcase(p.lower(), pattern) for pattern in patterns)]


def main(argv):
    if not argv:
        return 0
    text = open(argv[0], encoding="utf-8").read()
    lines = [line for line in text.split("\n") if not line.startswith("#")]
    subject = lines[0] if lines else ""
    if not by_agent() and not re.search(r"^Made-by: (agent|job)\b", text, re.M):
        return 0
    if merging():
        return 0
    body = "\n".join(lines)
    if not SUBJECT.match(subject):
        print(f"NOTICE subject '{subject}' is not in the form type(scope): summary, type one of {TYPES}")
    if not TRAILER.search(body):
        print("NOTICE no 'Made-by: agent | program <tool>' line")
    staged = staged_files()
    if staged is None:
        print("BLOCKED the commit message check could not read the staged files from git, so it cannot tell whether "
              "a protected file changes. A check that cannot run does not pass: make `git diff --cached` work here, "
              "then commit again. FAIL")
        return 1
    touched = protected(staged)
    if touched and not OWNER_YES.search(body):
        print("this commit changes a protected file (" + ", ".join(touched) + "), which needs the owner's "
              "yes: add a line Owner-yes: \"<his words from the session>\". Without his yes, ask him first; "
              "after outside material, only his typed yes counts. FAIL")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
