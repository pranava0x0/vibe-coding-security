#!/usr/bin/env python3
"""
Build the vibe-coding-security static site + LLM-friendly outputs.

Outputs (in dist/):
  - One HTML page per source .md file
  - style.css, .nojekyll
  - advisories.json — machine-readable index of all advisories
  - llms.txt — short index in llmstxt.org format
  - llms-full.txt — all advisories/playbooks/prevention concatenated
  - sitemap.xml — for search engines + LLM crawlers
  - robots.txt — explicit allow + sitemap pointer
  - search.json — minimal payload for a future client-side search

Each HTML page includes:
  - Semantic <article>, <header>, <nav>, <aside>, <main>, <footer>
  - <meta name="description"> per page (frontmatter or first paragraph)
  - Open Graph + Twitter card meta
  - JSON-LD SecurityAdvisory schema for advisory pages
  - Per-page table of contents (right rail at >=1200px, inline at smaller)
  - <time datetime=...> on all dates in meta

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
from datetime import date
from os.path import relpath
from pathlib import Path
from typing import Any

import markdown  # type: ignore
import yaml  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"
DIST_DIR = REPO_ROOT / "dist"

SITE_URL = "https://pranava0x0.github.io/vibe-coding-security"
REPO_URL = "https://github.com/pranava0x0/vibe-coding-security"
SITE_NAME = "vibe-coding-security"
SITE_TAGLINE = (
    "Living index of supply-chain attacks, malicious MCP servers, and "
    "prompt-injection campaigns relevant to vibe coding."
)

SECTIONS: list[tuple[str, str, str]] = [
    # (slug, label, source dir relative to repo root)
    ("advisories", "Advisories", "advisories"),
    ("playbooks", "Playbooks", "playbooks"),
    ("prevention", "Prevention", "prevention"),
    ("sources", "Sources", "sources"),
    ("tools", "Tools", "tools"),
]

TOP_LEVEL_PAGES: list[tuple[str, str]] = [
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
    output_path: Path
    title: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""
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


def derive_description(frontmatter: dict[str, Any], body: str) -> str:
    """First paragraph of body, stripped of markdown, max ~200 chars."""
    if frontmatter.get("description"):
        return str(frontmatter["description"]).strip()

    # Find TL;DR or first paragraph after first heading
    in_para = False
    buf: list[str] = []
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
    # Strip markdown
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
    """Rewrite markdown-style hrefs to their built equivalents.

    Algorithm:
      1. Skip external / mailto / anchor-only / data: hrefs.
      2. Normalize the href against the current page's repo path so we have
         a canonical repo-relative source path (with ../ resolved).
      3. If that canonical source is in source_to_output, rewrite to a
         current-page-relative URL pointing at the output file. This handles
         case sensitivity (ALERTS.md → alerts.html), README.md → index.html
         at any depth, and any other source-to-output renaming.
      4. Else if the canonical source exists in the repo at all, link to the
         canonical GitHub blob URL (covers .claude/, .github/, site/, raw
         JSON, etc.).
      5. Else fall back to the simple .md → .html rewrite (handles same-page
         anchors and otherwise-unknown paths gracefully).
    """
    github_blob = f"{REPO_URL}/blob/main"
    src_map = source_to_output or {}

    def make_relative(target_rel: Path) -> str:
        """Build a current-page-relative path to a dist file."""
        if current_relpath is None:
            return str(target_rel).replace("\\", "/")
        # Map current source's location to its output location to figure out
        # the right base for relative paths
        current_out = src_map.get(current_relpath)
        if current_out is None:
            # Top-level fallback
            current_out = Path("index.html")
        base_dir = current_out.parent if str(current_out.parent) != "." else Path(".")
        from os.path import relpath as _rp
        return _rp(target_rel, base_dir).replace("\\", "/")

    def replace(match: re.Match[str]) -> str:
        url = match.group(1)
        if url.startswith(("http://", "https://", "mailto:", "#", "data:", "javascript:")):
            return match.group(0)

        anchor = ""
        if "#" in url:
            url, anchor = url.split("#", 1)
            anchor = "#" + anchor

        # Resolve to a repo-relative path
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
            # Not built into the site, but exists in the repo → GitHub URL.
            if (REPO_ROOT / src_path).exists():
                return f'href="{github_blob}/{normalized}{anchor}" rel="noopener"'

        # Fall-through heuristics (unknown / can't be normalized)
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
    """Returns (html, toc_html, headings)."""
    md = markdown.Markdown(extensions=[
        "fenced_code",
        "tables",
        "toc",
        "sane_lists",
        "codehilite",
        "attr_list",
    ], extension_configs={
        "codehilite": {"css_class": "code", "guess_lang": False},
        "toc": {"toc_depth": "2-3", "permalink": False, "anchorlink": False},
    })
    html_out = md.convert(body)
    toc_html = md.toc  # type: ignore[attr-defined]
    # Extract headings for our own right-rail
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
    rel = relpath(target.output_path, current_dir)
    return rel.replace("\\", "/")


def build_sidebar(current: Page, all_pages: list[Page]) -> str:
    parts: list[str] = ['<nav class="sidebar-inner" aria-label="Site sections">']

    # Home
    home = next(p for p in all_pages if p.output_path == Path("index.html"))
    parts.append(_nav_link(home, current, "nav-home", "🏠 Home"))

    # Alerts (special)
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
    """Section breadcrumb for tablet (no sidebar visible)."""
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


# ────────────────────────────────────────────────────────────────────────────
# JSON-LD
# ────────────────────────────────────────────────────────────────────────────

def build_jsonld(page: Page, page_url: str) -> str:
    """Build JSON-LD for an advisory page; Article for everything else."""
    fm = page.frontmatter
    if page.section == "advisories" and not page.is_index:
        data = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": page.title,
            "description": page.description,
            "url": page_url,
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
            "keywords": ", ".join(fm.get("tags", []) + fm.get("ecosystems", [])),
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
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        }
    return '<script type="application/ld+json">' + json.dumps(data) + "</script>"


# ────────────────────────────────────────────────────────────────────────────
# Page discovery & rendering
# ────────────────────────────────────────────────────────────────────────────

def discover_pages() -> list[Page]:
    pages: list[Page] = []

    readme = REPO_ROOT / "README.md"
    if readme.exists():
        pages.append(Page(source_path=readme, output_path=Path("index.html"), title=SITE_NAME))

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


def preprocess(pages: list[Page]) -> None:
    """Parse frontmatter + body, render markdown, compute description, headings."""
    # Build source → output map for accurate link rewriting (handles case
    # sensitivity, README renames, and rejects unknown links to GitHub).
    src_map: dict[Path, Path] = {}
    for p in pages:
        try:
            src_map[p.source_path.relative_to(REPO_ROOT)] = p.output_path
        except ValueError:
            pass

    for p in pages:
        text = p.source_path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        p.frontmatter = fm
        p.body = body
        p.title = derive_title(fm, body, p.source_path)
        p.description = derive_description(fm, body)
        rendered, toc, headings = render_markdown(body)
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

    depth = len(page.output_path.parts) - 1
    asset_prefix = "../" * depth if depth else ""

    page_url = f"{SITE_URL}/{str(page.output_path).replace(chr(92), '/')}"
    if page.output_path == Path("index.html"):
        page_url = SITE_URL + "/"

    jsonld = build_jsonld(page, page_url)

    og_type = "article" if page.section == "advisories" and not page.is_index else "website"

    out = template
    repl = {
        "{{TITLE}}": html.escape(page.title),
        "{{DESCRIPTION}}": html.escape(page.description),
        "{{CANONICAL}}": html.escape(page_url),
        "{{OG_TYPE}}": og_type,
        "{{ASSET_PREFIX}}": asset_prefix,
        "{{SIDEBAR}}": sidebar,
        "{{BREADCRUMB}}": crumb,
        "{{META}}": meta_bar,
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

def build_llms_txt(pages: list[Page]) -> str:
    """llmstxt.org-format index."""
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
    ]

    sections_for_llms: list[tuple[str, str]] = [
        ("Active alerts", "alerts.html"),
        ("Advisories", "advisories/index.html"),
        ("Playbooks", "playbooks/index.html"),
        ("Prevention", "prevention/index.html"),
        ("Sources", "sources/index.html"),
        ("Tools", "tools/index.html"),
    ]

    # Advisories
    advisories = [p for p in pages if p.section == "advisories" and not p.is_index]
    advisories.sort(key=lambda p: str(p.frontmatter.get("date_disclosed", "")), reverse=True)

    lines.append("## Active alerts")
    lines.append("")
    lines.append(f"- [Alerts feed]({SITE_URL}/alerts.html): single scannable feed of all active, recent, and historical incidents")
    lines.append("")

    lines.append("## Advisories")
    lines.append("")
    for p in advisories:
        sev = p.frontmatter.get("severity", "")
        date_d = p.frontmatter.get("date_disclosed", "")
        url = f"{SITE_URL}/{str(p.output_path).replace(chr(92), '/')}"
        meta = f" [{sev}]" if sev else ""
        meta += f" {date_d}" if date_d else ""
        lines.append(f"- [{p.title}]({url}){meta}: {p.description}")
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
            url = f"{SITE_URL}/{str(p.output_path).replace(chr(92), '/')}"
            lines.append(f"- [{p.title}]({url}): {p.description}")
        lines.append("")

    lines.append("## Optional")
    lines.append("")
    lines.append(f"- [llms-full.txt]({SITE_URL}/llms-full.txt): every advisory, playbook, and prevention doc concatenated for ingestion")
    lines.append(f"- [advisories.json]({SITE_URL}/advisories.json): machine-readable advisory index with frontmatter")
    lines.append(f"- [GitHub source]({REPO_URL}): raw markdown, contribution guide, issue templates")
    lines.append("")

    return "\n".join(lines)


def build_llms_full_txt(pages: list[Page]) -> str:
    """Concatenated raw markdown of every advisory/playbook/prevention doc."""
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
            url = f"{SITE_URL}/{str(p.output_path).replace(chr(92), '/')}"
            out.append(f"---")
            out.append("")
            out.append(f"<!-- source: {p.source_path.relative_to(REPO_ROOT)} -->")
            out.append(f"<!-- canonical: {url} -->")
            out.append("")
            out.append(p.body.strip())
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


def build_sitemap(pages: list[Page]) -> str:
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        loc = f"{SITE_URL}/{str(p.output_path).replace(chr(92), '/')}"
        if p.output_path == Path("index.html"):
            loc = SITE_URL + "/"
        lastmod = str(p.frontmatter.get("last_updated") or today)
        lines.append("  <url>")
        lines.append(f"    <loc>{html.escape(loc)}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append('</urlset>')
    return "\n".join(lines)


def build_robots() -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )


def build_search_index(pages: list[Page]) -> str:
    items = []
    for p in pages:
        url = f"/{str(p.output_path).replace(chr(92), '/')}"
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
            url = f"{SITE_URL}/{str(p.output_path).replace(chr(92), '/')}"
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
                "url": url,
            })
    data.sort(key=lambda x: str(x.get("date_disclosed") or ""), reverse=True)
    return json.dumps({"generated": date.today().isoformat(), "advisories": data}, indent=2)


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

    (DIST_DIR / ".nojekyll").touch()

    pages = discover_pages()
    preprocess(pages)

    for page in pages:
        out_html = render_page(page, pages, template)
        out_path = DIST_DIR / page.output_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_html, encoding="utf-8")

    # LLM + crawler outputs
    (DIST_DIR / "llms.txt").write_text(build_llms_txt(pages), encoding="utf-8")
    (DIST_DIR / "llms-full.txt").write_text(build_llms_full_txt(pages), encoding="utf-8")
    (DIST_DIR / "sitemap.xml").write_text(build_sitemap(pages), encoding="utf-8")
    (DIST_DIR / "robots.txt").write_text(build_robots(), encoding="utf-8")
    (DIST_DIR / "search.json").write_text(build_search_index(pages), encoding="utf-8")
    (DIST_DIR / "advisories.json").write_text(build_advisories_json(pages), encoding="utf-8")

    print(f"Built {len(pages)} HTML pages → {DIST_DIR}")
    print("  + llms.txt, llms-full.txt, sitemap.xml, robots.txt, search.json, advisories.json")


if __name__ == "__main__":
    main()
