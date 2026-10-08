---
id: 2026-06-langgraph-rce-chain
title: "LangGraph RCE chain — SQLite SQL injection + msgpack deserialization → arbitrary code execution (June 2026)"
date_disclosed: 2026-06-09
last_updated: 2026-10-08
severity: critical
status: patched
ecosystems: [pypi, ai-agents]
tools_affected: [langgraph, langgraph-checkpoint-sqlite, langgraph-checkpoint-redis, LangSmith self-hosted, any app built on LangGraph with user-controlled filter input]
tags: [rce, sql-injection, deserialization, ai-agents, langchain, self-hosted, credential-theft]
---

## TL;DR

Security researcher Yarden Porat discovered a two-CVE chain in **LangGraph** that allows any attacker who can supply a filter query to a self-hosted LangGraph deployment to achieve **arbitrary code execution on the server**. CVE-2025-67644 (SQL injection in the SQLite checkpoint) feeds attacker-controlled serialized data into CVE-2026-28277 (unsafe msgpack deserialization), yielding RCE. A third CVE (CVE-2026-27022) covers the Redis-checkpointer variant. **LangChain's managed LangSmith Deployment is NOT affected**; self-hosted deployments are. Fix: upgrade `langgraph-checkpoint-sqlite ≥ 3.0.1` and `langgraph ≥ 1.0.10`.

## What happened

In **June 2026**, researcher Yarden Porat published a vulnerability chain in **LangGraph** (the LangChain-backed framework for building stateful multi-agent AI applications, ~98M+ downloads/month across the LangChain ecosystem).

### CVE-2025-67644 — SQL injection in SQLite checkpoint (CVSS 7.3)

`langgraph-checkpoint-sqlite < 3.0.1` passes user-controlled metadata filter keys directly into SQL queries without parameterization. An attacker who can reach the `get_state_history()` endpoint with attacker-controlled filter input can inject arbitrary SQL, including modifying the query to return a fabricated checkpoint row whose `checkpoint` column contains attacker-controlled binary data.

### CVE-2026-28277 — Unsafe msgpack deserialization (CVSS 6.8)

`langgraph < 1.0.10` deserializes checkpoint BLOBs using msgpack without type restrictions. When the application loads a checkpoint, it calls the deserializer on the BLOB — which can reconstruct arbitrary Python objects, including those with `__reduce__` hooks that execute code at reconstruction time.

### The chain

1. Attacker crafts a malicious msgpack payload containing a Python object that executes arbitrary code on deserialization.
2. Attacker sends a request to `get_state_history()` with a malicious filter key that exploits CVE-2025-67644 to inject a fake checkpoint row into the SQLite query result.
3. The fake row's `checkpoint` column contains the attacker's malicious msgpack blob.
4. When the application processes the result, LangGraph deserializes the blob via CVE-2026-28277 — executing the attacker's payload on the server.

### CVE-2026-27022 — RediSearch query injection (CVSS 6.5)

A parallel variant affects the Redis checkpointer: user-controlled filter keys are injected into RediSearch queries, enabling retrieval of other tenants' checkpoint data (information disclosure / partial escalation path to deserialization if combined with CVE-2026-28277).

### Why this matters for vibe coders

LangGraph is the backbone of the modern multi-agent vibe-coding stack. Self-hosted LangGraph deployments:
- Store every agent's state (conversation, tool outputs, intermediate reasoning) in checkpoints
- Often hold upstream LLM provider keys (Anthropic, OpenAI, AWS Bedrock) in adjacent environment variables
- Typically run with broad filesystem and network access so agents can use tools

A single RCE on a self-hosted LangGraph server is effectively **a cloud-account compromise** for any org where the LangGraph process holds provider keys.

## Am I affected?

```bash
# Check installed versions
pip show langgraph langgraph-checkpoint-sqlite langgraph-checkpoint-redis

# Vulnerable if:
# langgraph < 1.0.10
# langgraph-checkpoint-sqlite < 3.0.1
# (Redis checkpointer users: any version using user-controlled filter keys)

# Check if your deployment exposes get_state_history() with user-controlled input:
grep -r "get_state_history" . --include="*.py" | grep -v "test_"
```

