#!/usr/bin/env python3
# generated from system: edit there
"""The reachability check: every Markdown page in the library's folders is reachable from the top index by links, top
to bottom. Reports only: it prints NOTICE lines and always exits 0.

Rules written as text get skipped, rules built into templates and checks do not (the talk of 2026-10-21, P219): every
page carries a parent link and its folder's index lists it, so a reader, or a retrieval tool, can walk from `README.md` to
any page. This check walks the links breadth first from `README.md` at the root of `system`: Markdown links
`[text](path)` and reference links `[label]: path`, relative to the page that holds them; a link to a folder means
its `README.md`; an anchor (`#...`) and an outside address are ignored. The walk passes through any Markdown page in
the repository, but it reports only the pages under `docs/`, `processes/`, `library/`, `blueprints/`, `manifest/`
and `registries/` that it never reached.

Usage: python3 scripts/check_reach.py [<root>]
Standard library only.
"""
import os
import re
import sys
from collections import deque
from urllib.parse import unquote

SCOPE = ("docs", "processes", "library", "blueprints", "manifest", "registries")
SKIP = {".git", "node_modules", "__pycache__", ".venv"}
INLINE = re.compile(r"\[(?:[^\]\[]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REFERENCE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+.*)?$", re.M)
FENCE = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)


def notice(text):
    print("NOTICE: " + text)


def links(text):
    text = FENCE.sub("", text)
    text = re.sub(r"`[^`\n]*`", "", text)
    return INLINE.findall(text) + REFERENCE.findall(text)


def resolve(root, page, target):
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("//"):
        return None
    base = root if target.startswith("/") else os.path.dirname(page)
    full = os.path.normpath(os.path.join(base, target.lstrip("/")))
    if os.path.isdir(full):
        full = os.path.join(full, "README.md")
    if not full.lower().endswith(".md") or not os.path.isfile(full):
        return None
    if os.path.relpath(full, root).startswith(".."):
        return None
    return full


def in_scope(root):
    pages = set()
    for top in SCOPE:
        for folder, folders, files in os.walk(os.path.join(root, top)):
            folders[:] = sorted(f for f in folders if f not in SKIP)
            pages.update(os.path.normpath(os.path.join(folder, f)) for f in files if f.lower().endswith(".md"))
    return pages


def main(argv):
    root = os.path.abspath(argv[0]) if argv else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    start = os.path.join(root, "README.md")
    wanted = in_scope(root)
    if not os.path.isfile(start):
        notice("README.md is missing at the root; nothing is reachable")
        return 0
    reached, queue = {os.path.normpath(start)}, deque([os.path.normpath(start)])
    while queue:
        page = queue.popleft()
        try:
            with open(page, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError:
            continue
        for target in links(text):
            full = resolve(root, page, target)
            if full and os.path.normpath(full) not in reached:
                reached.add(os.path.normpath(full))
                queue.append(os.path.normpath(full))
    missing = sorted(wanted - reached)
    for page in missing:
        notice("not reachable from README.md by links: " + os.path.relpath(page, root).replace("\\", "/"))
    print(f"check_reach: {len(wanted)} page(s) in {', '.join(SCOPE)}; {len(wanted) - len(missing)} reached, "
          f"{len(missing)} not. Report only: nothing blocks.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
