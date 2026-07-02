#!/usr/bin/env python3
"""
Update the 'Last refreshed:' date in ALERTS.md to today.

Usage:
    python tools/update-alerts-date.py [--date YYYY-MM-DD]

If --date is not provided, uses today's date from the system.
"""

import sys
import re
from datetime import date
from pathlib import Path
from typing import Optional


def update_alerts_date(date_str: Optional[str] = None) -> bool:
    """
    Update ALERTS.md's 'Last refreshed:' date.

    Args:
        date_str: Optional date in YYYY-MM-DD format. If None, uses today.

    Returns:
        True if file was modified, False otherwise.
    """
    if date_str is None:
        date_str = date.today().isoformat()

    alerts_path = Path(__file__).resolve().parent.parent / "ALERTS.md"

    if not alerts_path.exists():
        print(f"Error: {alerts_path} not found", file=sys.stderr)
        return False

    content = alerts_path.read_text()

    # Pattern: **Last refreshed:** YYYY-MM-DD
    pattern = r"(\*\*Last refreshed:\*\*\s+)\d{4}-\d{2}-\d{2}"
    replacement = rf"\g<1>{date_str}"

    new_content = re.sub(pattern, replacement, content, count=1)

    if new_content == content:
        print(f"No date found or no change needed in {alerts_path}", file=sys.stderr)
        return False

    alerts_path.write_text(new_content)
    print(f"Updated ALERTS.md Last refreshed date to {date_str}")
    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update ALERTS.md Last refreshed date")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")

    args = parser.parse_args()

    success = update_alerts_date(args.date)
    sys.exit(0 if success else 1)
