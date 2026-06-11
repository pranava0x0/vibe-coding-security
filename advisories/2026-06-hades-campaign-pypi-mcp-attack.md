---
id: 2026-06-hades-campaign-pypi-mcp-attack
title: "Hades Campaign — 19 PyPI bioinformatics + MCP-developer packages poisoned with Bun credential stealer (June 2026)"
date_disclosed: 2026-06-08
last_updated: 2026-06-11
severity: critical
status: active
ecosystems: [pypi, npm]
tools_affected: [ensmallen, dynamo, spateo, coolbox, u-fish, napari-ufish, langchain-core-mcp, openai-mcp, instructor-mcp, tiktoken-mcp, ray-mcp-server, claude-code, cursor, openhands]
tags: [supply-chain, credential-theft, pypi, pth-file, bun-runtime, mcp-targeting, shai-hulud-lineage, miasma-lineage, bioinformatics]
---

## TL;DR

On **2026-06-08**, StepSecurity identified a sophisticated supply-chain campaign — dubbed **"Hades"** — that poisoned **19 PyPI packages** across 37 malicious wheel artifacts in two distinct target categories: (1) popular **bioinformatics / graph-ML packages** (ensmallen, dynamo, spateo, coolbox, u-fish, napari-ufish, gpsea, phenopacket-store-toolkit, and related tools), and (2) explicitly **MCP-developer-targeted packages** (`langchain-core-mcp`, `openai-mcp`, `instructor-mcp`, `tiktoken-mcp`, `ray-mcp-server`). The payload uses a **`*-setup.pth` startup hook** (auto-executes at every Python interpreter startup — no import or explicit run needed), silently downloads the **Bun JavaScript runtime**, and runs an obfuscated `_index.js` credential harvester that specifically targets **Claude / MCP configuration files** alongside the standard cloud-credential sweep. This is the **fifth documented copycat wave** of the open-sourced Mini Shai-Hulud / Miasma lineage and the **first to explicitly target Model Context Protocol developer tooling by name**.

## What happened

On **2026-06-08**, version 0.8.101 of the graph-ML package **ensmallen** on PyPI was identified as containing a supply-chain compromise. StepSecurity's Threat Research team identified a broader coordinated campaign — "The Hades Campaign" — that spans **37 malicious wheel artifacts across 19 packages** in two deliberately chosen target pools:

### Target pool 1: Bioinformatics / graph-ML packages

High-download packages in computational biology and genotype-phenotype analysis — authors / maintainers frequently run automated data-processing pipelines with broad cloud IAM access:

- `ensmallen` (popular graph embedding library)
- `embiggen` (graph neural network toolkit)
- `dynamo`, `spateo` (single-cell genomics tools)
- `coolbox` (genome browser framework)
- `u-fish`, `napari-ufish` (~60K+ combined monthly downloads)
- `gpsea`, `phenopacket-store-toolkit`, `ppkt2synergy`, `pyphetools` (phenotype analysis)

### Target pool 2: MCP developer tooling

Packages chosen to directly infect developers **building or consuming Model Context Protocol integrations** — who, by definition, are running local MCP servers connected to AI agents (Claude, Cursor, etc.) with broad tool access:

- `langchain-core-mcp`
- `openai-mcp`
- `instructor-mcp`
- `tiktoken-mcp`
- `ray-mcp-server`

This second pool is a meaningful escalation: MCP developers are a high-value target because their machines are simultaneously running AI agents with broad permissions, local MCP servers with tool access, and cloud credentials. A compromised MCP developer is a direct path to every AI agent tool that developer's projects expose.

### Three delivery branches

The campaign used three distinct PyPI delivery mechanisms, operated in parallel:

1. **`*-setup.pth` startup hook** — each compromised release bundles a `*-setup.pth` file (e.g., `ensmallen-setup.pth`, `dynamo-setup.pth`). Python auto-processes `.pth` files in `site-packages/` on startup — no import, no explicit run, no user action. This fires on every Python execution in the environment after install.

2. **Native extension import trigger** — some packages embed malicious code inside compiled `.abi3.so` extension modules. Activated on the first `import` of the package.

3. **`__init__.py` import hook** — traditional `pip install` → `import` → execute pattern in the `__init__.py` of the package's main module.

### Payload: Bun-based credential harvester

The `.pth` and `__init__.py` hooks run a multi-stage bootstrap:

1. Checks locale / geolocation (skips Russian/CIS-adjacent environments — same anti-forensic pattern as Mini Shai-Hulud).
2. Downloads the **Bun JavaScript runtime** from a CDN mirror (legitimizes the network request against egress monitors).
3. Executes an obfuscated `_index.js` payload, harvesting:
   - **AI / MCP specific**: Claude/MCP configuration (`~/.claude/`, `~/.cursor/mcp.json`), Anthropic API keys (`ANTHROPIC_API_KEY`), OpenAI API keys, HuggingFace tokens
   - Cloud credentials: AWS (`~/.aws/`), GCP (`~/.config/gcloud/`), Azure (`~/.azure/`), Kubernetes (`~/.kube/config`), HashiCorp Vault tokens
   - Source control: GitHub tokens, npm tokens, PyPI tokens, JFrog Artifactory tokens, CircleCI tokens, RubyGems tokens
   - Shell history (`~/.bash_history`, `~/.zsh_history`) and `.env*` files
   - Docker credentials (`~/.docker/config.json`), SSH keys (`~/.ssh/`)
