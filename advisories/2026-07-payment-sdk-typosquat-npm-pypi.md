---
id: 2026-07-payment-sdk-typosquat-npm-pypi
title: "Fake Paysafe / Skrill / Neteller payment SDKs on npm and PyPI steal credentials (July 2026)"
date_disclosed: 2026-07-07
last_updated: 2026-07-07
severity: high
status: contained
ecosystems: [npm, pypi]
tools_affected: [paysafe-checkout, paysafe-vault, neteller, skrill-payments, paysafe-js, paysafe-api, paysafe-node, paysafe-cards, paysafe-fraud, paysafe-kyc, skrill, skrill-sdk, paysafe-payments, paysafe-sdk]
tags: [supply-chain, typosquat, credential-theft, fake-sdk, npm, pypi, ci-cd-secrets, payment-fraud]
---

## TL;DR

Socket detected a coordinated typosquatting campaign on **2026-07-07**: **17 packages across npm (13) and PyPI (4)**, impersonating SDKs for the payment services **Paysafe, Skrill, and Neteller**. The fake SDKs mimic real client APIs closely enough to pass casual integration testing — they return fake "success" responses instead of calling the real payment platform — while silently harvesting environment-variable secrets (API keys, AWS/GitHub/npm tokens) and exfiltrating them over HTTPS to a C2 endpoint on AWS/ngrok infrastructure with a history of hosting NjRAT command-and-control. Each npm package was flagged as malware within **6 minutes** of publication.

## What happened

On July 7, 2026, a threat actor simultaneously published a cluster of packages presenting themselves as official or convenience SDKs for three payment processors popular with fintech and e-commerce developers:

**npm (13 packages, versions 1.0.0–1.0.3):** `paysafe-checkout`, `paysafe-vault`, `neteller`, `skrill-payments`, `paysafe-js`, `paysafe-api`, `paysafe-node`, `paysafe-cards`, `paysafe-fraud`, `paysafe-kyc`, `skrill`, `skrill-sdk`, `paysafe-payments`

**PyPI (4 packages, version 1.0.0):** `paysafe-kyc`, `paysafe-payments`, `paysafe-sdk`, `paysafe-api`

The malicious `paysafe-node` package, for example, implements a client that closely mirrors the real Paysafe REST API — it reads configuration from environment variables and exposes the expected endpoints for creating/retrieving payments and customers. Instead of making the real outbound call, it **immediately returns a simulated success response**, so a developer integrating and smoke-testing the "SDK" sees no errors. Behind the scenes, the package harvests every environment variable matching `KEY`, `SECRET`, `TOKEN`, `PASS`, or `AUTH` — in practice this captures values like `PAYSAFE_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `GITHUB_TOKEN`, and `NPM_TOKEN` from developer machines and CI/CD runners — and POSTs them as JSON to a C2 endpoint.

**C2 infrastructure:** `caliber-spinner-finishing[.]ngrok-free[.]dev:443`, reached over HTTPS; the hostname/domain was encoded in the payload using multi-step XOR/character-shift obfuscation to resist static string scanning. The IP the ngrok tunnel resolved to has a documented reputation as a C2 server for other stealer families, including NjRAT.

**NPM-vs-PyPI behavioral difference:** npm variants only activate credential theft when a Paysafe API key is actually present in the environment (reducing noise/detection in empty test environments); PyPI variants auto-activate on import regardless. The malware also includes sandbox/anti-analysis checks — it exits early on hosts with fewer than 2 CPU cores or common virtualization indicators, a common technique to evade automated scanners.

Socket's automated scanner flagged each npm package as malicious within roughly 6 minutes of publication, and the packages have since been removed from both registries.

## Am I affected?

```bash
# npm — check for any of the fake package names
npm ls paysafe-checkout paysafe-vault neteller skrill-payments paysafe-js \
  paysafe-api paysafe-node paysafe-cards paysafe-fraud paysafe-kyc \
  skrill skrill-sdk paysafe-payments 2>/dev/null

# PyPI — check installed packages
pip show paysafe-kyc paysafe-payments paysafe-sdk paysafe-api 2>/dev/null

# Check package.json / requirements.txt for any of these names
grep -E "paysafe-|neteller|skrill" package.json requirements.txt 2>/dev/null
```

If any of these packages appear in your dependency tree (direct or via a lockfile installed on/after **2026-07-07**), treat any secrets in the environment where they ran as compromised — particularly `PAYSAFE_API_KEY` and any cloud/CI credentials (`AWS_*`, `GITHUB_TOKEN`, `NPM_TOKEN`).

## If you are affected

1. **Remove the package immediately** and reinstall from the official, verified SDK for your payment provider.
2. **Rotate every credential** that was present as an environment variable on the machine/CI runner where the package ran — payment API keys first, then cloud and VCS tokens.
3. **Check outbound connection logs** for traffic to `caliber-spinner-finishing.ngrok-free.dev` or other `*.ngrok-free.dev` endpoints from build/CI infrastructure.
4. **Audit your payment provider dashboard** for unauthorized API key usage or newly created API keys you didn't provision.

→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention

- **Only install payment SDKs from the vendor's documented official package name**, verified against the provider's own developer docs — not from a search-engine or AI-assistant-suggested package name.
- **Never let an AI coding agent `npm install`/`pip install` a payment or auth SDK without confirming the exact package name against the vendor's official documentation first** — this campaign specifically targets the "ask the assistant for a payment SDK, install whatever it suggests" workflow common in vibe-coded fintech integrations.
- **Scope CI secrets narrowly** so a compromised dependency can only reach the minimum credentials it needs, not every `*_KEY`/`*_TOKEN`/`*_SECRET` in the environment.
- **Use a pre-install scanner** (Socket, Aikido, Snyk) that flags newly-published, low-download packages before they land in a lockfile.

→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## IOCs

| Type | Value |
|---|---|
| npm packages | `paysafe-checkout`, `paysafe-vault`, `neteller`, `skrill-payments`, `paysafe-js`, `paysafe-api`, `paysafe-node`, `paysafe-cards`, `paysafe-fraud`, `paysafe-kyc`, `skrill`, `skrill-sdk`, `paysafe-payments` |
| PyPI packages | `paysafe-kyc`, `paysafe-payments`, `paysafe-sdk`, `paysafe-api` |
| C2 domain | `caliber-spinner-finishing[.]ngrok-free[.]dev:443` |
| Malicious versions | npm: 1.0.0–1.0.3; PyPI: 1.0.0 |

## Sources

- [Socket — Coordinated npm and PyPI Campaign Typosquats Popular Secure Payment Apps](https://socket.dev/blog/npm-pypi-campaign-typosquats-popular-secure-payment-apps) — primary disclosure; full package list, C2 domain, obfuscation technique, behavioral analysis, 49 file-hash IOC list.
- [BleepingComputer — Fake Paysafe, Skrill SDKs on NPM and PyPi steal credentials](https://www.bleepingcomputer.com/news/security/fake-paysafe-skrill-sdks-on-npm-and-pypi-steal-credentials/) — independent corroboration; exfiltrated-data field list, activation-behavior differences between npm and PyPI variants.
- [gbhackers — npm and PyPI Malware Campaign Exfiltrates CI/CD Secrets Through Fake Payment SDKs](https://gbhackers.com/npm-and-pypi-malware/) — additional corroboration.
