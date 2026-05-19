---
id: ongoing-vibe-platform-exposure
title: "Vibe-coded app data exposure — Lovable, Bolt, Replit pattern issues"
date_disclosed: 2025
last_updated: 2026-05-19
severity: high
status: ongoing
ecosystems: [lovable, bolt, replit, v0, supabase]
tools_affected: [lovable, bolt, replit, v0]
tags: [data-exposure, rls, env-vars, bola, vibe-platform, configuration]
---

## TL;DR
Systemic data exposure across vibe-coding platforms in 2025–2026. Lovable: 16 critical flaws documented + a BOLA report left open 48 days. Bolt: env-var leakage in client bundles. Replit: secrets exposed via public Repls. Cross-platform: 40–62% of AI-generated code contains vulnerabilities, 91.5% of Q1 2026 vibe-coded apps had at least one AI-hallucination-related flaw. **May 2026 update:** Israeli researcher group **RedAccess scanned ~380,000 publicly accessible vibe-coded apps** (built on Lovable, Base44, Netlify, Replit) and found ~**5,000 leaking sensitive corporate/personal data** — medical records, financial info, full unredacted customer service conversations, internal banking data, shipping-route intel, vendor contracts. Many apps had no authentication at all; many more had a trivial "any email" gate. **February 2026 — Moltbook**: a social-networking site built entirely through vibe coding leaked **1.5M authentication tokens and 35K email addresses** via a misconfigured public database; founder publicly admitted he "didn't write one line of code." **Georgia Tech Vibe Security Radar (Q1 2026)**: CVE attribution data shows **35 CVEs in March 2026 alone, up from 6 in January 2026** — a ~6× quarterly increase.

## What's recurring
This isn't one incident — it's a pattern. The common shapes:

- **Missing or broken Row-Level Security.** Lovable + Supabase + agent default = `service_role` everywhere, RLS off. Anyone with the anon key can read every row.
- **Service keys in client bundles.** Bolt/Lovable sometimes inject backend service keys into the frontend build, where they ship to every visitor.
- **BOLA / IDOR.** Endpoints accept user-provided IDs without authorization checks — fetch `/users/2` even though you're user 1.
- **Public Repls leaking secrets.** Replit projects default to public unless paid; new users paste API keys into `index.js` and ship them to GitHub indirectly.
- **Hallucinated auth.** The agent writes auth-looking code that doesn't actually authenticate. Endpoints feel protected; they aren't.

## Am I affected?
If you've shipped a Lovable / Bolt / Replit / v0 app to real users without a security review, treat this as a "yes" until proven otherwise.

Quick self-audit:

```bash
# Are any service-role / admin keys in your client bundle?
# (Run from your built site root)
grep -r "service_role\|sk_live\|AKIA[0-9A-Z]\{16\}" dist/ build/ public/ .next/ 2>/dev/null

# Are your Supabase tables RLS-protected?
# Run in the Supabase SQL editor:
# SELECT schemaname, tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
```

→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md) — full walkthrough

## If you are affected
1. **Stop the bleeding.** If a service key is in your client bundle: rotate it immediately, then redeploy with the new key kept server-side only.
2. **Turn RLS on.** For every Supabase table, enable RLS and write explicit policies. Default-deny.
3. **Audit IDOR.** For every endpoint that takes an ID, verify the request's authenticated user owns the resource.
4. **Scan with a tool that knows the patterns.** Mobb, Vibe App Scanner, Snyk, Semgrep.

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)

**Hard rule for vibe-coded apps that will hold real user data:** before launch, have a human (or a dedicated security agent in a fresh context) audit the auth, the RLS, and the secret layout. The agent that wrote the code is exactly the wrong agent to review it — it cannot see what it didn't write.

## Sources
- [Vibe Eval — Vibe Coding Security: Risks, Vulnerabilities, and Fixes (2026)](https://vibe-eval.com/vibe-coding-security-risks)
- [The Next Web — Lovable security crisis: 48 days of exposed projects, closed bug reports](https://thenextweb.com/news/lovable-vibe-coding-security-crisis-exposed)
- [AIThinkerLab — Lovable AI Security Vulnerabilities: 16 Critical Flaws](https://aithinkerlab.com/lovable-ai-security-vulnerabilities-vibe-hacking/)
- [Mobb — The Hidden Security Crisis in AI-Generated Apps: 40% Are Leaking Sensitive Data](https://www.mobb.ai/blog/the-hidden-security-crisis-in-ai-generated-apps)
- [Android Headlines — Vibe Coding Rise is Fueling a Surge in Security Vulnerabilities](https://www.androidheadlines.com/2026/05/vibe-coding-security-risks-data-leaks-ai-apps.html)
- [Vibe App Scanner — Platform Security Guides](https://vibeappscanner.com/platforms)
- [Vibe Eval — Is Replit Safe in 2026?](https://vibe-eval.com/safety/replit/)
- [Axios — Thousands of AI-built apps exposed sensitive corporate and personal data, researchers found](https://www.axios.com/2026/05/07/loveable-replit-vibe-coding-privacy)
- [Security Boulevard — Thousands of Vibe-Coded Apps Exposing Corporate, Personal Data: RedAccess](https://securityboulevard.com/2026/05/thousands-of-vibe-coded-apps-exposing-corporate-personal-data-redaccess/)
- [VentureBeat — Vibe coding exposed 380,000 corporate apps — 5,000 held sensitive data](https://venturebeat.com/security/vibe-coded-apps-shadow-ai-s3-bucket-crisis-ciso-audit-framework)
- [IANS Research — Easy-to-Build, Easy-to-Expose: How Vibe Coding Is Creating New Data Risks](https://www.iansresearch.com/resources/all-blogs/post/security-blog/2026/05/15/easy-to-build--easy-to-expose--how-vibe-coding-is-creating-new-data-risks)
- [Futurism — Vibe Coded Apps Are Spilling Users' Personal Information Directly Into the Maw of Greedy Hackers](https://futurism.com/artificial-intelligence/vibe-coded-apps-spilling-personal-information)
