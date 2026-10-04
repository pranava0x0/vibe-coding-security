---
id: 2026-07-trigger-dev-self-hosted-coordinator-default-secret-env-exfiltration
title: "Trigger.dev (the background-jobs platform common in Next.js/Supabase stacks) — four vendor advisories from July 2026 that reached the GitHub Advisory Database only on 2026-10-02: self-hosted V1 coordinator mounts a Socket.IO namespace behind a hardcoded, undocumented default secret, from which an attacker with network access decrypts every run's environment variables and forges task completions (GHSA-gg6r-gp4c-89hp, CVSS 4.0 9.2, fixed 4.5.4); `trigger.dev deploy --log-level debug` prints resolved secrets (5.5, fixed 4.5.9); two alert-webhook SSRFs to internal and metadata endpoints (7.7 / 5.4, fixed 4.5.2)"
date_disclosed: 2026-07-09
last_updated: 2026-10-04
severity: critical
status: patched
ecosystems: [npm, javascript, nextjs, self-hosted]
tools_affected: ["trigger.dev self-hosted webapp/coordinator < 4.5.4 (run engine V1)", "trigger.dev CLI ≤ 4.5.8 (debug deploy logs)", "trigger.dev webapp < 4.5.2 (alert-channel webhook SSRF)", "any app whose background jobs hold DB / Stripe / LLM keys in Trigger.dev env vars"]
tags: [ghsa, trigger-dev, background-jobs, hardcoded-secret, default-credential, socket-io, environment-variables, credential-theft, ssrf, cloud-metadata, cli-logs, self-hosted, database-lag]
---

## TL;DR

Trigger.dev is the open-source background-jobs / workflow runner that a large share of AI-generated Next.js and Supabase apps reach for when they need queues, cron, or long-running LLM calls — and whose runs are configured with the app's real secrets as environment variables. Its maintainers published **four security advisories between 2026-07-09 and 07-31**, all fixed within days on npm; the GitHub Advisory Database only reviewed and listed them on **2026-10-02**, which is when `npm audit` starts flagging them. The one that matters: **GHSA-gg6r-gp4c-89hp (Critical, CVSS 4.0 9.2, fixed 4.5.4 / npm 2026-07-14)** — in self-hosted deployments the run-engine **V1 coordinator** "mounts a Socket.IO coordinator namespace using a hardcoded default secret (`coordinator-secret`) that was never documented for self-hosted operators"; anyone who can reach the port authenticates with the published default and then, via two further flaws, "exfiltrate[s] decrypted environment variables from any run or forge[s] task completion messages across arbitrary runs." The others: the CLI's `deploy --log-level debug` serialises the build-worker options **with unredacted resolved env values** (GHSA-fj2x-mqqp-3v2w, 5.5, ≤ 4.5.8 → 4.5.9) — the non-debug output masks them, so people pasted debug logs into issues believing them safe; and the **alert-channel webhook URL** is stored and fetched with no SSRF check (GHSA-xxv7-2vv3-h682, High 7.7, and GHSA-q567-cr4x-96w4, 5.4; both fixed 4.5.2), letting any org member POST from the control plane to internal services and cloud metadata. Self-hosters: upgrade to ≥ 4.5.9, rotate every secret that was in a run's environment, and check whether the coordinator port was ever reachable. Cloud customers were patched by the vendor.

## What happened

**GHSA-gg6r-gp4c-89hp — V1 coordinator default-secret unauthenticated Socket.IO (published 2026-07-20, CVSS 4.0 9.2, affected < 4.5.4, fixed 4.5.4).** Three interconnected flaws in self-hosted deployments still running the V1 run engine: the coordinator namespace authenticated with a hardcoded default secret that self-hosting docs never told operators to change; with that in hand an attacker "with network access" could pull *decrypted* environment variables for any run, and forge completion messages for arbitrary runs (that is, make the platform believe a job succeeded and feed it attacker-chosen output). References: PR #4236, release v4.5.4. The secret was *default* rather than *leaked* — the same shape as [Obot's auth-off quickstart](2026-08-agent-framework-mcp-cve-batch.md) and LiteLLM's example master key: a value in the repository that every deployment shares unless someone knows to override it.

**GHSA-fj2x-mqqp-3v2w — CLI debug deployment logs expose resolved environment secret values (published 2026-07-31, CVSS 3.1 5.5 `AV:L/AC:L/PR:N/UI:R/S:U/C:H`, affected ≤ 4.5.8, fixed 4.5.9).** `trigger.dev deploy --env staging --dry-run --log-level debug` serialised the full build-worker options object, including database connection strings and credentials, "despite the non-debug output properly masking these values, creating a false sense of security." The practical exposure is every debug log attached to a support ticket, a GitHub issue, or a CI job's console. References: PR #4420, release v4.5.9.

**GHSA-xxv7-2vv3-h682 (High 7.7) and GHSA-q567-cr4x-96w4 (5.4) — webhook alert-channel SSRF (both published 2026-07-09, affected < 4.5.2 / ≤ 4.5.1, fixed 4.5.2).** The webapp accepted a webhook URL for alert channels "as a bare string without validation," with no private-IP, loopback or metadata-endpoint check at either input or fetch; a low-privilege organisation member could make the control plane issue POSTs to internal services and `169.254.169.254`, scan ports via timing, and reach state-changing internal endpoints. References: PR #4199, commit `34b1a18`, release v4.5.2.

**The dates.** npm: 4.5.2 ships 2026-07-09 (the SSRF fix, same day as the advisories), **4.5.4 on 07-14**, 4.5.9 on 07-30; latest line is 4.7.x. The vendor advisories are dated 07-09 → 07-31. The advisory-database entries are dated **2026-10-02**, which is why a sweep sorting by publication date sees a "new" Trigger.dev wave in October. Per this corpus's rule, this file is dated by the vendor's disclosure, not the database's.

