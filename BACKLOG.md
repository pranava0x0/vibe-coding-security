# Backlog

> Ideas for future improvements. Priority: **high** / **medium** / **low**.
> Sourced from competitive analysis (Socket, OSV.dev, GHSA, ahrefs.com, simonwillison.net, news.ycombinator.com, Mintlify docs, Anthropic docs, Vercel/v0 changelogs).

## High

- **Client-side search.** `search.json` already ships; needs a 200-line UI (search box in the topbar, fuzzy match via fzf-lite or pagefind). Patterns to imitate: [news.ycombinator.com](https://hn.algolia.com/), [OSV.dev](https://osv.dev/list). Make it instant on type (< 50ms), keyboard-driven (`/` to focus), and accessible (ARIA live region).
- **Filter chips on `/alerts.html` and `/advisories/`.** Filter by severity, status, ecosystem, tool. State in URL hash so filters are shareable. Pattern: [GHSA](https://github.com/advisories) and [Socket Threat Feed](https://docs.socket.dev/docs/threat-feed).
- **Weekly sweep cadence.** Document who refreshes `ALERTS.md` weekly and how. Add a visible `Last swept: YYYY-MM-DD` on every page so staleness is immediately visible.
- **`scripts/check-lockfile.sh`** — reads `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` and greps for IOCs from the current advisory corpus. Output: `OK` or list of matches with advisory links. CLI version of what Socket does, scoped to this repo's data.
- **Per-tool quick-reference cards.** "If you use Cursor, read these 4 advisories." "If you use Claude Code, these 5." Reduces cognitive load and is highly shareable.

## Medium

- **GitHub Action: RSS-to-issue.** Poll Socket / Snyk / GHSA RSS, open a `new-advisory` issue when a relevant item appears. Filter by package popularity (>100k weekly downloads) or specific ecosystems to keep noise down.
- **CLI tool (`npx vcs-check`)** that wraps `npm install` and warns if the package appears in ALERTS or has been flagged. (Subset of `npq`, scoped to this repo's data.)
- **MCP server for the data.** Expose advisories + playbooks as an MCP server so AI agents can query them inline: `tell me if I should install <pkg>`. Highly on-theme; would dogfood the patterns we recommend in [prevention/mcp-hygiene.md](prevention/mcp-hygiene.md).
- **Browser extension** that overlays a warning on npm/PyPI package pages when the package matches an advisory IOC. Inspired by [Socket's browser extension](https://socket.dev/).
- **Per-package detail pages.** `/packages/axios.html` aggregating every advisory that mentions axios. Cross-links from advisory bodies.
- **Per-CVE detail pages.** Similar, for `/cve/CVE-2026-30615.html`.
- **PyPI parity.** Most current advisories are npm-flavored. Bring more Python-specific hardening into [prevention/](prevention/) (`pip --require-hashes`, `pip-audit`, `safety`, `cosign`-signed wheels).
- **Newsletter / email digest.** Buttondown or Substack mirror of new advisories. One-tap subscribe button.
- **Visualizations.** Chart of advisories per month (bar), ecosystem distribution (donut). Pattern: [HoneypotIO](https://honeypotio.com/), [CISA KEV catalog charts](https://www.cisa.gov/known-exploited-vulnerabilities-catalog). Avoid heavyweight libraries — vanilla SVG.
- **Webhook integration.** POST advisory updates to a Slack / Discord webhook (configurable per consumer).
- **Internationalization.** At least Spanish / Mandarin / Hindi for the top 5 advisories. Big vibe-coding audiences there.

## Low

- **JSON export of the advisory metadata** beyond `advisories.json` — formats like CSV, NDJSON for downstream pipelines.
- **OSV.dev contribution.** Where possible, push our IOC data back into OSV so the broader ecosystem benefits.
- **Stickers / printables.** A laminated 1-pager of the "60-second package vetting checklist" you can tape to a monitor.
- **`bin/new-advisory`** scaffold script that copies the template and pre-fills the frontmatter from CLI args.
- **Per-advisory timeline component.** Visual horizontal timeline (disclosed → patched → contained).
- **Dark/light toggle button.** Auto detection is already there; an explicit toggle lets users override.
- **`Cmd-K` palette.** Quick jump to any page. Pattern: [Mintlify docs](https://www.mintlify.com/), [Vercel dashboard](https://vercel.com/).
- **Print stylesheet refinement.** Add a QR code linking to the canonical URL in print output (useful for paper handouts at meetups).
- **Backup mirror on a different host** (Cloudflare Pages? Vercel?) so the site survives GitHub Pages outages.
- **OG:image generator.** Per-page social-share image generated at build time (title + severity badge + last-updated). Inspired by [vercel/og-image](https://og.vercel.app/).
- **GitHub Action that runs `linkchecker`** weekly against the deployed site and opens an issue if any link is broken (we already have internal-link validation; this catches external rot).

## Considered but not doing

- **Comments on advisories.** Spam risk vs. signal. People can open GitHub issues.
- **Login / user accounts.** Defeats the point of "static + cheap + boring."
- **A custom domain.** `pranava0x0.github.io/vibe-coding-security/` is fine and avoids the indirection.

---

## Source patterns we deliberately adopted

| Pattern | Source |
|---|---|
| `llms.txt` + `llms-full.txt` index/export split | [Anthropic docs](https://docs.anthropic.com/) via [Mintlify](https://www.mintlify.com/blog/real-llms-txt-examples) |
| Per-page `.md` mirror | [Mintlify auto-generation](https://www.mintlify.com/blog/simplifying-docs-with-llms-txt) — used by Anthropic, Cursor, Coinbase |
| Compact context variant (`llms-ctx.txt`) | Mintlify recommendation: ≤200K tokens for full ingestion |
| JSON Schema for frontmatter | [GHSA / OSV format](https://ossf.github.io/osv-schema/) approach |
| Versioned API endpoint | OSV.dev API pattern |
| Atom feed for change tracking | [Simon Willison's blog](https://simonwillison.net/atom/everything/), [Socket blog feed](https://socket.dev/blog/rss.xml) |
| Single scannable feed (`ALERTS.md`) | [HN front page](https://news.ycombinator.com/), [Socket Threat Feed](https://socket.dev/threat-feed) |
| "Edit on GitHub" + "View raw markdown" | [docs.github.com](https://docs.github.com/), [supabase.com/docs](https://supabase.com/docs) |
| `.well-known/security.txt` | [securitytxt.org](https://securitytxt.org/) standard |