**You are affected if:**
- You run a **self-hosted LangGraph server** (not LangSmith's managed cloud)
- You use the `SQLite` or `Redis` checkpointer
- Any user-supplied value reaches the `metadata_filter` parameter of `get_state_history()` or equivalent

LangChain's **managed LangSmith Deployment** is NOT affected.

## If you are affected

1. **Upgrade immediately**: `pip install "langgraph>=1.0.10" "langgraph-checkpoint-sqlite>=3.0.1"`
2. **Rotate all credentials** reachable from the LangGraph server process (LLM provider API keys, cloud IAM, database credentials).
3. **Check server logs** for unexpected `get_state_history` calls with unusual filter values (SQLi attempts often produce SQL syntax errors in logs).
4. **Apply network segmentation** — LangGraph servers should never be publicly reachable without authentication.
5. **Enforce authentication** on all LangGraph server endpoints before deploying to production.

## Prevention

- Deploy LangGraph behind authentication middleware — no unauthenticated access to any checkpoint endpoint.
- Treat LangGraph server credentials (LLM API keys in env vars) as privileged secrets; rotate on any suspected compromise.
- Never pass user-controlled values directly into LangGraph `metadata_filter` parameters without sanitization.
- Monitor for unexpected checkpoint reads in server logs.

## Update — 2026-09-15: three more LangChain/LangGraph advisories from the vendor's own index (June–August 2026), none covered by press

Walking the `langchain-ai/langgraph` and `langchain-ai/langchain` security-advisory tabs directly — the practice this repo adopted for Cursor and Claude Code — turned up three advisories published after this file's original write-up. All are vendor-published; none had aggregator coverage.

- **`langgraph-sdk` — GHSA-fvww-7h3r-vfhp** (High, CVSS 7.6, CWE-863; published 2026-08-28; **no CVE assigned**). In the Python SDK's custom-auth system, a decorator such as `@auth.on.threads(actions=["create"])` was meant to register a handler for the listed actions only; the `actions=` argument was **silently ignored**, so the handler ran for *every* action on that resource — and because resource-scoped handlers take precedence over broader fallbacks, the per-action denial the developer wrote elsewhere never ran. Per the advisory, "an authenticated user may therefore be able to perform actions the application intended to deny, such as reading, updating, or deleting another user's resource." Affects **0.1.45 – 0.4.3**; fixed **0.4.4**. Only Python deployments using `actions=` on `@auth.on.threads`, `@auth.on.assistants` or `@auth.on.crons` are exposed — which is the multi-tenant pattern the docs show. Reporter: Grg0rry. No CVE means no `pip-audit` hit; check the version by hand.
- **`langgraph-checkpoint-postgres` / `langgraph-checkpoint-sqlite` — CVE-2026-71433 / GHSA-47pj-3jcm-6whg** (Moderate, CVSS 5.3; 2026-07-30). Store namespaces are persisted as dot-joined strings and matched with `LIKE` without segment awareness, so a read scoped to `("foo",)` also returned `("foobar",)` and `("foo2",)`, and unescaped `_` / `%` in labels widened matches further. Applications using namespaces as **tenant or user boundaries** could leak memories across them; writes were unaffected. Fixed **3.1.1** for both packages (segment-aware matching, metacharacter escaping, `GLOB` in SQLite). Reporter: VuxNx.
- **`langchain` / `langchain-anthropic` — CVE-2026-55443 / GHSA-gr75-jv2w-4656** (Moderate, CVSS 5.1, CWE-22/59; 2026-06-12). The file-search middleware validated the starting directory but not the search pattern (globs and symlinks escaped the root), configuration loaders did not confine resolved paths, and prefix checks compared strings without segment boundaries — "when these components receive path values influenced by untrusted sources including LLMs acting on untrusted input, the result can be disclosure of files outside the intended boundary." `langchain` ≤ 1.3.8 → **1.3.9**; `langchain-anthropic` ≤ 1.4.5 → **1.4.6**. Reporters: Mistz1, deprrous.

None of these changes this file's status; the RCE chain above remains patched. The shape is the one this repo keeps meeting in agent frameworks: authorization and path confinement implemented as string operations on values the model can influence.

## Update — 2026-10-04: LangGraph's JavaScript/TypeScript custom authentication may not apply Store authorization at all (GHSA-4hm6-w6qq-w73v, CVSS 8.6, published 2026-09-28) — `langgraph-api` 0.1.2 – 0.14.x, fixed 0.15.0

[GHSA-4hm6-w6qq-w73v](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-4hm6-w6qq-w73v) (vendor advisory, 2026-09-28, High 8.6, credit coinspect-audits): LangGraph deployments that use **JavaScript/TypeScript custom authentication** "may fail to apply Store authorization changes," so an authenticated user reaches Store data outside their authorized namespace. The failing pattern is an authorization handler that *rewrites* the requested namespace to the caller's own rather than *rejecting* the request — the rewrite was not honoured. Affected `langgraph-api` ≥ 0.1.2 < 0.15.0; fixed 0.15.0. Workaround until upgrade: change every Store handler to reject unauthorized namespaces instead of rewriting them, for every Store action the deployment exposes. The Store is where agent memory lives (per-user facts, conversation state, tool results), so this is cross-tenant memory read/write in multi-user agent apps — the same class as the 09-15 `langgraph-sdk` decorator bug and the checkpoint `LIKE` namespace bug above, now in the JS runtime. Python deployments are not named as affected. File status unchanged.

## Update — 2026-10-08: a new SDK v3 streaming path-traversal advisory (GHSA-3fx2-cqw9-xr3c, 4.3; `langgraph` 1.2.3 – 1.2.13 → 1.2.14, `langgraph-sdk` 0.4.0 – 0.4.5 → 0.4.6)

Published on the LangGraph tab on **2026-10-07** (no CVE at fetch time; reporter Evelynkaz; CWE-22): the SDK v3 streaming client inserts `thread_id` and `assistant_id` into request paths **without encoding them**, so an application that passes attacker-controlled text as one of those identifiers lets relative path segments redirect an authenticated GET to another readable path on the same configured server, returning that response to the app; `thread_id` additionally lets the attacker control the query string. Read-only (no writes), and the managed LangGraph Platform is unaffected. Fixed in **`langgraph-sdk` 0.4.6** (and `langgraph` 1.2.14 if using `RemoteGraph`). Low severity (4.3), but it is the fourth SDK-layer authorization/path bug in this file in a month — the pattern is that the client libraries keep shipping identifier-handling that trusts application-supplied strings. Status unchanged (`patched`).

## Update — 2026-10-05: the SDK `actions=` bug tracked in the 09-15 update now has a CVE — CVE-2026-104873 (GitHub CNA, published 2026-10-02; CVSS 4.0 7.6), `langgraph-sdk` 0.1.45 – 0.4.3, fixed 0.4.4, vendor advisory dated 2026-08-28

The 09-15 update above listed [GHSA-fvww-7h3r-vfhp](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-fvww-7h3r-vfhp) as "no CVE." GitHub, as CNA, published **CVE-2026-104873** on **2026-10-02** with the same title ("LangGraph SDK custom auth silently ignores actions= on resource decorators"), the same range (`langgraph-sdk` ≥ 0.1.45, < 0.4.4) and the same vector (`CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N`, 7.6); the CNA record's references are the GHSA, the fix commit and the `sdk==0.4.4` release tag, so the pairing is the vendor's own. The mechanism, restated from the record: `@auth.on.threads`, `@auth.on.assistants` and `@auth.on.crons` "ignore the actions argument and register the selected handler for every action on the resource," and because that wildcard handler is selected ahead of broader fallbacks, "an authenticated user may bypass fallback action, ownership, or permission checks and read, update, or delete another user's resource." Only Python deployments that pass `actions=` to those decorators are affected; there is no workaround. **Date it by the vendor (08-28), not the CVE (10-02)**: scanners keyed on the CVE will start flagging `langgraph-sdk < 0.4.4` now, five weeks after the fix shipped. One third-party database page shows an 8.1 for this id; the CNA record and the vendor page both say 7.6, and this file uses the CNA's. Status unchanged.

## Sources

- [The Hacker News — "LangGraph Flaw Chain Exposes Self-Hosted AI Agents to Remote Code Execution"](https://thehackernews.com/2026/06/langgraph-flaw-chain-exposes-self.html) — primary disclosure, chain walkthrough.
- [CybersecurityNews — "Critical Vulnerability Chain in LangGraph Allows Attackers to Gain Full Server Control"](https://cybersecuritynews.com/vulnerability-chain-in-langgraph/) — attack steps, remediation.
- [CybersecurityNews — "LangGraph Vulnerability Allows Malicious Python Code Execution During Deserialization"](https://cybersecuritynews.com/langgraph-vulnerability/) — CVE-2026-28277 detail.
- [NVD — CVE-2025-67644](https://nvd.nist.gov/vuln/detail/CVE-2025-67644) — SQL injection in langgraph-checkpoint-sqlite.
- [NVD — CVE-2026-28277](https://nvd.nist.gov/vuln/detail/CVE-2026-28277) — unsafe msgpack deserialization.
- [Snyk — "SQL Injection in langgraph-checkpoint-sqlite"](https://security.snyk.io/vuln/SNYK-PYTHON-LANGGRAPHCHECKPOINTSQLITE-14361682) — version ranges, patch guidance.

**2026-09-15 update sources** — all fetched 2026-09-15:
- [LangGraph — GHSA-fvww-7h3r-vfhp: LangGraph SDK custom auth silently ignores actions= on resource decorators](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-fvww-7h3r-vfhp) — CVSS 7.6, langgraph-sdk 0.1.45 – 0.4.3 → 0.4.4, no CVE, reporter Grg0rry.
- [LangGraph — GHSA-47pj-3jcm-6whg: Namespace prefix matching crosses segment boundaries in Postgres and SQLite stores (CVE-2026-71433)](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-47pj-3jcm-6whg) — CVSS 5.3, < 3.1.1 → 3.1.1, the three failing scenarios.
- [LangChain — GHSA-gr75-jv2w-4656: Path traversal and sandbox escape in LangChain file-search middleware and loaders (CVE-2026-55443)](https://github.com/langchain-ai/langchain/security/advisories/GHSA-gr75-jv2w-4656) — CVSS 5.1, langchain ≤ 1.3.8 → 1.3.9, langchain-anthropic ≤ 1.4.5 → 1.4.6.
- [LangGraph security advisories index](https://github.com/langchain-ai/langgraph/security/advisories) and [LangChain security advisories index](https://github.com/langchain-ai/langchain/security/advisories) — newest entries 2026-08-28 and 2026-06-12 respectively.
- **2026-10-05 update sources** — [CVE Services — CVE-2026-104873](https://cveawg.mitre.org/api/cve/CVE-2026-104873) (fetched 2026-10-05: GitHub_M CNA, published 2026-10-02, title, range `>= 0.1.45, < 0.4.4`, CVSS 4.0 7.6, references = GHSA-fvww-7h3r-vfhp + fix commit + `sdk==0.4.4` tag); [langchain-ai/langgraph — GHSA-fvww-7h3r-vfhp](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-fvww-7h3r-vfhp) (re-fetched 2026-10-05: now shows the CVE id, published 2026-08-28, no workaround, credit Grg0rry).
- **2026-10-04 update source** — [langchain-ai/langgraph — GHSA-4hm6-w6qq-w73v: LangGraph JavaScript custom authentication may permit cross-user Store access](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-4hm6-w6qq-w73v) (published 2026-09-28: High 8.6, `langgraph-api` ≥ 0.1.2 < 0.15.0 → 0.15.0, the reject-not-rewrite workaround, credit coinspect-audits); [langgraph advisory tab](https://github.com/langchain-ai/langgraph/security/advisories?state=published) (walked 2026-10-04: newest 2026-09-28). Fetched 2026-10-04.
- **2026-10-08 update source** — [langchain-ai/langgraph — GHSA-3fx2-cqw9-xr3c: Unencoded identifiers in SDK v3 streaming can redirect authenticated GET requests](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-3fx2-cqw9-xr3c) (fetched 2026-10-08: Moderate 4.3 `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N`, CWE-22, `langgraph` 1.2.3–1.2.13 → 1.2.14 and `langgraph-sdk` 0.4.0–0.4.5 → 0.4.6, Platform unaffected, reporter Evelynkaz, published 2026-10-07; no CVE at fetch).
