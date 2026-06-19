---
id: 2025-12-react2shell-rce
title: "React2Shell — CVE-2025-55182 RCE in React Server Components (Dec 2025 → exploited through Apr 2026)"
date_disclosed: 2025-12-05
last_updated: 2026-06-04
severity: critical
status: patched
ecosystems: [npm, react, nextjs, vite, react-router]
tools_affected: [React 18/19 (RSC), Next.js, Waku, React Router (RSC mode), RedwoodSDK, Parcel RSC, Vite RSC plugin]
tags: [rce, deserialization, unauthenticated, cisa-kev, active-exploitation, react-server-components]
---

## TL;DR

**CVE-2025-55182 "React2Shell"** (CVSS 10.0, CISA KEV) is an unauthenticated RCE in **React Server Components** caused by insecure deserialization in React's Flight protocol. Any exposed RSC endpoint is a one-request RCE — no auth, no special setup. Exploitation in the wild was confirmed in December 2025; a large-scale credential-harvesting campaign had compromised at least **766 hosts** by April 2026. Patch to the fixed React version immediately.

## What happened

Security researchers disclosed a critical deserialization vulnerability in React's **Flight protocol** — the wire format used to stream React Server Component payloads. React did not properly validate payloads sent to React Server Function endpoints, allowing an unauthenticated attacker to craft a malicious payload that triggers **arbitrary code execution** on the server.

**Root cause:** Insecure deserialization in the RSC Flight protocol payload decoder. Attacker-controlled input is decoded and instantiated as framework objects without sanitization.

**Affected frameworks (any that expose an RSC endpoint):**
- React 18.x / 19.x (RSC mode)
- **Next.js** (all versions with App Router / RSC enabled)
- **Waku** (RSC-first framework)
- **React Router** (RSC preview mode)
- **RedwoodSDK** (RSC mode)
- **Parcel RSC plugin**
- **Vite RSC plugin**

**Exploitation timeline:**
- **2025-12-05**: First exploitation attempts detected in the wild (Windows and Linux)
- **2025-12-xx**: CISA adds CVE-2025-55182 to KEV catalog
- **2025-12-31**: ~90,300 instances still exposed
- **2026-01**: RondoDox botnet exploits React2Shell to hijack IoT devices and web servers
- **2026-04**: Large-scale credential harvesting campaign observed; at least **766 hosts** confirmed compromised — attackers steal database credentials, SSH keys, AWS secrets, shell history, Stripe API keys, and GitHub tokens; also deploy cryptomining and backdoors
- **2026-06**: ~68,400 U.S. instances remain; patch adoption still incomplete

**Downstream note:** The vulnerability surfaces in the **Next.js May 2026 security release** as a related RSC DoS (CVE-2026-23870) — a separate issue in the same component family, addressed in the same release window. React2Shell itself predates that batch.

## Am I affected?

```bash
# Check React version
node -e "console.log(require('react/package.json').version)"

# Patched versions:
# React 19.0.4, 19.1.5, 19.2.4 (and later)
# Next.js: 15.0.8, 15.1.12, 15.2.9, 15.3.9, 15.4.11, 15.5.10, 16.0.11, 16.1.5
# Check your Next.js version:
node -e "console.log(require('next/package.json').version)"
```

**You are only exposed if your app:**
1. Uses React Server Components (RSC / Server Actions / App Router), AND
2. Exposes an RSC endpoint to the public internet (or to untrusted network callers)

Vite-only apps using React in classic client mode (no RSC) are **not affected**.

## If you are affected

1. **Patch immediately**: upgrade React to 19.0.4 / 19.1.5 / 19.2.4+ and Next.js to the corresponding fixed version.
2. **Rotate all credentials** on any server that ran an exposed RSC endpoint — attackers demonstrated full credential harvest in the wild.
3. **Check for backdoors**: look for unexpected cron jobs, systemd services, or SSH authorized_keys entries added since December 2025.
4. See [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md).

## Prevention

- **Keep React and Next.js up to date** — this class of deserialization bug requires framework-level patching.
- **Do not expose RSC endpoints directly** to the public internet unless necessary; place them behind an auth layer.
- **Use a WAF** (Cloudflare, Vercel WAF, AWS WAF) with rules for abnormal RSC payload size/structure as a defense-in-depth layer.
- **Monitor for RCE IOCs**: unexpected outbound connections (cryptomining C2, exfil endpoints), new users/cron jobs/SSH keys.

## Sources

- [The Hacker News — "Critical RSC Bugs in React and Next.js Allow Unauthenticated Remote Code Execution"](https://thehackernews.com/2025/12/critical-rsc-bugs-in-react-and-nextjs.html) — initial disclosure, CVSS 10.0, affected frameworks.
- [CybersecurityNews — "Critical React2Shell RCE Vulnerability Exploited in the Wild"](https://cybersecuritynews.com/react2shell-rce-vulnerability/) — active exploitation confirmation, attack details.
- [The Hacker News — "Critical React2Shell Flaw Added to CISA KEV After Confirmed Active Exploitation"](https://thehackernews.com/2025/12/critical-react2shell-flaw-added-to-cisa.html) — CISA KEV listing.
- [The Hacker News — "RondoDox Botnet Exploits Critical React2Shell Flaw"](https://thehackernews.com/2026/01/rondodox-botnet-exploits-critical.html) — botnet exploitation, January 2026.
- [The Hacker News — "Hackers Exploit CVE-2025-55182 to Breach 766 Next.js Hosts, Steal Credentials"](https://thehackernews.com/2026/04/hackers-exploit-cve-2025-55182-to.html) — April 2026 large-scale campaign, 766 confirmed victims.
- [CybersecurityNews — "Microsoft Details Mitigations Against React2Shell RCE Vulnerability"](https://cybersecuritynews.com/microsoft-details-mitigations-against-react2shell-rce-vulnerability/) — mitigation guidance.
- [NVD CVE-2025-55182](https://nvd.nist.gov/vuln/detail/CVE-2025-55182) — official CVE record, CVSS 10.0.
- [Vercel security bulletins](https://vercel.com/kb/bulletin) — Next.js patched version matrix.
