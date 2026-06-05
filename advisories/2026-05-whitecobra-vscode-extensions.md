---
id: 2026-05-whitecobra-vscode-extensions
title: "WhiteCobra — recurring VS Code / Cursor / Windsurf / Open VSX crypto-stealer campaign (July 2025 → ongoing)"
date_disclosed: 2025-07-01
last_updated: 2026-06-05
severity: high
status: active
ecosystems: [vscode, cursor, windsurf, openvsx]
tools_affected: [VS Code, Cursor, Windsurf, any IDE using Open VSX extensions]
tags: [supply-chain, extension-marketplace, credential-theft, crypto-theft, lummastealer, malicious-extension]
---

## TL;DR

**WhiteCobra** is a persistent, funded threat-actor campaign that continuously floods the VS Code Marketplace and Open VSX registry with malicious extensions targeting crypto wallet users of **Cursor** and **Windsurf**. The group stole **$500,000** in July 2025 via a fake Solidity syntax-highlighting extension, was publicly exposed by Koi Security in May 2026, and can deploy a new campaign in under **3 hours** — so removals don't stop the campaign.

## What happened

WhiteCobra has published at least **24 malicious extensions** across the VS Code Marketplace and Open VSX registry. The campaign targets developers who use AI coding tools (Cursor, Windsurf) for blockchain and smart-contract development.

**Timeline:**
- **July 2025** — Initial $500,000 crypto theft via `contractshark.solidity-lang` (Cursor/Open VSX). The extension had professionally designed icons, a detailed description, and **54,000 downloads** on OpenVSX. The victim, Ethereum core developer Zak Cole, described how his wallet was drained.
- **2025–2026 ongoing** — Campaign continues; removed extensions are quickly replaced. Koi Security says WhiteCobra can deploy a new campaign in **under 3 hours**.
- **May 2026** — Koi Security published "WhiteCobra's Playbook Exposed," detailing C2 infrastructure setup guides, defined revenue targets of $10,000–$500,000 per campaign, and social engineering / marketing promotion strategies.
- **2026** — Malicious extensions resurface on OpenVSX after takedowns.

**Attack mechanism:**
1. Extension publishes to Open VSX (and mirrors to VS Code Marketplace) targeting developers who search for Solidity, Ethereum, web3, or AI coding extensions.
2. Extensions look legitimate — professional branding, high download counts achieved through promotion, detailed documentation.
3. On installation (Windows): a PowerShell script executes a Python script that shellcode-loads **LummaStealer** (a commercial info-stealer).
4. LummaStealer targets: **cryptocurrency wallet apps**, web browser extensions holding seed phrases/private keys, browser-stored credentials, and messaging apps.
5. Credentials exfiltrated to attacker C2; WhiteCobra converts crypto access to cash.

**Why `--ignore-scripts` doesn't help:** This attack installs via extension activation (VS Code extension marketplace install), not npm package install. The delivery is the IDE's own extension system.

**Connection to the Open Sesame vulnerability:** The Open VSX "Open Sesame" flaw (disclosed February 8, 2026, patched in version 0.32.0) allowed malicious extensions to bypass pre-publish security scanning by triggering a scanner-failure condition misinterpreted as "no scanners configured." This vulnerability likely lowered the barrier for WhiteCobra extensions to pass automated review checks. The flaw was found by Koi Security researcher Oran Simhony.

## Am I affected?

```bash
# Check for suspicious extensions recently installed in VS Code / Cursor / Windsurf
code --list-extensions 2>/dev/null | grep -i -E "solidity|ethereum|web3|contractshark|crypto|defi|blockchain"
# Note: Cursor and Windsurf use similar commands (cursor --list-extensions, etc.)

# Check for unexpected Python scripts or PowerShell one-liners in recent extension activity
ls -lt ~/.cursor/extensions/ | head -20   # Cursor
ls -lt ~/.windsurf/extensions/ | head -20  # Windsurf
ls -lt ~/.vscode/extensions/ | head -20    # VS Code

# On macOS, check for LummaStealer IOCs in common exfil paths
find ~/Library -name "*.log" -newer /tmp/last_week -size +1k 2>/dev/null | head -10
```

**High-risk profile:** If you use Cursor or Windsurf for Solidity/Ethereum/web3 development and have any crypto wallet browser extensions or desktop apps, you are the primary target.

## If you are affected

1. **Revoke any crypto wallet browser extensions** and regenerate wallet seed phrases immediately — assume any seed phrase that was ever on the affected machine is compromised.
2. **Rotate cloud credentials and GitHub tokens** (LummaStealer harvests browser-stored credentials broadly).
3. **Check npm tokens and API keys** stored in the browser.
4. **Uninstall any suspicious extension** and audit the full extension list against the [Open VSX trusted publisher list](https://open-vsx.org).
5. **Report to Koi Security** if you discover a new WhiteCobra extension variant.

## Prevention

- **Vet extension publishers before installing.** On Open VSX: check the publisher's history, number of extensions, and whether the publisher is the same as the upstream VS Code Marketplace publisher (Cursor/Windsurf use Open VSX; the namespace may be different from the Microsoft Marketplace).
- **Disable silent extension auto-update** in your AI IDE settings. Review extension changelogs manually before updating.
- **For Solidity/web3 development:** prefer well-known publishers with long histories (e.g., `JuanBlanco.solidity` for Solidity syntax) rather than newer alternatives.
- **Never keep wallet seed phrases in browser storage** on a development machine. Use hardware wallets for signing.
- **Check extension download counts critically:** WhiteCobra uses marketing and promotion to inflate counts artificially — 54,000 downloads is not an indication of legitimacy.

## Sources

- [BleepingComputer — "WhiteCobra floods VSCode market with crypto-stealing extensions"](https://www.bleepingcomputer.com/news/security/whitecobra-floods-vscode-market-with-crypto-stealing-extensions/) — campaign overview, Zak Cole victim case, LummaStealer payload detail.
- [Koi Security — "WhiteCobra's Playbook Exposed"](https://www.koi.ai/blog/whitecobra-vscode-cursor-extensions-malware) — threat actor profiling, C2 guide, revenue targets, 3-hour deployment capability.
- [BleepingComputer — "Malicious crypto-stealing VSCode extensions resurface on OpenVSX"](https://www.bleepingcomputer.com/news/security/malicious-crypto-stealing-vscode-extensions-resurface-on-openvsx/) — ongoing campaign persistence.
- [BleepingComputer — "Malicious VSCode extension in Cursor IDE led to $500K crypto theft"](https://www.bleepingcomputer.com/news/security/malicious-vscode-extension-in-cursor-ide-led-to-500k-crypto-theft/) — initial incident, Zak Cole account, July 2025.
- [The Hacker News — "Open VSX Bug Let Malicious VS Code Extensions Bypass Pre-Publish Security Checks"](https://thehackernews.com/2026/03/open-vsx-bug-let-malicious-vs-code.html) — Open Sesame vulnerability context.
- Cross-reference: [2026-01-vscode-fork-recommended-extension-hijack.md](2026-01-vscode-fork-recommended-extension-hijack.md), [2025-10-glassworm-vscode-worm.md](2025-10-glassworm-vscode-worm.md).
