#!/usr/bin/env python3
"""Check external source links in advisories for rot (404/410/DNS-fail), and
look up a Wayback snapshot for each dead one.

Polite by design (CLAUDE.md network ethics): informative User-Agent, >=1.8s
delay between requests, single 429 backoff, generous timeout. A 401/403/405 is
treated as ALIVE (security sites routinely bot-block HEAD/GET) — only 404/410
and connection/DNS failures count as rot, to avoid false positives.

Usage:
    python tools/check-external-links.py advisories/2025-*.md
"""
from __future__ import annotations

import re
import sys
import time
import json
import glob
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

UA = "vibe-coding-security-linkcheck/1.0 (+https://github.com/pranava0x0/vibe-coding-security)"
DELAY = 1.8           # seconds between any two outbound requests
TIMEOUT = 20
URL_RE = re.compile(r"https?://[^\s)]+")
ALIVE_CODES = {200, 201, 202, 203, 204, 206, 301, 302, 303, 307, 308, 401, 403, 405, 429}


def extract(paths: list[Path]) -> dict[str, list[str]]:
    """Return {url: [advisory filenames that cite it]}."""
    out: dict[str, list[str]] = {}
    for p in paths:
        for m in URL_RE.findall(p.read_text(encoding="utf-8")):
            url = m.rstrip(".,);:'\"]>")
            out.setdefault(url, [])
            if p.name not in out[url]:
                out[url].append(p.name)
    return out


def status(url: str) -> tuple[str, int | str]:
    """('ALIVE'|'DEAD'|'ERROR', code-or-reason)."""
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
            code = urllib.request.urlopen(req, timeout=TIMEOUT).status
            if code == 405:  # HEAD not allowed → try GET
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                code = urllib.request.urlopen(req, timeout=TIMEOUT).status
            return ("ALIVE" if code in ALIVE_CODES else "DEAD", code)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(8)
                continue
            return ("ALIVE" if e.code in ALIVE_CODES else "DEAD", e.code)
        except Exception as e:  # DNS, timeout, conn reset, bad cert...
            return ("ERROR", type(e).__name__)
    return ("ERROR", "retry-exhausted")


def wayback(url: str) -> str | None:
    try:
        api = f"https://archive.org/wayback/available?url={urllib.parse.quote(url, safe='')}"
        req = urllib.request.Request(api, headers={"User-Agent": UA})
        data = json.loads(urllib.request.urlopen(req, timeout=TIMEOUT).read())
        snap = data.get("archived_snapshots", {}).get("closest", {})
        return snap.get("url") if snap.get("available") else None
    except Exception:
        return None


def main() -> int:
    args = sys.argv[1:] or ["advisories/2025-*.md"]
    paths = sorted({Path(f) for pat in args for f in glob.glob(pat)})
    if not paths:
        print("no files matched", file=sys.stderr)
        return 2
    links = extract(paths)
    print(f"Checking {len(links)} unique URLs across {len(paths)} files...\n", flush=True)
    dead: list[dict] = []
    for i, url in enumerate(sorted(links), 1):
        kind, code = status(url)
        if kind != "ALIVE":
            wb = wayback(url)
            time.sleep(DELAY)
            dead.append({"url": url, "kind": kind, "code": code, "in": links[url], "wayback": wb})
            print(f"[{kind} {code}] {url}\n   cited by: {', '.join(links[url])}\n   wayback: {wb or 'NONE FOUND'}\n", flush=True)
        time.sleep(DELAY)
    print(f"\n=== {len(dead)} dead/error of {len(links)} checked ===")
    Path("tools/dead-links.json").write_text(json.dumps(dead, indent=2))
    print("wrote tools/dead-links.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
