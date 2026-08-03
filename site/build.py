#!/usr/bin/env python3
"""
Build the Vibe Coding · Security Issue Tracking static site + LLM-friendly outputs.

Outputs (in dist/):
  Per page:
    - <page>.html (rendered)
    - <page>.md (raw markdown source — Mintlify/Anthropic pattern so LLMs
      and tools can fetch the source without re-parsing HTML)

  Site-wide:
    - style.css, .nojekyll
    - llms.txt (llmstxt.org root index)
    - llms-full.txt (full corpus; advisories + playbooks + prevention)
    - llms-ctx.txt (compact: just alerts + advisory TL;DRs)
    - advisories/llms.txt, playbooks/llms.txt, prevention/llms.txt, etc.
      (per-section indexes for narrowly-scoped LLM consumption)
    - sitemap.xml + robots.txt
    - feed.xml (Atom feed of advisories)
    - advisories.json (structured frontmatter dump)
    - search.json (per-page index for client-side search)
    - advisory-schema.json (JSON Schema for advisory frontmatter — enables
      authoring tools to validate)
    - api/v1/advisories.json (versioned API endpoint)
    - api/v1/index.json (top-level API index)

Per page also includes:
  - Semantic HTML with <article>, <header>, <nav>, <aside>, <main>, <footer>
  - <meta name="description"> derived from frontmatter or first paragraph
  - canonical link, Open Graph, Twitter card
  - JSON-LD (TechArticle / Article + ItemList on index pages)
  - <link rel="alternate"> entries for the .md version + RSS + section indexes
  - Per-page TOC (right rail at >=1200px) auto-generated from h2/h3
  - "View raw markdown" link in the page header

Run locally:
    pip install -r site/requirements.txt
    python site/build.py
    open dist/index.html
"""

from __future__ import annotations

import html
import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from os.path import relpath as _relpath
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

import markdown  # type: ignore
import yaml  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"
DIST_DIR = REPO_ROOT / "dist"

SITE_URL = "https://pranava0x0.github.io/vibe-coding-security"
REPO_URL = "https://github.com/pranava0x0/vibe-coding-security"
SITE_NAME = "Vibe Coding - Security Issue Tracking"
SITE_NAME_DISPLAY = "Vibe Coding · Security Issue Tracking"
SITE_TAGLINE = (
    "Living index of supply-chain attacks, malicious MCP servers, and "
    "prompt-injection campaigns relevant to vibe coding."
)

SECTIONS: list[tuple[str, str, str]] = [
    ("advisories", "Advisories", "advisories"),
    ("playbooks", "Playbooks", "playbooks"),
    ("prevention", "Prevention", "prevention"),
    ("sources", "Sources", "sources"),
    ("tools", "Tools", "tools"),
]

TOP_LEVEL_PAGES: list[tuple[str, str]] = [
    ("ALERTS.md", "alerts.html"),
    ("CONTRIBUTING.md", "contributing.html"),
    ("SECURITY.md", "security.html"),
    ("CHANGELOG.md", "changelog.html"),
    ("BACKLOG.md", "backlog.html"),
    ("ISSUES.md", "issues.html"),
]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclass
class Page:
    source_path: Path
    output_path: Path
    title: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""
    raw_text: str = ""
    section: str = ""
    is_index: bool = False
    description: str = ""
    rendered_html: str = ""
    toc_html: str = ""
    headings: list[tuple[int, str, str]] = field(default_factory=list)


# ────────────────────────────────────────────────────────────────────────────
# Frontmatter + parsing
# ────────────────────────────────────────────────────────────────────────────

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
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return source_path.stem.replace("-", " ").replace("_", " ").title()


def _leading_blockquote_summary(body: str) -> str | None:
    """First paragraph of a leading `>` blockquote, cleaned — the page's intended
    summary (the llmstxt.org convention; README, ALERTS, and several playbooks
    open with one). Returns None if the body doesn't start with a blockquote, so
    callers fall through to first-paragraph extraction. Prevents a page whose body
    leads with a list (e.g. the README's numbered "How to use") from producing a
    meta/OG description that starts mid-list."""
    lines = body.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith("# "):  # skip a leading h1
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
    buf: list[str] = []
    for line in lines[i:]:
        s = line.strip()
        if s.startswith(">"):
            content = s[1:].strip()
            if not content:  # blank `>` line terminates the first paragraph
                break
            buf.append(content)
        elif buf:
            break
        else:
            return None  # no leading blockquote
    if not buf:
        return None
    text = " ".join(buf)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 200:
        text = text[:197].rsplit(" ", 1)[0] + "…"
    return text or None


def derive_description(frontmatter: dict[str, Any], body: str) -> str:
    if frontmatter.get("description"):
        return str(frontmatter["description"]).strip()

    # A leading `>` blockquote is the page's hand-written summary — prefer it over
    # scraping the first paragraph (which can land on a list item or code block).
    bq = _leading_blockquote_summary(body)
    if bq:
        return bq

    buf: list[str] = []
    in_para = False
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            if buf:
                break
            continue
        if stripped.startswith(("#", "```", ">", "|", "-", "*", "_", "<")):
            if buf:
                break
            continue
        if stripped.startswith("**TL;DR**") or stripped.lower().startswith("tl;dr"):
            in_para = True
            stripped = re.sub(r"^\*\*TL;DR\*\*\s*", "", stripped)
            stripped = re.sub(r"^tl;dr[:\s]*", "", stripped, flags=re.I)
        buf.append(stripped)
        in_para = True
        if len(" ".join(buf)) > 250:
            break

    desc = " ".join(buf)
    desc = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", desc)
    desc = re.sub(r"[*_`]+", "", desc)
    desc = re.sub(r"\s+", " ", desc).strip()
    if len(desc) > 200:
        desc = desc[:197].rsplit(" ", 1)[0] + "…"
    return desc or SITE_TAGLINE


