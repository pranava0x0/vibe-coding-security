---
id: 2026-11-coder-november-seven-advisories-aws-iam-database-password-in-api-errors-cli-session-token
title: "Coder: seven advisories from 2026-11-04 to 11-12; unauthenticated API errors could leak an AWS IAM database password (8.1); fixed 2.39.1, 2.38.7, 2.37.11"
date_disclosed: 2026-11-11
last_updated: 2026-11-13
severity: high
status: patched
ecosystems: [coder, go, cloud-dev-environment, ai-agents]
tools_affected: ["Coder (github.com/coder/coder/v2) before 2.39.1, 2.38.7, 2.37.11, 2.34.19 and 2.29.27", "Coder deployments with CODER_PG_AUTH=awsiamrds", "the `coder open app` CLI command", "Coder Agents workspace skills (read_skill_file)", "Coder dashboards that show agent-supplied app status links", "end-of-life Coder lines 2.30 to 2.33, 2.35 and 2.36 (no patch)"]
tags: [coder, ghsa-batch, cloud-dev-environment, credential-leak, session-token, csrf, denial-of-service, agent-skills, symlink, prompt-injection-surface, patched, no-cve]
---

## TL;DR
Coder published seven advisories between 2026-11-04 and 2026-11-12, none with a CVE. The one rated High (GHSA-w4m3-qhx8-c649, vendor 8.1): on deployments that use AWS IAM database authentication, a failed database connection put the connection URL, with its temporary password, into API error responses that unauthenticated requests could trigger. Releases 2.39.1, 2.38.7, 2.37.11, 2.34.19 and 2.29.27, all dated 2026-11-10 on the Go module proxy, carry the fixes for all seven. The newest advisories list no patch for lines 2.30 to 2.33 and 2.35, which the vendor calls end-of-life, and most list none for 2.36.

## What happened

The vendor tab (`coder/coder`, five pages, of which pages 1 and 2 were read) showed seven rows dated 2026-11-04 to 2026-11-12 when read on 2026-11-13. Earlier Coder advisories are in [the Coder home file](2026-09-coder-registry-cloudflare-terraform-supply-chain.md). All seven pages print "No known CVE".

| GHSA | Published | Vendor score | What it is | First fixed releases |
|---|---|---|---|---|
| GHSA-w4m3-qhx8-c649 | 2026-11-11 | 8.1 High | AWS IAM database password in API errors and logs | 2.39.1, 2.38.7, 2.37.11, 2.34.19, 2.29.27 |
| GHSA-6g9g-vmp7-r45p | 2026-11-11 | 6.1 | `coder open app` sends the session token to template app URLs | 2.39.1, 2.38.7, 2.37.11, 2.34.19, 2.29.27 |
| GHSA-5wcx-v9qj-4gj6 | 2026-11-11 | 4.6 | Agent-supplied app status links can use unsafe URL schemes | 2.39.0, 2.38.7, 2.37.11, 2.34.19, 2.29.27 |
| GHSA-7hf9-gp2x-ppfm | 2026-11-12 | 6.5 | Any authenticated user can crash `coderd` with one tailnet message | 2.37.3, 2.36.7, 2.35.9, 2.34.12, 2.29.27 |
| GHSA-9h3q-h2rh-35gg | 2026-11-06 | 6.5 | Crafted workspace agent RPC calls crash `coderd` | 2.37.1, 2.36.5, 2.35.8, 2.34.10, 2.29.21 |
| GHSA-jvgx-787p-cfmg | 2026-11-04 | 4.2 | CSRF protection skipped for API paths matching unanchored patterns | 2.39.0, 2.38.6, 2.37.10, 2.34.18, 2.29.26 |
| GHSA-hm3r-4cg2-22xx | 2026-11-04 | 3.1 Low | Coder Agents `read_skill_file` follows symlinks out of the skill directory | 2.39.0, 2.38.5, 2.37.9, 2.36.12, 2.34.17 |

Details the reader needs:

