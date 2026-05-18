---
id: 2026-04-pytorch-lightning-compromise
title: "PyTorch Lightning + intercom-client compromise (Mini Shai-Hulud, April–May 2026)"
date_disclosed: 2026-04-30
last_updated: 2026-05-18
severity: critical
status: contained
ecosystems: [pypi, npm]
tools_affected: [any-pytorch-project, any-ml-pipeline, claude-code, cursor, vscode]
tags: [supply-chain, credential-theft, mini-shai-hulud, teampcp, postinstall, ai-ml, pypi]
---

## TL;DR
On **2026-04-30**, attackers — the same TeamPCP / Mini Shai-Hulud crew behind [the TanStack wave](2026-05-tanstack-mini-shai-hulud.md) and [SAP packages](2026-04-mini-shai-hulud-sap.md) — published trojanized PyPI builds of **`pytorch-lightning` 2.6.2 and 2.6.3** (Lightning AI deep-learning framework). The npm package **`intercom-client@7.0.4`** was hit by the same campaign on the same day. Both shipped a hidden `_runtime/router_runtime.js` (~11 MB obfuscated Bun-compiled JS payload) that steals AWS/Azure/GCP credentials, GitHub/npm tokens, Docker configs, Claude Code + VS Code config, and attempts to back-door downstream repos with `.claude/settings.json` postinstall hooks. The PyTorch Lightning maintainers caught it in ~42 minutes; PyPI yanked both versions same day. Downgrade to **2.6.1**.

## What happened
This is the first time the Mini Shai-Hulud worm jumped cleanly across **PyPI ↔ npm**.

- **PyTorch Lightning 2.6.2** was published on 2026-04-30 from a compromised maintainer pipeline. **2.6.3** was published shortly after with the same payload. Both contained a hidden `_runtime/` directory packaged under the importable `lightning` namespace.
- On `import lightning`, the malicious wheel silently downloaded the **Bun** JavaScript runtime and executed `router_runtime.js`, an ~11 MB obfuscated payload (SHA-256: `5f5852b5f604369945118937b058e49064612ac69826e0adadca39a357dfb5b1`).
- The payload enumerates and exfiltrates: cloud credential files (`~/.aws/credentials`, `~/.azure`, `~/.config/gcloud`), GitHub tokens (`~/.config/gh/hosts.yml`), npm tokens (`.npmrc`), Docker configs, env files, browser secrets, **Claude Code settings (`~/.config/claude/*`)**, and VS Code workspace state.
- For each repo with push access, it adds a `.claude/settings.json` and `.vscode/tasks.json` with `runOn: folderOpen`, plus a `.claude/setup.mjs` and `.claude/router_runtime.js` — re-infection bait for collaborators who open the repo.
- Repos with description `"A Mini Shai-Hulud has Appeared"` and commit messages prefixed `EveryBoiWeBuildIsAWormyBoi` were created in victim accounts to host harvested loot, matching the same TTP as the TanStack wave 11 days later.

`intercom-client@7.0.4` (npm) carried the identical payload — same author email pattern, same `_runtime` directory in the tarball.

## Am I affected?

```bash
# PyPI side
pip show lightning pytorch-lightning 2>/dev/null | grep -E '^(Name|Version):'
pip freeze 2>/dev/null | grep -iE '^(pytorch-)?lightning=='

# Look for the malicious bundled JS payload
python -c "import lightning, os; p = os.path.dirname(lightning.__file__); \
  [print(os.path.join(r,f)) for r,_,fs in os.walk(p) for f in fs \
   if f.endswith('.js') or '_runtime' in r]" 2>/dev/null

# npm side
npm ls intercom-client --all 2>/dev/null | grep '7\.0\.4'

# Repo-side IOCs the worm plants
git log --all --author='claude' --pretty='%an <%ae> %s' | head
git log --all --grep='EveryBoiWeBuildIsAWormyBoi' --pretty='%H %s'
find . -path ./node_modules -prune -o \( -name 'router_runtime.js' -o -path '*/.claude/setup.mjs' \) -print
```

### IOCs

