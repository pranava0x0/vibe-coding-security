---
id: 2026-06-supabase-realtime-presence-read-rls-bypass
title: "Supabase Realtime ≤ 2.111.1: a private-channel client allowed `presence.write` but denied `presence.read` still received every other member's presence metadata — location, online status, rosters, typing indicators (CVE-2026-62247, CVSS 6.5); vendor advisory 2026-06-25, fixed 2.111.2 (2026-06-23), CVE published 2026-09-21"
date_disclosed: 2026-06-25
last_updated: 2026-09-24
severity: high
status: ongoing
ecosystems: [supabase, realtime, elixir, websocket, self-hosted]
tools_affected: ["Supabase Realtime ≤ 2.137.14 (GHSA-9vjf-j9f7-j42c, unpatched as of 2026-09-24)", "Supabase Realtime server <= 2.111.1 (self-hosted / docker-compose deployments)", "any app using Realtime Presence on private channels with a presence-read policy stricter than its presence-write policy", "Supabase-scaffolded apps with 'members can join, only admins see the roster' presence designs"]
tags: [cve, authorization-bypass, rls, supabase, realtime, presence, data-exposure, websocket, self-hosted]
---

## TL;DR
**CVE-2026-62247** (GitHub CNA, published to NVD **2026-09-21**, CVSS 3.1 **6.5** Medium) is a Realtime Authorization bug in **Supabase Realtime ≤ 2.111.1**: the server "did not correctly honor per-extension RLS policies `presence.read` under specific conditions." A client on a **private channel** whose policy allowed `presence.write` but **explicitly denied `presence.read`** still received `presence_diff` messages, which "contain every other member's presence metadata" — whatever the app tracks in presence state: live location, who is online, "currently viewing" rosters, typing indicators tied to user ids. Confidentiality only; `postgres_changes` row data and broadcast are unaffected; apps where presence read and write are granted uniformly have no differential and are not exposed. Found by Cipher / Causal Security; fixed in **2.111.2** (released **2026-06-23**, "ensure presence.read permission is respected"), vendor advisory published **2026-06-25**. The CVE arrived three months later — if you self-host Realtime, check the image tag, not the news.

## What happened

**The mechanism.** Supabase Realtime Authorization gates private channels with Row Level Security policies on the `realtime.messages` table, evaluated per *extension* — `broadcast` and `presence` — and per operation (a `SELECT` policy grants read, an `INSERT` policy grants write). The supported-but-uncommon shape is a channel where members may *publish* their own presence but only some members may *see* the roster: "members may chat, but only admins may see the roster," in the advisory's words. Before 2.111.2, a client authorised for `presence.write` and denied `presence.read` was still sent the `presence_diff` events the server emits when members join, leave or update their state, so the denied client received the full presence payload of every other member on the channel.

**The vendor's framing (GHSA-rcr8-2525-4r7p).** "Realtime Authorization did not correctly honor per-extension RLS policies `presence.read` under specific conditions." Impact: any presence metadata the application treats as restricted leaks "to every presence-write-authorized member of a private channel." The advisory is explicit about the boundary: no integrity or availability impact, `postgres_changes` unaffected, and no exposure "where `presence.read` is uniform." CWE-863 Incorrect Authorization; affected `<= 2.111.1`, patched `>= 2.111.2`; reporter credited as cipher-creator, "Found by Cipher / Causal Security."

**The fix and the dates.** Release **v2.111.2** landed on **2026-06-23** with one line under Bug Fixes — "ensure presence.read permission is respected (#1969)" — two days *before* the advisory was published on the vendor repo (2026-06-25). The release note does not mention the advisory or a CVE; the link between them is the advisory's patched-version field. NVD's record (`CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`) is dated **2026-09-21**, and the GitHub Advisory Database had not yet mirrored the vendor advisory when this was written (the `github.com/advisories/GHSA-rcr8-2525-4r7p` URL returned 404; the `supabase/realtime` repo URL resolves). The recurring shape: a CVE date is not a disclosure date, and the vendor tab is where the real one lives.

**Who this reaches.** Supabase's hosted platform runs Realtime on its own upgrade schedule and the advisory does not state when hosted projects moved past 2.111.1; the actionable population is **self-hosters** (the official docker-compose stack pins a `supabase/realtime` image tag) and anyone who forked the server. The at-risk *design* is common in exactly the apps this audience ships: a "live cursors / who's online" feature bolted onto a Supabase app where the roster is supposed to be admin-only, or presence state that carries a user's location or the document they are viewing.

