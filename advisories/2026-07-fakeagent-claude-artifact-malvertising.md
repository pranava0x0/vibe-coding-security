---
id: 2026-07-fakeagent-claude-artifact-malvertising
title: "FakeAgent — malicious Bing ad + poisoned Claude Artifact push a fake \"Claude Desktop\" installer that deploys SectopRAT (July 2026)"
date_disclosed: 2026-07-23
last_updated: 2026-07-23
severity: high
status: contained
ecosystems: [claude-ai, claude-desktop]
tools_affected: [claude-ai-artifacts, claude-desktop]
tags: [malvertising, trust-abuse, infostealer, rat, dll-sideloading, etherhiding, claude-artifacts]
---

## TL;DR
Between **2026-07-21 and 07-22**, attackers ran Bing search ads for "Claude Desktop app" that led to a **legitimate `claude.ai` Artifact** (a public page hosted on Anthropic's own domain, viewed ~7,100 times before takedown) which redirected victims to a fake `ClaudeDesktop.exe` installer. The installer sideloaded a malicious DLL through a genuine JetBrains Chromium helper binary to deploy the **SectopRAT** (ArechClient2) infostealer, using Ethereum-transaction-based "EtherHiding" for command-and-control. At least **29 organizations** were compromised in two days. Anthropic removed the poisoned Artifact after Huntress reported it; no product vulnerability was involved — this abused Claude.ai's legitimate Artifact-hosting feature as a malware-distribution shell.

## What happened
Huntress identified a malvertising campaign it named **FakeAgent**: victims searching Bing for "Claude Desktop app" saw a sponsored ad linking not to a spoofed lookalike domain but to a **public Claude Artifact hosted directly on claude.ai** — trustworthy-looking because the URL itself is genuine Anthropic infrastructure. The Artifact acted as a fake download portal and redirected through `claude.ai.download-app[.]us` to `downloading-api.it[.]com`, where victims downloaded `ClaudeDesktop.exe` ([Huntress](https://www.huntress.com/blog/fakeagent-claude-desktop-malvertising-ends-in-dotnet-rat); [BleepingComputer](https://www.bleepingcomputer.com/news/security/fake-claude-app-promoted-by-bing-ads-pushes-sectoprat-malware/)).

The "installer" is actually JetBrains' legitimate `jcef_helper.exe`, abused via **DLL sideloading**: it loads an attacker-supplied `libcef.dll` in place of the real Chromium Embedded Framework library. That DLL is packed with VMProtect and contains an embedded Ethereum smart-contract reference used for C2 ("EtherHiding" — the same blockchain-covert-channel technique this repo tracks elsewhere for supply-chain worm C2, here applied to a desktop-malware delivery chain rather than a package). A secondary payload, `DockerDesktop.exe`, establishes persistence via a scheduled task. A companion DLL (`tempdir.dll`) performs GPU/DirectX-based anti-VM checks (examining DirectX adapters for virtualization signatures) before a shader-based AES-256-CTR routine decrypts the final payload — an unusually elaborate anti-analysis chain for a malvertising drop.

The end payload is **SectopRAT (ArechClient2)**, a long-running .NET-based RAT/infostealer that targets browser-stored passwords, payment card data, and messaging-app credentials.

Huntress traced the domain-registration email behind the campaign to at least **10 other malware-distribution domains dating to December 2025**, one of which was previously linked to StealC and had infrastructure seized during **Operation Endgame**; Huntress also connected the actor to an earlier **April 2026 Docker Hub campaign** that used the identical DLL-sideloading technique. Neither source offers a confident named-actor attribution.

Anthropic removed the malicious Artifact after Huntress's report; no confirmation of a fix to the Artifacts feature itself has been published, since the abuse relied on social engineering (a fake ad + a public Artifact used as a landing page) rather than a vulnerability in Claude.ai.

## Am I affected?
This is a desktop-malware campaign delivered via a fake installer, not a package or dependency — check for the artifacts of the installer chain rather than a version string:

```bash
# Windows: look for the sideloaded/dropped files from this campaign
# (adjust search roots to wherever a "ClaudeDesktop.exe"/"DockerDesktop.exe" may have been run from)
dir /s /b "%USERPROFILE%\Downloads\ClaudeDesktop.exe" "%USERPROFILE%\Downloads\DockerDesktop.exe" 2>nul
dir /s /b "%TEMP%\libcef.dll" "%TEMP%\tempdir.dll" 2>nul

# Check scheduled tasks for anything unfamiliar created around 2026-07-21/22
schtasks /query /fo LIST /v | findstr /i "Docker Claude"
```
You never installed Claude Desktop via a Bing ad or a `claude.ai` Artifact link — the real installer is only ever distributed from `claude.ai/download` directly (not from a shared Artifact page). If a machine downloaded and ran `ClaudeDesktop.exe` from a search-ad-driven link on 2026-07-21 or 07-22, treat it as compromised.

## If you are affected
→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) — for credential/session rotation guidance if a dev workstation ran the payload.
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — SectopRAT harvests browser-stored credentials broadly; rotate anything that was logged into a browser session on the affected machine.

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — avoid storing long-lived credentials in browser password managers on developer machines that also browse the open web.
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — the general discipline applies to installers too: always download developer tools from the vendor's own documented download page, never from a search-ad link, even when the ad's landing page resolves to the vendor's real domain.

## Why this matters for vibe coders
This is a distinct category from the CVEs and supply-chain package compromises this repo usually tracks: it's **trust-abuse of a legitimate AI-vendor hosting feature** (Claude Artifacts) as a malware-distribution shell, not a bug in Claude Desktop or Claude.ai itself. Anyone who has ever shared or opened a public Claude Artifact link should treat "the URL is claude.ai" as necessary but **not sufficient** evidence of safety — a search ad can point to attacker-controlled content hosted on a fully legitimate first-party domain. The same lesson applies to any platform (Notion, GitHub Pages, Google Sites, Vercel previews) that lets any user publish content under a trusted first-party domain.

## Sources
- [Huntress — FakeAgent: Claude Desktop Malvertising Ends in .NET RAT](https://www.huntress.com/blog/fakeagent-claude-desktop-malvertising-ends-in-dotnet-rat) — primary technical writeup: full delivery chain, DLL sideloading detail, EtherHiding C2 analysis, actor infrastructure history.
- [BleepingComputer — Fake Claude app promoted by Bing ads pushes SectopRAT malware](https://www.bleepingcomputer.com/news/security/fake-claude-app-promoted-by-bing-ads-pushes-sectoprat-malware/) — independent corroboration, 29-organization impact figure, Anthropic's removal of the Artifact.
