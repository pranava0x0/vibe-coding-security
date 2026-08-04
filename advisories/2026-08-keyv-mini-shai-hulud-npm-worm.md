---
id: 2026-08-keyv-mini-shai-hulud-npm-worm
title: "keyv / cacheable npm worm — Shai-Hulud-lineage credential stealer plants Claude Code + VS Code auto-run hooks (Aug 2026, active)"
date_disclosed: 2026-08-04
last_updated: 2026-08-04
severity: critical
status: active
ecosystems: [npm, claude-code, vscode]
tools_affected: [keyv, cacheable, cache-manager, flat-cache, file-entry-cache, cacheable-request, "@cacheable/*", claude-code, vscode]
tags: [supply-chain, credential-theft, worm, shai-hulud, ai-agent-config-poisoning, provenance-abuse, ethereum-c2, github-actions]
---

## TL;DR
An attacker compromised the GitHub maintainer account behind **keyv** and its sibling `@cacheable`-family caching packages (a combined dependency tree with hundreds of millions of downloads) and published poisoned releases carrying a **Shai-Hulud-lineage credential-stealing worm** — the same release also planted `.claude/settings.json` and `.vscode/tasks.json` auto-run hooks in affected repos. It's still unfolding as of this writing: package/version counts are climbing hour to hour, no fixed version has been announced, and researchers disagree on exact scope.

## What happened
Starting around **2026-08-03 15:00 UTC**, Wiz observed C2-resolution traffic to public Ethereum RPC nodes tied to this campaign; at **2026-08-04 ~09:00 UTC**, the attacker used a compromised GitHub maintainer account to push malicious commits directly to the `keyv` repository's default branch and cut a new release, `keyv@6.0.0` ([Aikido](https://www.aikido.dev/blog/keyv-and-friends-compromised-in-npm-supply-chain-attack); [Wiz](https://www.wiz.io/blog/keyv-and-cacheable-npm-supply-chain-attack)). The same maintainer account owns a cluster of related caching packages — `cache-manager`, `cacheable-request`, `flat-cache`, `file-entry-cache`, `cacheable`, `@cacheable/memory`, `@cacheable/node-cache`, `@cacheable/utils`, `@cacheable/net` — all of which received poisoned releases in the same window.

**Two distinct payload mechanisms shipped together:**

1. **npm install-time credential stealer.** The poisoned `package.json` adds `"preinstall": "node setup.mjs"`. `setup.mjs` is an obfuscated dropper that checks for the Bun JavaScript runtime, downloads Bun 1.3.13 if absent, and hands off to a ~728 KB compiled bundle (`Math_Symbol.js` / `math_init.js`) that harvests npm tokens (`~/.npmrc`, validated against the registry before exfiltration), GitHub tokens (classic PATs, OAuth, GitHub App, JWT/OIDC — including reading GitHub Actions runner memory), AWS credentials (config files, env vars, EC2/ECS instance-metadata, cross-region Secrets Manager enumeration), Kubernetes service-account tokens, HashiCorp Vault tokens, Stripe/Slack tokens, and roughly 200 glob patterns covering `.env` files, SSH keys, Terraform state, Docker configs, IDE settings, and VPN configs. Files over 5 MB are skipped; the harvester runs up to 64 concurrent reads.
2. **AI-agent config auto-run hooks (planted in affected repos, not the npm registry).** The same compromised-maintainer commit added `.claude/settings.json` with a `SessionStart` hook invoking `.vscode/setup.mjs`, and `.vscode/tasks.json` with an `"Environment Setup"` task set to `runOn: folderOpen` invoking `.claude/setup.mjs` — a cross-triggering pair, so opening the repo in either Claude Code or VS Code can fire the other tool's copy of the payload ([The Hacker News](https://thehackernews.com/2026/08/keyv-linked-npm-worm-poisons-hundreds.html)). This is the same "AI coding tool auto-executes workspace config on open" root cause this repo already tracks for Claude Code, Cursor, Windsurf, and Amazon Q — VS Code and Claude Code both gate automatic tasks/hooks behind workspace-trust by default, so a trusted-workspace click is still required, but any repo a developer has already trusted (a fork, a clone of a popular package) is exposed the moment it's reopened.

**Scale is still moving and sources disagree.** SafeDep verified 353 poisoned versions across 79 package names at time of reporting (via The Hacker News); Aikido's later count put it at "at least 868 packages across 1,381 versions"; OX Security reported "+440 packages"; combined download-volume estimates across all cited sources exceed **2 billion monthly installs**. Weekly/monthly download figures for `keyv` itself also vary by source (127M weekly per one report vs. 604M monthly per another) — stated here as reported rather than picked, per this repo's accuracy bar; treat both as rough orders of magnitude, not precise counts, while the incident is still active.

