---
id: 2025-09-shai-hulud-original
title: "Shai-Hulud npm worm — original wave (September 2025)"
date_disclosed: 2025-09-15
last_updated: 2026-05-16
severity: critical
status: contained
ecosystems: [npm]
tools_affected: [any-node-project, cursor, claude-code]
tags: [supply-chain, worm, credential-theft, npm, github]
---

## TL;DR
On 2025-09-15, the first self-replicating npm worm — Shai-Hulud — was discovered. ~200 packages compromised, including `@ctrl/tinycolor` (2.2M weekly), `ngx-bootstrap` (300k weekly), and several CrowdStrike-owned packages. The worm stole GitHub/npm/AWS/GCP credentials, then re-published itself into every other package owned by each compromised maintainer.

## What happened
The worm's flow:

1. **Execute via postinstall.** Each compromised package had a `postinstall` hook that ran `bundle.js`.
2. **Steal credentials.** Scan filesystem for GitHub tokens, `~/.npmrc`, AWS/GCP creds.
3. **Leak via private repos → public.** Flip the maintainer's private repos to public, exposing source + any committed secrets.
4. **Publish to a `Shai-Hulud` GitHub repo.** Stolen creds uploaded as base64 JSON.
5. **Replicate.** Use stolen npm tokens to enumerate every other package the maintainer owns; publish new versions of each with the worm injected.

This was the first time the npm community saw worm-style self-propagation. Named after the Dune sandworms.

## Am I affected?

```bash
# Check the canonical first-infection package
npm ls @ctrl/tinycolor --all
npm ls ngx-bootstrap --all
npm ls ng2-file-upload --all
```

Full IOC lists are maintained by the sources below — cross-reference your lockfile against them.

```bash
# Was a "Shai-Hulud" repo planted on your GitHub?
gh api /user/repos --paginate --jq '.[] | select(.name | test("Shai-Hulud"; "i")) | .full_name'
```

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources
- [Sysdig — Shai-Hulud: The novel self-replicating worm](https://www.sysdig.com/blog/shai-hulud-the-novel-self-replicating-worm-infecting-hundreds-of-npm-packages)
- [Checkmarx — Inside Shai-Hulud's Maw](https://checkmarx.com/zero-post/inside-shai-huluds-maw-how-the-npm-worm-exploits-and-propagates/)
- [ReversingLabs — Shai-Hulud npm supply chain attack](https://www.reversinglabs.com/blog/shai-hulud-worm-npm)
- [CISA Alert — Widespread Supply Chain Compromise Impacting npm Ecosystem](https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem)
- [Xygeni — Shai-Hulud: The npm Packages Worm Explained](https://xygeni.io/blog/shai-hulud-the-npm-packages-worm-explained/)
