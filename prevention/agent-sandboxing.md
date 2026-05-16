# Agent sandboxing

> If you let an agent execute shell commands on your host, you've delegated your full user privileges to a system that takes instructions from text it reads on the internet. Put the agent in a box.

## Why this matters

`--dangerously-skip-permissions` is the most attractive footgun in modern dev tooling. It's so convenient, and so destructive, that the [Claude Code docs themselves](https://code.claude.com/docs/en/security) call it out by name.

Real incidents from the last year:
- December 2025: Claude generated `rm -rf tests/ patches/ plan/ ~/` and `~/` expanded to the home directory. User lost desktop files, keychain, and application data.
- The Amazon Q wiper prompt would have wiped local files and AWS resources if it had been better-formed.
- The Supabase lethal trifecta exfiltrates DB rows via prompt injection in user-submitted content.

The pattern: agent reads untrusted text → agent generates a tool call → tool call runs with your privileges.

## The hierarchy of sandboxing

From least to most isolated. Pick the highest level you can tolerate.

### Level 0 — confirm every command (default)
Don't pass `--dangerously-skip-permissions` (or equivalent for your tool). Review each shell command and file edit before approving.

**Cost:** mild friction. **Catches:** most accidents and obvious injections.

### Level 1 — devcontainer (recommended for most)
Run the agent inside a [devcontainer](https://containers.dev/) or VS Code Remote Container. The agent can `rm -rf` to its heart's content; your host filesystem is untouched.

```jsonc
// .devcontainer/devcontainer.json
{
  "name": "agent-sandbox",
  "image": "mcr.microsoft.com/devcontainers/typescript-node:20",
  "mounts": [
    "source=${localWorkspaceFolder},target=/workspace,type=bind"
  ],
  "remoteEnv": {
    // Inject only what the agent needs; not your full host env
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}"
  },
  "postCreateCommand": "npm install --ignore-scripts"
}
```

Anthropic publishes a [reference devcontainer for Claude Code](https://github.com/anthropics/claude-code/tree/main/.devcontainer) — copy that as a starting point.

**Cost:** initial setup, ~5 minutes per project. **Catches:** filesystem destruction, credential theft from `~/`, most npm install fallout.

### Level 2 — Docker container with no network
For exploratory / "let me try this random repo" work. Run the agent in a container with no internet:

```bash
docker run --rm -it \
  -v "$PWD:/work" -w /work \
  --network=none \
  node:20 \
  bash
```

No outbound network means no credential exfiltration, no malicious package install. **Cost:** can't actually `npm install`. **Catches:** everything network-dependent.

### Level 3 — VM (Lima / OrbStack / UTM)
Full VM with a fresh user account, no host filesystem mount unless needed. The most isolated practical option.

**Cost:** heavier resource use. **Catches:** kernel-level escapes, the rare container breakout.

### Level 4 — separate physical machine
A junk laptop or a Raspberry Pi for "I'm going to let this thing run unsupervised overnight."

**Cost:** real money. **Catches:** literally everything.

## Specific tool-by-tool

### Claude Code

- **Default:** `claude` — confirm-each-step. Keep it this way unless you're in a sandbox.
- **Inside a devcontainer:** `claude --dangerously-skip-permissions` is reasonable.
- **On your host:** never `--dangerously-skip-permissions`. The brief productivity boost is not worth the December-2025-Reddit-thread of you losing your home directory.
- **Restrict tools:** use `--allowedTools` to whitelist only what's needed. Block `Bash` when you can.
- **Restrict MCPs:** keep only MCPs you've vetted. → [mcp-hygiene.md](mcp-hygiene.md)

### Cursor

- Keep Cursor updated (≥1.7 to avoid CurXecute/MCPoison/case-sensitivity bugs).
- Review every MCP entry; pin exact versions in `mcp.json`.
- For agent mode running shell commands, prefer the in-app per-command confirmation.

### v0 / Lovable / Bolt / Replit

- These run in the vendor's cloud — your local host isn't at risk from agent shell commands.
- The risk is **the app they produce**. Audit before launch. → [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)
- Don't paste production credentials into the chat; bind keys at deploy time via the platform's secret store.

## The "isolated identity" trick

Inside the sandbox, set up a fresh GitHub / npm / cloud identity with **only the permissions the agent needs**. If the agent goes rogue, only the sandbox identity gets revoked — your real account is untouched.

For example: a `gh-bot` GitHub account that's added as a collaborator with `write` only on the specific repos the agent works on. When the agent goes off, you revoke the bot and rotate.

## What this does and doesn't solve

**Solves:**
- Accidental destructive shell commands.
- Filesystem credential theft from `~/`.
- Outbound exfiltration (Level 2+).

**Doesn't solve:**
- Bad code being committed and merged (you still need review).
- The agent leaking via something it has legitimate access to (a connected MCP).
- Prompt-injected actions within the agent's allowed scope (e.g., the agent has DB write access, gets injected to write attacker data — see lethal trifecta).

Defense in depth: sandbox + review + least-privilege MCPs + least-privilege credentials.
