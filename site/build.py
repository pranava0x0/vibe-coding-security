#!/usr/bin/env python3
"""
Build the vibe-coding-security static site.

- Reads every .md file in the repo root, advisories/, playbooks/, prevention/,
  sources/, tools/ (skips PLAN.md, anything under .github, .claude, site/, dist/).
- Parses optional YAML frontmatter (id, title, severity, status, date_disclosed,
  last_updated, ecosystems, tags, tools_affected).
- Converts markdown to HTML (markdown + tables + fenced code + toc + codehilite).
- Rewrites internal .md links to .html.
- Wraps in a single shared template with sidebar nav + topbar.
- Generates dist/ with one HTML per source MD, plus a homepage.

Run locally:
    pip install markdown pyyaml pygments
    python site/build.py
    open dist/index.html
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import markdown  # type: ignore
import yaml  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"
DIST_DIR = REPO_ROOT / "dist"

# Sections rendered into the sidebar, in display order.
SECTIONS: list[tuple[str, str, str]] = [
    # (slug, label, source dir relative to repo root or "." for repo root pages)
    ("advisories", "Advisories", "advisories"),
    ("playbooks", "Playbooks", "playbooks"),
    ("prevention", "Prevention", "prevention"),
    ("sources", "Sources", "sources"),
    ("tools", "Tools", "tools"),
]

# Top-level pages rendered from repo root (besides README.md → index.html).
TOP_LEVEL_PAGES: list[tuple[str, str]] = [
    # (source filename, output filename)
    ("ALERTS.md", "alerts.html"),
    ("CONTRIBUTING.md", "contributing.html"),
    ("security.md", "security.html"),
    ("backlog.md", "backlog.html"),
    ("issues.md", "issues.html"),
]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclass
class Page:
    source_path: Path
    output_path: Path  # relative to DIST_DIR
    title: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    section: str = ""  # slug from SECTIONS, or "" for top-level
    is_index: bool = False  # True for section README.md → section/index.html


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        data = {}
    return data, text[match.end():]


def derive_title(frontmatter: dict[str, Any], body: str, source_path: Path) -> str:
    if frontmatter.get("title"):
        return str(frontmatter["title"])
    # First # heading
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return source_path.stem.replace("-", " ").replace("_", " ").title()


def rewrite_links(html: str) -> str:
    """Rewrite href="...md" → href="...html" but leave external URLs alone."""
    def replace(match: re.Match[str]) -> str:
        url = match.group(1)
        if url.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)
        # Anchor preserved
        anchor = ""
        if "#" in url:
            url, anchor = url.split("#", 1)
            anchor = "#" + anchor
        if url.endswith(".md"):
            url = url[:-3] + ".html"
        elif url.endswith("/"):
            url = url + "index.html"
        return f'href="{url}{anchor}"'
    return re.sub(r'href="([^"]+)"', replace, html)


def discover_pages() -> list[Page]:
    pages: list[Page] = []

    # README.md → index.html
    readme = REPO_ROOT / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        pages.append(Page(
            source_path=readme,
            output_path=Path("index.html"),
            title="vibe-coding-security",
            frontmatter=fm,
        ))

    # Top-level pages
    for src_name, out_name in TOP_LEVEL_PAGES:
        src = REPO_ROOT / src_name
        if not src.exists():
            continue
        text = src.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        title = derive_title(fm, body, src)
        pages.append(Page(
            source_path=src,
            output_path=Path(out_name),
            title=title,
            frontmatter=fm,
        ))

    # Section pages
    for slug, label, src_dir in SECTIONS:
        sec_dir = REPO_ROOT / src_dir
        if not sec_dir.is_dir():
            continue
        for md_path in sorted(sec_dir.glob("*.md")):
            text = md_path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            title = derive_title(fm, body, md_path)
            is_index = md_path.name == "README.md"
            out_name = "index.html" if is_index else f"{md_path.stem}.html"
            pages.append(Page(
                source_path=md_path,
                output_path=Path(slug) / out_name,
                title=title,
                frontmatter=fm,
                section=slug,
                is_index=is_index,
            ))

    return pages


def render_markdown(body: str) -> str:
    md = markdown.Markdown(extensions=[
        "fenced_code",
        "tables",
        "toc",
        "sane_lists",
        "codehilite",
    ], extension_configs={
        "codehilite": {"css_class": "code", "guess_lang": False},
    })
    return md.convert(body)


def severity_badge(sev: str | None) -> str:
    if not sev:
        return ""
    sev = sev.lower()
    return f'<span class="badge badge-sev-{sev}">{sev}</span>'


def status_badge(status: str | None) -> str:
    if not status:
        return ""
    s = status.lower()
    return f'<span class="badge badge-status-{s}">{s}</span>'


def relative_url(page: Page, current: Page) -> str:
    """Build a relative URL from current.output_path to page.output_path."""
    from os.path import relpath
    current_dir = current.output_path.parent if current.output_path.parent != Path() else Path()
    rel = relpath(page.output_path, current_dir if str(current_dir) != "." else ".")
    return rel.replace("\\", "/")


def build_sidebar(current: Page, all_pages: list[Page]) -> str:
    """Sidebar nav. Highlights current section."""
    parts: list[str] = []
    home_url = relative_url(next(p for p in all_pages if p.output_path == Path("index.html")), current)
    is_home = current.output_path == Path("index.html")
    parts.append(f'<a href="{home_url}" class="nav-home{" active" if is_home else ""}">Home</a>')

    alerts_page = next((p for p in all_pages if p.output_path == Path("alerts.html")), None)
    if alerts_page:
        url = relative_url(alerts_page, current)
        active = current.output_path == Path("alerts.html")
        parts.append(f'<a href="{url}" class="nav-alerts{" active" if active else ""}">⚠ Alerts</a>')

    for slug, label, _src in SECTIONS:
        index_page = next((p for p in all_pages if p.section == slug and p.is_index), None)
        if not index_page:
            continue
        url = relative_url(index_page, current)
        active = current.section == slug
        parts.append(f'<div class="nav-section">')
        parts.append(f'  <a href="{url}" class="nav-section-header{" active" if active else ""}">{label}</a>')
        # Sub-items: every page in section except the index, sorted
        if active:
            items = [p for p in all_pages if p.section == slug and not p.is_index]
            # Sort: advisories by date desc; everything else alphabetical
            if slug == "advisories":
                items.sort(key=lambda p: str(p.frontmatter.get("date_disclosed", "")), reverse=True)
            else:
                items.sort(key=lambda p: p.title.lower())
            parts.append('  <ul class="nav-section-items">')
            for item in items:
                url2 = relative_url(item, current)
                active2 = current.output_path == item.output_path
                sev = item.frontmatter.get("severity", "")
                badge = f' <span class="dot dot-{sev}"></span>' if sev else ""
                active_cls = ' class="active"' if active2 else ""
                parts.append(f'    <li><a href="{url2}"{active_cls}>{item.title}{badge}</a></li>')
            parts.append('  </ul>')
        parts.append('</div>')

    return "\n".join(parts)


def build_meta(page: Page) -> str:
    """Return the meta-bar HTML for an advisory (or "" if no metadata)."""
    fm = page.frontmatter
    if not fm or page.section != "advisories" or page.is_index:
        return ""
    parts: list[str] = ['<div class="meta">']
    if "severity" in fm:
        parts.append(severity_badge(str(fm["severity"])))
    if "status" in fm:
        parts.append(status_badge(str(fm["status"])))
    if "date_disclosed" in fm:
        parts.append(f'<span class="meta-item"><strong>Disclosed:</strong> {fm["date_disclosed"]}</span>')
    if "last_updated" in fm:
        parts.append(f'<span class="meta-item"><strong>Updated:</strong> {fm["last_updated"]}</span>')
    if "ecosystems" in fm and fm["ecosystems"]:
        eco = ", ".join(str(e) for e in fm["ecosystems"])
        parts.append(f'<span class="meta-item"><strong>Ecosystems:</strong> {eco}</span>')
    if "tools_affected" in fm and fm["tools_affected"]:
        tools = ", ".join(str(t) for t in fm["tools_affected"])
        parts.append(f'<span class="meta-item"><strong>Tools:</strong> {tools}</span>')
    if "tags" in fm and fm["tags"]:
        tags = " ".join(f'<span class="tag">{t}</span>' for t in fm["tags"])
        parts.append(f'<span class="meta-item">{tags}</span>')
    parts.append('</div>')
    return "\n".join(parts)


def render_page(page: Page, all_pages: list[Page], template: str) -> str:
    text = page.source_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    page.frontmatter = fm  # refresh
    page.title = derive_title(fm, body, page.source_path)

    html = render_markdown(body)
    html = rewrite_links(html)
    sidebar = build_sidebar(page, all_pages)
    meta = build_meta(page)

    # Repo-relative depth for asset paths
    depth = len(page.output_path.parts) - 1
    asset_prefix = "../" * depth if depth else ""

    out = template
    out = out.replace("{{TITLE}}", page.title)
    out = out.replace("{{ASSET_PREFIX}}", asset_prefix)
    out = out.replace("{{SIDEBAR}}", sidebar)
    out = out.replace("{{META}}", meta)
    out = out.replace("{{CONTENT}}", html)
    out = out.replace("{{BUILD_DATE}}", date.today().isoformat())
    return out


def main() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    template = (SITE_DIR / "template.html").read_text(encoding="utf-8")

    # Copy static assets (CSS)
    css_src = SITE_DIR / "style.css"
    if css_src.exists():
        shutil.copy(css_src, DIST_DIR / "style.css")

    # Add CNAME / nojekyll
    (DIST_DIR / ".nojekyll").touch()

    pages = discover_pages()

    # Render each page
    for page in pages:
        # Parse frontmatter so build_sidebar can read severities
        text = page.source_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        page.frontmatter = fm
        page.title = derive_title(fm, text, page.source_path)

    for page in pages:
        rendered = render_page(page, pages, template)
        out_path = DIST_DIR / page.output_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")

    # Write an advisories JSON dump for anyone who wants to consume it
    adv_data = []
    for p in pages:
        if p.section == "advisories" and not p.is_index:
            adv_data.append({
                "id": p.frontmatter.get("id"),
                "title": p.title,
                "severity": p.frontmatter.get("severity"),
                "status": p.frontmatter.get("status"),
                "date_disclosed": str(p.frontmatter.get("date_disclosed", "")),
                "last_updated": str(p.frontmatter.get("last_updated", "")),
                "ecosystems": p.frontmatter.get("ecosystems", []),
                "tools_affected": p.frontmatter.get("tools_affected", []),
                "tags": p.frontmatter.get("tags", []),
                "url": "/" + str(p.output_path).replace("\\", "/"),
            })
    adv_data.sort(key=lambda x: str(x.get("date_disclosed") or ""), reverse=True)
    (DIST_DIR / "advisories.json").write_text(
        json.dumps({"generated": date.today().isoformat(), "advisories": adv_data}, indent=2),
        encoding="utf-8",
    )

    print(f"Built {len(pages)} pages → {DIST_DIR}")


if __name__ == "__main__":
    main()