**Why vibe coders should care.** A Trigger.dev run's environment is where the app's `DATABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, Stripe secret and LLM provider keys end up, because background jobs are the part of the app that talks to everything. Decrypting "environment variables from any run" is therefore the whole secret set, and forging task completions lets an attacker inject output into whatever the job feeds (a database write, an email send, an agent's next step). Self-hosting Trigger.dev is the documented path for teams that want to keep jobs off the vendor cloud — the same population that would not know a coordinator default secret existed.

## Am I affected?

```bash
# Self-hosted only for the coordinator bug; the CLI bug affects anyone who ran debug deploys.
npm ls trigger.dev @trigger.dev/sdk 2>/dev/null | grep -E 'trigger.dev@|sdk@'   # fixed: >= 4.5.9 (all four)
npm view trigger.dev time --json | grep -E '"4\.5\.(2|4|9)"'                   # 07-09 / 07-14 / 07-30

# Self-hosted: is the run engine V1 coordinator deployed, and is its port reachable beyond the webapp network?
docker compose ps 2>/dev/null | grep -i coordinator
grep -rn "COORDINATOR_SECRET\|coordinator-secret" docker-compose*.yml .env* 2>/dev/null   # default value present = exposed on < 4.5.4

# Did anyone paste a debug deploy log anywhere? Search CI logs / issue tracker for:
grep -rl "log-level debug" .github/workflows 2>/dev/null
```

## If you are affected

1. Upgrade `trigger.dev` and the self-hosted images to **≥ 4.5.9** (4.7.x current).
2. Self-hosters on < 4.5.4 with a reachable coordinator: **rotate every secret that was configured as a run environment variable** — database URLs, service-role keys, payment and LLM keys — and review job outputs from the exposure window for forged completions. [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. Set a unique coordinator secret and keep the coordinator port off any network the webapp's users can reach.
4. If a debug deploy log was ever shared: treat the values in it as leaked and rotate them.
5. If untrusted org members existed on < 4.5.2: check the webapp's outbound logs for POSTs to internal ranges; rotate instance credentials if the metadata endpoint was reachable.

## Prevention

- Default credentials in a self-hosted control plane are a vulnerability class, not a configuration oversight; before deploying any job runner, grep its compose files for `*-secret`, `changeme` and `admin` literals and set every one. [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- Masking in normal output and not in debug output is a recurring CLI failure; never attach `--log-level debug` output to a public issue without a secrets scan. [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- Any user-supplied webhook URL is an SSRF primitive: validate at input *and* at fetch (DNS rebinding), block link-local and private ranges, and use IMDSv2 on AWS hosts.
- Dependency scanners only flag what the advisory database carries; a vendor tab can be three months ahead. For platforms that hold your secrets, watch the vendor's `security/advisories` tab directly.

## Sources

- [triggerdotdev/trigger.dev — GHSA-gg6r-gp4c-89hp: V1 coordinator default-secret unauth Socket.IO](https://github.com/advisories/GHSA-gg6r-gp4c-89hp) — vendor advisory published 2026-07-20 (database 2026-10-02): Critical, CVSS 4.0 9.2, the `coordinator-secret` default, the env-var exfiltration and task-completion forgery chain, affected < 4.5.4, patched 4.5.4, PR #4236. Fetched 2026-10-04.
- [triggerdotdev/trigger.dev — GHSA-fj2x-mqqp-3v2w: Trigger CLI debug deployment logs expose resolved environment secret values](https://github.com/advisories/GHSA-fj2x-mqqp-3v2w) — published 2026-07-31: CVSS 3.1 5.5 with vector, the `deploy --env staging --dry-run --log-level debug` reproduction, "false sense of security" wording, ≤ 4.5.8 → 4.5.9, PR #4420. Fetched 2026-10-04.
- [triggerdotdev/trigger.dev — GHSA-xxv7-2vv3-h682: Server-side request forgery via unvalidated webhook alert-channel URL](https://github.com/advisories/GHSA-xxv7-2vv3-h682) (High 7.7, < 4.5.2, low-privilege org member, metadata endpoint) and [GHSA-q567-cr4x-96w4: Blind SSRF via alert-channel webhook](https://github.com/advisories/GHSA-q567-cr4x-96w4) (5.4, `AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N`, ≤ 4.5.1 → 4.5.2, PR #4199, commit `34b1a18`) — both published 2026-07-09. Fetched 2026-10-04.
- [GitHub Advisory Database — `agent`, sorted by published date](https://github.com/advisories?query=agent+sort%3Apublished-desc) and the [reviewed-critical npm list](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Anpm+severity%3Acritical) — the three trigger.dev entries dated 2026-10-02 (the listing that surfaced this batch). Fetched 2026-10-04.
- npm registry `time` for `trigger.dev` (queried 2026-10-04): 4.5.3 2026-07-10, **4.5.4 2026-07-14**, 4.5.8 2026-07-27, **4.5.9 2026-07-30**; newest releases 4.7.0 – 4.7.2 (September 2026). No CVE ids assigned to any of the four as of 2026-10-04 (NVD keyword query on `trigger.dev`, 10-01 → 10-04: none).
- Related in this corpus: [n8n September 30 batch](2026-09-n8n-september-30-ten-advisory-batch.md) (the other self-hosted automation platform where the AI/agent surface and the credential store coincide), [Obot auth-off quickstart in the MCP batch](2026-08-agent-framework-mcp-cve-batch.md).
