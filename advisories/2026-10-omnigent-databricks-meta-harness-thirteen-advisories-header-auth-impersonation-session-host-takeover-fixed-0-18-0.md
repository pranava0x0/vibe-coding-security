---
id: 2026-10-omnigent-databricks-meta-harness-thirteen-advisories-header-auth-impersonation-session-host-takeover-fixed-0-18-0
title: "Omnigent, the Databricks meta-harness for coding agents: thirteen advisories since June, default header auth impersonation and session-host takeover; upgrade to 0.18.0"
date_disclosed: 2026-10-14
last_updated: 2026-10-18
severity: critical
status: patched
ecosystems: [pypi, ai-agents, agent-orchestration, self-hosted, python]
tools_affected: ["omnigent before 0.18.0 (PyPI), every multi-user server", "omnigent before 0.7.0 bound to a non-loopback address with no auth provider configured", "omnigent 0.3.0 through 0.13.0 accepting uploaded bundles on runners with sandbox.type none", "Claude Code, Codex, Cursor, OpenCode, Hermes and Pi sessions run through an Omnigent host"]
tags: [cve, authentication-bypass, authorization-bypass, path-traversal, rce, policy-bypass, sandbox-escape, agent-orchestration, multi-tenant, databricks, vulncheck, github-cna, zero-file-product]
---

## TL;DR

Omnigent, the open-source "meta-harness for all your AI agents" that Databricks publishes on PyPI and that runs Claude Code, Codex, Cursor, OpenCode, Hermes and Pi sessions on hosts you connect to it, has thirteen vendor advisories on its security tab dated 2026-06-29 to 2026-10-14. Five carry CVE ids. The two that matter most for anyone running a multi-user server: before 0.7.0 the default authentication mode trusted a client-supplied `X-Forwarded-Email` header, so anyone who could reach the server could be any user (GHSA-x6v6-fg8x-997h, 9.4, published 2026-10-14 for a fix shipped 2026-07-27), and before 0.18.0 an authenticated user who learned another user's host identifier could import a session onto that host and run an agent under the other user's operating-system account (GHSA-rqfc-q7j9-5v59, 9.9, published 2026-10-13). The rest are a bundle-upload family (an uploaded agent's working directory, terminal, sub-agent, Python callable tools, YAML `function:` policy and source tools each reached the runner's host filesystem or ran code as the runner) and a policy family (the shell parser and the Git policy that are meant to confine an agent to a repository, branch and working directory could be stepped around). Everything listed is fixed in `omnigent` 0.18.0, published 2026-10-13. An upgrade is the whole fix for the authentication and policy items. Uploaded agents that used Python or TypeScript source tools stop working on multi-user servers after 0.18.0 and have to move those tools to MCP.

The repository had no file here. The product surfaced on 2026-10-18 because VulnCheck assigned CVE-2026-112015 to the September sub-agent advisory and the record landed on the advisory database's `agent` listing. The tab had been publishing for sixteen weeks.

## What happened

Omnigent (`omnigent-ai/omnigent`, 10.9k stars, Apache-2.0, Python 3.12 or newer, PyPI author "Databricks, Inc.") is an orchestration layer that stores agent bundles, starts sessions on connected hosts and sandboxes, and applies policies to what the agent may run. Its multi-user server mode is where every advisory below applies. The June advisory on the shell parser says the report went "privately to Databricks by email on June 16, 2026", which is the only place the vendor's name appears on the tab.

### Authentication and tenant isolation

