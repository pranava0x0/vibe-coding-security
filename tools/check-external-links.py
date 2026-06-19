#!/usr/bin/env python3
"""Check external source links in advisories for rot, and look up a Wayback
snapshot for each dead one. Usable as a gate.

Polite by design (CLAUDE.md network ethics): informative User-Agent, >=1.8s
delay between requests, single 429 backoff, generous timeout. A 401/403/405 is
treated as ALIVE (security sites routinely bot-block HEAD/GET) — only 404/410/451
and connection/DNS failures are flagged, to avoid false positives.

Non-citation URLs (localhost, RFC1918/link-local, *.test/*.local/*.invalid,
example.*, and obvious attacker/placeholder hosts) are SKIPPED — they appear in
PoC/"Am I affected?" snippets, not in `## Sources`, and must never be checked or
archived.

Exit codes (so it can gate a PR / pre-commit on touched advisory files):
    0  no rotted citations (everything ALIVE, SKIPPED, or transiently ERRORed)
    1  at least one citation is DEAD (404/410/451) with NO Wayback snapshot
    2  bad invocation (no files matched)
Transient ERRORs (DNS/timeout/reset) are reported but do NOT fail the gate.

Usage:
    python tools/check-external-links.py advisories/2025-*.md
    python tools/check-external-links.py advisories/2026-04-litellm-sql-injection.md
"""
from __future__ import annotations

import re
import sys
import time
import json
import glob
import ipaddress
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

UA = "vibe-coding-security-linkcheck/1.0 (+https://github.com/pranava0x0/vibe-coding-security)"
DELAY = 1.8           # seconds between any two outbound requests
TIMEOUT = 20
URL_RE = re.compile(r"https?://[^\s)]+")
ALIVE_CODES = {200, 201, 202, 203, 204, 206, 301, 302, 303, 307, 308, 401, 403, 405, 429}
DEAD_CODES = {404, 410, 451}   # the only codes that fail the gate (with no archive)

# Hosts that are illustrative, not citations — never check or archive these.
IGNORE_EXACT = {"localhost", "example.com", "example.org", "example.net", "0.0.0.0"}
IGNORE_SUFFIX = (".local", ".test", ".invalid", ".example", ".localhost")
IGNORE_SUBSTR = ("attacker", "evil", "victim", "malicious", "example.")  # placeholder demo hosts


def is_ignorable(url: str) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    if not host:
        return True
    if host in IGNORE_EXACT or host.endswith(IGNORE_SUFFIX):
        return True
    if any(s in host for s in IGNORE_SUBSTR):
        return True
    try:  # RFC1918 / loopback / link-local IPs
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        return False


def extract(paths: list[Path]) -> dict[str, list[str]]:
    """Return {url: [advisory filenames that cite it]}, skipping non-citation hosts."""
    out: dict[str, list[str]] = {}
    for p in paths:
        for m in URL_RE.findall(p.read_text(encoding="utf-8")):
            url = m.rstrip(".,);:'\"]>")
            if is_ignorable(url):
                continue
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
    print(f"Checking {len(links)} unique citation URLs across {len(paths)} files...\n", flush=True)
    flagged: list[dict] = []
    gate_failures: list[dict] = []
    for url in sorted(links):
        kind, code = status(url)
        if kind != "ALIVE":
            wb = wayback(url)
            time.sleep(DELAY)
            rec = {"url": url, "kind": kind, "code": code, "in": links[url], "wayback": wb}
            flagged.append(rec)
            gate = kind == "DEAD" and code in DEAD_CODES and not wb
            if gate:
                gate_failures.append(rec)
            tag = "GATE-FAIL" if gate else kind
            print(f"[{tag} {code}] {url}\n   cited by: {', '.join(links[url])}\n   wayback: {wb or 'NONE FOUND'}\n", flush=True)
        time.sleep(DELAY)
    Path("tools/dead-links.json").write_text(json.dumps(flagged, indent=2))
    print(f"=== {len(flagged)} flagged ({len(gate_failures)} gate-failing: dead + no archive) "
          f"of {len(links)} checked → tools/dead-links.json ===")
    if gate_failures:
        print("\nFAIL: dead citations with no Wayback snapshot (fix the URL or drop it):")
        for r in gate_failures:
            print(f"  {r['code']} {r['url']}  [{', '.join(r['in'])}]")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
