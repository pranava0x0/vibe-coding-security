# Advisory feeds

> Machine-readable sources. Wire these into your monitoring stack so you don't have to keep tabs open.

## RSS / Atom feeds

| Feed | URL |
|---|---|
| Socket Blog | `https://socket.dev/blog/rss.xml` |
| Snyk Blog | `https://snyk.io/blog/feed/` |
| StepSecurity Blog | `https://www.stepsecurity.io/blog/rss.xml` |
| Aikido Blog | `https://www.aikido.dev/blog/rss.xml` |
| Checkmarx Blog | `https://checkmarx.com/feed/` |
| The Hacker News | `https://feeds.feedburner.com/TheHackersNews` |
| Bleeping Computer | `https://www.bleepingcomputer.com/feed/` |
| CISA Alerts | `https://www.cisa.gov/cybersecurity-advisories/all.xml` |
| Simon Willison | `https://simonwillison.net/atom/everything/` |
| Anthropic Blog | `https://www.anthropic.com/news/rss.xml` |

Drop these into [Feedly](https://feedly.com/), [NetNewsWire](https://netnewswire.com/), [Inoreader](https://www.inoreader.com/), [Miniflux](https://miniflux.app/), or your reader of choice.

## Machine-readable APIs

For automation (Slack bots, custom dashboards, CI checks):

### GitHub Advisory Database (GHSA)
- Browse: [github.com/advisories](https://github.com/advisories)
- API: `GET https://api.github.com/advisories?ecosystem=npm&per_page=100`
- GraphQL: query `securityAdvisories` with date filters.

```bash
# Get the 10 latest npm advisories
gh api '/advisories?ecosystem=npm&per_page=10' --jq '.[] | {ghsa: .ghsa_id, summary, severity, published_at, identifiers}'
```

### OSV.dev
- All-ecosystem aggregator (GHSA + Go vuln DB + RustSec + PyPA + crates.io advisories + more).
- API: [osv.dev/list](https://osv.dev/list)

```bash
# Query a specific package
curl -X POST "https://api.osv.dev/v1/query" -d '{"package":{"name":"chalk","ecosystem":"npm"}}'
```

### npm Advisories
- `npm audit` reads this directly.
- Programmatic: same data as GHSA via npm registry.

### Socket
- Has a free API tier for project scans.
- Docs: [docs.socket.dev](https://docs.socket.dev/)

### CISA Known Exploited Vulnerabilities (KEV)
- JSON: [cisa.gov/known-exploited-vulnerabilities.json](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json)
- Updated continuously; useful for triage prioritization.

## 3D, simulation and scientific computing

Blender, OpenUSD, FreeCAD, ComfyUI, Omniverse and notebook or workflow tools rarely appear in npm or PyPI advisory feeds. Their fixes arrive through research CNAs and each project's own repository. If you drive any of them with a coding agent, watch these:

| Tool | Where its security fixes appear |
|---|---|
| Blender | No advisory page. CVE records come from VulnCheck. Release dates: `https://download.blender.org/release/` |
| OpenUSD (`usd-core`) | `https://github.com/PixarAnimationStudios/OpenUSD/security/advisories` and ZDI advisories |
| FreeCAD | `https://github.com/FreeCAD/FreeCAD/security/advisories` |
| ComfyUI | `https://github.com/Comfy-Org/ComfyUI/security/advisories` and the ComfyUI-Manager repository |
| NVIDIA Omniverse, Isaac, BioNeMo, PhysicsNeMo | `https://github.com/NVIDIA/product-security` |
| Jupyter | `https://jupyter.org/security` and the `jupyterlab`, `jupyter_server` and `jupyterhub` repository advisory tabs |
| Galaxy, Nextflow, QGIS | each project's repository advisory tab |
| Siemens industrial and digital-twin products | CSAF feed: `https://cert-portal.siemens.com/productcert/csaf/ssa-feed-tlp-white.json` |

```bash
# Published advisories on a project's own tab (works where the web page needs a login or a browser)
gh api 'repos/PixarAnimationStudios/OpenUSD/security-advisories?per_page=10' \
  --jq '.[] | {ghsa: .ghsa_id, cve: .cve_id, severity, published_at, summary}'
```

A CVE in one of these tools is usually "local, user interaction required". When an agent opens a downloaded model, scene or checkpoint for you, the agent supplies that interaction.

## Slack / Discord communities

These often see chatter before the blog posts:

- **[OWASP Slack](https://owasp.org/slack/invite)** — `#supply-chain`, `#llm-top10`.
- **[CNCF Slack](https://slack.cncf.io/)** — `#tag-security`, `#wg-supply-chain-security`.
- **[Anthropic Discord](https://www.anthropic.com/discord)** — Claude Code channels often pick up issues in near-real-time.
- **[Cursor Discord](https://discord.gg/cursor)** — same for Cursor.

## A minimal "I want a Slack ping" setup

```yaml
# GitHub Actions, runs every hour, pings Slack on new GHSA matching your stack
name: ghsa-watch
on:
  schedule: [{ cron: '0 * * * *' }]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: |
          gh api '/advisories?ecosystem=npm&per_page=20&sort=published&direction=desc' \
            --jq '.[] | select(.published_at > "'"$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)"'") | .html_url' \
            | while read url; do
                curl -X POST -H 'Content-type: application/json' \
                  --data "{\"text\":\"New GHSA: $url\"}" \
                  ${{ secrets.SLACK_WEBHOOK }}
              done
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

(Adjust per your stack — filter by package or severity to keep volume reasonable.)

## What we use for this repo

The advisories here are sourced primarily from: Socket, Snyk, StepSecurity, Aikido, Wiz, Microsoft Security Blog, Palo Alto Unit 42, GHSA, Simon Willison, and direct vendor advisories. Cross-referenced across at least two independent sources before a full advisory file lands.
