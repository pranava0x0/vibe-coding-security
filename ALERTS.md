# Active alerts

> Single scannable feed. Latest on top. Each entry links to a full advisory.
>
> **Last refreshed:** 2026-05-17. If this date is more than 7 days old, treat the repo as stale — check [sources/](sources/) directly.

---

## 🔴 ACTIVE — react now

### 2026-05-13 — Systemic MCP stdio RCE class (~200,000 servers exposed)
OX Security: 7,000 vulnerable MCP servers on public IPs; ~200,000 total estimated. Three database MCPs (Apache Doris, Alibaba RDS, Apache Pinot) disclosed same window; **Alibaba declined to patch**. Microsoft MCP server hit by CVE-2026-26118.
→ [advisories/2026-05-mcp-stdio-systemic-rce.md](advisories/2026-05-mcp-stdio-systemic-rce.md)

### 2026-05 — Windsurf zero-click MCP RCE (CVE-2026-30615)
Prompt injection in MCP-fetched content writes to `mcp.json` and auto-registers attacker-controlled server — **no user interaction**. CVSS 8.0. Patched in Windsurf > 1.9544.26. Cursor / Claude Code / Gemini-CLI have the same class issue; vendors declined to issue CVEs.
→ [advisories/2026-05-windsurf-zero-click-mcp-rce.md](advisories/2026-05-windsurf-zero-click-mcp-rce.md)

### 2026-05-14 — `node-ipc` compromised (versions 9.1.6, 9.2.3, 12.0.1)
822K weekly downloads. Identical 80KB payload, DNS-based exfil to `sh.azurestaticprovider.net` / `37.16.75.69`. Steals 90+ credential categories. Forensic marker: tarball files timestamped 1985-10-26.
→ [advisories/2026-05-node-ipc-compromise.md](advisories/2026-05-node-ipc-compromise.md)

### 2026-05-11 → 2026-05-12 — Mini Shai-Hulud wave: TanStack, Mistral, UiPath, OpenSearch
**172 unique packages, 403 malicious versions** across npm + PyPI. Operated by **TeamPCP**. First documented case of malicious npm package carrying **valid SLSA provenance** (published by legitimate pipeline after attacker hijacked the runner).
→ [advisories/2026-05-tanstack-mini-shai-hulud.md](advisories/2026-05-tanstack-mini-shai-hulud.md)

### 2026-04 (ongoing) — Mini Shai-Hulud SAP packages
`mbt`, `@cap-js/db-service`, `@cap-js/postgres`, `@cap-js/sqlite` compromised. Same TeamPCP playbook. Harvests local dev creds, GH/npm tokens, cloud creds.
→ [advisories/2026-04-mini-shai-hulud-sap.md](advisories/2026-04-mini-shai-hulud-sap.md)

### 2026-04 — "Comment and Control" prompt injection (Claude Code Sec Review / Gemini CLI / Copilot Agent)
CVSS **9.4 Critical**. Payload in GitHub PR title/issue body/comment hijacks AI agent to exfiltrate Actions runner secrets. All three vendors patched.
→ [advisories/2026-04-comment-and-control-pr-injection.md](advisories/2026-04-comment-and-control-pr-injection.md)

---

## 🟠 RECENT — verify exposure

### 2026-03-31 — `axios` compromise (70M+ weekly downloads)
Two malicious Axios versions connected to Sapphire Sleet C2 to pull a RAT. Auto-update enabled = silent infection. Removed but inspect lockfiles from late March.
→ [advisories/2026-03-axios-compromise.md](advisories/2026-03-axios-compromise.md)

### 2025-11-24 — Shai-Hulud "The Second Coming"
492 packages (132M monthly downloads), Zapier / ENS / PostHog / Postman trojanized. 25,000+ malicious GitHub repos. Aligned with npm classic-token revocation deadline.
→ [advisories/2025-11-shai-hulud-second-coming.md](advisories/2025-11-shai-hulud-second-coming.md)

### 2025-09-17 — `postmark-mcp` backdoor (first malicious MCP)
v1.0.16 silently BCC'd every outgoing email to `phan@giftshop[.]club`. Built trust over 15 clean versions. 1,643 downloads before removal.
→ [advisories/2025-09-postmark-mcp-backdoor.md](advisories/2025-09-postmark-mcp-backdoor.md)

