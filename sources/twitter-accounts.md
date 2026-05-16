# X (Twitter) accounts to follow

> Build a dedicated list. Most supply-chain stories break here hours before the blog posts go up.

## Vendors that ship advisories fast

- **[@SocketSecurity](https://x.com/SocketSecurity)** — first to spot most npm package compromises. Single best signal for npm.
- **[@snyksec](https://x.com/snyksec)** — Snyk Security team. Broad coverage across npm, PyPI, Maven, etc.
- **[@StepSecurityIO](https://x.com/StepSecurityIO)** — focuses on CI/CD and GitHub Actions supply-chain. Caught several of the qix and Shai-Hulud waves.
- **[@aikidosecurity](https://x.com/aikidosecurity)** — fast, detailed package compromise writeups.
- **[@wiz_io](https://x.com/wiz_io)** — Wiz research team; deep writeups on supply-chain and cloud incidents.
- **[@checkmarx](https://x.com/checkmarx)** — strong on PyPI typosquatting and slopsquatting.
- **[@reversinglabs](https://x.com/reversinglabs)** — package reversing and advanced analysis.
- **[@ChainguardLabs](https://x.com/ChainguardLabs)** — supply-chain hardening + sigstore.

## Independent researchers

- **[@GossiTheDog](https://x.com/GossiTheDog)** (Kevin Beaumont) — general infosec broadcast, often first to amplify breaking incidents.
- **[@simonw](https://x.com/simonw)** (Simon Willison) — prompt injection, MCP, "lethal trifecta" framing. Best LLM-security commentator.
- **[@vxunderground](https://x.com/vxunderground)** — malware sample feed. Useful when you want to see what a payload actually does.
- **[@sethmlarson](https://x.com/sethmlarson)** — PSF security developer-in-residence; coined "slopsquatting" with [@AndrewN](https://x.com/AndrewN).
- **[@lirantal](https://x.com/lirantal)** — `npq` author, runs the Node.js security working group.
- **[@RonMasas](https://x.com/RonMasas)** — Backslash Security; deep dives on AI/MCP attacks.

## Vendors of the tools you use

Follow the security or product accounts for whatever you actually use:

- **[@AnthropicAI](https://x.com/AnthropicAI)** + [@claudeai](https://x.com/claudeai) + [@_catwu](https://x.com/_catwu) (Claude Code lead)
- **[@cursor_ai](https://x.com/cursor_ai)** — Cursor releases and CVE notices
- **[@OpenAIDevs](https://x.com/OpenAIDevs)** + [@kevinweil](https://x.com/kevinweil)
- **[@github](https://x.com/github) / [@githubsecurity](https://x.com/githubsecurity)**
- **[@v0](https://x.com/v0)** (Vercel v0)
- **[@vercel](https://x.com/vercel)**
- **[@lovable_dev](https://x.com/lovable_dev)**
- **[@stackblitz](https://x.com/stackblitz)** (Bolt)
- **[@replit](https://x.com/replit)**
- **[@windsurf_ai](https://x.com/windsurf_ai)**
- **[@supabase](https://x.com/supabase)** + [@kiwicopple](https://x.com/kiwicopple)

## Official / government

- **[@CISACyber](https://x.com/CISACyber)** — CISA alerts. Slower than private researchers but authoritative.
- **[@GitHubSecurity](https://x.com/GitHubSecurity)** — GHSA pushes.

## How to set this up

1. Create an X list called "Supply Chain" or "Vibe Security."
2. Add the accounts above (or whichever subset matches your stack).
3. Pin the list. Scan it once a day, ideally in the morning before you start writing code.
4. If you don't use X, the same accounts mostly cross-post to Bluesky / Mastodon / LinkedIn.

## What to do when you see something live

1. Don't panic. Most incidents are scoped narrowly.
2. Check if you use the affected package/tool/MCP.
3. If yes → [ALERTS.md](../ALERTS.md) → matching advisory → matching playbook.
4. If you're the first to spot it for this repo, open an issue with the `new-advisory` template.