**Why it matters for vibe coders.** Supabase is the default backend of the AI-scaffolded stack, and Realtime Presence is the feature an assistant reaches for when asked for "show who's online." Presence state is arbitrary JSON the client publishes — assistants routinely put user ids, display names, emails, current page, geolocation in it. RLS is the control everyone is told to rely on ([Supabase MCP lethal trifecta](2025-07-supabase-mcp-lethal-trifecta.md), [Supabase Auth OIDC bypass](2026-03-supabase-auth-oidc-bypass.md)); this is a case where a correctly written policy was not enforced by the component that was supposed to apply it. Medium severity, narrow precondition, but the failure mode — "the policy said no and the server sent it anyway" — is the one that invalidates a whole class of "RLS protects it" reasoning until the server is patched.

## Am I affected?

- **Affected if:** you run Supabase Realtime **≤ 2.111.1** (self-hosted) **and** at least one private channel has a presence policy where write is allowed and read is denied for some members (differential presence visibility).
- **Not affected if:** Realtime ≥ 2.111.2; presence read and write are granted to the same set of members; you only use public channels or only broadcast / `postgres_changes`.

```bash
# Self-hosted: which Realtime image is running?
grep -n "supabase/realtime" docker-compose.yml          # image tag < v2.111.2 = affected
docker ps --format '{{.Image}}' | grep realtime

# Do you have a differential presence policy? Look for presence policies on realtime.messages
# where a SELECT (read) policy is narrower than the INSERT (write) policy.
psql "$DATABASE_URL" -c "select policyname, cmd, qual, with_check from pg_policies where schemaname='realtime' and tablename='messages';"

# Grep the app for presence payloads that carry sensitive fields
grep -rn "\.track(" --include=*.ts --include=*.tsx --include=*.js . | grep -v node_modules
```

## If you are affected

1. **Upgrade Realtime to ≥ 2.111.2** (bump the image tag, restart; hosted projects: confirm with Supabase support if you rely on differential presence policies).
2. Assume that, for the window your deployment ran an affected version, every presence-write-authorised member of a differential channel could see every other member's presence state. If that state carried location, viewing activity or identifiers you treat as private, evaluate it as a disclosure ([auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md) covers the data-inventory step).
3. Reduce what presence carries: publish a short opaque id and resolve names/locations server-side behind an authorised query, rather than pushing the sensitive fields into the presence payload itself.

## Prevention

