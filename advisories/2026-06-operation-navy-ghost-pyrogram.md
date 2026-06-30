---
id: 2026-06-operation-navy-ghost-pyrogram
title: "Operation Navy Ghost — 8 fake pyrogram packages on PyPI target Telegram bot developers with full-server backdoor using Telegram as C2 (Jun 2026)"
date_disclosed: 2026-06-25
last_updated: 2026-06-30
severity: high
status: unconfirmed
ecosystems: [pypi, python]
tools_affected: [pyrogram, vlifegram, vlife-gram, kelragram, pyrogram-navy, pyrogram-styled, sepgram, pyrogram-zeeb, pyrogram-kelra]
tags: [supply-chain, backdoor, credential-theft, telegram, pypi, typosquat, c2, fake-package]
---

## TL;DR

A threat actor published **8 fake `pyrogram` forks** to PyPI over 6 months (November 2025 – June 2026), planting a hidden backdoor that grants **full remote shell and file-system access** to any server running the infected bot — using the **victim's own Telegram bot as the C2 channel**, bypassing traditional network egress monitoring. ~24,300 total downloads across all malicious packages.

## What happened

Between **November 22, 2025 and June 7, 2026**, a threat actor operating under three PyPI identities (`wndrzzka`, `narutorawr18`, `deylin`) published 8 malicious packages to PyPI, each a trojanized clone of the legitimate `pyrogram` Telegram bot framework (347,395 monthly downloads).

The attackers injected a hidden file, `pyrogram/helpers/secret.py`, into legitimate pyrogram source code. The backdoor registered **invisible Telegram command handlers** that activate when messages are sent from 16 attacker-controlled Telegram accounts:

| Command | Effect |
|---|---|
| `/asu <code>` | Execute arbitrary Python on the server |
| `/wann <code>` | Execute arbitrary Python (alternate) |
| `/asi <cmd>` | Execute shell command via subprocess |
| `/wann2 <cmd>` | Execute shell command (alternate) |

**Stolen data travels back through Telegram itself** — using the victim's own bot token to send document attachments to the attacker. No outbound connection to an unfamiliar IP or domain is required; the exfil blends in as normal bot traffic on `api.telegram.org`.

Two injection techniques were used across packages: (1) import-time execution wired at the top of `__init__.py`, and (2) a hook buried inside the `Client.start()` lifecycle method — so the backdoor fires either at module import *or* at bot startup, depending on the variant.

The campaign operated under three separate PyPI publisher identities and published 32+ package versions in total. The shared Telegram control account ID `327471892` across multiple packages indicates coordinated operation rather than independent actors.

### Affected packages and download counts

| Package | Versions | Downloads |
|---|---|---|
| `pyrogram-navy` | 16+ | 15,370 |
| `vlifegram` | 9 | 4,150 |
| `kelragram` | 6 | 2,530 |
| `vlife-gram` | 5 | 1,030 |
| `sepgram` | 3 | 1,041 |
| `pyrogram-kelra` | 1 | 672 |
| `pyrogram-styled` | 1 | 432 |
| `pyrogram-zeeb` | 1 | 264 |
| **Total** | **32+** | **~24,300** |

All packages have been removed from PyPI following Checkmarx's disclosure on June 25, 2026.

## Am I affected?

Check your Python environment for any of the malicious package names:

```bash
# Check installed packages
pip show pyrogram-navy vlifegram vlife-gram kelragram pyrogram-styled sepgram pyrogram-zeeb pyrogram-kelra 2>/dev/null | grep -E "^Name:|^Version:"

# Check pip install history (Linux)
grep -E "pyrogram-navy|vlifegram|vlife-gram|kelragram|pyrogram-navy|pyrogram-styled|sepgram|pyrogram-zeeb|pyrogram-kelra" \
  ~/.local/share/pip/logs/*.log 2>/dev/null

# Check for the hidden backdoor file in any pyrogram installation
find $(python -c "import site; print(site.getsitepackages()[0])") \
  -path "*/pyrogram/helpers/secret.py" 2>/dev/null
```

