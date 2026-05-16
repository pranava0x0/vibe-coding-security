---
id: 2025-11-shai-hulud-second-coming
title: "Shai-Hulud 'The Second Coming' (November 2025)"
date_disclosed: 2025-11-24
last_updated: 2026-05-16
severity: critical
status: contained
ecosystems: [npm]
tools_affected: [any-node-project, cursor, claude-code, lovable, bolt, replit]
tags: [supply-chain, worm, credential-theft, npm, github, trufflehog]
---

## TL;DR
On 2025-11-24, attackers launched the second Shai-Hulud wave: 492 npm packages (132M monthly downloads) trojanized, including packages from Zapier, ENS Domains, PostHog, and Postman. The worm scanned for secrets with TruffleHog, dumped them to public GitHub repos, then re-published itself into every package its compromised maintainers owned. 25,000+ malicious GitHub repos appeared in days.

## What happened
A more aggressive, more automated version of the original Shai-Hulud worm. Key differences vs. the September 2025 wave:

- **Uses bun.** Drops `setup_bun.js` to install Bun, then runs `bun_environment.js` (the real payload). Faster, harder to scan with classic Node tooling.
- **Uses TruffleHog.** Runs the open-source secret scanner on the host filesystem to maximize credential haul.
- **Targets enterprise.** Packages from Zapier, ENS, PostHog, Postman caught in the wave — broad supply-chain exposure across SaaS toolchains.
- **Timing.** Aligned with npm's deadline to revoke classic tokens (2025-12-09). Attackers raced to exploit unmigrated maintainer accounts.

The worm published 25,000+ public GitHub repositories across ~350 unique users, each containing exfiltrated secrets in base64-encoded JSON files.

## Am I affected?

```bash
# If you installed ANY of these in late Nov / early Dec 2025
npm ls --all 2>/dev/null | grep -iE '(zapier|ens|posthog|postman)'

# Generic: search for the worm's GitHub repo signature
gh search repos "shai-hulud" --limit 50
gh search repos "Shai-Hulud" --owner YOUR_USER  # check your own org didn't get a planted repo
```

```bash
# Check for the worm's bun-based execution traces
find ~/.npm -name "setup_bun.js" -o -name "bun_environment.js" 2>/dev/null
```

If you find traces or installed an affected package during the window, treat all credentials on the machine as compromised.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — `--ignore-scripts`, lockfile audits
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — don't keep long-lived tokens on disk

## Timeline
- **2025-11-24** — second wave detected, takedowns begin
- **2025-12-09** — npm classic token revocation deadline (the reason attackers raced)
- **2026-05-16** — most packages cleaned, but old lockfiles still vulnerable

## Sources
- [Microsoft Security Blog — Shai-Hulud 2.0: Guidance for detecting, investigating, and defending](https://www.microsoft.com/en-us/security/blog/2025/12/09/shai-hulud-2-0-guidance-for-detecting-investigating-and-defending-against-the-supply-chain-attack/)
- [Wiz — Sha1-Hulud 2.0 Supply Chain Attack: 25K+ Repos Exposed](https://www.wiz.io/blog/shai-hulud-2-0-ongoing-supply-chain-attack)
- [Aikido — Shai Hulud 2.0 Strikes Again: Zapier & ENS Domains](https://www.aikido.dev/blog/shai-hulud-strikes-again-hitting-zapier-ensdomains)
- [Palo Alto Unit 42 — Shai-Hulud Worm Compromises npm Ecosystem (Updated Nov 26)](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/)
- [Socradar — Shai Hulud's "The Second Coming"](https://socradar.io/blog/shai-hulud-the-second-coming-npm-campaign/)
- [Netskope — Shai-Hulud 2.0: Aggressive, Automated, and Fast Spreading](https://www.netskope.com/blog/shai-hulud-2-0-aggressive-automated-one-of-fastest-spreading-npm-supply-chain-attacks-ever-observed)
