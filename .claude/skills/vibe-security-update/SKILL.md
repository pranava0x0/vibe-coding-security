---
name: vibe-security-update
description: Sweep current security threats relevant to vibe coding (supply-chain attacks, malicious MCPs, prompt injection campaigns, AI-tool CVEs) and refresh ALERTS.md + advisories/. Trigger when the user says "update the security data", "refresh the sweep", "/vibe-security-update", or any phrase about updating the vibe-coding-security feed. Uses tiered search depth (deep 24h / medium 3d / shallow 7d) and a self-learning source-priority list to focus future runs on sources that produce hits.
---

# vibe-security-update

You are running a fresh sweep of vibe-coding-relevant security incidents and integrating findings into this repo. The repo is `vibe-coding-security/` and you are at its root.

## Output for the user (always include at end)

A 5-line summary:
1. Date of this sweep
2. # of new advisories added
3. # of existing advisories updated (status, IOCs, sources)
4. # of new sources discovered + added to priority list
5. Link to commit (if pushed)

---

## Process

### Step 0 — Load state

Read these files (all required):

- `ALERTS.md` — current active/recent/historical feed
- `advisories/README.md` — index
- `.claude/skills/vibe-security-update/source-priorities.json` — ranked sources
- `.claude/skills/vibe-security-update/runs.log.md` — prior runs

Set:
- `today` = current absolute date (YYYY-MM-DD)
- `t_24h` = today − 1 day
- `t_3d` = today − 3 days
- `t_7d` = today − 7 days

### Step 1 — Tiered web research (in parallel)

Run these in **a single message with parallel WebSearch calls**. Three depth tiers:

**Tier A — DEEP (24h window).** Comprehensive. Aim for ~8 parallel queries. Cover:
- "npm supply chain attack {today.year}" + last 24h
- "malicious npm package compromise {today.year}"
- "malicious mcp server {today.year}"
- "Cursor vulnerability CVE {today.year}"
- "Claude Code vulnerability prompt injection {today.year}"
- "Lovable / Bolt / v0 / Replit security {today.year}"
- "AI coding assistant security incident {today.year}"
- "PyPI malicious package supply chain {today.year}"
- "AI agent framework CVE {today.year}" — rotate framework names: Semantic Kernel / LangChain / OpenClaw / PraisonAI / Langflow / aider / OpenHands / SWE-agent. As of 2026-Q2 this is a top attack-surface category (decorator-as-documentation pattern → RCE).

For each query, prepend top sources from `source-priorities.json` (top 10 by weight) via the `allowed_domains` filter on rotating subsets so we don't miss high-signal pages buried under news aggregators.

**Tier B — MEDIUM (3-day window).** ~4 parallel queries on top-weight sources:
- "{top-3-source-domains} supply chain"
- "GitHub Advisory Database npm critical"
- "Shai-Hulud OR mini-shai-hulud cross-ecosystem npm pypi {today.year}"
- "{tool-vendor} security advisory" — rotate vendor across:
  - **IDEs/agents:** Cursor, Anthropic (Claude Code), Windsurf, Google (Antigravity), Cline, aider, OpenHands, OpenClaw
  - **Vibe-coding platforms:** Lovable, Bolt, v0, Replit, Base44
  - **Web frameworks:** Vercel (Next.js), React/Meta, Svelte, Tailwind, Vite
  - **Backend/Auth/DB:** Supabase, Prisma, NextAuth.js, FastAPI, Streamlit, Google AI Studio SDK
  - **Agent SDKs:** Microsoft (Semantic Kernel), LangChain, PraisonAI
- "{vendor} coordinated security release {today.year}" — catches multi-CVE rollups (Vercel May 2026 shipped 13 in one batch; Anthropic similar cadence post-source-leak).

**Tier C — SHALLOW (7-day window).** ~3 parallel queries to catch slower-moving stories and social-media disclosure:
- "vibe coding security incident week {today.year}"
- "AI agent CVE OR security disclosed {today.year}"
- "vibe coding security site:substack.com OR site:x.com OR site:bsky.app {today.year}" — Substack newsletters (vibecodingweekly, mvidmar, ipenewsletter) and security-research X/Bluesky posts (StepSecurity, Snyk, Aikido, Socket) regularly break new IOCs hours before traditional aggregators pick them up. Also probe `news.ycombinator.com` and `reddit.com/r/{programming,netsec,cybersecurity}` discussions for first-hand reports.

Don't repeat queries already run within the last 24h (check `runs.log.md`).

### Step 2 — Triage findings

For each unique candidate incident pulled from results, decide:

**A. NEW ADVISORY** — write a new file in `advisories/` if:
- Package > 100k weekly downloads compromised, OR
- CVE in major AI coding tool, OR
- CVE in major AI-agent framework SDK (LangChain, Semantic Kernel, PraisonAI, OpenClaw, etc.), OR
- CVE in core vibe-coding web stack (Next.js, React, Svelte, Vite, Tailwind, FastAPI, Streamlit, Prisma, NextAuth.js, Supabase) with practical exploitation path, OR
- Malicious MCP server, OR
- Prompt-injection PoC against vibe-coding tool, OR
- Vibe platform data exposure with PII impact, OR
- Cross-ecosystem worm (npm ↔ PyPI ↔ RubyGems with identical payload), OR
- Significant supply-chain hygiene incident at a major AI vendor (e.g., source-map leak, accidental token exposure)

