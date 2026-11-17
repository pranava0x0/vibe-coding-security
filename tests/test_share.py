"""Share links: every alert, advisory and section has a direct link that resolves."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "site"))

from build import (  # noqa: E402
    SIDEBAR_MAX_ITEMS,
    Page,
    add_share_links,
    stable_alert_ids,
)


def _alerts_page() -> Page:
    return Page(source_path=REPO_ROOT / "ALERTS.md", output_path=Path("alerts.html"), title="Alerts")


def test_alert_id_is_the_advisory_stem():
    rendered = (
        '<h3 id="2026-11-16-long-title-slug">2026-11-16 — <strong>Title</strong></h3>\n'
        '<p>Body.</p><p>→ <a href="advisories/2026-11-foo.html">x</a></p>\n'
        '<h3 id="second">Second</h3><p>no advisory link</p>'
    )
    out, remap = stable_alert_ids(rendered)
    assert '<h3 id="2026-11-foo">' in out
    assert '<h3 id="second">' in out
    assert remap == {"2026-11-16-long-title-slug": "2026-11-foo"}


def test_alert_id_prefers_the_arrow_link_over_earlier_citations():
    rendered = ('<h3 id="x">t</h3><p>See <a href="advisories/2025-01-other.html">o</a>.</p>'
                '<p>→ <a href="advisories/2026-11-own.html">x</a></p>')
    out, _ = stable_alert_ids(rendered)
    assert '<h3 id="2026-11-own">' in out


def test_two_alerts_for_one_advisory_get_distinct_ids():
    block = '<h3 id="{}">t</h3><p><a href="advisories/2026-11-foo.html">x</a></p>'
    out, _ = stable_alert_ids(block.format("a") + block.format("b"))
    assert re.findall(r'<h3 id="([^"]+)">', out) == ["2026-11-foo", "2026-11-foo-2"]


def test_alert_headings_get_a_share_pill_and_sections_get_a_hash():
    out = add_share_links('<h2 id="s">S</h2><h3 id="a">A</h3>', _alerts_page())
    assert '<a class="share" href="#s" aria-label="Copy link to this section" aria-describedby="s">#</a></h2>' in out
    assert '<a class="share" href="#a" aria-label="Share link to this alert" aria-describedby="a">Share</a></h3>' in out


def test_built_alerts_link_every_entry_by_advisory_stem(dist_dir):
    page = (dist_dir / "alerts.html").read_text(encoding="utf-8")
    ids = re.findall(r'<h3 id="([^"]+)">', page)
    assert ids, "no alert headings"
    assert len(ids) == len(set(ids)), "duplicate alert ids"
    for hid in ids:
        assert f'class="share" href="#{hid}"' in page, f"alert {hid} has no share link"
    linked = [hid for hid in ids if (dist_dir / "advisories" / f"{re.sub(r'-[0-9]+$', '', hid)}.html").exists()
              or (dist_dir / "advisories" / f"{hid}.html").exists()]
    # Nearly every alert names its advisory; the id should be that advisory's stem.
    assert len(linked) >= 0.9 * len(ids), f"only {len(linked)}/{len(ids)} alert ids are advisory stems"


def test_toc_links_resolve_on_alerts_page(dist_dir):
    page = (dist_dir / "alerts.html").read_text(encoding="utf-8")
    toc = re.search(r'<aside class="toc".*?</aside>', page, re.DOTALL)
    assert toc
    ids = set(re.findall(r'\sid="([^"]+)"', page))
    for target in re.findall(r'href="#([^"]+)"', toc.group(0)):
        assert target in ids, f"TOC link #{target} has no target"


def test_every_page_has_a_share_action(all_html_files, dist_dir):
    for f in all_html_files:
        text = f.read_text(encoding="utf-8")
        assert 'class="page-action share"' in text, f"{f.relative_to(dist_dir)}: no Share action"


def test_advisories_index_rows_have_share_links(dist_dir):
    page = (dist_dir / "advisories" / "index.html").read_text(encoding="utf-8")
    rows = re.findall(r'<td><a href="(20[^"]+\.html)">', page)
    assert rows
    for href in rows:
        assert f'class="share" href="{href}"' in page, f"index row {href} has no share link"


def test_advisory_sidebar_is_capped_and_keeps_current_page(dist_dir):
    pages = sorted((dist_dir / "advisories").glob("20*.html"))
    oldest = pages[0]
    text = oldest.read_text(encoding="utf-8")
    sidebar = re.search(r'<aside id="sidebar".*?</aside>', text, re.DOTALL).group(0)
    items = re.findall(r"<li><a ", sidebar)
    assert len(items) <= SIDEBAR_MAX_ITEMS + 1
    assert f'href="{oldest.name}" class="active"' in sidebar
    assert "nav-more" in sidebar
