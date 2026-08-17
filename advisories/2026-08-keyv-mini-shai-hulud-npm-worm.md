---
id: 2026-08-keyv-mini-shai-hulud-npm-worm
title: "keyv / cacheable npm worm ('ChainDrop') — Shai-Hulud-lineage credential stealer plants Claude Code + VS Code auto-run hooks (Aug 2026)"
date_disclosed: 2026-08-04
last_updated: 2026-08-17
severity: critical
status: active
ecosystems: [npm, claude-code, vscode]
tools_affected: [keyv, cacheable, cache-manager, flat-cache, file-entry-cache, cacheable-request, "@cacheable/*", claude-code, vscode]
tags: [supply-chain, credential-theft, worm, shai-hulud, chaindrop, ai-agent-config-poisoning, provenance-abuse, ethereum-c2, github-actions]
---

## TL;DR
An attacker compromised the GitHub maintainer account behind **keyv** and its sibling `@cacheable`-family caching packages (a combined dependency tree with hundreds of millions of downloads) and published poisoned releases carrying a **Shai-Hulud-lineage credential-stealing worm** — the same release also planted `.claude/settings.json` and `.vscode/tasks.json` auto-run hooks in affected repos. **Microsoft's own Security Blog has since named the campaign "ChainDrop"** and confirmed it spread to **400+ packages across multiple, unrelated publisher accounts** — not just the original keyv/cacheable maintainer — via stolen npm tokens propagating the worm publisher-to-publisher. Package/version counts climbed for the first ~48 hours before stabilizing; as of this update, still no single official "fixed" release exists — pin to a version predating 2026-08-04 rather than trusting `latest`.

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

**Update (2026-08-06) — "ChainDrop," and confirmation the worm spread beyond the original maintainer account.** Microsoft's Security Blog published its own technical analysis on 2026-08-04, naming the campaign **ChainDrop** and confirming it as a **self-propagating worm**: "one stolen [npm] token can produce malicious patch releases across every package available to that publisher," and Microsoft's own count puts the confirmed scope at **more than 400 packages compromised across multiple unrelated publisher accounts** — i.e., the worm didn't stay contained to the keyv/`@cacheable` maintainer's own packages, it used stolen tokens harvested from early victims to poison further, unrelated publishers' packages in turn. Microsoft's writeup adds two technical details not in the original reporting: the credential-harvesting payload encrypts stolen data with **AES-256-GCM** before exfiltration, and Microsoft's recommended mitigation is to **update to npm CLI v12** (which defaults to blocking unapproved lifecycle scripts) and to **enable the `min-release-age` setting** so a freshly-published version of any dependency isn't installed until it's had time to be flagged. Combined download-volume estimates across all cited sources (Aikido, Wiz, Microsoft) remain in the **~2 billion monthly installs** range for the affected package set as a whole.

**Update (2026-08-08) — maintainer account named, government advisory issued, lineage confirmed to April 2026 PyPI compromise.** Multiple independent writeups (Chainguard, corroborated by SC Media) now publicly name the compromised account as belonging to **Jared Wray (`jaredwray`)**, maintainer of record for the keyv/cacheable package family. Chainguard's technical analysis traces the identical `setup.mjs` filename, Bun 1.3.13 staging path, and hook-file structure directly back to the **April 2026 PyTorch Lightning PyPI compromise** and the **May 2026 `@antv` npm wave** (both already tracked in this repo), confirming this is the third documented wave of the same toolkit lineage rather than an independently-developed payload. Singapore's **Cyber Security Agency (CSA)** issued a public advisory on the campaign (AD-2026-009) — the first government-body advisory this repo has tracked for a keyv/cacheable-lineage incident. No official "clean" release has still been announced as of this update; continue pinning to a pre-2026-08-04 version.

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

## Update — 2026-08-15: two propagation details not in the original disclosure — tarball rebuilding (invisible in source review) and GitHub-API commit propagation (no `npm install` required)

The Register's follow-up analysis identifies two distinct propagation mechanisms beyond the preinstall-hook vector already described above: (1) **tarball rebuilding** — when the worm locates an npm token with write access, it downloads the *published tarball* for accessible packages and rebuilds it to include the payload directly, bypassing the source repository entirely, so **reviewing the GitHub source repo shows no evidence of compromise** since the malicious code exists only in the published artifact; (2) **GitHub-API commit propagation** — using stolen GitHub credentials, the worm commits the `.claude/settings.json` / `.vscode/tasks.json` hook files (described above) **directly into repository branches via the GitHub API**, across every repo the stolen token can reach. Combined with the auto-run hooks, this means a developer can be infected simply by **opening an infected branch in VS Code or Claude Code — no `npm install` ever runs**. ActiveState CEO Abby Kearns characterized this as "the first campaign to notice the gap" between what dependency-scanning tools check (published packages) and what actually executes (repo-committed AI-tool config), and recommended treating repository-supplied configuration as executable content subject to the same scrutiny as a `package.json` diff. Package count as of this update: 444 (up from earlier counts), ~2 billion combined monthly downloads across affected dependencies.

