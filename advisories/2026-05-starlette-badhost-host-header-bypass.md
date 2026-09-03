---
id: 2026-05-starlette-badhost-host-header-bypass
title: "BadHost — Starlette host-header auth bypass blasts FastAPI, vLLM, LiteLLM, MCP servers (CVE-2026-48710)"
date_disclosed: 2026-05-22
last_updated: 2026-09-03
severity: critical
status: patched
ecosystems: [pypi, fastapi, mcp, ai-agents]
tools_affected: [starlette, fastapi, vllm, litellm, mcp-python-sdk, text-generation-inference, openai-compatible-proxies]
tags: [cve, authentication-bypass, host-header, two-parsers-one-string, framework-level, mcp, fastapi, cisa-kev]
---

## TL;DR
**CVE-2026-48710 ("BadHost")** — Starlette < 1.0.1 builds `request.url` from the raw HTTP `Host` header without validation. A single character (`/`, `?`, or `#`) in `Host` shifts the path/query/fragment boundaries when the URL is re-parsed, so middleware that authorizes on `request.url.path` sees a different path than the ASGI router actually dispatched. **Any auth middleware reading `request.url.path` fails open.** Starlette ships ~**325M downloads/week** and sits under **FastAPI, vLLM, LiteLLM, Text Generation Inference, OpenAI-compatible proxies, the Python MCP SDK, and most AI-agent dashboards** — one bug, one character, an enormous blast radius. X41 D-Sec found it during an OSTIF-sponsored vLLM audit; coordinated disclosure 2026-05-22; **patched in Starlette 1.0.1 (2026-05-21)**.

## What happened
Starlette reconstructs `request.url` by concatenating the HTTP `Host` header with the request path and re-parsing the result. The `Host` value is **not validated against RFC 9112 § 3.2 / RFC 3986 § 3.2.2** before reconstruction. A malicious client sends a `Host` header that contains an HTTP-meaningful character — `/`, `?`, or `#` — and the re-parser splits the URL in a different place than the ASGI server did.

Result: `request.url.path` returns one string, `request.scope["path"]` (the actual routed path) returns another. **Auth middleware that decides on `request.url.path` runs its check against the wrong value.** The router still dispatches to the protected endpoint.

The minimal PoC published by X41:

```http
GET /admin HTTP/1.1
Host: foo?
```

…returns `200 OK` against a server whose middleware blocks `/admin` via `request.url.path`. One character. No credentials.

The bug was found by **JJ, Yassine El Baaj, and Markus Vervier at X41 D-Sec** during a sponsored source-code audit of **vLLM** for **OSTIF.org** funded by the **Alpha-Omega Project**. Independent reports from **ehhthing** and **Nicolas Lamoureux** corroborated. Coordinated disclosure was published 2026-05-22 (badhost.org, OSTIF, X41 advisory X41-2026-002, Starlette GHSA-86qp-5c8j-p5mr), one day after the upstream fix shipped — so operators had effectively zero lead time before the technique was public.

### Why this is bigger than one CVE

Starlette is the ASGI foundation under most modern Python AI infrastructure:

| Tool | What it does | Why it inherits BadHost |
|---|---|---|
| FastAPI | The dominant Python web/AI API framework | Built directly on Starlette; any `Depends()` auth on path is exposed |
| vLLM | Open-source LLM inference server | Public `/generate` etc. behind path-based auth |
| LiteLLM | OpenAI-compatible proxy → 100+ models | Admin endpoints, master-key gated |
| Text Generation Inference | Hugging Face's inference server | Same |
| MCP Python SDK / FastMCP | Server-side MCP | Path-based tool dispatch |
| OpenAI-compatible proxies | LM Studio, Ollama wrappers, custom shims | Same |
| Agent harnesses / eval dashboards | LangChain Server, OpenHands, etc. | Anything using `request.url.path` for routing/auth |

Starlette has **~325 M weekly PyPI downloads** and **400 K+ dependent GitHub projects** — possibly the broadest-surface Python security event of 2026.

### "Two parsers, one string" — a recurring class
BadHost is the third recent disclosure where two parts of one stack disagree on how to interpret a string, and the security check runs on the wrong interpretation. Sibling shapes already in this repo:

- **Argv-smuggling** — [Claude Code `eagerParseCliFlag` deeplink RCE](2026-05-claude-code-deeplink-rce.md): the pre-parser and the main argv parser disagree on which token is a flag *value*.
- **Allowlist vs resolver** — [Claude Code SOCKS5 null-byte bypass](2026-05-claude-code-sandbox-socks5-bypass.md): the matcher sees `attacker.com\x00.google.com`, the OS truncates at `\x00` and dials `attacker.com`.
- **Auth-middleware vs ASGI router** (BadHost, this advisory): middleware reads `request.url.path` (rebuilt from `Host`), router reads `scope["path"]` (raw ASGI path), they diverge.

