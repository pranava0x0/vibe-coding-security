---
id: 2026-02-google-api-key-gemini-scope-escalation
title: "Google API keys silently gain Gemini access when a project enables the Generative Language API — 2,863 leaked keys exposed"
date_disclosed: 2026-02-25
last_updated: 2026-02-25
severity: high
status: mitigated
ecosystems: [google-cloud, gemini, google-ai-studio-sdk]
tools_affected: [Google AI Studio SDK, Gemini API, Google Cloud API keys, Google Maps API keys]
tags: [credential-exposure, api-key-leak, privilege-escalation, google-cloud, gemini, vendor-hygiene]
---

## TL;DR
Google Cloud reuses a single API key format (`AIza...`) for both low-sensitivity, publicly-embeddable services (Google Maps) and high-sensitivity ones (Gemini). The moment a project owner enables the Generative Language API — often for an unrelated reason, or by another team in the same project — **every existing key in that project silently gains access to Gemini endpoints**, with no notification to the developer who originally deployed the key as a "safe to expose" Maps key. Truffle Security scanned public sources and found **2,863 live keys** exposed this way, some capable of reading uploaded files and cached content, or running up thousands of dollars in usage charges.

## What happened
Google API keys are commonly treated as safe to embed client-side for services like Google Maps — Google's own documentation historically described Maps keys as identifiers rather than secrets, since HTTP-referrer restrictions were assumed to contain the blast radius. Truffle Security scanned the **November 2025 Common Crawl dataset** for exposed `AIza...`-prefixed keys and found **2,863 live keys** across public websites.

The root cause: Google Cloud's API key model is **project-scoped, not key-scoped, by default**. When any API is enabled on a Google Cloud project — including the **Generative Language API** that powers Gemini — every unrestricted API key that already exists in that project automatically gains the ability to call the newly-enabled API too, with no re-issuance, no notification, and (for keys created before scoped defaults existed) no warning that a previously "harmless" identifier now authenticates to a materially more sensitive service. A key deployed years earlier purely for Maps tile requests can, after someone in the same project turns on Gemini for an unrelated feature, be used by anyone who scraped it off a public webpage to call Gemini.

**What an attacker could do with a leaked key:** access private data through the `/files/` and `/cachedContents/` endpoints (uploaded documents, prior conversation context cached server-side), and generate usage charges by maxing out API calls — one developer reported an **$82,314.44** bill from a stolen key over a two-day span, up from a normal ~$180/month spend, as separately reported by The Register in March 2026. An attacker can also exhaust quota, denying service to the legitimate application.

**Disclosure timeline:** Truffle Security reported the issue to Google on **2025-11-21**. Google initially classified it as **"Intended Behavior"** (2025-11-25), then **reclassified it as a Bug** on **2025-12-02** after Truffle demonstrated the issue using Google's own infrastructure, and finally classified it as **"Single-Service Privilege Escalation, READ"** on **2026-01-13**. Google has since implemented a leaked-key detection pipeline and states new AI Studio keys will default to Gemini-only scope going forward, with proactive leak notifications planned — but as of the public disclosure (2026-02-25), the **root-cause fix — preventing pre-existing keys from silently inheriting newly-enabled API scopes — remained in progress**, meaning the underlying class of exposure was not yet closed for existing projects.

## Am I affected?
You're exposed if you have ever embedded a Google API key client-side (in a web app, mobile app, or any public repository) for a low-sensitivity service like Maps, Places, or Static Maps, **and** the Google Cloud project that key belongs to has the Generative Language API enabled — by you, by a teammate, or by any other project member, at any point since the key was created.

```bash
# Search your own repos/build output for exposed Google API keys
grep -rE "AIza[0-9A-Za-z_\-]{35}" . --include="*.js" --include="*.html" --include="*.json" --include="*.env*" 2>/dev/null

# Check in Google Cloud Console whether the Generative Language API is enabled
# on the project that issued a given key:
#   APIs & Services → Enabled APIs & services → search "Generative Language API"
```

Also check GitHub, client-side bundles, and any public repo for a key you assumed was safe to expose — the safety assumption itself is what this vulnerability breaks.

## If you are affected
1. **Rotate the key immediately** in Google Cloud Console, regardless of whether you've confirmed abuse — treat any publicly-exposed `AIza...` key as compromised.
2. **Apply key restrictions**: scope every key to the specific APIs it needs (API restrictions) and, where possible, the specific HTTP referrers/IP ranges/apps that should call it (application restrictions). An unrestricted key is the entire vulnerability class in one setting.
3. **Split keys by sensitivity**: don't let a key intended for a public-facing Maps widget live in the same project as your Gemini/AI Studio usage, if you can avoid it — project-level API enablement is what causes the silent scope grant.
4. **Review billing** for anomalous Gemini API usage on any project where a key may have been publicly exposed.
5. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

**For vibe coders specifically:** if an AI coding assistant scaffolds a project using a Google Maps or other "safe to expose" Google API key pattern, verify current Google Cloud key-restriction settings before shipping — don't rely on old guidance (including the assistant's own training data) that a given Google API key type is inherently safe client-side. Always set explicit API restrictions on every key you create, and don't enable the Generative Language API on a project that also holds keys meant for lower-sensitivity, publicly-exposed use.

## Sources
- [Truffle Security — Google API Keys Weren't Secrets. But then Gemini Changed the Rules.](https://trufflesecurity.com/blog/google-api-keys-werent-secrets-but-then-gemini-changed-the-rules) — primary disclosure, fetched directly: 2,863 exposed keys, disclosure timeline, Google's classification changes.
- [BleepingComputer — Previously harmless Google API keys now expose Gemini AI data](https://www.bleepingcomputer.com/news/security/previously-harmless-google-api-keys-now-expose-gemini-ai-data/)
- [CSO Online — 'Silent' Google API key change exposed Gemini AI data](https://www.csoonline.com/article/4138749/silent-google-api-key-change-exposed-gemini-ai-data.html)
- [The Hacker News — Thousands of Public Google Cloud API Keys Exposed with Gemini Access After API Enablement](https://thehackernews.com/2026/02/thousands-of-public-google-cloud-api.html)
- [The Register — Dev stunned by $82K Gemini API key bill after theft](https://www.theregister.com/2026/03/03/gemini_api_key_82314_dollar_charge/) — independent corroboration of real-world financial impact from a leaked key.
