---
id: 2026-08-openvsx-evil-twin-extensions
title: "77 'evil twin' Open VSX extensions impersonate real tools, exfiltrate Git/CI metadata to a single C2 domain"
date_disclosed: 2026-08-04
last_updated: 2026-08-04
severity: high
status: contained
ecosystems: [open-vsx, vscode]
tools_affected: [Open VSX Registry, VS Code-compatible editors using Open VSX (Windsurf, VSCodium, Eclipse Theia, etc.)]
tags: [extension-marketplace, supply-chain, reconnaissance, typosquat, evil-twin, dns-txt-failover]
---

## TL;DR
Manifold Security found **77 counterfeit Open VSX extensions**, published between **2026-07-26 and 2026-08-01** under unrelated, unaffiliated accounts, each impersonating a real published extension (name/branding copied, all shipped as version `0.0.1`). All 77 beacon to a single domain, `mangorbit[.]com`, registered just 11 days before the campaign began. 58 of the extensions send only lightweight telemetry (hostname, workspace folder name, editor version); 19 go further and collect Git remote/branch/commit metadata and CI environment identifiers (GitHub, Azure DevOps, Buildkite, CircleCI, Gitpod). Open VSX removed the extensions by **2026-08-03**; developers must uninstall them manually.

## What happened
The "evil twin" technique: register a marketplace listing that copies a legitimate, already-trusted extension's name and description, publish it from a fresh account with no relationship to the real maintainer, and rely on a developer's search or a stale bookmark landing on the fake instead of (or alongside) the real one. All 77 extensions in this campaign were published as `0.0.1` — consistent with disposable, single-use publisher accounts rather than an established extension being hijacked.

**Two payload tiers, by extension count:**
- **58 lightweight variants (1.6–3.3 KB payload).** Transmit minimal telemetry — hostname, workspace folder name, editor version — tagged with a per-package tracking identifier, on install/activation.
- **19 reconnaissance-grade variants (~10 KB payload).** Collect materially more: Git configuration (origin/upstream remote URLs reduced to host + organization, commit email domain), repository metadata (current branch, HEAD commit SHA), CI/CD environment variables (`GITHUB_REPOSITORY`, `CI_PROJECT_PATH`, Azure DevOps URIs, Buildkite/CircleCI/Gitpod identifiers), workspace filesystem paths, and a full enumeration of the victim's other installed extensions.

**Infrastructure.** All 77 extensions communicate with `mangorbit[.]com`, registered **2026-07-15** — 11 days ahead of the first publish — via subdomains `pulse.mangorbit[.]com`, `pulse2.mangorbit[.]com`, and `api.mangorbit[.]com`, plus randomized `cb.mangorbit[.]com` entries. The malware queries `_beacon.<domain>` **DNS TXT records** to resolve its live C2 endpoint, allowing the operators to relocate infrastructure post-deployment without shipping new extension code. Retry logic spans seven days and treats any HTTP response — success or error — as beacon confirmation, a low-effort resilience pattern rather than a sophisticated one.

**Impersonated targets** spanned a mix of niche and higher-profile developer tools, including extensions branded around IOTA/Move blockchain tooling, Salesforce Marketing Cloud, ApexSQL, UAVCAN DSDL, LEGO Education tooling, and — notably — a listing impersonating `marketplace.visualstudio` itself.

**No actor attribution** has been published as of this writing. Manifold Security (researchers Ax Sharma and Cody Nash) discovered and disclosed the campaign; Open VSX removed all identified extensions by 2026-08-03, one day before public disclosure.

## Am I affected?
```bash
# List installed extensions and cross-check against the campaign's publishers/names
# (VS Code / VSCodium / any Open VSX-based editor)
code --list-extensions --show-versions   # or your editor's equivalent CLI

# Any extension you installed between 2026-07-26 and 2026-08-01 at version 0.0.1
# from a publisher you don't recognize is a candidate match — verify the publisher
# account against the extension's real, established maintainer before trusting it.
```
Also check outbound network logs (proxy, firewall, EDR) for any connection to `mangorbit[.]com` or its subdomains (`pulse.`, `pulse2.`, `api.`, `cb.`) from a developer workstation or CI runner — that confirms the payload executed, not just that the extension was installed.

## If you are affected
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)
1. Uninstall any matching extension immediately — Open VSX's own takedown does not remove it from machines that already installed it.
2. If any of the 19 reconnaissance-grade variants ran, treat your Git remotes, CI project identifiers, and workspace layout as disclosed to the attacker; rotate any CI tokens that a follow-on campaign could plausibly target using that recon.

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — apply the same "verify the publisher, not just the name" discipline to editor extensions that you would to an npm/PyPI package.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
- Before installing any Open VSX or VS Code Marketplace extension, check the publisher's account age and prior publish history — a `0.0.1` release from a brand-new account impersonating an established tool's name is the exact pattern this campaign used.
- Block or alert on outbound connections to newly-registered domains from developer/CI environments; a domain registered days before first use is a recurring IOC across extension-marketplace campaigns this repo tracks (WhiteCobra/LummaStealer, GlassWorm).

## Why this matters for vibe coders
This is a sibling of the already-tracked **WhiteCobra** (persistent VS Code/Open VSX threat actor, LummaStealer payloads, $500K in stolen crypto) and **GlassWorm** (steganographic Open VSX worm) campaigns, but a distinct actor and infrastructure: no crypto-wallet targeting, no invisible-Unicode payload concealment, and a DNS-TXT-record C2-relocation trick not previously documented in this repo's extension-marketplace coverage. It reinforces that **IDE extension marketplaces are functioning as a second, less-scrutinized package registry** — treat an extension install with the same skepticism as an `npm install` of an unfamiliar package, especially version `0.0.1` releases impersonating a name you already trust.

## Sources
- [Manifold Security — Open VSX 'Evil Twin' extensions](https://www.manifold.security/blog/open-vsx-evil-twin-extensions) — primary disclosure: full technical breakdown, IOC list, C2 infrastructure, impersonated-extension list, researcher attribution.
- [The Hacker News — Open VSX Removes 77 Malicious Evil Twin Extensions Exfiltrating Developer Data](https://thehackernews.com/2026/08/open-vsx-removes-77-malicious-evil-twin.html) — independent corroboration, 2026-08-04, takedown-timeline confirmation.
- [BleepingComputer — 77 Open VSX extensions found harvesting developer info](https://www.bleepingcomputer.com/news/security/77-open-vsx-extensions-found-harvesting-developer-info/) — independent corroboration.