The general lesson: **never base a security decision on a *reconstructed* value when a *canonical* value is available right next to it.** In Starlette, the canonical value is `request.scope["path"]`. In a CLI, it's the post-parse argv structure. In a network allowlist, it's the bytes the OS will actually pass to `connect()`.

## Am I affected?

```bash
# 1) Is Starlette < 1.0.1 anywhere in your deps?
pip show starlette 2>/dev/null | grep -E '^(Name|Version):'
pip list 2>/dev/null | grep -i starlette

# Locked versions, all envs:
grep -RniE 'starlette[<=>!~ ]+[0-9]' requirements*.txt pyproject.toml poetry.lock pdm.lock uv.lock 2>/dev/null

# 2) Does any middleware in your code make security decisions from
#    request.url, request.url.path, or str(request.url)?
#    Each match is a candidate gap.
grep -RnE 'request\.url(\.path)?|str\(request\.url\)' . 2>/dev/null

# 3) Live probe (against your OWN server) — does it serve a protected path
#    when Host is "foo?" ?
curl -sk -H 'Host: foo?' -o /dev/null -w '%{http_code}\n' https://your-host/admin
# 200 → vulnerable. 4xx/5xx → likely fine.

# Or use the official scanner:
#   https://badhost.org/  (X41 + Persistent Security Industries + Bintech)
```

### IOCs / identifiers

| Type | Value |
|---|---|
| CVE | `CVE-2026-48710` |
| GHSA | `GHSA-86qp-5c8j-p5mr` |
| PYSEC | `PYSEC-2026-161` |
| X41 advisory | `X41-2026-002` |
| Affected | `starlette >= 0.8.3, <= 1.0.0` |
| Fixed | `starlette 1.0.1` (released 2026-05-21) |
| Disclosed | 2026-05-22 |
| Trigger payload | `Host: foo?` (or any `/`, `?`, `#` in `Host`) |
| Researcher group | JJ, Yassine El Baaj, Markus Vervier (X41 D-Sec) — OSTIF / Alpha-Omega vLLM audit |
| Official CVSS | 6.5 (Moderate). X41 calls it critical given downstream blast radius. |

## If you are affected
1. **Upgrade Starlette to ≥ 1.0.1** in every environment that runs FastAPI / vLLM / LiteLLM / MCP server / any ASGI app:
   ```bash
   pip install --upgrade 'starlette>=1.0.1'
   # then, in each downstream:
   pip install --upgrade fastapi vllm litellm 'mcp>=0' text-generation
   ```
   Pin the floor in `requirements.txt` / `pyproject.toml`.

2. **In middleware, replace `request.url.path` with `request.scope["path"]`** anywhere a security decision is made. The scope path comes directly from the ASGI server, not from a reconstructed URL, and it's the value the router actually dispatched. This is the structural fix; the Starlette patch is defense-in-depth on top of it.

3. **Treat any pre-patch deployment as potentially probed.** The scanner at `badhost.org` was public from disclosure day; assume external scans hit you. Review access logs for unusual `Host` headers (`Host:` containing `/`, `?`, `#`, or other URI-unsafe characters) across 2026-05-21 → your patch date.

4. **Rotate the credentials that lived behind the path-auth-gated endpoints** if you cannot rule out unauthorized access — particularly LLM API keys, MCP server tokens, admin/master keys on LiteLLM, model-management UIs, and any secrets retrievable from now-exposed admin pages.

5. **Audit downstream MCP servers separately.** A Python MCP server using FastAPI/Starlette and serving over HTTP is reachable from any caller that can hit its `Host`; the canonical local-bind defense (the historical "MCP runs on stdio") does *not* apply once you've exposed an HTTP transport.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ **Don't authorize on reconstructed strings.** When the framework hands you both a canonical and a derived value, the canonical one is the security boundary. In Starlette: `request.scope["path"]`, not `request.url.path`. In any auth allowlist: the post-canonicalization form.
→ **Validate the `Host` header at the edge.** Put a reverse proxy or ASGI middleware that enforces RFC-grammar `Host` values *before* your auth middleware runs.
→ **MCP-over-HTTP needs the same network posture as any other public API** — auth on every endpoint, allowlists by IP, not "MCP is local-only." (See [advisories/2026-05-mcp-stdio-systemic-rce.md](2026-05-mcp-stdio-systemic-rce.md) for the broader systemic MCP-exposure class.)

## September 2026 update — added to CISA KEV, confirmed exploited in the wild

