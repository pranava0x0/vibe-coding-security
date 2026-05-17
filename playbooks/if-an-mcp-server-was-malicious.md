# If an MCP server you installed was malicious

> Scope: any MCP (Model Context Protocol) server you connected to Claude Code, Cursor, Codex, Windsurf, Gemini CLI, or any other agent that turns out to be backdoored.
>
> Canonical example: [postmark-mcp backdoor](../advisories/2025-09-postmark-mcp-backdoor.md). Class-wide reference: [Systemic MCP stdio RCE](../advisories/2026-05-mcp-stdio-systemic-rce.md).

## Authoritative references

- **[Model Context Protocol — Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)** — the official spec.
- **[Anthropic — Claude Code Security docs](https://code.claude.com/docs/en/security)** — MCP section.
- **[Network Intelligence — MCP Security Checklist](https://www.networkintelligence.ai/blogs/model-context-protocol-mcp-security-checklist/)** — practical 2026 checklist.
- **[Towards Data Science — The MCP Security Survival Guide](https://towardsdatascience.com/the-mcp-security-survival-guide-best-practices-pitfalls-and-real-world-lessons/)**.
- **[SentinelOne — MCP Security: Complete Guide](https://www.sentinelone.com/cybersecurity-101/cybersecurity/mcp-security/)**.

## Do this first (60 seconds)

```bash
# 1. Find and remove the MCP server from every config
grep -r "<bad-mcp-name>" \
  ~/.cursor/ ~/.windsurf/ ~/.codeium/ \
  ~/.config/claude/ ~/Library/Application\ Support/Claude/ \
  2>/dev/null
# Delete the entry from each mcp.json / settings file.

# 2. Kill any running MCP process
pkill -9 -f "<bad-mcp-name>"

# 3. Restart your agent (Cursor / Claude Code / Windsurf) to drop the connection.
```

## Triage

### What could the MCP do?

MCP servers run as **subprocesses with your user's privileges** and act on behalf of the AI agent. Per the [MCP spec](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices), they should be treated as untrusted dependencies with root-equivalent permissions. Blast radius depends on what the MCP claimed to do:

- **Email MCP (postmark, gmail):** BCC every sent email, read inbox, send on your behalf. ([postmark-mcp pattern](../advisories/2025-09-postmark-mcp-backdoor.md).)
- **DB MCP (supabase, postgres, doris, alibaba RDS, pinot):** read every row, write rows, drop tables — RLS bypass if it uses a service key. ([Supabase lethal trifecta](../advisories/2025-07-supabase-mcp-lethal-trifecta.md), [May 2026 DB MCPs](../advisories/2026-05-mcp-stdio-systemic-rce.md).)
- **Filesystem MCP:** read every file the agent had access to, including `~/.ssh/`, `~/.aws/`, `~/.config/`.
- **GitHub MCP:** any action your authenticated `gh` could take.
- **Shell-execution MCP:** arbitrary code execution as your user.
- **Browser MCP:** read cookies, session tokens, autofill data.

**Assume the MCP did everything its declared scope allowed, plus everything its process privileges allowed.**

### What did the MCP have access to?

Audit which credentials and services were configured:

```bash
# Look at the MCP server's package source to see what it imported and called
# (You should always do this BEFORE installing — see prevention/mcp-hygiene.md)
npm view <bad-mcp> repository.url
# Or for git-installed MCPs, find the source dir
find ~/.npm ~/.cache -name "<bad-mcp-name>" -type d 2>/dev/null
```

### What domains did it contact?

```bash
# macOS: check Little Snitch / pf logs if running
# Linux: check journalctl, ufw logs

# Or check known IOC domains from the relevant advisory
# (e.g., postmark-mcp → phan@giftshop[.]club)
```

## Rotate

Based on what the MCP had access to:

| MCP type | Rotate |
|---|---|
| Email (Postmark, Gmail, SendGrid) | API key for the email service. Also any **other** credentials ever sent through email by the agent (password resets, API key delivery, MFA codes). |
| Database (Supabase, Postgres, etc.) | DB password / service-role key. Audit row contents for unexpected writes. |
| GitHub | → [if-your-github-pat-leaked.md](if-your-github-pat-leaked.md) |
| Cloud (AWS/GCP/Azure) | → [rotating-cloud-credentials.md](rotating-cloud-credentials.md) |
| Filesystem | Full machine compromise — all on-disk creds. → [if-you-installed-a-bad-npm-package.md](if-you-installed-a-bad-npm-package.md) |
| Shell execution | Full machine compromise. Consider reimaging. |

## Audit data exfiltration

The hardest part of an MCP compromise is figuring out what was sent out:

- **Email logs.** For email MCPs: pull "sent" log from the provider; look for unexpected BCC fields, forwards, or recipients.
- **Database access logs.** For DB MCPs: pull query logs (Supabase has these); look for unusual `SELECT *` patterns from the agent's IP/user.
- **API service logs.** Vendor dashboards show request volume — spikes during the malicious window indicate exfiltration.
- **GitHub repos.** Search for any new public repos containing your data: `gh search repos "<unique-string-from-your-data>"`.

## Replace with a vetted MCP

Don't reinstall the same MCP just because the bad version got pulled. Get the **official version** from the vendor's domain or GitHub org. Verify publisher. Pin a specific commit/version. Run the vetting checklist before reconnecting:

→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — vetting checklist + the lethal-trifecta framing.

## Document

Add to `issues.md`:

- MCP name, version, install date, removal date
- Which credentials it had access to
- What you rotated + audit findings
- Whether you found evidence of exfiltration

Also: open an issue on the **official vendor's repo** (if it's a typo-squat of a real product) so they can warn other users. See how Postmark handled it: [Postmark — Security Alert: Malicious 'postmark-mcp' npm Package Impersonating Postmark](https://postmarkapp.com/blog/information-regarding-malicious-postmark-mcp-package).

## Prevention going forward

- → [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — vetting, config hygiene, OAuth 2.1 + PKCE, `127.0.0.1` binding, session-scoped auth.
- → [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — run agents (and their MCPs) inside a devcontainer so blast radius is contained.
- Quarterly: cull MCPs you don't actively use. Every active MCP is attack surface.
