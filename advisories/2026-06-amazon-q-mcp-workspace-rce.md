---
id: 2026-06-amazon-q-mcp-workspace-rce
title: "Amazon Q Developer CVE-2026-12957 + CVE-2026-12958 — auto-loading .amazonq/mcp.json runs attacker code with live cloud credentials on repo open (June 2026)"
date_disclosed: 2026-06-26
last_updated: 2026-06-27
severity: high
status: patched
ecosystems: [mcp, aws, ide-extensions]
tools_affected: [Amazon Q Developer, AWS Language Server, VS Code, JetBrains, Eclipse, Visual Studio]
tags: [rce, mcp, workspace-trust, cloud-credentials, credential-theft, aws, malicious-repo]
---

## TL;DR

**Amazon Q Developer** automatically loaded MCP server configurations from `.amazonq/mcp.json` in any opened workspace — without user consent or trust verification — and spawned those servers as **unsandboxed processes inheriting the developer's live AWS credentials**. Opening a malicious repository was sufficient to execute attacker code and exfiltrate AWS keys, cloud tokens, SSH sockets, and API secrets. Patched in Language Servers for AWS 1.65.0 (released May 12, 2026); Wiz Research disclosed publicly June 26, 2026.

## What happened

**Amazon Q Developer** is AWS's AI coding assistant, available as a plugin for VS Code, JetBrains, Eclipse, and Visual Studio. Like other AI coding assistants in this class (Claude Code, Cursor, Gemini CLI), it supports **Model Context Protocol (MCP) servers** — local processes the assistant spawns to access databases, APIs, build tools, and other developer infrastructure.

On **April 20, 2026**, Wiz Research reported two vulnerabilities to AWS:

### CVE-2026-12957 — MCP config auto-execution without workspace trust (CVSS 8.5)

Amazon Q read `.amazonq/mcp.json` from any opened workspace and **immediately launched the MCP servers it defined** — without prompting the developer for consent or verifying that the workspace was trusted. The launched processes **inherited the developer's full environment**, providing attackers immediate access to:

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
- Cloud CLI tokens (GCP, Azure, any others in the environment)
- API secrets and SSH agent sockets
- `~/.aws/credentials`, `~/.kube/config`, and other credential files reachable from the environment

Wiz demonstrated the complete attack chain using `aws sts get-caller-identity` — a single cloned repo could escalate from "git clone" to full cloud account access.

### CVE-2026-12958 — Symlink validation bypass enabling path traversal (companion bug)

A missing symlink check in the workspace file processor allowed an attacker to construct symlinks that pointed outside the workspace trust boundary, enabling arbitrary file writes to the developer's home directory. This bypassed the workspace isolation that MCP server restrictions were meant to enforce.

**Attack vectors:**

- A public repository with a malicious `.amazonq/mcp.json` (fake coding tests, AI-demo repos, open-source contributions)
- A typosquatted or Shai-Hulud-poisoned package that plants `.amazonq/mcp.json` in the project directory
- A malicious pull request to an existing repository

This is the same attack class as:
- [Claude Code CVE-2025-59536](2025-08-claude-code-inverseprompt.md) — CLAUDE.md/hooks auto-execute on folder trust
- **Cursor CVE-2025-54136** — auto-run on repository open
- [Windsurf CVE-2026-30615](2026-05-windsurf-zero-click-mcp-rce.md) — zero-click MCP RCE
- [TrustFall](2026-05-trustfall-mcp-auto-execute.md) — five AI CLIs auto-execute MCP servers on folder-trust dialog

The pattern is systemic: every AI coding assistant that reads workspace config files and spawns processes before establishing trust is a potential "git clone to cloud compromise" vector.

**No known public exploitation** was reported before the patch was released. AWS auto-updates the language server unless network configuration prevents it.

## Am I affected?

**You are exposed if you use Amazon Q Developer and have not updated.**

Check your current Language Server for AWS version:

