"""Guards for runs.log.md: one heading per sweep, appended, never overwritten.

On 2026-10-20 a sweep wrote its notes and its deferred line over the previous
day's entry instead of adding a `## 2026-10-20` heading, and the next run read
a 10-19 header above 10-20 content. These checks fail the gate on that shape.
"""
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "vibe-security-update"
HEADING = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$", re.M)


def _entries():
    text = (SKILL_DIR / "runs.log.md").read_text(encoding="utf-8")
    dates = HEADING.findall(text)
    parts = HEADING.split(text)[1:]
    return dates, dict(zip(parts[0::2], parts[1::2]))


def test_run_log_headings_are_unique_and_ascending():
    dates, _ = _entries()
    assert dates, "runs.log.md has no `## YYYY-MM-DD` entries"
    assert len(dates) == len(set(dates)), f"duplicate run-log headings: {dates}"
    assert dates == sorted(dates), f"run-log headings are not in ascending order: {dates}"


def test_every_run_log_entry_has_one_yaml_block_and_one_notes_paragraph():
    _, bodies = _entries()
    for date, body in bodies.items():
        assert body.count("```yaml") == 1, f"{date}: expected exactly one ```yaml block"
        assert body.count("**Notes.**") == 1, f"{date}: expected exactly one **Notes.** paragraph"


def test_newest_run_log_entry_matches_alerts_refresh_date():
    dates, _ = _entries()
    alerts = (Path(__file__).resolve().parent.parent / "ALERTS.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*Last refreshed:\*\* (\d{4}-\d{2}-\d{2})", alerts)
    assert m, "ALERTS.md has no Last refreshed marker"
    assert dates[-1] == m.group(1), (
        f"newest run-log heading {dates[-1]} != ALERTS.md Last refreshed {m.group(1)}: "
        "a sweep must append its own `## YYYY-MM-DD` entry, never edit the previous one"
    )