- **GHSA-x6v6-fg8x-997h (2026-10-14, Critical, 9.4, `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L`, CWE-290).** Header authentication read the user's identity from `X-Forwarded-Email`, or from the header named by `OMNIGENT_AUTH_HEADER`, without checking that the request came from a trusted proxy and without binding it to a session or token. Header mode was the default whenever `OMNIGENT_AUTH_PROVIDER` was unset and multi-user auth was not enabled, so a server that was never configured for accounts was exposed as shipped. Any client that could reach the server could read other users' sessions, transcripts and workspaces, post events as them, and reach administrative routes if an admin identity was guessable. Affected before 0.7.0, verified by the reporter in 0.5.1. Fixed in 0.7.0 (PR #3107, PyPI 2026-07-27): a server bound to a non-loopback address now enables accounts authentication by default, the deploy templates set `OMNIGENT_AUTH_ENABLED=1`, and header mode is reserved for deployments behind an SSO proxy that strips the client's copy of the header. The advisory states the finding is source analysis with no runtime test. Reporter TahirMars. The advisory was published eleven weeks after the fix.
- **GHSA-rqfc-q7j9-5v59 (2026-10-13, Critical, 9.9, `AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`, CWE-284, CWE-863).** Session imports did not consistently check that the importing user owned the selected host. A user who obtained another user's host identifier, which the advisory says may be visible to anyone who can view a shared session, could link an imported session to that host and run an agent under the other user's operating-system account, with everything that account can reach. Affected 0.13.0.dev20260902 up to but not including 0.18.0. Fixed in 0.18.0, which verifies host ownership on import and on replacement. Reporter Rea1mindxRing.

### Uploaded bundles reaching the runner

All of these need an authenticated user who can upload or edit an agent bundle on a multi-user server. The vendor states that trusted single-user and local operation, where the operator already controls the code, is outside the threat model.

| Advisory | Published | Score | What the bundle could do | Affected | Fixed |
|---|---|---|---|---|---|
| GHSA-jrrm-9hc7-2v3h, CVE-2026-62674 | 2026-06-29 (CVE 2026-08-21, GitHub CNA) | 9.0 | `PUT /sessions/{id}/agent` accepted a replacement bundle for a shared or template agent; a stdio MCP server added there ran as the runner in every later session using that agent | before 0.3.0 | 0.3.0 (2026-06-27) |
| GHSA-756x-9hf6-q4h4, CVE-2026-62675 | 2026-06-29 | 8.8 | server-side Python callable tool definitions in an uploaded bundle were imported and executed by the runner | before 0.3.0 | 0.3.0 |
| GHSA-p8rw-8qj3-hf33, CVE-2026-62677 | 2026-06-29 | 8.8 | the root agent's `os_env.cwd` was stored verbatim; on a runner without `OMNIGENT_RUNNER_WORKSPACE` it became the environment root, with host filesystem read and write | before 0.3.0 for the root agent | 0.3.0 for the root path, 0.14.0 for the rest |
| GHSA-598r-29w2-g93q | 2026-09-16 | 9.9 | a terminal's `os_env.cwd` skipped the upload check and took precedence over the runner-provided workspace at runtime; with `sandbox.type: none` that is an unconfined host shell; `OMNIGENT_RUNNER_WORKSPACE` does not help here | 0.3.0 through 0.13.0 | 0.14.0 (2026-09-15, PR #7457) |
| GHSA-p5x3-3gqh-x44g, CVE-2026-112015 | 2026-09-16 (CVE 2026-10-18, VulnCheck) | 8.8 vendor; VulnCheck 7.7 (4.0) and 7.5 (3.1) | a nested sub-agent's `os_env.cwd` skipped the same check, so a value rejected at the root was accepted one level down | 0.3.0 through 0.13.0 | 0.14.0 |
| GHSA-q5jc-8hqr-9hm4 | 2026-09-16 | 8.8 | the single-file YAML bundle path checked `handler` and `callable` keys against the allowlist and not `function`, so a `function:` policy imported and called any Python target at session start, before the LLM did anything | 0.13.0 and earlier | 0.14.0 |
| GHSA-jw77-57v9-jmcm | 2026-10-13 | 8.8 | Python tool discovery ran uploaded source tools while building tool schemas, before the isolation that applies to later tool calls | 0.3.0 up to 0.18.0 | 0.18.0, which rejects uploaded Python and TypeScript source tools on multi-user servers |

The 0.14.0 fix validates working directories on the root agent, every terminal and every nested sub-agent and terminal, and rejects absolute and parent-traversing paths in POSIX and Windows forms on the untrusted upload path. It does not change terminal runtime precedence; the boundary is enforced at upload. The 0.14.0 release note says only "Improved validation of uploaded agent settings". The 0.18.0 release note has no security line at all.

### Policies that were meant to confine the agent

- **GHSA-7mqg-cx4g-x2rf, CVE-2026-62676 (2026-06-29, High, 7.1, CWE-184).** The shared shell-command parser in `policies/builtins/_shell.py` produced no operation for command forms it did not recognise, the evaluator treated that as abstain, and abstain resolved to allow. A confined agent, misaligned or prompt-injected, could push to a repository or branch outside the allowlist or leave its working directory. Fixed in 0.3.0. Reported by aaronjmars, credited as the Aeon autonomous security agent.
- **GHSA-m3m2-42jg-grrv (2026-10-13, High, 7.6 on CVSS 4.0, CWE-184).** The GitHub and working-directory policies could fail to apply to some shell commands. 0.18.0 (PR #9844) improves parsing and requires policy handling for syntax that cannot be classified. Reporter fg0x0.
- **GHSA-h6vq-3549-mppq (2026-10-13, High, 8.3, CWE-184).** The built-in GitHub policy misclassified Git commands that carried global options, so repository and branch restrictions could be skipped. Affected 0.1.0 up to 0.18.0. Reporters manus-pi and manus-use.
- **GHSA-v3vj-mch3-x6c2 (2026-10-13, High, 8.8 local, CWE-668, CWE-732).** On Linux with the bubblewrap sandbox, helper executors had access to host temporary files that should have stayed outside the sandbox; code inside the sandbox could compromise the launcher and run as the account running Omnigent. Fixed in 0.18.0 (PR #9844), which removes the broad temporary-directory grants and rejects sandbox configurations that expose the launcher's directory. Reporter sfwani.

Four of the thirteen name the same two reporters (manus-pi and manus-use), the pair that reported the GitSpawn and Orval clusters tracked here in September.

### Dates

Fix 0.3.0 shipped 2026-06-27 and the four June advisories were published two days later; the GitHub CNA records for them are dated 2026-08-21. Fix 0.7.0 shipped 2026-07-27 and its advisory was published 2026-10-14. Fix 0.14.0 shipped 2026-09-15 and its three advisories were published the next day. Fix 0.18.0 shipped 2026-10-13, the same day as its five advisories. VulnCheck's CVE-2026-112015 record is dated 2026-10-18, for a bug fixed thirty-three days earlier.

## Am I affected?

- You run `omnigent server` for more than one person, or on a host other users can reach. Check the version:

```bash
pip show omnigent | grep -i ^version     # anything below 0.18.0 carries at least one open item above
python3 -c "import omnigent, importlib.metadata as m; print(m.version('omnigent'))"
```

- If the server ever ran a version below 0.7.0 bound to a non-loopback address with `OMNIGENT_AUTH_PROVIDER` unset and `OMNIGENT_AUTH_ENABLED` unset, every user's sessions and transcripts were readable and writable by anyone who could reach the port, with no log line that distinguishes a forged identity from a real one. Treat them as read.
- If any user can upload bundles and a runner runs with `sandbox.type: none`, a version from 0.3.0 through 0.13.0 let an uploaded terminal or sub-agent reach the runner's host filesystem. `OMNIGENT_RUNNER_WORKSPACE` being set does not clear the terminal path.
- If you still run `OMNIGENT_AUTH_PROVIDER=header` after 0.7.0, confirm that the reverse proxy strips an inbound identity header before it injects its own, and that the server is not reachable except through that proxy.
- Imported sessions: after upgrading, list sessions whose host does not belong to the importing user and stop any that should not be there.

## If you are affected

1. Upgrade to `omnigent` 0.18.0 or later on the server and on every agent host, then restart agent processes and helper executors. The vendor's own command form: `uv tool install --upgrade --python 3.12 'omnigent==0.18.0'`.
2. If the server was reachable below 0.7.0 without accounts auth, rotate every credential an Omnigent session could use: the provider keys in `claude-sdk` OAuth profiles, GitHub and `gh` tokens the sandbox authenticates with, and whatever the connected hosts hold. Review sessions and events for identities you do not recognise. [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) covers the host side.
3. If untrusted users could upload bundles on a runner below 0.14.0 with `sandbox.type: none`, treat that runner's host account as compromised: rebuild it, and rotate what it could read. [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. Move custom tools in uploaded agents from Python or TypeScript source tools to MCP, upload the corrected bundle, and start new sessions. Uploading a replacement does not change sessions already running.
5. Until the upgrade lands, the vendor's interim advice is to limit uploads and edits to trusted operators, disconnect sensitive hosts from multi-user servers, restrict agent shell access, and run untrusted agents in a disposable VM or container with no host credentials or mounts.

## Prevention

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — the harness's policy layer is not the sandbox; three of the thirteen advisories are the policy parser letting a command through, and one is the sandbox launcher itself.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — a shared agent host holds every user's provider and Git credentials; scope them per user and per session so one forged identity does not read them all.
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — the June critical was a stdio MCP server smuggled into a shared agent bundle; treat an MCP entry in a bundle you did not write as code.

## Sources

- [omnigent-ai/omnigent security advisories, page 1](https://github.com/omnigent-ai/omnigent/security/advisories) and [page 2](https://github.com/omnigent-ai/omnigent/security/advisories?page=2) — vendor tab, fetched 2026-10-18: thirteen rows, dates and severities as listed above.
- [GHSA-x6v6-fg8x-997h — default header authentication trusts client-controlled X-Forwarded-Email](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-x6v6-fg8x-997h) — vendor advisory, published 2026-10-14, fetched 2026-10-18: 9.4, affected before 0.7.0, default-mode statement, PR #3107, source-only analysis note, reporter.
- [GHSA-rqfc-q7j9-5v59 — session imports can use another user's host without authorization](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-rqfc-q7j9-5v59) — vendor advisory, published 2026-10-13, fetched 2026-10-18: 9.9, affected range, fix in 0.18.0.
- [GHSA-598r-29w2-g93q — per-terminal os_env.cwd bypasses the uploaded-bundle workspace guard](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-598r-29w2-g93q) — vendor advisory, published 2026-09-16, fetched 2026-10-18: 9.9, `OMNIGENT_RUNNER_WORKSPACE` not a mitigation, PR #7457.
- [GHSA-p5x3-3gqh-x44g — uploaded bundle's sub-agent os_env.cwd escapes workspace containment](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-p5x3-3gqh-x44g) — vendor advisory, published 2026-09-16, fetched 2026-10-18: 8.8, the related-advisory list, reporters.
- [GHSA-q5jc-8hqr-9hm4 — single-file YAML function policy key bypasses handler allowlist](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-q5jc-8hqr-9hm4) — vendor advisory, published 2026-09-16, fetched 2026-10-18.
- [GHSA-h6vq-3549-mppq — Git commands can bypass repository and branch policies](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-h6vq-3549-mppq), [GHSA-jw77-57v9-jmcm — uploaded source tools can execute code with runner privileges](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-jw77-57v9-jmcm), [GHSA-m3m2-42jg-grrv — shell commands can bypass configured agent policies](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-m3m2-42jg-grrv), [GHSA-v3vj-mch3-x6c2 — sandbox launcher isolation failure permits host-level code execution](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-v3vj-mch3-x6c2) — vendor advisories, published 2026-10-13, fetched 2026-10-18: scores, ranges, PR #9844, the source-tool migration note.
- [GHSA-jrrm-9hc7-2v3h](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-jrrm-9hc7-2v3h), [GHSA-756x-9hf6-q4h4](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-756x-9hf6-q4h4), [GHSA-p8rw-8qj3-hf33](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-p8rw-8qj3-hf33), [GHSA-7mqg-cx4g-x2rf](https://github.com/omnigent-ai/omnigent/security/advisories/GHSA-7mqg-cx4g-x2rf) — vendor advisories, published 2026-06-29, fetched 2026-10-18: the four June findings, the "reported privately to Databricks" line, the 0.14.0 follow-up note on the cwd family.
- [CVE-2026-112015 — CNA record (VulnCheck)](https://cveawg.mitre.org/api/cve/CVE-2026-112015) — fetched 2026-10-18: published 2026-10-18, 7.7 (4.0) and 7.5 (3.1), references the vendor advisory, the fix commit and the v0.14.0 release, credits George Chen and manus-pi.
- [CVE-2026-62674](https://cveawg.mitre.org/api/cve/CVE-2026-62674) and [CVE-2026-62677](https://cveawg.mitre.org/api/cve/CVE-2026-62677) — CNA records (GitHub), fetched 2026-10-18: published 2026-08-21, the mechanism sentences quoted above, fix PRs #1418 and #1417.
- [GitHub Advisory Database — query `omnigent`](https://github.com/advisories?query=omnigent+sort%3Apublished-desc) and [query `agent`, sorted by publication](https://github.com/advisories?query=agent+sort%3Apublished-desc) — fetched 2026-10-18: the five CVE rows, and the 2026-10-18 row that surfaced the product.
- [omnigent-ai/omnigent releases](https://github.com/omnigent-ai/omnigent/releases) and [v0.14.0](https://github.com/omnigent-ai/omnigent/releases/tag/v0.14.0) — fetched 2026-10-18: release dates, the one validation line in 0.14.0, no security line in 0.18.0.
- [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent) — repository page, fetched 2026-10-18: description, 10.9k stars, install commands, Python 3.12 requirement.
- [PyPI JSON — omnigent](https://pypi.org/pypi/omnigent/json) — fetched 2026-10-18: author "Databricks, Inc.", upload dates 0.3.0 2026-06-27, 0.7.0 2026-07-27, 0.14.0 2026-09-15, 0.18.0 2026-10-13.