```bash
# In VS Code: Help → About → show all versions (look for Amazon Q Language Server)
# Or check the AWS extension output channel for version info

# Check installed plugin versions:
# VS Code:    Extensions view → Amazon Q → check version (need ≥ 2.20)
# JetBrains:  Plugins → Amazon Q → check version (need ≥ 4.3)
# Eclipse:    Help → Install New Software (need ≥ 2.7.4)
# VS (Win):   Extensions → Amazon Q Toolkit (need ≥ 1.94.0.0)
```

**Check if your repo has a malicious `.amazonq/mcp.json`:**

```bash
# Look for unexpected MCP server definitions in your project
cat .amazonq/mcp.json 2>/dev/null

# Check for recently added/modified mcp.json files
git log --all --oneline -- .amazonq/mcp.json

# Look for unexpected commands in the mcp definition
grep -r '"command"' .amazonq/ 2>/dev/null
```

**Audit for unexpected cloud activity:**

```bash
# Check for unauthorized AWS STS calls (CloudTrail)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=GetCallerIdentity \
  --start-time 2026-04-20T00:00:00Z \
  --query 'Events[*].[EventTime,Username,SourceIPAddress]' \
  --output table
```

## If you are affected

1. **Update immediately** to Language Servers for AWS ≥ 1.69.0 (AWS's recommended target). The language server auto-updates unless the network blocks it; reload your IDE to pull the latest build.
2. If you opened any untrusted repositories between **November 2025 (when MCP support shipped) and May 12, 2026**, rotate your AWS credentials immediately.
3. Review CloudTrail for unexpected `GetCallerIdentity`, `AssumeRole`, or API calls from developer workstations during the vulnerable window.
4. Remove any `.amazonq/mcp.json` file from your repository that you didn't author, or verify every `command` entry in existing ones.

See also:
- [Rotating cloud credentials playbook](../playbooks/rotating-cloud-credentials.md)
- [If your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention

- **Keep AI coding tools on `latest`** — many AI tool security fixes ship with no CVE or advisory. Auto-update or check weekly.
- **Review `.amazonq/mcp.json`, `.mcp.json`, `.claude/settings.json`, and `.cursor/` in every repo before opening** with an AI coding assistant. These files define what processes the assistant will spawn.
- **Never open repositories from untrusted sources** directly with an AI coding assistant. Clone first, inspect config files, then open.
- **Gate changes to AI-tool config files** behind `CODEOWNERS` review in any collaborative repo.
- **Apply minimal-privilege IAM:** developer workstation roles should have session duration limits (e.g., 1-hour STS tokens) and `aws:SourceIp` conditions where practical — this limits the blast radius if credentials are exfiltrated.
- See: [MCP hygiene](../prevention/mcp-hygiene.md), [Credential hygiene](../prevention/credential-hygiene.md)

## Sources

- [The Hacker News — Amazon Q Developer Flaw Could Let Malicious Repos Run Code via MCP Configs](https://thehackernews.com/2026/06/amazon-q-developer-flaw-could-let.html) — primary disclosure; CVE-2026-12957 + CVE-2026-12958; Wiz Research attribution; patch versions; disclosure timeline.
- [SecurityWeek — Amazon Q Flaw Enabled Cloud Credential Theft via Malicious Repositories](https://www.securityweek.com/amazon-q-flaw-enabled-cloud-credential-theft-via-malicious-repositories/) — technical details; Wiz PoC (`aws sts get-caller-identity`); attack vectors; patch timeline; related CVEs in Claude/Cursor/Windsurf.
- [CyberSecurityNews — Amazon Q Vulnerability Let Attackers Execute Code and Access Sensitive Cloud Environments](https://cybersecuritynews.com/amazon-q-vulnerability/) — patch version breakdown per IDE; auto-update behavior; CVE-2026-12958 symlink details.
- Cross-link: [TrustFall — five AI CLIs auto-execute MCP servers on folder-trust dialog](2026-05-trustfall-mcp-auto-execute.md) — same root class; Anthropic won't fix.
- Cross-link: [Windsurf CVE-2026-30615 zero-click MCP RCE](2026-05-windsurf-zero-click-mcp-rce.md) — parallel CVE in same attack class.