4. Exfiltrates to attacker C2. The campaign is tracked across the broader Miasma lineage; specific C2 infrastructure varies per sub-wave.

### Campaign scope

StepSecurity and SecurityWeek track the Hades Campaign as part of the broader **Miasma / Shai-Hulud cluster**: as of June 10, 2026, the combined campaign spans **471 total artifacts** across npm and PyPI — 411 npm artifacts across 106 packages and 60 PyPI artifacts across 37 packages (Hades being the latest PyPI arm).

## Am I affected?

```bash
# Check for poisoned packages in your active virtualenv / global site-packages
pip list | grep -iE 'ensmallen|embiggen|dynamo|spateo|coolbox|u-fish|napari-ufish|gpsea|phenopacket|ppkt2synergy|pyphetools|langchain-core-mcp|openai-mcp|instructor-mcp|tiktoken-mcp|ray-mcp-server'

# Check for .pth startup hooks placed by the malware
python -c "import site; print(site.getsitepackages())"
# Then look for unexpected *.pth files in those directories:
find "$(python -m site --user-site)" "$(python -c 'import site; print(site.getsitepackages()[0])')" -name "*setup.pth" 2>/dev/null

# Check MCP / Claude configuration for unexpected entries
cat ~/.claude/mcp.json 2>/dev/null
cat ~/.cursor/mcp.json 2>/dev/null
```

If you installed any affected package after **2026-06-07**, treat the machine as compromised regardless of whether credentials look intact.

## If you are affected

1. **Rotate all credentials** reachable from the affected environment: Anthropic API keys, OpenAI API keys, cloud keys (AWS/GCP/Azure), GitHub/npm/PyPI tokens, SSH keys.
2. **Audit MCP configuration files** (`~/.claude/mcp.json`, `~/.cursor/mcp.json`) for unexpected server entries that could run attacker-controlled tools against your AI agents.
3. **Remove the malicious `.pth` file** from your Python site-packages; it re-executes the payload on every Python run.
4. **Reinstall clean package versions** (or remove the packages if not needed).
5. **Audit shell history** and cloud audit logs for lateral-movement indicators.

## Why this matters for vibe coders

MCP is the nervous system of modern AI-coding workflows. A developer building MCP integrations for Claude / Cursor is a high-trust target: their machine likely runs local MCP servers with shell, file-write, database, and cloud-API tool access — the same tools the adversary wants to pivot through. Poisoning `langchain-core-mcp` or `tiktoken-mcp` targets exactly those developers. The `*-setup.pth` delivery mechanism means the payload is persistent: it re-executes every time Python starts in the affected environment, even if the package is later removed (the `.pth` file may remain in `site-packages/`).

## Relation to the broader Miasma/Shai-Hulud lineage

Hades is the **fifth documented copycat wave** of the Mini Shai-Hulud worm after TeamPCP open-sourced it in May 2026:

| Wave | Date | Ecosystems | Distinctive |
|---|---|---|---|
| [deadcode09284814 typosquats](2026-05-shai-hulud-copycat-wave.md) | May 18 | npm | Near-verbatim worm clone, DDoS payload |
| [TrapDoor](2026-05-trapdoor-cross-ecosystem-stealer.md) | May 22 | npm + PyPI + Crates.io | `.cursorrules`/`CLAUDE.md` poisoning |
| [Miasma @redhat](2026-06-miasma-redhat-cloud-services-compromise.md) | June 1 | npm | Greek-myth theming, Anthropic camouflage exfil |
| [Phantom Gyp](2026-06-phantom-gyp-miasma-wave4.md) | June 3 | npm | binding.gyp install-time primitive, SLSA forgery |
| **Hades** | **June 8** | **PyPI** | **`.pth` + Bun runtime, MCP-developer targeting** |

Note: On **2026-06-10**, the Miasma worm source code was briefly open-sourced to GitHub via compromised developer accounts (repositories named "Miasma-Open-Source-Release"), mirroring what TeamPCP did with Mini Shai-Hulud on 2026-05-12. A sixth copycat wave is likely. See the [Miasma @redhat advisory](2026-06-miasma-redhat-cloud-services-compromise.md) for the source-code-leak update.

## Sources

- [StepSecurity — The Hades Campaign: Graph ML PyPI Packages Deploy Cross-Platform Memory Scrapers, AI Analyst Misdirection, and a Wiper Deterrent](https://www.stepsecurity.io/blog/the-hades-campaign-pypi-packages)
- [The Hacker News — Hades PyPI Attack: 19 Packages Poisoned to Auto-Run Bun Credential Stealer](https://thehackernews.com/2026/06/hades-pypi-attack-19-packages-poisoned.html)
- [BleepingComputer — New Shai-Hulud attack trojanizes 19 science-focused PyPI packages](https://www.bleepingcomputer.com/news/security/new-shai-hulud-attack-trojanizes-19-science-focused-pypi-packages/)
- [SecurityWeek — Over 100 NPM, PyPI Packages Hit in New Shai-Hulud Supply Chain Attacks](https://www.securityweek.com/over-100-npm-pypi-packages-hit-in-new-shai-hulud-supply-chain-attacks/)
- [CybersecurityNews — New Shai-Hulud Attack Compromises 23 PyPI Packages to Target MCP Developers](https://cybersecuritynews.com/23-pypi-packages-compromised/)
