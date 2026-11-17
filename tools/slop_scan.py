#!/usr/bin/env python3
"""Flag AI-slop prose in advisories and ALERTS.md.

    python tools/slop_scan.py                  # files changed against origin/main
    python tools/slop_scan.py advisories/x.md  # named files
    python tools/slop_scan.py --all            # whole corpus

Two kinds of finding:
  pattern  a line of tools/slop_patterns.tsv matched. Exit status 1.
  style    a sentence over MAX_WORDS words, an em-dash, or a semicolon joining
           clauses. Reported, exit status unchanged, because older files carry
           thousands. tests/test_prose.py enforces style on new advisories only.

The pattern list is meant to grow: when review finds a slop sentence this
missed, add a line to tools/slop_patterns.tsv in the same PR.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PATTERNS_FILE = REPO / "tools" / "slop_patterns.tsv"
MAX_WORDS = 35

_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
_FENCE = re.compile(r"^```.*?^```", re.S | re.M)
_LINK = re.compile(r"!?\[[^\]]*\]\([^)]*\)")
_CODE = re.compile(r"`[^`]*`")
_QUOTE = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”")
_SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9*`\[])")


def load_patterns() -> list[tuple[str, re.Pattern[str], str]]:
    out = []
    for line in PATTERNS_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, regex, fix = line.split("\t")
        out.append((name, re.compile(regex, re.I), fix))
    return out


def prose_lines(text: str):
    """Yield (line_number, cleaned_text) for prose lines.

    Skips frontmatter, fenced code, headings, tables and Sources entries'
    link text. Strips links, inline code and quoted strings."""
    body_start = 0
    fm = _FRONTMATTER.match(text)
    if fm:
        body_start = text[: fm.end()].count("\n")
        text = "\n" * body_start + text[fm.end():]
    text = _FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    for no, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith(("#", "|", "<!--")):
            continue
        s = _LINK.sub("LINK", s)
        s = _CODE.sub("CODE", s)
        s = _QUOTE.sub("QUOTE", s)
        yield no, s


def scan_text(text: str, patterns=None):
    patterns = patterns if patterns is not None else load_patterns()
    pattern_hits, style_hits = [], []
    for no, s in prose_lines(text):
        for name, rx, fix in patterns:
            m = rx.search(s)
            if m:
                pattern_hits.append((no, name, m.group(0), fix))
        if " — " in s or " -- " in s:
            style_hits.append((no, "em-dash", "use a full stop or a comma"))
        if re.search(r"[a-z)]; [a-z]", s):
            style_hits.append((no, "semicolon", "split into two sentences"))
        for sent in _SENTENCE.split(s.lstrip("-*> 0123456789.")):
            n = len(sent.split())
            if n > MAX_WORDS:
                style_hits.append((no, f"long-sentence ({n} words)", "one idea per sentence"))
    return pattern_hits, style_hits


def changed_files() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=AM", "origin/main...HEAD"],
            cwd=REPO, capture_output=True, text=True, check=True,
        ).stdout.split()
        out += subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=AM", "HEAD"],
            cwd=REPO, capture_output=True, text=True, check=True,
        ).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    keep = {p for p in out if p == "ALERTS.md" or (p.startswith("advisories/") and p.endswith(".md"))}
    return [REPO / p for p in sorted(keep) if (REPO / p).exists()]


def main(argv: list[str]) -> int:
    if "--all" in argv:
        files = sorted((REPO / "advisories").glob("*.md")) + [REPO / "ALERTS.md"]
    elif argv:
        files = [Path(a).resolve() for a in argv]
    else:
        files = changed_files()
    if not files:
        print("slop_scan: no files to check")
        return 0
    patterns = load_patterns()
    total = 0
    for f in files:
        p_hits, s_hits = scan_text(f.read_text(encoding="utf-8"), patterns)
        rel = f.relative_to(REPO) if f.is_relative_to(REPO) else f
        for no, name, match, fix in p_hits:
            print(f"{rel}:{no}: [{name}] '{match}' -> {fix}")
        if "--all" not in argv:
            for no, name, fix in s_hits:
                print(f"{rel}:{no}: style [{name}] -> {fix}")
        total += len(p_hits)
    print(f"slop_scan: {total} pattern hit(s) in {len(files)} file(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
