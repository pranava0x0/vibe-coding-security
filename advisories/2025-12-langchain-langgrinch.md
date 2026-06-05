---
id: 2025-12-langchain-langgrinch
title: "LangChain LangGrinch + path-traversal + SSRF (CVE-2025-68664, CVE-2026-34070, CVE-2026-26019)"
date_disclosed: 2025-12-23
last_updated: 2026-06-05
severity: critical
status: patched
ecosystems: [pypi, npm, ai-agents, langchain]
tools_affected: [langchain, langchain-core, langgraph, @langchain/community]
tags: [cve, deserialization, prompt-injection, secret-exfil, path-traversal, ssrf, ai-agent-framework]
---

## TL;DR
**LangGrinch (CVE-2025-68664, CVSS 9.3 Critical)** — `langchain-core`'s `dumps()` / `dumpd()` serializers did not escape user-controlled dictionaries containing the reserved `"lc"` key. Attacker-supplied data round-tripped through `loads()` could instantiate classes from `langchain_core` / `langchain` namespaces, exfiltrate environment-variable secrets, and reach arbitrary code execution via Jinja2 templates. Patched in `langchain-core` **0.3.81** and **1.2.5** (Dec 23, 2025). A follow-on path-traversal, **CVE-2026-34070 (CVSS 7.5)**, in `langchain_core/prompts/loading.py` lets a deserialized config load files outside the intended directory; patched in **1.2.22** (May 2026). With LangChain at ~98M downloads/month, any vibe-coded agent that loads user-influenced data through LangChain's serializer is in scope.

## What happened
On **2025-12-23**, **Cyata** disclosed **CVE-2025-68664** ("LangGrinch") to LangChain. The bug lived in `langchain_core.load.dump.dumps()` / `dumpd()`: when serializing a "free-form dictionary" that happened to contain a key named `"lc"`, the serializer treated it as a *LangChain magic marker* rather than user data. On deserialization (`loads()`/`loadd()`), the magic-marker path could:

1. Read fields and instantiate classes from the **allowlisted** `langchain_core` and `langchain` namespaces.
2. Use those classes (notably anything that takes a Jinja2 template) to render attacker-controlled strings, which Jinja2 can evaluate as Python.
3. Reach `os.environ` and the global module namespace — extracting `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, AWS keys, etc.

The exploitation path is realistic for vibe coders: any LangChain agent that **stores chains, messages, prompts, or tool configs by serializing user-influenced data to JSON** — for example, persisting a chat history in Redis/Postgres and reloading it — gives an attacker who controls part of that data a write→read→RCE primitive.

Five months later (**May 2026**), researcher *Rickidevs* disclosed **CVE-2026-34070**, a path-traversal in `langchain_core/prompts/loading.py`. The loader took filename values out of a deserialized config dictionary and `open()`ed them without normalizing the path, letting an attacker chained off LangGrinch read arbitrary files (or, with the right write-then-read, complete the original RCE primitive on stricter Jinja2 sandboxes).

Both bugs are in `langchain-core`, which is depended on transitively by `langchain`, `langgraph`, `langsmith`, and every official LangChain integration. **LangChain reports ~98M downloads in the last month; ~847M total.**

## Am I affected?

```bash
# Are you on a vulnerable langchain-core?
pip show langchain-core | grep -E '^(Name|Version):'

# Anything <0.3.81 OR (>=1.0.0,<1.2.5) is vulnerable to LangGrinch
# Anything <1.2.22 is vulnerable to CVE-2026-34070

