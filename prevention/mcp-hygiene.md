# MCP hygiene

> An MCP server is arbitrary code running with your agent's privileges. Treat installing one with the same scrutiny as `sudo npm install -g`.

## Why MCPs are different from libraries

When you install a library, *your* code calls it. You decide when and how.

When you install an MCP server, **the agent calls it autonomously**, often with credentials you've configured. A malicious MCP doesn't need to wait for a user action — it just needs to be invoked once.

The [postmark-mcp backdoor](../advisories/2025-09-postmark-mcp-backdoor.md) shipped 15 clean versions before backdooring v1.0.16. The [Supabase lethal trifecta](../advisories/2025-07-supabase-mcp-lethal-trifecta.md) didn't even need a malicious MCP — just an over-privileged legitimate one.

## Vetting checklist (before connecting any MCP)

For each new MCP server:

- [ ] **Is the publisher the vendor itself?** Prefer `@vercel/mcp-...`, `@supabase/mcp-...`, the vendor's own repo. Avoid community typo-squats.
- [ ] **Is the source readable?** Open the repo, read `package.json`, read the main entry file. If it's obfuscated or bundled-only, walk away.
- [ ] **What network destinations does it contact?** Grep for `fetch(`, `axios`, `http.request` — confirm endpoints match the declared purpose.
- [ ] **What filesystem paths does it read?** Grep for `readFile`, `homedir()`, `~/`, `process.env.HOME`. An email MCP that reads `~/.aws/credentials` is malicious.
- [ ] **What env vars / config does it consume?** Make sure you understand every key you're about to hand it.
- [ ] **What's the install count + history?** A v1.0.16 from a brand-new publisher with low downloads and no GitHub stars is suspicious. So is a long-lived project where the maintainer changed last week.
- [ ] **Has it been audited / reviewed publicly?** Search for `<mcp-name> security` and `<mcp-name> vulnerability` before installing.
- [ ] **Pin a specific version (or commit) in `mcp.json`**, never `latest`.

## Configuration hygiene

```jsonc
// ~/.cursor/mcp.json — example of a hardened config
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server@0.4.2"],   // exact version, official scope
      "env": {
        "SUPABASE_ACCESS_TOKEN": "sbp_readonly_xxx"   // read-only key, scoped to specific tables
      }
    }
  }
}
```

Rules:
- **Exact versions, not `latest`.** Otherwise every restart can pull a fresh release.
- **Least-privilege credentials.** Read-only keys, scoped to specific resources. Never `service_role`.
- **No personal data in env if avoidable.** Pass at runtime where possible.
- **Periodically audit `mcp.json`** — `cat ~/.cursor/mcp.json && cat ~/.config/claude/*.json` — and delete entries you no longer use.

## The "lethal trifecta" rule

Simon Willison's framing: an agent system is exploitable if it has **all three** of:
1. Access to private data.
2. Exposure to untrusted content.
3. The ability to externally communicate.

If your MCP setup has all three, prompt injection becomes data exfiltration. → [advisory](../advisories/2025-07-supabase-mcp-lethal-trifecta.md)

**Mitigations** (apply at least one):
- Remove untrusted content from the agent's context (e.g., don't let it read user-submitted rows in the same session it has DB write).
- Limit external communication (read-only MCPs, no shell, no HTTP).
- Split agents: one reads untrusted content with no privileges, a different agent acts on summaries with no untrusted input.

## Limit the MCPs you connect

Each MCP is a new attack surface. Don't connect Slack, GitHub issues, Notion, email, and a DB to the same agent unless you really need to. The agent that fixes your code doesn't need to read your inbox.

Quarterly: cull MCPs you don't actively use.

## When the MCP isn't your own

If you must use a community MCP:
- Fork it. Pin your fork. Auto-deploy from a hash, not from upstream `main`.
- Subscribe to the upstream repo's releases — if the maintainer goes quiet or behavior changes, you'll notice.
- Don't auto-update.
