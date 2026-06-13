---
id: 2026-06-solana-fakefix-campaign
title: "Solana FakeFix Campaign — 25 malicious npm + PyPI packages steal wallet keys and developer secrets via GitHub issue spam (June 2026)"
date_disclosed: 2026-06-10
last_updated: 2026-06-13
severity: high
status: active
ecosystems: [npm, pypi]
tools_affected: [Solana SDK, any project using @solana-labs/web3.js, solana-web3-stable, solana-rpc-client, solana-mev-bot, Claude Code, Cursor, Codex]
tags: [supply-chain, credential-theft, social-engineering, npm, pypi, crypto-wallet, github-issue-spam, cross-ecosystem]
---

## TL;DR

The **"Solana FakeFix" campaign** planted **25 malicious packages** (16 npm + 4 PyPI + 5 additional CMS-loader variants) that impersonate Solana Web3 SDK tooling, promoted via **fake GitHub issue spam** on nine popular open-source projects framing the attacker's package as a community bug fix. Payloads harvest Solana wallet keys, cloud credentials, SSH keys, and AI-tool config from victim machines the moment a package is installed (npm `postinstall`) or imported (PyPI `__init__.py`). A bonus fake MEV bot package directly social-engineers users into pasting private keys.

## What happened

An unattributed threat actor published **25 malicious packages** targeting the Solana Web3 and DeFi developer community, combining typosquatting with GitHub social-engineering:

### Package families

| Family | Count | Ecosystems | Examples |
|---|---|---|---|
| FakeFix core | 16 npm + 4 PyPI = 20 | npm, PyPI | `solana-web3-stable`, `solana-rpc-client`, `@solana-labs/web3.js` (typosquat) |
| CMS loader group | 5 npm | npm | Related loader packages with similar payload |

Package names closely mirrored the legitimate Solana SDK (e.g., `@solana-labs/web3.js`, `solana-web3-stable`, `solana-rpc-client`), exploiting namespace confusion between the official `@solana-labs` scope and look-alike names.

### GitHub issue spam — new social engineering vector

The threat actor opened **nine fake GitHub issues** across different popular open-source Solana projects, each framing a malicious package as "the community fix" for a real bug or compatibility issue in the authentic SDK. This is a new supply-chain social-engineering shape: rather than relying on typosquatting discovery alone, the attacker **actively funnels traffic to the malicious package** via trusted community forums, positioning installation as the appropriate remediation step.

### Payload mechanics

- **npm (`postinstall`)**: A JavaScript payload fires immediately on `npm install`, requiring no explicit package import.
- **PyPI (`__init__.py`)**: Malicious code runs on the first `import` of the package, activated by any test run, notebook cell, or script.
- **Bonus — `solana-mev-bot`**: A standalone fake MEV (Miner Extractable Value) bot package that uses social engineering to prompt the user to paste their Solana private key directly, framing it as required for "automated profit extraction."

### Credentials targeted

- Solana private keys and wallet recovery phrases (primary target)
- Browser wallet extensions (Phantom, Backpack, MetaMask)
- Cloud credentials: AWS `~/.aws/credentials`, GCP `~/.config/gcloud/`, Azure `~/.azure/`
- AI tool config: `~/.claude/settings.json`, `ANTHROPIC_API_KEY`, OpenAI API keys, `~/.cursor/mcp.json`
- SSH keys (`~/.ssh/`), GitHub tokens, npm tokens, `.env*` files
- System environment variables

## Am I affected?

```bash
# Check npm for FakeFix packages
npm list --depth=0 2>/dev/null | grep -iE 'solana-web3-stable|solana-rpc-client|solana-mev-bot'

# Check PyPI
pip list 2>/dev/null | grep -iE 'solana-web3-stable|solana-rpc-client|solana-mev'

# Audit recent GitHub issues for issue-spam pattern (if you maintain a Solana repo)
# Look for issues recommending installing an unfamiliar package as a "fix"

# Check for unexpected persistence artifacts
# Windows: Registry Run keys, scheduled tasks
# Linux/macOS: crontab -l, ~/.bashrc, ~/.zshrc
```

If you installed any Solana-related package after seeing a GitHub issue recommending it as a "fix," treat the environment as compromised.

## If you are affected

1. **Rotate Solana wallets immediately** — generate a new keypair and move all funds. Private keys exposed to this payload are irrecoverable.
2. **Revoke and rotate** all cloud credentials (AWS, GCP, Azure), GitHub tokens, npm tokens, and AI-tool API keys (Anthropic, OpenAI).
3. **Audit MCP config files** (`~/.claude/mcp.json`, `~/.cursor/mcp.json`) for unexpected servers.
4. **Remove affected packages** and rebuild CI runners from clean images.
5. **Check GitHub issues** on any repo you maintain for spam linking to FakeFix packages; close and label as spam.

## Prevention

- Never install a package recommended in a GitHub issue without independently verifying on the official registry that the package (a) exists, (b) is maintained by a known organization, and (c) matches the expected name exactly.
- For Solana SDK, the official package is `@solana/web3.js` (scoped under `@solana`, NOT `@solana-labs/web3.js` variants from unknown publishers).
- Crypto private keys should never leave the wallet app — no npm package or script legitimately requires a raw private key as input.

## Sources

- [CybersecurityNews — Solana FakeFix Campaign Uses 25 Malicious npm and PyPI Packages to Steal Developer Secrets](https://cybersecuritynews.com/solana-fakefix-campaign-uses-25-malicious-npm-and-pypi-packages/)
- [Socket.dev — 5 Malicious npm Packages Typosquat Solana and Ethereum Libraries, Steal Private Keys](https://socket.dev/blog/5-malicious-npm-packages-typosquat-solana-and-ethereum-libraries-steal-private-keys)
