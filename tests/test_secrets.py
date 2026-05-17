"""No real secrets, PII, or API keys should ever be committed."""

from __future__ import annotations

import re
from pathlib import Path


# Patterns adapted from gitleaks / GitHub secret-scanning defaults
SECRET_PATTERNS = [
    # AWS
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    # Stripe live
    (re.compile(r"sk_live_[0-9a-zA-Z]{24,}"), "Stripe live secret key"),
    # GitHub PAT (classic)
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "GitHub classic PAT"),
    # GitHub fine-grained
    (re.compile(r"github_pat_[A-Za-z0-9_]{82}"), "GitHub fine-grained PAT"),
    # OpenAI
    (re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{40,}"), "OpenAI key"),
    # Anthropic
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{32,}"), "Anthropic key"),
    # Slack tokens
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    # Generic JWT
    (re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"), "JWT"),
    # AWS secret access key — high false-positive, only catch with key= prefix
    (re.compile(r"aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*[A-Za-z0-9/+]{40}"), "AWS secret key"),
]

# Files where example/illustrative tokens appear and are clearly fake
ALLOWLIST_SUBSTRINGS = {
    # Common placeholder/example tokens used in docs
    "ghp_xxx", "sk_live_xxx", "ghp_abc", "AKIA_OLD",
    "sk-ant-xxx", "sbp_readonly_xxx",
    # GitHub PAT example used in detection regex literals (we explain the
    # pattern in docs — that's intentional)
    "ghp_[a-zA-Z0-9]{36}",
    "github_pat_[a-zA-Z0-9_]{82}",
    "AKIA[0-9A-Z]{16}",
    "AIza[0-9A-Za-z_-]{35}",
    "sk-[a-zA-Z0-9]{32,}",
    "sk_live_[a-zA-Z0-9]+",
    "sk-ant-[A-Za-z0-9_-]",
    "sk-(?:proj-)?[A-Za-z0-9_-]",
    "sk_live_[0-9a-zA-Z]",
    "ghp_[A-Za-z0-9]",
    "github_pat_[A-Za-z0-9_]",
}


def _line_is_allowlisted(line: str) -> bool:
    return any(s in line for s in ALLOWLIST_SUBSTRINGS)


def test_no_real_secrets_in_authored_markdown(all_md_files):
    hits = []
    for md in all_md_files:
        for i, line in enumerate(md.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if _line_is_allowlisted(line):
                continue
            for pattern, label in SECRET_PATTERNS:
                if pattern.search(line):
                    hits.append(f"{md.name}:{i}: possible {label}: {line.strip()[:120]}")
    assert not hits, "Possible committed secrets:\n" + "\n".join(hits)


def test_no_real_secrets_in_source_code(repo_root: Path):
    """Scan site/, tests/, .github/, and skill .md files."""
    candidate_dirs = [
        repo_root / "site",
        repo_root / "tests",
        repo_root / ".github",
        repo_root / ".claude",
    ]
    hits = []
    for d in candidate_dirs:
        if not d.exists():
            continue
        for f in d.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix in {".pyc"} or "__pycache__" in f.parts:
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if _line_is_allowlisted(line):
                    continue
                for pattern, label in SECRET_PATTERNS:
                    if pattern.search(line):
                        hits.append(f"{f.relative_to(repo_root)}:{i}: possible {label}")
    assert not hits, "Possible committed secrets:\n" + "\n".join(hits)