# ────────────────────────────────────────────────────────────────────────────
# Markdown rendering
# ────────────────────────────────────────────────────────────────────────────

def rewrite_links(
    html_text: str,
    current_relpath: Path | None = None,
    source_to_output: dict[Path, Path] | None = None,
) -> str:
    """Rewrite markdown-style hrefs to their built equivalents."""
    github_blob = f"{REPO_URL}/blob/main"
    src_map = source_to_output or {}

    def make_relative(target_rel: Path) -> str:
        if current_relpath is None:
            return str(target_rel).replace("\\", "/")
        current_out = src_map.get(current_relpath) or Path("index.html")
        base_dir = current_out.parent if str(current_out.parent) != "." else Path(".")
        return _relpath(target_rel, base_dir).replace("\\", "/")

    def replace(match: re.Match[str]) -> str:
        url = match.group(1)
        if url.startswith(("http://", "https://", "mailto:", "#", "data:", "javascript:")):
            return match.group(0)

        anchor = ""
        if "#" in url:
            url, anchor = url.split("#", 1)
            anchor = "#" + anchor

        normalized: str | None = None
        if current_relpath is not None and not url.startswith("/"):
            try:
                base_dir = current_relpath.parent
                resolved = (REPO_ROOT / base_dir / url).resolve()
                normalized = str(resolved.relative_to(REPO_ROOT))
            except (ValueError, OSError):
                normalized = None

        if normalized is not None:
            src_path = Path(normalized)
            if src_path in src_map:
                target = src_map[src_path]
                return f'href="{make_relative(target)}{anchor}"'
            if (REPO_ROOT / src_path).exists():
                return f'href="{github_blob}/{normalized}{anchor}" rel="noopener"'

        if url.endswith("/README.md"):
            url = url[: -len("README.md")] + "index.html"
        elif url == "README.md":
            url = "index.html"
        elif url.endswith(".md"):
            url = url[:-3] + ".html"
        elif url.endswith("/"):
            url = url + "index.html"

        return f'href="{url}{anchor}"'

    return re.sub(r'href="([^"]+)"', replace, html_text)


def render_markdown(body: str) -> tuple[str, str, list[tuple[int, str, str]]]:
    md = markdown.Markdown(extensions=[
        "fenced_code", "tables", "toc", "sane_lists", "codehilite", "attr_list",
    ], extension_configs={
        "codehilite": {"css_class": "code", "guess_lang": False},
        "toc": {"toc_depth": "2-3", "permalink": False, "anchorlink": False},
    })
    html_out = md.convert(body)
    toc_html = md.toc  # type: ignore[attr-defined]
    headings: list[tuple[int, str, str]] = []
    for token in md.toc_tokens:  # type: ignore[attr-defined]
        _walk_toc(token, headings, depth=2)
    return html_out, toc_html, headings


def _walk_toc(token: dict, out: list[tuple[int, str, str]], depth: int) -> None:
    out.append((depth, token["id"], token["name"]))
    for child in token.get("children", []):
        _walk_toc(child, out, depth + 1)


# ────────────────────────────────────────────────────────────────────────────
# HTML helpers
# ────────────────────────────────────────────────────────────────────────────

def severity_badge(sev: str | None) -> str:
    if not sev:
        return ""
    s = html.escape(str(sev).lower())
    return f'<span class="badge badge-sev-{s}" aria-label="Severity {s}">{s}</span>'


def status_badge(status: str | None) -> str:
    if not status:
        return ""
    s = html.escape(str(status).lower())
    return f'<span class="badge badge-status-{s}" aria-label="Status {s}">{s}</span>'


def relative_url(target: Page, current: Page) -> str:
    current_dir = current.output_path.parent if str(current.output_path.parent) != "." else Path(".")
    return _relpath(target.output_path, current_dir).replace("\\", "/")


def build_sidebar(current: Page, all_pages: list[Page]) -> str:
    parts: list[str] = ['<nav class="sidebar-inner" aria-label="Site sections">']

    home = next(p for p in all_pages if p.output_path == Path("index.html"))
    parts.append(_nav_link(home, current, "nav-home", "🏠 Home"))

    alerts = next((p for p in all_pages if p.output_path == Path("alerts.html")), None)
    if alerts:
        parts.append(_nav_link(alerts, current, "nav-alerts", "⚠ Alerts"))

    for slug, label, _ in SECTIONS:
        index_page = next((p for p in all_pages if p.section == slug and p.is_index), None)
        if not index_page:
            continue
        url = relative_url(index_page, current)
        active = current.section == slug
        parts.append('<div class="nav-section">')
        parts.append(
            f'<a href="{url}" class="nav-section-header{" active" if active else ""}">{html.escape(label)}</a>'
        )
        if active:
            items = [p for p in all_pages if p.section == slug and not p.is_index]
            if slug == "advisories":
                items.sort(key=lambda p: str(p.frontmatter.get("date_disclosed", "")), reverse=True)
            else:
                items.sort(key=lambda p: p.title.lower())
            parts.append('<ul class="nav-section-items">')
            for item in items:
                url2 = relative_url(item, current)
                active2 = current.output_path == item.output_path
                cls = ' class="active"' if active2 else ""
                sev = str(item.frontmatter.get("severity", "")).lower()
                dot = f' <span class="dot dot-{sev}" aria-hidden="true"></span>' if sev else ""
                parts.append(
                    f'<li><a href="{url2}"{cls}>{html.escape(item.title)}{dot}</a></li>'
                )
            parts.append('</ul>')
        parts.append('</div>')

    parts.append('</nav>')
    return "\n".join(parts)


def _nav_link(target: Page, current: Page, cls: str, label: str) -> str:
    url = relative_url(target, current)
    active = current.output_path == target.output_path
    full_cls = cls + (" active" if active else "")
    return f'<a href="{url}" class="{full_cls}">{label}</a>'