**CISA added CVE-2026-48710 to its Known Exploited Vulnerabilities catalog on 2026-09-02** (one of seven CVEs added that day), listed as "HTTP Request/Response Smuggling Vulnerability" — CISA's categorical label for the same Host-header/path-desync flaw described above. This confirms in-the-wild exploitation roughly 3.5 months after the coordinated disclosure and the Starlette 1.0.1 patch. Status remains `patched` (the fix has been available since 2026-05-21), but any instance still running Starlette ≤ 1.0.0 should now be treated as an active exploitation target, not a theoretical risk — see the credential-rotation guidance above.

## Sources
- [badhost.org — BadHost: CVE-2026-48710 (X41 D-Sec, Persistent Security Industries, Bintech)](https://badhost.org/) — canonical writeup + free scanner.
- [OSTIF — Disclosing the BADHOST Vulnerability in Starlette](https://ostif.org/disclosing-the-badhost-vulnerability-in-starlette/) — coordinated-disclosure narrative; vLLM-audit context.
- [X41 D-Sec advisory X41-2026-002 — Request Host Header not Validated in Starlette](https://x41-dsec.de/lab/advisories/x41-2026-002-starlette/) — researcher advisory; technical detail and PoC.
- [GitHub Security Advisory — GHSA-86qp-5c8j-p5mr (Kludex/starlette)](https://github.com/Kludex/starlette/security/advisories/GHSA-86qp-5c8j-p5mr) — upstream advisory + fix.
- [Starlette release notes — 1.0.1](https://starlette.dev/release-notes/) — patch details (`Host` validated against RFC 9112 / 3986; fall back to `scope["server"]`).
- [NVD — CVE-2026-48710](https://nvd.nist.gov/vuln/detail/CVE-2026-48710) — official CVE entry (CVSS 6.5).
- [FastAPI Discussion #15593 — Does GHSA-86qp-5c8j-p5mr affect FastAPI installations using Starlette ≤ 1.0.0?](https://github.com/fastapi/fastapi/discussions/15593) — confirms FastAPI inherits the bug.
- [CSO Online — FastAPI-based AI tools exposed to authentication bypass by flaw in Starlette framework](https://www.csoonline.com/article/4177711/fastapi-based-ai-tools-exposed-to-authentication-bypass-by-flaw-in-starlette-framework.html) — downstream-impact framing.
- [Cybersecurity News — Attackers Can Exploit BadHost to Access Sensitive AI Agent Server Endpoints](https://cybersecuritynews.com/badhost-ai-agent-vulnerability/) — corroborating timeline.
- [GBHackers — BadHost Vulnerability Exposes Sensitive AI Agent Server Endpoints to Attackers](https://gbhackers.com/badhost-vulnerability-exposes-sensitive-ai-agent-server/) — corroboration.
- [Cyber Kendra — BadHost (CVE-2026-48710): One Rogue Header Line Unlocks Your Entire AI Stack](https://www.cyberkendra.com/2026/05/badhost-cve-2026-48710-one-rogue-header.html) — corroboration.
- [Hacker News thread — BadHost – CVE-2026-48710: Starlette Host-Header Auth Bypass](https://news.ycombinator.com/item?id=48277107) — discussion + reproductions.
- [Firethering — A Critical Bug in a 325M-Download Package Put Millions of AI Agents at Risk](https://firethering.com/badhost-starlette-critical-vulnerability-ai-agents/) — scale.
- [GIGAZINE — Vulnerability in Starlette Endangers Millions of AI Agents](https://gigazine.net/gsc_news/en/20260527-millions-ai-agents-imperiled-vulnerability-starlette/) — mainstream coverage.
- [HackingPassion — BadHost Breaks Into FastAPI and vLLM With a Single Character](https://hackingpassion.com/badhost-starlette-cve-2026-48710/) — PoC walkthrough.
- [AI Weekly — Starlette BadHost flaw breaks AI agent auth](https://aiweekly.co/alerts/starlette-badhost-flaw-breaks-ai-agent-auth) — AI-industry coverage.
- [Tenable — CVE-2026-48710](https://www.tenable.com/cve/CVE-2026-48710) — CVE catalog.
- [ITdaily — 'BadHost' vulnerability threatens millions of AI agents and MCP servers](https://itdaily.com/news/security/badhost-vulnerability-threatens-ai-agents-mcp-servers/) — MCP angle.
- [CISA — Adds Seven Known Exploited Vulnerabilities to Catalog (2026-09-02)](https://www.cisa.gov/news-events/alerts/2026/09/02/cisa-adds-seven-known-exploited-vulnerabilities-catalog) — KEV listing for CVE-2026-48710.
- [The Hacker News — CISA Adds Seven Exploited Flaws as Attackers Deploy Reverse Shells and Crypto Miners](https://thehackernews.com/2026/09/cisa-adds-seven-exploited-flaws-as.html) — KEV batch coverage.
