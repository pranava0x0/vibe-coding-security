---
id: 2026-01-vscode-fork-recommended-extension-hijack
title: "AI IDEs recommend non-existent extensions — OpenVSX namespace hijack (Jan 2026)"
date_disclosed: 2026-01-05
last_updated: 2026-05-23
severity: high
status: mitigated
ecosystems: [vscode, openvsx]
tools_affected: [cursor, windsurf, google-antigravity, trae, any-vscode-fork]
tags: [supply-chain, ide-extension, openvsx, namespace-hijack, recommendation-poisoning, slopsquatting-adjacent]
---

## TL;DR
Koi Security found that the major VS Code-fork AI IDEs — **Cursor, Windsurf, Google Antigravity, and Trae** — ship a recommended-extensions list that points at extensions which **don't exist on OpenVSX** (the marketplace those forks actually use). Because the **publisher namespaces were unclaimed**, anyone could register them and upload malware, and every developer with the matching tool installed would see the IDE itself say **"Recommended: …"** — a trusted-by-the-vendor install prompt that runs an attacker's extension with **full system access**. Cursor fixed it **2025-12-01**; Google removed the recommendations and marked it fixed **2026-01-01**; **Windsurf never responded**. Koi pre-registered the dangling namespaces to block exploitation; **no malicious abuse was observed before disclosure.**

## What happened
Cursor, Windsurf, Antigravity, and Trae are forks of Microsoft VS Code. They inherited VS Code's **hardcoded recommended-extensions configuration**, which references extensions by their **Microsoft Visual Studio Marketplace** identity. But these forks can't use the MS Marketplace — they use **OpenVSX** (operated by the Eclipse Foundation). Many of the recommended extensions (and their **publisher namespaces**) **were never published to OpenVSX**, leaving those namespaces **unclaimed and registerable by anyone**.

The attack is a clean recommendation-poisoning chain:
1. Attacker registers an unclaimed namespace on OpenVSX — e.g. `ms-ossdata.vscode-postgresql`.
2. Uploads a malicious extension under it.
3. A developer (say, one who uses PostgreSQL) opens Cursor/Windsurf/Antigravity, and the IDE surfaces **"Recommended: PostgreSQL extension."**
4. The developer trusts the IDE's own recommendation and clicks install. The extension runs with **full local privileges** — SSH keys, AWS credentials, source code, all reachable for exfiltration.

This is **slopsquatting-adjacent** but distinct: it's not an AI hallucinating a package name ([slopsquatting](ongoing-slopsquatting.md)), it's the **IDE's trusted recommendation surface** pointing at a registry where the name is up for grabs — a *marketplace-divergence* gap. It sits alongside the [Nx Console poisoning](2026-05-nx-console-vscode-compromise.md) (hijacking a *real* extension) and [GlassWorm](2025-10-glassworm-vscode-worm.md) (worming through Open VSX) as the third distinct IDE-extension supply-chain shape.

Koi disclosed to the vendors in **late November 2025**. **Cursor** fixed it on **2025-12-01**. **Google** removed **13** extension recommendations from Antigravity on 2025-12-26 and marked the issue fixed on **2026-01-01** (after initially closing the report). **Windsurf** never responded. As a stopgap, Koi **claimed the dangling namespaces** itself and uploaded inert placeholder extensions (its `ms-ossdata.vscode-postgresql` placeholder has 500+ installs), and coordinated with the **Eclipse Foundation** to verify referenced namespaces, remove non-official contributors, and add registry-level safeguards.

## Am I affected?
You are exposed if you use **Windsurf** (unfixed at disclosure) or an **older build** of Cursor / Antigravity / Trae from before the fixes, and you act on the IDE's "Recommended extensions" prompt.

```bash
# What extensions has your fork actually installed (and from where)?
cursor --list-extensions --show-versions 2>/dev/null
windsurf --list-extensions --show-versions 2>/dev/null

# Inspect the recommended-extensions config in your workspaces/profiles
grep -rn 'recommendations' .vscode/extensions.json ~/.cursor ~/.windsurf 2>/dev/null

# Distrust auto-recommended extensions: verify the publisher on OpenVSX
# (open.vsx.org/extension/<publisher>/<name>) before installing anything the IDE suggests.
```

If you installed an extension solely because the IDE recommended it, **verify the publisher is the genuine, official author on OpenVSX** — not a freshly-registered namespace. When in doubt, remove it and rotate any credentials reachable from that machine.

### Facts

| Type | Value |
|---|---|
| Researcher | Koi Security |
| Affected IDEs | Cursor, Windsurf, Google Antigravity, Trae (VS Code forks on OpenVSX) |
| Root cause | inherited MS-Marketplace recommendations + **unclaimed OpenVSX namespaces** |
| Example namespace | `ms-ossdata.vscode-postgresql` (was unclaimed) |
| Cursor fix | 2025-12-01 |
| Google/Antigravity fix | 13 recs removed 2025-12-26; marked fixed 2026-01-01 |
| Windsurf | no response |
| Exploitation seen | none before disclosure (Koi pre-claimed namespaces) |

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) — closest analogue for "a tool inside my editor was hostile"; rotate everything the editor could reach.
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — vet IDE extensions like packages: confirm the publisher, install count, and source before installing, even when the IDE "recommends" it.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ **Don't trust an IDE recommendation as proof of authenticity.** On OpenVSX-backed forks, a "Recommended" label only means the name was in a config file — not that the publisher is who you think. Verify on open.vsx.org first.

## Sources
- [Koi Security — How We Prevented Cursor, Windsurf & Google Antigravity from Recommending Malware](https://www.koi.ai/blog/how-we-prevented-cursor-windsurf-google-antigravity-from-recommending-malware) — canonical research, namespace list, vendor timeline.
- [The Hacker News — VS Code Forks Recommend Missing Extensions, Creating Supply Chain Risk in Open VSX](https://thehackernews.com/2026/01/vs-code-forks-recommend-missing.html)
- [BleepingComputer — VSCode IDE forks expose users to "recommended extension" attacks](https://www.bleepingcomputer.com/news/security/vscode-ide-forks-expose-users-to-recommended-extension-attacks/)
- [SC Media — AI IDEs pushed fake extensions, posing malware risk, say researchers](https://www.scworld.com/news/ai-ides-pushed-fake-extensions-posing-malware-risk-say-researchers)
- [GBHackers — Cursor, Windsurf & Google Antigravity IDEs Linked to Malicious Extension Exposure](https://gbhackers.com/cursor-windsurf-google-antigravity-ides-linked-to-malicious-extension/)
- [Cyberwarzone — VSCode fork extension attack: hijacked recommendations](https://cyberwarzone.com/2026/01/06/vscode-fork-extension-attack-hijacked-recommendations/)
