---
id: ongoing-vibe-platform-exposure
title: "Vibe-coded app data exposure — Lovable, Bolt, Replit, Base44 pattern issues"
date_disclosed: 2025
last_updated: 2026-08-23
severity: high
status: ongoing
ecosystems: [lovable, bolt, replit, v0, supabase, base44]
tools_affected: [lovable, bolt, replit, v0, base44]
tags: [data-exposure, rls, env-vars, bola, vibe-platform, configuration, auth-bypass]
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
- **RLS enabled with no policies attached — a configuration warning, not exposure by itself.** Distinct from "RLS off": Supabase's linter flags it separately (`rls_enabled_no_policy`), and for ordinary roles a *read* with no matching policy is default-deny (an empty result, not an error, not your data). The real risk is indirect — a *write* against it fails loudly with a genuine RLS-violation error, and the fix people reach for is often disabling RLS entirely rather than modeling the missing policy — and that a policy count says nothing about bypass roles (`service_role`, table owner), which skip RLS regardless of how many policies exist.
- **Orphaned backend projects.** A side-project or demo backend (Supabase/Firebase/etc.) outlives the frontend that used to call it — the app gets abandoned, redirected, or never finished, but the backend project stays live and reachable indefinitely, along with whatever RLS/policy state (or lack of it) it shipped with.

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

## June 2026 — Escape.tech production scan: 5,600 apps, 2,000+ vulnerabilities, 400+ exposed secrets

Security startup **Escape** scanned **5,600 production vibe-coded applications** in May–June 2026 and reported **2,000+ distinct vulnerabilities** across the corpus — including **400+ exposed secrets** (API keys, service tokens, connection strings embedded in client bundles or unauthenticated endpoints) and **175 cases of personal data leakage** that included medical records, bank account data, and partial payment information. The study's conclusion: the median vibe-coded app in production has at least one critical-severity finding; roughly 1-in-14 leaks data that would constitute a notifiable breach under GDPR or CCPA. The Escape findings are consistent with the RedAccess 380K-app scan from May 2026 — both show that **vibe-coded apps are systematically under-secured at launch**, not sporadically.

## June 2026 — Tea dating app: 72,000 user photos leaked via unauthenticated endpoint

**Tea**, an AI-generated dating app built with Lovable + Supabase, leaked **72,000 user profile photos** via a publicly accessible Supabase storage bucket with no Row-Level Security policy. The bucket URL was embedded in the client bundle. No authentication was required to enumerate or download photos. The app had ~8,000 registered users; photos included faces and location-tagged images. Reported by a security researcher on June 6, 2026; the developer patched within 48 hours. Representative of the Lovable + Supabase `service_role`-in-client-bundle antipattern that appears in the Escape data.

## June 2026 — VibeWrench study: AI agents as attack amplifiers in vibe-coded repos

Researchers from the **VibeWrench** project (Carnegie Mellon + Stanford, June 2026 preprint) studied what happens when AI coding agents are given repositories that contain the vulnerabilities documented in this advisory. Key finding: agents given repositories with RLS-off Supabase configurations **consistently reproduced and extended** the misconfiguration rather than correcting it — the agent's existing code context amplified the original mistake. Agents asked to "add a new endpoint" in a repo with IDOR added new endpoints with IDOR. Agents asked to "improve authentication" in repos with hallucinated-auth patterns added more layers of hallucinated auth, not real auth checks. **The fix**: run a security-specialist agent in a *separate* context with no exposure to the original code, and explicitly instruct it to look for the antipatterns documented here.

## April 2026 — Lovable platform-wide BOLA: public-project regression, disputed then acknowledged

