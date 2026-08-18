---
id: 2026-03-axios-compromise
title: "Axios npm package compromise (March 2026)"
date_disclosed: 2026-03-31
last_updated: 2026-08-18
severity: critical
status: contained
ecosystems: [npm]
tools_affected: [any-node-project, any-frontend-with-http-client, usebruno-cli]
tags: [supply-chain, rat, c2, npm, auto-update, cve]
---

## TL;DR
On 2026-03-31, two malicious versions of `axios` (70M+ weekly downloads) were published. They connected to a C2 owned by the Sapphire Sleet threat actor to pull a remote access trojan. Because Axios is commonly auto-updated, projects with permissive version ranges fetched the malware on the next install or CI run. Now tracked as **CVE-2026-34841 (CVSS 9.8)** via the downstream advisory on **`@usebruno/cli`**, which transitively pulled the bad axios.

## What happened
The two malicious Axios versions were **`1.14.1` and `0.30.4`**. They injected a hidden dependency, **`plain-crypto-js@4.2.1`** — a package never imported anywhere in the axios source. Its only job was a **`postinstall` script acting as a cross-platform RAT dropper** (macOS, Windows, Linux), contacting `sapphire-sleet`-attributed infrastructure on install and pulling a second-stage RAT for persistent access to dev machines and CI runners.

Detected within hours and removed, but the auto-update vector means thousands of `^x.y.z` and `~x.y.z` ranges resolved to the malicious versions during the window.

**Downstream blast radius — `@usebruno/cli` (CVE-2026-34841):** Bruno (the API client/IDE) shipped a CLI that pulled the compromised axios transitively. Anyone who ran `npm install` of `@usebruno/cli` between **~00:21 and ~03:30 UTC on 2026-03-31** may have resolved the malicious axios and executed the RAT dropper. Bruno pinned axios to a safe version; `@usebruno/cli` **< 3.2.1 is affected — upgrade to ≥ 3.2.1.** This is a textbook reminder that the worry isn't only the famous package — it's everything that depends on it.

## Am I affected?

```bash
# Show all axios versions in your tree
npm ls axios --all

# Check lockfile for the bad versions (1.14.1 / 0.30.4) and the tell-tale dropper dep
grep -A2 '"axios"' package-lock.json
grep -nE '"(axios)":\s*"(1\.14\.1|0\.30\.4)"|plain-crypto-js' package-lock.json

# Bruno CLI users: confirm you're on a fixed release
npm ls @usebruno/cli 2>/dev/null
```

If your `package.json` uses `"axios": "^1.x.x"` and you installed between 2026-03-31 and the takedown, your lockfile will have pinned the malicious version's hash. The clearest single IOC is the presence of **`plain-crypto-js@4.2.1`** anywhere in your tree — it has no legitimate use.

```bash
# Check for outbound connections to known Sapphire Sleet C2 (consult Microsoft Security Blog for current IOCs)
# Generic: look at dev-machine network logs for unexpected outbound from node processes around the install date
```

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — pin exact versions, use `npm ci` not `npm install` in CI

## Update — 2026-08-18: same actor now formally tied to the September 2025 qix (chalk/debug) compromise and a March 2025 typo-crypto incident

Amazon Threat Intelligence's 2026-07-29 report confirms this compromise and the [September 2025 qix/chalk/debug compromise](../advisories/2025-09-qix-compromise.md) were carried out by the same DPRK-linked actor (tracked as SAPPHIRE SLEET / STARDUST CHOLLIMA / BlueNoroff / CageyChameleon / Alluring Pisces), along with a previously-unlinked March 2025 `typo-crypto` package compromise — four npm supply-chain incidents across 13 months from one operator using a consistent playbook (socially engineer a trusted maintainer, publish a trojanized `postinstall`-hook update, reuse code across payloads). See the qix-compromise advisory for full attribution detail.

## Sources
- [AWS Security Blog — Amazon identifies North Korean hacker group behind open-source supply chain attacks](https://aws.amazon.com/blogs/security/amazon-identifies-north-korean-hacker-group-behind-open-source-supply-chain-attacks/) — cross-campaign attribution linking this incident to qix/chalk/debug and typo-crypto.
- [Microsoft Security Blog — Mitigating the Axios npm supply chain compromise](https://www.microsoft.com/en-us/security/blog/2026/04/01/mitigating-the-axios-npm-supply-chain-compromise/)
- [Trend Micro — Axios NPM Package Compromised](https://www.trendmicro.com/en_us/research/26/c/axios-npm-package-compromised.html)
- [Sophos — Axios npm package compromised to deploy malware](https://www.sophos.com/en-us/blog/axios-npm-package-compromised-to-deploy-malware)
- [GitHub Advisory Database — GHSA-658g-p7jg-wx5g / CVE-2026-34841: Axios npm Supply Chain Incident Impacting @usebruno/cli](https://github.com/advisories/GHSA-658g-p7jg-wx5g) — versions, time window, fixed `@usebruno/cli` 3.2.1.
- [GitLab Advisory Database — CVE-2026-34841 (@usebruno/cli)](https://advisories.gitlab.com/pkg/npm/@usebruno/cli/CVE-2026-34841/)
- [NVD — CVE-2026-34841](https://nvd.nist.gov/vuln/detail/CVE-2026-34841)
- [StepSecurity — axios Compromised on npm: Malicious Versions Drop Remote Access Trojan](https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan) — `plain-crypto-js@4.2.1` dropper IOC.
- [Miggo — CVE-2026-34841: Bruno CLI Supply Chain RAT](https://www.miggo.io/vulnerability-database/cve/CVE-2026-34841)
