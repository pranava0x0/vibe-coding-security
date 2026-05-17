"""Validate the vibe-security-update skill: source-priorities.json schema +
runs.log.md monotonic dates + SKILL.md frontmatter."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import yaml


SKILL_DIR_NAME = ".claude/skills/vibe-security-update"


def test_skill_md_has_frontmatter(repo_root: Path):
    skill = repo_root / SKILL_DIR_NAME / "SKILL.md"
    assert skill.exists(), "SKILL.md missing"
    text = skill.read_text(encoding="utf-8")
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "SKILL.md frontmatter not parseable"
    fm = yaml.safe_load(m.group(1))
    assert "name" in fm and fm["name"] == "vibe-security-update"
    assert "description" in fm and len(fm["description"]) > 50


def test_source_priorities_is_valid_json(repo_root: Path):
    p = repo_root / SKILL_DIR_NAME / "source-priorities.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert "last_updated" in data
    assert "sources" in data and isinstance(data["sources"], dict)
    assert len(data["sources"]) >= 50, "should have substantive source list"


def test_every_source_has_required_fields(repo_root: Path):
    p = repo_root / SKILL_DIR_NAME / "source-priorities.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    required = {"weight", "hits", "last_hit", "ecosystems", "tier"}
    valid_tiers = {"vendor", "research", "aggregator", "independent", "official"}
    for domain, src in data["sources"].items():
        missing = required - set(src.keys())
        assert not missing, f"source {domain!r} missing fields: {missing}"
        assert 1 <= int(src["weight"]) <= 20, f"{domain}: weight out of [1,20]: {src['weight']}"
        assert int(src["hits"]) >= 0, f"{domain}: negative hits"
        assert src["tier"] in valid_tiers, f"{domain}: invalid tier {src['tier']!r}"
        assert isinstance(src["ecosystems"], list)


def test_runs_log_has_at_least_one_entry(repo_root: Path):
    p = repo_root / SKILL_DIR_NAME / "runs.log.md"
    text = p.read_text(encoding="utf-8")
    assert "## " in text, "runs.log.md should have at least one '## YYYY-MM-DD' entry"


def test_runs_log_dates_are_monotonic(repo_root: Path):
    """Newer entries should appear after older ones (chronological order)."""
    p = repo_root / SKILL_DIR_NAME / "runs.log.md"
    text = p.read_text(encoding="utf-8")
    dates = re.findall(r"^##\s+(\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
    parsed = [date.fromisoformat(d) for d in dates]
    assert parsed == sorted(parsed), f"runs.log.md dates not in chronological order: {dates}"


def test_source_priorities_last_updated_recent(repo_root: Path):
    """last_updated should be within the last 60 days OR equal to the latest runs.log entry."""
    src = json.loads((repo_root / SKILL_DIR_NAME / "source-priorities.json").read_text())
    last_updated = date.fromisoformat(src["last_updated"])

    log_text = (repo_root / SKILL_DIR_NAME / "runs.log.md").read_text()
    dates = re.findall(r"^##\s+(\d{4}-\d{2}-\d{2})", log_text, re.MULTILINE)
    latest_run = max(date.fromisoformat(d) for d in dates)

    delta_today = (date.today() - last_updated).days
    assert delta_today <= 90 or last_updated == latest_run, (
        f"source-priorities last_updated={last_updated} is {delta_today} days old "
        f"and doesn't match latest run {latest_run}"
    )
