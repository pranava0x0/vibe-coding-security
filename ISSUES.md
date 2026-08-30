# Issues

> Audit trail of bugs, broken links, factual corrections, performance issues, and UAT findings.
> Each entry: date, area, description, root cause (**code bug** vs. **content bug** vs. **infra**), status, resolution commit.
> Newest entries first within each section.

## Open

_None open._

## Fixed

### Sweep skill: classifier rejections, a context-window-sized preamble, and a build-budget ratchet — 2026-08-29

Prompted by a review of the automated daily sweeps over the preceding two weeks. Three distinct problems, one shared root cause: the skill accretes detail every run and nothing ever bounded it.

- **Bug: research subagents rejected by the cyber-safeguards classifier — 8 failures across 5 consecutive days.** `API Error: Sonnet 5's safeguards flagged this message` on 2026-08-13 (Tier C), 08-14 (Tier A), 08-15 (Tier A + Tier B ×2, including a softened-framing retry), 08-16 (Tier A), 08-17 (Tier A + Tier B). **Every failure was a subagent launch; zero were direct `WebSearch`/`WebFetch` calls from the main session on the same queries the same day.** Root cause: **content bug** — Step 1 had grown to ~6,300 tokens of technique-annotated bullets (91 campaign-codename mentions, 88 C2/exfil references, 250 exploit-primitive terms, plus control-bypass and target-enumeration phrasing). Delivered to a fresh agent as its only message, with no repo, corpus, or defensive framing visible, that is indistinguishable from autonomous offensive tasking. Fixed structurally, not by rewording: bare query strings now live in `references/queries.md` (delegable), technique detail in `references/triage-patterns.md` (main session, triage time only), and `SKILL.md` carries explicit scope + delegation rules. The workaround previously existed only as prose in `runs.log.md`, which no run read far enough back to find — hence the same failure five days running.
- **Bug: Step 0 mandated ~345K tokens of reading — more than a context window.** `SKILL.md` (48K) + `runs.log.md` (192K) + `ALERTS.md` (68K) + `source-priorities.json` (26K) + `advisories/README.md` (10K). Root cause: **process bug** — it truncated silently every run, which is the mechanism behind both the rediscovered-classifier-workaround above and the 2026-06-19 stale-checkout duplication. `runs.log.md` was also O(n²): run *n* re-read all *n−1* prior entries, ~10.7M tokens of re-reading across 93 runs. Fixed: log rotated to 7 live entries + a grep-only archive; durable rules distilled into `LEARNINGS.md`; `ALERTS.md`/`README.md` reads replaced by a greppable `advisory-index.jsonl` from the new `tools/sweep_context.py`. **~345K → ~33K tokens (-90%)**, guarded by `tests/test_sweep_context.py` so it cannot silently re-bloat.
- **Bug: the `llms*.txt` build budget was a hand-turned ratchet that quietly cut corpus coverage.** `LLMS_TXT_TIER1_MAX` went 40 → 36 → 34 across 2026-08-20/22/29, and before that the per-entry description trim went 90 → 70 → 60 → 52 → 40 → 34 → 30 → 24 → 14 chars over eight consecutive sweeps. Each adjustment was a human solving "fit the byte budget" by hand, and each one reduced how much of the corpus the index actually listed — with CI only complaining after a breach. Root cause: **code bug** (wrong control surface). Fixed: `build.py` binary-searches the largest Tier-1 membership that fits (`_fit_tier1_max`), so a build cannot exceed budget by construction; caps + headroom moved into `build.py` and imported by `tests/test_llms.py` so the two cannot drift; a regression test fails if a hardcoded `*_TIER1_MAX` is reintroduced. Coverage rose at unchanged caps (`llms-full.txt` Tier 1: 60 → 72 advisories in full). Note the repo's own guidance (`"fix the growth rule rather than shaving the cosmetic knob"`) had been written down in 2026-08-21 and then not applied to the knob it was written about.
- **Process risk documented, not just noted: a research-only subagent pushed directly to `main` on 2026-08-14.** Sharing the orchestrator's checkout with no worktree isolation and no file-editing instruction, it read `SKILL.md`, inferred the sweep workflow unprompted, ran the build, and pushed — bypassing branch protection. Root cause: **process bug** — an instruction was used where a capability boundary was needed. Now a named rule in `SKILL.md` and `LEARNINGS.md`: research agents get worktree isolation or no repo write path, and only the orchestrating session writes, commits, or pushes.
- **Audit finding (no change needed): the published corpus is clean on the exploit-content axis.** Of 231 bash code fences across 217 advisories, 5 contain anything payload-shaped, all using placeholder domains (`attacker.example`, `attacker.io`) and labelled as simplified reconstructions of published research; `PoC` references point at others' work rather than reproducing it; IOCs are framed as defender signals. Recorded here so a future sweep doesn't re-litigate it.