def build_meta_bar(page: Page) -> str:
    fm = page.frontmatter
    if not fm or page.section != "advisories" or page.is_index:
        return ""
    parts: list[str] = ['<aside class="meta" aria-label="Advisory metadata">']

    badges: list[str] = []
    if fm.get("severity"):
        badges.append(severity_badge(str(fm["severity"])))
    if fm.get("status"):
        badges.append(status_badge(str(fm["status"])))
    if badges:
        parts.append(f'<div class="meta-badges">{"".join(badges)}</div>')

    rows: list[str] = []
    if fm.get("date_disclosed"):
        d = html.escape(str(fm["date_disclosed"]))
        rows.append(
            f'<div class="meta-row"><span class="meta-label">Disclosed</span>'
            f'<time datetime="{d}">{d}</time></div>'
        )
    if fm.get("last_updated"):
        d = html.escape(str(fm["last_updated"]))
        rows.append(
            f'<div class="meta-row"><span class="meta-label">Updated</span>'
            f'<time datetime="{d}">{d}</time></div>'
        )
    if fm.get("ecosystems"):
        chips = "".join(
            f'<span class="chip chip-eco">{html.escape(str(e))}</span>'
            for e in fm["ecosystems"]
        )
        rows.append(f'<div class="meta-row"><span class="meta-label">Ecosystems</span><span class="chips">{chips}</span></div>')
    if fm.get("tools_affected"):
        chips = "".join(
            f'<span class="chip chip-tool">{html.escape(str(t))}</span>'
            for t in fm["tools_affected"]
        )
        rows.append(f'<div class="meta-row"><span class="meta-label">Tools</span><span class="chips">{chips}</span></div>')
    if fm.get("tags"):
        chips = "".join(
            f'<span class="chip chip-tag">{html.escape(str(t))}</span>'
            for t in fm["tags"]
        )
        rows.append(f'<div class="meta-row"><span class="meta-label">Tags</span><span class="chips">{chips}</span></div>')
    if rows:
        parts.append('<div class="meta-rows">')
        parts.extend(rows)
        parts.append('</div>')

    parts.append('</aside>')
    return "\n".join(parts)


def build_toc(page: Page) -> str:
    if not page.headings or len(page.headings) < 3:
        return ""
    parts: list[str] = ['<aside class="toc" aria-label="On this page"><h2 class="toc-title">On this page</h2><ol class="toc-list">']
    for depth, slug, name in page.headings:
        if depth > 3:
            continue
        cls = f"toc-d{depth}"
        parts.append(f'<li class="{cls}"><a href="#{html.escape(slug)}">{html.escape(name)}</a></li>')
    parts.append('</ol></aside>')
    return "\n".join(parts)


def build_breadcrumb(page: Page, all_pages: list[Page]) -> str:
    if not page.section or page.is_index:
        return ""
    home = next(p for p in all_pages if p.output_path == Path("index.html"))
    section_idx = next(
        (p for p in all_pages if p.section == page.section and p.is_index),
        None,
    )
    if not section_idx:
        return ""
    parts = [
        '<nav class="breadcrumb" aria-label="Breadcrumb">',
        f'<a href="{relative_url(home, page)}">Home</a>',
        '<span aria-hidden="true">›</span>',
        f'<a href="{relative_url(section_idx, page)}">{html.escape(section_idx.title)}</a>',
        '</nav>',
    ]
    return "\n".join(parts)


def build_page_actions(page: Page) -> str:
    """'View raw markdown' / 'Edit on GitHub' actions in the page header."""
    md_name = page.output_path.name.replace(".html", ".md")
    md_url = md_name
    try:
        src_rel = page.source_path.relative_to(REPO_ROOT)
        gh_edit = f"{REPO_URL}/blob/main/{src_rel.as_posix()}"
    except ValueError:
        gh_edit = REPO_URL
    return (
        '<div class="page-actions">'
        f'<a href="{md_url}" class="page-action" rel="alternate">View raw markdown</a>'
        f'<a href="{gh_edit}" class="page-action" rel="noopener">Edit on GitHub ↗</a>'
        '</div>'
    )


# ────────────────────────────────────────────────────────────────────────────
# JSON-LD
# ────────────────────────────────────────────────────────────────────────────

def build_jsonld(page: Page, page_url: str, all_pages: list[Page]) -> str:
    fm = page.frontmatter

    # Advisories index → ItemList
    if page.section == "advisories" and page.is_index:
        items = [p for p in all_pages if p.section == "advisories" and not p.is_index]
        items.sort(key=lambda p: str(p.frontmatter.get("date_disclosed", "")), reverse=True)
        data = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "Vibe Coding Security Advisories",
            "url": page_url,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "url": f"{SITE_URL}/{p.output_path.as_posix()}",
                    "name": p.title,
                }
                for i, p in enumerate(items)
            ],
        }
    elif page.section == "advisories" and not page.is_index:
        data = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": page.title,
            "description": page.description,
            "url": page_url,
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME_DISPLAY, "url": SITE_URL},
            "keywords": ", ".join(list(fm.get("tags", [])) + list(fm.get("ecosystems", []))),
            "articleSection": "Security Advisory",
        }
        if fm.get("date_disclosed"):
            data["datePublished"] = str(fm["date_disclosed"])
        if fm.get("last_updated"):
            data["dateModified"] = str(fm["last_updated"])
    else:
        data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page.title,
            "description": page.description,
            "url": page_url,
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME_DISPLAY, "url": SITE_URL},
        }
    return '<script type="application/ld+json">' + json.dumps(data) + "</script>"


# ────────────────────────────────────────────────────────────────────────────
# Page discovery & rendering
# ────────────────────────────────────────────────────────────────────────────

