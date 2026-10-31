#!/usr/bin/env python3
# generated from system: edit there
"""The views check: only the repository mirror writes `views/`. Run by git at the commit-msg stage.

A view is a read-only copy of shared data, at `views/<owner>/<path>`, written by `system`'s repository mirror
(`mirror.py --repositories`, decision 0029 in `system`). A view is never edited where it lands: its original is changed
in the repository that owns it (`views/sources.csv` names it), and the mirror writes the view again. So an agent's or a
routine's commit that adds, changes, removes or renames anything under `views/` is refused (exit 1) unless it is the
mirror's own commit, all three of: its subject starts with `chore(mirror): `; its message holds the line
`Made-by: job | program mirror`; and the commit runs inside the mirror's run, which sets the environment marker
`NEXEGO_MIRROR_RUN` to the branch it commits on (`chore/mirror-<date>-<time>`), the branch the commit is made on. So
`git commit --amend --no-edit` on the mirror's branch, which keeps the message, is refused outside the run.

This check stops honest mistakes, not deliberate ones: the marker is not a secret, and anyone can set the marker by
hand. Nothing a session leaves in a view lasts either way: the mirror's next run rewrites a view that differs from
its original.

Let through: a commit that touches nothing under `views/`; a merge or a revert git itself is making (it has written
MERGE_HEAD or REVERT_HEAD), as the commit-message check lets one through, so that bringing `main` into a branch never
stops on views the mirror wrote there (an edit staged during such a merge is not caught: the pull request's review is
the guard then); and a commit the owner makes by hand, which is never blocked (the owner's rule of 2026-09-29:
freedom, not new blocks, kept by the commit-message check too): it gets a NOTICE when it changes `views/` or when
git cannot list its staged files, and passes. A commit counts as an agent's or a routine's as in the commit-message
check: an AI tool's shell made it, or its message says `Made-by: agent` or `Made-by: job`. Paths are matched without
regard to letter case, read NUL-separated (`-z`, so no name is quoted or split), and a moved file counts under its
old path and its new one. When git cannot list the staged files (a path that is not UTF-8 counts as that), an agent's
or a routine's commit is refused: the check could not run. Standard library only.

Usage: python3 scripts/check_views.py <commit message file>   (the commit-msg hook passes the file)
"""
import os
import re
import subprocess
import sys

VIEWS = "views/"
MIRROR_SUBJECT = "chore(mirror): "
MIRROR_TRAILER = re.compile(r"^Made-by: job \| program mirror\s*$", re.M)
MIRROR_RUN = "NEXEGO_MIRROR_RUN"  # set by mirror.py for its own commit only, to the branch it commits on
MIRROR_BRANCH = "chore/mirror-"
AGENT_TRAILER = re.compile(r"^Made-by: (agent|job)\b", re.M)
AGENT_MARKERS = ("AI_AGENT", "CLAUDECODE", "CLAUDE_CODE_REMOTE", "CODEX_SANDBOX")


def staged_files():
    """The paths this commit changes, a moved file under both its paths, or None when git cannot say."""
    try:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--no-renames", "-z"],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
    except (subprocess.CalledProcessError, OSError, UnicodeDecodeError):
        return None
    return [path for path in out.split("\0") if path]


def merging():
    """True only while git itself is in the middle of a merge or a revert: it has written MERGE_HEAD or REVERT_HEAD."""
    for ref in ("MERGE_HEAD", "REVERT_HEAD"):
        try:
            if subprocess.run(["git", "rev-parse", "-q", "--verify", ref], capture_output=True).returncode == 0:
                return True
        except OSError:
            return False
    return False


def current_branch():
    """The branch the commit is made on, or "" (a detached HEAD, or git cannot say)."""
    try:
        return subprocess.run(["git", "symbolic-ref", "-q", "--short", "HEAD"], capture_output=True, text=True,
                              encoding="utf-8").stdout.strip()
    except (OSError, UnicodeDecodeError):
        return ""


def in_mirror_run():
    """True when the mirror's run set its marker to the branch this commit is made on, a mirror branch."""
    marker = os.environ.get(MIRROR_RUN, "")
    return marker.startswith(MIRROR_BRANCH) and marker == current_branch()


def message_text(path):
    """The commit message without git's comment lines."""
    with open(path, encoding="utf-8") as handle:
        return "\n".join(line for line in handle.read().split("\n") if not line.startswith("#")).strip("\n")


def main(argv):
    if not argv:
        print("check_views: no commit message file was given; run it as a commit-msg hook")
        return 0
    text = message_text(argv[0])
    by_agent = any(os.environ.get(name) for name in AGENT_MARKERS) or bool(AGENT_TRAILER.search(text))
    paths = staged_files()
    if paths is None:
        if not by_agent:
            print("NOTICE check_views: git could not list the staged files; the owner's own commit passes")
            return 0
        print("FAIL check_views: git could not list the staged files, so the check could not run")
        return 1
    touched = [p for p in paths if p.replace("\\", "/").lower().startswith(VIEWS)]
    if not touched or merging():
        return 0
    if text.startswith(MIRROR_SUBJECT) and MIRROR_TRAILER.search(text) and in_mirror_run():
        return 0
    shown = ", ".join(touched[:5]) + (f" and {len(touched) - 5} more" if len(touched) > 5 else "")
    if not by_agent:
        print(f"NOTICE check_views: this commit changes views/ ({shown}), which only the repository mirror writes; "
              "the owner's own commit passes, and the mirror's next run writes each view again from its original")
        return 0
    print(f"FAIL check_views: this commit changes views/ ({shown}), which only the repository mirror writes, inside "
          "its own run. A view is a read-only copy: change its original in the repository that owns it "
          "(views/sources.csv names it), and the mirror writes the view again at system's review cycle.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
