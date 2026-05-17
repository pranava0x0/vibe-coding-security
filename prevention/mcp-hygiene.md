# MCP hygiene

> An MCP server is arbitrary code running with your agent's privileges. Treat installing one with the same scrutiny as `sudo npm install -g`.

## Canonical references (read first)

- **[Model Context Protocol — Security Best Practices (official spec)](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)** — the canonical guide from the protocol authors.
- **[Anthropic — Claude Code Security docs (MCP section)](https://code.claude.com/docs/en/security)** — Anthropic's recommendation: write your own MCP servers or only use ones from providers you trust.
- **[Anthropic — Making Claude Code more secure and autonomous (sandboxing)](https://www.anthropic.com/engineering/claude-code-sandboxing)** — official sandboxing model and rationale.
- **[Network Intelligence — MCP Security Checklist](https://www.networkintelligence.ai/blogs/model-context-protocol-mcp-security-checklist/)** — practical 2026 checklist.
- **[Towards Data Science — The MCP Security Survival Guide](https://towardsdatascience.com/the-mcp-security-survival-guide-best-practices-pitfalls-and-real-world-lessons/)** — best practices, pitfalls, real-world lessons.
- **[SentinelOne — MCP Security: Complete Guide](https://www.sentinelone.com/cybersecurity-101/cybersecurity/mcp-security/)** — broader threat model.

## Why MCPs are different from libraries

When you install a library, *your* code calls it. You decide when and how.

When you install an MCP server, **the agent calls it autonomously**, often with credentials you've configured. A malicious MCP doesn't need a user action — it just needs to be invoked once.

The [postmark-mcp backdoor](../advisories/2025-09-postmark-mcp-backdoor.md) shipped 15 clean versions before backdooring v1.0.16. The [Supabase lethal trifecta](../advisories/2025-07-supabase-mcp-lethal-trifecta.md) didn't even need a malicious MCP — just an over-privileged legitimate one. The [systemic MCP stdio RCE class](../advisories/2026-05-mcp-stdio-systemic-rce.md) (OX Security, May 2026) showed the problem affects ~200,000 servers across the ecosystem.

## Vetting checklist (before connecting any MCP)

For each new MCP server:

- [ ] **Is the publisher the vendor itself?** Prefer `@vercel/mcp-…`, `@supabase/mcp-…`, the vendor's own GitHub org. Avoid community typo-squats.
- [ ] **Is the source readable?** Open the repo, read `package.json`, read the main entry file. If it's obfuscated or bundled-only, walk away. (Socket's [supply-chain risk indicators](https://docs.socket.dev/docs/supply-chain-risk) explicitly flag obfuscated code.)
- [ ] **What network destinations does it contact?** Grep for `fetch(`, `axios`, `http.request` — confirm endpoints match the declared purpose.
- [ ] **What filesystem paths does it read?** Grep for `readFile`, `homedir()`, `~/`, `process.env.HOME`. An email MCP that reads `~/.aws/credentials` is malicious.
- [ ] **What env vars / config does it consume?** Make sure you understand every key you're about to hand it.
- [ ] **Install count + history?** Brand-new publisher with low downloads and no GitHub stars is suspicious. So is a long-lived project where the maintainer changed last week.
- [ ] **Has it been audited / reviewed publicly?** Search for `<mcp-name> security` and `<mcp-name> vulnerability` before installing.
- [ ] **Pin a specific version** (or commit SHA) in `mcp.json`, never `latest`.

## Configuration hygiene

```jsonc
// ~/.cursor/mcp.json — hardened example
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server@0.4.2"],   // exact version, official scope
      "env": {
        "SUPABASE_ACCESS_TOKEN": "sbp_readonly_xxx"   // read-only, scoped to specific tables
      }
    }
  }
}
```

Rules drawn from the [official MCP spec](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices) and Anthropic's docs:

- **Exact versions, not `latest`** — otherwise every restart can pull a fresh release.
- **Least-privilege credentials** — read-only keys, scoped to specific resources. Never `service_role`.
- **For local-only servers, bind to `127.0.0.1`, never `0.0.0.0`.** Per the MCP spec, "this is one of the most common and dangerous misconfigurations in MCP deployments" — `0.0.0.0` enables DNS rebinding and remote attacks.
- **Use OAuth 2.1 + PKCE for hosted MCPs.** Don't share tokens between MCP servers; each should have service-specific, narrowly-scoped credentials.
- **Prefer session-scoped authorization** — access expires when the task ends; human must re-approve. Don't grant agents persistent long-lived OAuth tokens.
- **Periodically audit `mcp.json`** — `cat ~/.cursor/mcp.json && cat ~/.config/claude/*.json` — and delete entries you no longer use.

## The "lethal trifecta" rule

[Simon Willison's framing](https://simonwillison.net/2025/Jul/6/supabase-mcp-lethal-trifecta/): an agent system is exploitable if it has **all three** of:

1. Access to private data.
2. Exposure to untrusted content.
3. The ability to externally communicate.

If your MCP setup has all three, prompt injection becomes data exfiltration. → [advisory](../advisories/2025-07-supabase-mcp-lethal-trifecta.md). This concern is officially echoed in [OWASP LLM Top 10 — LLM01 Prompt Injection](https://owasp.org/www-project-top-10-for-large-language-model-applications/) and [LLM03 Supply Chain Vulnerabilities](https://genai.owasp.org/llm-top-10/).

**Mitigations** (apply at least one):

- Remove untrusted content from the agent's context (don't let it read user-submitted rows in the same session it has DB write).
- Limit external communication (read-only MCPs, no shell, no HTTP).
- Split agents: one reads untrusted content with no privileges, a different agent acts on summaries with no untrusted input.

## Limit the MCPs you connect

Each MCP is a new attack surface. Don't connect Slack, GitHub issues, Notion, email, and a DB to the same agent unless you really need to. **The agent that fixes your code doesn't need to read your inbox.** Quarterly: cull MCPs you don't actively use.

## When the MCP isn't your own

If you must use a community MCP:

- Fork it. Pin your fork. Auto-deploy from a hash, not from upstream `main`.
- Subscribe to the upstream repo's releases — if the maintainer goes quiet or behavior changes, you'll notice.
- Don't auto-update.

## Audit-time tooling

- **[MCP Inspector](https://github.com/modelcontextprotocol/inspector)** — Anthropic's official tool. Sandbox + introspect an MCP before connecting.
- **[`mcp-scan`](https://github.com/invariantlabs-ai/mcp-scan)** — static analysis for MCP servers; flags risky patterns.

## TL;DR — five rules

1. **Treat every MCP as untrusted code** with root-equivalent permissions: audit before installing, scope to the minimum, pin versions, monitor at runtime, and remove what you don't need. ([MCP spec](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices))
2. **Treat all tool inputs as untrusted** — they come from an LLM, not directly from the user.
3. **Don't bind to `0.0.0.0`** for local servers.
4. **Never share tokens between MCP servers.** Service-specific, minimal-scope.
5. **Don't compose the lethal trifecta** — private data + untrusted content + outbound communication = exfiltration.