def discover_pages() -> list[Page]:
    pages: list[Page] = []

    readme = REPO_ROOT / "README.md"
    if readme.exists():
        pages.append(Page(source_path=readme, output_path=Path("index.html"), title=SITE_NAME_DISPLAY))

    for src_name, out_name in TOP_LEVEL_PAGES:
        src = REPO_ROOT / src_name
        if not src.exists():
            continue
        pages.append(Page(source_path=src, output_path=Path(out_name), title=src.stem))

    for slug, label, src_dir in SECTIONS:
        sec_dir = REPO_ROOT / src_dir
        if not sec_dir.is_dir():
            continue
        for md_path in sorted(sec_dir.glob("*.md")):
            is_index = md_path.name == "README.md"
            out_name = "index.html" if is_index else f"{md_path.stem}.html"
            pages.append(Page(
                source_path=md_path,
                output_path=Path(slug) / out_name,
                title=md_path.stem,
                section=slug,
                is_index=is_index,
            ))
    return pages


def _strip_leading_h1(body: str) -> str:
    """Remove the first '# Heading' line from a markdown body if present.

    The template renders the title as <h1 class="page-title">, so a body-level
    h1 would produce two h1s on the page (bad for accessibility + SEO)."""
    lines = body.splitlines()
    i = 0
    # skip leading blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith("# "):
        # drop the line + any immediately-following blank
        del lines[i]
        if i < len(lines) and not lines[i].strip():
            del lines[i]
    return "\n".join(lines)


def preprocess(pages: list[Page]) -> None:
    src_map: dict[Path, Path] = {}
    for p in pages:
        try:
            src_map[p.source_path.relative_to(REPO_ROOT)] = p.output_path
        except ValueError:
            pass

    for p in pages:
        text = p.source_path.read_text(encoding="utf-8")
        p.raw_text = text
        fm, body = parse_frontmatter(text)
        p.frontmatter = fm
        p.body = body
        p.title = derive_title(fm, body, p.source_path)
        p.description = derive_description(fm, body)

        # Strip body-level h1 to avoid duplicating the template's h1
        body_for_render = _strip_leading_h1(body)

        rendered, toc, headings = render_markdown(body_for_render)
        try:
            relpath_in_repo = p.source_path.relative_to(REPO_ROOT)
        except ValueError:
            relpath_in_repo = None
        p.rendered_html = rewrite_links(rendered, relpath_in_repo, src_map)
        p.toc_html = toc
        p.headings = headings


def render_page(page: Page, all_pages: list[Page], template: str) -> str:
    sidebar = build_sidebar(page, all_pages)
    meta_bar = build_meta_bar(page)
    toc = build_toc(page)
    crumb = build_breadcrumb(page, all_pages)
    actions = build_page_actions(page)

    depth = len(page.output_path.parts) - 1
    asset_prefix = "../" * depth if depth else ""

    page_url = f"{SITE_URL}/{page.output_path.as_posix()}"
    if page.output_path == Path("index.html"):
        page_url = SITE_URL + "/"

    md_alt_url = page_url[:-5] + ".md" if page_url.endswith(".html") else page_url + "index.md"

    jsonld = build_jsonld(page, page_url, all_pages)

    og_type = "article" if page.section == "advisories" and not page.is_index else "website"

    if page.output_path == Path("index.html"):
        html_title = SITE_NAME_DISPLAY
    else:
        html_title = f"{html.escape(page.title)} — {SITE_NAME_DISPLAY}"

    out = template
    repl = {
        "{{TITLE}}": html.escape(page.title),
        "{{HTML_TITLE}}": html_title,
        "{{DESCRIPTION}}": html.escape(page.description),
        "{{CANONICAL}}": html.escape(page_url),
        "{{MD_ALTERNATE}}": html.escape(md_alt_url),
        "{{OG_TYPE}}": og_type,
        "{{ASSET_PREFIX}}": asset_prefix,
        "{{SIDEBAR}}": sidebar,
        "{{BREADCRUMB}}": crumb,
        "{{META}}": meta_bar,
        "{{ACTIONS}}": actions,
        "{{TOC}}": toc,
        "{{CONTENT}}": page.rendered_html,
        "{{BUILD_DATE}}": date.today().isoformat(),
        "{{JSONLD}}": jsonld,
        "{{SITE_URL}}": SITE_URL,
        "{{REPO_URL}}": REPO_URL,
        "{{HAS_TOC}}": "has-toc" if toc else "",
    }
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


# ────────────────────────────────────────────────────────────────────────────
# LLM-friendly outputs
# ────────────────────────────────────────────────────────────────────────────

def _human_size(num_bytes: int) -> str:
    """Approximate human-readable byte size for the llms.txt index.

    Rounded to the nearest 10KB (or 0.1MB) so the figure stays accurate as the
    corpus grows without jittering on every build — keeps determinism intact
    while never going stale the way a hardcoded '~230KB' did."""
    kb = num_bytes / 1024
    if kb < 1000:
        return f"~{round(kb / 10) * 10}KB"
    return f"~{kb / 1024:.1f}MB"


def _page_md_url(p: Page) -> str:
    return f"{SITE_URL}/{p.output_path.as_posix()[:-5]}.md"


def _page_html_url(p: Page) -> str:
    if p.output_path == Path("index.html"):
        return SITE_URL + "/"
    return f"{SITE_URL}/{p.output_path.as_posix()}"


