---
id: 2026-06-hades-pypi-worm
title: "Hades — Shai-Hulud family targets bioinformatics and MCP developers via PyPI .pth + Bun runtime (June 2026)"
date_disclosed: 2026-06-08
last_updated: 2026-06-10
severity: critical
status: active
ecosystems: [pypi, npm, ai-agents, mcp]
tools_affected: [Dynamo, Spateo, CoolBox, U-FISH, Napari-UFISH, embiggen, ensmallen, gpsea, phenopacket-store-toolkit, pyphetools, ppkt2synergy, any package under the affected maintainer, MCP-development PyPI packages]
tags: [supply-chain, credential-theft, pth-autoexec, bun-runtime, bioinformatics, mcp, worm, shai-hulud-family]
---

## TL;DR

**Hades** is a new wave in the Shai-Hulud worm family (tracked by Socket) that compromised **19 bioinformatics PyPI packages** and **~23 MCP developer packages** by June 8–9, 2026, embedding a `.pth` startup hook that silently downloads the **Bun JavaScript runtime from GitHub** and runs a credential-stealing `_index.js` payload at every Python startup — no explicit install hook, no `npm install`, just starting Python. Exfiltrates GitHub, npm, PyPI, Anthropic, AWS/GCP/Azure, and Claude/MCP config credentials.

## What happened

**Socket's Threat Research Team** discovered the "Hades" wave as part of a broader campaign report titled "Mini Shai-Hulud, Miasma, and Hades Worms Target Bioinformatics and MCP Developers via Malicious PyPI Packages" (June 8–9, 2026). The campaign spans 471 total malicious artifacts: 411 npm artifacts across 106 packages and 60 PyPI artifacts across 37 packages, attributed to overlapping threat actors in the Shai-Hulud worm ecosystem.

### Bioinformatics subcluster (19 packages)

The attacker injected malicious wheels into 37 releases covering 19 popular scientific Python packages, targeting researchers in bioinformatics and AI life-science tooling:

- **Graph learning / cell dynamics**: Dynamo, Spateo
- **Chromatin / genome analysis**: CoolBox
- **Microscopy / image analysis**: U-FISH, Napari-UFISH
- **Graph embeddings**: embiggen, ensmallen
- **Rare disease phenotyping**: gpsea, phenopacket-store-toolkit, ppkt2synergy, pyphetools

### MCP developer subcluster (~23 packages)

A second cluster of ~23 PyPI packages targets developers building **Model Context Protocol (MCP) servers** and AI agent tooling, with package names chosen to impersonate widely used MCP-adjacent Python libraries. The attacker also planted **typosquat packages** (`rsquests`, `tlask`, `rlask`) mimicking popular HTTP and web framework names.

### Attack mechanism: `.pth` + Bun runtime download

The attack exploits a Python feature used for legitimate namespace injection:

1. The malicious wheel bundles a `*-setup.pth` file alongside an obfuscated `_index.js` payload.
2. Python automatically executes `.pth` files at interpreter startup via the `site` module — **no `import`, no explicit invocation required**. Any script or REPL that starts Python will trigger this.
3. The `.pth` file checks whether the Bun JavaScript runtime is installed, and if not, **downloads Bun from GitHub** (binary fetch, bypasses static analysis of the wheel).
4. Bun executes `_index.js`, the credential-stealing payload.

The newer bioinformatics sub-cluster adds a second delivery path: **trojanized native `.abi3.so` CPython extension files** that fire at `import` time, providing a fallback if the `.pth` hook is detected or blocked.

### Payload and exfiltration targets

The `_index.js` payload harvests:
- **AI/ML tool credentials**: Anthropic API keys, Claude/MCP config (`~/.claude/`), AI coding assistant settings
- **Cloud credentials**: AWS, GCP, Azure, Kubernetes, HashiCorp Vault
- **Developer credentials**: GitHub, npm, PyPI, RubyGems, JFrog, CircleCI, Docker
- **SSH keys**, shell history, `.env` files, `.npmrc`, `.pypirc`

Exfiltration uses GitHub repositories created by the attacker as staging points (same C2 infrastructure as the prior Shai-Hulud npm waves).

### Broader campaign totals

Socket is tracking the campaign alongside prior Mini Shai-Hulud, Miasma, and Phantom Gyp waves: **471 total malicious artifacts** (411 npm, 60 PyPI). The Hades PyPI list now stands at **453+ total artifacts** in Socket's tracker since the campaign began.

## Am I affected?

```bash
# Check if any of the known compromised packages are installed
pip show dynamo spateo coolbox ufish napari-ufish embiggen \
         ensmallen gpsea phenopacket-store-toolkit pyphetools ppkt2synergy 2>/dev/null

# Check PyPI package versions — any release between 2026-06-08 and cleanup date
# is potentially compromised; verify with Socket or Snyk

# Look for .pth files from unusual packages in your Python site-packages
python3 -c "import site; print(site.getsitepackages())" 
# Then check for unexpected *-setup.pth files
find "$(python3 -c 'import site; print(site.getsitepackages()[0])')" -name '*-setup.pth' 2>/dev/null

# Check for _index.js in site-packages (payload artifact)
find "$(python3 -c 'import site; print(site.getsitepackages()[0])')" -name '_index.js' 2>/dev/null

# Check for the Bun runtime being unexpectedly present
which bun 2>/dev/null || ls ~/.bun/bin/bun 2>/dev/null

# Scan for Anthropic credential harvesting targets
ls ~/.claude/ ~/.claude/settings.json ~/.claude.json 2>/dev/null
```

