---
id: 2026-08-swe-agent-inspector-path-traversal
title: "SWE-agent trajectory inspector — unauthenticated path traversal on an all-interfaces, wildcard-CORS server leaks trajectory files holding repo contents and API keys (CVE-2026-75482, unpatched)"
date_disclosed: 2026-08-17
last_updated: 2026-09-13
severity: high
status: active
ecosystems: [pypi, python, swe-agent, ai-agent-framework]
tools_affected: ["SWE-agent (sweagent)", "sweagent inspector"]
tags: [cve, path-traversal, unauthenticated, cors, bind-all-interfaces, credential-exposure, agent-framework, unpatched, cwe-22]
---

## TL;DR

**SWE-agent** ships a web viewer for the JSON "trajectory" files its agent runs produce — `sweagent inspector` — and that viewer is an HTTP server that **binds every interface, sets `Access-Control-Allow-Origin: *`, requires no login, and joins whatever path you give `/trajectory/` onto the trajectory directory without rejecting `..`**. Anyone on the network, or any web page the developer opens (via CORS), can read trajectory-shaped JSON files anywhere on the host. Trajectories contain what the agent saw and did: repository contents, command output, and — because runs are configured with model keys and tokens in the environment — **API keys and secrets**. Reported on GitHub **2026-07-19**, a fix PR opened **2026-08-15**, **CVE-2026-75482** published by VulnCheck as CNA on **2026-08-17** (CVSS 4.0 **8.7** / 3.1 **7.5**). As of 2026-09-13 the issue is open, the PR is unmerged, and SWE-agent has no published security advisory. Affected: **every release through 1.1.0**.

## What happened