def build_llms_txt(pages: list[Page], full_bytes: int | None = None, ctx_bytes: int | None = None) -> str:
    lines: list[str] = [
        f"# {SITE_NAME}",
        "",
        f"> {SITE_TAGLINE}",
        "",
        "Tracks active supply-chain attacks (npm + PyPI), malicious MCP servers, ",
        "CVEs in AI coding tools (Cursor, Claude Code, Windsurf, Gemini CLI, Copilot), ",
        "prompt-injection campaigns, and credential-theft incidents that target ",
        "people who build with AI coding tools. Every advisory has concrete ",
        "'am I affected?' commands, IOCs where available, and links to recovery playbooks.",
        "",
        "Audience: solo devs and small teams shipping with Cursor, Claude Code, ",
        "Lovable, v0, Bolt, Replit, Windsurf, Codex.",
        "",
        "Every page is also available as raw markdown (replace `.html` with `.md` ",
        "in any URL, or follow the `<link rel=\"alternate\">` declaration).",
        "",
        "## Active alerts",
        "",
        f"- [Alerts feed]({SITE_URL}/alerts.html) ([md]({SITE_URL}/alerts.md)): single scannable feed of active, recent, and historical incidents",
        f"- [Atom feed]({SITE_URL}/feed.xml): subscribe for new advisories in any RSS reader",
        "",
    ]

    advisories = [p for p in pages if p.section == "advisories" and not p.is_index]
    advisories.sort(key=lambda p: str(p.frontmatter.get("date_disclosed", "")), reverse=True)

    lines.append("## Advisories")
    lines.append("")
    for p in advisories:
        sev = p.frontmatter.get("severity", "")
        date_d = p.frontmatter.get("date_disclosed", "")
        meta = f" [{sev}]" if sev else ""
        meta += f" {date_d}" if date_d else ""
        # root llms.txt is a scannable *index*, not a full-text export (that's
        # llms-full.txt) — cap each one-line description so the index stays
        # roughly flat as the advisory corpus grows, instead of every sweep
        # eventually re-hitting LLMS_TXT_MAX_BYTES the way llms-full.txt/
        # llms-ctx.txt repeatedly have. (2026-07-16)
        # 2026-07-22: tightened from 160 to 145 chars — the corpus grew past the
        # llms.txt size cap (tests/test_llms.py) again; trim per-entry length as
        # the corpus grows rather than bumping the cap, per standing guidance.
        # 2026-07-25: tightened from 145 to 130 chars — same reason, 3 more
        # advisories pushed the index past the 80KB cap again.
        # 2026-07-27: tightened from 130 to 122 chars — same reason, 1 more
        # advisory pushed the index past the 80KB cap again.
        # 2026-07-29: tightened from 122 to 108 chars — same reason, 3 more
        # advisories pushed the index past the 80KB cap again.
        # 2026-07-31: tightened from 108 to 96 chars — same reason, 5 more
        # advisories pushed the index past the 80KB cap again.
        # 2026-08-01: tightened from 96 to 88 chars — same reason, 2 more
        # advisories pushed the index past the 80KB cap again.
        # 2026-08-03: tightened from 88 to 75 chars — 1 new advisory + 1
        # updated advisory pushed the index 1 byte past the 80KB cap again.
        desc = p.description
        if len(desc) > 75:
            desc = desc[:74].rsplit(" ", 1)[0] + "…"
        lines.append(
            f"- [{p.title}]({_page_html_url(p)}) ([md]({_page_md_url(p)})){meta}: {desc}"
        )
    lines.append("")

    for slug, label, _ in SECTIONS:
        if slug == "advisories":
            continue
        items = [p for p in pages if p.section == slug and not p.is_index]
        items.sort(key=lambda p: p.title.lower())
        if not items:
            continue
        lines.append(f"## {label}")
        lines.append("")
        for p in items:
            lines.append(f"- [{p.title}]({_page_html_url(p)}) ([md]({_page_md_url(p)})): {p.description}")
        lines.append("")

    full_size = _human_size(full_bytes) if full_bytes else "~500KB"
    ctx_size = _human_size(ctx_bytes) if ctx_bytes else "~70KB"
    lines.append("## Optional")
    lines.append("")
    lines.append(f"- [llms-full.txt]({SITE_URL}/llms-full.txt): every advisory + playbook + prevention doc concatenated ({full_size}) for full-context ingestion")
    lines.append(f"- [llms-ctx.txt]({SITE_URL}/llms-ctx.txt): compact context — alerts + per-advisory TL;DRs only ({ctx_size})")
    lines.append(f"- [advisories/llms.txt]({SITE_URL}/advisories/llms.txt): advisories-only index")
    lines.append(f"- [playbooks/llms.txt]({SITE_URL}/playbooks/llms.txt): playbooks-only index")
    lines.append(f"- [prevention/llms.txt]({SITE_URL}/prevention/llms.txt): prevention-only index")
    lines.append(f"- [advisories.json]({SITE_URL}/advisories.json): structured advisory index with frontmatter")
    lines.append(f"- [api/v1/advisories.json]({SITE_URL}/api/v1/advisories.json): same data behind a stable versioned URL")
    lines.append(f"- [advisory-schema.json]({SITE_URL}/advisory-schema.json): JSON Schema for advisory frontmatter")
    lines.append(f"- [GitHub source]({REPO_URL}): raw markdown, contribution guide, issue templates")
    lines.append("")

    return "\n".join(lines)


def build_section_llms_txt(section_slug: str, section_label: str, pages: list[Page]) -> str:
    """Per-section llms.txt — same format as root, scoped to one section."""
    items = [p for p in pages if p.section == section_slug and not p.is_index]
    if section_slug == "advisories":
        items.sort(key=lambda p: str(p.frontmatter.get("date_disclosed", "")), reverse=True)
    else:
        items.sort(key=lambda p: p.title.lower())

    lines: list[str] = [
        f"# {SITE_NAME} — {section_label}",
        "",
        f"> {section_label} section of {SITE_NAME}. {len(items)} entries.",
        "",
        f"Root: {SITE_URL}/llms.txt",
        "",
        f"## {section_label}",
        "",
    ]
    for p in items:
        meta = ""
        if section_slug == "advisories":
            sev = p.frontmatter.get("severity", "")
            date_d = p.frontmatter.get("date_disclosed", "")
            meta = f" [{sev}]" if sev else ""
            meta += f" {date_d}" if date_d else ""
        lines.append(
            f"- [{p.title}]({_page_html_url(p)}) ([md]({_page_md_url(p)})){meta}: {p.description}"
        )
    lines.append("")
    return "\n".join(lines)


