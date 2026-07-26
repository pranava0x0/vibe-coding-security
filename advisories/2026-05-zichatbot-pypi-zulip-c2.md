---
id: 2026-05-zichatbot-pypi-zulip-c2
title: "ZiChatBot — 3 trojanized PyPI packages use the Zulip chat API as C2, suspected OceanLotus/APT32 (May 2026)"
date_disclosed: 2026-05-06
last_updated: 2026-07-26
severity: medium
status: contained
ecosystems: [pypi, python]
tools_affected: [uuid32-utils, colorinal, termncolor]
tags: [supply-chain, backdoor, typosquat, pypi, c2, in-channel-c2, nation-state]
---

## TL;DR

Kaspersky disclosed **ZiChatBot**, a backdoor hidden inside three typosquatted PyPI packages (`uuid32-utils`, `colorinal`, `termncolor`) uploaded in July 2025 and undetected for nearly ten months. Instead of a dedicated C2 server, the malware relays commands and exfiltrates data through **Zulip's public team-chat REST API** — the same "use a trusted chat platform as C2" pattern this repo already tracked in [Operation Navy Ghost's Telegram-as-C2](2026-06-operation-navy-ghost-pyrogram.md), now confirmed on a second messaging platform. Kaspersky suspects a link to **OceanLotus/APT32** based on 64% dropper-code similarity to a previously attributed sample, but calls that attribution unconfirmed.

## What happened

Between **July 16–22, 2025**, two PyPI publisher accounts uploaded three packages designed to look like unremarkable Python utilities:

| Package | First uploaded | Downloads (as of disclosure) |
|---|---|---|
| `uuid32-utils` | 2025-07-16 | 1,479 |
| `colorinal` | 2025-07-22 | 614 |
| `termncolor` | 2025-07-22 | 387 |

`termncolor` declared `colorinal` as a dependency, so installing the "wrapper" package pulled in the malicious one — a plausible-deniability layering technique. Each wheel bundled a native dropper (`terminate.dll` on Windows, `terminate.so` on Linux) that Python loads at import time via `__init__.py` → `unicode.py`. The dropper decrypts an embedded payload with AES-CBC (key string `"xterminalunicode"`), drops a final-stage DLL (`libcef.dll`, loaded by a legitimate-looking helper `vcpktsvr.exe`), and installs persistence: a `Run` registry key (`pkt-update` → `vcpktsvr.exe`) on Windows, a crontab entry (`/tmp/obsHub/obs-check-update`) on Linux.

The payload — designated **ZiChatBot** — supports exactly one control command: fetch and execute shellcode. Rather than a fixed C2 server, it authenticates to the public team-chat platform **Zulip** (organization `helper.zulipchat.com`, credential `Morian-bot@helper.zulipchat.com`) and uses two channel/topic pairs — one to report system info, one to receive shellcode — blending in as ordinary chat-app traffic on a domain most corporate egress policies allow by default. Zulip has since deactivated the abused organization.

Kaspersky's KTAE similarity engine found the dropper's decryption/decompression routine 64% similar to a previously attributed OceanLotus (APT32) sample, and notes OceanLotus's documented pivot into supply-chain attacks (a prior 2025 GitHub-phishing campaign) as circumstantial support — but states this explicitly as a suspected, not confirmed, link. Kaspersky also reports no observed infections in its own telemetry or public reports as of disclosure, despite the ten-month dwell time.

## Am I affected?

```bash
# Check for the three known-malicious package names
pip show uuid32-utils colorinal termncolor 2>/dev/null | grep -E "^Name:|^Version:"

# Check pip install history
grep -E "uuid32-utils|colorinal|termncolor" ~/.local/share/pip/logs/*.log 2>/dev/null

# Look for the dropper files inside any installed copy
find $(python -c "import site; print(site.getsitepackages()[0])") \
  \( -name "terminate.dll" -o -name "terminate.so" -o -name "libcef.dll" \) 2>/dev/null

# Windows persistence check
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v pkt-update 2>nul

# Linux persistence check
crontab -l 2>/dev/null | grep -i "obs-check-update\|obsHub"
```