**You are affected if** you installed any of the named packages (or any MCP-development PyPI package from an unfamiliar maintainer) between June 8 and whenever the compromised versions are removed from PyPI.

**Treat your machine as fully compromised** if `.pth` execution fired — rotate all credentials listed below.

## If you are affected

1. **Uninstall the compromised packages** via `pip uninstall <package>`.
2. **Delete any `*-setup.pth` and `_index.js` artifacts** from your Python site-packages directory.
3. **Rotate in priority order**:
   - Anthropic API key (`ANTHROPIC_API_KEY`, `~/.claude/settings.json`)
   - GitHub personal access tokens / fine-grained tokens
   - npm authentication tokens (`~/.npmrc`)
   - AWS/GCP/Azure credentials (`~/.aws/credentials`, gcloud ADC, Azure CLI)
   - PyPI / JFrog / RubyGems publish tokens
   - SSH private keys (`~/.ssh/id_*`)
4. **Audit MCP configurations** (`~/.claude/`, `~/.cursor/mcp.json`, `~/.config/cline/`) for injected server entries or modified URLs.
5. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- **Scan PyPI packages before installing**: use Socket (`socket npm audit` equivalent for PyPI), Snyk, or `pip-audit`.
- **Flag `.pth` files in dependencies**: any newly installed package that adds a `.pth` file to site-packages should be treated as suspicious unless it's a well-known namespace package.
- **The Bun runtime binary is not standard** in scientific Python environments; unexpected `~/.bun/` directory is an immediate red flag.
- Pin scientific / ML dependencies to exact versions and hash-verify them (`pip install --require-hashes`).
- **MCP developers**: prefer the `pypi.org/simple/` index with hash-pinned `requirements.txt` over bare `pip install`. Do not install unfamiliar MCP-toolkit packages without auditing their source.
- See [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).

## Why bioinformatics and MCP developers?

The attacker is targeting two high-value segments:
- **Bioinformatics researchers** typically work in Jupyter notebooks or conda/venv environments, run frequent `pip install` commands from papers/tutorials, and have cloud compute (AWS, GCP) credentials for large-scale analysis — a high-value credential harvest.
- **MCP developers** have privileged access to AI agent orchestration tooling: Claude/Anthropic API keys, GitHub OAuth for agent automation, and often service accounts for the downstream tools their MCP servers control.

Both groups are less likely to have supply-chain security monitoring tooling than enterprise software engineers.

## Sources

- [Socket — "Mini Shai-Hulud, Miasma, and Hades Worms Target Bioinformatics and MCP Developers via Malicious PyPI Packages"](https://socket.dev/blog/mini-shai-hulud-miasma-and-hades-worms-target-bioinformatics-and-mcp-developers-via-malicious) — Primary disclosure; campaign totals, both subclusters, attack mechanism, IOCs.
- [BleepingComputer — "New Shai-Hulud attack trojanizes 19 science-focused PyPI packages"](https://www.bleepingcomputer.com/news/security/new-shai-hulud-attack-trojanizes-19-science-focused-pypi-packages/) — Bioinformatics package list, Bun runtime download mechanism.
- [The Hacker News — "Hades PyPI Attack: 19 Packages Poisoned to Auto-Run Bun Credential Stealer"](https://thehackernews.com/2026/06/hades-pypi-attack-19-packages-poisoned.html) — Payload description, campaign context.
- [CyberSecurityNews — "New Shai-Hulud Attack Compromises 23 PyPI Packages to Target MCP Developers"](https://cybersecuritynews.com/23-pypi-packages-compromised/) — MCP developer subcluster; ~23 packages, typosquats (rsquests, tlask, rlask).
- [Snyk — Zero-Day Vulnerability Alert (Node-gyp Supply Chain Compromise June 2026)](https://security.snyk.io/node-gyp-supply-chain-compromise-june-2026) — Cross-ecosystem tracking; campaign totals.
- Cross-reference: [2026-06-phantom-gyp-miasma-wave4.md](2026-06-phantom-gyp-miasma-wave4.md) — Phantom Gyp (npm, binding.gyp) — parallel June 2026 npm arm of the same family.
- Cross-reference: [2026-06-miasma-redhat-cloud-services-compromise.md](2026-06-miasma-redhat-cloud-services-compromise.md) — Miasma @redhat-cloud-services npm arm.
- Cross-reference: [2026-05-trapdoor-cross-ecosystem-stealer.md](2026-05-trapdoor-cross-ecosystem-stealer.md) — TrapDoor (prior cross-ecosystem wave, same `.cursorrules`/`CLAUDE.md` poisoning family).
- Cross-reference: [2026-04-elementary-data-pypi-ghcr-compromise.md](2026-04-elementary-data-pypi-ghcr-compromise.md) — Prior PyPI `.pth` auto-exec attack (same delivery primitive).