def _advisory_age_days(fm: dict[str, Any]) -> int | None:
    """Best-effort age in days from date_disclosed (YYYY-MM-DD or YYYY-MM). None if unparseable."""
    raw = str(fm.get("date_disclosed") or "")
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            d = datetime.strptime(raw, fmt).date()
            return (date.today() - d).days
        except ValueError:
            continue
    return None


def build_llms_full_txt(pages: list[Page]) -> str:
    out: list[str] = [
        f"# {SITE_NAME} — full corpus",
        "",
        f"Generated {date.today().isoformat()} from {REPO_URL}",
        "",
        f"Every advisory, playbook, prevention guide, and source list concatenated for LLM ingestion. ",
        f"The canonical web version of each document is linked above its content.",
        "",
        "---",
        "",
    ]

    def emit(group_label: str, group_pages: list[Page]) -> None:
        out.append(f"# {group_label}")
        out.append("")
        for p in group_pages:
            out.append(f"---")
            out.append("")
            out.append(f"<!-- source: {p.source_path.relative_to(REPO_ROOT)} -->")
            out.append(f"<!-- canonical: {_page_html_url(p)} -->")
            out.append("")
            # Prefix with the title as a heading so LLMs can navigate the
            # document by section title. (Bodies typically start with ## TL;DR
            # — without the title, structure is hard to follow.)
            out.append(f"## {p.title}")
            out.append("")
            # 2026-07-14: status=historical advisories are patched/superseded
            # patterns kept for reference, not active incidents — emit only
            # TL;DR + a link to the canonical page instead of the full body.
            # 2026-07-17: broadened per BACKLOG.md — trimming on status=historical
            # alone doesn't scale (almost nothing is ever marked historical in
            # practice), so also trim status=patched/contained/mitigated advisories
            # whose date_disclosed is > 120 days old. These are resolved,
            # non-actionable incidents for a reader triaging *current* risk; the
            # full write-up remains one click away via the per-page mirror. This
            # is the "real fix" flagged as open since 2026-06-19 (repeated cap
            # bumps instead of broader trimming).
            # 2026-07-29: tightened the age threshold from 120 to 90 days — the
            # corpus grew past LLMS_FULL_MAX_BYTES again after 3 more advisories;
            # trim more aggressively as the corpus grows, per standing guidance.
            _age = _advisory_age_days(p.frontmatter)
            _trim_status = p.frontmatter.get("status") in ("patched", "contained", "mitigated")
            if p.section == "advisories" and (
                p.frontmatter.get("status") == "historical"
                or (_trim_status and _age is not None and _age > 90)
            ):
                tldr = _extract_section(p.body, "TL;DR") or p.description
                out.append((tldr or "").strip())
                out.append("")
                out.append(f"_Historical/superseded pattern — full write-up at {_page_html_url(p)}._")
                out.append("")
            else:
                # Strip the body's own leading # heading if present, to avoid
                # duplication with the prefix above.
                out.append(_strip_leading_h1(p.body).strip())
                out.append("")
        out.append("")

    advisories = [p for p in pages if p.section == "advisories" and not p.is_index]
    advisories.sort(key=lambda p: str(p.frontmatter.get("date_disclosed", "")), reverse=True)
    emit("Advisories", advisories)

    playbooks = [p for p in pages if p.section == "playbooks" and not p.is_index]
    playbooks.sort(key=lambda p: p.title.lower())
    emit("Playbooks", playbooks)

    prevention = [p for p in pages if p.section == "prevention" and not p.is_index]
    prevention.sort(key=lambda p: p.title.lower())
    emit("Prevention", prevention)

    sources_pages = [p for p in pages if p.section == "sources" and not p.is_index]
    sources_pages.sort(key=lambda p: p.title.lower())
    emit("Sources", sources_pages)

    tools_pages = [p for p in pages if p.section == "tools"]
    tools_pages.sort(key=lambda p: p.title.lower())
    if tools_pages:
        emit("Tools", tools_pages)

    return "\n".join(out)