## If you are affected

1. Kill any process descended from `vcpktsvr.exe` (Windows) or the cron-launched `obs-check-update` job (Linux).
2. Remove the `pkt-update` registry Run key or the `obsHub` crontab entry.
3. Treat the host as fully compromised — the payload executes arbitrary shellcode with the user's privileges. Follow the general webapp/server-compromise playbook and rotate credentials the process could reach.
4. Uninstall the three packages and reinstall only genuinely-needed dependencies from verified, actively-maintained projects.

→ [Playbook: if you installed a bad npm/PyPI package](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [Playbook: rotating cloud credentials](../playbooks/rotating-cloud-credentials.md)

## Prevention

- Treat unfamiliar single-purpose "utility" packages (uuid generators, terminal-color helpers) with the same scrutiny as high-profile dependencies — these are exactly the low-attention, low-download names attackers pick for long dwell times.
- Audit `requirements.txt`/lockfiles for packages with very low download counts relative to their apparent age, and for wrapper packages whose only purpose is depending on another obscure package.
- Monitor egress from build/CI/production hosts for connections to chat-platform APIs (Zulip, Slack, Telegram, Discord) from processes that aren't your actual chat integration — this pattern generalizes beyond Telegram (see the Navy Ghost cross-link below) to any messaging API a compromised host's process can reach.

→ [Prevention: package vetting checklist](../prevention/package-vetting-checklist.md)
→ [Prevention: supply chain attack surface](../prevention/supply-chain-attack-surface.md)

## IOCs

| Type | Value |
|---|---|
| Malicious packages | `uuid32-utils`, `colorinal`, `termncolor` |
| Publisher accounts | email prefixes `laz***@tutamail.com`, `sym***@proton.me` (per Kaspersky, partially redacted) |
| Dropper files | `terminate.dll` (Windows), `terminate.so` (Linux) |
| Final-stage payload | `libcef.dll`, loaded via `vcpktsvr.exe` |
| Windows persistence | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run\pkt-update` → `vcpktsvr.exe` |
| Linux persistence | crontab entry `/tmp/obsHub/obs-check-update` (hourly) |
| C2 infrastructure | Zulip organization `helper.zulipchat.com`, account `Morian-bot@helper.zulipchat.com` (deactivated by Zulip) |
| Malware family | ZiChatBot |
| Suspected attribution | OceanLotus / APT32 (unconfirmed, 64% code similarity only) |

## Technique note

This is the **second in-channel-C2 campaign this repo tracks** after [Operation Navy Ghost](2026-06-operation-navy-ghost-pyrogram.md)'s Telegram-based backdoor, confirming the pattern generalizes beyond Telegram: any application holding credentials to a trusted messaging/chat API (Zulip, Slack, Discord, Telegram) can be weaponized as an "in-band" C2 channel that egress monitors tuned for unfamiliar IPs/domains will not catch. Network defenders should treat unexpected chat-API traffic from non-chat-integration processes as a detection signal, not just unfamiliar domains.

## Sources

- [Securelist (Kaspersky) — OceanLotus suspected of distributing ZiChatBot malware via wheel packages in PyPI](https://securelist.com/oceanlotus-suspected-pypi-zichatbot-campaign/119603/) — primary disclosure; package names, dropper mechanics, IOCs, attribution reasoning; published 2026-05-06.
- [Daily Security Review — ZiChatBot Backdoor Uses Zulip API as C2 in PyPI Supply Chain Attack](https://dailysecurityreview.com/cyber-security/zichatbot-backdoor-uses-zulip-api-as-c2-in-pypi-supply-chain-attack/) — independent corroboration of package names, download counts, and Zulip C2 mechanism.