**Exfiltration and C2.** Stolen credentials are encrypted (readable only with the attacker's RSA private key) and uploaded to newly created public GitHub repositories whose description contains the string `"Shai-Hulud: Here We Go Again"` — Wiz counted 546 such repos created on 2026-08-04 alone; other sources report figures approaching 1,300. A fallback C2 channel resolves through the domain `npm-cache[.]com` (registered 2026-05-22, currently resolving via Cloudflare), with `pypi-get[.]com` and `js-mirror[.]com` also observed. Wiz additionally documented the malware querying **public Ethereum RPC endpoints** (`eth-mainnet.nodereal[.]io`, `go.getblock[.]io`, `eth.llamarpc[.]com`) to resolve C2 configuration from an on-chain smart contract, funded from a wallet address previously flagged for scam activity — the same blockchain-dead-drop resilience pattern this repo already tracks for Solana-memo and Ethereum-based C2 in other 2026 campaigns.

**Provenance abuse.** The poisoned releases carried **valid OIDC and SLSA provenance**, published through the legitimate GitHub Actions release pipeline, and the commit that planted the `.claude`/`.vscode` hooks carried a green GitHub-verified badge with `github-actions[bot]` as the listed author. As this repo has noted before: a verified-provenance badge proves *who ran the pipeline*, not that the artifact is safe — here it proves the *attacker's* pipeline ran, using the maintainer's stolen credentials.

**Attribution.** Researchers describe the malware as a descendant of the "Mini" Shai-Hulud family with code/infrastructure similarities to the TeamPCP and `antv` (self-minted Sigstore attestation) campaigns already tracked in this repo, and note the same IDE-hook mechanism appeared in an April 2026 PyPI (`lightning`) compromise. No named actor or initial-access vector for the maintainer account itself has been confirmed as of this writing.

**No official patched version has been published by the maintainers, npm, or GitHub as of this writing.** `latest` tags on affected packages may still resolve to a malicious version — pin to a known-good version predating this incident rather than trusting `latest`.

## Am I affected?
```bash
# Check installed versions against the packages named in this incident
npm ls keyv cache-manager cacheable-request flat-cache file-entry-cache cacheable \
  @cacheable/memory @cacheable/node-cache @cacheable/utils @cacheable/net 2>/dev/null

# keyv@6.0.0 and cache-manager@7.2.10 / cacheable-request@13.0.20 / @cacheable/utils@2.5.1
# are confirmed-malicious releases per Wiz's published IOC list:
# https://github.com/wiz-sec-public/wiz-research-iocs/blob/main/reports/keyv-packages.csv

# Look for the dropper and payload files this campaign plants
find . -path '*/node_modules/*' \( -name 'setup.mjs' -o -name 'Math_Symbol.js' -o -name 'math_init.js' \) 2>/dev/null

# Check for the planted AI-agent auto-run hooks in YOUR OWN repos (not node_modules) —
# this is the part that persists even after you remove the bad package
grep -l "SessionStart" .claude/settings.json 2>/dev/null
grep -l "folderOpen" .vscode/tasks.json 2>/dev/null

# Look for the exfil GitHub-repo marker if you suspect you were a source of stolen creds
# (search github.com for repos you don't recognize with this description string)
# "Shai-Hulud: Here We Go Again"
```
If any of the above match, treat every credential the affected machine or CI runner had access to as compromised — npm tokens, GitHub tokens/PATs, AWS/GCP/Azure credentials, Kubernetes service-account tokens, Vault tokens, Stripe/Slack tokens, SSH keys, and any `.env` secrets.

## If you are affected
1. Remove the affected package versions immediately; do not simply re-run `npm install` against `latest` until a confirmed-clean version is announced — pin to a version predating 2026-08-04.
2. Treat any machine or CI runner that installed an affected version as fully compromised; rebuild rather than clean in place.
3. Delete the planted `.claude/settings.json` `SessionStart` hook and `.vscode/tasks.json` `folderOpen` task if found, and diff them against your last known-good commit before trusting the workspace again.
4. Rotate every credential class listed above, in priority order (npm and GitHub tokens first, since those enable further propagation).

→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — pin exact versions, avoid `latest`/floating ranges, use lockfiles with integrity hashes.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
- Diff `.claude/`, `.vscode/tasks.json`, `AGENTS.md`, and other agent-config files on every dependency-tree change, the same way you'd review a `package.json` diff — this campaign proves the two are now the same threat surface.
- A green "provenance verified" badge on an npm release confirms the publishing pipeline ran, not that the artifact is safe; it does not substitute for pinning known-good versions.
- npm ≥ 12 blocks unapproved dependency lifecycle scripts by default (`allowScripts: off`) — upgrade if you haven't; earlier npm clients remain exposed to the `preinstall` vector used here.

## Sources
- [Aikido Security — Keyv and friends compromised in npm supply chain attack](https://www.aikido.dev/blog/keyv-and-friends-compromised-in-npm-supply-chain-attack) — primary technical writeup: payload structure, credential targets, exfil GitHub-repo marker, IOC hashes.
- [The Hacker News — Keyv-Linked npm Worm Poisons Hundreds of Packages, Plants Claude Code and VS Code Hooks](https://thehackernews.com/2026/08/keyv-linked-npm-worm-poisons-hundreds.html) — SafeDep-sourced version/package counts, `.claude`/`.vscode` hook mechanism and workspace-trust caveat, provenance-abuse detail.
- [Wiz — keyv and cacheable npm Package Hijacked in Supply Chain Attack](https://www.wiz.io/blog/keyv-and-cacheable-npm-supply-chain-attack) — timeline, Ethereum RPC C2 resolution, C2 domain IOCs, campaign attribution/lineage, IOC hash list (github.com/wiz-sec-public/wiz-research-iocs).
