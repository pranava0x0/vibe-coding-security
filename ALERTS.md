# Active alerts

> Single scannable feed. Latest on top. Each entry links to a full advisory.
>
> **Last refreshed:** 2026-06-12. If this date is more than 7 days old, treat the repo as stale — check [sources/](sources/) directly.

---

## 🔴 ACTIVE — react now

### 2026-06-10 — Streamlit CVE-2026-33682 — unauthenticated SSRF on Windows leaks NTLMv2 credentials (patched in 1.54.0)
**CVE-2026-33682** — **Streamlit < 1.54.0 on Windows** improperly validates filesystem paths, allowing an unauthenticated attacker to supply a **UNC path** (e.g., `\\attacker-ip\share`) that coerces the server into an outbound SMB connection on port 445. Windows auto-authenticates with **NTLMv2**, transmitting the process account's credential hash to the attacker — crackable offline or relayable in NTLM relay attacks for network lateral movement. No user interaction or credentials required. Streamlit is widely used as a quick-UI layer in vibe-coded AI/data apps. Fixed in **Streamlit 1.54.0**. Linux/macOS deployments are NOT affected.
→ [advisories/2026-06-streamlit-ssrf-windows.md](advisories/2026-06-streamlit-ssrf-windows.md)

### 2026-06-09 — LangGraph self-hosted RCE chain (CVE-2025-67644 + CVE-2026-28277) — SQL injection chains into msgpack deserialization
Security researcher Yarden Porat disclosed a **two-CVE chain** in **LangGraph** (LangChain's multi-agent framework) that allows RCE on any self-hosted deployment with user-controlled filter input. **CVE-2025-67644** (SQL injection in `langgraph-checkpoint-sqlite < 3.0.1`) injects attacker-controlled serialized data into a checkpoint query result; **CVE-2026-28277** (unsafe msgpack deserialization in `langgraph < 1.0.10`) then executes that data as Python code when the checkpoint is loaded. A third CVE (**CVE-2026-27022**, CVSS 6.5) covers an analogous RediSearch injection in the Redis checkpointer. **LangChain's managed LangSmith cloud is NOT affected** — only self-hosted instances. A self-hosted LangGraph server typically holds LLM provider API keys (Anthropic, OpenAI, AWS Bedrock) and cloud IAM credentials — treat an RCE as a cloud-account compromise. Patch: `pip install "langgraph>=1.0.10" "langgraph-checkpoint-sqlite>=3.0.1"`.
→ [advisories/2026-06-langgraph-rce-chain.md](advisories/2026-06-langgraph-rce-chain.md)

### 2026-06-08 — Hades Campaign — 19 PyPI bioinformatics + MCP-developer packages poisoned with Bun credential stealer
**Hades** is the **fifth documented copycat wave** of the open-sourced Mini Shai-Hulud / Miasma worm lineage. **37 malicious wheel artifacts across 19 PyPI packages** fall into two target pools: (1) popular **bioinformatics / graph-ML packages** (`ensmallen`, `dynamo`, `spateo`, `coolbox`, `u-fish`, `napari-ufish`, `gpsea`, and related tools) and (2) explicitly **MCP-developer-targeted packages** (`langchain-core-mcp`, `openai-mcp`, `instructor-mcp`, `tiktoken-mcp`, `ray-mcp-server`). Delivery uses three parallel mechanisms: **`*-setup.pth` startup hooks** (auto-execute at every Python interpreter startup — no import needed), **native extension `.abi3.so` import triggers**, and **`__init__.py` import hooks**. The `.pth` delivery is particularly dangerous: even if you remove the package, the `.pth` file may remain in `site-packages/` and re-execute the payload on every Python run. The payload silently downloads the **Bun JavaScript runtime** and runs an obfuscated `_index.js` harvester targeting **Claude/MCP config files** (`~/.claude/`, `~/.cursor/mcp.json`), Anthropic/OpenAI API keys, AWS/GCP/Azure/K8s credentials, GitHub/npm/PyPI tokens, SSH keys, Docker credentials, and shell history. **First wave to explicitly target MCP-developer tooling by name.** Also note: on **2026-06-09–10**, the **Miasma source code was briefly open-sourced on GitHub** ("Miasma-Open-Source-Release" repos) — a sixth copycat wave is expected imminently.
→ [advisories/2026-06-hades-campaign-pypi-mcp-attack.md](advisories/2026-06-hades-campaign-pypi-mcp-attack.md)

### 2026-06-05 — Miasma Wave 5 — 73 Microsoft Azure GitHub repos + mantine-datatable poisoned; payload auto-fires via Claude Code / Cursor / Gemini CLI (**contained 2026-06-12**)
Credentials stolen during the [Phantom Gyp / Wave 4](advisories/2026-06-phantom-gyp-miasma-wave4.md) binding.gyp campaign were used to push malicious commits to **73 Microsoft GitHub repositories** (Azure, Azure-Samples, Microsoft, MicrosoftDocs organizations) and **5 mantine-datatable / mantine-contextmenu repos** on 2026-06-05. Wave 5 introduces a **registry bypass**: no npm package is published — the attacker commits a **4.3 MB payload runner directly to the source repo** and wires it to auto-execute via **five developer tools: Claude Code, Gemini CLI, Cursor, VS Code, and the npm test hook**. Opening a compromised repository in any of these tools triggers a full credential harvest without running `npm install`. **GitHub's automated detection disabled all 73 repositories within 105 seconds**. **2026-06-12 update: all 73 Microsoft repositories have been restored** following GitHub's investigation confirming Miasma-lineage attribution; a small number of customers who pulled content during the compromise window were notified. **Status: contained.** If you cloned or pulled any affected Microsoft Azure org or mantine-datatable family repo between **2026-06-04 and 2026-06-05**, rotate all cloud and developer credentials.
→ [advisories/2026-06-miasma-wave5-microsoft-azure-github.md](advisories/2026-06-miasma-wave5-microsoft-azure-github.md)

### 2026-06-04 — IronWorm — Rust npm worm with eBPF kernel rootkit + Tor C2 (36 packages)
JFrog Security Research identified a new self-propagating npm worm called **IronWorm**, starting from the compromised account `asteroiddao`. Unlike prior waves (Miasma/Shai-Hulud), IronWorm deploys a **Rust ELF binary** that hides behind an **eBPF kernel rootkit** (invisible to eBPF-based EDR monitoring) and exfiltrates credentials over **Tor** (bypasses IP blocklists and DNS monitoring). Targets 86 env vars and 20 credential files — specifically harvests **OpenAI, Anthropic, AWS** credentials alongside npm tokens, SSH keys, and Exodus wallet files. Propagates by publishing trojanized versions of victims' own packages via stolen npm credentials including Trusted Publishing secrets. Commit author masquerades as `"claude"`. Backdates git timestamps up to 13 years to evade timeline detection.
→ [advisories/2026-06-ironworm-npm-rust-ebpf.md](advisories/2026-06-ironworm-npm-rust-ebpf.md)

### 2026-06-06 — Gluestack @react-native-aria packages backdoored with RAT (~960K weekly downloads)
A compromised npm contributor access token let attackers publish malicious versions of **17 of the 20 `@react-native-aria` packages** plus **`@gluestack-ui/utils`** (cumulative ~960K weekly downloads) on **2026-06-06**, embedding a **Remote Access Trojan (RAT)** with commands to harvest system info and exfiltrate to attacker C2. All malicious versions have been deprecated; Gluestack revoked the compromised token. Roll back to pre-June-6 versions and treat the machine as fully compromised if you installed any of these packages during the window.
→ [advisories/2026-06-gluestack-react-native-aria-rat.md](advisories/2026-06-gluestack-react-native-aria-rat.md)

### 2026-06-03 — Phantom Gyp — Miasma wave 4: self-propagating npm worm via binding.gyp (57 packages / 286+ versions)
StepSecurity and Snyk flagged a new wave of the Miasma / Shai-Hulud worm lineage on **2026-06-03**, using **`binding.gyp` / node-gyp** (rather than `preinstall`/`postinstall` lifecycle hooks) to execute malicious code at install time — a technique StepSecurity named **"Phantom Gyp."** Snyk tracks it as *Node-gyp Supply Chain Compromise June 2026*: **57 packages / 286+ malicious versions**, with **`@vapi-ai/server-sdk` (408K+ monthly downloads)** as the highest-profile victim. The worm also **forges SLSA v1 provenance attestations** on repackaged packages — a green provenance badge is not safety. **`--ignore-scripts` alone does NOT block this** — the binding.gyp native-build step runs regardless. Fourth copycat wave of the open-sourced Mini Shai-Hulud worm.
→ [advisories/2026-06-phantom-gyp-miasma-wave4.md](advisories/2026-06-phantom-gyp-miasma-wave4.md)

### 2026-06-01 — Cline CVE-2026-44211 — cross-origin WebSocket hijack → 1-click RCE (CVSS 9.7)
**CVE-2026-44211** (CVSS 9.7) — **Cline** (the VS Code AI coding agent, widely used for Claude/GPT-4 coding assistance) starts a WebSocket server on **port 3484 with no authentication and no origin validation**. Any webpage the developer visits can connect and issue arbitrary shell commands. Affects **Cline ≤ 2.13.0**. Same "localhost is not a security boundary" root cause as OpenClaw CVE-2026-25253, OpenCode CVE-2026-22812, and Marimo CVE-2026-39987. Patch immediately to the fixed version.
→ [advisories/2026-06-cline-cve-2026-44211-websocket-rce.md](advisories/2026-06-cline-cve-2026-44211-websocket-rce.md)

### 2026-06 — Claude Code GitHub Actions [bot] trust bypass (patched in v1.0.94)
Researcher RyotaK (GMO Flatt Security) found that `checkWritePermissions()` in **`anthropics/claude-code-action`** trusted any GitHub actor whose username ends in `[bot]` — no actual permission check. Combined with prompt injection in a PR comment or issue body, an unauthenticated external attacker could exfiltrate CI secrets, steal OIDC tokens, and push malicious code to any downstream repo — including Anthropic's own `claude-code-action` source, making it a supply-chain vector into every repo that pins the action. **Patched in Claude Code GitHub Actions v1.0.94.** Update your workflows and pin to the full commit SHA.
→ [advisories/2026-06-claude-code-github-actions-bot-bypass.md](advisories/2026-06-claude-code-github-actions-bot-bypass.md)

### 2026-06-01 — codexui-android npm package steals OpenAI Codex auth tokens
Aikido Security flagged **`codexui-android`** (~29K weekly npm downloads): a clean GitHub source repo hides a malicious pre-built `dist/` that runs a `postinstall` hook reading `~/.codex/auth.json` (the OpenAI Codex OAuth blob) and POSTing it to **`sentry.anyclaw.store/startlog`** — a fake Sentry host chosen to blend into error-monitoring egress. Actor self-identified as **"BrutalStrike"**; `anyclaw.store` domain registered April 12, 2026. Same actor delivered the payload via two Android apps (50K+ and 10K+ installs). **First documented supply-chain attack targeting OpenAI Codex authentication tokens.** If you installed this package on a machine with Codex configured, revoke your OpenAI Codex OAuth token immediately and audit sibling AI-tool config files (`~/.claude/settings.json`, `~/.cursor/mcp.json`, etc.).
→ [advisories/2026-06-codexui-android-codex-token-stealer.md](advisories/2026-06-codexui-android-codex-token-stealer.md)

### 2026-06-01 — Miasma: @redhat-cloud-services npm scope compromised by Mini-Shai-Hulud-derived worm
Wiz Research flagged a supply-chain compromise of Red Hat's official **`@redhat-cloud-services`** npm scope (used by the Hybrid Cloud Console / Insights / OpenShift frontends). In a **~72-second automated burst on 2026-06-01**, **32 packages and 96 malicious versions** were published, each carrying a **`preinstall`** script that runs a **~4.2 MB obfuscated payload** harvesting **AWS / GCP / Azure / Kubernetes / HashiCorp Vault / GitHub / npm / CircleCI** credentials. The payload is a **lightly reskinned descendant of the Mini Shai-Hulud worm** that [TeamPCP open-sourced 2026-05-12](advisories/2026-05-shai-hulud-copycat-wave.md) — Greek-mythology theming (`spartan`/`miasma`) replaces Dune markers, with **new GCP/Azure cloud-identity collectors**. Notable IOC: exfil hits a **camouflage URL `https://api.anthropic.com:443/v1/api`** (fake path on real-vendor host, chosen to blend into AI-tool egress logs). ~80K weekly cumulative downloads in scope; initial access was a **compromised Red Hat employee GitHub account → GitHub Actions OIDC token → `npm publish`** (no separate npm credential theft). Red Hat issued [RHSB-2026-006](https://access.redhat.com/security/vulnerabilities/RHSB-2026-006); malicious versions removed from npm. **Third copycat wave** of the open-sourced worm after [TrapDoor](advisories/2026-05-trapdoor-cross-ecosystem-stealer.md) and the [`deadcode09284814` typosquats](advisories/2026-05-shai-hulud-copycat-wave.md), and the first to disguise exfil as AI-vendor API traffic. **2026-06-11 update:** The Miasma source code was [briefly open-sourced on GitHub](https://safedep.io/miasma-worm-source-leaked-github/) ("Miasma-Open-Source-Release" repos) on June 9–10 before removal — a sixth copycat wave is expected.
→ [advisories/2026-06-miasma-redhat-cloud-services-compromise.md](advisories/2026-06-miasma-redhat-cloud-services-compromise.md)

### 2026-05-22 — Megalodon: 5,561 GitHub repos backdoored via mass GitHub-Actions workflow injection in 6 hours
SafeDep flagged **Megalodon**: an automated campaign that pushed **5,718 malicious commits across 5,561 GitHub repositories on 2026-05-18** (~6-hour burst), injecting `.github/workflows/*.yml` files that base64-decode → bash → exfil **`$GITHUB_TOKEN`, OIDC, masked CI secrets, AWS/npmrc/SSH/Docker creds, `.env*`** to **`216.126.225.129:8443`**. Two variants: **`SysDiag`** (mass, new workflow on every push/PR) and **`Optimize-Build`** (targeted, replaces an existing workflow with a `workflow_dispatch` dormant backdoor — the variant that reached **`@tiledesk/tiledesk-server` npm 2.18.6 → 2.18.12** when the legit maintainer republished from the poisoned source). Throwaway author identities: `build-bot`, `auto-ci`, `ci-bot`, `pipeline-bot`. **Distinct from TeamPCP**; Hudson Rock matched **~33% of affected accounts to known infostealer victims** — credentials almost certainly came from the [GlassWorm](advisories/2025-10-glassworm-vscode-worm.md) ecosystem. CISA bundled this with [Nx Console](advisories/2026-05-nx-console-vscode-compromise.md) in its [2026-05-28 supply-chain alert](https://www.cisa.gov/news-events/alerts/2026/05/28/supply-chain-compromises-impact-nx-console-and-github-repositories). Audit any bot-authored workflow change after **2026-05-17 23:00 UTC**.
→ [advisories/2026-05-megalodon-github-actions-mass-campaign.md](advisories/2026-05-megalodon-github-actions-mass-campaign.md)

### 2026-05-22 — BadHost: Starlette host-header auth bypass blasts FastAPI, vLLM, LiteLLM, MCP servers (CVE-2026-48710)
**CVE-2026-48710** — Starlette < 1.0.1 rebuilds `request.url` from the raw HTTP `Host` header without RFC validation. A single `/`, `?`, or `#` in `Host` shifts path/query/fragment boundaries on re-parse, so middleware reading `request.url.path` sees a different path than the ASGI router actually dispatched. **Any auth middleware that checks `request.url.path` fails open** — one character, no credentials. Starlette ships **~325M downloads/week** and underpins **FastAPI, vLLM, LiteLLM, Text Generation Inference, OpenAI-compatible proxies, the Python MCP SDK, and most AI-agent dashboards**. X41 D-Sec found it during an OSTIF-sponsored vLLM audit; coordinated disclosure **2026-05-22**, one day after the upstream fix. **Patched in Starlette 1.0.1.** Structural fix: replace `request.url.path` with `request.scope["path"]` in any security-decision code. Third entry in the "two parsers, one string" class (siblings: Claude Code argv-smuggling deeplink, Claude Code SOCKS5 null-byte).
→ [advisories/2026-05-starlette-badhost-host-header-bypass.md](advisories/2026-05-starlette-badhost-host-header-bypass.md)

### 2026-05-22 — Composio AI-agent platform breach (LLM-augmented attacker registered malicious tool definitions in the sandbox)
**Composio** — the AI-agent infrastructure platform that brokers ~100 MCP toolkits (GitHub/Gmail/Jira/Notion/Slack/Linear/HubSpot/Drive/Vercel/Sentry…) — disclosed that an attacker **brute-forced exploit chains with LLM-generated attack patterns** on **2026-05-21 (01:05 – 09:15 PT)**, landed in an *internal monitoring agent*, pivoted into the automated-remediation system, then **registered malicious tool definitions inside the sandboxed execution environment** to reach arbitrary code execution. Blast radius: **~5,001 user GitHub OAuth connections + ~5,241 cached API keys** (~0.3% of active). Composio mandated full API-key rotation by **2026-05-23 23:00 PT** and deleted all keys older than 2026-05-22 23:00 PT. Second documented **"AI tool → cloud platform" OAuth pivot** (after [Vercel/Context.ai](advisories/2026-04-vercel-context-ai-breach.md)) and **first** with attacker openly using LLM-augmented exploitation + a *malicious-tool-definition-in-sandbox* primitive. Audit your GitHub/Google OAuth grants for any Composio-connected app.
→ [advisories/2026-05-composio-ai-agent-platform-breach.md](advisories/2026-05-composio-ai-agent-platform-breach.md)

### 2026-05-25 — Cargo May 2026 security release — symlink-override + sparse-URL credential leak (CVE-2026-5223, CVE-2026-5222)
First Cargo-itself CVEs in this repo. **CVE-2026-5223 (medium):** Cargo did not reject symlinks inside crate tarballs from **third-party registries** → a malicious crate's tarball can extract one directory up and **overwrite the cached source of another crate from the same registry**, hijacking a subsequent `cargo build`. **crates.io users NOT affected** (crates.io rejects symlink uploads server-side). **CVE-2026-5222 (low):** sparse-registry URL normalization stripped `.git`, so creds for `…/index.git` are replayed against `…/index`. Both fixed in **Rust 1.96.0 (2026-05-28)**. Generalizes [TrapDoor](advisories/2026-05-trapdoor-cross-ecosystem-stealer.md)'s Crates.io arm: build-system archive-extraction primitives are supply-chain primitives. Upgrade Rust; if you run a mirror registry, enable server-side symlink rejection.
→ [advisories/2026-05-cargo-symlink-sparse-url-cves.md](advisories/2026-05-cargo-symlink-sparse-url-cves.md)

### 2026-05-22 — TrapDoor — cross-ecosystem stealer that poisons your `.cursorrules` / `CLAUDE.md`
Socket flagged **TrapDoor**: **34+ malicious packages / 384+ versions** pushed to **npm + PyPI + Crates.io** at once (first activity 2026-05-22 20:20 UTC), impersonating crypto/DeFi/AI/security dev tooling (`prompt-engineering-toolkit`, `solidity-deploy-guard`, `defi-threat-scanner`). npm `postinstall` runs `trap-core.js` (live-validates AWS/GitHub tokens); PyPI auto-execs on import; Rust `build.rs` XOR-encrypts keystores → GitHub Gists. The vibe-coding twist: it **rewrites `.cursorrules` / `CLAUDE.md` with zero-width Unicode** so your own AI agent exfiltrates secrets under the guise of an "automated security scan." Markers: GitHub `ddjidd564`, `ddjidd564.github.io`, `P-2024-001`. Distinct actor (not TeamPCP). Grep your agent-config files for invisible Unicode.
→ [advisories/2026-05-trapdoor-cross-ecosystem-stealer.md](advisories/2026-05-trapdoor-cross-ecosystem-stealer.md)

### 2026-05-20 — Claude Code network-sandbox SOCKS5 null-byte allowlist bypass (silent fix in 2.1.90)
A host like `attacker-host.com\x00.google.com` passes Claude Code's egress allowlist (matcher sees the trailing `.google.com`) but the OS truncates at the null byte and dials `attacker-host.com`. Affected **v2.0.24 → v2.1.89** (~130 versions / 5.5 months); **silently patched in v2.1.90 (2026-04-01)** — no CVE, no advisory, no changelog note. If you used the sandbox as a real boundary while running untrusted repos/MCP content, rotate any reachable creds. Researcher: Aonan Guan / oddguan.com. Second silently-fixed sandbox bypass in ~5 months.
→ [advisories/2026-05-claude-code-sandbox-socks5-bypass.md](advisories/2026-05-claude-code-sandbox-socks5-bypass.md)

### 2026-05-18 — Nx Console VS Code extension compromised (nrwl.angular-console 18.95.0) — CVE-2026-48027, CISA KEV
Trojanized **Nx Console** (~2.2M installs) live ~**11–18 min** on the VS Code Marketplace. On any `folderOpen` it pulled a **498 KB stealer hidden in a dangling orphan commit inside `nrwl/nx`** and exfiltrated GitHub/npm/AWS/Vault/K8s/1Password secrets — plus **`~/.claude/settings.json`** — over HTTPS + GitHub API + DNS tunneling. Maintainer token leaked in the [TanStack / Mini Shai-Hulud wave](advisories/2026-05-tanstack-mini-shai-hulud.md); this is the **same extension** behind GitHub's ~3,800-repo breach. ~6,000+ may have auto-updated. **CVE-2026-48027** assigned and **added to CISA KEV 2026-05-27** (federal deadline **2026-06-10**); clean version is **Nx Console ≥ 18.100.0**. Disable silent extension auto-update.
→ [advisories/2026-05-nx-console-vscode-compromise.md](advisories/2026-05-nx-console-vscode-compromise.md)

### 2026-05-20 — TeamPCP breaches GitHub's internal repos via poisoned VS Code extension
GitHub confirmed ~**3,800 internal repositories** exfiltrated after an employee installed a **poisoned VS Code extension** — now named as the trojanized **[Nx Console `nrwl.angular-console@18.95.0`](advisories/2026-05-nx-console-vscode-compromise.md)**, linked to the [TanStack / Mini Shai-Hulud wave](advisories/2026-05-tanstack-mini-shai-hulud.md). Actor is **TeamPCP** (PCPcat/DeadCatx3/UNC6780) — same group as the Mini Shai-Hulud worm — who listed the source for sale at **$50K**. No evidence customer data outside internal repos hit (investigation ongoing). Lesson: your IDE extension marketplace is an unaudited supply-chain surface. Disable silent extension auto-update on credential-holding editors.
→ [advisories/2026-05-teampcp-github-breach.md](advisories/2026-05-teampcp-github-breach.md)

### 2026-05-19 — Mini Shai-Hulud May 19 wave — @antv npm + Microsoft `durabletask` PyPI
TeamPCP pushed **~637 malicious versions across ~317 npm packages** (the whole `@antv` scope, `echarts-for-react` ~1.1M weekly, `timeago.js`, `size-sensor`) in a 22-min burst, plus trojanized **Microsoft `durabletask`** PyPI versions **1.4.1/1.4.2/1.4.3** (pin to 1.4.0). Payload steals 20+ cred classes, attempts **Docker host-socket escape**, plants VS Code + Claude Code backdoors, and now **self-mints valid Sigstore provenance** (green badge ≠ safe). Campaign total: ~1,055 versions / ~502 packages (npm+PyPI+Composer).
→ [advisories/2026-05-mini-shai-hulud-may19-wave.md](advisories/2026-05-mini-shai-hulud-may19-wave.md)

### 2026-05-18 — Shai-Hulud copycats after the worm source went public
TeamPCP **open-sourced the Mini Shai-Hulud worm** (2026-05-12) and posted a **$1,000 "biggest supply-chain attack" competition on BreachForums** — and the worm is now a commodity. Actor `deadcode09284814` shipped **four npm packages** (~2,700 downloads): **`chalk-tempalte`** (near-verbatim worm clone, C2 `87e0bbc636999b.lhr.life`, marker "A Mini Sha1-Hulud has Appeared"), **`@deadcode09284814/axios-util`** (SSH/env/cloud-cred exfil → `80.200.28.28:2222`), **`axois-utils`** (Golang **"Phantom Bot" DDoS** botnet + Windows/Linux persistence), and **`color-style-utils`** (IP/geo/wallet theft → `edcf8b03c84634.lhr.life`). Low volume so far, but copycats with noisier payloads (DDoS, not just stealers) are the new tail of the [Mini Shai-Hulud wave](advisories/2026-05-tanstack-mini-shai-hulud.md).
→ [advisories/2026-05-shai-hulud-copycat-wave.md](advisories/2026-05-shai-hulud-copycat-wave.md)

### 2026-05-12 — Claude Code `claude-cli://` deeplink RCE — patched in 2.1.118
`eagerParseCliFlag()` in `main.tsx` accepted `--settings=` from anywhere in argv, including values smuggled through `--prefill`. The registered `claude-cli://` URL handler turns that into a one-click silent RCE: a malicious link can swap your `~/.claude/settings.json` (hooks) and run any shell command on session start. Researcher: Joernchen / 0day.click. Upgrade immediately.
→ [advisories/2026-05-claude-code-deeplink-rce.md](advisories/2026-05-claude-code-deeplink-rce.md)

### 2025-07 → ongoing — WhiteCobra — VS Code / Cursor / Windsurf / Open VSX crypto-stealer campaign
**WhiteCobra** is a persistent, funded threat-actor campaign continuously flooding the VS Code Marketplace and Open VSX with malicious extensions targeting crypto wallet users of **Cursor** and **Windsurf**. The group stole **$500,000** in July 2025 via a fake Solidity syntax-highlighting extension (`contractshark.solidity-lang`, 54,000 OpenVSX downloads), deploys **LummaStealer** payloads that steal crypto wallets, browser credentials, and messaging app data, and can redeploy a new campaign in under **3 hours** — so removals don't stop it. Koi Security exposed the threat actor's playbook in May 2026. At least **24 malicious extensions** documented across VS Code Marketplace and Open VSX. If you use Cursor or Windsurf for Solidity/web3 development, audit your extensions now.
→ [advisories/2026-05-whitecobra-vscode-extensions.md](advisories/2026-05-whitecobra-vscode-extensions.md)

### 2026-05-06 — ClaudeBleed — Claude in Chrome extension hijack (v1.0.70, **partial fix**)
LayerX: Claude's `externally_connectable` handler trusts *any* other Chrome extension to issue commands to Claude. Zero-permission neighbor extension → Claude drives Gmail, Drive, GitHub on the user's behalf. Anthropic shipped v1.0.70 with extra approval prompts but did not remove the handler; side-panel / privileged-mode bypass still works. Treat as **mitigated, not patched**.
→ [advisories/2026-05-claudebleed-chrome-extension.md](advisories/2026-05-claudebleed-chrome-extension.md)

### 2026-05-13 — OpenClaw "Claw Chain" (CVE-2026-44112/44113/44115/44118)
Four chainable flaws in **OpenClaw** AI agent — TOCTOU sandbox-escape (read + write), here-doc allowlist bypass, owner impersonation. ~245K public instances; 63% with no auth. Patched in **OpenClaw 2026.4.22**. If you exposed an instance: assume full compromise.
→ [advisories/2026-05-openclaw-claw-chain.md](advisories/2026-05-openclaw-claw-chain.md)

### 2026-05-13 — Systemic MCP stdio RCE class (~200,000 servers exposed)
OX Security: 7,000 vulnerable MCP servers on public IPs; ~200,000 total estimated. Three database MCPs (Apache Doris, Alibaba RDS, Apache Pinot) disclosed same window; **Alibaba declined to patch**. Microsoft MCP server hit by CVE-2026-26118. Named KEV-listed instance: **nginx-ui "MCPwn" (CVE-2026-33032, CVSS 9.8)** — empty default IP allowlist on `/mcp_message` = unauthenticated full nginx takeover in 2 requests; ~2,600 exposed, exploited in the wild, patch ≥ 2.3.4. **New this sweep:** **`aws-mcp-server` CVE-2026-5058 + CVE-2026-5059** (CVSS 9.8 each, unauthenticated command-injection RCE in the allowed-commands handler, ZDI-26-245/-246, patches pending — remove from network); **`n8n-mcp` CVE-2026-39974** (post-auth SSRF that reflects responses → IMDS-credential theft; fixed 2.47.4).
→ [advisories/2026-05-mcp-stdio-systemic-rce.md](advisories/2026-05-mcp-stdio-systemic-rce.md)

### 2026-05-11 — PraisonAI auth bypass (CVE-2026-44338) — exploited in 3h44m; four additional platform CVEs
Legacy Flask API server shipped with auth disabled. Sysdig honeypot saw scanner probing **3 hours, 44 minutes** after GHSA published. Affects PraisonAI 2.5.6–4.6.33. Fixed in **4.6.34**. **June 2026 addition:** `praisonai-platform` package carries four more CVEs: **CVE-2026-47408** (unauthenticated A2A tool execution), **CVE-2026-47418** (cross-workspace IDOR), **CVE-2026-47416** (privilege escalation to owner), **CVE-2026-47409** (missing auth on member removal). Upgrade `praisonai-platform` to the patched version.
→ [advisories/2026-05-praisonai-auth-bypass.md](advisories/2026-05-praisonai-auth-bypass.md)

### 2026-05-11 → 2026-05-12 — Mini Shai-Hulud wave: TanStack, Mistral, UiPath, OpenSearch — CISA KEV; OpenAI mac certs revoked
**172 unique packages, 403 malicious versions** across npm + PyPI (518M+ cumulative downloads). Operated by **TeamPCP**. First documented case of malicious npm package carrying **valid SLSA provenance**. TanStack subset is **CVE-2026-45321 (CVSS 9.6)** — **CISA KEV 2026-05-27**, federal deadline **2026-06-10**. **OpenAI** disclosed (2026-05-14) that **two employee devices** were compromised, limited credential material exfiltrated from internal source-code repos; ChatGPT Desktop / Codex / Codex-cli / Atlas re-signed; **old macOS/Windows/iOS/Android certs revoked 2026-06-12**. Second AI-vendor code-signing-cert rotation in five weeks (cf. [Axios → 2026-05-08](advisories/2026-03-axios-compromise.md)).
→ [advisories/2026-05-tanstack-mini-shai-hulud.md](advisories/2026-05-tanstack-mini-shai-hulud.md)

### 2026-05-14 — `node-ipc` compromised (versions 9.1.6, 9.2.3, 12.0.1)
822K weekly downloads. Identical 80KB payload, DNS-based exfil to `sh.azurestaticprovider.net` / `37.16.75.69`. Steals 90+ credential categories. Forensic marker: tarball files timestamped 1985-10-26.
→ [advisories/2026-05-node-ipc-compromise.md](advisories/2026-05-node-ipc-compromise.md)

### 2026-05-08 — Cursor "Open-Folder" autorun + Git-hook RCE (CVE-2026-26268, CVE-2026-22708, CVE-2026-32202)
Three Cursor IDE flaws: malicious Git pre-commit hooks in nested bare repos execute on agent autopilot; shell built-ins bypass Auto-Run allowlist; Workspace Trust off by default. Opening or cloning an untrusted repo is a silent-RCE primitive. Patched in **Cursor 2.5**.
→ [advisories/2026-05-cursor-open-folder-autorun.md](advisories/2026-05-cursor-open-folder-autorun.md)

### 2026-05-07 — Microsoft Semantic Kernel — prompt-injection-to-RCE (CVE-2026-25592, CVE-2026-26030)
.NET SDK: `[KernelFunction]`-exposed `DownloadFileAsync` lets prompt-injected agent escape Azure Container Apps Python sandbox. **CVSS 10.0**. Python SDK: `InMemoryVectorStore` filter uses `eval()` on user-influenced input. **CVSS 9.9**. Patch .NET 1.71.0 / Python 1.39.4.
→ [advisories/2026-05-semantic-kernel-rce.md](advisories/2026-05-semantic-kernel-rce.md)

### 2026-05-06 → 05-07 — Next.js + React May 2026 security release (13 CVEs)
Headline: **CVE-2026-44578 (CVSS 8.6) — unauthenticated SSRF** in WebSocket upgrade handler, all self-hosted Next.js 13.4.13+ (Vercel-hosted unaffected). ~79K vulnerable instances on Shodan. **CVE-2026-23870** is an upstream React Server Components DoS. Upgrade to **Next.js 15.5.18 / 16.2.6**.
→ [advisories/2026-05-nextjs-react-security-release.md](advisories/2026-05-nextjs-react-security-release.md)

### 2026-05 — Windsurf zero-click MCP RCE (CVE-2026-30615)
Prompt injection in MCP-fetched content writes to `mcp.json` and auto-registers attacker-controlled server — **no user interaction**. CVSS 8.0. Patched in Windsurf > 1.9544.26. Cursor / Claude Code / Gemini-CLI have the same class issue; vendors declined to issue CVEs.
→ [advisories/2026-05-windsurf-zero-click-mcp-rce.md](advisories/2026-05-windsurf-zero-click-mcp-rce.md)

### 2026-05 — PCPJack — credential-stealing counter-worm that removes TeamPCP infections
**PCPJack** poses as a cleanup tool for **TeamPCP** infections — it genuinely removes TeamPCP's malicious processes and configurations, giving victims false confidence that their host is clean, while PCPJack's own credential harvest runs in the background. Disclosed May 2026 by SentinelLabs. Chains **5 CVEs** to spread worm-like across Kubernetes clusters, Docker hosts, Redis, MongoDB, and RayML environments. Most critically, it exploits **CVE-2025-55182 (React2Shell, CVSS 10.0)** and **CVE-2025-29927 (Next.js)** to gain initial footholds via web apps, then pivots from the compromised web server into cloud credentials it finds on the same host (`~/.aws`, `KUBECONFIG`, Docker socket). Any unpatched React/Next.js app running on a host with cloud credentials is a potential lateral-movement entry point into the developer's entire cloud infrastructure. **Do not trust the absence of TeamPCP infections as a sign of a clean host** — PCPJack specifically cleans TeamPCP to reduce detection noise. **June 2026 update:** PCPJack has escalated to building a **230-node covert SMTP relay network** from hijacked AWS, Google Cloud, and Azure servers — syncing verified outbound-mail proxies every five minutes for downstream spam/phishing abuse.
→ [advisories/2026-05-pcpjack-counter-worm.md](advisories/2026-05-pcpjack-counter-worm.md)

### 2026-04 (ongoing) — Mini Shai-Hulud SAP packages
`mbt`, `@cap-js/db-service`, `@cap-js/postgres`, `@cap-js/sqlite` compromised. Same TeamPCP playbook. Harvests local dev creds, GH/npm tokens, cloud creds.
→ [advisories/2026-04-mini-shai-hulud-sap.md](advisories/2026-04-mini-shai-hulud-sap.md)

### 2026-04-30 — PyTorch Lightning + intercom-client (Mini Shai-Hulud cross-ecosystem)
`pytorch-lightning` 2.6.2/2.6.3 (PyPI) and `intercom-client@7.0.4` (npm) shipped with hidden `_runtime/router_runtime.js` (~11 MB Bun JS payload). Steals cloud creds, GitHub/npm tokens, Claude Code + VS Code config. Plants `.claude/setup.mjs` and `.vscode/tasks.json` postinstall hooks in victim repos. Caught in ~42 minutes. Downgrade to **2.6.1**. Same threat actor (TeamPCP) as TanStack wave 11 days later.
→ [advisories/2026-04-pytorch-lightning-compromise.md](advisories/2026-04-pytorch-lightning-compromise.md)

### 2026-04 — "Comment and Control" prompt injection (Claude Code Sec Review / Gemini CLI / Copilot Agent)
CVSS **9.4 Critical**. Payload in GitHub PR title/issue body/comment hijacks AI agent to exfiltrate Actions runner secrets. All three vendors patched.
→ [advisories/2026-04-comment-and-control-pr-injection.md](advisories/2026-04-comment-and-control-pr-injection.md)

---

## 🟠 RECENT — verify exposure

### 2025-11-09 — n8n Ni8mare (CVE-2026-21858, CVSS 10.0) — unauth RCE in workflow automation; ~60K instances; exploited in wild
**CVE-2026-21858 "Ni8mare"** (CVSS 10.0) — any network-reachable attacker can run arbitrary commands on a self-hosted **n8n** instance without credentials, gaining full control over the host and **all OAuth tokens and API keys stored in n8n's credential store** (Google Drive, Slack, GitHub, HubSpot, Notion, Jira, etc.). n8n is widely used as an AI workflow orchestration layer — this is structurally equivalent to the [Composio breach](advisories/2026-05-composio-ai-agent-platform-breach.md) pattern. An estimated **26,512–100,000 instances** were exposed; GreyNoise logged **33,000+ exploitation attempts** between January 27–February 3, 2026. **Patched in n8n 1.121.0** (November 18, 2025). A follow-on authenticated sandbox bypass (CVE-2026-25049, CVSS 9.4) was disclosed in February 2026 with public exploits; additional RCE/credential-exposure flaws followed in March 2026. **June 2026 cluster:** three new critical/high flaws — **CVE-2026-44789** (unauthenticated SSRF via unvalidated webhook URLs → IMDS credential theft, CVSS 9.1), **CVE-2026-44790** (code-node sandbox escape via prototype pollution, CVSS 8.8, auth required), and **CVE-2026-44791** (stored XSS in workflow node names → session-token theft, CVSS 8.7). All fixed in **n8n 1.155.0**. Upgrade to the latest n8n release.
→ [advisories/2025-11-n8n-ni8mare-rce.md](advisories/2025-11-n8n-ni8mare-rce.md)

### 2025-12-05 → ongoing — React2Shell (CVE-2025-55182, CVSS 10.0) — RCE in React Server Components; CISA KEV; 766+ hosts compromised
**CVE-2025-55182 "React2Shell"** (CVSS 10.0, CISA KEV) is an unauthenticated RCE via **insecure deserialization in React's Flight protocol**. Any exposed React Server Component (RSC) endpoint is a one-request RCE — no credentials needed. Affects **Next.js, Waku, React Router (RSC mode), RedwoodSDK, Parcel RSC, Vite RSC plugin**. First exploited **2025-12-05**; a large-scale credential-harvesting campaign had compromised at least **766 hosts** through April 2026 (database creds, SSH keys, AWS secrets, Stripe API keys, GitHub tokens + cryptomining backdoors). The RondoDox botnet weaponized it in January 2026. **Patched in React 19.0.4/19.1.5/19.2.4** and corresponding Next.js versions. This is a historical backfill — if you haven't patched, patch now.
→ [advisories/2025-12-react2shell-rce.md](advisories/2025-12-react2shell-rce.md)

### 2026-03-12 — TeamPCP breaches Trivy GitHub Actions → LiteLLM 1.82.7–1.82.8 backdoored (March 2026)
TeamPCP **force-pushed malicious replacements onto 75 of 76 `aquasecurity/trivy-action` release tags**, injecting an `entrypoint.sh` that exfiltrated `$GITHUB_TOKEN`, masked CI secrets, and cloud creds from any pipeline running `trivy-action` by tag (not SHA). LiteLLM's release pipeline was hit: the stolen PyPI token was used to push **LiteLLM 1.82.7 + 1.82.8** (~3.4M daily downloads) live for ~3 hours. **1,705 dependent PyPI packages** had their CI pipelines exposed. Cisco internal source code was stolen in a related breach. **Novel pattern: security scanner as supply-chain attack vector** — `trivy-action` was running with the same CI permissions as any other action. Upgrade LiteLLM to ≥ 1.83.0; pin all GitHub Actions to full commit SHAs, not tags.
→ [advisories/2026-03-trivy-litellm-supply-chain.md](advisories/2026-03-trivy-litellm-supply-chain.md)

### 2026-01-07 — LangSmith CVE-2026-25750 — unvalidated baseUrl → account takeover
**CVE-2026-25750** (CVSS 8.5) — LangSmith Studio accepted an arbitrary `baseUrl` parameter without validation; all authenticated API calls (including session tokens) were forwarded to attacker-controlled hosts. Companion **CVE-2026-25528** is SSRF via the distributed tracing header → cloud IMDS credential theft. LangSmith cloud was silently patched **2025-12-20**; self-hosted deployments need **LangSmith ≥ 0.12.71**. LangSmith stores upstream LLM provider keys + trace data for every agent run — account takeover = full workspace compromise. An AI observability platform that holds every upstream provider key is a high-trust hub; treat it accordingly.
→ [advisories/2026-01-langsmith-account-takeover.md](advisories/2026-01-langsmith-account-takeover.md)

### 2026-04-24 — LiteLLM proxy pre-auth SQL injection (CVE-2026-42208, CISA KEV)
**CVE-2026-42208** (CVSS 9.3) — BerriAI's **LiteLLM** proxy concatenates the caller-supplied `Authorization: Bearer` value directly into the API-key verification SQL query. Any **unauthenticated** attacker reaches read/write on the proxy database — which holds **every upstream LLM provider key** (OpenAI / Anthropic / AWS Bedrock / Azure / Vertex / Cohere / Mistral) for everyone the proxy fronts. **Exploited 26 hours after disclosure** ([Sysdig honeypot 2026-04-26 16:17 UTC](https://www.sysdig.com/blog/cve-2026-42208-targeted-sql-injection-against-litellms-authentication-path-discovered-36-hours-following-vulnerability-disclosure)); **CISA KEV 2026-05-08** with detected exploitation against US financial-services and healthcare critical infrastructure. Affects **1.81.16 → 1.83.6**, fixed **1.83.7** (run `1.83.10-stable`). Same "AI/data tool ships an unauthenticated network endpoint" cluster as [Langflow](advisories/2026-03-langflow-rce.md), [PraisonAI](advisories/2026-05-praisonai-auth-bypass.md), [Marimo](advisories/2026-04-marimo-notebook-rce.md), [Flowise](advisories/2026-04-flowise-rce-cluster.md).
→ [advisories/2026-04-litellm-sql-injection.md](advisories/2026-04-litellm-sql-injection.md)

### 2026-04-23 — Flowise RCE cluster — CVE-2025-59528 actively exploited + April Agent-node cluster (CVE-2026-41265 et al.)
**Flowise** — the drag-and-drop LLM workflow builder (~38K stars, **12,000–15,000 internet-exposed instances**) — has two overlapping RCE problems. **CVE-2025-59528** (CVSS 10.0): unauth code injection in the `CustomMCP` node (`eval` on `mcpServerConfig`), under **active exploitation since early April 2026** (VulnCheck observed a Starlink-IP attacker); fixed in **3.0.6**. **April 2026 Agent-node cluster** (CVE-2026-41265 Airtable, CVE-2026-41138 Airtable+Pandas, CVE-2026-41264/41268 generic, CVE-2026-40933, CVE-2026-41137 CSV, CVE-2026-41269 file upload — CVSS 9.2 each): the various Agent classes evaluate **LLM-generated Python with no sandbox**, so any chatflow caller can prompt-inject the LLM into emitting Python that runs on the host. All fixed in **3.1.0** (use **3.1.1**). Flowise stores upstream LLM provider keys — assume those are exfiltrated on any exposed vulnerable host. Sibling of [Langflow](advisories/2026-03-langflow-rce.md), [Marimo](advisories/2026-04-marimo-notebook-rce.md), [Semantic Kernel decorator-as-documentation](advisories/2026-05-semantic-kernel-rce.md).
→ [advisories/2026-04-flowise-rce-cluster.md](advisories/2026-04-flowise-rce-cluster.md)

### 2026-04-24 — elementary-data PyPI + GHCR compromise (malicious `.pth` auto-exec)
`elementary-data==0.23.3` (dbt observability tool, ~**1M+ monthly downloads**) shipped a top-level **`elementary.pth`** that Python auto-execs at *every* interpreter startup — a 3-stage infostealer grabbing cloud tokens, SSH keys, K8s creds, and crypto wallets. The matching **GHCR Docker images were poisoned** (`ghcr.io/elementary-data/elementary`), so every unpinned `pull`/`FROM` ran the trojan. Initial access: a **GitHub Actions script injection** → forged signed release → the *real* publish pipeline. Fixed in **0.23.4**. Pin images by digest; flag `.pth` files in dependencies.
→ [advisories/2026-04-elementary-data-pypi-ghcr-compromise.md](advisories/2026-04-elementary-data-pypi-ghcr-compromise.md)

### 2026-04-22 — Bitwarden CLI backdoored — first supply-chain malware to hunt AI-tool creds
`@bitwarden/cli` **v2026.4.0** (npm; ~70K weekly downloads) was live ~**90 min** as one arm of TeamPCP's **"Shai-Hulud: The Third Coming"** Checkmarx-channel campaign. Beyond multi-cloud cred theft + a self-propagating npm worm + GitHub commit dead-drop C2, it carried a **novel module that scrapes authenticated AI coding assistants** — AI-tool config + **MCP files** (Claude Code, Cursor, Codex). Bitwarden vault data was unaffected; the risk is anyone who *installed the poisoned CLI*. Rotate cloud/GitHub/npm tokens and every AI-tool/MCP key.
→ [advisories/2026-04-bitwarden-cli-shai-hulud-third-coming.md](advisories/2026-04-bitwarden-cli-shai-hulud-third-coming.md)

### 2026-04-19 — Vercel breach via Context.ai OAuth supply chain
Lumma Stealer compromised a Context.ai employee → attackers used the Workspace OAuth grant to pivot into a Vercel employee's account, then into Vercel internals, then enumerated/decrypted non-sensitive customer environment variables. Encrypted "sensitive" env vars, Next.js / Turbopack source, and npm packages were not touched. First widely documented "AI tool → cloud platform" OAuth pivot. Rotate everything in non-sensitive env vars and mark every credential as sensitive going forward.
→ [advisories/2026-04-vercel-context-ai-breach.md](advisories/2026-04-vercel-context-ai-breach.md)

### 2026-04-08 — Marimo notebook pre-auth RCE (CVE-2026-39987) — exploited in <10h, CISA KEV
Marimo's `/terminal/ws` WebSocket endpoint **skips authentication** (every other WS endpoint calls `validate_auth()`), handing any network-reachable attacker a **full PTY shell**. Sysdig saw exploitation **9h 41m** after disclosure (credential theft in <3 min); **CISA KEV** 2026-04-23. Affects **≤ 0.20.4**, fixed in **0.23.0**. Same "AI/data tool ships an unauthenticated network endpoint" class as [Langflow](advisories/2026-03-langflow-rce.md) and [PraisonAI](advisories/2026-05-praisonai-auth-bypass.md) — patch on disclosure, never expose a notebook server.
→ [advisories/2026-04-marimo-notebook-rce.md](advisories/2026-04-marimo-notebook-rce.md)

### 2026-02-17 — Cline `2.3.0` supply-chain compromise — "Clinejection" → OpenClaw payload
GitHub-issue-title prompt injection → Cline's own AI triage bot ran attacker-controlled `npm install` → Cacheract poisoned the Actions cache → next publish workflow restored poisoned cache and leaked `NPM_RELEASE_TOKEN` → attacker pushed `cline@2.3.0` with a `postinstall` script installing **OpenClaw** as a system daemon. ~4,000 installs in 8h before takedown. Cline's rotation hit the wrong token. Researcher: Adnan Khan.
→ [advisories/2026-02-cline-clinejection.md](advisories/2026-02-cline-clinejection.md)

### 2026-02-17 — SANDWORM_MODE npm worm: MCP server injection, CI implant, 48-hour delayed activation (19 packages)
**SANDWORM_MODE** is a self-propagating npm supply-chain worm discovered by Socket in February 2026. **19 malicious packages** across two publisher aliases typosquat Claude Code, OpenClaw, and popular Node.js utilities. Two-stage attack: **Stage 1** (immediate on `npm install`) steals all developer/CI credentials — npm tokens, GitHub tokens, AWS/GCP/Azure keys, SSH keys, and crypto wallet seeds — and exfiltrates them to a GitHub API endpoint. **Stage 2** fires after a **48-hour delay plus up to 48h random jitter** — deliberately longer than npm security's typical 6–24h triage window — and runs a deeper sweep from password managers, **injects a malicious MCP server with embedded prompt injection** into Claude Code/Cursor config, installs Git hook persistence, and self-propagates by publishing trojanized versions of packages the victim maintains. The GitHub Actions **`ci-quality/code-quality-check`** Action is also used as a weaponized "code quality scanner" that harvests CI secrets and OIDC tokens and patches `.github/workflows/*.yml` for persistence. If you installed any AI-tool-adjacent npm packages in February 2026 and your MCP config, Git hooks, or workflows contain unfamiliar entries, Stage 2 may already have fired.
→ [advisories/2026-02-sandworm-mode-npm-worm.md](advisories/2026-02-sandworm-mode-npm-worm.md)

### 2025-12-28 — Shai-Hulud 3.0 — `@vietmoney/react-big-calendar@0.26.2` (test payload)
Third generation of the Shai-Hulud worm dropped on a dormant npm package (no update since March 2021) with **heavier obfuscation + reliability improvements** but the same install-time credential-theft + GitHub-exfil core. Low downloads / no major spread — Aikido: "we may have caught the attackers testing their payload." Snyk's "Holiday Whisper." Now read in retrospect as the **TeamPCP rehearsal** that became the [SAP](advisories/2026-04-mini-shai-hulud-sap.md) / [PyTorch Lightning](advisories/2026-04-pytorch-lightning-compromise.md) / [Bitwarden CLI](advisories/2026-04-bitwarden-cli-shai-hulud-third-coming.md) / [TanStack](advisories/2026-05-tanstack-mini-shai-hulud.md) / [@antv+durabletask](advisories/2026-05-mini-shai-hulud-may19-wave.md) wave through Q2 2026. Remove `@vietmoney/react-big-calendar` and check for a planted exfil repo on your GitHub.
→ [advisories/2025-12-shai-hulud-3-test-payload.md](advisories/2025-12-shai-hulud-3-test-payload.md)

### 2025-12-23 — LangChain LangGrinch + path traversal (CVE-2025-68664 / CVE-2026-34070)
`langchain-core`'s `dumps()`/`dumpd()` did not escape user dicts containing the reserved `"lc"` key → attacker-controlled round-trip can instantiate framework classes, render Jinja2, read env vars, reach RCE. Patched in `langchain-core` 0.3.81 / 1.2.5 (LangGrinch) and 1.2.22 (CVE-2026-34070 path traversal). LangChain at ~98M downloads/month — anything that loads user-influenced JSON through LangChain's serializer is in scope.
→ [advisories/2025-12-langchain-langgrinch.md](advisories/2025-12-langchain-langgrinch.md)

### 2026-03-31 — `axios` compromise (70M+ weekly downloads)
Two malicious Axios versions connected to Sapphire Sleet C2 to pull a RAT. Auto-update enabled = silent infection. Removed but inspect lockfiles from late March.
→ [advisories/2026-03-axios-compromise.md](advisories/2026-03-axios-compromise.md)

### 2026-03-31 — Claude Code source-map leak (~512K lines of internal TypeScript)
Missing `*.map` entry in `.npmignore` shipped a 59.8 MB source map exposing 512,000 lines of Claude Code internals. No model weights or user data leaked. Subsequent Claude Code CVE cadence accelerated as researchers reverse-engineered internals. Patched within a day.
→ [advisories/2026-03-claude-code-source-map-leak.md](advisories/2026-03-claude-code-source-map-leak.md)

### 2026-03-27 — OpenHands git-diff command injection (CVE-2026-33718)
`get_git_diff()` interpolates the `path` param from `/api/conversations/{id}/git/diff` into a `shell=True` command — authenticated attackers run arbitrary commands in the agent sandbox. CVSS HIGH, authenticated-only (but exposed/no-auth instances are common). Fixed in **OpenHands 1.5.0**.
→ [advisories/2026-03-openhands-git-diff-rce.md](advisories/2026-03-openhands-git-diff-rce.md)

### 2026-03-17 — Langflow unauthenticated RCE (CVE-2026-33017) — CISA KEV
A single crafted HTTP request to the public flow-build endpoint runs arbitrary Python on any exposed Langflow instance — **no auth**. CVSS 9.8, exploited ~20h after disclosure (NATS-as-C2, AWS-key theft). **Incomplete fix:** 1.8.2 is still exploitable; upgrade to **1.9.0**.
→ [advisories/2026-03-langflow-rce.md](advisories/2026-03-langflow-rce.md)

### 2026-03-11 — Supabase Auth OIDC issuer-validation bypass (CVE-2026-31813)
Supabase Auth (`gotrue`) < 2.185.0 doesn't validate the OIDC token issuer when Apple/Azure providers are enabled — an attacker mints signed ID tokens from their own IdP and logs in as **any user**. Account-takeover primitive for self-hosted Supabase, the default backend for most vibe-coded apps. Fix: **2.185.0**.
→ [advisories/2026-03-supabase-auth-oidc-bypass.md](advisories/2026-03-supabase-auth-oidc-bypass.md)

### 2026-02-28 — Google Antigravity Secure Mode sandbox escape
Pillar Security: `find_by_name` tool exposed `fd -X` flag injection *before* Secure Mode's network/sandbox checks fired. Single prompt injection → arbitrary RCE outside the sandbox. Disclosed 2026-01-07, patched 2026-02-28.
→ [advisories/2026-02-google-antigravity-sandbox-escape.md](advisories/2026-02-google-antigravity-sandbox-escape.md)

### 2026-02-09 — Claude Desktop Extensions (DXT) zero-click RCE — Anthropic declines to fix
LayerX: DXT extensions run **unsandboxed with full user privileges**, and Claude will autonomously chain a low-trust reader connector (Google Calendar/email/Drive) into a high-trust local executor. A malicious calendar event + a vague prompt ("check my calendar and take care of it") = **zero-click local RCE, CVSS 10.0**; ~10,000+ users / 50 extensions. Anthropic called it "outside our current threat model" → **no patch**. Distinct from ClaudeBleed (Chrome). Don't co-locate reader and executor MCP servers in one Claude profile.
→ [advisories/2026-02-claude-desktop-extensions-rce.md](advisories/2026-02-claude-desktop-extensions-rce.md)

### 2026-01-12 — OpenCode AI coding agent — twin localhost RCEs (CVE-2026-22812 + CVE-2026-22813)
**OpenCode** — the **71K-star** open-source AI coding agent (anomalyco / SST) — shipped **two unauth RCEs** in the same window. **CVE-2026-22812** (CVSS 8.8): the local HTTP server **binds `0.0.0.0` with CORS `*`** and exposes `POST /session/{id}/shell` unauthenticated → any web page the developer visits sends one `fetch()` and runs arbitrary commands. **CVE-2026-22813** (CVSS 9.4): the chat UI inserts **LLM markdown responses straight into the DOM** with no DOMPurify and no CSP → any attacker-controlled text the agent ever reads (poisoned file, fetched page, MCP reply) → XSS → WebSocket → shell. **Both fixed in v1.0.216** (per-session auth token). **~220,000 instances exposed**; **public PoCs on GitHub** with command-exec / file-r/w / interactive-shell modes. Same "**localhost is not a security boundary in the browser-attacker model**" root cause as [OpenClaw CVE-2026-25253](advisories/2026-01-openclaw-cve-2026-25253-gatewayurl-rce.md) and [Marimo CVE-2026-39987](advisories/2026-04-marimo-notebook-rce.md); the markdown variant is a **connector-chaining lethal-trifecta in one app**.
→ [advisories/2026-01-opencode-localhost-rce.md](advisories/2026-01-opencode-localhost-rce.md)

### 2026-01-26 — OpenClaw 1-click RCE via WebSocket gateway-URL token theft (CVE-2026-25253)
**CVE-2026-25253** (CVSS 8.8) — OpenClaw's Control UI blindly trusted the `gatewayUrl` query-string parameter in browser URLs. A single click on a malicious link silently pointed OpenClaw at an attacker-controlled WebSocket gateway, leaked the **auth token**, and ran arbitrary commands on the victim's machine with the agent's full system privileges. The localhost-only assumption failed because the *browser* — which trivially reaches `localhost` — is the network attacker; even instances behind NAT were exploitable. Patched in **OpenClaw 2026.1.29** (confirmation modal; later releases added origin validation). Distinct from May's [Claw Chain cluster](advisories/2026-05-openclaw-claw-chain.md) — different bug, different month, different researcher. Public PoCs available.
→ [advisories/2026-01-openclaw-cve-2026-25253-gatewayurl-rce.md](advisories/2026-01-openclaw-cve-2026-25253-gatewayurl-rce.md)

### 2026-02-01 — ClawHavoc — mass malicious-skill poisoning of OpenClaw's ClawHub marketplace
Koi Security audited all **2,857 skills** on **ClawHub** (the open-by-default skill marketplace for the self-hosted **OpenClaw** agent, formerly Clawdbot/Moltbot) and found **341 malicious** — **335 from one campaign ("ClawHavoc")** that uses **fake prerequisites** to install **Atomic Stealer (AMOS)**. First malicious skill 2026-01-27, surge 01-31. As the marketplace grew to 10,700+ skills, the count more than doubled (824+; some trackers cite ~1,184). Publishing needs only a **GitHub account a week old**. Installing an AI-agent skill = `curl | bash` — vet the publisher, distrust any "install this first" step. **May 2026 update — Snyk "ToxicSkills":** an ecosystem-wide audit of **3,984 skills across ClawHub + skills.sh** found **prompt injection in 36%**, **1,467 malicious payloads**, and **2.9% that fetch-and-execute remote content at runtime** (so scan-on-publish misses them — a "skill scanner" badge is not safety). Class problem, multiple marketplaces, not one campaign.
→ [advisories/2026-02-clawhavoc-clawhub-skills.md](advisories/2026-02-clawhavoc-clawhub-skills.md)

### 2026-01-05 — AI IDEs recommend non-existent extensions — OpenVSX namespace hijack
Koi Security: **Cursor / Windsurf / Antigravity / Trae** recommend extensions that don't exist on **OpenVSX** (the marketplace these forks use), leaving the publisher namespaces **unclaimed** — an attacker registers `ms-ossdata.vscode-postgresql`, uploads malware, and the **IDE itself** prompts "Recommended," which installs with full local privileges. Cursor fixed 2025-12-01; Google fixed 2026-01-01; **Windsurf never responded**. Koi pre-claimed the dangling namespaces; no abuse observed pre-disclosure. Verify any "recommended" extension's publisher on open.vsx.org before installing.
→ [advisories/2026-01-vscode-fork-recommended-extension-hijack.md](advisories/2026-01-vscode-fork-recommended-extension-hijack.md)

### 2025-11-24 — Shai-Hulud "The Second Coming"
492 packages (132M monthly downloads), Zapier / ENS / PostHog / Postman trojanized. 25,000+ malicious GitHub repos. Aligned with npm classic-token revocation deadline.
→ [advisories/2025-11-shai-hulud-second-coming.md](advisories/2025-11-shai-hulud-second-coming.md)

### 2025-10 — Windsurf path-traversal via prompt-injected README — Cascade reads/writes arbitrary files (CVE-2025-62353)
**CVE-2025-62353** (CVSS 9.8) — HiddenLayer found that Windsurf's **Cascade** agent followed instructions hidden inside a project's `README.md` (HTML-comment markers, invisible to humans) to change its workspace path to the filesystem root and then **read/write arbitrary files** on the developer's machine. Critically, **Auto-Execution OFF and `write_to_file` on the explicit deny list did NOT stop it** — the deny check ran on the *current* (already-rewritten) workspace scope. Affects **all Windsurf ≤ 1.12.12**. Same "two parsers, one string" family as [Claude Code argv-smuggling](advisories/2026-05-claude-code-deeplink-rce.md), [SOCKS5 null-byte](advisories/2026-05-claude-code-sandbox-socks5-bypass.md), and [Starlette BadHost](advisories/2026-05-starlette-badhost-host-header-bypass.md). Upgrade Windsurf, rotate dev creds, audit any repo you opened in old Windsurf for invisible-comment or zero-width-Unicode injection.
→ [advisories/2025-10-windsurf-cve-2025-62353-path-traversal.md](advisories/2025-10-windsurf-cve-2025-62353-path-traversal.md)

### 2025-10-21 — Cursor & Windsurf ship stale Chromium — 94+ n-day vulns (1.8M devs)
OX Security ("Forked and Forgotten"): both IDEs lag behind upstream VS Code/Electron, inheriting **94+ already-patched Chromium/V8 n-days**; OX weaponized **CVE-2025-7656** (V8 integer overflow) against the *latest* builds. The exposure is any attacker-controlled web content rendered in the IDE (preview panes, webviews, agent-fetched pages). **Windsurf didn't respond; Cursor dismissed the PoC as "self-inflicted DoS, out of scope."** No per-bug patch — keep the IDE on its newest release and don't open untrusted content inside it.
→ [advisories/2025-10-cursor-windsurf-chromium-ndays.md](advisories/2025-10-cursor-windsurf-chromium-ndays.md)

### 2025-10-17 — GlassWorm — self-propagating VS Code / Open VSX worm (post-takedown macOS wave active as of 2026-06-12)
First self-propagating worm in VS Code/Open VSX extensions. Hides payload in **invisible Unicode** (literally unreadable in an editor); C2 was **quad-redundant** — Solana blockchain dead-drop + BitTorrent DHT + Google Calendar dead-drops + direct VPS IPs. Stole npm/GitHub/Git creds (poisoning **300+ GitHub repos** alone), drained 49 crypto wallets, dropped SOCKS proxies + hidden VNC, re-seeded itself. Multiple 2026 waves (Dec 2025; 72+ Open VSX extensions since Jan 31; v2 Mar–Apr hitting 150+ GitHub repos; 73 "sleeper" extensions in late April). On **2026-05-26 14:00 UTC**, **CrowdStrike + Google + Shadowserver Foundation** disabled all four C2 channels simultaneously — but the operator reconstituted on **fresh infrastructure** and returned in **June 2026 targeting macOS exclusively** with AES-256-CBC encryption, AppleScript/LaunchAgent persistence (replaces PowerShell/Registry), and a **hardware-wallet trojanization module** (backdoored Ledger Live + Trezor Suite). The new macOS wave also sweeps 50+ browser crypto extensions and macOS Keychain. Status: **active** — eBPF/EDR tools tuned for the Windows variant may not detect the macOS AppleScript variant. Check [koi.ai IOC list](https://www.koi.ai/blog/glassworm-goes-mac-fresh-infrastructure-new-tricks) for current macOS-wave IOCs. Almost certainly fed the [Megalodon](advisories/2026-05-megalodon-github-actions-mass-campaign.md) credential pool.
→ [advisories/2025-10-glassworm-vscode-worm.md](advisories/2025-10-glassworm-vscode-worm.md)

### 2025-09-17 — `postmark-mcp` backdoor (first malicious MCP)
v1.0.16 silently BCC'd every outgoing email to `phan@giftshop[.]club`. Built trust over 15 clean versions. 1,643 downloads before removal.
→ [advisories/2025-09-postmark-mcp-backdoor.md](advisories/2025-09-postmark-mcp-backdoor.md)

### 2025-09-15 — Shai-Hulud npm worm (original)
First self-replicating npm worm. ~200 packages including `@ctrl/tinycolor` (2.2M weekly), `ngx-bootstrap` (300k weekly). Stole GitHub/npm/AWS/GCP creds, leaked private repos.
→ [advisories/2025-09-shai-hulud-original.md](advisories/2025-09-shai-hulud-original.md)

### 2025-09-08 — `qix` account compromise (2B weekly downloads)
`chalk`, `debug`, `ansi-styles`, `strip-ansi`, `color-convert`, `wrap-ansi` + 12 more. Phishing email from `npmjs.help` impersonating npm support. ~2 hours live. Browser-side crypto-wallet hijack payload.
→ [advisories/2025-09-qix-compromise.md](advisories/2025-09-qix-compromise.md)

### 2025-08-26 — Nx `s1ngularity` (first AI-CLI-assisted malware)
Postinstall script that *invoked Claude Code and Gemini CLI* to scan for secrets. 2,349 distinct credentials leaked to public GitHub repos. 4 hours live.
→ [advisories/2025-08-nx-s1ngularity.md](advisories/2025-08-nx-s1ngularity.md)

### 2025-07-17 — Amazon Q VS Code extension wiper prompt
v1.84.0 shipped with attacker-injected prompt telling Q to wipe local filesystem + cloud resources. Malformed and inert in practice, but the supply-chain path (open PR → admin access → release) was real.
→ [advisories/2025-07-amazon-q-wiper.md](advisories/2025-07-amazon-q-wiper.md)

### 2025-07 — Cursor CurXecute (CVE-2025-54135) + MCPoison (CVE-2025-54136)
Prompt injection via MCP server data → Cursor modifies `mcp.json` → auto-executes attacker code. Patched in Cursor 1.3. MCPoison: trust bound to MCP key name, not command — persistent backdoor.
→ [advisories/2025-07-cursor-curxecute-mcpoison.md](advisories/2025-07-cursor-curxecute-mcpoison.md)

### 2025-07 — Supabase MCP lethal trifecta
Demonstrated by Simon Willison / General Analysis: Cursor + Supabase MCP with `service_role` key + reading attacker-controlled rows = full DB exfiltration via stored prompt injection. RLS bypassed entirely.
→ [advisories/2025-07-supabase-mcp-lethal-trifecta.md](advisories/2025-07-supabase-mcp-lethal-trifecta.md)

---

## 🟡 HISTORICAL — patched, but pattern recurs

### 2025-08 → 2026-Q2 — Claude Code InversePrompt + May 2026 CVE cluster (CVE-2025-54794/54795, CVE-2025-59536, CVE-2026-21852, CVE-2026-33068, CVE-2026-24887, CVE-2026-35021, CVE-2026-39861, CVE-2026-35603, TrustFall)
Indirect prompt injection chains that turn Claude Code's own tool use against the user. May 2026 added find-command bypass, prompt-editor command injection, symlink-following sandbox escape, and privilege escalation. Anthropic has patched all listed; cadence accelerated after the [source-map leak](advisories/2026-03-claude-code-source-map-leak.md). The *class* of attack (hidden text in fetched content, MCP-delivered prompts, malicious env config) keeps recurring — see also [Comment and Control](advisories/2026-04-comment-and-control-pr-injection.md).
→ [advisories/2025-08-claude-code-inverseprompt.md](advisories/2025-08-claude-code-inverseprompt.md)

### Ongoing — Slopsquatting (AI-hallucinated package names)
LLMs invent package names that don't exist. Attackers register them. Next user who pastes the same hallucinated code gets owned. 500+ packages registered in waves on PyPI.
→ [advisories/ongoing-slopsquatting.md](advisories/ongoing-slopsquatting.md)

### Ongoing — Lovable / Bolt / Replit data exposure patterns
Lovable BOLA left open 48 days. Bolt env-var leakage. Replit public repls leaking secrets. RLS misconfigurations across thousands of vibe-coded apps. **May 2026:** RedAccess scanned 380K vibe-coded apps and found ~5K leaking medical / financial / customer-service data. Class issue, not single incident. (Replit shipped Security Agent in April 2026 and Workspace Security Center 2.0 on May 8, 2026 — partial defender response.)
→ [advisories/ongoing-vibe-platform-exposure.md](advisories/ongoing-vibe-platform-exposure.md)

---

## How alerts get triaged

- **🔴 ACTIVE** — incident in last 14 days OR malware still propagating
- **🟠 RECENT** — last 12 months, still relevant to anyone with old lockfiles
- **🟡 HISTORICAL** — patched, but the attack pattern keeps re-occurring; read for context

Promotion/demotion happens on full sweeps (target: weekly). See [sources/README.md](sources/README.md) for the monitoring list.
