---
id: 2026-03-axios-compromise
title: "Axios npm package compromise (March 2026)"
date_disclosed: 2026-03-31
last_updated: 2026-05-16
severity: critical
status: contained
ecosystems: [npm]
tools_affected: [any-node-project, any-frontend-with-http-client]
tags: [supply-chain, rat, c2, npm, auto-update]
---

## TL;DR
On 2026-03-31, two malicious versions of `axios` (70M+ weekly downloads) were published. They connected to a C2 owned by the Sapphire Sleet threat actor to pull a remote access trojan. Because Axios is commonly auto-updated, projects with permissive version ranges fetched the malware on the next install or CI run.

## What happened
Two malicious Axios versions were published, contacting `sapphire-sleet`-attributed infrastructure on install. The C2 served a second-stage RAT giving the attacker persistent access to dev machines and CI runners.

Detected within hours and removed, but the auto-update vector means thousands of `^x.y.z` and `~x.y.z` ranges resolved to the malicious versions during the window.

## Am I affected?

```bash
# Show all axios versions in your tree
npm ls axios --all

# Check lockfile for the bad versions (cross-reference with the Microsoft / Trend Micro advisories below)
grep -A2 '"axios"' package-lock.json
```

If your `package.json` uses `"axios": "^1.x.x"` and you installed between 2026-03-31 and the takedown, your lockfile will have pinned the malicious version's hash.

```bash
# Check for outbound connections to known Sapphire Sleet C2 (consult Microsoft Security Blog for current IOCs)
# Generic: look at dev-machine network logs for unexpected outbound from node processes around the install date
```

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — pin exact versions, use `npm ci` not `npm install` in CI

## Sources
- [Microsoft Security Blog — Mitigating the Axios npm supply chain compromise](https://www.microsoft.com/en-us/security/blog/2026/04/01/mitigating-the-axios-npm-supply-chain-compromise/)
- [Trend Micro — Axios NPM Package Compromised](https://www.trendmicro.com/en_us/research/26/c/axios-npm-package-compromised.html)
- [Sophos — Axios npm package compromised to deploy malware](https://www.sophos.com/en-us/blog/axios-npm-package-compromised-to-deploy-malware)