| Type | Value |
|---|---|
| Malicious versions | `pytorch-lightning==2.6.2`, `pytorch-lightning==2.6.3`, `intercom-client@7.0.4` |
| Payload file | `_runtime/router_runtime.js` (~11 MB) |
| Payload SHA-256 | `5f5852b5f604369945118937b058e49064612ac69826e0adadca39a357dfb5b1` |
| Postinstall artifact | `.claude/settings.json`, `.claude/setup.mjs`, `.claude/router_runtime.js`, `.vscode/tasks.json` |
| Commit author | `claude` (with `users.noreply.github.com` email on commits not made by your team) |
| Commit message prefix | `EveryBoiWeBuildIsAWormyBoi` |
| Repo description | `"A Mini Shai-Hulud has Appeared"` |
| Last known clean version | `pytorch-lightning==2.6.1` |

If you pip-installed or `uv add`-ed Lightning on 2026-04-30, treat every credential reachable from that host as compromised — including GitHub fine-grained PATs, cloud creds, Claude Code settings, and any npm tokens cached in `~/.npmrc`.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) — same playbook works for PyPI
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)

```bash
# Pin a clean version
pip install --force-reinstall 'pytorch-lightning==2.6.1'

# Remove planted postinstall artifacts
find . -path ./node_modules -prune -o -type d -name '.claude' -print -exec rm -rfv {} +
```

## Why this matters for vibe coders
The PyTorch Lightning hit is the first **cross-ecosystem** Mini Shai-Hulud incident — the same threat actor spreads the same payload through PyPI and npm. ML/data scientists who don't think of themselves as "npm users" are now in scope: the worm uses Bun (a JS runtime) inside Python packages, and plants `.claude/` postinstall hooks regardless of which package manager you used.

Also notable: the payload specifically targets **Claude Code config** and **VS Code workspace state**. Vibe coders running ML notebooks alongside Claude Code on the same machine are the bullseye.

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — same principles apply to `pip --no-build-isolation` and `pip --require-hashes`
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Use `pip-audit` and Socket's `pip` plugin in CI. Pin exact versions with hashes in `requirements.txt`.
→ Set `PIP_INDEX_URL` to a curated mirror and require maintainer signing where possible.

## Sources
- [Socket — PyTorch Lightning PyPI Package Compromised in Supply Chain Attack](https://socket.dev/blog/lightning-pypi-package-compromised)
- [Lightning AI — How the PyTorch Lightning Community Discovered a Supply Chain Attack and Fixed It in 42 Minutes](https://lightning.ai/blog/pytorch-lightning-supply-chain-attack)
- [Semgrep — Shai-Hulud Themed Malware Found in the PyTorch Lightning AI Training Library](https://semgrep.dev/blog/2026/malicious-dependency-in-pytorch-lightning-used-for-ai-training/)
- [Aikido — Popular PyTorch Lightning Package Compromised by Mini Shai-Hulud](https://www.aikido.dev/blog/pytorch-lightning-pypi-compromise-mini-shai-hulud)
- [SafeDep — PyTorch Lightning Compromised: Shai-Hulud Worm Reaches PyPI](https://safedep.io/malicious-pytorch-lightning-pypi-compromise/)
- [Kodem — Mini Shai-Hulud Attack: PyTorch Lightning (2.6.2, 2.6.3) and intercom-client (7.0.4)](https://www.kodemsecurity.com/resources/mini-shai-hulud-strikes-pytorch-lightning-and-intercom-client-inside-the-cross-ecosystem-supply-chain-attack)
- [Penligent — PyTorch Lightning Supply Chain Attack](https://www.penligent.ai/hackinglabs/pytorch-lightning-supply-chain-attack/)
- [The Hacker News — PyTorch Lightning and Intercom-client Hit in Supply Chain Attacks](https://thehackernews.com/2026/04/pytorch-lightning-compromised-in-pypi.html)
- [Aviatrix — PyTorch Lightning Supply Chain Attack Exposes Developer Credentials](https://aviatrix.ai/threat-research-center/backdoored-pytorch-lightning-package-drops-credential-stealer-2026/)
- [Lightning-AI/pytorch-lightning issue #21689 — Possible supply chain attack on version 2.6.3](https://github.com/Lightning-AI/pytorch-lightning/issues/21689)
