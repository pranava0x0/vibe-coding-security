---
id: 2026-04-vercel-context-ai-breach
title: "Vercel breach via Context.ai OAuth supply chain (April 2026)"
date_disclosed: 2026-04-19
last_updated: 2026-05-19
severity: high
status: contained
ecosystems: [vercel, nextjs, third-party-ai]
tools_affected: [vercel, context.ai]
tags: [oauth, third-party-ai, infostealer, lumma, environment-variables, vibe-platform]
---

## TL;DR
On **2026-04-19** Vercel published a security bulletin disclosing that an attacker had pivoted from a third-party AI productivity tool (**Context.ai**) into a Vercel employee's Workspace, then into Vercel's internal environment, and enumerated/decrypted non-sensitive customer environment variables before being evicted. Initial access was via **Lumma Stealer** infecting a Context.ai employee — the AI-tool OAuth grant carried the compromise into Vercel. **Vercel's open-source projects (Next.js, Turbopack) and npm packages were not affected.** Sensitive (encrypted-at-rest) env vars were not accessed. This is the first widely documented "AI tool → cloud platform" OAuth-pivot supply-chain incident, and a preview of every "let me connect [SaaS] to my LLM dashboard" risk class.

## What happened
- **Stage 1 — infostealer.** A Context.ai employee's workstation was compromised by **Lumma Stealer**, harvesting Google Workspace tokens.
- **Stage 2 — Workspace takeover.** Attackers used the stolen tokens to access a Vercel employee's Google Workspace account, because Context.ai had been authorized to call Workspace on the user's behalf.
- **Stage 3 — Vercel takeover.** From the compromised Workspace, attackers pivoted into the same employee's Vercel account (Vercel uses Workspace SSO for staff).
- **Stage 4 — internal recon and exfil.** Attackers enumerated and decrypted **non-sensitive** environment variables stored on customer projects. Vercel says **encrypted-at-rest sensitive env vars were not accessed**, and confirmed (with GitHub, Microsoft, npm, Socket) that **Next.js, Turbopack, and the public npm packages were not touched**.
- **Stage 5 — disclosure.** Vercel CEO Guillermo Rauch posted a detailed thread on X on **2026-04-19**; Vercel published its KB bulletin on **2026-04-20**. Context.ai confirmed the upstream compromise.

Trend Micro and TechCrunch reported the threat actor as "sophisticated," with "operational velocity and detailed understanding of Vercel's systems," which is consistent with a targeted operation rather than opportunistic infostealer-log resale.

## Am I affected?

```bash
# 1. Were you a Vercel customer with projects that had non-encrypted env vars during the April window?
#    Check the Vercel dashboard → Project → Settings → Environment Variables → "sensitive" toggle.
#    Anything NOT marked sensitive was readable to the attacker.

# 2. Rotate everything in plaintext env vars regardless. Examples to check:
#    - Webhook signing secrets
#    - Third-party API keys (Stripe restricted keys, Postmark, SendGrid, OpenAI, Anthropic)
#    - Database connection strings (rotate if not marked sensitive)
#    - Feature-flag service keys
```

You are affected if any non-sensitive env var on a Vercel project contains a credential that grants persistent access to anything (auth provider keys, billing-system keys, internal API tokens).

### IOCs

| Type | Value |
|---|---|
| Compromised third party | `Context.ai` (AI productivity / meeting-notes tool) |
| Initial-access malware | `Lumma Stealer` (on Context.ai endpoint) |
| Affected Vercel surface | Customer environment variables **not** marked sensitive |
| Unaffected | Next.js, Turbopack, Vercel npm packages, encrypted-at-rest env vars |
| Disclosure date | 2026-04-19 (CEO X thread) / 2026-04-20 (Vercel KB) |

## If you are affected
1. Rotate every credential that lived in a non-sensitive env var on any Vercel project during the April 2026 window. Use [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) as a template.
2. Audit Vercel project access logs for the window 2026-04-15 → 2026-04-19 (Vercel published indicators on request).
3. **Mark every credential-bearing env var as "sensitive" going forward.** It costs nothing and removes them from readable storage.
4. Disconnect any Google Workspace OAuth grant to AI tools you do not actively use. Workspace → Security → "Third-party apps with account access."
5. If your project depends on Context.ai itself, treat any data it processed as exposed.

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ Default-deny third-party AI OAuth scopes. Each "Connect to my [calendar/inbox/drive]" you grant a vibe-coding-adjacent AI tool is now also a third-party-risk vector into whatever else uses the same SSO.
→ Treat AI-tool vendors as cloud third parties: ask for SOC 2, an infostealer-response playbook, and a workstation-EDR commitment before authorizing.

## Sources
- [Vercel — April 2026 security incident bulletin](https://vercel.com/kb/bulletin/vercel-april-2026-security-incident) — Primary vendor disclosure.
- [TechCrunch — App host Vercel says it was hacked and customer data stolen](https://techcrunch.com/2026/04/20/app-host-vercel-confirms-security-incident-says-customer-data-was-stolen-via-breach-at-context-ai/) — Confirms Context.ai as upstream third party.
- [The Hacker News — Vercel Breach Tied to Context AI Hack Exposes Limited Customer Credentials](https://thehackernews.com/2026/04/vercel-breach-tied-to-context-ai-hack.html) — Attack chain and impact scope.
- [Trend Micro — The Vercel Breach: OAuth Supply Chain Attack Exposes the Hidden Risk in Platform Environment Variables](https://www.trendmicro.com/en_us/research/26/d/vercel-breach-oauth-supply-chain.html) — OAuth pivot analysis.
- [OX Security — Vercel Breached via Context AI Supply Chain Attack](https://www.ox.security/blog/vercel-context-ai-supply-chain-attack-breachforums/) — Independent confirmation; threat-actor commentary.
- [Reco — The Vercel and Context AI breach: an AI supply chain attack, step by step](https://www.reco.ai/blog/vercel-context-ai-breach) — Step-by-step chain.
- [Dark Reading — Vercel Employee's AI Tool Access Led to Data Breach](https://www.darkreading.com/application-security/vercel-employees-ai-tool-access-data-breach) — Confirms employee/Workspace OAuth pivot.
- [Safe Security — The Vercel Breach 2026: How One Tool Became Every Organization's Third-Party Risk Problem](https://safe.security/resources/blog/vercel-breach-third-party-risk-management/) — Third-party-risk framing.
- [Rescana — Vercel April 2026 Security Incident: Context.ai-Linked Breach](https://www.rescana.com/post/vercel-april-2026-security-incident-context-ai-linked-breach-exposes-non-sensitive-environment-variables-and-customer-ac/) — Tactical impact summary.
