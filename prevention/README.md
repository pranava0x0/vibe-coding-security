# Prevention

Hardening guides — the things you do **before** an incident so the incident doesn't matter.

| Topic | Doc |
|---|---|
| Locking down `npm install` | [npm-hardening.md](npm-hardening.md) |
| Vetting MCP servers before connecting them | [mcp-hygiene.md](mcp-hygiene.md) |
| Where credentials live (and where they shouldn't) | [credential-hygiene.md](credential-hygiene.md) |
| Running agents inside containers/VMs | [agent-sandboxing.md](agent-sandboxing.md) |
| 60-second checklist before any new install | [package-vetting-checklist.md](package-vetting-checklist.md) |

## The 5 highest-leverage habits

If you do nothing else from this folder, do these:

1. **`npm config set ignore-scripts true`** globally. Re-enable per-project only when you've audited what the postinstall does. → [npm-hardening.md](npm-hardening.md)
2. **Stop running agents with `--dangerously-skip-permissions` on your host.** Use a devcontainer. → [agent-sandboxing.md](agent-sandboxing.md)
3. **Never paste API keys into a chat window.** Use 1Password CLI / env vars from disk. → [credential-hygiene.md](credential-hygiene.md)
4. **Vet every MCP server before connecting it.** Read the source, check the publisher, pin a version. → [mcp-hygiene.md](mcp-hygiene.md)
5. **Verify a package on the registry website before installing what an LLM suggested.** 15 seconds, stops most slopsquatting. → [package-vetting-checklist.md](package-vetting-checklist.md)
