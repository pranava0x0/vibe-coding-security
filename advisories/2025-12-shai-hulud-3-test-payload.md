---
id: 2025-12-shai-hulud-3-test-payload
title: "Shai-Hulud 3.0 test payload — @vietmoney/react-big-calendar@0.26.2 (Dec 2025)"
date_disclosed: 2025-12-28
last_updated: 2026-05-26
severity: high
status: contained
ecosystems: [npm]
tools_affected: [any-node-project, cursor, claude-code]
tags: [supply-chain, worm, credential-theft, npm, shai-hulud, teampcp, test-payload]
---

## TL;DR
A **third generation of the Shai-Hulud worm** ("Shai-Hulud 3.0" / Snyk's "Holiday Whisper") landed on npm on **2025-12-28** as a single low-profile package — **`@vietmoney/react-big-calendar@0.26.2`** — with much **heavier obfuscation and reliability improvements** but the same install-time credential-theft + self-propagation goals as v1/v2. Aikido characterized it as **attackers testing their payload** — and indeed, ~4 months later the same TTPs returned at scale as the [TeamPCP Mini Shai-Hulud wave](2026-05-tanstack-mini-shai-hulud.md). Low download count; remove the package, but treat this primarily as **the test bench that produced the April–May 2026 worm cluster**.

## What happened
`@vietmoney/react-big-calendar` had sat dormant on npm since **March 2021**. On **2025-12-28**, the publisher account pushed **version 0.26.2** — its first update in nearly five years — carrying a modified Shai-Hulud variant. Per Aikido and Snyk, the changes versus the [original Shai-Hulud](2025-09-shai-hulud-original.md) / [Second Coming](2025-11-shai-hulud-second-coming.md) were primarily:

- **Heavier obfuscation** of the install-time payload (string mangling, dynamic require, indirection layers) to evade static-scan engines that caught v1/v2.
- **Reliability improvements** on the credential-collection logic and the GitHub-repo creation step that exfiltrates harvested secrets to attacker-controlled public repos.
- **Unchanged core**: still relies on install-time execution (npm lifecycle hooks) to scrape env vars, cloud creds, CI/CD secrets, GitHub/npm tokens, and SSH keys, then leak to attacker-owned GitHub repos.

The package had **low downloads / no major spread** at the time of detection (Aikido: "we may have caught the attackers testing their payload"). The wider context: this Dec 2025 drop is now read as a **TeamPCP-attributable rehearsal** for the campaigns that followed — the [SAP / Mini Shai-Hulud arm](2026-04-mini-shai-hulud-sap.md), [PyTorch Lightning + intercom-client](2026-04-pytorch-lightning-compromise.md), the [Bitwarden CLI "Third Coming"](2026-04-bitwarden-cli-shai-hulud-third-coming.md), the [TanStack / Mini Shai-Hulud wave](2026-05-tanstack-mini-shai-hulud.md), the [May 19 @antv + Microsoft `durabletask` wave](2026-05-mini-shai-hulud-may19-wave.md), and finally the [source-leak copycats](2026-05-shai-hulud-copycat-wave.md) after TeamPCP open-sourced the worm on 2026-05-12.

Naming note: this variant is referred to as **"Shai-Hulud 3.0"** (Upwind, OX, Mondoo, Snyk) or **"Holiday Whisper"** (Snyk). The "3.0" label puts it in the worm-lineage:
- **v1** = [original 2025-09 worm](2025-09-shai-hulud-original.md) (~200 packages including `@ctrl/tinycolor`)
- **v2** = [Second Coming 2025-11](2025-11-shai-hulud-second-coming.md) (492 packages, 132M monthly downloads)
- **v3** = this Dec 2025 test-payload drop, then evolved into Mini Shai-Hulud at scale through Q2 2026

## Am I affected?

```bash
# Did the test package land in your tree?
npm ls @vietmoney/react-big-calendar --all 2>/dev/null

# Grep lockfiles directly (catches transitive)
grep -REn "@vietmoney/react-big-calendar" \
  package-lock.json npm-shrinkwrap.json yarn.lock pnpm-lock.yaml 2>/dev/null

# The worm marker: was a public Shai-Hulud-style exfil repo created on your GitHub account?
gh api /user/repos --paginate \
  --jq '.[] | select(.name | test("Sha[i1]-Hulud|shaihulud"; "i")) | .full_name' 2>/dev/null
```

If any hit, treat as full credential compromise: rotate everything reachable from the affected machine, delete the planted GitHub repo, and search GitHub for any other repos containing your secrets.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — disable install scripts, pin versions
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources
- [Upwind — Shai-Hulud 3.0: npm Supply Chain Worm Reappears With Enhanced Obfuscation](https://www.upwind.io/feed/shai-hulud-3-npm-supply-chain-worm) — canonical "3.0" naming, obfuscation analysis.
- [Snyk — The Holiday Whisper: Shai-Hulud 3.0](https://snyk.io/blog/shai-hulud-3-0/) — alternate name, payload behavior changes.
- [Aikido — Shai Hulud strikes again - The golden path](https://www.aikido.dev/blog/shai-hulud-strikes-again---the-golden-path) — first-detection writeup, "testing the payload" framing, single-package scope.
- [OX Security — Shai Hulud #3: New npm Malware Variant Found in the Wild](https://www.ox.security/blog/shai-hulud-3-the-attack-continues/) — variant analysis, lineage.
- [The Hacker News — Researchers Spot Modified Shai-Hulud Worm Testing Payload on npm Registry](https://thehackernews.com/2025/12/researchers-spot-modified-shai-hulud.html) — Dec 2025 initial coverage.
- [Mondoo — Shai-Hulud Strikes Back, with v3.0](https://mondoo.com/blog/shai-hulud-strikes-back-with-v3-0-the-evolution-of-a-potent-and-persistent-npm-supply-chain-worm) — evolution + persistence framing.
- [Cybernews — New Shai-Hulud 3.0 malware variant discovered](https://cybernews.com/security/shai-hulud-malware-3rd-variant-detected-supply-chain-threat/) — variant confirmation.
- [Techzine — On the heels of 2.0, Shai-Hulud 3.0 emerges as a supply chain threat](https://www.techzine.eu/news/security/137580/on-the-heels-of-2-0-shai-hulud-3-0-emerges-as-a-supply-chain-threat/) — lineage placement.
- [Phoenix Security — Beat Sha1-Hulud 3.0 Before It Ships Your Secrets](https://phoenix.security/sha1-hulud-v3-npm-supply-chain-attack/) — defender guidance.
- [CyCraft — The Return of Shai Hulud: Analyzing New Variants of npm Supply Chain Attacks](https://www.cycraft.com/en/post/npm-variant-en-20260310) — variant comparison v1/v2/v3.
