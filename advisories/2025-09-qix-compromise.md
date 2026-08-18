---
id: 2025-09-qix-compromise
title: "qix npm account compromise — chalk, debug, ansi-styles (September 2025)"
date_disclosed: 2025-09-08
last_updated: 2026-08-18
severity: critical
status: contained
ecosystems: [npm]
tools_affected: [any-node-project, any-frontend, cursor, claude-code]
tags: [supply-chain, phishing, npm, crypto-wallet-hijack, browser]
---

## TL;DR
On 2025-09-08, npm maintainer Josh Junon (qix) was phished. The attacker took over ~18 of his packages — `chalk`, `debug`, `ansi-styles`, `strip-ansi`, `color-convert`, `wrap-ansi`, and more — collectively serving over **2 billion downloads per week**. The injected payload was a browser-side crypto-wallet hijacker. Malicious versions were live for ~2 hours before takedown.

## What happened
The attacker sent a spear-phishing email from `npmjs.help` (look-alike domain), impersonating npm support. The email warned of imminent account lockout unless 2FA was reset. The page collected credentials + the OTP, giving the attacker a fully-authenticated session.

Within minutes the attacker pushed new versions of 18 packages with crypto-stealing JS. The code was designed to be **inert in pure Node contexts** (so server-side projects didn't notice anything) but to **hook browser web APIs** when bundled into frontend code, silently rewriting wallet addresses during transactions.

Because chalk/debug/ansi-styles are foundational logging/styling deps, they appear as transitive deps in essentially every Node project. The blast radius was limited only by the short detection window and the browser-only payload.

## Am I affected?

```bash
# Lockfile check — all the qix packages
npm ls chalk debug ansi-styles strip-ansi color-convert wrap-ansi ansi-regex --all
```

If you ran `npm install` (not `npm ci` with a pre-locked file) between roughly 2025-09-08 08:00 UTC and 10:00 UTC, your lockfile may have pinned a malicious version. Re-install from a clean lockfile and run `npm audit`.

If you ship a frontend that bundles these packages, audit any user reports of wallet-address discrepancies during that window.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)

For browser-shipped builds: re-bundle from a clean lockfile, invalidate CDN caches, redeploy.

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — pin exact versions in lockfile, use `npm ci`
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — for maintainers: hardware 2FA, look-alike-domain awareness

## Update — 2026-08-18: formally attributed to the same DPRK-linked actor behind the March 2026 Axios compromise

Amazon Threat Intelligence published a report on **2026-07-29** publicly tying this incident — and a March 2025 `typo-crypto` package compromise not previously covered in this repo — to the **same DPRK-linked threat actor** already attributed to the [March 2026 Axios compromise](2026-03-axios-compromise.md), tracked under the aliases **SAPPHIRE SLEET, STARDUST CHOLLIMA, BlueNoroff, CageyChameleon, and Alluring Pisces**. AWS states plainly: "the debug and chalk incidents haven't previously been connected to it... this is the first time these compromises have been publicly tied to this DPRK-linked threat actor" — whereas the Axios compromise had already carried this attribution. Amazon's attribution rests on shared TTPs across all four incidents: trojanized npm packages, `postinstall`-hook execution, code reuse across payloads, and a consistent initial-access pattern of socially engineering a trusted maintainer before publishing the malicious update — the same phishing-for-2FA-reset playbook used against Josh Junon (qix) here. This confirms a single operator ran at least four separate npm supply-chain compromises across a 13-month span (March 2025 → March 2026) using the same toolkit and access technique, rather than four unrelated incidents.

## Sources
- [AWS Security Blog — Amazon identifies North Korean hacker group behind open-source supply chain attacks](https://aws.amazon.com/blogs/security/amazon-identifies-north-korean-hacker-group-behind-open-source-supply-chain-attacks/) — primary source for the 2026-08-18 update: threat-actor aliases, attribution of debug/chalk/typo-crypto to the same actor as Axios, shared-TTP analysis.
- [Socket — npm Author Qix Compromised via Phishing](https://socket.dev/blog/npm-author-qix-compromised-in-major-supply-chain-attack)
- [StepSecurity — 20+ Popular NPM Packages Compromised](https://www.stepsecurity.io/blog/20-popular-npm-packages-compromised-chalk-debug-strip-ansi-color-convert-wrap-ansi)
- [Phoenix Security — Largest NPM Compromise in History](https://phoenix.security/qix-npm-compromise/)
- [Palo Alto Networks — Widespread npm Supply Chain Attack](https://www.paloaltonetworks.com/blog/cloud-security/npm-supply-chain-attack/)
- [Wiz — Widespread npm Supply Chain Attack: Impact & Scope](https://www.wiz.io/blog/widespread-npm-supply-chain-attack-breaking-down-impact-scope-across-debug-chalk)