Security researcher **@weezerOSINT** reported a Broken Object Level Authorization (BOLA) flaw to Lovable's HackerOne program on **March 3, 2026**: any authenticated Lovable user could read another tenant's public-project **source code and AI chat history** by visiting the project link, because a backend permission-unification change in **February 2026** silently re-enabled chat/source access that Lovable had deliberately disabled for public projects back in March–May 2025 (enterprise projects were restricted from public visibility in May 2025; all new projects went private-by-default in November 2025). HackerOne triagers closed the report(s) as duplicates/expected behavior without escalating, on the belief that public-project visibility was intentional. After **48 days** with no fix, the researcher published the finding on X on **April 20, 2026**, prompting wide pickup (The Register, Fast Company, Bastion) and framing it as a mass breach affecting every public Lovable project created before November 2025.

**Lovable's initial framing disputed the "breach" characterization** — a spokesperson told The Register the exposure was closer to a documentation gap around what "public" means for a project. In its own published incident response, Lovable instead attributed the root cause to the February 2026 backend regression plus a HackerOne triage-process failure, stated the exposure was **limited to public projects' chat history and source code** (private projects and Lovable Cloud were not affected), shipped a fix within **~2 hours** of the public disclosure, converted all public projects to private (apart from official templates), and began notifying affected project owners. **Source discrepancy worth flagging:** The Register's initial writeup (and downstream secondary coverage) described the exposure as including "database credentials," while Lovable's own incident postmortem states only chat history and source code were exposed and explicitly excludes credentials/Lovable Cloud — stated here as reported by each source rather than reconciled, since Lovable's post is the more authoritative primary account of scope but was published after, and in response to, the wider "database credentials" framing.

This is the same underlying 48-day-open BOLA report already summarized in this advisory's TL;DR and sourced via The Next Web; this section adds the full timeline, Lovable's dispute-then-acknowledge response, and the discrepancy over what data was actually exposed.

## July 2025 — Base44 auth endpoint exposure (patched within 24 hours)

**Base44**, an AI-powered app builder (similar positioning to Lovable/Bolt), shipped with **unauthenticated registration and OTP verification endpoints** whose only intended protection was an `app_id` parameter — which was not treated as a secret and was trivially enumerable from the client. A researcher demonstrated that registration/login flows could be invoked for any app without possessing the `app_id` as a secret, bypassing authentication entirely. Base44 patched the issue within **24 hours** of responsible disclosure; no exploitation was confirmed. The pattern (auth endpoint protected only by a non-secret identifier) recurs across vibe-coding platforms as a direct consequence of AI-generated auth code that looks correct but isn't.

## June 2026 — Wiz Research: Base44 critical vulnerability exposes private enterprise app data

**Wiz Research** disclosed a **critical vulnerability** in **Base44** (the AI-powered app builder comparable to Lovable/Bolt) that exposed **private enterprise applications and their data** to unauthenticated access. The vulnerability allowed an attacker to enumerate and access Base44 apps belonging to other organizations without authentication, bypassing the intended per-org isolation boundary. Enterprise users of Base44 who had deployed internal-facing applications (HR tools, customer management dashboards, internal knowledge bases) were exposed.

Base44 patched the vulnerability promptly after Wiz's responsible disclosure. Wiz characterized the issue as a **"critical" access-control flaw** affecting the platform's multi-tenant isolation layer — the same class of bug (BOLA / broken object-level authorization at the platform layer, not individual app layer) that has appeared in Lovable (48-day-open BOLA report) and Replit (public Repl defaults). The pattern: vibe-coding platforms are building multi-tenant infrastructure at speed, and access-control mistakes at the platform level have wider blast radius than in any individual app they host.

## July 2026 — Theori's Xint Code study: authorization flaws double as AI-hardened apps grow (greenfield vs. brownfield)

