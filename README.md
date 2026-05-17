# Vibe Coding — Security Issue Tracking

> A living index of supply-chain attacks, malicious MCP servers, prompt-injection campaigns, and credential-theft incidents that target people who build with AI coding tools.
>
> _(The GitHub repo and short URL slug remain `vibe-coding-security`; "Vibe Coding · Security Issue Tracking" is the human-readable site title.)_

**Audience.** Anyone shipping with Cursor, Claude Code, Lovable, v0, Bolt, Replit, Windsurf, Codex, or any agent that runs `npm install` / `pip install` on its own. If an LLM has ever suggested a package and you installed it without reading the source, this repo is for you.

**Last full sweep:** 2026-05-17 · **Website:** [pranava0x0.github.io/vibe-coding-security](https://pranava0x0.github.io/vibe-coding-security/)

---

## How to use this repo

1. **Hit by something right now?** → start at [ALERTS.md](ALERTS.md). It's a single scannable feed, latest on top.
2. **Wondering if a specific incident matters to you?** → [advisories/](advisories/) — one file per incident, with concrete `am I affected?` checks.
3. **Already compromised and need to recover?** → [playbooks/](playbooks/) — credential rotation, package removal, blast-radius assessment.
4. **Trying not to get hit in the first place?** → [prevention/](prevention/) — npm hardening, MCP hygiene, credential storage, sandboxing.
5. **Want to monitor this stuff yourself?** → [sources/](sources/) — who to follow on X, which blogs, which feeds.

---

## Why this exists

Vibe coding broke the old contract. The old contract was: a human reads the README, a human picks the dependency, a human runs `npm install`. The new contract is: an agent picks a dependency it half-remembers, runs `npm install` inside `--dangerously-skip-permissions`, and your shell history, `~/.npmrc`, `~/.aws/credentials`, and SSH keys leave the building before you finish your coffee.

In the last 12 months alone:

- **Shai-Hulud** (Sep 2025) — first self-replicating npm worm. Stole npm/GitHub/AWS/GCP creds, made private repos public, then re-published itself into every package the compromised maintainer owned.
- **Shai-Hulud "Second Coming"** (Nov 2025) — 492 packages, 132M downloads/month, hit Zapier / ENS / PostHog / Postman. 25,000+ malicious GitHub repos in days.
- **Nx s1ngularity** (Aug 2025) — first malware to *use Claude Code and Gemini CLI as recon tools* to find your credentials. 2,349 secrets leaked in hours.
- **qix compromise** (Sep 2025) — `chalk`, `debug`, `ansi-styles`. 2 *billion* downloads per week, single phishing email.
- **Postmark MCP** (Sep 2025) — first malicious MCP server. Built trust over 15 versions, then silently BCC'd every email to the attacker.
- **Mini Shai-Hulud** (April–May 2026, ongoing) — SAP packages, TanStack (`@tanstack/react-router`, 12.7M weekly), node-ipc (10M weekly, **two days ago**).
- **Axios** (Mar 2026) — 70M+ weekly downloads, auto-updated into thousands of projects before takedown.

Most defenders have hours to react. Most vibe coders find out weeks later, when their AWS bill arrives.

---

## What this repo is not

- **Not a vulnerability scanner.** Use [Socket](https://socket.dev/), [Snyk](https://snyk.io/), [StepSecurity](https://www.stepsecurity.io/), or `npm audit`. We point at them; we don't replace them.
- **Not a feed for every CVE.** Only incidents that meaningfully affect people building with AI coding tools (npm/PyPI compromise, malicious MCPs, IDE/agent vulnerabilities, prompt-injection campaigns).
- **Not infallible.** Every entry is dated and sourced. Verify before you act on it.

---

## Keeping it fresh

The repo ships with a Claude Code skill at [`.claude/skills/vibe-security-update/`](.claude/skills/vibe-security-update/SKILL.md). Running `/vibe-security-update` (or asking Claude to "refresh the sweep") performs a tiered web sweep — **deep over the last 24h, medium over 3d, light over 7d** — and updates ALERTS.md + advisories. The skill maintains a [`source-priorities.json`](.claude/skills/vibe-security-update/source-priorities.json) that **learns over time**: sources that consistently produce hits gain weight and get queried first on future runs.

The website (built from the markdown sources) auto-deploys on every push to `main` via GitHub Actions ([`.github/workflows/deploy-site.yml`](.github/workflows/deploy-site.yml)). The build runs through [`site/validate.py`](site/validate.py) in CI — broken internal links, missing meta tags, skipped heading levels, or malformed frontmatter fail the deploy. Build locally with:

```bash
pip install -r site/requirements.txt
python site/build.py        # writes dist/
python site/validate.py     # 9 checks: links, metadata, JSON-LD, sitemap, llms.txt
open dist/index.html
```

## LLM-friendly outputs

Every build also emits machine-readable artifacts under `dist/`:

- **[llms.txt](https://pranava0x0.github.io/vibe-coding-security/llms.txt)** — [llmstxt.org](https://llmstxt.org/) format index with one-line descriptions of every page.
- **[llms-full.txt](https://pranava0x0.github.io/vibe-coding-security/llms-full.txt)** — every advisory, playbook, and prevention doc concatenated as raw markdown. Drop this into any LLM context window for full coverage in one paste.
- **[advisories.json](https://pranava0x0.github.io/vibe-coding-security/advisories.json)** — structured index of all advisories with frontmatter (severity, status, ecosystems, dates, IDs).
- **[search.json](https://pranava0x0.github.io/vibe-coding-security/search.json)** — minimal per-page index for future client-side search.
- **[sitemap.xml](https://pranava0x0.github.io/vibe-coding-security/sitemap.xml)** + **[robots.txt](https://pranava0x0.github.io/vibe-coding-security/robots.txt)** — for search-engine and LLM crawlers.

Each rendered HTML page also includes JSON-LD (`TechArticle` for advisories, `Article` for everything else) with `datePublished` / `dateModified`, plus Open Graph + Twitter card meta tags.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New advisory? Open an issue with the `new-advisory` template, or submit a PR using the format in [advisories/README.md](advisories/README.md).

If you spotted something live and need it logged in the next hour, just open an issue with a link and we'll flesh it out.

---

## License

CC0 / public domain. Copy, fork, mirror, paste into your own runbooks. Attribution appreciated but not required.
