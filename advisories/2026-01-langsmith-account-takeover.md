---
id: 2026-01-langsmith-account-takeover
title: "LangSmith CVE-2026-25750 unvalidated baseUrl → account takeover (January 2026)"
date_disclosed: 2026-01-07
last_updated: 2026-06-03
severity: high
status: patched
ecosystems: [pypi, ai-agents, langchain]
tools_affected: [langsmith, langchain, langsmith-sdk]
tags: [cve, ssrf, account-takeover, ai-agent-framework, session-token, unvalidated-redirect, langchain]
---

## TL;DR
**CVE-2026-25750** (CVSS 8.5) — LangSmith Studio's self-hosted dashboard allowed any authenticated user to set an arbitrary `baseUrl` parameter that the client used for API calls without validation. An attacker who can influence the `baseUrl` (via SSRF, prompt injection, or shared-workspace manipulation) can redirect session tokens to an attacker-controlled server — **full account takeover without credential theft**. Companion **CVE-2026-25528** is an SSRF via the distributed tracing header. LangSmith cloud was silently patched **December 20, 2025**; self-hosted deployments need upgrade to **0.12.71**.

## What happened
On **2026-01-07**, Miggo Research disclosed two chained vulnerabilities in LangSmith, LangChain's observability and tracing platform used by AI development teams to monitor LLM calls, trace agent runs, and share datasets.

### CVE-2026-25750 — Unvalidated `baseUrl` → session token exfil
LangSmith Studio (the React UI) reads a `baseUrl` configuration value and uses it as the host for all authenticated API calls — including those that carry the user's session token in headers. No origin validation was applied to this parameter. An attacker who can set or influence `baseUrl` (e.g., through a misconfigured shared workspace, a poisoned environment variable in a vibe-coded deployment, or a prompt-injected agent run that writes config) can point it at `https://attacker.example.com` — all subsequent API calls deliver the victim's session token to the attacker. **One token = full account access** — all traces, all datasets, all API keys stored in the workspace.

### CVE-2026-25528 — SSRF via distributed tracing header
The LangSmith tracing endpoint accepted a caller-controlled URL in the distributed tracing header without SSRF validation. An attacker-controlled value could cause the LangSmith backend to make outbound requests to internal infrastructure (cloud IMDS, internal services) and reflect the response back to the attacker — cloud credential theft from the LangSmith server's execution environment.

### Timeline
- **2025-12-20** — LangSmith cloud silently patched (no changelog entry at the time)
- **2026-01-07** — Miggo Research disclosed; CVE numbers assigned; NVD published
- **January 2026** — Self-hosted fix released in **LangSmith 0.12.71**

## Am I affected?

```bash
# Check self-hosted LangSmith version
pip show langsmith 2>/dev/null | grep -E '^(Name|Version):'
# Or check the LangSmith self-hosted container tag:
docker inspect <langsmith-container> 2>/dev/null | grep -i version

# Grep for baseUrl in any LangSmith config you control
grep -r "baseUrl\|base_url" ~/.langchain/ .langsmith* langsmith.env 2>/dev/null
```

**Self-hosted LangSmith < 0.12.71** is vulnerable. LangSmith cloud users are patched (as of 2025-12-20) but should audit workspace sharing permissions regardless.

### IOCs

| Type | Value |
|---|---|
| CVE | `CVE-2026-25750` (account takeover, CVSS 8.5) |
| CVE | `CVE-2026-25528` (SSRF, lower CVSS) |
| GHSA | available via GitHub Advisory Database |
| Affected self-hosted versions | LangSmith < 0.12.71 |
| Fixed self-hosted version | LangSmith 0.12.71 |
| Cloud patched | 2025-12-20 (silent) |
| Attack primitive | Unvalidated `baseUrl` → session token exfil to attacker host |

## If you are affected
1. **Upgrade self-hosted LangSmith** to 0.12.71 immediately: update your Docker image / Helm chart to the patched tag.
2. **Rotate all session tokens / API keys** stored in the LangSmith workspace if you ran < 0.12.71 on an internet-accessible host or in a shared multi-tenant environment. Workspace API keys (which include upstream LLM provider keys if your team stored them in LangSmith datasets or environment configs) should be treated as potentially exfiltrated.
3. **Audit workspace sharing.** If you shared a LangSmith workspace with external collaborators, they had a potential attack surface for CVE-2026-25750.
4. **Check for unexpected outbound requests** from your LangSmith host in December 2025 / January 2026 (CVE-2026-25528 SSRF exploitation). Particularly look for requests to cloud IMDS endpoints (`169.254.169.254`, `fd00:ec2::254`).

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Any AI observability/tracing platform (LangSmith, AgentOps, Helicone, Portkey) that stores your LLM provider keys is a **high-trust hub** — a single account takeover exposes every upstream key. Treat these platforms with the same rigor as your secrets manager.
→ Pin `baseUrl` / API endpoints in config as constants, never as user-settable runtime parameters. If a parameter affects where authenticated requests go, it must be validated against a strict allowlist.

## Sources
- [Miggo Research — CVE-2026-25750: LangSmith Account Takeover via Unvalidated baseUrl](https://www.miggo.io/blog/cve-2026-25750-langsmith-account-takeover) — canonical discovery and PoC
- [The Hacker News — LangSmith Vulnerability Allows Account Takeover via SSRF Chain](https://thehackernews.com/2026/01/langsmith-vulnerability-allows-account.html)
- [Cybersecurity News — CVE-2026-25750: LangSmith Studio Session Token Exfiltration](https://cybersecuritynews.com/cve-2026-25750-langsmith-studio-session-token-exfiltration/)
- [NVD — CVE-2026-25750](https://nvd.nist.gov/vuln/detail/CVE-2026-25750)
- [GitHub Advisory Database — GHSA for LangSmith CVE-2026-25750](https://github.com/advisories?query=langsmith)