- **Keep presence payloads minimal.** Presence state fans out to every reader by design; a policy bug (this one) or a design slip (uniform read) exposes all of it. Put identifiers in, keep PII out.
- **Track the vendor's advisory tab for every self-hosted Supabase component** — `supabase/realtime`, `supabase/auth`, `supabase/storage-api`, `supabase/postgrest` — not only the `supabase/supabase` repo, whose tab is empty; the CVE for this bug lagged the fix by three months.
- **Pin and update self-hosted images on a schedule.** The docker-compose stack pins tags; a pinned tag that never moves is a pinned vulnerability. [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- Test authorization negatively: for each private channel policy, join as a denied user and assert the events do *not* arrive — the advisory's bug is invisible to positive-path tests.

## Update 2026-09-24 — a second, worse Realtime bug, published today with **no patched version**: any broadcaster can splice raw bytes into every other subscriber's JSON frame and forge `postgres_changes` events — on public channels with only the anon key (GHSA-9vjf-j9f7-j42c, CVSS 8.2)

On **2026-09-24** the `supabase/realtime` maintainers (published by edgurgel) opened **[GHSA-9vjf-j9f7-j42c](https://github.com/supabase/realtime/security/advisories/GHSA-9vjf-j9f7-j42c)** — "Client-supplied bytes are spliced unvalidated into other subscribers' JSON frames, letting any broadcaster forge Realtime protocol events (including `postgres_changes`) to every other client on the channel." **High, CVSS 3.1 8.2**, CWE-20 / CWE-116, affected **≤ 2.137.14**, **patched versions: none listed**, reporter Elias Hasas (`@zer0d4y5`). No CVE yet, and the GitHub releases page shows `v2.137.15` through `v2.138.1` on 2026-09-23 with no security note.

**Mechanism, per the advisory.** The **binary broadcast** path (`decode_binary/1`) accepts the client's payload without parsing it. When the server re-serialises the message for subscribers on the **V1 serializer**, it wraps those bytes in a `Jason.Fragment`, which the JSON encoder inserts verbatim into the outgoing envelope — so a broadcaster who sends a payload that closes the broadcast object and continues with attacker-chosen top-level fields rewrites the frame every other client receives. Because of Erlang map iteration order "all fields except `topic` can be overwritten." Consequences the advisory spells out: **forged `postgres_changes` notifications** "with attacker-controlled schema, table, operation, and record data — requiring no database write permissions"; forged `phx_close` messages that make subscribers "silently stop receiving channel events"; and unparseable JSON that throws in victim clients. **V2-serializer subscribers are protected** by length-prefixed binary framing. And the authorization boundary is the part that matters for this audience: "On a public channel no authorization of any kind is involved: the anon key is published in every client bundle by design, and public channels run with `policies: nil`" — so anyone who can read your bundle can broadcast, and anyone who can broadcast can make every connected client believe a row was inserted, updated or deleted.

**What this means.** A React/Next.js front end that subscribes to `postgres_changes` to update a cart, a dashboard, a chat thread or an order status — the standard Supabase pattern — will render attacker-fabricated rows, and an app that *acts* on those events (sends an email, marks an order shipped, updates local state that later gets written back) is driven by them. The bug is in the server, so it reaches Supabase-hosted projects as well as self-hosters; the advisory does not say whether hosted Realtime has been updated, and there is no version to check against because none is listed as fixed. This file's status moves to **`ongoing`** and severity to **`high`** on that basis; it will return to `patched` when a fixed release is named.

**Until a fix ships:** (1) do not let clients broadcast on channels where other clients consume `postgres_changes` — use separate channels for client broadcast and for database changes, and make the `postgres_changes` channels private with RLS policies that deny `broadcast` writes; (2) prefer the V2 serializer in clients where the SDK exposes it; (3) never let a `postgres_changes` event trigger a write or an external action without re-reading the row from the database; (4) self-hosters, watch `supabase/realtime` releases for the fix and pin to it the day it lands.

## Sources
- [supabase/realtime — GHSA-rcr8-2525-4r7p: Incorrect Authorization in supabase/realtime](https://github.com/supabase/realtime/security/advisories/GHSA-rcr8-2525-4r7p) — vendor advisory, published 2026-06-25: the `presence.read` / `presence.write` differential, the `presence_diff` leak, the confidentiality-only scope, "members may chat, but only admins may see the roster," affected `<= 2.111.1` / patched `>= 2.111.2`, CVSS 3.1 6.5, CWE-863, credit to Cipher / Causal Security. (The `github.com/advisories/…` mirror URL returned 404 on 2026-09-22.) Fetched 2026-09-22.
- [NVD API — CVE-2026-62247](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-62247) — published 2026-09-21, source `security-advisories@github.com`, CVSS 3.1 6.5 `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`, description matching the vendor advisory. Fetched 2026-09-22.
- [supabase/realtime — release v2.111.2](https://github.com/supabase/realtime/releases/tag/v2.111.2) — 2026-06-23, Bug Fixes: "ensure presence.read permission is respected (#1969)"; no advisory or CVE reference in the notes. Fetched 2026-09-22.
- [GitHub Advisory Database — advisories matching `supabase`, newest first](https://github.com/advisories?query=supabase+sort%3Apublished-desc) — the listing that did *not* yet carry this advisory on 2026-09-22 (it surfaced through a `Supabase security advisory` search and the NVD record instead). Fetched 2026-09-22.
- Related in this corpus: [Supabase MCP lethal trifecta](2025-07-supabase-mcp-lethal-trifecta.md) and [Supabase Auth OIDC issuer-validation bypass (CVE-2026-31813)](2026-03-supabase-auth-oidc-bypass.md).
- **2026-09-24 update sources** — [supabase/realtime — GHSA-9vjf-j9f7-j42c](https://github.com/supabase/realtime/security/advisories/GHSA-9vjf-j9f7-j42c) (vendor advisory, published 2026-09-24: title, CVSS 8.2, affected `≤ 2.137.14`, no patched version, the `decode_binary/1` / `Jason.Fragment` mechanism, V1-vs-V2 serializer scope, the public-channel/anon-key sentence, the forged-event, `phx_close` and malformed-JSON impacts, reporter). Fetched 2026-09-24. [supabase/realtime — releases](https://github.com/supabase/realtime/releases) (fetched 2026-09-24: v2.137.16 → v2.138.1 all dated 2026-09-23, none mentioning the advisory). Single-source as of 2026-09-24 — the vendor's own advisory; no CVE, no database mirror, no independent write-up yet.
