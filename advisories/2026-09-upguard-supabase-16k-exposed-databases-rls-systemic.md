---
id: 2026-09-upguard-supabase-16k-exposed-databases-rls-systemic
title: "UpGuard finds 16,326 Supabase databases with publicly readable tables across ~300,000 Supabase-backed domains — more than half carry PII, some carry plaintext passwords, auth tokens and card data; the mechanism in almost every case is a table created by migration or API with row-level security never enabled (2026-09-25)"
date_disclosed: 2026-09-25
last_updated: 2026-09-26
severity: high
status: ongoing
ecosystems: [supabase, lovable, bolt, v0, replit, postgres]
tools_affected: [supabase, "Supabase-backed apps built with Lovable / Bolt / v0 / Replit / Claude Code / Cursor", "any app shipping the anon key with tables lacking RLS"]
tags: [data-exposure, rls, supabase, vibe-platform, pii, plaintext-passwords, systemic-misconfiguration, anon-key, internet-scale-study, ongoing]
---

## TL;DR
On **2026-09-25** UpGuard published the largest measurement to date of the failure mode this repo has tracked as [ongoing-vibe-platform-exposure](ongoing-vibe-platform-exposure.md): of roughly **300,000 domains** fingerprinted as Supabase-backed, **16,326 databases returned readable table contents to an unauthenticated query using nothing but the public `anon` key and project URL every front end ships**. More than half of those show personal-data indicators; a smaller share exposes **passwords and authentication tokens**, and a very small number expose plausible **payment-card data**. The case studies are not toys: a US valet service with 100,000+ customer records and 78,000 licence plates, a Philippine OTP relay with 100,000+ SMS messages (passcodes included), a consulate's 25,000 applicant records with emergency-housing addresses, and a Canadian immigration coaching service storing **884 plaintext passwords**. TechCrunch carried Supabase's response the same day. **If you built on Supabase with an AI tool, assume any table created by a migration or through the API has RLS off unless you turned it on yourself** — check today.

## What happened

UpGuard (Greg Pollock, Director of Research) built a corpus of Supabase-backed sites from two sources — BuiltWith's technographic index and the raw JavaScript bundles in the Chrome UX Report dataset on BigQuery — by matching the Supabase project-URL and key patterns that every client bundle embeds. Roughly **300,000 domains** matched. For each, UpGuard issued the request a browser would make for a table named `users`; the response classifies the project as *readable* (rows returned), *readable but differently named* (the API lists other accessible tables), or *protected*. **16,326 projects returned readable rows.** UpGuard then sampled contents for PII indicators (names, emails, phones, addresses), credential indicators (password and token columns) and card-number patterns, and notified the owners of the most significant exposures.

The finding is a distribution, not a bug: Supabase has had RLS **on by default for tables created in the Table Editor since March 2025**, but **tables created programmatically — by a migration, by `CREATE TABLE` in the SQL editor, or by an AI coding tool writing SQL for you — still default to RLS off**, and a table with RLS off is world-readable through PostgREST to anyone holding the `anon` key, which is by design public. UpGuard's framing: "data leaks are the multiplicative product of a technology's ease of misconfiguration and the size of its user base," and it explicitly names AI coding tools writing migrations as the reason the second factor has grown — the report calls Supabase "the most recommended database product by Claude Code."

Geographically, European projects were less likely to leak (UpGuard credits data-protection law), and the exposed set skews towards ecommerce and restaurant apps (payment data) and unlicensed betting sites (passwords). UpGuard's report also collects the smaller prior measurements — Matt Turner's Lovable finding (CVE-2025-48757, March 2025), Modern Pentest's 28 % of 107 YC startups, Symbiotic's 39 of 1,072 apps, Escape's 175 databases in ~1,400 apps, Red Access's ~5,000 accessible apps in 380,000 URLs, and Wiz's Moltbook 1.5 M-token leak — so this is the sixth independent measurement of the same mechanism in eighteen months, at ten to a hundred times the sample size.

Supabase's statement to TechCrunch (CISO Bil Harmer): projects are "secure by default," security is "a shared responsibility between the company and its customers," and "Security at Supabase is never finished. We care deeply about getting it right, and we'll keep making it easier for every developer to ship securely." Neither the UpGuard report nor TechCrunch records a change to the programmatic-table default.

## Am I affected?

You are in the exposed population if **any** of these is true:

