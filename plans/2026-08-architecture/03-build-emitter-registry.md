# Spec 03 — Software architecture: split `build.py` into an emitter registry

> **Theme:** refactor · **Effort:** medium · **Blocks:** nothing
> **Status:** proposed

## Problem

`site/build.py` is 1,178 lines and does eight unrelated jobs: frontmatter
parsing, markdown rendering, HTML chrome, JSON-LD, page discovery, seven flavours
of text/XML/JSON output, and orchestration.

It is not badly written — it is well-commented, deterministic by design, and
already carries hand-drawn section banners marking its own seams:

| Line | Banner | Span |
|---|---|---|
| 109 | Frontmatter + parsing | ~100 |
| 212 | Markdown rendering | ~80 |
| 294 | HTML helpers | ~175 |
| 471 | JSON-LD | ~50 |
| 524 | Page discovery & rendering | ~130 |
| 657 | LLM-friendly outputs | ~440 |
| 1098 | Main | ~80 |

The author has already done the categorisation work. The problem is that the
categories are enforced by comment rather than by module, which produces three
concrete costs:

**Adding an output means editing `main()`.** Every one of Spec 02's four new
outputs — `iocs.json`, `iocs.ndjson`, `iocs.csv`, `osv/*.json`, `integrity.txt` —
appends another hand-written `(DIST_DIR / "x").write_text(build_x(pages))` line to
an already 78-line `main()`. That function is on track to become the longest in
the file, and it is the one place where forgetting a line silently ships an
incomplete site.

**The "LLM-friendly outputs" banner is a lie.** It spans lines 657–1096 and
contains `build_sitemap`, `build_robots`, `build_atom_feed`, `build_search_index`,
`build_advisories_json`, `build_advisory_schema`, and `build_api_index` — none of
which are LLM-related. The banner stopped describing its contents some time ago
and nothing caught it, which is exactly what comment-enforced structure does.

**Ordering constraints are invisible.** `main()` must build `llms-full.txt` and
`llms-ctx.txt` *before* `llms.txt`, because the index reports their byte sizes.
That is documented in a comment. Spec 02 adds a second, stronger constraint —
`integrity.txt` must be written strictly last. Two implicit ordering rules
enforced by comment placement is one more than is safe.

## Proposal

Split into a package with an explicit emitter registry. Each output declares
itself; `main()` runs the registry.

### Target layout

```
site/
  build.py            # thin entry point: python3 site/build.py still works
  builder/
    __init__.py
    config.py         # SITE_URL, SECTIONS, SITE_NAME, paths  (from lines 42–90)
    page.py           # Page dataclass, discover_pages, preprocess
    frontmatter.py    # parse_frontmatter, derive_title, derive_description
    markdown_render.py# rewrite_links, render_markdown, _walk_toc
    chrome.py         # badges, sidebar, meta bar, toc, breadcrumb, page actions
    jsonld.py         # build_jsonld
    render.py         # render_page
    registry.py       # the Emitter protocol + register decorator
    emitters/
      __init__.py     # imports every module below, so registration happens
      pages.py        # HTML pages + .md mirrors
      llms.py         # llms.txt, llms-full, llms-ctx, per-section
      feeds.py        # sitemap.xml, feed.xml, robots.txt
      data.py         # search.json, advisories.json, advisory-schema.json
      api.py          # api/v1/*
      integrity.py    # integrity.txt   (Spec 02)
      iocs.py         # iocs.{json,ndjson,csv}   (Spec 02)
      osv.py          # osv/*.json + all.zip     (Spec 02)
```

The module boundaries follow the existing banners almost exactly. This is
deliberate: the seams are already known-good, and a refactor that invents new
boundaries is a refactor that has to justify them.

### The registry

```python
# builder/registry.py
from dataclasses import dataclass, field
from typing import Callable, Protocol

class Emitter(Protocol):
    def __call__(self, ctx: "BuildContext") -> None: ...

@dataclass(frozen=True)
class Registration:
    fn: Emitter
    name: str
    order: int          # lower runs first; ties broken by name for determinism
    description: str

_REGISTRY: list[Registration] = []

def emitter(*, name: str, order: int = 100, description: str = "") -> Callable:
    def decorate(fn: Emitter) -> Emitter:
        _REGISTRY.append(Registration(fn, name, order, description))
        return fn
    return decorate

def all_emitters() -> list[Registration]:
    return sorted(_REGISTRY, key=lambda r: (r.order, r.name))
```

Usage:

```python
# builder/emitters/llms.py
@emitter(name="llms", order=20, description="llms.txt, llms-full.txt, llms-ctx.txt")
def emit_llms(ctx: BuildContext) -> None:
    full = build_llms_full_txt(ctx.pages)
    compact = build_llms_ctx_txt(ctx.pages)
    ctx.write("llms-full.txt", full)
    ctx.write("llms-ctx.txt", compact)
    ctx.write("llms.txt", build_llms_txt(ctx.pages, len(full.encode()), len(compact.encode())))
```

Note what this fixes: the full-before-index ordering constraint is now *inside*
one function where it is locally obvious, rather than spread across `main()`
where it depends on statement order.

### `BuildContext`

```python
@dataclass
class BuildContext:
    dist: Path
    pages: list[Page]
    template: str
    written: list[Path] = field(default_factory=list)

    def write(self, relpath: str | Path, content: str) -> None:
        p = self.dist / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        self.written.append(p)
```

Routing every write through `ctx.write` gives two things for free:

1. **`integrity.txt` becomes trivial and correct.** It reads `ctx.written` rather
   than walking `dist/`, so it can never race an emitter that writes late.
2. **The build can report what it produced** without the seven hand-maintained
   `print()` lines at the end of `main()`, which are already drifting from what
   is actually emitted.