def build_llms_ctx_txt(pages: list[Page]) -> str:
    """Compact mid-tier: per-advisory TL;DR + 'am I affected?' only — far smaller
    than llms-full.txt while still covering every advisory. Grows ~linearly with
    the corpus (see LLMS_CTX_MAX_BYTES in tests/test_llms.py for the current cap).

    Pattern documented in: Mintlify's llms.txt guidance + Anthropic docs."""
    advisories = [p for p in pages if p.section == "advisories" and not p.is_index]
    advisories.sort(key=lambda p: str(p.frontmatter.get("date_disclosed", "")), reverse=True)

    lines: list[str] = [
        f"# {SITE_NAME} — compact context",
        "",
        f"> {SITE_TAGLINE}",
        "",
        f"Generated {date.today().isoformat()}. Compact variant: alerts + per-advisory ",
        "TL;DR + 'am I affected?' commands. For full content use llms-full.txt.",
        "",
        f"Index: {SITE_URL}/llms.txt | Full: {SITE_URL}/llms-full.txt | Web: {SITE_URL}/",
        "",
        "---",
        "",
    ]

    for p in advisories:
        sev = p.frontmatter.get("severity", "")
        status = p.frontmatter.get("status", "")
        date_d = p.frontmatter.get("date_disclosed", "")
        tag_line = " | ".join(
            x for x in [
                f"severity={sev}" if sev else "",
                f"status={status}" if status else "",
                f"disclosed={date_d}" if date_d else "",
            ] if x
        )

        # Extract just TL;DR section if present (truncated to keep this variant compact).
        # 2026-07-22: tightened from 395/355 to 370/330 chars. 2026-07-26: tightened
        # further to 350/310 chars. 2026-07-30: tightened again to 325/290 chars.
        # 2026-08-02: tightened again to 295/260 chars — the corpus grew past the
        # llms-ctx.txt size cap (tests/test_llms.py) again after the Copilot Word
        # worm advisory; trim per-entry length here as the corpus grows rather than
        # bumping the cap, per this repo's standing guidance.
        tldr = _extract_section(p.body, "TL;DR") or p.description
        tldr = tldr.strip()
        tldr_short = tldr[:295] + "…" if len(tldr) > 295 else tldr
        affected = _extract_section(p.body, "Am I affected?")
        affected_short = affected[:260] + "…" if affected and len(affected) > 260 else affected

        lines.append(f"## {p.title}")
        lines.append("")
        if tag_line:
            lines.append(f"_{tag_line}_")
            lines.append("")
        lines.append(f"URL: {_page_html_url(p)}")
        lines.append("")
        lines.append(tldr_short)
        lines.append("")
        if affected_short:
            lines.append("**Am I affected?**")
            lines.append("")
            lines.append(affected_short.strip())
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def _extract_section(body: str, section_title: str) -> str | None:
    """Return the body of `## <section_title>` until the next `## ` heading."""
    pattern = re.compile(
        rf"^##\s+{re.escape(section_title)}\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(body)
    if not m:
        return None
    return m.group(1).strip()


def build_sitemap(pages: list[Page]) -> str:
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        loc = _page_html_url(p)
        lastmod = str(p.frontmatter.get("last_updated") or today)

        # Frequency + priority hints for crawlers
        if p.output_path == Path("alerts.html") or p.output_path == Path("index.html"):
            changefreq = "daily"
            priority = "1.0"
        elif p.section == "advisories" and not p.is_index:
            changefreq = "monthly"
            priority = "0.8"
        elif p.section == "advisories" and p.is_index:
            changefreq = "weekly"
            priority = "0.9"
        elif p.section in {"playbooks", "prevention"}:
            changefreq = "monthly"
            priority = "0.7"
        else:
            changefreq = "monthly"
            priority = "0.5"

        lines.append("  <url>")
        lines.append(f"    <loc>{html.escape(loc)}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append('</urlset>')
    return "\n".join(lines)


def build_robots() -> str:
    return (
        "# Crawlers welcome. AI/LLM training: explicitly allowed.\n"
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )


def build_atom_feed(pages: list[Page]) -> str:
    advisories = [p for p in pages if p.section == "advisories" and not p.is_index]
    advisories.sort(key=lambda p: str(p.frontmatter.get("last_updated") or p.frontmatter.get("date_disclosed") or ""), reverse=True)

    # Determinism: use the most-recent advisory's last_updated as the feed
    # <updated>, not datetime.now(). This way two consecutive builds produce
    # identical output (only changes when source changes).
    feed_updated_date = (
        str(advisories[0].frontmatter.get("last_updated"))
        if advisories else date.today().isoformat()
    )
    feed_updated = (
        f"{feed_updated_date}T00:00:00Z" if len(feed_updated_date) == 10 else feed_updated_date
    )

    out: list[str] = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        f'  <title>{xml_escape(SITE_NAME_DISPLAY)}</title>',
        f'  <link href="{SITE_URL}/" rel="alternate"/>',
        f'  <link href="{SITE_URL}/feed.xml" rel="self"/>',
        f'  <id>{SITE_URL}/</id>',
        f'  <updated>{feed_updated}</updated>',
        f'  <subtitle>{xml_escape(SITE_TAGLINE)}</subtitle>',
        '  <generator>vibe-coding-security site builder</generator>',
    ]
    for p in advisories[:25]:
        url = _page_html_url(p)
        updated = str(p.frontmatter.get("last_updated") or p.frontmatter.get("date_disclosed") or feed_updated_date)
        if len(updated) == 10:
            updated = f"{updated}T00:00:00Z"
        out.append("  <entry>")
        out.append(f"    <title>{xml_escape(p.title)}</title>")
        out.append(f'    <link href="{url}"/>')
        out.append(f"    <id>{url}</id>")
        out.append(f"    <updated>{updated}</updated>")
        out.append(f"    <summary>{xml_escape(p.description)}</summary>")
        for tag in p.frontmatter.get("tags", []):
            out.append(f'    <category term="{xml_escape(str(tag))}"/>')
        out.append("  </entry>")
    out.append('</feed>')
    return "\n".join(out)


def build_search_index(pages: list[Page]) -> str:
    items = []
    for p in pages:
        url = f"/{p.output_path.as_posix()}"
        items.append({
            "title": p.title,
            "url": url,
            "section": p.section or "root",
            "description": p.description,
            "severity": p.frontmatter.get("severity", ""),
            "status": p.frontmatter.get("status", ""),
            "date_disclosed": str(p.frontmatter.get("date_disclosed", "")),
        })
    return json.dumps({"generated": date.today().isoformat(), "items": items}, indent=2)


def build_advisories_json(pages: list[Page]) -> str:
    data = []
    for p in pages:
        if p.section == "advisories" and not p.is_index:
            data.append({
                "id": p.frontmatter.get("id"),
                "title": p.title,
                "description": p.description,
                "severity": p.frontmatter.get("severity"),
                "status": p.frontmatter.get("status"),
                "date_disclosed": str(p.frontmatter.get("date_disclosed", "")),
                "last_updated": str(p.frontmatter.get("last_updated", "")),
                "ecosystems": p.frontmatter.get("ecosystems", []),
                "tools_affected": p.frontmatter.get("tools_affected", []),
                "tags": p.frontmatter.get("tags", []),
                "url": _page_html_url(p),
                "markdown_url": _page_md_url(p),
            })
    data.sort(key=lambda x: str(x.get("date_disclosed") or ""), reverse=True)
    return json.dumps({"generated": date.today().isoformat(), "advisories": data}, indent=2)


def build_advisory_schema() -> str:
    """JSON Schema (draft 2020-12) for advisory frontmatter."""
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SITE_URL}/advisory-schema.json",
        "title": "VibeCodingSecurityAdvisory",
        "description": "Frontmatter schema for an advisory under advisories/",
        "type": "object",
        "required": ["id", "title", "severity", "status", "date_disclosed", "last_updated"],
        "additionalProperties": True,
        "properties": {
            "id": {
                "type": "string",
                "pattern": "^[0-9]{4}-[0-9]{2}(-[a-z0-9-]+)?$|^ongoing-[a-z0-9-]+$",
                "description": "YYYY-MM-short-id or ongoing-short-id."
            },
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "severity": {"enum": ["critical", "high", "medium", "low"]},
            "status": {"enum": ["active", "contained", "patched", "mitigated", "ongoing", "historical", "unconfirmed"]},
            "date_disclosed": {
                "type": "string",
                "pattern": "^[0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?$",
                "description": "Date or partial date — YYYY, YYYY-MM, or YYYY-MM-DD."
            },
            "last_updated": {"type": "string", "format": "date"},
            "ecosystems": {"type": "array", "items": {"type": "string"}},
            "tools_affected": {"type": "array", "items": {"type": "string"}},
            "tags": {"type": "array", "items": {"type": "string"}},
            "description": {"type": "string"},
        },
    }
    return json.dumps(schema, indent=2)


