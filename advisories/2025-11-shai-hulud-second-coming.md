---
id: 2025-11-shai-hulud-second-coming
title: "Shai-Hulud 'The Second Coming' (November 2025)"
date_disclosed: 2025-11-24
last_updated: 2026-07-17
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
- **2026-07-15/16** — new named victim surfaces 8 months later: AI music-generation company **Suno** (see below)

## Update 2026-07-17 — new named victim: Suno (AI music generator), disclosed via hacker-to-journalist leak, not vendor postmortem

A hacker using the handle **ellie.191** shared Suno's internal source code (2023–2024 vintage) and a customer data set (emails, phone numbers, Stripe payment details for reportedly hundreds of thousands of accounts) with journalist Jason Koebler at [404 Media](https://www.404media.co/hack-reveals-suno-ai-music-generator-scraped-youtube-deezer-and-genius/), published 2026-07-15. The leaked code documents Suno's training-data ingestion pipeline (YouTube Music, Deezer, Genius, Pond5, Jamendo, Freesound, IMSLP, podcast RSS feeds — millions of clips, tens of thousands of hours of audio), which is separately significant for the music-labels' litigation against Suno; that data-sourcing angle is outside this repo's scope and is not covered further here.

**Attack-vector attribution — hedge explicitly:** the hacker themselves claims initial access came from **stealing an employee's credentials via the Shai-Hulud npm supply-chain worm**, then using those credentials to pull internal source code. This claim is *not* independently forensically confirmed by Suno or a security researcher in any source found this sweep — it is the intruder's own account, reported consistently by two independently-fetched outlets ([Cryptobriefing](https://cryptobriefing.com/suno-hack-ai-music-data-scraping/): *"The attack vector was a npm supply-chain worm called Shai-Hulud"*; [Decrypt](https://decrypt.co/373682/leaks-reveal-suno-fed-thousands-hours-deezer-youtube-pond5-data-ai): *"The intruder claims to have used a piece of malware called the Shai-Hulud worm"*), but the primary breach-disclosure article (404 Media) does not itself name a vector. Treat the Shai-Hulud attribution as **claimed, not confirmed**.

**Suno's response:** the company says it identified the incident in **November 2025** — squarely inside this advisory's "Second Coming" wave window (2025-11-24 detection) — and characterized it internally as "limited" and "quickly contained," stating the exposed code was outdated and no longer in use, and concluding individual customer notifications weren't legally required. It did not proactively disclose the breach to users or the public; the incident only became known because the hacker leaked material to a journalist roughly 8 months later. Suno did not respond to Decrypt's request for comment on the record beyond that characterization.

**Why this belongs in this advisory rather than as a standalone entry:** the November 2025 timing places the claimed initial-access credential theft inside the already-tracked Second Coming wave (this file), and the pattern — a worm-driven credential theft disclosed publicly only much later, via the attacker's own leak rather than the victim's own postmortem — is itself a recurring shape worth flagging for future sweeps: **check named victims of past Shai-Hulud/Miasma waves for delayed self-disclosure or attacker-leak disclosure months after the original wave**, since a vendor's internal "contained" assessment doesn't mean the public ever learns what was actually taken.

## Sources (2026-07-17 update)
- [404 Media — Hack Reveals Suno AI Music Generator Scraped YouTube, Deezer, and Genius](https://www.404media.co/hack-reveals-suno-ai-music-generator-scraped-youtube-deezer-and-genius/) — primary breach disclosure; does not itself name an attack vector.
- [Cryptobriefing — Hack reveals Suno's data scraping methods for AI music generation](https://cryptobriefing.com/suno-hack-ai-music-data-scraping/) — independent corroboration naming Shai-Hulud as the claimed vector.
- [Decrypt — Leaks Reveal Suno Fed Thousands of Hours of Deezer, YouTube and Pond5 Data Into Its AI](https://decrypt.co/373682/leaks-reveal-suno-fed-thousands-hours-deezer-youtube-pond5-data-ai) — independent corroboration naming Shai-Hulud as the claimed vector; quotes Suno's "limited"/"quickly contained" characterization.

## Sources
- [Microsoft Security Blog — Shai-Hulud 2.0: Guidance for detecting, investigating, and defending](https://www.microsoft.com/en-us/security/blog/2025/12/09/shai-hulud-2-0-guidance-for-detecting-investigating-and-defending-against-the-supply-chain-attack/)
- [Wiz — Sha1-Hulud 2.0 Supply Chain Attack: 25K+ Repos Exposed](https://www.wiz.io/blog/shai-hulud-2-0-ongoing-supply-chain-attack)
- [Aikido — Shai Hulud 2.0 Strikes Again: Zapier & ENS Domains](https://www.aikido.dev/blog/shai-hulud-strikes-again-hitting-zapier-ensdomains)
- [Palo Alto Unit 42 — Shai-Hulud Worm Compromises npm Ecosystem (Updated Nov 26)](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/)
- [Socradar — Shai Hulud's "The Second Coming"](https://socradar.io/blog/shai-hulud-the-second-coming-npm-campaign/)
- [Netskope — Shai-Hulud 2.0: Aggressive, Automated, and Fast Spreading](https://www.netskope.com/blog/shai-hulud-2-0-aggressive-automated-one-of-fastest-spreading-npm-supply-chain-attacks-ever-observed)