### `order` values

| Range | Purpose |
|---|---|
| 0–19 | Page rendering — everything else may depend on pages existing |
| 20–79 | Independent data outputs (llms, feeds, data, api, iocs, osv) |
| 80–98 | Outputs that read other outputs |
| 99 | `integrity.txt` — always last, enforced by a test |

Ordering is now data, and can be asserted:

```python
def test_integrity_emitter_runs_last():
    assert all_emitters()[-1].name == "integrity"
```

### `main()` after

```python
def main() -> None:
    ctx = prepare_dist()
    for reg in all_emitters():
        reg.fn(ctx)
    report(ctx)
```

---

## The refactor gate: byte-identical output

**This refactor must not change a single byte of `dist/`.** That is the whole
safety argument — it lets a 1,178-line restructure land without content review.

### Procedure

Run every build with the date pinned (see "Date-dependent outputs" below — this
is required, not optional):

```bash
export SOURCE_DATE_EPOCH_DATE=2026-08-03

# 1. Snapshot the pre-refactor output.
git checkout main -- site/
python3 site/build.py
find dist -type f -exec sha256sum {} + | sed 's| dist/| |' | sort > /tmp/before.sha

# 2. Apply the refactor.
git checkout <refactor-branch> -- site/
python3 site/build.py
find dist -type f -exec sha256sum {} + | sed 's| dist/| |' | sort > /tmp/after.sha

# 3. The gate.
diff /tmp/before.sha /tmp/after.sha && echo "BYTE-IDENTICAL ✓"
```

An empty diff is the pass condition. Anything else means the refactor changed
behaviour and must be investigated before merging — no exceptions, no "that
change is fine."

### Two things that will break this, and their fixes

**Date-dependent outputs — do this first.** `date.today()` is embedded in more
places than it looks:

- `build_search_index`, `build_advisories_json`, `build_api_index` — a
  `"generated"` key each.
- **`render_page` ([site/build.py:645](../../site/build.py))** — the
  `{{BUILD_DATE}}` footer substitution, which lands in **all 137 HTML pages**.

So a snapshot taken yesterday differs from one taken today in essentially every
file in `dist/`. The gate is unusable until this is fixed — it is a prerequisite,
not a caveat.

Fix: make the build date injectable, as a small standalone PR **before** the
refactor starts:

```python
BUILD_DATE = os.environ.get("SOURCE_DATE_EPOCH_DATE") or date.today().isoformat()
```

Then both snapshots run with the same pinned value:

```bash
SOURCE_DATE_EPOCH_DATE=2026-08-03 python3 site/build.py
```

This is a real improvement independent of the refactor — it makes the whole build
reproducible, which is squarely on-mission for a repo that publishes an integrity
manifest, and it means any future change can be diffed the same way.

**Dict iteration order in JSON.** Python dicts preserve insertion order and
`json.dumps` follows it, so reordering keys while moving code between modules
silently changes output. Move key construction verbatim; do not "tidy" it.

### Sequencing

Do this refactor **before** Spec 02's new emitters, not after. Adding three new
outputs to the current `main()` and then splitting is strictly more work than
splitting and then adding them to a registry — and the byte-identical gate only
works cleanly when the two sides emit the same set of files.

If Spec 02 has already started, land the mechanical split first with the existing
emitters, then rebase Spec 02's outputs onto the registry.

### Stage it

One PR per stage, each independently byte-identical:

1. Create `builder/` package; move config + `Page` + frontmatter + markdown.
   `build.py` re-imports them. No behaviour change.
2. Move chrome, JSON-LD, render.
3. Introduce `registry.py` and `BuildContext`; convert `main()` to the loop with
   emitters still defined in place.
4. Split emitters into `emitters/*.py`.

Four small diffs each provably identical beat one large diff that is merely
plausibly identical.

---

## Test changes

Tests currently import from `build`. After the split some will need to import
from `builder.*`. Keep re-exports in `site/build.py` so the entry point and any
external caller keep working:

```python
# site/build.py
from builder.config import *          # noqa: F401,F403
from builder.registry import all_emitters
from builder.emitters import *        # noqa: F401,F403  — triggers registration
```

Check `tests/test_build.py` and `tests/test_rewriter.py` for direct imports and
update paths there rather than contorting the package layout to preserve them.

New tests:

- `test_registry.py::test_every_emitter_has_unique_name`
- `test_registry.py::test_integrity_emitter_runs_last`
- `test_registry.py::test_emitter_order_is_deterministic` — `all_emitters()`
  returns the same sequence across calls
- `test_build.py::test_all_expected_outputs_written` — assert against
  `ctx.written` rather than a hardcoded list

---

## Done when

- [ ] `site/builder/` package exists with the layout above.
- [ ] Every output goes through a registered emitter; `main()` is the loop.
- [ ] Every write goes through `ctx.write`.
- [ ] Build date is injectable (shipped first, as its own PR); two builds on
      different days with the same `SOURCE_DATE_EPOCH_DATE` are identical.
- [ ] Byte-identical gate passes on the full `dist/` tree.
- [ ] `python3 site/build.py` still works unchanged from the repo root.
- [ ] `validate.py` unchanged and passing — it reads `dist/`, which did not change.
- [ ] 302 existing tests pass, plus the new registry tests.

## Explicitly out of scope

- Behaviour changes of any kind. Bugs noticed during the move get logged to
  ISSUES.md and fixed in a separate PR, so the gate stays meaningful.
- Rewriting `validate.py`. It is 315 lines with one clear job and does not have
  this problem.
- Performance work. The build takes seconds; there is nothing to fix.
- Swapping the markdown library or template engine.
