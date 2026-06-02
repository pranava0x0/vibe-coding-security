---
id: 2026-05-shai-hulud-copycat-wave
title: "Shai-Hulud copycats after the worm source went public (May 2026)"
date_disclosed: 2026-05-18
last_updated: 2026-06-02
severity: high
status: active
ecosystems: [npm]
tools_affected: [any-node-project, cursor, claude-code]
tags: [supply-chain, worm, credential-theft, npm, copycat, ddos, infostealer, teampcp]
---

## TL;DR
On 2026-05-12 TeamPCP **open-sourced the fully weaponized Mini Shai-Hulud worm** to public GitHub and announced a paid "biggest supply-chain attack" **competition on BreachForums**. Within days, low-skill copycats began shipping near-verbatim clones on npm — the first being **`chalk-tempalte`**, a barely-modified copy of the leaked worm with its own C2. A single actor (`deadcode09284814`) published **four malicious packages** mixing a Shai-Hulud clone, plain infostealers, and a **Golang DDoS botnet ("Phantom Bot")**. Downloads are small so far (~2,700–3,000), but the worm is now a commodity — expect more.

> **Update 2026-06-02:** the worm is now a *named-family* commodity. Three distinct copycat waves have shipped derivatives of the open-sourced Mini Shai-Hulud worm in three weeks:
> 1. **This typosquat wave** (`deadcode09284814`, 2026-05-18) — near-verbatim clones with `*.lhr.life` C2 + DDoS botnet payload variant.
> 2. **[TrapDoor](2026-05-trapdoor-cross-ecosystem-stealer.md)** (2026-05-22) — different actor, cross-ecosystem (npm + PyPI + Crates.io), `.cursorrules` / `CLAUDE.md` poisoning as a new persistence primitive.
> 3. **[Miasma](2026-06-miasma-redhat-cloud-services-compromise.md)** (2026-06-01) — the first to land on a major *legitimate* npm scope (`@redhat-cloud-services`) rather than typosquats; Greek-mythology theming replaces Dune markers, GCP/Azure cloud-identity collectors added, and exfil is disguised as **`api.anthropic.com/v1/api`** (camouflage on a real AI-vendor host). Treat any future "worm reskin" finding as a likely fourth copycat in this lineage.

## What happened
The May 11–12 [TanStack / Mini Shai-Hulud wave](2026-05-tanstack-mini-shai-hulud.md) ended with TeamPCP publishing the worm's complete toolchain — CI cache-poisoning scripts, the OIDC-token extractor, and the credential stealer with its propagation logic — to public GitHub repos, then posting a **$1,000 contest on BreachForums** for the biggest supply-chain campaign (offering to buy "meaningful access" / a cut of ransoms on top). Commoditizing the worm is the story: the barrier to launching a Shai-Hulud-class attack dropped to "clone a repo, swap the C2 key."

Five days later (disclosed 2026-05-18), researchers found the first clones on npm, all from the user **`deadcode09284814`**, ~2,678–3,000 combined downloads:

- **`chalk-tempalte`** (typosquat of `chalk-template`) — a near-unmodified copy of the leaked Shai-Hulud source with the actor's own C2 server + private key. Exfil to **`87e0bbc636999b.lhr.life`**. Plants the worm's GitHub-repo marker string **"A Mini Sha1-Hulud has Appeared"**.
- **`@deadcode09284814/axios-util`** — straightforward infostealer; siphons SSH keys, environment variables, and cloud credentials to **`80.200.28.28:2222`**.
- **`axois-utils`** (typosquat of `axios-utils`) — delivers a Golang DDoS botnet called **Phantom Bot** (HTTP / TCP / UDP flooding). Establishes persistence on **Windows** (Startup folder) and **Linux** (scheduled task).
- **`color-style-utils`** — steals IP address, IP geolocation, and crypto-wallet data to **`edcf8b03c84634.lhr.life`**.

Note the two `*.lhr.life` C2 endpoints: that's the **localhost.run SSH-tunnel service**, used here as disposable, hard-to-block C2. OX Security and ReversingLabs both warn that the source leak means TeamPCP is no longer the only operator — this is the npm analogue of any worm whose source escapes: a long tail of copycats with varied, sometimes noisier payloads (DDoS, not just credential theft).

This wave is small in download volume but distinct from the [original Shai-Hulud](2025-09-shai-hulud-original.md), [Second Coming](2025-11-shai-hulud-second-coming.md), and the [TeamPCP Mini Shai-Hulud](2026-05-tanstack-mini-shai-hulud.md) campaigns: the threat actor is no longer a single coordinated group, and the trigger was a **deliberate source release + bounty**, not a maintainer compromise.

## Am I affected?

```bash
# Did any of the named copycat packages land in your tree?
npm ls chalk-tempalte axois-utils color-style-utils @deadcode09284814/axios-util --all 2>/dev/null

# Grep lockfiles directly (catches transitive)
grep -REn "chalk-tempalte|axois-utils|color-style-utils|deadcode09284814" \
  package-lock.json npm-shrinkwrap.json yarn.lock pnpm-lock.yaml 2>/dev/null

# Known C2 endpoints — check shell history / proxy logs / DNS
grep -REn "lhr\.life|80\.200\.28\.28:2222|87e0bbc636999b|edcf8b03c84634" . 2>/dev/null

# Worm marker: was a Shai-Hulud repo planted on your GitHub?
gh api /user/repos --paginate --jq '.[] | select(.name | test("Sha1?-Hulud"; "i")) | .full_name' 2>/dev/null
```

If any hit, assume credential theft: rotate everything reachable from the affected machine and check for the planted GitHub repo / scheduled task / Startup-folder persistence.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — disable install scripts, pin versions, watch for typosquats
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources
- [The Register — Shai-Hulud copycat worm infects yet another npm package](https://www.theregister.com/cyber-crime/2026/05/18/shai-hulud-copycat-hits-another-npm-package/5242180) — first copycat, chalk-tempalte, BreachForums competition.
- [BleepingComputer — Leaked Shai-Hulud malware fuels new npm infostealer campaign](https://www.bleepingcomputer.com/news/security/leaked-shai-hulud-malware-fuels-new-npm-infostealer-campaign/) — package list, IOCs, download counts.
- [The Hacker News — Four Malicious npm Packages Deliver Infostealers and Phantom Bot DDoS Malware](https://thehackernews.com/2026/05/four-malicious-npm-packages-deliver.html) — Phantom Bot, persistence, actor deadcode09284814.
- [OX Security — New Actors Deploy Shai-Hulud Clones: TeamPCP Copycats Are Here](https://www.ox.security/blog/new-actors-deploy-shai-hulud-clones-teampcp-copycats-are-here/) — copycat analysis, source-leak context.
- [ReversingLabs — Shai-Hulud code drop: Open season for supply chain attacks](https://www.reversinglabs.com/blog/the-shai-hulud-code-drop) — commoditization of the worm.
- [Cybernews — Copycat hackers using Shai-Hulud to attack NPM](https://cybernews.com/security/shai-hulud-supply-chain-attack-competition/) — BreachForums competition details.
- [SecurityAffairs — Shai-Hulud worm copycats emerge after source code leak](https://securityaffairs.com/192366/malware/shai-hulud-worm-copycats-emerge-after-source-code-leak.html) — corroborating timeline.
- [Mondoo — When Worm Source Code Goes Open Source: The Shai-Hulud Clones Arrive](https://mondoo.com/blog/shai-hulud-clones-arrive-when-worm-source-code-goes-open-source) — clone analysis, detection guidance.