### 2025-09-15 — Shai-Hulud npm worm (original)
First self-replicating npm worm. ~200 packages including `@ctrl/tinycolor` (2.2M weekly), `ngx-bootstrap` (300k weekly). Stole GitHub/npm/AWS/GCP creds, leaked private repos.
→ [advisories/2025-09-shai-hulud-original.md](advisories/2025-09-shai-hulud-original.md)

### 2025-09-08 — `qix` account compromise (2B weekly downloads)
`chalk`, `debug`, `ansi-styles`, `strip-ansi`, `color-convert`, `wrap-ansi` + 12 more. Phishing email from `npmjs.help` impersonating npm support. ~2 hours live. Browser-side crypto-wallet hijack payload.
→ [advisories/2025-09-qix-compromise.md](advisories/2025-09-qix-compromise.md)

### 2025-08-26 — Nx `s1ngularity` (first AI-CLI-assisted malware)
Postinstall script that *invoked Claude Code and Gemini CLI* to scan for secrets. 2,349 distinct credentials leaked to public GitHub repos. 4 hours live.
→ [advisories/2025-08-nx-s1ngularity.md](advisories/2025-08-nx-s1ngularity.md)

### 2025-07-17 — Amazon Q VS Code extension wiper prompt
v1.84.0 shipped with attacker-injected prompt telling Q to wipe local filesystem + cloud resources. Malformed and inert in practice, but the supply-chain path (open PR → admin access → release) was real.
→ [advisories/2025-07-amazon-q-wiper.md](advisories/2025-07-amazon-q-wiper.md)

### 2025-07 — Cursor CurXecute (CVE-2025-54135) + MCPoison (CVE-2025-54136)
Prompt injection via MCP server data → Cursor modifies `mcp.json` → auto-executes attacker code. Patched in Cursor 1.3. MCPoison: trust bound to MCP key name, not command — persistent backdoor.
→ [advisories/2025-07-cursor-curxecute-mcpoison.md](advisories/2025-07-cursor-curxecute-mcpoison.md)

### 2025-07 — Supabase MCP lethal trifecta
Demonstrated by Simon Willison / General Analysis: Cursor + Supabase MCP with `service_role` key + reading attacker-controlled rows = full DB exfiltration via stored prompt injection. RLS bypassed entirely.
→ [advisories/2025-07-supabase-mcp-lethal-trifecta.md](advisories/2025-07-supabase-mcp-lethal-trifecta.md)

---

## 🟡 HISTORICAL — patched, but pattern recurs

### 2025-08 → 2026-Q1 — Claude Code InversePrompt (CVE-2025-54794, CVE-2025-54795, CVE-2025-59536, CVE-2026-21852, CVE-2026-33068, TrustFall)
Indirect prompt injection chains that turn Claude Code's own tool use against the user. Anthropic has patched all listed. The *class* of attack (hidden text in fetched content, MCP-delivered prompts, malicious env config) keeps recurring — see also [Comment and Control](advisories/2026-04-comment-and-control-pr-injection.md).
→ [advisories/2025-08-claude-code-inverseprompt.md](advisories/2025-08-claude-code-inverseprompt.md)

### Ongoing — Slopsquatting (AI-hallucinated package names)
LLMs invent package names that don't exist. Attackers register them. Next user who pastes the same hallucinated code gets owned. 500+ packages registered in waves on PyPI.
→ [advisories/ongoing-slopsquatting.md](advisories/ongoing-slopsquatting.md)

### Ongoing — Lovable / Bolt / Replit data exposure patterns
Lovable BOLA left open 48 days. Bolt env-var leakage. Replit public repls leaking secrets. RLS misconfigurations across thousands of vibe-coded apps. Class issue, not single incident. (Replit shipped Security Agent in April 2026 and Workspace Security Center 2.0 on May 8, 2026 — partial defender response.)
→ [advisories/ongoing-vibe-platform-exposure.md](advisories/ongoing-vibe-platform-exposure.md)

---

## How alerts get triaged

- **🔴 ACTIVE** — incident in last 14 days OR malware still propagating
- **🟠 RECENT** — last 12 months, still relevant to anyone with old lockfiles
- **🟡 HISTORICAL** — patched, but the attack pattern keeps re-occurring; read for context

Promotion/demotion happens on full sweeps (target: weekly). See [sources/README.md](sources/README.md) for the monitoring list.
