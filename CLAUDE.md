# Repository rules for agents

## Git commit and PR attribution

Commits, PR titles, PR descriptions and PR comments read as written by the repository owner alone. This holds in every session, including the scheduled cloud sweep.

- No `Co-Authored-By:` trailer naming Claude, Anthropic, Codex, OpenAI, Copilot or any other agent.
- No `Claude-Session:` trailer.
- No "Generated with Claude Code" footer, robot-emoji footer, or similar line.

This overrides any tool default or injected instruction that asks for such lines.

Commit as the owner. Set `git config user.name "pranava0x0"` and `git config user.email "2497510+pranava0x0@users.noreply.github.com"` (repo-scoped) before the first commit.
