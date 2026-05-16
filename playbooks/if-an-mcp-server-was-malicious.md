# If an MCP server you installed was malicious

> Scope: any MCP (Model Context Protocol) server you connected to Claude Code, Cursor, Codex, or another agent that turns out to be backdoored. The canonical example is the [postmark-mcp backdoor](../advisories/2025-09-postmark-mcp-backdoor.md).

## Do this first (60 seconds)

```bash
# 1. Find and remove the MCP server from every config
grep -r "<bad-mcp-name>" ~/.cursor/ ~/.config/claude/ ~/Library/Application\ Support/Claude/ 2>/dev/null
# Delete the entry from each mcp.json / settings file.

# 2. Kill any running MCP process
pkill -9 -f "<bad-mcp-name>"

# 3. Restart your agent (Cursor / Claude Code) to drop the connection.
```

## Triage

### What could the MCP do?
MCP servers run as **subprocesses with your user's privileges** and act on behalf of the agent. Depending on what the MCP claimed to do, the real blast radius could include:

- **Email MCP (e.g., postmark, gmail):** BCC every sent email, read inbox, send on your behalf.
- **DB MCP (supabase, postgres):** read every row, write rows, drop tables — RLS bypass if it uses a service key.
- **Filesystem MCP:** read every file the agent had access to, including `~/.ssh/`, `~/.aws/`, `~/.config/`.
- **GitHub MCP:** any action your authenticated `gh` could take.
- **Shell-execution MCP:** arbitrary code execution as your user.
- **Browser MCP:** read cookies, session tokens, autofill data.

Assume the MCP did **everything its declared scope allowed, plus everything its process privileges allowed**.

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

# Or check for connections to known IOC domains from the relevant advisory
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
| Filesystem | Treat as full machine compromise — all on-disk creds. → [if-you-installed-a-bad-npm-package.md](if-you-installed-a-bad-npm-package.md) |
| Shell execution | Full machine compromise. Consider reimaging. |

## Audit data exfiltration

The hardest part of an MCP compromise is figuring out what was sent out. Check:

- **Email logs.** For email MCPs: pull the "sent" log from the provider and look for unexpected BCC fields, forwards, or recipients.
- **Database access logs.** For DB MCPs: pull query logs (Supabase has these) and look for unusual `SELECT *` patterns from the agent's IP/user.
- **API service logs.** Vendor dashboards usually show request volume — spikes during the malicious window indicate exfiltration.
- **GitHub repos.** Search for any new public repos in your account or in the wider GitHub population that contain your data: `gh search repos "<unique-string-from-your-data>"`.

## Replace with a vetted MCP

Don't reinstall the same MCP just because the bad version got pulled. Get the official version from the **vendor's domain or GitHub org**, verify the publisher, and pin a specific commit/version.

→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — vetting checklist

## Document

Add an entry to your team's `issues.md`:
- MCP name, version, install date, removal date
- Which credentials it had access to
- What you rotated + audit findings
- Whether you found evidence of exfiltration

Also: open an issue on the official vendor's repo (if it's a typo-squat of a real product) so they can warn other users.
