# Active alerts

> Single scannable feed. Latest on top. Each entry links to a full advisory.
>
> **Last refreshed:** 2026-05-16. If this date is more than 7 days old, treat the repo as stale — check [sources/](sources/) directly.

---

## 🔴 ACTIVE — react now

### 2026-05-14 — `node-ipc` compromised (3 malicious versions)
Three malicious versions of `node-ipc` (10M+ weekly downloads) published simultaneously. Identical 80KB obfuscated credential-stealing payload. Foundational IPC library, transitive dependency in thousands of projects.
→ [advisories/2026-05-node-ipc-compromise.md](advisories/2026-05-node-ipc-compromise.md)

### 2026-05-11 — `@tanstack/*` Mini Shai-Hulud (84 artifacts, 42 packages)
`@tanstack/react-router` (12.7M weekly downloads) and 41 sibling packages compromised via GitHub Actions "Pwn Request" + cache poisoning + OIDC token abuse.
→ [advisories/2026-05-tanstack-mini-shai-hulud.md](advisories/2026-05-tanstack-mini-shai-hulud.md)

### 2026-04 (ongoing) — Mini Shai-Hulud SAP packages
`mbt`, `@cap-js/db-service`, `@cap-js/postgres`, `@cap-js/sqlite` compromised. Harvests local dev creds, GitHub/npm tokens, GH Actions secrets, AWS/Azure/GCP/Kubernetes creds.
→ [advisories/2026-04-mini-shai-hulud-sap.md](advisories/2026-04-mini-shai-hulud-sap.md)

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

### 2025-08 → 2026-Q1 — Claude Code InversePrompt (CVE-2025-54794, CVE-2025-54795)
Indirect prompt injection chains that turn Claude Code's own tool use against the user. Patched, but the *class* of attack (hidden text in fetched content, MCP-delivered prompts) is permanent.
→ [advisories/2025-08-claude-code-inverseprompt.md](advisories/2025-08-claude-code-inverseprompt.md)

### Ongoing — Slopsquatting (AI-hallucinated package names)
LLMs invent package names that don't exist. Attackers register them. Next user who pastes the same hallucinated code gets owned. 500+ packages registered in waves on PyPI.
→ [advisories/ongoing-slopsquatting.md](advisories/ongoing-slopsquatting.md)

### Ongoing — Lovable / Bolt / Replit data exposure patterns
Lovable BOLA left open 48 days. Bolt env-var leakage. Replit public repls leaking secrets. RLS misconfigurations across thousands of vibe-coded apps. Class issue, not single incident.
→ [advisories/ongoing-vibe-platform-exposure.md](advisories/ongoing-vibe-platform-exposure.md)

---

## How alerts get triaged

- **🔴 ACTIVE** — incident in last 14 days OR malware still propagating
- **🟠 RECENT** — last 12 months, still relevant to anyone with old lockfiles
- **🟡 HISTORICAL** — patched, but the attack pattern keeps re-occurring; read for context

Promotion/demotion happens on full sweeps (target: weekly). See [sources/README.md](sources/README.md) for the monitoring list.
