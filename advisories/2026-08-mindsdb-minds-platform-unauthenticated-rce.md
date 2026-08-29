---
id: 2026-08-mindsdb-minds-platform-unauthenticated-rce
title: "MindsDB Minds Platform — unpatched CVSS 10.0 unauthenticated RCE via prompt injection, plus a separate patched file-upload RCE"
date_disclosed: 2026-08-14
last_updated: 2026-08-29
severity: critical
status: active
ecosystems: [pypi, mindsdb, ai-agent-frameworks]
tools_affected: [mindsdb, minds-platform, cowork-server]
tags: [cve, unauthenticated-rce, prompt-injection, eval-on-llm-output, path-traversal, ai-data-platform, central-credentials-cache]
---

## TL;DR
MindsDB's **Minds Platform** — an open-source "AI systems you can control" product for connecting agents to your own data, deployable self-hosted (VPC/on-prem/cloud) — shipped a **CVSS 10.0 unauthenticated remote code execution** flaw (**CVE-2026-73678**) where a single crafted prompt to an unauthenticated API endpoint reaches an agent's "scratchpad" tool, which runs attacker-supplied Python through a bare `exec()` with no sandbox. **As of this sweep, no patched version has been released.** A second, unrelated, already-patched vulnerability in the base MindsDB project (**CVE-2026-27483**, CVSS 8.8) lets an authenticated user path-traverse the file-upload endpoint to overwrite a pip internals file and get RCE the next time a handler is installed — fixed in 25.9.1.1.

## What happened

**CVE-2026-73678 — unauthenticated RCE via prompt injection into the scratchpad tool (GHSA-jcxw-h8ph-pxpv, unpatched).** MindsDB's `cowork-server` component (the FastAPI backend behind Minds Platform's project/conversation/agent orchestration layer) ships three compounding defects: (1) the entire API requires no authentication at all; (2) CORS is configured with a wildcard origin; and (3) the "Anton" agent's built-in scratchpad tool executes arbitrary Python via `exec(compiled, namespace)` with no sandboxing. The exploit chain needs no credentials whatsoever: an attacker first calls the unauthenticated `PUT /api/v1/settings/` endpoint to register their own LLM API key (so the platform will actually run their prompt), then `POST`s a crafted prompt to `POST /api/v1/responses/` instructing the agent to invoke the scratchpad tool with attacker-supplied Python source. That code runs with the OS-level privileges of the server process, exposing SSH keys, stored credentials, and environment secrets. This is a textbook instance of this repo's ["decorator/annotation-as-documentation"](2026-05-semantic-kernel-rce.md) and "eval-on-LLM-output" pattern classes — the tool boundary exists in name only, with no distinction between a developer's own trusted code and text an anonymous network caller typed into a prompt.

Independent trackers (VulnCheck, cve.threatint.com) confirm CVE-2026-73678 with matching CVSS 10.0, affected-version, and mechanism detail — **note a discrepancy worth flagging under this repo's accuracy bar**: MindsDB's own GitHub Security Advisory page (GHSA-jcxw-h8ph-pxpv) informally references "CVE-2026-73678" in its prose but its structured CVE field currently shows "No known CVE," while VulnCheck's advisory and multiple CVE-tracking aggregators list it as reserved/published. Treat the CVE number as correct (two independent third-party trackers agree on it) but be aware the vendor's own structured metadata hasn't caught up. **Affected: Minds Platform ≤ 26.1.0. No patched version exists as of 2026-08-29** — this is a live, actively-exploitable, unauthenticated CVSS 10.0 hole with no fix to upgrade to.