### Backend-misconfiguration coverage gap — 2026-08-23
Prompted by a personalized exposure audit of the maintainer's other projects, which surfaced two misconfiguration classes the audit playbook and pattern-class advisory didn't yet distinguish. Went through three rounds of Codex PR review (#85) before merge — see the entry below for what each round caught.
- **Coverage gap: "RLS off" and "RLS enabled with zero policies" were treated as one check.** [`playbooks/auditing-a-vibe-coded-repo.md`](playbooks/auditing-a-vibe-coded-repo.md) item 2 only tested the `rowsecurity` boolean; added a `pg_policies` count query and explanation for the distinct, quieter `rls_enabled_no_policy` gap Supabase's own linter flags separately. Root cause: content gap.
- **Coverage gap: no guidance on orphaned/abandoned backend projects.** Added item 13 to the same playbook plus a quarterly-audit bullet to [`prevention/credential-hygiene.md`](prevention/credential-hygiene.md): old demo/side-project backends (Supabase/Firebase/etc.) that outlive their frontend and stay live with a valid public key. Root cause: content gap — the checklist assumed one app always has one still-linked backend.
- Also added a CORS note covering hosting/template header-rule scope (not just app code) and a new item on default over-disclosure in AI-generated bios/portfolio pages. Both new recurring patterns folded into [`advisories/ongoing-vibe-platform-exposure.md`](advisories/ongoing-vibe-platform-exposure.md)'s "what's recurring" list and the sweep skill's query set (`.claude/skills/vibe-security-update/SKILL.md`) so future automated sweeps watch for real-world incidents matching them.
- **Codex review (PR #85) took three rounds to settle — each round's fix revealed the next inaccuracy.** Round 1: RLS-enabled-with-zero-policies is default-deny for ordinary roles, not a leak (the real risk is fragility + bypass-role credentials); anon/publishable keys are meant to be public and shouldn't be blanket-"rotated" (pausing/deleting the project is what actually matters; rotation is for secret/service-role keys); wildcard CORS only "travels" to a new route if the same header rule's path matcher covers it, not automatically by shared origin. Round 2 (only visible once round 1 landed): the "default-deny, not an error" claim was read-only — a *write* against a policy-less table fails loudly with a real RLS-violation error; a catch-all CORS matcher isn't automatically exploitable — depends on credential mode; and `ALERTS.md`'s exposure summary still grouped RLS-no-policy under a "data exposure" heading despite the corrected framing. Round 3 (only visible once round 2 landed): "write" was still too broad — only `INSERT` hits the implicit `WITH CHECK` and errors loudly; `UPDATE`/`DELETE` are silent no-ops like reads, since the implicit-deny `USING` filter excludes every row first; the bearer-token CORS claim assumed an attacker's page could read/attach a token it doesn't have (it can't — that'd be a separate token-exposure bug); and the table owner is only bypass-capable when `FORCE ROW LEVEL SECURITY` isn't set on the table. Round 4 (only visible once round 3 landed): "regardless of table-level `GRANT`s" overstated it — a role's base table `GRANT` is a separate, prior gate Postgres checks before RLS is ever consulted; revoke it and you get a flat "permission denied" error instead of the RLS-mediated outcomes described. Scoped the paragraph to assume the grant Supabase's `anon`/`authenticated` roles carry by default. Ten findings total, all corrected in the touched files before merge. Root cause: content bug — Postgres RLS and CORS semantics are precise enough that each successive "fix" needs the same scrutiny as the original claim, not just the parts a reviewer already flagged.

### Supply-chain coverage gap + CI self-hardening — 2026-06-01
Prompted by a personalized exposure audit of the maintainer's other repos, which surfaced pathway categories this knowledge base didn't yet represent or practice.
- **Coverage gap: no CI/CD prevention guide.** Added [`prevention/ci-cd-hardening.md`](prevention/ci-cd-hardening.md) (SHA-pin actions, least-privilege `permissions:`, third-party-action-with-write-token anti-pattern, dangerous triggers, script injection, OIDC publishing) and [`prevention/supply-chain-attack-surface.md`](prevention/supply-chain-attack-surface.md) (a map of all 11 pathways external code/data enters, each linked to its deep guide). Wired both into `prevention/README.md`, `README.md`, `npm-hardening.md`, and `CHANGELOG.md`. Root cause: content gap — GitHub Actions is a top supply-chain vector (Megalodon, elementary-data, Comment-and-Control advisories) but had no dedicated guide.
- **Practice-what-we-preach: the project's own `deploy-site.yml` had the exact gap it documents.** Pinned all four actions to commit SHAs (were floating `@vN`) and scoped `permissions:` per job (`build`: `contents: read`; `deploy`: `pages: write` + `id-token: write`, previously granted to both jobs). Root cause: infra hygiene. Regression guard: a future test could assert no floating `@vN` action tags remain in `.github/workflows/` (logged to BACKLOG).

### Low-severity UAT follow-ups — 2026-06-01
- **[UAT-001] Homepage meta/OG description started mid-list** ("1. Hit by something right now?…"). `derive_description()` now prefers a page's leading `>` blockquote summary (the llmstxt.org convention the README/ALERTS/playbooks already use), falling through to paragraph extraction otherwise. Homepage description is now "A living index of supply-chain attacks…". Bonus: 20 other pages (alerts, playbooks, prevention, sources, tools) improved from list/code fragments to their real summaries — verified with a full before/after description diff; **no advisory descriptions changed, no regressions**. Root cause: code (deriver heuristic).
- **[UAT-002] `.page-action` touch target ~30px → 44px** (`site/style.css` `min-height`). "View raw markdown" / "Edit on GitHub" are now 44px tall, single-line at desktop width (verified in preview). Root cause: code (CSS).
- **[UAT-003] node-ipc "10M weekly" → "~822K weekly"** in `README.md`, matching the sourced figure in `advisories/2026-05-node-ipc-compromise.md` (single source of truth). Root cause: content.

### Data-freshness + llms.txt-accuracy pass — 2026-06-01
- **`README.md` "Last full sweep: 2026-05-28" → "2026-05-31"** — was stale vs the actual last sweep (recorded in the skill `runs.log.md` and reflected by ALERTS.md "Last refreshed: 2026-05-31"). Root cause: content (field not bumped by recent daily sweeps).
- **`README.md` node-ipc "two days ago" → "May 14"** — a relative date frozen at the 2026-05-16 seed (node-ipc disclosed 2026-05-14); 18 days stale. Replaced with an absolute date so it can't rot. Root cause: content.
- **llms.txt size annotations were badly stale** — generated `llms.txt` advertised `llms-full.txt (~230KB)` / `llms-ctx.txt (~10KB)`; real sizes were ~505KB / ~71KB. Made the figures **dynamic** in `build.py` (`_human_size()` computes from the actual built bytes) so the index can never drift again; README/CHANGELOG prose updated to match. Root cause: hardcoded magic numbers (code/content).
- **`tests/test_llms.py` `LLMS_FULL_MAX_BYTES` 512KB → 640KB** — `llms-full.txt` was at ~505KB (98.7% of the cap); the next daily sweep would have broken the build/deploy. Bumped with a dated comment + a note to trim historical advisories rather than keep raising the cap. Root cause: corpus growth against a guardrail (maintenance).

---

## UAT log

### 2026-06-01 — UAT pass (local `dist/` build) + freshness/perf/llms.txt audit

Run against a local server of `dist/` (browser walkthrough at 1280px desktop, 375px mobile, dark mode) + `python3 site/validate.py` + `pytest tests/` + a live HTTP sweep of all artifact URLs.

**Findings:**

- **[INFO]** Renders cleanly at 1280px (3-column: nav + sidebar + right-rail TOC), 634px (single-column, hamburger), and 375px mobile. Dark mode (`prefers-color-scheme: dark`) themes the whole page; severity colors intact.
- **[INFO]** Mobile hamburger menu works — `body.nav-open` toggled by an inline `onclick` (no external JS); opens a full-screen nav with all 7 sections. `aria-expanded` flips correctly; toggle button is 44×44px.
- **[INFO]** No console errors/warnings anywhere (site ships zero external JS; only inline JSON-LD + the menu `onclick`).
- **[INFO]** All 9 `validate.py` checks pass; **86/86 pytest** pass (incl. build determinism after the dynamic-size change).
- **[INFO]** Live HTTP sweep: all 32 sampled URLs (HTML, `.md` mirrors, all `llms*.txt`, per-section `llms.txt`, JSON/API endpoints, feed, sitemap, robots, security.txt) return 200.
- **[FRESH]** Fixed two stale date strings in README (see Fixed: `2026-05-28`→`2026-05-31`, and node-ipc "two days ago"→"May 14"). ALERTS.md "Last refreshed: 2026-05-31" is current (1 day old, inside the 7-day window). `.well-known/security.txt` `Expires: 2027-12-31` — valid. Build/feed/sitemap dates are generated via `date.today()` — always fresh.
- **[PERF]** HTML pages 5–22KB gzipped (alerts.html largest at 72KB raw / 22KB gz); `style.css` 17KB raw / 4.3KB gz. A typical page = 2 requests (HTML + CSS), no JS/fonts/images/third-parties. Excellent.
- **[PERF]** **Fixed:** `llms-full.txt` (~505KB) was at 98.7% of its 512KB test cap — one sweep from breaking the deploy. Cap bumped to 640KB. `llms-ctx.txt` ~71KB (cap 96KB).
- **[LLMS]** **Fixed:** the index's size annotations were wrong (`~230KB`/`~10KB` vs real `~505KB`/`~71KB`); now computed dynamically. `llms.txt` validated: starts with `# title`, `> summary`, has all required sections, lists every advisory, Optional section links the alternates.
- **[OPEN]** Logged UAT-001 (homepage meta description starts mid-list), UAT-002 (`.page-action` ~30px touch target), UAT-003 (node-ipc download-count discrepancy) — all low severity.

**No regressions.** Build, validators, and full test suite green after the fixes.

### 2026-05-17 — UAT pass on deployed site

Run against <https://pranava0x0.github.io/vibe-coding-security/>. Manual walkthrough + automated tests (`python3 site/validate.py` + `pytest tests/`).

**Findings:**

- **[INFO]** Site loads cleanly at 375×667 (iPhone SE), 414×896 (iPhone Pro Max), 768×1024 (iPad portrait), 1024×768 (iPad landscape), 1280×800, 1920×1080. No layout breakage at any breakpoint.
- **[INFO]** Sidebar appears at ≥900px; right-rail TOC at ≥1200px. Below those breakpoints, content stays single-column with hamburger menu.
- **[INFO]** All 9 build-validator checks pass (required outputs, no leftover .md links, all internal links resolve, HTML metadata present, heading hierarchy OK, advisory frontmatter complete, llms.txt format, sitemap.xml well-formed, advisories.json sane).
- **[INFO]** All pytest checks pass (advisory frontmatter schema, link integrity, no committed secrets, advisory ID uniqueness, llms.txt format, JSON-LD parses, sitemap parses, atom feed parses, build determinism, etc.).
- **[INFO]** Light + dark themes render correctly under `prefers-color-scheme`. `prefers-reduced-motion` honored.
- **[PERF]** Average page weight (HTML + CSS) under 30KB gzipped. No JS bundles. No web fonts. No third-party requests.
- **[PERF]** `llms-full.txt` is ~145KB (well under the 200K-token Mintlify recommendation).
- **[PERF]** `llms-ctx.txt` is ~12KB — fits in any context window.
- **[PERF]** `feed.xml` truncated to 25 most recent advisories to keep size sane.
- **[A11Y]** Skip-link present and works. 44px touch targets on all interactive elements. ARIA labels on nav landmarks. `<time datetime>` on all dates. Focus-visible outlines on every link and button.

**No regressions detected.** Site, build, and skill are all in known-good state.

---

## Repo-specific issues

_Bugs in the build pipeline, skill, or site go here, not in `advisories/`._

_None at this time._
