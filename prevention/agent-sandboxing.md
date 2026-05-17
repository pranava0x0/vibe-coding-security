# Agent sandboxing

> If you let an agent execute shell commands on your host, you've delegated your full user privileges to a system that takes instructions from text it reads on the internet. Put the agent in a box.

## Canonical references

- **[Anthropic — Making Claude Code more secure and autonomous (sandboxing)](https://www.anthropic.com/engineering/claude-code-sandboxing)** — the official sandboxing architecture. Filesystem + network isolation, reduces permission prompts by 84% in internal usage.
- **[Anthropic — Claude Code auto mode: a safer way to skip permissions](https://www.anthropic.com/engineering/claude-code-auto-mode)** — the official guidance: **auto mode is for sandboxed environments only**.
- **[Anthropic — Claude Code Security docs](https://code.claude.com/docs/en/security)** — primary reference, kept up to date.
- **[Karpathy — 2025 LLM Year in Review](https://karpathy.bearblog.dev/year-in-review-2025/)** — coined "autonomy slider"; argues for keeping LLMs on a tight leash.
- **[devcontainers.dev](https://containers.dev/)** — the standard for isolated dev environments.

## What Karpathy actually says

Andrej Karpathy (who coined "vibe coding") frames it as an **autonomy slider** — dial between tight human control and longer AI leashes. He's been candid about the failure mode: agents that run too long produce slop, and *he has personally accepted changes without reading the diffs.* His [AutoResearch](https://www.nextbigfuture.com/2026/03/andrej-karpathy-on-code-agents-autoresearch-and-the-self-improvement-loopy-era-of-ai.html) project codifies the discipline:

- **Strict time budget per experiment** — runs can't expand indefinitely.
- **Single success metric** — only changes that improve the metric are kept.
- **Automatic rollback** — failed or worse-performing changes are reverted automatically.

These constraints effectively create a sandbox where LLMs operate in **short bursts with clear success metrics and automatic rollback**. The lesson for vibe coding: give the agent a contained environment, narrow goal, and a way to undo.

## Why this matters

`--dangerously-skip-permissions` is the most attractive footgun in modern dev tooling. So convenient, so destructive, that [Anthropic's own docs](https://code.claude.com/docs/en/security) call it out by name.

Real incidents from the last year (each documented in [advisories/](../advisories/)):

- **Dec 2025**: Claude generated `rm -rf tests/ patches/ plan/ ~/` and `~/` expanded to the home directory. User lost desktop files, keychain, and application data.
- **Jul 2025**: [Amazon Q wiper prompt](../advisories/2025-07-amazon-q-wiper.md) would have wiped local files and AWS resources if better-formed.
- **Jul 2025**: [Supabase lethal trifecta](../advisories/2025-07-supabase-mcp-lethal-trifecta.md) exfiltrates DB rows via prompt injection in user-submitted content.
- **Apr 2026**: [Comment and Control](../advisories/2026-04-comment-and-control-pr-injection.md) — CVSS 9.4 — hits Claude Code Security Review, Gemini CLI, Copilot Agent on GitHub Actions runners.

The pattern: agent reads untrusted text → agent generates a tool call → tool call runs with your privileges.

## The hierarchy of sandboxing

From least to most isolated. Pick the highest level you can tolerate.

### Level 0 — confirm every command (default)

Don't pass `--dangerously-skip-permissions` (or equivalent). Review each shell command and file edit before approving.

**Cost:** mild friction. **Catches:** most accidents and obvious injections.

### Level 1 — Claude Code's built-in sandbox

As of late 2025, Claude Code ships with **[official sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)** — filesystem isolation (read-write only in the working directory) + network isolation (via a unix-domain-socket proxy). Enable it; it reduces permission-prompt fatigue by ~84% per Anthropic's measurements without giving up safety.

For [Auto Mode](https://www.anthropic.com/engineering/claude-code-auto-mode) (March 2026), Anthropic's official guidance is **only use it in a sandboxed environment**. Don't run Auto Mode on the host.

### Level 2 — devcontainer (recommended for most projects)

Run the agent inside a [devcontainer](https://containers.dev/) or VS Code Remote Container. Agent can `rm -rf` to its heart's content; your host filesystem is untouched.

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

Anthropic publishes a [reference devcontainer for Claude Code](https://github.com/anthropics/claude-code) — fork that as a starting point.

**Cost:** initial setup ~5 minutes per project. **Catches:** filesystem destruction, credential theft from `~/`, most npm install fallout.

### Level 3 — Docker container with no network

For exploratory / "let me try this random repo" work:

```bash
docker run --rm -it \
  -v "$PWD:/work" -w /work \
  --network=none \
  node:20 bash
```

No outbound network = no credential exfiltration. **Cost:** can't `npm install`. **Catches:** everything network-dependent.

### Level 4 — VM (Lima / OrbStack / UTM)

Fresh user account, no host filesystem mount unless needed. The most isolated practical option.

**Cost:** heavier resource use. **Catches:** kernel-level escapes, the rare container breakout.

### Level 5 — separate physical machine

A junk laptop or Raspberry Pi for unsupervised overnight runs. **Cost:** real money. **Catches:** literally everything.

## Specific tool guidance

### Claude Code

- **Default:** `claude` — confirm-each-step. Keep it this way unless you're in a sandbox.
- **Inside a devcontainer (or with Anthropic's built-in sandbox):** Auto Mode or `--dangerously-skip-permissions` is reasonable. See [Auto Mode docs](https://www.anthropic.com/engineering/claude-code-auto-mode).
- **On your host:** **never** `--dangerously-skip-permissions`. The brief productivity boost isn't worth a December-2025-Reddit-thread of losing your home directory.
- **Restrict tools:** use `--allowedTools` to whitelist only what's needed. Block `Bash` when you can.
- **Restrict MCPs:** keep only MCPs you've vetted. → [mcp-hygiene.md](mcp-hygiene.md)

### Cursor

- Keep updated (≥1.7 to avoid CurXecute / MCPoison / case-sensitivity bugs — see [advisory](../advisories/2025-07-cursor-curxecute-mcpoison.md)).
- Review every MCP entry; pin exact versions in `mcp.json`.
- For agent mode running shell commands, prefer in-app per-command confirmation.

### Windsurf

- Update past 1.9544.26 — [CVE-2026-30615](../advisories/2026-05-windsurf-zero-click-mcp-rce.md) is a zero-click MCP RCE.
- Same MCP hygiene as Cursor / Claude Code.

### v0 / Lovable / Bolt / Replit

- These run in the vendor's cloud — your local host isn't at risk from agent shell commands.
- The risk is **the app they produce**. Audit before launch. → [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)
- Don't paste production credentials into the chat. Bind keys at deploy time via the platform's secret store.
- Replit shipped [Security Agent (April 2026) and Workspace Security Center 2.0 (May 2026)](../advisories/ongoing-vibe-platform-exposure.md) — enable them.

## The "isolated identity" trick

Inside the sandbox, set up a fresh GitHub / npm / cloud identity with **only the permissions the agent needs**. If the agent goes rogue, only the sandbox identity gets revoked — your real account is untouched.

Example: a `gh-bot` GitHub account that's added as a collaborator with `write` only on the specific repos the agent works on. When the agent goes off, revoke the bot and rotate.

## What this does and doesn't solve

**Solves:**

- Accidental destructive shell commands.
- Filesystem credential theft from `~/`.
- Outbound exfiltration (Level 3+).

**Doesn't solve:**

- Bad code being committed and merged (you still need review — see the [auditing playbook](../playbooks/auditing-a-vibe-coded-repo.md)).
- The agent leaking via something it has legitimate access to (a connected MCP — see [mcp-hygiene.md](mcp-hygiene.md)).
- Prompt-injected actions within the agent's allowed scope (e.g., agent has DB write, gets injected to write attacker data — the [lethal trifecta](../advisories/2025-07-supabase-mcp-lethal-trifecta.md)).

Defense in depth: sandbox + review + least-privilege MCPs + least-privilege credentials.

## Further reading

- **[Anthropic — Security lessons from Claude Code's first year (Harmonic)](https://www.harmonic.security/resources/security-lessons-from-claude-codes-first-year)**
- **[Backslash — Claude Code Security Best Practices](https://www.backslash.security/blog/claude-code-security-best-practices)**
- **[The Reality of Vibe Coding: AI Agents and the Security Debt Crisis (Towards Data Science)](https://towardsdatascience.com/the-reality-of-vibe-coding-ai-agents-and-the-security-debt-crisis/)**
- **[Vibe Coding: A Programming Revolution or the Next Security Crisis? (SC Media UK)](https://insight.scmagazineuk.com/vibe-coding-a-programming-revolution-or-the-next-security-crisis)**