**CVE-2026-27483 — authenticated path-traversal RCE via file upload (GHSA-4894-xqv6-vrfq, patched 25.9.1.1).** Separately, in the base `mindsdb/mindsdb` project (not `minds-platform`), the `/api/files` endpoint fails to validate filenames in multipart form uploads, letting an authenticated attacker inject `../` traversal sequences to write arbitrary files anywhere on the server. The disclosed exploitation path overwrites pip's own initialization module; when the platform's dependency-installation feature (used when installing a new handler) subsequently shells out to pip, the attacker's payload executes via the resulting subprocess call — arbitrary-file-write escalated to RCE through a normal, expected platform feature. CVSS 8.8. **Affected: MindsDB ≤ 25.9.1.0, fixed in 25.9.1.1** (the fix uses `pathlib.Path` for proper path handling and bumps the `python-multipart` dependency from 0.0.18 to 0.0.20).

The two CVEs affect different repositories in the MindsDB org (`minds-platform`'s `cowork-server` vs. the core `mindsdb` project) but reinforce the same lesson already tracked across this repo's "AI/data tools shipping unauthenticated network RCE primitives" cluster (Langflow, PraisonAI, Marimo, LiteLLM, Flowise, MLflow): a tool that sits in the middle of an AI/data architecture — holding LLM provider keys, database credentials, and file-system access — is only as safe as its weakest exposed endpoint, and "authenticated" is not a given even for the primary API surface.

## Am I affected?

```bash
# Minds Platform (cowork-server) — check your deployed version
# You are affected if you self-host Minds Platform <= 26.1.0 with the API
# reachable from any untrusted network (including your LAN or a Docker
# bridge network other containers can reach) — there is currently NO PATCH.
curl -s -o /dev/null -w "%{http_code}\n" http://<your-minds-host>:<port>/api/v1/settings/
# A 200/2xx response with no auth prompt confirms the unauthenticated surface is reachable.

# Base MindsDB — check your installed version
pip show mindsdb 2>/dev/null | grep Version
# You are affected if version <= 25.9.1.0. Upgrade to >= 25.9.1.1.
```

If you run Minds Platform self-hosted and cannot fully firewall it off from untrusted networks, treat it as compromised risk until a patch ships — there is no configuration flag documented that closes this off short of network isolation.

## If you are affected
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — rotate any credentials reachable from the host running Minds Platform or MindsDB
→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)
- Never expose an AI-agent orchestration server's API to an untrusted network by default — require authentication and bind to `127.0.0.1` or a private network segment until the vendor ships one.
- Treat any tool that executes LLM-selected or LLM-generated code (a "scratchpad," "code interpreter," or "sandbox" tool inside an agent framework) as a code-execution primitive first and a convenience feature second — verify it actually sandboxes execution rather than trusting the name.
- For self-hosted MindsDB, upgrade to ≥ 25.9.1.1 now; for Minds Platform, monitor for a patch and isolate the service on an untrusted network in the meantime.

## Sources
- [MindsDB — GitHub Security Advisory GHSA-jcxw-h8ph-pxpv](https://github.com/mindsdb/minds-platform/security/advisories/GHSA-jcxw-h8ph-pxpv) — fetched directly: vendor's own description of the unauthenticated-RCE-via-scratchpad chain, CVSS 10.0, root causes, no patched version listed.
- [VulnCheck — MindsDB Minds Platform Unauthenticated RCE via Scratchpad exec()](https://vulncheck.com/advisories/mindsdb-minds-platform-unauthenticated-rce-via-scratchpad-exec) — fetched directly: independent confirmation of CVE-2026-73678, CVSS 10.0, affected version, disclosure date 2026-08-14.
- [cve.threatint.com — CVE-2026-73678](https://cve.threatint.com/CVE/CVE-2026-73678) — fetched directly: CVSS 3.1/4.0 both 10.0, GHSA/VulnCheck/NVD reference links, publish/reserve/update dates.
- [MindsDB — GitHub Security Advisory GHSA-4894-xqv6-vrfq](https://github.com/mindsdb/mindsdb/security/advisories/GHSA-4894-xqv6-vrfq) — fetched directly: CVE-2026-27483, CVSS 8.8, path-traversal-to-RCE-via-pip-overwrite mechanism, patched 25.9.1.1.