def build_api_index() -> str:
    return json.dumps({
        "name": SITE_NAME,
        "version": "v1",
        "generated": date.today().isoformat(),
        "endpoints": {
            "advisories": f"{SITE_URL}/api/v1/advisories.json",
            "schema": f"{SITE_URL}/advisory-schema.json",
            "feed": f"{SITE_URL}/feed.xml",
            "sitemap": f"{SITE_URL}/sitemap.xml",
            "llms_index": f"{SITE_URL}/llms.txt",
            "llms_full": f"{SITE_URL}/llms-full.txt",
            "llms_compact": f"{SITE_URL}/llms-ctx.txt",
        },
        "docs": SITE_URL + "/",
        "source": REPO_URL,
        "license": "CC0-1.0",
    }, indent=2)


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

def main() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    template = (SITE_DIR / "template.html").read_text(encoding="utf-8")

    css = SITE_DIR / "style.css"
    if css.exists():
        shutil.copy(css, DIST_DIR / "style.css")

    # Copy .well-known/ verbatim (security.txt etc.)
    wellknown_src = REPO_ROOT / ".well-known"
    if wellknown_src.is_dir():
        shutil.copytree(wellknown_src, DIST_DIR / ".well-known")

    (DIST_DIR / ".nojekyll").touch()

    pages = discover_pages()
    preprocess(pages)

    # HTML pages + .md mirrors
    for page in pages:
        # HTML
        html_path = DIST_DIR / page.output_path
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(render_page(page, pages, template), encoding="utf-8")

        # Raw markdown mirror (frontmatter preserved if present)
        md_relpath = Path(str(page.output_path).replace(".html", ".md"))
        md_path = DIST_DIR / md_relpath
        md_path.write_text(page.raw_text, encoding="utf-8")

    # Site-wide LLM-friendly outputs. Build full + ctx first so the llms.txt
    # index can report their real byte sizes (keeps the "(~NKB)" annotations
    # honest as the corpus grows, instead of a hardcoded number that goes stale).
    llms_full = build_llms_full_txt(pages)
    llms_ctx = build_llms_ctx_txt(pages)
    (DIST_DIR / "llms.txt").write_text(
        build_llms_txt(pages, len(llms_full.encode("utf-8")), len(llms_ctx.encode("utf-8"))),
        encoding="utf-8",
    )
    (DIST_DIR / "llms-full.txt").write_text(llms_full, encoding="utf-8")
    (DIST_DIR / "llms-ctx.txt").write_text(llms_ctx, encoding="utf-8")

    # Per-section llms.txt
    for slug, label, _ in SECTIONS:
        section_pages = [p for p in pages if p.section == slug]
        if not section_pages:
            continue
        (DIST_DIR / slug / "llms.txt").write_text(
            build_section_llms_txt(slug, label, pages), encoding="utf-8"
        )

    (DIST_DIR / "sitemap.xml").write_text(build_sitemap(pages), encoding="utf-8")
    (DIST_DIR / "robots.txt").write_text(build_robots(), encoding="utf-8")
    (DIST_DIR / "feed.xml").write_text(build_atom_feed(pages), encoding="utf-8")
    (DIST_DIR / "search.json").write_text(build_search_index(pages), encoding="utf-8")
    (DIST_DIR / "advisories.json").write_text(build_advisories_json(pages), encoding="utf-8")
    (DIST_DIR / "advisory-schema.json").write_text(build_advisory_schema(), encoding="utf-8")

    # Versioned API
    api_dir = DIST_DIR / "api" / "v1"
    api_dir.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "api" / "index.json").write_text(build_api_index(), encoding="utf-8")
    (api_dir / "index.json").write_text(build_api_index(), encoding="utf-8")
    (api_dir / "advisories.json").write_text(build_advisories_json(pages), encoding="utf-8")

    print(f"Built {len(pages)} HTML pages + {len(pages)} .md mirrors → {DIST_DIR}")
    print("  + llms.txt, llms-full.txt, llms-ctx.txt")
    print("  + per-section llms.txt for", ", ".join(s[0] for s in SECTIONS))
    print("  + feed.xml, sitemap.xml, robots.txt")
    print("  + advisories.json, advisory-schema.json, search.json")
    print("  + api/v1/{index,advisories}.json")


if __name__ == "__main__":
    main()