Use the template in `CONTRIBUTING.md`. Filename: `YYYY-MM-short-id.md`.

**B. UPDATE EXISTING** — append to an existing advisory if:
- Status changed (active → contained, etc.)
- New IOCs published
- New sources strengthen / correct the writeup
- Patched version released

Always bump `last_updated` in frontmatter when touched.

**C. SKIP** — log but don't write up if:
- Already covered in an existing advisory with no new info
- Not relevant to vibe coding audience (e.g., kernel CVE, generic enterprise vuln)
- Single unconfirmed source (need ≥2 independent for a full advisory)

### Step 3 — Update ALERTS.md

For every NEW or UPDATED advisory:

- Insert/move into the right tier (🔴 active / 🟠 recent / 🟡 historical) by date:
  - 🔴 active = last 14 days OR malware still propagating
  - 🟠 recent = last 12 months
  - 🟡 historical = older OR pattern-class
- Update the `Last refreshed:` date at the top of ALERTS.md.
- Maintain latest-on-top within each tier.

### Step 4 — Update source priorities (the learning step)

For each source domain that contributed to a NEW or UPDATED advisory this run:

```python
# Pseudocode
src = source_priorities["sources"][domain]
src["hits"] += 1
src["last_hit"] = today
src["weight"] = min(20, src["weight"] + 1)   # cap at 20
src["ecosystems"] = unique(src.get("ecosystems", []) + new_ecosystems)
```

For sources NOT seen in any run for >60 days, decay weight by 1 (min 1). This keeps the list responsive to changing landscape.

For NEW sources discovered this run (not yet in the list), add with `weight: 5, hits: 1, last_hit: today, ecosystems: [...]`.

Write the updated JSON back. Sort by weight desc for readability.

### Step 5 — Append to runs.log.md

Add an entry:

```markdown
## YYYY-MM-DD

- **Queries run:** N (deep: a, medium: b, shallow: c)
- **New advisories:** [list of IDs] or "none"
- **Updated advisories:** [list of IDs] or "none"
- **Sources gained weight:** [list of domains]
- **New sources added:** [list of domains]
- **Notes:** [anything noteworthy — false-alarms, blocked domains, sweep duration]
```

### Step 6 — Sanity checks before committing

- All new advisory files have valid frontmatter (id, title, date_disclosed, last_updated, severity, status, ecosystems, sources).
- All internal links resolve (e.g., references to `playbooks/foo.md` exist).
- ALERTS.md still parses as markdown.
- `advisories/README.md` table has rows for all advisories.
- No secret or PII accidentally pasted into an advisory.

### Step 7 — Commit + push

```bash
git add -A
git status --short
# If anything changed:
git commit -m "sweep YYYY-MM-DD: N new, M updated"
git push
```

If nothing changed (zero new, zero updated), still commit the `runs.log.md` + `source-priorities.json` updates with message: `sweep YYYY-MM-DD: no new incidents`.

---

## Source-priority semantics

The `source-priorities.json` schema:

```json
{
  "version": 1,
  "last_updated": "YYYY-MM-DD",
  "notes": "Higher weight = query first / trust faster. Cap 20. Min 1.",
  "sources": {
    "<domain>": {
      "weight": <int 1-20>,
      "hits": <int>,
      "last_hit": "YYYY-MM-DD" | null,
      "ecosystems": [<str>...],
      "tier": "vendor" | "research" | "aggregator" | "independent" | "official"
    }
  }
}
```

Use `weight` to:
- Pick top 10 sources for the `allowed_domains` filter in deep-tier queries
- Decide whether a single-source claim is trustworthy (weight ≥ 12 = OK to start a draft; lower = wait for second source)

## Constraints & cautions

- **Don't fabricate.** If a candidate incident doesn't have ≥2 independent sources, mark it `status: unconfirmed` in a new advisory and link only the sources you have. Do not invent IOCs, package names, or version numbers.
- **Verify dates against `today`.** Use `Today's date is YYYY-MM-DD` from the system context as ground truth, not the model's intuition.
- **Cap output.** If a sweep finds more than 10 candidate incidents, prioritize by severity × audience overlap with vibe coders. Log skipped ones in `runs.log.md` under "Notes: deferred".
- **Don't touch playbooks/prevention** in a routine sweep — those are evergreen. If you find a new attack pattern that warrants a new playbook, flag in `runs.log.md` under "Notes: playbook backlog" and let a human decide.
- **Don't auto-resolve status to `patched`** unless a vendor explicitly says so in a primary source.
- **Treat AI-agent framework CVEs as time-critical.** As of 2026-Q2, baseline disclosure-to-exploit is < 4 hours (per Sysdig honeypot data on PraisonAI). Prioritize these in triage and write them up same-day even if only 2 sources are available.
- **Cross-link cross-ecosystem worms.** When the same threat actor or payload appears in multiple ecosystems, cross-link the advisories explicitly (see Mini Shai-Hulud: TanStack ↔ PyTorch Lightning). Don't let the npm advisory and the PyPI advisory live in isolation.
- **Decorator-as-documentation pattern.** Watch specifically for vulnerabilities where an SDK annotation (`[KernelFunction]`, `@tool`, `@function_tool`, FastAPI's `@app.get`) is treated as documentation rather than a security boundary. This is now a known recurring class. When you see one, look for sibling vulnerabilities in the same SDK.