GitHub user **geo-chen** — the same reporter behind [aider's `.aider.conf.yml` auto-exec bug](2026-09-aider-conf-yml-command-execution.md) — opened [SWE-agent/SWE-agent#1472](https://github.com/SWE-agent/SWE-agent/issues/1472) on 2026-07-19: *"Path traversal in the trajectory inspector reads off-path trajectory/JSON files (unauthenticated, all-interfaces bind, wildcard CORS)."* The `/trajectory/` handler in `sweagent/inspector/server.py` takes the request path, joins it to the served trajectory directory, and never checks that the result is still inside it; the built-in sanitization does not reject parent-directory segments. Three configuration choices turn a local viewer bug into a network one: the server binds **`0.0.0.0`**, answers every origin with a **wildcard CORS** header, and has **no authentication**. The read sink parses the target as trajectory JSON, so disclosure is limited to JSON files with a trajectory-like shape — which, per VulnCheck's advisory, "can contain repository contents, command output, and secrets/API keys."

VulnCheck published the finding as **CVE-2026-75482** on **2026-08-17** (CVSS 4.0 `AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N` = 8.7; CVSS 3.1 7.5; CWE-22), affected **≤ 1.1.0**, no patched version, no mitigation listed. NVD carries the same scores and lists the PyPI package `sweagent` **v0 through v1.1.0**; the GitHub Advisory Database mirrored it as **GHSA-hpx7-jm9p-88gh** the same day, unreviewed, with no package or version range filled in. The project's own security-advisories tab says *"There aren't any published security advisories."*

A community fix exists and has been waiting for a month. [PR #1505](https://github.com/SWE-agent/SWE-agent/pull/1505) (Chessing234, opened 2026-08-15) adds a `resolve_trajectory_path()` that rejects `..` segments — including percent-encoded variants — and absolute paths that escape the served directory, **binds `127.0.0.1` by default** with an explicit `--host` flag for deliberate network exposure, drops the unconditional wildcard CORS header, and adds nine regression tests (Codecov reported 92% patch coverage). Its last recorded activity is the bot comment on the day it opened.

Why it belongs in this feed: SWE-agent is one of the reference agent-orchestration frameworks, run routinely on shared research boxes and CI hosts, and the inspector is *the* way people look at what a run did. A trajectory is a complete transcript of an agent with credentials operating on a repository. Exposing that directory to the LAN — and to any web page via CORS — is the [Deadbugz](2026-09-deadbugz-mcp-supply-chain-campaign.md)/[Grafana MCP](2026-08-agent-framework-mcp-cve-batch.md) pattern from the other side: not an agent being fed bad input, but an agent's *output* being an unauthenticated network service by default.

## Am I affected?

```bash
pip show sweagent 2>/dev/null | grep -i '^version'    # any version ≤ 1.1.0 is affected; no fixed release exists
# Is the inspector up, and on what interface?
ps aux | grep -iE 'sweagent (inspector|/inspector)' | grep -v grep
ss -tlnp | grep -i python | grep -v '127.0.0.1'         # inspector bound to 0.0.0.0 shows here
# What could be read: any trajectory-shaped JSON reachable from the served directory upward
find / -name '*.traj' -o -name 'trajectory*.json' 2>/dev/null | head
```

If the inspector ran bound to all interfaces on a host that is reachable from other machines — or from a browser that visited untrusted pages while it was running — assume every trajectory on that host has been read, and treat any key that appears in a trajectory as leaked.

## If you are affected

1. Stop the inspector; run it only on loopback until a release includes PR #1505 or equivalent (`ssh -L` to it if you need it from elsewhere). Do not put it behind a "just for the team" wildcard.
2. Rotate every credential that appears in a trajectory the server could reach — model API keys, `GITHUB_TOKEN`s, anything the agent's environment held: [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md), [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) — the trajectory *is* the agent's session record; read it as the attacker would have.

## Prevention

- [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — keys that reach an agent's environment end up in its logs. Scope and rotate them; never let a long-lived token be the thing a trajectory captures.
- [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — treat agent artefacts (trajectories, transcripts, tool outputs) as sensitive by default and keep viewers for them off the network.
- This repo's standing observation for smaller AI-coding tools ([aider](2026-09-aider-conf-yml-command-execution.md) is the sibling case): **no advisory channel means no advisory** — the GitHub issue and the CNA record are the disclosure. Watch the tracker, not the (empty) security tab, and keep such tools on `latest`.

## Sources

- [VulnCheck Advisory — SWE-agent Trajectory Inspector Path Traversal File Disclosure (CVE-2026-75482)](https://www.vulncheck.com/advisories/swe-agent-trajectory-inspector-path-traversal-file-disclosure) — fetched 2026-09-13; the CNA record: CVSS 4.0 vector and 8.7 score, affected ≤ 1.1.0, no patched version, reporter geo-chen, the `0.0.0.0` / wildcard-CORS / no-auth description, what trajectory files contain.
- [NVD — CVE-2026-75482](https://nvd.nist.gov/vuln/detail/CVE-2026-75482) — fetched via the NVD API 2026-09-13; published 2026-08-17, CVSS 4.0 8.7 and 3.1 7.5 from `disclosure@vulncheck.com`, CWE-22, `sweagent` v0–v1.1.0.
- [GitHub Advisory Database — GHSA-hpx7-jm9p-88gh (CVE-2026-75482)](https://github.com/advisories/GHSA-hpx7-jm9p-88gh) — fetched 2026-09-13; unreviewed mirror published 2026-08-17, no package or version range recorded.
- [SWE-agent/SWE-agent#1472 — Path traversal in the trajectory inspector](https://github.com/SWE-agent/SWE-agent/issues/1472) — fetched 2026-09-13; the reporter's issue, opened 2026-07-19, still open; mechanism and the three compounding server settings.
- [SWE-agent/SWE-agent#1505 — fix(inspector): reject off-directory trajectory paths, bind to loopback, drop wildcard CORS](https://github.com/SWE-agent/SWE-agent/pull/1505) — fetched 2026-09-13; unmerged fix opened 2026-08-15: `resolve_trajectory_path()`, loopback default with `--host`, CORS removal, nine regression tests.
- [SWE-agent — security advisories](https://github.com/SWE-agent/SWE-agent/security/advisories) — fetched 2026-09-13; "There aren't any published security advisories."