**Am I affected (update):** tarball rebuilding means you cannot rule out compromise by reviewing a package's GitHub source alone — check the actual installed tarball contents, not just the repo. GitHub-API commit propagation means any repository you have open-and-trusted in VS Code or Claude Code should be checked for unexpected `.claude/settings.json` or `.vscode/tasks.json` changes even if you never ran `npm install` in it.

## Update — 2026-08-09 (backfilled this sweep): first observed Shai-Hulud-lineage payload delivered through the official MCP Registry

OX Security reports a distinct new distribution vector for the same worm lineage tracked in this advisory: a clean-looking PyPI-linked **MCP server named "V.A.P.E"** (marketed as cryptocurrency-chain security tooling) was listed on the **official Model Context Protocol Registry** (`registry.modelcontextprotocol.io`) — the first documented case of a Shai-Hulud-lineage payload reaching victims through the official MCP Registry rather than npm/PyPI directly. The linked PyPI package itself stays clean to evade automated scanners; the malicious payload lives in the associated GitHub repository (`jUXTAPOSITION1/V.A.P.E`), embedded in `.vscode/settings.json` / `.claude/settings.json` — the same auto-run-hook mechanism described above. **Opening or cloning the repository in Claude Code or VS Code triggers the malware**, harvesting developer tokens, cloud credentials, and session keys to further propagate the worm. OX Security identified five actively-distributing repositories at time of writing: `techtoboggan/claude-desktop-hardened-linux`, `rainb0w-clwn/node-cache-manager-fs-binary-ts`, `diegobbarbosa09/Automacao_swaglabs_cypress`, `evilgodfahim/kal`, and `jUXTAPOSITION1/V.A.P.E` itself — several using names that mimic legitimate `cache-manager`/Claude-tooling projects, extending this campaign's targeting of AI-coding-tool users beyond package names into repository and MCP-listing names.

**Am I affected (update):** if you use the official MCP Registry to discover MCP servers, do not assume a registry listing implies safety — check any MCP server's *linked repository* (not just its package) for `.vscode/settings.json` / `.claude/settings.json` before opening it in an editor, and cross-reference the five repository names above directly.

## Sources
- [OX Security — Shai-Hulud Outbreak Debrief: The Worm Evolves into MCP](https://www.ox.security/blog/shai-hulud-outbreak-debrief-the-worm-evolves-into-mcp/) — primary source for the 2026-08-09 update: V.A.P.E MCP Registry listing, five named repositories, trigger mechanism.
- [Aikido Security — Keyv and friends compromised in npm supply chain attack](https://www.aikido.dev/blog/keyv-and-friends-compromised-in-npm-supply-chain-attack) — primary technical writeup: payload structure, credential targets, exfil GitHub-repo marker, IOC hashes.
- [The Hacker News — Keyv-Linked npm Worm Poisons Hundreds of Packages, Plants Claude Code and VS Code Hooks](https://thehackernews.com/2026/08/keyv-linked-npm-worm-poisons-hundreds.html) — SafeDep-sourced version/package counts, `.claude`/`.vscode` hook mechanism and workspace-trust caveat, provenance-abuse detail.
- [Wiz — keyv and cacheable npm Package Hijacked in Supply Chain Attack](https://www.wiz.io/blog/keyv-and-cacheable-npm-supply-chain-attack) — timeline, Ethereum RPC C2 resolution, C2 domain IOCs, campaign attribution/lineage, IOC hash list (github.com/wiz-sec-public/wiz-research-iocs).
- [Microsoft Security Blog — ChainDrop supply chain compromise: Anatomy of a self-propagating worm](https://www.microsoft.com/en-us/security/blog/2026/08/04/chaindrop-supply-chain-compromise-anatomy-self-propagating-worm/) — vendor naming ("ChainDrop"), 400+ packages across multiple unrelated publishers, AES-256-GCM exfil detail, npm v12 / `min-release-age` mitigation guidance.
- [Chainguard — The keyv and cacheable npm Supply Chain Attack: Inside the Mini Shai-Hulud Campaign](https://www.chainguard.dev/unchained/the-keyv-and-cacheable-npm-supply-chain-attack-inside-the-mini-shai-hulud-campaign) — names the compromised maintainer account, traces toolkit lineage to the April 2026 PyTorch Lightning and May 2026 @antv compromises.
- [Cyber Security Agency of Singapore — Ongoing npm Supply Chain Attack Affecting Keyv and Related Packages ("Shai-Hulud" Worm), AD-2026-009](https://www.csa.gov.sg/alerts-and-advisories/advisories/ad-2026-009/) — first government-body advisory tracked for this incident.
- [The Register — ChainDrop worm crawls into npm supply chain, evades standard defenses](https://www.theregister.com/security/2026/08/15/chaindrop_worm_crawls_into_npm_supply_chain_evades_standard_defenses/5287958) — added for the 2026-08-15 update: tarball-rebuilding and GitHub-API commit-propagation detail, ActiveState CEO quote, updated package count.
