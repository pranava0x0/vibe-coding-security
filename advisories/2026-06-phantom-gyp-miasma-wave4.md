---
id: 2026-06-phantom-gyp-miasma-wave4
title: "Phantom Gyp — Miasma wave 4: self-propagating npm worm via binding.gyp (June 2026)"
date_disclosed: 2026-06-04
last_updated: 2026-06-07
severity: critical
status: active
ecosystems: [npm]
tools_affected: [any project that npm-installs a node-gyp-dependent package; notably @vapi-ai/server-sdk (408K+ monthly downloads)]
tags: [supply-chain, worm, credential-theft, self-propagating, miasma-lineage, provenance-forgery]
---

## TL;DR

A fourth wave of the Miasma / Shai-Hulud worm lineage hit npm on **June 3–4, 2026**, using **`binding.gyp`** instead of `preinstall`/`postinstall` scripts to run malicious code at install time — a technique StepSecurity named **"Phantom Gyp."** Snyk tracks it as *Node-gyp Supply Chain Compromise June 2026*; **57 packages / 286+ malicious versions** (including **`@vapi-ai/server-sdk` with 408K+ monthly downloads** as the highest-profile victim) were published. Same credential-theft and self-propagation core as prior waves, with a novel install-time primitive **plus forged SLSA v1 provenance attestations** on repackaged malicious versions — green "verified provenance" badges are not safety.

## What happened

On **2026-06-03** (and continuing through June 4), a threat actor published 57 malicious npm packages that use native-addon build plumbing (**`binding.gyp`** + node-gyp) to execute a malicious payload at `npm install` time. Unlike `preinstall`/`postinstall` lifecycle hooks — which many npm audit tools flag by default — `binding.gyp` triggers code execution via the native build step and is not blocked by `--ignore-scripts` unless native addons are also disabled.

**What the payload does:**
- Steals credentials (cloud keys, GitHub tokens, `.env` files, SSH keys)
- Injects malicious GitHub Actions workflows (same `.github/workflows/*.yml` shape as [Megalodon](2026-05-megalodon-github-actions-mass-campaign.md))
- Exfiltrates stolen credentials to attacker C2
- Self-propagates by publishing additional poisoned npm packages using stolen npm tokens (worm behavior)

**Largest victim: `@vapi-ai/server-sdk`** — the official Vapi.ai voice AI server SDK with **408,000+ monthly downloads** was among the first packages hit, at 23:30 UTC on June 3, 2026. The campaign infected **57 packages across 286+ malicious versions** in a rolling wave lasting under two hours. A notable escalation: the worm **forges SLSA v1 provenance attestations** on repackaged malicious versions — reinfected packages display a green "verified provenance" badge and pass standard provenance verification, yet carry the malicious payload (same forgery primitive as the May 19 Mini Shai-Hulud wave that self-minted Sigstore attestations).

**June 5 follow-on (Wave 5):** On 2026-06-05, credentials stolen during this binding.gyp wave were used to compromise a Microsoft contributor's GitHub account, planting malicious commits in **73 Microsoft GitHub repositories** (Azure, Azure-Samples, Microsoft, MicrosoftDocs) and **5 mantine-datatable repos** — without touching the npm registry. See [2026-06-miasma-wave5-microsoft-azure-github.md](2026-06-miasma-wave5-microsoft-azure-github.md) for full details.

**Attribution / lineage:** The underlying payload and IOCs are consistent with the Miasma / Mini Shai-Hulud worm family (Greek-mythology theming). This is the **fourth documented copycat wave** after:
1. [`deadcode09284814` typosquats](2026-05-shai-hulud-copycat-wave.md) (May 2026)
2. [TrapDoor cross-ecosystem](2026-05-trapdoor-cross-ecosystem-stealer.md) (May 2026)
3. [Miasma — @redhat-cloud-services](2026-06-miasma-redhat-cloud-services-compromise.md) (June 1, 2026)

**New primitive: binding.gyp execution.** `binding.gyp` defines how node-gyp builds a native C/C++ addon. When any `binding.gyp` exists in a package, `npm install` runs `node-gyp build` as part of the standard build step — it is not a lifecycle script and is not suppressed by `npm install --ignore-scripts`. The malicious packages include fake `binding.gyp` files that trigger `node-gyp build`, which executes attacker-controlled JavaScript via the configure/build flow. This is the first documented use of this technique at scale in a supply-chain worm campaign.

## Am I affected?

```bash
# Check for suspicious packages installed since June 3, 2026
# Look for packages with binding.gyp that are not well-known native addons
find node_modules -name "binding.gyp" | while read f; do
  pkg=$(echo "$f" | cut -d/ -f1-3)
  echo "$pkg"
done

# Check install timestamps in npm cache
npm cache ls 2>/dev/null | grep -E "2026-06-0[34]"

# Snyk scan (updates signatures frequently)
npx snyk test
```

If you ran `npm install` on any project between **2026-06-03 00:00 UTC** and **2026-06-05** and any transitive dependency pulled in an unfamiliar native-addon package, treat the machine as potentially compromised.

## If you are affected

1. **Rotate all credentials** accessible from the affected machine: cloud API keys, GitHub/npm/PyPI tokens, SSH keys.
2. **Audit GitHub Actions workflows** added after 2026-06-02: `git log --all --oneline -- .github/workflows/`
3. **Check for new npm packages published** from your account: `npm search --json maintainer:<your-username> | jq '.[].date'`
4. See [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md).

## Prevention

- **Disable binding.gyp execution** for packages that don't need native addons: use `--ignore-scripts` AND audit any package that legitimately requires native build.
- **Pin npm packages to exact versions + lockfile integrity** (`npm ci` over `npm install` in CI).
- **Block unexpected workflow file creation** via branch-protection rules requiring code review on `.github/workflows/` changes.
- **Monitor npm publish activity** for your account/org with StepSecurity's npm package monitoring.

## Sources

- [Snyk — "Node-gyp Supply Chain Compromise June 2026"](https://snyk.io/blog/node-gyp-supply-chain-compromise-self-propagating-npm-worm-binding-gyp/) — canonical analysis, 57-package scope, "Phantom Gyp" technique detail, payload behavior.
- [StepSecurity — "Phantom Gyp" campaign tracking](https://www.stepsecurity.io) — technique naming, IOC list, timeline.
- [The Hacker News — Miasma Supply Chain](https://thehackernews.com/2026/06/miasma-supply-chain-attack-compromises.html) — family lineage context.
- Cross-reference: [2026-06-miasma-wave5-microsoft-azure-github.md](2026-06-miasma-wave5-microsoft-azure-github.md) — Wave 5 that used credentials stolen in this wave to hit 73 Microsoft GitHub repos via direct source-repo poisoning.
- Cross-reference: [2026-06-miasma-redhat-cloud-services-compromise.md](2026-06-miasma-redhat-cloud-services-compromise.md), [2026-05-shai-hulud-copycat-wave.md](2026-05-shai-hulud-copycat-wave.md), [2026-05-trapdoor-cross-ecosystem-stealer.md](2026-05-trapdoor-cross-ecosystem-stealer.md).
