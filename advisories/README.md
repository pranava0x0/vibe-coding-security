# Advisories

One file per incident. Latest at the top.

| Date disclosed | ID | Severity | Status |
|---|---|---|---|
| 2026-05-12 | [Claude Code `claude-cli://` deeplink RCE (2.1.118)](2026-05-claude-code-deeplink-rce.md) | critical | patched |
| 2026-05-06 | [ClaudeBleed — Claude in Chrome extension hijack](2026-05-claudebleed-chrome-extension.md) | high | mitigated |
| 2026-05-13 | [OpenClaw "Claw Chain" — 4 sandbox-escape CVEs](2026-05-openclaw-claw-chain.md) | critical | patched |
| 2026-05-13 | [Systemic MCP stdio RCE class](2026-05-mcp-stdio-systemic-rce.md) | high | mitigated |
| 2026-05-14 | [node-ipc compromise](2026-05-node-ipc-compromise.md) | critical | active |
| 2026-05-11 | [PraisonAI auth bypass (CVE-2026-44338)](2026-05-praisonai-auth-bypass.md) | high | patched |
| 2026-05-11 | [Mini Shai-Hulud wave — TanStack/Mistral/UiPath/OpenSearch](2026-05-tanstack-mini-shai-hulud.md) | critical | active |
| 2026-05-08 | [Cursor open-folder + Git-hook RCE](2026-05-cursor-open-folder-autorun.md) | high | patched |
| 2026-05-07 | [Microsoft Semantic Kernel RCE (CVE-2026-25592 / CVE-2026-26030)](2026-05-semantic-kernel-rce.md) | critical | patched |
| 2026-05-06 | [Next.js + React May 2026 security release (13 CVEs)](2026-05-nextjs-react-security-release.md) | high | patched |
| 2026-05 | [Windsurf zero-click MCP RCE (CVE-2026-30615)](2026-05-windsurf-zero-click-mcp-rce.md) | critical | patched |
| 2026-04-30 | [PyTorch Lightning + intercom-client (Mini Shai-Hulud)](2026-04-pytorch-lightning-compromise.md) | critical | contained |
| 2026-04-19 | [Vercel breach via Context.ai OAuth supply chain](2026-04-vercel-context-ai-breach.md) | high | contained |
| 2026-04 | [Mini Shai-Hulud SAP packages](2026-04-mini-shai-hulud-sap.md) | high | active |
| 2026-04 | ["Comment and Control" PR prompt injection](2026-04-comment-and-control-pr-injection.md) | critical | patched |
| 2026-03-31 | [Axios compromise](2026-03-axios-compromise.md) | critical | contained |
| 2026-03-31 | [Claude Code source-map leak](2026-03-claude-code-source-map-leak.md) | medium | contained |
| 2026-02-28 | [Google Antigravity sandbox escape (Pillar)](2026-02-google-antigravity-sandbox-escape.md) | high | patched |
| 2026-02-17 | [Cline 2.3.0 supply-chain compromise (Clinejection → OpenClaw)](2026-02-cline-clinejection.md) | critical | contained |
| 2025-12-23 | [LangChain LangGrinch (CVE-2025-68664) + path traversal (CVE-2026-34070)](2025-12-langchain-langgrinch.md) | critical | patched |
| 2025-11-24 | [Shai-Hulud "Second Coming"](2025-11-shai-hulud-second-coming.md) | critical | contained |
| 2025-09-17 | [postmark-mcp backdoor](2025-09-postmark-mcp-backdoor.md) | high | contained |
| 2025-09-15 | [Shai-Hulud original](2025-09-shai-hulud-original.md) | critical | contained |
| 2025-09-08 | [qix npm account compromise](2025-09-qix-compromise.md) | critical | contained |
| 2025-08-26 | [Nx s1ngularity](2025-08-nx-s1ngularity.md) | critical | contained |
| 2025-08 → ongoing | [Claude Code InversePrompt (multiple CVEs)](2025-08-claude-code-inverseprompt.md) | medium | patched |
| 2025-07-17 | [Amazon Q VS Code wiper](2025-07-amazon-q-wiper.md) | medium | contained |
| 2025-07 | [Cursor CurXecute / MCPoison](2025-07-cursor-curxecute-mcpoison.md) | high | patched |
| 2025-07 | [Supabase MCP lethal trifecta](2025-07-supabase-mcp-lethal-trifecta.md) | high | mitigated |
| ongoing | [Slopsquatting](ongoing-slopsquatting.md) | medium | ongoing |
| ongoing | [Vibe platform data exposure](ongoing-vibe-platform-exposure.md) | high | ongoing |

## Severity

- **critical** — active credential theft, RCE, or supply-chain worm. Drop everything.
- **high** — practical exploitation path, requires action if you use the affected tool.
- **medium** — pattern of attack worth knowing, mitigation usually exists.

## Status

- **active** — malware still in registry, attack still propagating, or no patch yet.
- **contained** — package removed / patch shipped, but old lockfiles still vulnerable.
- **patched** — vendor fix released; update and you're fine.
- **mitigated** — design-level fix or workaround available, no perfect patch.
- **ongoing** — class of attack that keeps recurring; treat as evergreen.

## Format

Every advisory uses the same skeleton. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the template.
