# Tools

> Software that helps prevent, detect, or recover from the incidents tracked in this repo. Cross-referenced with the [prevention](../prevention/) and [playbooks](../playbooks/) sections.

## Pre-install / install-time

| Tool | What it does | Cost | License |
|---|---|---|---|
| **[Socket](https://socket.dev/)** | Reputation scoring + behavioral indicators ([supply-chain risk list](https://docs.socket.dev/docs/supply-chain-risk)). Browser extension + GitHub App. Caught most 2025–2026 npm worms within hours. | Free tier; paid for orgs. | Commercial |
| **[`npq`](https://github.com/lirantal/npq)** | Wraps `npm install`, prompts before installing low-reputation packages. Maintained by Liran Tal (Node.js Security WG). | Free | Apache-2.0 |
| **[Snyk Open Source](https://snyk.io/product/open-source-security-management/)** | Dep + code vuln scanning, IDE plugin, CI integration, auto-fix PRs. | Free tier; paid for orgs. | Commercial |
| **[StepSecurity Harden-Runner](https://github.com/step-security/harden-runner)** | Locks down GitHub Actions runners — alerts on unexpected outbound. Caught several supply-chain attacks live. | Free for OSS / paid tier. | Apache-2.0 |
| **[npm cooldown](https://mondoo.com/blog/npm-supply-chain-security-package-manager-defenses-2026)** | Built-in: `npm config set before "<3 days ago>"`. pnpm has `minimum-release-age`. Simplest, most underused defense. | Free | — |

## Lockfile + repo scanning

| Tool | What it does | Cost | License |
|---|---|---|---|
| **[`npm audit`](https://docs.npmjs.com/cli/v10/commands/npm-audit)** | Built-in, reads GHSA. Quick first pass. [Known limitations](https://www.pkgpulse.com/guides/why-npm-audit-is-broken) — don't rely on it alone. | Free | ISC |
| **[`osv-scanner`](https://github.com/google/osv-scanner)** | Google's all-ecosystem scanner, reads [osv.dev](https://osv.dev/). | Free | Apache-2.0 |
| **[`lockfile-lint`](https://github.com/lirantal/lockfile-lint)** | Validates lockfile sources, hostnames, integrity. Wire into pre-commit. | Free | Apache-2.0 |
| **[Semgrep](https://semgrep.dev/)** | Fast SAST with curated rule sets. Catches lots of vibe-coded antipatterns. | Free tier; paid for advanced rules. | LGPL |
| **[Trivy](https://github.com/aquasecurity/trivy)** | Container + filesystem + SBOM scanner. Strong supply-chain coverage. | Free | Apache-2.0 |
| **[GitHub Advanced Security (CodeQL)](https://github.com/features/security)** | Deep semantic analysis if you're on a paid GitHub plan. | Paid | Commercial |

## Vibe-coded app scanning

| Tool | What it does | Cost | License |
|---|---|---|---|
| **[Vibe App Scanner](https://vibeappscanner.com/)** | Targets the specific failure modes of Lovable / Bolt / Replit / Cursor apps. [Platform-specific guides](https://vibeappscanner.com/platforms). | Free + paid | Commercial |
| **[Mobb](https://www.mobb.ai/)** | Auto-fixes common vibe-coded vulns. See [their 40% leak study](https://www.mobb.ai/blog/the-hidden-security-crisis-in-ai-generated-apps). | Free tier | Commercial |
| **[Wiz](https://www.wiz.io/)** / **[Orca Security](https://orca.security/)** | Cloud + SaaS posture scanners. Standard for orgs. | Paid | Commercial |
| **[Anthropic Claude Code Security](https://www.anthropic.com/news/claude-code-security)** | Research-preview agent that scans codebases and suggests patches. Remember it's vulnerable to [Comment and Control](../advisories/2026-04-comment-and-control-pr-injection.md) — isolate its workflow secrets. | Research preview | Commercial |

## Credential / secret management

| Tool | What it does | Cost | License |
|---|---|---|---|
| **[1Password CLI](https://developer.1password.com/docs/cli/)** | `op run --env-file=...` injects secrets at runtime, never on disk. | Paid | Commercial |
| **[Bitwarden CLI](https://bitwarden.com/help/cli/)** | OSS alternative to 1Password CLI. | Free + paid | GPL |
| **[Doppler](https://www.doppler.com/)** | Hosted secrets manager with CLI injection. | Free tier | Commercial |
| **[Infisical](https://infisical.com/)** | OSS secrets manager. Self-hostable. | Free + cloud | MIT |
| **[HashiCorp Vault](https://www.vaultproject.io/)** | Industry-standard secrets vault for orgs; dynamic secrets, leasing. | Free + Enterprise | MPL / BSL |
| **[`gitleaks`](https://github.com/gitleaks/gitleaks)** | Pre-commit secret scanner. Wire into Husky / lefthook. | Free | MIT |
| **[`trufflehog`](https://github.com/trufflesecurity/trufflehog)** | Repo + filesystem secret scanner. Also what [Shai-Hulud 2.0 uses against you](../advisories/2025-11-shai-hulud-second-coming.md) — running it on your own assets first is good defense. | Free + paid | AGPL |
| **[GitGuardian](https://www.gitguardian.com/)** | Server-side commit scanning + history sweep. | Free tier | Commercial |
| **[GitHub secret scanning + push protection](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)** | Built into GitHub. Blocks commits with known token patterns. Free for public repos. | Free / paid | — |

## MCP-specific

| Tool | What it does | Cost | License |
|---|---|---|---|
| **[MCP Inspector](https://github.com/modelcontextprotocol/inspector)** | Official Anthropic tool. Sandbox + introspect an MCP before connecting. | Free | MIT |
| **[`mcp-scan`](https://github.com/invariantlabs-ai/mcp-scan)** | Static analysis for MCP servers — flags risky patterns. | Free | Apache-2.0 |

## Agent sandboxing

| Tool | What it does | Cost | License |
|---|---|---|---|
| **[devcontainers](https://containers.dev/)** | VS Code + Docker isolated dev envs. The default answer for AI agent sandboxing. | Free | MIT |
| **[Claude Code built-in sandbox](https://www.anthropic.com/engineering/claude-code-sandboxing)** | Anthropic's official filesystem + network isolation. ~84% reduction in permission prompts in their internal testing. | Free | Commercial |
| **[Lima](https://lima-vm.io/)** / **[OrbStack](https://orbstack.dev/)** | Lightweight macOS VMs for higher-isolation work. | Free / paid | Apache-2.0 / Commercial |
| **[gVisor](https://gvisor.dev/)** | Userspace kernel container runtime — stronger isolation than vanilla Docker. | Free | Apache-2.0 |
| **[Anthropic's Claude Code devcontainer](https://github.com/anthropics/claude-code)** | Reference devcontainer setup. Fork it. | Free | MIT |

## CI/CD hardening

| Tool | What it does | License |
|---|---|---|
| **[StepSecurity Harden-Runner](https://github.com/step-security/harden-runner)** | Egress allowlist + tampering detection for GitHub Actions. Caught real attacks live. | Apache-2.0 |
| **[`zizmor`](https://github.com/woodruffw/zizmor)** | Static analysis for GitHub Actions workflows. Catches the "Pwn Request" pattern that hit [TanStack](../advisories/2026-05-tanstack-mini-shai-hulud.md). | MIT |
| **[OpenSSF Scorecard](https://github.com/ossf/scorecard)** | Auto-scores your repo's security posture (signed commits, dependency pinning, branch protection, etc.). | Apache-2.0 |
| **[OpenSSF Allstar](https://github.com/ossf/allstar)** | GitHub App that enforces baseline security policies across your org. | Apache-2.0 |
| **[`npm` trusted publishing](https://docs.npmjs.com/trusted-publishers/)** | Built into npm CLI ≥11.5.1. OIDC publishing from CI; kill long-lived tokens. | — |
| **[npm provenance](https://docs.npmjs.com/generating-provenance-statements/)** | `npm publish --provenance` adds SLSA-style attestation. | — |

## Standards and frameworks (reference)

For teams that want to formalize this:

- **[SLSA — Supply-chain Levels for Software Artifacts](https://slsa.dev/)** ([OpenSSF project](https://openssf.org/projects/slsa/)) — incrementally adoptable supply-chain integrity. v1.2 added the Source Track in November 2025.
- **[NIST SSDF (SP 800-218)](https://csrc.nist.gov/Projects/ssdf)** — Secure Software Development Framework.
- **[CISA — Defending Against Software Supply Chain Attacks](https://www.cisa.gov/resources-tools/resources/defending-against-software-supply-chain-attacks)**.
- **[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)** — concise, authoritative cheatsheets for every common AppSec topic.
- **[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)** — verification standard.
- **[OWASP LLM Top 10 (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)** — AI-specific.
- **[Model Context Protocol — Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)** — canonical MCP guidance.

## What we use to maintain this repo

- **Manual research** across the sources in [sources/](../sources/).
- **GHSA + Socket RSS feeds** for the first signal on most new incidents.
- **X lists** for the fastest commentary (especially weekends).
- **[`vibe-security-update` skill](../.claude/skills/vibe-security-update/SKILL.md)** — tiered sweep (deep 24h / medium 3d / shallow 7d) with self-learning source-priority list. Run it via Claude Code to refresh ALERTS.md and the advisories.