# Search the codebase for risky patterns
grep -RnE 'langchain.*\.load(s|d)?\(' . 2>/dev/null
grep -RnE 'langchain.*\.dump(s|d)?\(' . 2>/dev/null
# Or pickled / Redis-stored chains:
grep -RnE 'PickleSerializer|RedisChatMessageHistory|json\.loads.*langchain' . 2>/dev/null
```

You are affected if:
- You run a vulnerable `langchain-core` *and* persist or transmit chain/prompt/message objects that touch any user input, OR
- You import LangChain into a service that accepts JSON from third parties and at any point does `loads()` on it.

### IOCs

| Type | Value |
|---|---|
| CVE | `CVE-2025-68664` ("LangGrinch") |
| CVE | `CVE-2026-34070` (path traversal) |
| GHSA | `GHSA-r399-636x-v7f6` (LangGrinch) |
| CVSS | `9.3` (LangGrinch) / `7.5` (path traversal) |
| Affected | `langchain-core <0.3.81 OR >=1.0.0,<1.2.5` (LangGrinch); `langchain-core <1.2.22` (path-traversal) |
| Fixed | `langchain-core 0.3.81`, `1.2.5`, `1.2.22` |
| Marker key | dictionaries containing the literal string `"lc"` round-tripped through `langchain.load.dump` |

## If you are affected
1. Pin and upgrade: `pip install --upgrade "langchain-core>=1.2.22"` (also pulls compatible `langchain` / `langgraph`).
2. Audit code paths where chain/message/prompt objects are loaded from user-influenced JSON (Redis, Postgres, files, HTTP bodies). Add a schema check before `loads()`.
3. Treat any environment variables the LangChain process could read as **disclosed** until proven otherwise. Rotate LLM provider keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.), cloud keys, and any secrets in the same process. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. Disable Jinja2 templating in any LangChain component that doesn't strictly require it.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ Never use a framework deserializer (LangChain `load.dump`, Pydantic `parse_obj_as`, pickle) on data you didn't write. Use plain JSON + an explicit schema.
→ Pin AI-framework packages to exact versions in production; treat AI-agent framework CVEs as < 4-hour disclosure-to-exploit per the [PraisonAI baseline](2026-05-praisonai-auth-bypass.md).

## June 2026 update — CVE-2026-26019: @langchain/community RecursiveUrlLoader SSRF

**CVE-2026-26019** (moderate) was disclosed in the **JavaScript/TypeScript** LangChain package `@langchain/community` (up to version 1.1.13). The `RecursiveUrlLoader` class validates URLs with `String.startsWith()` (a string-prefix check, not a semantic URL comparison), allowing crafted subdomains like `https://example.com.attacker.com` to bypass the `preventOutside` same-domain restriction. Additionally, the crawler did not block access to cloud metadata endpoints (`169.254.169.254`), loopback, or RFC-1918 private addresses — enabling SSRF to AWS/GCP/Azure instance metadata services.

**Fixed in `@langchain/community` 1.1.14** by replacing the prefix check with strict `URL` API origin validation and adding explicit SSRF filters for private IP ranges, loopback, cloud metadata, and non-HTTP(S) schemes.

```bash
# Check JS/TS LangChain community version
npm list @langchain/community 2>/dev/null
# Vulnerable: <1.1.14
```

If your LangChain JS agent uses `RecursiveUrlLoader` and processes user-supplied or externally-fetched URLs, upgrade immediately.

| Field | Value |
|---|---|
| CVE | `CVE-2026-26019` |
| GHSA | `GHSA-gf3v-fwqg-4vh7` |
| Affected | `@langchain/community <1.1.14` |
| Fixed | `@langchain/community 1.1.14` |

## Sources
- [Cyata — All I Want for Christmas is Your Secrets: LangGrinch hits LangChain Core (CVE-2025-68664)](https://cyata.ai/blog/langgrinch-langchain-core-cve-2025-68664/) — Original disclosure (Dec 23, 2025), full PoC chain.
- [NVD — CVE-2025-68664 Detail](https://nvd.nist.gov/vuln/detail/CVE-2025-68664) — Official CVE record + CVSS 9.3.
- [The Hacker News — Critical LangChain Core Vulnerability Exposes Secrets via Serialization Injection](https://thehackernews.com/2025/12/critical-langchain-core-vulnerability.html) — Independent confirmation.
- [Cybersecurity News — Critical Langchain Vulnerability Let attackers Exfiltrate Sensitive Secrets from AI systems](https://cybersecuritynews.com/langchain-vulnerability/) — Impact framing; download stats.
- [Miggo — CVE-2025-68664: LangChain Deserialization RCE](https://www.miggo.io/vulnerability-database/cve/CVE-2025-68664) — Technical breakdown.
- [SOCRadar — CVE-2025-68664: Critical LangChain Flaw Enables Secret Extraction](https://socradar.io/blog/cve-2025-68664-langchain-flaw-secret-extraction/) — Aggregator confirmation.
- [GitHub — Rickidevs/CVE-2026-34070 (path traversal disclosure)](https://github.com/Rickidevs/CVE-2026-34070) — CVE-2026-34070 researcher writeup.
- [Vucense — Security Audit: Patching the Langchain CVE-2026-34070 and the Risks of Unchecked AI Deserialization](https://vucense.com/tech-guides/vulnerabilities/security-audit-patching-the-langchain-cve-2026-34070-and-the-risks-of-unchecked-ai-deserialization/) — Path-traversal context + patched-version (1.2.22) confirmation.
- [Hacker News thread — Critical vulnerability in LangChain – CVE-2025-68664](https://news.ycombinator.com/item?id=46386009) — Community discussion and exploitation context.
- [GitHub Advisory Database — CVE-2026-26019](https://github.com/advisories/GHSA-gf3v-fwqg-4vh7) — SSRF in @langchain/community RecursiveUrlLoader.
- [CyberSecurityNews — LangChain Community SSRF Bypass Vulnerability Enables Access to Internal Services](https://cybersecuritynews.com/langchain-community-ssrf-bypass-vulnerability/) — CVE-2026-26019 write-up.
- [NVD — CVE-2026-26019 Detail](https://nvd.nist.gov/vuln/detail/CVE-2026-26019) — Official CVE record.
