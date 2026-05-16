# Tools

> Software that helps prevent, detect, or recover from the incidents tracked in this repo.

## Pre-install / install-time

| Tool | What it does | Cost |
|---|---|---|
| **[Socket](https://socket.dev/)** | Reputation scoring for every npm/PyPI package, supply-chain risk signals. Browser extension + GitHub App. | Free tier; paid for orgs. |
| **[npq](https://github.com/lirantal/npq)** | Wraps `npm install`, prompts before installing low-reputation packages. | OSS. |
| **[Snyk](https://snyk.io/)** | Dep + code vuln scanning, IDE plugin, CI integration. | Free tier; paid for orgs. |
| **[StepSecurity Harden-Runner](https://github.com/step-security/harden-runner)** | Locks down GitHub Actions runners — alerts on unexpected outbound. Caught several supply-chain attacks live. | OSS / free tier. |

## Lockfile + repo scanning

| Tool | What it does | Cost |
|---|---|---|
| **`npm audit`** | Built-in. Reads GHSA. Quick first pass. | Free. |
| **[osv-scanner](https://github.com/google/osv-scanner)** | Google's all-ecosystem scanner. Reads OSV.dev. | OSS. |
| **[Semgrep](https://semgrep.dev/)** | Fast SAST with curated rule sets. Catches lots of vibe-coded antipatterns. | Free tier; paid for advanced rules. |
| **[Trivy](https://github.com/aquasecurity/trivy)** | Container + filesystem + SBOM scanner. | OSS. |

## Vibe-coded app scanning

| Tool | What it does | Cost |
|---|---|---|
| **[Vibe App Scanner](https://vibeappscanner.com/)** | Targets the specific failure modes of Lovable/Bolt/Replit/Cursor apps. | Free + paid. |
| **[Mobb](https://www.mobb.ai/)** | Auto-fixes common vibe-coded vulns. | Free tier. |
| **[Wiz](https://www.wiz.io/) / [Orca](https://orca.security/)** | Cloud + SaaS posture scanners. Overkill for solo but standard for orgs. | Paid. |

## Credential / secret management

| Tool | What it does | Cost |
|---|---|---|
| **[1Password CLI](https://developer.1password.com/docs/cli/)** | `op run --env-file=...` injects secrets at runtime, never on disk. | Paid. |
| **[Bitwarden CLI](https://bitwarden.com/help/cli/)** | OSS alternative to 1Password CLI. | Free + paid. |
| **[doppler](https://www.doppler.com/)** | Hosted secrets manager with CLI injection. | Free tier. |
| **[Infisical](https://infisical.com/)** | OSS secrets manager. Self-hostable. | OSS + cloud. |
| **[gitleaks](https://github.com/gitleaks/gitleaks)** | Pre-commit secret scanner. Wire into Husky / lefthook. | OSS. |
| **[trufflehog](https://github.com/trufflesecurity/trufflehog)** | Repo / filesystem secret scanner. Also what Shai-Hulud 2.0 uses against *you* — running it on your own assets first is good defense. | OSS + paid. |

## MCP-specific

| Tool | What it does | Cost |
|---|---|---|
| **[MCP Inspector](https://github.com/modelcontextprotocol/inspector)** | Official Anthropic tool. Sandbox + introspect an MCP before connecting it. | OSS. |
| **[mcp-scan](https://github.com/invariantlabs-ai/mcp-scan)** | Static analysis for MCP servers — flags risky patterns. | OSS. |

## Agent sandboxing

| Tool | What it does | Cost |
|---|---|---|
| **[devcontainers](https://containers.dev/)** | VS Code + Docker for isolated dev envs. The default sandboxing answer. | OSS. |
| **[Lima](https://lima-vm.io/) / [OrbStack](https://orbstack.dev/)** | Lightweight macOS VMs for higher-isolation work. | OSS / paid. |
| **[gVisor](https://gvisor.dev/)** | Userspace kernel container runtime — stronger isolation than vanilla Docker. | OSS. |
| **[Anthropic's Claude Code devcontainer](https://github.com/anthropics/claude-code)** | Reference devcontainer setup for Claude Code. Fork it. | OSS. |

## CI/CD hardening

| Tool | What it does |
|---|---|
| **[StepSecurity Harden-Runner](https://github.com/step-security/harden-runner)** | Egress allowlist + tampering detection for GitHub Actions. |
| **[zizmor](https://github.com/woodruffw/zizmor)** | Static analysis for GitHub Actions workflows. Catches the "Pwn Request" pattern that hit TanStack. |
| **[OpenSSF Scorecard](https://github.com/ossf/scorecard)** | Auto-scores your repo's security posture. |
| **[allstar](https://github.com/ossf/allstar)** | GitHub App that enforces baseline security policies on your org. |

## What we use to maintain this repo

- **Manual research** across the sources in [sources/](../sources/).
- **GHSA + Socket RSS feeds** for the first signal on most new incidents.
- **X lists** for the fastest commentary, especially weekends.
- No automation yet for promoting feed items into advisories — see [backlog.md](../backlog.md).