Security firm **Theori** published findings from its **Xint Code** AI-code-scanning platform (published 2026-07-22) comparing three AI-assisted development scenarios rather than just scanning apps after the fact: a **greenfield app built from a well-written spec** (experienced-developer oversight), a **greenfield app built from a minimal "just build this" prompt** (casual/vibe-coded), and a **brownfield app** — the legacy PHP forum **Gnuboard7**, migrated to a Laravel + React stack and then AI-hardened. Each was scanned for 30 minutes combining runtime and source analysis. Combined result: **434 exploitable vulnerabilities** — **196** in the two greenfield apps, **238** in the hardened brownfield app. By category: **93 denial-of-service/rate-limiting** flaws, **88 authorization/IDOR** flaws, **54 access-boundary/traversal/SSRF** flaws, and **23 critical-severity** findings (11 hardcoded secrets, 6 debug-mode RCE). The headline finding for larger/legacy codebases specifically: **IDOR/authorization flaws made up only 11% of findings in the small greenfield apps but 28% in the larger brownfield app** — fine-grained authorization holds up while an app is small and breaks down as it grows, even when the AI was explicitly asked to harden the code rather than just extend it. Consistent with, and adds a controlled-comparison methodology to, the RedAccess/Escape.tech findings already tracked in this advisory.

## Sources
- [Vibe Eval — Vibe Coding Security: Risks, Vulnerabilities, and Fixes (2026)](https://vibe-eval.com/vibe-coding-security-risks)
- [The Next Web — Lovable security crisis: 48 days of exposed projects, closed bug reports](https://thenextweb.com/news/lovable-vibe-coding-security-crisis-exposed)
- [AIThinkerLab — Lovable AI Security Vulnerabilities: 16 Critical Flaws](https://aithinkerlab.com/lovable-ai-security-vulnerabilities-vibe-hacking/)
- [Mobb — The Hidden Security Crisis in AI-Generated Apps: 40% Are Leaking Sensitive Data](https://www.mobb.ai/blog/the-hidden-security-crisis-in-ai-generated-apps)
- [Android Headlines — Vibe Coding Rise is Fueling a Surge in Security Vulnerabilities](https://www.androidheadlines.com/2026/05/vibe-coding-security-risks-data-leaks-ai-apps.html)
- [Vibe App Scanner — Platform Security Guides](https://vibeappscanner.com/platforms)
- [Vibe Eval — Is Replit Safe in 2026?](https://vibe-eval.com/safety/replit/)
- [The Register — Lovable denies data leak, cites 'intentional behavior'](https://www.theregister.com/2026/04/20/lovable_denies_data_leak/) — initial disclosure, HackerOne timeline, Lovable's dispute of the "breach" framing.
- [Lovable — Our response to the April 2026 incident](https://lovable.dev/blog/our-response-to-the-april-2026-incident) — Lovable's own postmortem: root cause, scope, timeline, remediation.
- [Axios — Thousands of AI-built apps exposed sensitive corporate and personal data, researchers found](https://www.axios.com/2026/05/07/loveable-replit-vibe-coding-privacy)
- [Security Boulevard — Thousands of Vibe-Coded Apps Exposing Corporate, Personal Data: RedAccess](https://securityboulevard.com/2026/05/thousands-of-vibe-coded-apps-exposing-corporate-personal-data-redaccess/)
- [VentureBeat — Vibe coding exposed 380,000 corporate apps — 5,000 held sensitive data](https://venturebeat.com/security/vibe-coded-apps-shadow-ai-s3-bucket-crisis-ciso-audit-framework)
- [IANS Research — Easy-to-Build, Easy-to-Expose: How Vibe Coding Is Creating New Data Risks](https://www.iansresearch.com/resources/all-blogs/post/security-blog/2026/05/15/easy-to-build--easy-to-expose--how-vibe-coding-is-creating-new-data-risks)
- [Futurism — Vibe Coded Apps Are Spilling Users' Personal Information Directly Into the Maw of Greedy Hackers](https://futurism.com/artificial-intelligence/vibe-coded-apps-spilling-personal-information)
- [SecurityWeek — Vibe-Coded Apps Riddled With Exploitable Security Flaws](https://www.securityweek.com/vibe-coded-apps-riddled-with-exploitable-security-flaws/) — Theori Xint Code study, fetched directly; greenfield-vs-brownfield methodology, 434 total findings.
