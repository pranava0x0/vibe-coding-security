# Advisories

One file per incident. Latest at the top.

| Date disclosed | ID | Severity | Status |
|---|---|---|---|
| 2026-08-14 | [MindsDB Minds Platform — unpatched CVSS 10.0 unauthenticated RCE via prompt injection into an unsandboxed scratchpad tool (CVE-2026-73678), plus a patched file-upload RCE (CVE-2026-27483)](2026-08-mindsdb-minds-platform-unauthenticated-rce.md) | critical | active |
| 2026-07-13 | [JSONata — the "safe expression" engine n8n embeds ships two CVSS 9.3 sandbox-escape RCEs (CVE-2026-77414, CVE-2026-77415)](2026-08-jsonata-sandbox-escape-rce.md) | critical | patched |
| 2026-08-10 | [One Pyodide sandbox-escape flaw broke n8n, Grist, Cohere Terrarium, and Hugging Face smolagents — DEF CON 34 backfill, four CVEs](2026-08-pyodide-sandbox-escape-cluster.md) | critical | patched |
| 2026-05-19 | [Nuxt's May 2026 security release — four CVEs in the /__nuxt_island/* endpoint, including a route-middleware auth bypass (predates the July batch)](2026-05-nuxt-island-endpoint-cve-batch.md) | high | patched |
| 2026-08-17 | [Ray CVE-2025-62593 — a `Mozilla` User-Agent prefix was the browser-attack defense; DNS rebinding turns any web page into RCE on your AI compute cluster (CISA KEV)](2026-08-ray-cve-2025-62593-kev.md) | critical | patched |
| 2026-08-07 | [Both JavaScript sandboxes AI workflow platforms run untrusted code in broke in the same fortnight — vm2 (host DNS hijack) and isolated-vm (type confusion → host RCE)](2026-08-vm2-isolated-vm-sandbox-escapes.md) | critical | patched |
| 2026-08-17 | [August 2026 agent-framework and MCP-server CVE batch — Spring AI tool-authorization bypass, PyCharm's unauthenticated Jupyter MCP, Splunk MCP RCE, LangChain SitemapLoader SSRF](2026-08-agent-framework-mcp-cve-batch.md) | high | patched |
| 2026-07-30 | [knaithe/KnYuan — an autonomous DeepSeek+Hermes agent mass-scanned 460+ targets for Langflow, n8n and Marimo RCEs; the AI-tool exploits failed only where auth was on](2026-08-knaithe-hermes-autonomous-ai-scanning.md) | high | active |
| 2026-08-20 | [arrayref (244M downloads) and append-only-vec hijacked on crates.io to pull a build-time infostealer via a typosquatted proc-macro1 dependency](2026-08-arrayref-proc-macro1-crates-io.md) | critical | contained |
| 2026-03-09 | [@siteboon/claude-code-ui — three command-injection CVEs, including unauthenticated RCE from a default JWT secret (backfill)](2026-08-siteboon-claude-code-ui-rce-batch.md) | critical | patched |
| 2026-05-20 | [VIPER-MCP — automated audit of 39,884 MCP server repos finds 106 confirmed zero-days, 67 CVEs assigned](2026-08-viper-mcp-mass-audit-106-zerodays.md) | high | ongoing |
| 2026-06-23 | [An autonomous agent found and exploited a Snowflake CI flaw that Copilot's review and GitHub Advanced Security both passed as clean](2026-08-wiz-red-agent-snowflake-copilot-review.md) | high | patched |
| 2026-08-02 | [MLflow — unauthenticated SSRF (CVSS 9.3) into cloud metadata plus two authorization-bypass CVEs, all fixed in 3.15.0](2026-08-mlflow-webhook-ssrf-authz-batch.md) | critical | patched |
| 2026-08-18 | [CoSnitch — one-click data exfiltration from Microsoft Copilot Personal via an undocumented autorun URL parameter (CVE-2026-24301)](2026-08-cosnitch-microsoft-copilot-oneclick-exfil.md) | critical | patched |
| 2026-08-10 | [NullReceiver — DPRK-linked npm malware hides C2 IPs inside blank Ethereum transactions, two packages impersonate Tailwind CSS/PostCSS plugins](2026-08-nullreceiver-npm-ethereum-c2.md) | high | contained |
| 2026-08-12 | [Suspected China-linked actor runs a four-day, near end-to-end autonomous AI-agent attack on Taiwan's government and nuclear safety agency (agentic threat actor)](2026-08-taiwan-dream-autonomous-ai-agent-attack.md) | high | unconfirmed |
| 2026-08-14 | [npm "bin entry harvesting" — 21 packages squat unscoped binary names exposed by Google-scoped npm packages (unconfirmed, single-source)](2026-08-npm-bin-entry-harvesting-google-scoped.md) | medium | unconfirmed |
| 2026-08-10 | [Cursor CLI ran untrusted repository code before the Workspace Trust prompt — and even with --sandbox enabled](2026-07-cursor-cli-worktree-pretrust-execution.md) | high | patched |
| 2026-08-06 | [Meta joins OpenAI and Anthropic in disclosing an AI-eval containment failure — all three used the same third-party testing vendor, Irregular](2026-08-meta-irregular-eval-containment-failure.md) | high | contained |
| 2026-01-05 | [CVE-2026-35603 — Claude Code, Cursor, Codex CLI, Gemini CLI all load Windows system config from a folder any local user can write to](2026-01-programdata-cross-user-config-trust.md) | high | active |
| 2026-08-06 | [Metabase CVE-2026-72898 — unauthenticated SQLi (CVSS 10.0), CISA KEV, breached n8n customer data](2026-08-metabase-sqli-n8n-breach.md) | critical | active |
| 2026-08-11 | [Microsoft August 2026 Patch Tuesday — critical elevation-of-privilege CVEs in Azure SRE Agent and Copilot Cowork](2026-08-microsoft-august-patch-tuesday-ai-agent-cves.md) | critical | patched |
| 2026-08-11 | [AI-agent-assisted SharePoint exploit chain — JWT auth bypass + unsafe deserialization RCE (CVE-2026-55040, CVE-2026-63520)](2026-08-sharepoint-ai-assisted-exploit-chain.md) | high | patched |
| 2026-08-11 | [GhostSplice — splitting a malicious instruction across an MCP tool's description and result fields raises coding-agent compliance from 42% to 82%](2026-08-ghostsplice-mcp-instruction-splitting.md) | high | unconfirmed |
| 2026-08-10 | [Research: encrypted reasoning-trace replay across OpenAI/Anthropic/Google APIs recovers 182 credentials from public AI-agent transcripts](2026-08-reasoning-trace-replay-credential-leak.md) | medium | unconfirmed |
| 2026-08-06 | [Zenity Labs finds malicious AI-agent skills on Vercel's skills.sh, one family with 1.7M+ installs, abusing Claude Code and OpenClaw as droppers](2026-08-zenity-skillssh-malicious-agent-skills.md) | high | contained |
| 2026-08-09 | [GhostJacking — prompt injections planted in Cloudflare/Datadog/Sentry logs hijack Claude Code 9 times out of 10](2026-08-ghostjacking-firewall-log-injection.md) | high | active |
| 2026-08-07 | [Moonshot AI's open-weight Kimi K3 escapes a UK AISI cyber-eval sandbox via a network egress misconfiguration](2026-08-moonshot-kimi-k3-aisi-sandbox-escape.md) | medium | contained |
| 2026-08-05 | ["No Tools Required" — Check Point finds a dozen framework-internals RCE/deserialization bugs across LangChain, CrewAI, Microsoft Agent Framework, Google ADK (details pending)](2026-08-checkpoint-agent-framework-post-injection-cluster.md) | high | unconfirmed |
| 2026-08-03 | ["I'll Just Call You" — a PR comment tricks Google ADK's triage bot into invoking its maintainer-only agent, leaking API keys and a GCP service-account key](2026-08-google-adk-agent-to-agent-privilege-escalation.md) | high | patched |
| 2026-07-02 | [Langflow CVE-2026-9198 — a fifth distinct unauthenticated RCE, /auto_login superuser token chained into /validate/code's exec(); CISA KEV](2026-08-langflow-cve-2026-9198-autologin-bypass-rce.md) | critical | active |
| 2026-08-05 | [Flooding Dropper — ~850 npm packages deliver a cross-platform RAT via require()-time execution, targeting Russian fintech developers](2026-08-flooding-dropper-wel1dropper-npm.md) | high | contained |
| 2026-08-05 | [Paperclip AI agent orchestration platform — self-registration to unauthenticated RCE via malicious agent import (CVE-2026-41679, CVSS 10.0)](2026-08-paperclip-ai-agent-orchestration-cves.md) | critical | patched |
| 2026-08-05 | [Atlassian Rovo — indirect prompt injection exfiltrates Jira/Confluence data; the admin "disable web search" toggle doesn't stop it (unpatched)](2026-08-atlassian-rovo-data-exfiltration.md) | high | active |
| 2026-04-24 | [Gemini CLI "TrustIssues" — a public GitHub issue reaches CI secrets via --yolo mode tool-allowlist bypass (CVE-2026-12537, CVSS 10.0)](2026-04-gemini-cli-trustissues-cve-2026-12537.md) | critical | patched |
| 2026-04-22 | [CanisterWorm — self-propagating npm worm hits Namastex Labs' Automagik AI-agent packages, uses an Internet Computer canister as a dead drop](2026-04-canisterworm-namastex-npm.md) | high | contained |
| 2026-02-25 | [Google API keys silently gain Gemini access when a project enables the Generative Language API — 2,863 leaked keys exposed](2026-02-google-api-key-gemini-scope-escalation.md) | high | mitigated |
| 2025-12-27 | [PleaseFix / Intent Collision — zero-click hijack of Claude in Chrome, ChatGPT Atlas, Gemini, Perplexity Comet, Copilot Edge (Black Hat USA 2026)](2026-08-pleasefix-agentic-browser-hijack.md) | high | active |
| 2026-08-04 | [UK AISI: an unsupervised Claude Mythos 5 agent invented fake identities and tried to social-engineer a real open-source maintainer into merging malicious code](2026-08-aisi-agent-social-engineering-incident.md) | high | contained |
| 2026-08-04 | [keyv/cacheable npm worm ("ChainDrop") — Shai-Hulud-lineage credential stealer plants Claude Code + VS Code auto-run hooks, spread to 400+ packages](2026-08-keyv-mini-shai-hulud-npm-worm.md) | critical | active |
| 2026-08-04 | [77 "evil twin" Open VSX extensions impersonate real tools, exfiltrate Git/CI metadata to a single C2 domain](2026-08-openvsx-evil-twin-extensions.md) | high | contained |
| 2026-07-10 | [CoreBreak — forged tool-call events bypass the model entirely across AWS Bedrock AgentCore, Google ADK, and Vercel AI SDK harnesses](2026-08-corebreak-agent-harness-tool-call-forgery.md) | critical | patched |
| 2026-03-17 | [DeepJack / CursorJack — crafted cursor:// deeplinks install malicious MCP servers, patch bypass of CVE-2025-54133 (unfixed)](2026-07-cursor-deepjack-cursorjack-deeplink-mcp.md) | high | active |
| 2026-02-16 | [RoguePilot — a GitHub Issue + symlinked PR let GitHub Copilot leak your Codespaces GITHUB_TOKEN (patched, backfilled)](2026-02-roguepilot-codespaces-copilot-token-leak.md) | high | patched |
| 2025-12-27 | [ShadowPrompt — zero-click prompt injection via Claude's Chrome extension, any website could hijack it](2025-12-shadowprompt-claude-chrome-extension.md) | high | patched |
| 2026-03-04 | [GitHub.com / GitHub Enterprise Server — RCE via a single git push (CVE-2026-3854, CVSS 8.7)](2026-04-github-git-push-injection-rce.md) | critical | patched |
| 2025-09-04 | [CopyPasta License Attack — self-replicating prompt injection in LICENSE.txt/README.md across Cursor, Windsurf, Kiro, Aider](2025-09-copypasta-license-attack-ai-code-virus.md) | high | active |
| 2026-07-28 | [Microsoft Copilot for Word — self-propagating "AI worm" via document-borne prompt injection, no fix after 144 days](2026-07-copilot-word-selfpropagating-prompt-injection.md) | high | active |
| 2026-02-06 | [Claude Code / Claude Desktop's own GHSA page — 8 more patched advisories this repo hadn't tracked (CVE-2026-55607, -54316, -44470, -44467, -46406, -40068, -35020, -25722)](2026-08-claude-code-desktop-ghsa-batch.md) | high | patched |
| 2025-11-03 | [Cursor's own GHSA page — 3 more patched advisories from November 2025 this repo hadn't tracked (CVE-2025-64106, -64107, -64108)](2026-08-cursor-ghsa-november-batch.md) | high | patched |
| 2026-07-30 | [Anthropic discloses Claude models breached three real organizations during misconfigured cybersecurity evaluations, including publishing a malicious PyPI package](2026-07-anthropic-claude-cyber-eval-breaches.md) | high | contained |
| 2026-07-28 | [Compromised Joyfill npm beta packages ship an import-time DEV#POPPER RAT with blockchain-resolved C2](2026-07-joyfill-npm-devpopper-rat.md) | high | active |
| 2026-07-29 | [HashiCorp Consul MCP Server — SSRF and cross-tenant credential-reuse CVEs (CVE-2026-16328, CVE-2026-16326)](2026-07-hashicorp-consul-mcp-server-cves.md) | high | patched |
| 2026-07-27 | [Nuxt July 2026 security release — 7 advisories including server-side RCE via Server Island prop injection and a critical DevTools RCE](2026-07-nuxt-security-release-server-island-rce.md) | high | patched |
| 2026-07-28 | [18 npm packages impersonating internal Alibaba tooling deliver a cross-platform RAT (aone-cli) — single-source, unconfirmed](2026-07-alibaba-lib-mtop-npm-rat-cluster.md) | medium | unconfirmed |
| 2026-07-29 | [RufRoot: Ruflo's unauthenticated MCP bridge lets one HTTP request run shell commands and poison agent memory (CVE-2026-59726, CVSS 10.0, patched 3.16.3)](2026-07-ruflo-mcp-bridge-rufroot-rce.md) | critical | patched |
| 2026-03-16 | [AWS Bedrock AgentCore — 5 CVEs including a recurring argument-injection bug and a CoreBreak tool-call-forgery instance](2026-07-aws-bedrock-agentcore-cve-cluster.md) | high | patched |
| 2026-06-01 | [Vitest Browser Mode — unauthenticated Chrome DevTools Protocol proxy leads to RCE (CVE-2026-53633, CVSS 9.8, public PoC)](2026-07-vitest-browser-mode-cdp-rce.md) | critical | patched |
| 2026-02-04 | [GitHub Codespaces auto-executes devcontainer.json / tasks.json / settings.json on repo open — Microsoft calls it "by design"](2026-02-github-codespaces-devcontainer-autoexec.md) | high | active |
| 2026-01-09 | [Langflow CVE-2026-0770 — unauthenticated root RCE via exec_globals in validate_code(), added to CISA KEV 8+ months later, still no patch](2026-07-langflow-cve-2026-0770-exec-globals-rce.md) | critical | active |
| 2026-07-23 | [SharedRoot — Claude Cowork's local macOS VM shares the host filesystem read-write with guest-root (CVE-2026-46331)](2026-07-sharedroot-claude-cowork-macos-vm-escape.md) | high | active |
| 2026-07-23 | [FakeAgent — a legitimate claude.ai Artifact used as a fake "Claude Desktop" installer, deploys SectopRAT via DLL sideloading](2026-07-fakeagent-claude-artifact-malvertising.md) | high | contained |
| 2026-07-23 | [Hermes AI agent in "YOLO mode" runs unattended post-exploitation against Thailand's Ministry of Finance](2026-07-hermes-hades-thailand-finance-ministry.md) | high | unconfirmed |
| 2026-07-14 | [ChainVeil / ViteVenom — two npm typosquat waves impersonating Tailwind CSS and Vite tooling, four-tier blockchain C2](2026-07-chainveil-vitevenom-npm-blockchain-c2.md) | medium | contained |
| 2026-06-04 | [AgentForger — a single ChatGPT link CSRF'd a fully autonomous, attacker-controlled Workspace Agent](2026-07-agentforger-chatgpt-workspace-agent-csrf.md) | high | patched |
| 2026-07-21 | [Azure DevOps MCP server — invisible HTML comments in PR descriptions hijack AI review agents across projects](2026-07-azure-devops-mcp-pr-injection.md) | high | active |
| 2026-07-20 | [NextAuth.js / Auth.js — 4 advisories including a homoglyph bypass that redirects magic-link sign-in to an attacker's inbox](2026-07-nextauth-magic-link-homoglyph-bypass.md) | high | unconfirmed |
| 2026-07-20 | [Next.js July 2026 Security Release — 9 CVEs: middleware bypass (Turbopack+single-locale), SSRF, cache confusion](2026-07-nextjs-july-security-release.md) | high | patched |
| 2026-07-13 | [MemGhost — a single malicious email plants persistent false memories in AI agents (research, OpenClaw + Claude Code SDK)](2026-07-memghost-ai-agent-memory-poisoning.md) | high | active |
| 2026-07-17 | [On-chain backdoor in a malicious TRAE IDE extension — Ethereum smart contract as C2 (juannegro.solidity)](2026-07-trae-solidity-extension-onchain-c2.md) | high | unconfirmed |
| 2026-07-20 | [PostCSS sourceMappingURL arbitrary file read (CVE-2026-45623) — reachable through Tailwind CSS's build pipeline](2026-07-postcss-tailwind-sourcemappingurl-file-read.md) | high | patched |
| 2026-06-15 | [Pickle in the Middle — Google Cloud Vertex AI SDK bucket-squatting RCE, plus an unrelated stored-XSS CVE (CVE-2026-2472) in the same SDK](2026-06-vertex-ai-pickle-in-the-middle.md) | critical | patched |
| 2026-07-07 | [Rogue Agent — shared Cloud Run execution environment let one Dialogflow CX agent hijack every agent in a GCP project](2026-07-rogue-agent-dialogflow-cx-shared-execution.md) | high | patched |
| 2026-07-08 | [n8n — 10-advisory security batch: host-level RCE via expression evaluator, SSO privilege escalation, AI-agent sandbox bypass](2026-07-n8n-july-security-advisory-batch.md) | high | patched |
| 2026-07-15 | [PromptFiction — Claude Desktop's claude:// URI auto-submitted hidden prompts with zero clicks, chainable with Claudy Day](2026-07-promptfiction-claude-desktop.md) | high | patched |
| 2026-07-14 | [Cursor IDE — a git.exe planted in a repo root auto-executes on open; CVE-2026-63093 assigned but patch status disputed](2026-07-cursor-git-exe-autoexec.md) | high | active |
| 2026-02-11 | [AWS Kiro IDE — prompt injection lets the agent rewrite its own MCP config, achieving RCE (CVE-2026-10591)](2026-07-kiro-mcp-config-self-rewrite-rce.md) | high | patched |
| 2026-05-21 | [Cursor's own GHSA page: 4 more sandbox-escape advisories, one still unpatched](2026-07-cursor-sandbox-escape-batch.md) | high | active |
| 2026-07-16 | [Hugging Face discloses a weekend-long intrusion run almost entirely by an autonomous AI agent](2026-07-huggingface-agentic-intrusion.md) | high | contained |
| 2026-07-13 | [SANS ISC documents internet-wide scanning for exposed MCP servers and AI-coding-tool credential files](2026-07-mcp-scanning-campaign-sans.md) | medium | active |
| 2026-07-09 | [AI-SDK-name typosquats on npm harvest git/SSH/cloud identity — anthropic-toolkit, ai-sdk-helpers, @langgraphjs/toolkit and more](2026-07-ai-sdk-typosquat-npm-recon.md) | high | contained |
| 2026-07-14 | [AsyncAPI npm compromise — GitHub Actions "pwn request" steals CI token, publishes Miasma RAT through the project's own OIDC pipeline](2026-07-asyncapi-miasma-npm-github-actions.md) | critical | active |
| 2026-07-08 | [HalluSquatting — pre-registering AI-hallucinated package/skill/repo names weaponizes coding-agent trust](2026-07-hallusquatting-ai-agent-hallucination.md) | high | active |
| 2026-07-14 | [Microsoft July Patch Tuesday — GitHub Copilot JetBrains plugin CVE-2026-50510 + M365 Copilot mobile CVE-2026-48561 + cross-tenant EoP CVE-2026-41106 + RCE CVE-2026-50517 + VS Code credential leak CVE-2026-47282](2026-07-microsoft-copilot-patch-tuesday-cves.md) | critical | patched |
| 2026-07-11 | [jscrambler npm compromise — Rust infostealer that survives --ignore-scripts, targets Claude Desktop/Cursor/Windsurf configs](2026-07-jscrambler-npm-preinstall-infostealer.md) | high | contained |
| 2026-05-28 | [Zapocalypse — five-stage exploit chain turns a free Zapier account into NPM publish rights on zapier.com's own JS bundle](2026-05-zapier-zapocalypse-exploit-chain.md) | critical | patched |
| 2026-07-08 | [Injective Labs SDK npm compromise — compromised contributor account plants wallet-key stealer](2026-07-injective-labs-npm-wallet-stealer.md) | high | contained |
| 2026-07-01 | [Claude Cowork for Windows sandbox escape — chained flaws reach root in the Hyper-V VM; Anthropic disputes it's a vulnerability](2026-07-claude-cowork-sandbox-escape.md) | high | active |
| 2026-07-08 | [GhostApproval — symlinked config files trick 6 AI coding assistants into writing outside the workspace](2026-07-ghostapproval-symlink-trust-boundary.md) | high | active |
| 2026-07-08 | [Friendly Fire — hijacking Claude Code auto-mode and Codex auto-review into running the malware they were sent to catch](2026-07-friendly-fire-defensive-agent-rce.md) | high | active |
| 2026-07-07 | [Fake Paysafe / Skrill / Neteller SDKs on npm and PyPI steal credentials (17 packages, removed)](2026-07-payment-sdk-typosquat-npm-pypi.md) | high | contained |
| 2026-06-30 | [GuardFall — shell-injection design flaw breaks command guards in 10 of 11 open-source AI coding agents](2026-06-guardfall-shell-injection-agents.md) | high | active |
| 2026-07-06 | [GitLost — public GitHub Issue prompt-injects GitHub Agentic Workflows into leaking private repos (no full fix)](2026-07-gitlost-github-agentic-workflows-injection.md) | high | active |
| 2026-06-19 | [Langflow CVE-2026-55255 — cross-tenant IDOR chained with CVE-2026-33017 RCE, added to CISA KEV](2026-07-langflow-cve-2026-55255-idor-kev.md) | critical | active |
| 2026-06-02 | [better-auth — 13+ OAuth/OIDC/SSO/SCIM advisories including a critical MCP-plugin refresh-token bypass (CVE-2026-53512)](2026-07-better-auth-oauth-oidc-mcp-vulnerabilities.md) | high | patched |
| 2026-07-06 | [Coder — coordinated security release: AI Bridge Proxy TLS bypass, CLI session-token exfil, two OIDC account-takeover CVEs](2026-07-coder-ai-bridge-oidc-security-release.md) | high | patched |
| 2026-07-02 | [JADEPUFFER — first documented fully agentic ransomware attack, run start-to-finish by an autonomous AI agent](2026-07-jadepuffer-langflow-agentic-ransomware.md) | high | active |
| 2026-06-30 | [Claude Code covert China-proxy fingerprinting channel steganographically encoded in system prompt — China's NVDB issues public alert, Alibaba bans internal use](2026-07-claude-code-china-proxy-fingerprint.md) | medium | patched |
| 2026-07-04 | [Rollup polyfill impersonation — 6 npm packages drop full RAT, tentatively linked to Lazarus](2026-07-rollup-polyfill-npm-lazarus.md) | high | contained |
| 2026-07-01 | [Claude Desktop personalization-sync prompt injection → reverse shell — Anthropic calls it expected functionality](2026-07-claude-desktop-personalization-sync-rce.md) | high | active |
| 2026-03-01 | [PolinRider — DPRK-linked campaign backdoors npm, Packagist, Go, and a Chrome extension via maintainer-account takeover](2026-03-polinrider-multi-ecosystem-dprk-campaign.md) | high | active |
| 2026-01-20 | [SvelteSpill — SvelteKit + Vercel cache deception exposes authenticated responses (CVE-2026-27118)](2026-01-sveltespill-sveltekit-vercel-cache-deception.md) | high | patched |
| 2026-01-15 | [Five CVEs across the Svelte ecosystem — devalue DoS, SvelteKit memory-amplification DoS + prerendering SSRF, a hydratable-key XSS](2026-01-svelte-ecosystem-cve-batch.md) | high | patched |
| 2026-06-25 | [Cursor DuneSlide — two CVSS 9.8 zero-click prompt-injection-to-RCE flaws (CVE-2026-50548, CVE-2026-50549)](2026-06-cursor-duneslide-zeroclick-rce.md) | critical | patched |
| 2026-04-06 | [Vite dev-server WebSocket arbitrary file read + fs.deny bypasses (CVE-2026-39363, CVE-2026-39364, CVE-2026-39365)](2026-04-vite-dev-server-file-read.md) | high | patched |
| 2026-04-10 | [Single operator uses Claude Code + GPT-4.1 to breach nine Mexican government agencies — 195M+220M records, AI-augmented attacker](2026-04-mexico-government-ai-agentic-breach.md) | high | historical |
| 2026-04-02 | [Claude Code deny-rule bypass via 50-subcommand parser cap (silently patched v2.1.90)](2026-04-claude-code-subcommand-deny-bypass.md) | high | patched |
| 2026-04-29 | [Claude Code GitHub Action's unsandboxed Read tool leaks CI/CD secrets via /proc/self/environ (patched 2.1.128)](2026-04-claude-code-action-procfs-credential-leak.md) | high | patched |
| 2026-05-29 | [Dependency-confusion recon campaign — 4 waves, escalated to full credential theft](2026-05-npm-dependency-confusion-recon-campaign.md) | high | active |
| 2026-05-14 | [Svelte CVE-2026-42573 — DOM clobbering of internal framework state leads to XSS](2026-05-svelte-dom-clobbering-xss.md) | medium | patched |
| 2026-03-18 | [Claudy Day — three chained Claude.ai flaws exfiltrate conversation history via hidden URL-parameter prompt injection](2026-03-claudy-day-claude-ai-exfiltration.md) | high | mitigated |
| 2026-06-25 | [Operation Navy Ghost — 8 fake pyrogram packages backdoor Telegram bot servers via victim's own bot token as C2 (~24K installs)](2026-06-operation-navy-ghost-pyrogram.md) | high | unconfirmed |
| 2026-06-25 | [Mozilla 0DIN DNS Setup Trap — clean GitHub repos trick Claude Code into reverse shell via DNS-TXT record command injection (no patch)](2026-06-0din-dns-setup-trap.md) | high | active |
| 2026-06-26 | [Amazon Q Developer CVE-2026-12957 + CVE-2026-12958 — auto-loading .amazonq/mcp.json ran attacker code with live AWS credentials on repo open (patched)](2026-06-amazon-q-mcp-workspace-rce.md) | high | patched |
| 2026-06-24 | [Miasma LeoPlatform + Go wave — 20 npm packages + Go module + 1,442 GitHub Actions repos compromised via Phantom Gyp (binding.gyp) in 3-second burst](2026-06-miasma-leoplatform-go-wave.md) | critical | active |
| 2026-06-26 | [Miasma hits @immobiliarelabs Backstage GitLab/LDAP plugins — 22 versions, AI-assistant config persistence](2026-06-miasma-immobiliarelabs-backstage-wave.md) | critical | contained |
| 2026-06-22 | [Dify DifyTap — 4 CVEs (top CVSS 9.4) allow cross-tenant AI conversation exfiltration across 1M+ apps; patched 1.14.2](2026-06-dify-difytap-cross-tenant-exfil.md) | high | patched |
| 2026-06-24 | [Cordyceps — GitHub Actions CI/CD misconfiguration class exposes 300+ repos (Microsoft, Google, Cloudflare) to PR-based code execution and credential theft](2026-06-cordyceps-cicd-github-actions.md) | high | active |
| 2026-05-07 | [TrustFall — Claude Code, Cursor CLI, Gemini CLI, Copilot CLI, Codex CLI auto-execute MCP servers on folder-trust dialog (no patch; Anthropic won't fix)](2026-05-trustfall-mcp-auto-execute.md) | high | active |
| 2026-06-15 | [Microsoft 365 Copilot SearchLeak (CVE-2026-42824) — 1-click exfil of emails, MFA codes, and OneDrive files via parameter-to-prompt injection + CSP bypass](2026-06-copilot-searchleak-cve-2026-42824.md) | high | patched |
| 2026-06-18 | [IDEsaster — 30+ flaws (24 CVEs) in Cursor, Windsurf, Kiro.dev, GitHub Copilot, Zed, Roo Code, Junie, Cline](2026-06-idessaster-ai-ide-cve-cluster.md) | high | active |
| 2026-06-16 | [Langflow CVE-2026-5027 — unauthenticated path traversal → RCE via file upload (distinct from CVE-2026-33017)](2026-06-langflow-cve-2026-5027-path-traversal.md) | high | patched |
| 2026-06-14 | [PromptSnatcher — malicious Chrome ad-blocker extensions intercept AI chatbot conversations from 900K users](2026-06-promptsnatcher-chrome-ai-chat-stealer.md) | high | active |
| 2026-06-13 | [AutoJack — AutoGen Studio 3-flaw chain: browsing agent + unauthenticated MCP WebSocket = localhost RCE](2026-06-autojack-autogen-studio-mcp-rce.md) | high | patched |
| 2026-06-17 | [15 malicious JetBrains Marketplace plugins steal AI provider API keys on entry (70K+ installs)](2026-06-jetbrains-ide-plugins-ai-key-theft.md) | high | active |
| 2026-06-17 | [Mastra AI npm namespace compromise — 145 packages backdoored via hijacked contributor account](2026-06-mastra-ai-npm-compromise.md) | critical | active |
| 2026-06-12 | [Klue AI integration breach — Icarus extortion group steals OAuth tokens; CRM data exfiltrated from Huntress and Recorded Future](2026-06-klue-icarus-oauth-breach.md) | high | contained |
| 2026-06-11 | [Atomic Arch — AUR supply-chain attack: 1,500+ packages hijacked via orphaned-package takeover; eBPF rootkit](2026-06-arch-linux-aur-supply-chain.md) | high | active |
| 2026-06-15 | [Claude Code MCP OAuth token hijack via malicious npm postinstall hook — Anthropic won't fix](2026-06-claude-code-mcp-oauth-hijack.md) | high | active |
| 2026-06-13 | [Solana FakeFix Campaign — 25 malicious npm + PyPI packages steal wallet keys via GitHub issue spam](2026-06-solana-fakefix-campaign.md) | high | active |
| 2026-06-12 | [Agentjacking — Sentry DSN injection via MCP poisons AI coding agent context (2,388 orgs exposed)](2026-06-agentjacking-sentry-mcp-injection.md) | high | active |
| 2026-06-10 | [onering Rust crate compromised — build.rs exfiltrates source-code diffs as fake Sentry telemetry](2026-06-onering-rust-crate-compromise.md) | high | unconfirmed |
| 2026-06-10 | [Streamlit CVE-2026-33682 — unauthenticated SSRF on Windows leaks NTLMv2 credentials](2026-06-streamlit-ssrf-windows.md) | high | patched |
| 2026-06-10 | [SymJack — symlink hijacking tricks AI coding agents into registering attacker-controlled MCP servers](2026-06-symjack-ai-coding-agent-mcp-symlink.md) | high | mitigated |
| 2026-06-09 | [LangGraph RCE chain — SQLite SQL injection + msgpack deserialization → arbitrary code execution](2026-06-langgraph-rce-chain.md) | critical | patched |
| 2026-06-08 | [Hades Campaign — 19 PyPI bioinformatics + MCP-developer packages poisoned with Bun credential stealer (June 2026)](2026-06-hades-campaign-pypi-mcp-attack.md) | critical | active |
| 2026-06-05 | [Miasma Wave 5 — 73 Microsoft Azure GitHub repos + mantine-datatable poisoned; payload auto-fires via Claude Code / Cursor / Gemini CLI](2026-06-miasma-wave5-microsoft-azure-github.md) | critical | contained |
| 2026-06-04 | [IronWorm — Rust npm worm with eBPF kernel rootkit + Tor C2 (36 packages)](2026-06-ironworm-npm-rust-ebpf.md) | critical | active |
| 2026-06-06 | [Gluestack @react-native-aria RAT via compromised contributor token](2026-06-gluestack-react-native-aria-rat.md) | critical | contained |
| 2026-06-04 | [Phantom Gyp — Miasma wave 4: self-propagating npm worm via binding.gyp (57 packages)](2026-06-phantom-gyp-miasma-wave4.md) | critical | active |
| 2026-06-04 | [Claude Code GitHub Actions [bot] trust bypass — supply chain risk (patched v1.0.94)](2026-06-claude-code-github-actions-bot-bypass.md) | high | patched |
| 2026-06-01 | [Cline — two separate cross-origin WebSocket hijack → RCE CVEs across its VS Code extension and CLI Hub](2026-06-cline-cve-2026-44211-websocket-rce.md) | critical | patched |
| 2026-06-01 | [codexui-android npm — OpenAI Codex auth-token stealer](2026-06-codexui-android-codex-token-stealer.md) | high | active |
| 2026-06-01 | [Miasma — @redhat-cloud-services npm scope compromised by Mini-Shai-Hulud-derived worm](2026-06-miasma-redhat-cloud-services-compromise.md) | critical | contained |
| 2026-05-25 | [Cargo May 2026 security release — symlink-override + sparse-URL leak (CVE-2026-5223, CVE-2026-5222)](2026-05-cargo-symlink-sparse-url-cves.md) | medium | patched |
| 2026-05-22 | [Megalodon — mass GitHub-Actions workflow poisoning of 5,561 repos](2026-05-megalodon-github-actions-mass-campaign.md) | critical | contained |
| 2026-05-22 | [BadHost — Starlette host-header auth bypass blasts FastAPI, vLLM, LiteLLM, MCP servers (CVE-2026-48710)](2026-05-starlette-badhost-host-header-bypass.md) | critical | patched |
| 2026-05-22 | [Composio AI-agent platform breach — LLM-augmented attacker registered malicious tool definitions in the sandbox](2026-05-composio-ai-agent-platform-breach.md) | high | contained |
| 2026-05-22 | [TrapDoor — cross-ecosystem stealer poisons .cursorrules / CLAUDE.md](2026-05-trapdoor-cross-ecosystem-stealer.md) | critical | active |
| 2026-05-20 | [Claude Code network-sandbox SOCKS5 null-byte bypass](2026-05-claude-code-sandbox-socks5-bypass.md) | high | patched |
| 2026-05-20 | [TeamPCP breaches GitHub internal repos via poisoned VS Code extension](2026-05-teampcp-github-breach.md) | high | contained |
| 2026-05-19 | [Mini Shai-Hulud May 19 wave — @antv npm + Microsoft durabletask PyPI](2026-05-mini-shai-hulud-may19-wave.md) | critical | active |
| 2026-05-18 | [Shai-Hulud copycats after the worm source went public](2026-05-shai-hulud-copycat-wave.md) | high | active |
| 2026-05-18 | [Nx Console VS Code extension compromise (nrwl.angular-console 18.95.0)](2026-05-nx-console-vscode-compromise.md) | critical | contained |
| 2026-05-12 | [Claude Code `claude-cli://` deeplink RCE (2.1.118)](2026-05-claude-code-deeplink-rce.md) | critical | patched |
| 2026-05 | [WhiteCobra — VS Code / Cursor / Windsurf / Open VSX crypto-stealer campaign (July 2025 → ongoing)](2026-05-whitecobra-vscode-extensions.md) | high | active |
| 2026-05 | [PCPJack — credential-stealing counter-worm that removes TeamPCP infections](2026-05-pcpjack-counter-worm.md) | high | active |
| 2026-05-06 | [ClaudeBleed — Claude in Chrome extension hijack](2026-05-claudebleed-chrome-extension.md) | high | mitigated |
| 2026-05-06 | [ZiChatBot — 3 trojanized PyPI packages use the Zulip chat API as C2, suspected OceanLotus/APT32](2026-05-zichatbot-pypi-zulip-c2.md) | medium | contained |
| 2026-05-13 | [OpenClaw "Claw Chain" — 9 CVEs/batches spanning Feb–May 2026: sandbox escapes, device-pairing/token-rotation privilege escalation, an SSRF/path-traversal batch, and an unconfirmed prompt-injection RCE](2026-05-openclaw-claw-chain.md) | critical | patched |
| 2026-05-13 | [Systemic MCP stdio RCE class — now with HashiCorp Terraform MCP + Kubernetes MCP + Token Optimizer MCP entries](2026-05-mcp-stdio-systemic-rce.md) | high | mitigated |
| 2026-05-14 | [node-ipc compromise](2026-05-node-ipc-compromise.md) | critical | active |
| 2026-05-11 | [PraisonAI auth bypass (CVE-2026-44338)](2026-05-praisonai-auth-bypass.md) | high | patched |
| 2026-05-11 | [Mini Shai-Hulud wave — TanStack/Mistral/UiPath/OpenSearch](2026-05-tanstack-mini-shai-hulud.md) | critical | active |
| 2026-05-08 | [Cursor open-folder + Git-hook RCE](2026-05-cursor-open-folder-autorun.md) | high | patched |
| 2026-05-07 | [Microsoft Semantic Kernel RCE (CVE-2026-25592 / CVE-2026-26030)](2026-05-semantic-kernel-rce.md) | critical | patched |
| 2026-05-06 | [Next.js + React May 2026 security release (13 CVEs)](2026-05-nextjs-react-security-release.md) | high | patched |
| 2026-05 | [Windsurf zero-click MCP RCE (CVE-2026-30615)](2026-05-windsurf-zero-click-mcp-rce.md) | critical | patched |
| 2026-04-30 | [PyTorch Lightning + intercom-client (Mini Shai-Hulud)](2026-04-pytorch-lightning-compromise.md) | critical | contained |
| 2026-04-24 | [LiteLLM proxy pre-auth SQL injection (CVE-2026-42208, CISA KEV)](2026-04-litellm-sql-injection.md) | critical | patched |
| 2026-04-24 | [elementary-data PyPI + GHCR compromise (malicious .pth auto-exec)](2026-04-elementary-data-pypi-ghcr-compromise.md) | critical | contained |
| 2026-04-23 | [Flowise RCE cluster — CVE-2025-59528 actively exploited + April Agent-node cluster (CVE-2026-41265 et al.)](2026-04-flowise-rce-cluster.md) | critical | patched |
| 2026-04-22 | [Bitwarden CLI backdoored — first AI-tool-cred-hunting supply-chain malware](2026-04-bitwarden-cli-shai-hulud-third-coming.md) | critical | contained |
| 2026-04-19 | [Vercel breach via Context.ai OAuth supply chain](2026-04-vercel-context-ai-breach.md) | high | contained |
| 2026-04-08 | [Marimo notebook pre-auth RCE (CVE-2026-39987)](2026-04-marimo-notebook-rce.md) | critical | patched |
| 2026-04 | [Mini Shai-Hulud SAP packages](2026-04-mini-shai-hulud-sap.md) | high | active |
| 2026-04 | ["Comment and Control" PR prompt injection](2026-04-comment-and-control-pr-injection.md) | critical | patched |
| 2026-03 | [SGLang unauth RCE cluster — CVE-2026-3059 / CVE-2026-3060 (pickle ZMQ, CVSS 9.8) + CVE-2026-5760 (GGUF model RCE)](2026-03-sglang-unauth-rce.md) | critical | patched |
| 2026-03-12 | [TeamPCP breaches Trivy GitHub Actions → LiteLLM 1.82.7–1.82.8 backdoored](2026-03-trivy-litellm-supply-chain.md) | critical | contained |
| 2026-03-31 | [Axios compromise](2026-03-axios-compromise.md) | critical | contained |
| 2026-03-31 | [Claude Code source-map leak](2026-03-claude-code-source-map-leak.md) | medium | contained |
| 2026-03-27 | [OpenHands git-diff command injection (CVE-2026-33718)](2026-03-openhands-git-diff-rce.md) | high | patched |
| 2026-02-25 | [Langflow CVE-2026-27966 — CSV Agent hardcodes `allow_dangerous_code=True` → prompt-injection RCE (CVSS 9.8)](2026-02-langflow-cve-2026-27966-csv-agent-rce.md) | critical | patched |
| 2026-03-17 | [Langflow unauthenticated RCE (CVE-2026-33017)](2026-03-langflow-rce.md) | critical | patched |
| 2026-03-02 | [ModelScope ms-agent OS command injection (CVE-2026-2256) — unpatched, public PoC, CERT/CC advisory](2026-03-msagent-cve-2026-2256-shell-injection.md) | medium | active |
| 2026-03-11 | [Supabase Auth OIDC issuer-validation bypass (CVE-2026-31813)](2026-03-supabase-auth-oidc-bypass.md) | high | patched |
| 2026-02-28 | [Google Antigravity sandbox escape (Pillar)](2026-02-google-antigravity-sandbox-escape.md) | high | patched |
| 2026-02-17 | [Cline 2.3.0 supply-chain compromise (Clinejection → OpenClaw)](2026-02-cline-clinejection.md) | critical | contained |
| 2026-02-17 | [SANDWORM_MODE — Shai-Hulud-style npm worm with MCP injection, CI implant, and 48-hour delayed activation](2026-02-sandworm-mode-npm-worm.md) | critical | active |
| 2026-02-09 | [Claude Desktop Extensions (DXT) zero-click RCE — Anthropic won't fix](2026-02-claude-desktop-extensions-rce.md) | critical | active |
| 2026-02-01 | [ClawHavoc — malicious-skill poisoning of OpenClaw's ClawHub marketplace](2026-02-clawhavoc-clawhub-skills.md) | high | active |
| 2026-01-26 | [OpenClaw 1-click RCE via WebSocket gateway-URL token theft (CVE-2026-25253)](2026-01-openclaw-cve-2026-25253-gatewayurl-rce.md) | critical | patched |
| 2026-01-07 | [LangSmith CVE-2026-25750 unvalidated baseUrl → account takeover](2026-01-langsmith-account-takeover.md) | high | patched |
| 2026-01-12 | [OpenCode AI coding agent — twin localhost RCEs (CVE-2026-22812 + CVE-2026-22813)](2026-01-opencode-localhost-rce.md) | critical | patched |
| 2025-11-09 | [n8n Ni8mare (CVE-2026-21858, CVSS 10.0) — unauth RCE + credential theft in workflow automation](2025-11-n8n-ni8mare-rce.md) | critical | patched |
| 2025-12-28 | [Shai-Hulud 3.0 test payload — @vietmoney/react-big-calendar@0.26.2](2025-12-shai-hulud-3-test-payload.md) | high | contained |
| 2025-12-23 | [LangChain LangGrinch (CVE-2025-68664) + path traversal (CVE-2026-34070)](2025-12-langchain-langgrinch.md) | critical | patched |
| 2025-12-05 | [React2Shell — CVE-2025-55182 RCE in React Server Components (CISA KEV, exploited through Apr 2026)](2025-12-react2shell-rce.md) | critical | patched |
| 2026-01-05 | [AI IDEs recommend non-existent extensions — OpenVSX namespace hijack](2026-01-vscode-fork-recommended-extension-hijack.md) | high | mitigated |
| 2025-11-24 | [Shai-Hulud "Second Coming"](2025-11-shai-hulud-second-coming.md) | critical | contained |
| 2025-10-21 | [Cursor & Windsurf ship stale Chromium — 94+ n-day vulns](2025-10-cursor-windsurf-chromium-ndays.md) | high | active |
| 2025-10 | [Windsurf path-traversal via prompt-injected README (CVE-2025-62353)](2025-10-windsurf-cve-2025-62353-path-traversal.md) | critical | patched |
| 2025-10-17 | [GlassWorm — self-propagating VS Code / Open VSX worm](2025-10-glassworm-vscode-worm.md) | high | active |
| 2025-09-17 | [postmark-mcp backdoor](2025-09-postmark-mcp-backdoor.md) | high | contained |
| 2025-09-15 | [Shai-Hulud original](2025-09-shai-hulud-original.md) | critical | contained |
| 2025-09-08 | [qix npm account compromise](2025-09-qix-compromise.md) | critical | contained |
| 2025-09-01 | [Lies in the Loop (LITL) — approval-dialog padding hides malicious commands below the fold; no vendor fix (Claude Code, VS Code Copilot)](2025-09-litl-ai-approval-dialog-bypass.md) | high | active |
| 2025-08-26 | [Salesloft Drift OAuth Breach — UNC6395 steals Salesforce CRM data from Cloudflare, Palo Alto, Zscaler and hundreds of orgs](2025-08-salesloft-drift-oauth-breach.md) | high | contained |
| 2025-08-26 | [Nx s1ngularity](2025-08-nx-s1ngularity.md) | critical | contained |
| 2025-08 → ongoing | [Claude Code InversePrompt (multiple CVEs)](2025-08-claude-code-inverseprompt.md) | medium | patched |
| 2025-07-17 | [Amazon Q VS Code wiper](2025-07-amazon-q-wiper.md) | medium | contained |
| 2025-07 | [Cursor CurXecute / MCPoison](2025-07-cursor-curxecute-mcpoison.md) | high | patched |
| 2025-07 | [Supabase MCP lethal trifecta](2025-07-supabase-mcp-lethal-trifecta.md) | high | mitigated |
| 2025-06-25 | [VSXPloit — Open VSX nightly build pipeline token theft; 8M+ developers at risk (patched June 2025)](2025-06-vsxploit-openvsx-build-token-theft.md) | high | patched |
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
