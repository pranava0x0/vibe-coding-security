"""Guards for runs.log.md: one heading per sweep, appended, never overwritten.

On 2026-10-20 a sweep wrote its notes and its deferred line over the previous
day's entry instead of adding a `## 2026-10-20` heading, and the next run read
a 10-19 header above 10-20 content. These checks fail the gate on that shape.
"""
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "vibe-security-update"
HEADING = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})", re.M)  # same shape as tests/test_skill.py


def _entries():
    text = (SKILL_DIR / "runs.log.md").read_text(encoding="utf-8")
    dates = HEADING.findall(text)
    parts = HEADING.split(text)[1:]
    return dates, dict(zip(parts[0::2], parts[1::2]))


def test_run_log_headings_are_unique():
    """Ascending order is checked by tests/test_skill.py::test_runs_log_dates_are_monotonic."""
    dates, _ = _entries()
    assert dates, "runs.log.md has no `## YYYY-MM-DD` entries"
    assert len(dates) == len(set(dates)), f"duplicate run-log headings: {dates}"


def test_every_run_log_entry_has_one_yaml_block_and_one_notes_paragraph():
    _, bodies = _entries()
    for date, body in bodies.items():
        assert body.count("```yaml") == 1, f"{date}: expected exactly one ```yaml block"
        assert body.count("**Notes.**") == 1, f"{date}: expected exactly one **Notes.** paragraph"


def test_alerts_refresh_date_is_not_older_than_newest_run_log_entry():
    """A sweep appends its own entry, so the newest heading can never be newer than the
    ALERTS refresh stamp. The stamp may be newer (a targeted correction, or a gate run on a
    later day re-stamping ALERTS) without a new entry."""
    dates, _ = _entries()
    alerts = (Path(__file__).resolve().parent.parent / "ALERTS.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*Last refreshed:\*\* (\d{4}-\d{2}-\d{2})", alerts)
    assert m, "ALERTS.md has no Last refreshed marker"
    assert m.group(1) >= dates[-1], (
        f"newest run-log heading {dates[-1]} is newer than ALERTS.md Last refreshed {m.group(1)}: "
        "a sweep must run update-alerts-date.py and append its own `## YYYY-MM-DD` entry"
    )