- **AWS IAM database password (GHSA-w4m3-qhx8-c649).** Only deployments with `CODER_PG_AUTH=awsiamrds` are affected, and only while Coder is failing to open new database connections, such as during an outage or failover. The advisory says "Coder returned this error in API responses, including to unauthenticated requests." The password is valid for 15 minutes. An attacker who can also reach the database over the network could read or change data, including user accounts and roles. The error was also written to server logs and CLI output. The vendor's workarounds, restricting database network access and limiting the database user, "limit the impact but don't prevent the password from appearing in errors".
- **CLI session token (GHSA-6g9g-vmp7-r45p).** `coder open app` replaced `$SESSION_TOKEN` in an external app's URL with the user's real session token wherever the URL pointed. A template author could collect the tokens of users who ran the command on that app. The dashboard path was fixed earlier under GHSA-2x8w-q434-f76p. Credits include Anthropic's Security Team and Ada Logics.
- **Agent status links (GHSA-5wcx-v9qj-4gj6).** A process holding the agent token, including an AI agent manipulated through prompt injection in the advisory's words, could show an unsafe link to anyone viewing the workspace or task. The dashboard's Content Security Policy blocks `javascript:` links from running script. The fix keeps only `http`, `https` and `file` links, and applies to new status updates only.
- **Two crashes (GHSA-7hf9-gp2x-ppfm, GHSA-9h3q-h2rh-35gg).** Availability only. The first needs any authenticated user and, since 2.18.0, no workspace access. The second needs an agent token.
- **CSRF (GHSA-jvgx-787p-cfmg).** A same-site page, such as a workspace app on the wildcard access URL, could make a signed-in user's browser send some state-changing requests. The advisory says deployments started with `--samesite-auth-cookie none` "can be attacked from any website".
- **Skill symlink (GHSA-hm3r-4cg2-22xx).** A malicious skill in the victim's workspace could return a file outside the skill directory to the model. The read stays inside what the workspace agent's user can already read. Line 2.29 is not affected.

The Go module proxy dates v2.39.1, v2.38.7, v2.37.11, v2.34.19 and v2.29.27 to 2026-11-10 between 14:20 and 15:10 UTC, and v2.39.0 to 2026-11-03.

## Am I affected?

```bash
coder version                      # server and client versions
env | grep -E '^CODER_PG_AUTH='    # awsiamrds = the High advisory applies
ps aux | grep -E 'samesite-auth-cookie[ =]none'   # widens the CSRF advisory
```

- Below 2.39.1 on 2.39, below 2.38.7 on 2.38, below 2.37.11 on 2.37, below 2.34.19 on 2.34, or below 2.29.27 on 2.29: at least one of the seven applies.
- On 2.30 to 2.33, 2.35 or 2.36: affected by the newer advisories with no patch on that line. The table shows the last patch each line received.
- For the database password: check server logs and CLI output from any database outage for a connection URL.
- For the CLI token: review templates for external app URLs that contain `$SESSION_TOKEN`.

## If you are affected

1. Upgrade to the patched release on your line. Move off end-of-life lines.
2. If you use `awsiamrds` and had a database outage or failover on an affected version, review database audit logs for that window and check user accounts and roles for changes. The temporary password expires, but changes made with it do not.
3. If users ran `coder open app` against templates you do not fully trust, have them sign out to end their sessions, and delete their API tokens. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) covers what a workspace owner's session can reach.
4. Restart workspaces after the upgrade so they run the updated agent. The skill-symlink advisory says `read_skill_file` fails on workspaces running an older agent until they restart.

## Prevention

- [Agent sandboxing](../prevention/agent-sandboxing.md): treat anything an agent can write into a dashboard, a status link or a skill directory as untrusted input.
- Keep the database reachable only from Coder, and give its user the least privilege that works.
- Install skills only from sources you trust, and review skill directories for symbolic links.
- Keep the default `--samesite-auth-cookie lax`.

## Sources

Single source: the vendor, for its own product.

- [coder/coder security advisories tab](https://github.com/coder/coder/security/advisories), pages 1 and 2, fetched 2026-11-13: the seven rows and their dates.
- [GHSA-w4m3-qhx8-c649](https://github.com/coder/coder/security/advisories/GHSA-w4m3-qhx8-c649), fetched 2026-11-13: score, ranges, conditions, quoted sentences, workarounds.
- [GHSA-6g9g-vmp7-r45p](https://github.com/coder/coder/security/advisories/GHSA-6g9g-vmp7-r45p), fetched 2026-11-13: score, ranges, mechanism, credits.
- [GHSA-5wcx-v9qj-4gj6](https://github.com/coder/coder/security/advisories/GHSA-5wcx-v9qj-4gj6), fetched 2026-11-13: score, ranges, the prompt-injection sentence, the fix's scope.
- [GHSA-7hf9-gp2x-ppfm](https://github.com/coder/coder/security/advisories/GHSA-7hf9-gp2x-ppfm), fetched 2026-11-13: score, ranges, conditions.
- [GHSA-9h3q-h2rh-35gg](https://github.com/coder/coder/security/advisories/GHSA-9h3q-h2rh-35gg), fetched 2026-11-13: score, ranges, conditions.
- [GHSA-jvgx-787p-cfmg](https://github.com/coder/coder/security/advisories/GHSA-jvgx-787p-cfmg), fetched 2026-11-13: score, ranges, the quoted sentence, end-of-life lines.
- [GHSA-hm3r-4cg2-22xx](https://github.com/coder/coder/security/advisories/GHSA-hm3r-4cg2-22xx), fetched 2026-11-13: score, ranges, conditions.
- [Go module proxy version list for github.com/coder/coder/v2](https://proxy.golang.org/github.com/coder/coder/v2/@v/list), read 2026-11-13 with the per-version `.info` records: release times.