If you find the backdoor file:
```bash
# Confirm the file exists (legitimate pyrogram does NOT have helpers/secret.py)
python -c "import pyrogram; import os; print(os.path.join(os.path.dirname(pyrogram.__file__), 'helpers', 'secret.py'))"
```

**Signs of compromise:**
- Any of the 8 package names in `pip list` or install logs
- `pyrogram/helpers/secret.py` present in your pyrogram installation
- Unexpected Telegram messages from your own bot (the backdoor uses the bot's own token)
- Unexplained file uploads in your bot's sent-messages history

## If you are affected

1. **Stop all affected bots immediately** — the backdoor uses the bot's own Telegram session, so simply stopping the process terminates attacker access to the C2 channel.
2. **Revoke all Telegram bot tokens** for bots that ran under affected packages, and generate new tokens via `@BotFather`. Token revocation invalidates any session the attacker may have been using.
3. **Treat the server as compromised** — the backdoor provides arbitrary shell and Python execution, meaning the attacker may have installed persistence, exfiltrated secrets, or pivoted. Follow the full server-compromise playbook.
4. **Rotate all credentials stored on the server** — API keys, database passwords, cloud credentials, SSH keys, `.env` files. Assume anything readable by the process was exfiltrated.
5. **Reinstall from the official `pyrogram` package** on PyPI: `pip install pyrogram`.

→ [Playbook: if your webapp was compromised](../playbooks/if-your-webapp-was-compromised.md)
→ [Playbook: rotating cloud credentials](../playbooks/rotating-cloud-credentials.md)

## Prevention

- **Install only the official `pyrogram` package.** The legitimate package is `pyrogram` (note: no suffixes, no "navy", no "styled", no user prefix). Verify publisher: `pip index versions pyrogram` should show the official Pyrogram maintainer.
- **Pin package versions with hash verification** in production bot deployments:
  ```
  pyrogram==2.0.106 --hash=sha256:<known-good-hash>
  ```
- **Audit your `requirements.txt` for unfamiliar pyrogram forks.** Any package with a `pyrogram-*` name that isn't the official one is suspect.
- **Monitor for new command registrations in your bot.** If your bot suddenly responds to commands you didn't implement, it may be compromised.
- **Restrict server outbound access** — even though this backdoor uses Telegram's API (which most orgs allow), limiting file-upload endpoints and monitoring for unexpected Telegram API calls from backend servers adds detection opportunity.

→ [Prevention: supply chain attack surface](../prevention/supply-chain-attack-surface.md)
→ [Prevention: package vetting checklist](../prevention/package-vetting-checklist.md)

## IOCs

| Type | Value |
|---|---|
| Malicious packages | `pyrogram-navy`, `vlifegram`, `vlife-gram`, `kelragram`, `pyrogram-styled`, `sepgram`, `pyrogram-zeeb`, `pyrogram-kelra` |
| PyPI publisher accounts | `wndrzzka`, `narutorawr18`, `deylin` |
| Backdoor file | `pyrogram/helpers/secret.py` |
| Shared attacker Telegram ID | `327471892` (present in multiple packages) |
| Total attacker Telegram IDs | 16 (full list in Checkmarx report) |
| Campaign name | Operation Navy Ghost |
| C2 channel | Victim's own Telegram bot (via `api.telegram.org`) |

## Technique note

The **Telegram-as-C2** pattern is distinct from every other PyPI backdoor tracked in this repo. Prior campaigns exfiltrate to attacker-controlled servers (GitHub Gists, disposable SSH tunnels, Google Calendar dead-drops, AI-vendor API host camouflage). This campaign uses the **victim's own bot token** to relay control through Telegram's infrastructure — which is allowlisted in virtually every corporate egress policy for bot deployments. Network-layer egress monitoring that flags unknown IPs or unexpected domains will not catch this technique.

## Sources

- [Checkmarx Zero — Operation Navy Ghost: How Attackers Planted a Telegram-Powered Backdoor Across Fake pyrogram Packages on PyPI](https://checkmarx.com/zero-post/operation-navy-ghost-pyrogram-telegram-supplychain-attack/) — primary disclosure; full package list, version counts, download totals, attacker Telegram IDs, YARA rule, injection technique analysis; published 2026-06-25.
