# Backlog

> Ideas for future improvements. Priority: **high** / **medium** / **low**.
> Sourced from competitive analysis (Socket, OSV.dev, GHSA, ahrefs.com, simonwillison.net, news.ycombinator.com, Mintlify docs, Anthropic docs, Vercel/v0 changelogs). The 2026-06-01 research batch below also draws on Sigstore, deps.dev, OpenSSF Scorecard, FIRST EPSS, CISA KEV, the OSV schema, purl/PEP 740, pnpm/npm/uv docs, and the Internet Archive.

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

## Supply-chain & download-safety ideas (2026-06-01 research pass)

> A focused batch researched on 2026-06-01, weighted toward the maintainer's priority: **helping a developer decide whether and how to safely install something from the internet.** Deduplicated against the lists above (client-side search, filter chips, per-package/CVE pages, `npx vcs-check`, `check-lockfile.sh`, browser extension, PyPI parity, OSV.dev contribution, linkchecker are already captured there — items below either extend or don't overlap them). Each item tagged _(priority · effort)_. Verify any post-cutoff tooling/version claim against current docs when implementing.

### Verify-before-you-install (the priority theme)

- **Consumer-side provenance / attestation verification guide.** A new `prevention/` page on how to *check* an artifact's build origin **before trusting it** — the missing counterpart to our existing *publish*-provenance docs, and the single biggest gap for the "downloading from the internet" model. Exact commands: `npm audit signatures` (verifies registry signatures + Sigstore provenance for the installed tree), `gh attestation verify <file> --repo <org>/<repo>`, PyPI/PEP 740 `pypi-attestations verify pypi --repository <repo> <file-url>`, `cosign verify-blob-attestation`. _(high · low)_ — [npm audit](https://docs.npmjs.com/cli/v10/commands/npm-audit/), [gh attestation verify](https://cli.github.com/manual/gh_attestation_verify), [PyPI attestations](https://docs.pypi.org/attestations/).
- **Refresh `prevention/npm-hardening.md` for the 2026 npm cooldown + publishing changes.** npm 11.10+ ships a native `min-release-age` setting (in **days**, via `.npmrc`) that supersedes the doc's current `npm config set before` trick — and npm errors if you combine `min-release-age` with `--before`. Also note the new 2FA-gated/staged publishing (blocks stolen-CI-token publishes — the Shai-Hulud vector). _(high · low)_ — [npm/cli](https://github.com/npm/cli), [GitHub: a more secure npm](https://github.blog/security/supply-chain-security/our-plan-for-a-more-secure-npm-supply-chain/).
- **Dependency-cooldown matrix across every package manager.** One shareable table — npm `min-release-age` (days), pnpm `minimumReleaseAge` (minutes; default 1440 in v11), Yarn `npmMinimalAgeGate`, Bun `minimumReleaseAge` (seconds), uv `exclude-newer`, pip (no native → `--require-hashes` + pinned lockfile). Most 2025–26 attacks had a takedown window under a week, so "don't install anything published in the last N days" is the cheapest high-impact defense. _(high · low)_ — [cooldowns.dev](https://cooldowns.dev/), [Datadog: dependency cooldowns](https://securitylabs.datadoghq.com/articles/dependency-cooldowns/).
- **Web "paste your lockfile / SBOM" checker.** Client-side, no backend: paste a `package-lock.json` / `pnpm-lock.yaml` / `requirements.txt` (or a CycloneDX/SPDX SBOM) → cross-check every `package@version` against this repo's IOC corpus → list matches with advisory links. The in-browser complement to the planned `scripts/check-lockfile.sh`. _(high · medium)_
- **pnpm "secure defaults" recipe.** A "switch to pnpm and paste this" config block: `minimumReleaseAge`, an `allowBuilds` allow-list (lifecycle scripts blocked by default), `blockExoticSubdeps: true`, `trustPolicy: no-downgrade`. Lowest-effort high-impact move for a solo dev — covers cooldown + scripts + provenance-downgrade in one file. _(medium · low)_ — [pnpm supply-chain security](https://pnpm.io/supply-chain-security).
- **Slopsquat / typosquat name-check.** For any LLM-suggested package, confirm it actually resolves (`npm view` / `pip index versions`) **and** isn't a 1–2 edit-distance neighbor of a far more popular package. ~20% of LLM-suggested package names are hallucinated and attackers pre-register the predictable ones — squarely the AI-coding threat model. Ship as a mode of the planned `vcs-check` CLI. _(medium · medium)_ — [CSA slopsquatting note](https://cloudsecurityalliance.org/), [Snyk](https://snyk.io/articles/slopsquatting-mitigation-strategies/).
- **Trust-signals panel on package pages (build-time, cached).** Surface the heuristics that predict malice: days-since-first-publish, has-install-script, maintainer count, OpenSSF Scorecard score, typosquat flag. deps.dev + Scorecard serve free no-auth JSON — fetch once at build, cache to disk, treat a fetch failure as "no data" (never break the build). _(medium · medium-large)_ — [deps.dev API](https://docs.deps.dev/api/v3/), [OpenSSF Scorecard](https://scorecard.dev/).

### Machine-readable IOC & advisory data (so the tools you already run flag these incidents)

- **Structured IOC + affected-package frontmatter (+ schema/validator update).** The enabler for everything below. Add optional frontmatter — `cves`, `cwes`, `cvss` (vector string), `affected_packages` (ecosystem / name / `purl` / `bad_versions` / `fixed`), `iocs` (domains / ips / sha256 / accounts) — since today these facts live only in advisory prose (scraping prose is noisy: citation domains mix with real C2). Back-compatible (`additionalProperties: true`); main cost is back-filling existing advisories, so front-load new ones. Mind purl gotchas: npm scopes encode `@`→`%40`, PyPI names lowercase and `_`→`-`. _(high · medium)_ — [OSV schema](https://ossf.github.io/osv-schema/), [purl spec](https://github.com/package-url/purl-spec).
- **OSV-format export + register as an OSV.dev data source.** Emit `osv/<id>.json` + an `all.zip` so OSV-Scanner and the whole osv.dev ecosystem ingest these advisories automatically (scope to incidents with a real `package@version`; leave agent/MCP/CVE-only ones minimal). Then submit the feed as an osv.dev data source — they explicitly invite third-party DBs. Concretizes (and supersedes) the existing low-priority "OSV.dev contribution" item. _(high · medium-high)_ — [OSV schema](https://ossf.github.io/osv-schema/), [OSV data sources](https://google.github.io/osv.dev/data/).
- **Consolidated `iocs.json` (+ `.ndjson`, `.csv`) indicator feed.** One record per indicator (package@version as a purl, C2 domain, IP, SHA-256, npm account) with `advisory_id` / `url` / `first_seen` / `severity` / `tags`. `curl | jq`-able: grep a lockfile, seed an allow/deny list, import to a SIEM — no SCA tool required. Distinct from the existing generic metadata export (advisory rows vs. indicators). _(high · medium)_
- **CVSS-vector + CWE + EPSS + CISA-KEV enrichment.** Store CVSS *vector* strings (not just the number) and CWE IDs; fetch EPSS exploit-probability and CISA-KEV membership at build time and badge advisories accordingly ("In CISA KEV" is the strongest urgency signal there is). Stamp an "as of" date — EPSS/KEV drift daily; cache, never hardcode. _(medium · low-medium)_ — [FIRST EPSS API](https://www.first.org/epss/api), [CISA KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) ([JSON mirror](https://github.com/cisagov/kev-data)).
- **Embeddable shields.io verdict badge.** Emit a tiny per-package JSON matching the shields endpoint schema so a maintainer can drop `![vibe-sec](https://img.shields.io/endpoint?url=<site>/badge/npm/<pkg>.json)` in a README → "flagged: malware" / "no known incident". Free distribution + backlinks, at the point of decision. _(low · small, after the lookup index)_ — [shields endpoint badge](https://shields.io/badges/endpoint-badge).
- **(Considered — deferred) OpenVEX / STIX-TAXII / MISP feeds.** Researched and valid, but aimed at SBOM pipelines (VEX) and SOC / threat-intel teams (STIX/MISP), not this site's solo-dev audience — and OSV already conveys "affected". TAXII also implies a live server (anti-static). Revisit only if a real consumer asks; a static MISP feed (`manifest.json` + per-event JSON + `hashes.csv`) is the only one worth eventual consideration.

### Make the site itself verifiable (practice what we preach)

- ✅ **Done (2026-06-01)** — **Pin GitHub Actions to commit SHAs + minimize workflow `permissions:`.** `deploy-site.yml` now pins all four actions to 40-hex commit SHAs and scopes permissions per job (`build`: `contents: read`; `deploy`: `pages: write` + `id-token: write`). Shipped alongside the new [ci-cd-hardening.md](prevention/ci-cd-hardening.md) guide. Remaining follow-up: add `.github/dependabot.yml` (`github-actions` ecosystem) to keep the pins current — see the Dependabot item below. — [pinact](https://github.com/suzuki-shunsuke/pinact), [OpenSSF CI/CD hardening guide](https://openssf.org/blog/2025/06/11/maintainers-guide-securing-ci-cd-pipelines-after-the-tj-actions-and-reviewdog-supply-chain-attacks/).
- **Content-integrity manifest (`dist/integrity.txt`).** ~15 lines in `build.py`: SHA-256 of every published file, written last, so anyone can verify the bytes they received match what was published — the static-site equivalent of build provenance, exactly on-mission for a "trust what you download" site. Link from `security.html`; assert completeness in `validate.py`. _(high · low)_
- **Source archival / anti-link-rot.** At build/CI time, POST each cited source URL to the Wayback Machine "Save Page Now" (respecting the 1.5–2s/host rule), store the snapshot URL, and render an "📦 archived" link beside each live citation. Advisories live or die by citations that 404; this keeps every claim verifiable. _(high · medium)_ — [Wayback Save Page Now](https://help.archive.org/help/save-pages-in-the-wayback-machine/), [waybackpy](https://pypi.org/project/waybackpy/).
- **Hash-pin the site's own Python deps + Dependabot.** `uv pip compile --generate-hashes` → `requirements.lock`, installed with `pip install --require-hashes`; add `.github/dependabot.yml` watching `pip` + `github-actions` (auto-bumps the pinned SHAs above). _(medium · low)_ — [pip secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/).
- **CI hardening gates.** **[`zizmor`](https://github.com/woodruffw/zizmor)** to lint our own workflows (catches unpinned actions + injection — guards the 2026-06-01 SHA-pinning from silently regressing; cheapest, do first), OpenSSF Scorecard action + README badge (verifiable third-party trust signal), a CSP `<meta>` tag (easy — zero third-party requests — with an honest `security.html` note that GitHub Pages can't set real HTTP headers / `frame-ancestors`), and quality gates: Lighthouse CI perf+a11y budget (enforces "minimize page weight"), pa11y/axe, `html-validate`, `cspell` over advisories. _(low-medium · medium)_ — [scorecard-action](https://github.com/ossf/scorecard-action), [lighthouse-ci-action](https://github.com/treosh/lighthouse-ci-action), [pa11y-ci](https://github.com/pa11y/pa11y-ci).

## Deploy reliability & content gaps (2026-06-19 follow-ups)

> Surfaced while fixing a 2-week deploy outage (broken internal links failed `validate.py` on every sweep 2026-06-04 → 06-19; live site frozen at 2026-06-03). Fix shipped; these are the durable follow-ups.

- **Pre-commit guardrail in the sweep skill (DONE — skill + CI-on-PR; a git hook is the remaining option).** The skill mandates running `build.py → validate.py → pytest` before committing, and `.github/workflows/ci.yml` now runs that same gate on every `pull_request` (so a PR can't merge red — previously only `push` to `main` was gated, by `deploy-site.yml`). Still worth adding a local `pre-commit` / `pre-push` hook so a future *automated* sweep that commits straight to `main` (bypassing PRs) can't skip the gate either. _(medium · low)_
- **Add external-link checking to CI.** `tools/check-external-links.py` now exits non-zero on `404 + no Wayback` and ignores localhost/private/test URLs, so it can gate. It's not in `ci.yml` yet because it's network-dependent (flaky in CI) and slow (~1.8s/URL). Options: run it only on advisory files changed in the PR (`git diff --name-only`), nightly, or as a non-blocking annotation. _(medium · medium)_
- **Trim historical-status advisories from `llms-full.txt` / `llms-ctx.txt` at build time.** The size caps were bumped again (50→64KB / 640→896KB / 96→128KB) but `llms-full.txt` is ~790KB (~200K tokens) and has outgrown "one Claude paste." Real fix: exclude `status: historical` (and maybe `patched` older than N months) from the concatenated files, keeping them in per-page mirrors. Stops the cap-bumping treadmill. _(high · medium)_
- **Auto-bump (or assert) `README.md` "Last full sweep".** It drifts behind `ALERTS.md` "Last refreshed" because daily sweeps don't touch it (was 2026-06-12 while ALERTS said 2026-06-19). Either derive it in `build.py` or add a `validate.py` check that the two dates match. _(medium · low)_
- **Author the playbooks the sweeps keep wanting.** Broken links pointed at non-existent playbooks that are clearly desired by advisory authors — write them and re-point: `playbooks/if-you-ran-malicious-postinstall.md` (referenced 4×: postinstall/build-script credential theft), `playbooks/if-your-local-ai-agent-was-exploited.md` (Cline/OpenCode-class 1-click RCE), `playbooks/if-your-webapp-was-compromised.md` (RCE in a deployed app), `playbooks/if-you-ran-an-unpatched-ai-framework.md` (Langflow/LiteLLM-class — rotate every brokered provider key). _(medium · medium)_
- **`prevention/prompt-injection-defense.md` — the biggest prevention gap.** ~8 advisories are injection-class (InversePrompt, Comment-and-Control, CurXecute/MCPoison, Agentjacking, TrapDoor, ClawHavoc, PromptSnatcher) but there's no prevention doc. Cover: lethal-trifecta framing, "two parsers one string" class, agent-config files as a *write*-target (grep `.cursorrules`/`CLAUDE.md`/`AGENTS.md`/`SKILL.md`/`.github/copilot-instructions.md` for zero-width/bidi/variation-selector Unicode and diff on every dep change), MCP tool-description/tool-definition poisoning, and the CSA "Agent Context Poisoning: SKILL.md" note. _(high · medium)_
- **Bump deploy-workflow actions off Node 20.** `deploy-site.yml`'s SHA-pinned `actions/checkout`, `actions/setup-python`, `actions/upload-artifact` target Node 20 (deprecated; currently force-run on Node 24). Re-pin to current major SHAs before GitHub drops the Node-20 compat shim. Coordinate with the existing SHA-pin + `dependabot.yml (github-actions)` backlog item. _(medium · low)_

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
