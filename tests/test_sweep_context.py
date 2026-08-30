"""Guards on the sweep's per-run context cost and its generated state files.

Why this file exists
--------------------
Step 0 of the `vibe-security-update` skill used to mandate reading five files
totalling ~345K tokens — more than fits in a context window. It therefore
truncated silently on every run, which is how a documented workaround for a
recurring blocker sat unread in the middle of `runs.log.md` for five days, and
how a sweep once ran against a checkout 15 sweeps stale.

The cost was not one bad file; it was monotonic growth (~3,560 tokens/day across
the five) with nothing asserting a ceiling. These tests are that ceiling.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "vibe-security-update"

# Rough but stable: ~4 bytes/token for English prose and markdown. Precise
# tokenisation isn't the point — catching a 10x regression is.
BYTES_PER_TOKEN = 4

# Everything Step 0 tells a sweep to read, and what it may cost. The budget is
# ~2.5x current usage: generous enough that normal growth doesn't cause noise,
# tight enough that a return to reading whole indexes fails immediately.
STEP0_READS = [
    "SKILL.md",
    "LEARNINGS.md",
    "runs.log.md",
    "source-priorities.top.json",
    "references/queries.md",
]
STEP0_TOKEN_BUDGET = 80_000

# Files that exist to be grepped, never read into context. No size limit — they
# are allowed to grow forever, which is exactly why nothing may read them whole.
GREP_ONLY = [
    "advisory-index.jsonl",
    "source-priorities.json",
    "runs.archive.md",
]

MAX_LIVE_RUN_ENTRIES = 7


def _tokens(path: Path) -> int:
    return path.stat().st_size // BYTES_PER_TOKEN


def test_step0_files_all_exist():
    missing = [name for name in STEP0_READS if not (SKILL_DIR / name).exists()]
    assert not missing, f"Step 0 tells the sweep to read files that don't exist: {missing}"


def test_step0_context_within_budget():
    """The whole Step 0 preamble, not any single file, is the thing that blew up."""
    sizes = {name: _tokens(SKILL_DIR / name) for name in STEP0_READS}
    total = sum(sizes.values())
    breakdown = "\n".join(f"    {v:>7,} tok  {k}" for k, v in sorted(sizes.items(), key=lambda kv: -kv[1]))
    assert total <= STEP0_TOKEN_BUDGET, (
        f"Step 0 reads ~{total:,} tokens, over the {STEP0_TOKEN_BUDGET:,} budget:\n{breakdown}\n"
        "Move the growth into a grep-only file (see GREP_ONLY) or distil it into "
        "LEARNINGS.md. Do not raise this budget — that is the loop this test exists to break."
    )


@pytest.mark.parametrize("name", GREP_ONLY)
def test_grep_only_files_are_not_referenced_as_reads(name):
    """A grep-only file must never be listed among Step 0's reads."""
    assert name not in STEP0_READS


def test_runs_log_is_rotated():
    """`runs.log.md` keeps a small live window; older entries go to the archive."""
    log = (SKILL_DIR / "runs.log.md").read_text(encoding="utf-8")
    entries = [ln for ln in log.splitlines() if ln.startswith("## 20")]
    assert len(entries) <= MAX_LIVE_RUN_ENTRIES, (
        f"runs.log.md holds {len(entries)} entries (max {MAX_LIVE_RUN_ENTRIES}). "
        "Rotate the oldest into runs.archive.md — see SKILL.md Step 5."
    )
    assert (SKILL_DIR / "runs.archive.md").exists(), "archive missing; rotation would lose history"


def test_generated_state_is_current():
    """advisory-index.jsonl / source-priorities.top.json must match their sources.

    A stale index silently answers "not tracked" for something that is, which
    is exactly the duplicate-advisory failure mode this index was meant to end."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "sweep_context.py"), "--check"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"generated sweep state is stale:\n{result.stderr}\n"
        "Run `python3 tools/sweep_context.py` and commit the result."
    )


def test_advisory_index_covers_every_advisory():
    index_path = SKILL_DIR / "advisory-index.jsonl"
    indexed = {json.loads(line)["id"] for line in index_path.read_text(encoding="utf-8").splitlines() if line.strip()}
    on_disk = {p.stem for p in (REPO_ROOT / "advisories").glob("*.md") if p.name != "README.md"}
    missing = on_disk - indexed
    assert not missing, f"advisories absent from the index (triage would call them new): {sorted(missing)[:10]}"


def test_technique_detail_is_out_of_the_delegable_query_file():
    """`references/queries.md` is the one file that may be delegated.

    It must stay bare query strings. The technique-dense material belongs in
    triage-patterns.md — sending it to a fresh agent as a task list is what
    tripped the cyber-safeguards classifier eight times in August 2026."""
    queries = (SKILL_DIR / "references" / "queries.md").read_text(encoding="utf-8")
    assert (SKILL_DIR / "references" / "triage-patterns.md").exists()
    # A generous ceiling: bare queries + rotation lists, not annotated bullets.
    assert _tokens(SKILL_DIR / "references" / "queries.md") <= 4_000, (
        "queries.md has grown past a bare query list — annotations belong in "
        "triage-patterns.md, which is never delegated."
    )
    for banned in ("## Named attack classes", "Query notes"):
        assert banned not in queries, f"triage material leaked into the delegable file: {banned!r}"