1. Your app's client bundle contains a Supabase project URL and `anon` key (it does — that is how Supabase works) **and** at least one table was created outside the Table Editor without an explicit `ALTER TABLE … ENABLE ROW LEVEL SECURITY`.
2. An AI tool (Lovable, Bolt, v0, Replit, Claude Code, Cursor, Copilot) wrote your schema or migrations. UpGuard's report and this repo's own [Lovable/Supabase findings](ongoing-vibe-platform-exposure.md) both show generated migrations routinely omit RLS.
3. You enabled RLS but wrote **no policies**, or wrote a permissive `USING (true)` policy to "make it work."

Check every table in one query from the SQL editor (the Supabase dashboard's Security Advisor lints the same thing):

```sql
select schemaname, tablename, rowsecurity
from pg_tables
where schemaname = 'public' and rowsecurity = false;
```

Any row returned is a table PostgREST will serve to the `anon` role subject only to the role's grants — and the default grants on `public` are broad. Then confirm from the outside, with your own project's public values (this is your own system, not someone else's):

```bash
curl -s "https://<your-project>.supabase.co/rest/v1/users?select=*&limit=1" \
  -H "apikey: <your anon key>" -H "Authorization: Bearer <your anon key>"
```

A JSON array with a row in it is the exposure UpGuard measured. Also grep your repo for the `service_role` key — it bypasses RLS entirely and must never reach a client bundle or a committed `.env`.

## If you are affected

1. **Enable RLS on every public table now** (`alter table public.<t> enable row level security;`). With no policies this blocks all `anon` access immediately; the app may break, which is the correct failure direction. Then add scoped policies (`auth.uid() = user_id`), not `USING (true)`.
2. **Assume the data was read.** UpGuard's scan was one of many; the `anon` key has been in your bundle since launch. If passwords were stored in your own tables (rather than Supabase Auth), force resets; if tokens, revoke them. → [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) for the disclosure and triage order.
3. **Rotate any `service_role` key that was ever in client code or git history** → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. Run the full checklist in → [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md); RLS is the first item because it is the one that leaks whole tables.

## Prevention

- **Treat "RLS on" as part of the migration, not a dashboard setting.** Every `create table` in a migration gets `enable row level security` and at least one policy in the same file, so a regenerated schema cannot silently regress. Put it in the prompt for whichever AI tool writes your SQL ("every table must enable RLS with per-user policies") and in code review.
- **Lint for it in CI.** A query like the one above, run against a preview branch and failing the build on any `rowsecurity = false` row, is a five-line check. → [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- **Never store passwords in your own table** — use Supabase Auth; 884 plaintext passwords in one case study existed only because the app rolled its own.
- **Keep `service_role` server-side only** → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- Related pattern file, updated with each measurement: [ongoing-vibe-platform-exposure.md](ongoing-vibe-platform-exposure.md).

## Sources
- [UpGuard — Everything, Everywhere: Systemic Data Exposure in Supabase Apps](https://www.upguard.com/blog/everything-everywhere-systemic-data-exposure-in-supabase-apps) — primary, 2026-09-25 (Greg Pollock): the ~300,000-domain corpus, the BuiltWith + Chrome UX Report method, the `users`-table probe, the 16,326 figure, the PII / password / card breakdown, the five case studies, the prior-research table, the Table-Editor-vs-API RLS default. Fetched 2026-09-26.
- [TechCrunch — Some Supabase customers are publicly exposing reams of people's data to the web](https://techcrunch.com/2026/09/25/some-supabase-customers-are-publicly-exposing-reams-of-peoples-data-to-the-web/) — 2026-09-25 (Zack Whittaker): independent write-up with Supabase CISO Bil Harmer's statement quoted verbatim, the valet / adult-site / consulate / SIM-farm examples, the $10 B valuation context. Fetched 2026-09-26.
- [Unite.AI — UpGuard Study Finds 16,326 Supabase Databases Exposing Readable Tables](https://www.unite.ai/upguard-study-finds-16-326-supabase-databases-exposing-readable-tables/) — 2026-09-25: restates the report's methodology and counts; used to cross-check the numbers above, not as an independent source. Fetched 2026-09-26.
- Not fetched: Cybernews and other syndications (403 / paraphrase only). No Supabase blog post on the study existed at sweep time; the vendor statement is as carried by TechCrunch.
- Related in this corpus: [ongoing-vibe-platform-exposure](ongoing-vibe-platform-exposure.md) (the pattern file; Lovable CVE-2025-48757, Base44, Red Access), [Supabase Realtime presence / broadcast bypasses](2026-06-supabase-realtime-presence-read-rls-bypass.md) (the RLS-bypass sibling on the realtime path).
