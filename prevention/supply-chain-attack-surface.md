# Supply-chain attack surface: where external code & data get in

> Every channel through which code or data from the internet reaches your machine, your CI, or your users — with the one defense that matters for each. Start here, then go deep in the linked guide. If you only remember one thing: **anything you didn't write and didn't pin is running on trust.**

Most people picture "supply-chain risk" as `npm install`. That's one door. In a modern vibe-coding setup there are at least eleven, and the agent opens several of them for you. This page maps them so nothing is invisible. Each row links to the deep guide or the incidents that prove it matters.

## The pathways

### 1. Package managers (npm · PyPI · cargo · gem · …)
The obvious one. An LLM suggests a package, the agent runs `npm install` / `pip install`, and direct **and transitive** dependencies — plus their lifecycle scripts — execute on your machine.
- **Defense:** `ignore-scripts`, a release **cooldown** (skip anything published in the last few days), exact pins, and a 15-second registry check before installing what an LLM suggested. → [npm-hardening.md](npm-hardening.md), [package-vetting-checklist.md](package-vetting-checklist.md)
- **Proof:** [Shai-Hulud](../advisories/2025-09-shai-hulud-original.md), [qix](../advisories/2025-09-qix-compromise.md), [node-ipc](../advisories/2026-05-node-ipc-compromise.md), [slopsquatting](../advisories/ongoing-slopsquatting.md).

### 2. Lockfiles & transitive depth
A clean `package.json` says nothing about the hundreds of transitive packages a lockfile pins. No lockfile = `install` resolves live and can pull a freshly-published malicious version.
- **Defense:** commit the lockfile, use `npm ci` (not `install`) in CI, and **read the lockfile diff in every PR** — "fix typo" + 47 new transitive deps is a flag. Pin Python with hashes (`--require-hashes` / `uv lock`).

### 3. CI/CD — third-party GitHub Actions
Your CI runs `uses:` steps you don't control, with your repo's write token and secrets, on every push and on a timer. A re-taggable action is remote code with credentials.
- **Defense:** pin every action to a commit **SHA**, scope `permissions:` to the floor, never give a floating third-party action a write token. → [ci-cd-hardening.md](ci-cd-hardening.md)
- **Proof:** [Megalodon](../advisories/2026-05-megalodon-github-actions-mass-campaign.md), [elementary-data](../advisories/2026-04-elementary-data-pypi-ghcr-compromise.md), [Comment-and-Control](../advisories/2026-04-comment-and-control-pr-injection.md).

### 4. Third-party code in the browser (CDN `<script>`, web fonts)
A `<script src="https://cdn…">` or a CDN ES-module import loads **unverified remote code into every visitor's browser**, gated only by a mutable version URL. If the CDN or package is compromised, your users run the attacker's JS.
- **Defense:** add **Subresource Integrity** (`integrity="sha384-…"`) to every third-party `<script>`/`<link>`, or self-host the asset. Self-host fonts to also stop the IP leak to the font CDN. (SRI can't cover dynamically-generated CSS like Google Fonts — self-host those.)

### 5. MCP servers & AI-agent skills / plugins
An MCP server or an installed agent skill is **arbitrary code running with your agent's privileges** — and these marketplaces are usually open-by-default.
- **Defense:** read the source, check the publisher, pin a version, and prefer session-scoped auth over long-lived tokens before connecting anything. → [mcp-hygiene.md](mcp-hygiene.md)
- **Proof:** [Postmark MCP backdoor](../advisories/2025-09-postmark-mcp-backdoor.md), [ClawHavoc / ClawHub](../advisories/2026-02-clawhavoc-clawhub-skills.md), [systemic MCP stdio RCE](../advisories/2026-05-mcp-stdio-systemic-rce.md).

### 6. The AI coding agent itself — and its config
The agent autonomously runs installs, launches servers, and follows instructions it reads. Its **permission/allowlist config** decides how much runs without you. A wildcard auto-approve (e.g. `Bash(curl:*)`, `Bash(npm:*)`, `Bash(pip install:*)`, or — worse — auto-approving a command that echoes a secret) turns any prompt-injection or mistake into unattended code execution and credential leakage.
- **Defense:** don't run with `--dangerously-skip-permissions` on your host; sandbox the agent; keep allowlists **narrow and per-project** (scope `curl` to specific domains, never auto-approve printing secrets, constrain `install` to subcommands). → [agent-sandboxing.md](agent-sandboxing.md)

### 7. Editor & browser extensions
VS Code / Cursor / Open VSX extensions and browser extensions are first-class code with broad reach into everything the editor or browser touches — and a recurring compromise vector.
- **Defense:** treat an extension install like a dependency — check the publisher, pin where possible, and periodically audit what's installed.
- **Proof:** [Nx Console](../advisories/2026-05-nx-console-vscode-compromise.md), [GlassWorm](../advisories/2025-10-glassworm-vscode-worm.md), [ClaudeBleed](../advisories/2026-05-claudebleed-chrome-extension.md).

### 8. Scraped / fetched web data
Data is not safe just because it isn't code. Fetched HTML/JSON/PDF/CSV/XML can carry **unsafe-deserialization** payloads, **XXE**, **CSV formula injection** (a cell starting `=`/`+`/`-`/`@` executes when the export is opened in a spreadsheet), **stored XSS** if rendered back unescaped, and **prompt injection** when an ingested document is fed to an LLM.
- **Defense:** parse with safe loaders only (`yaml.safe_load`, never `pickle`/`pandas.read_pickle` on fetched bytes, disable XXE), neutralize CSV cells on export, **escape every scraped value before rendering**, and treat any document you feed to an LLM as attacker-controlled.

### 9. Downloaded datasets & binaries
A dataset, model weight, PDF, or release binary pulled from the web is an artifact you're trusting blind unless you verify it.
- **Defense:** record provenance (**source URL + SHA-256 + capture date**) and verify checksums/signatures (`gh attestation verify`, `cosign verify-blob`) before use. Never commit opaque binaries you can't re-derive.

### 10. Global / system installs
`brew install`, `npm i -g`, `pipx`, `uv tool install`, and `curl … | bash` setup scripts run **outside any repo and outside any lockfile** — invisible to your project's controls but on the same machine as your keys.
- **Defense:** prefer project-local installs; pin versions and verify checksums for global tools; read any `curl|bash` script before piping it to a shell.

### 11. Hosted build environments (Vercel · Netlify · CI runners)
When you deploy on a hosted builder, **it** runs `install` with your env vars/secrets on a machine you don't control. Same package-supply-chain rules apply, one trust-boundary further out.
- **Defense:** commit lockfiles, pin, apply the cooldown, and scope deploy tokens narrowly — the build environment inherits all of §1–§3.

## The one habit per pathway

| Pathway | Do this and most of the risk is gone |
|---|---|
| Package managers | cooldown + `ignore-scripts` + pin |
| Lockfiles | commit it, `npm ci`, read the diff |
| GitHub Actions | pin to SHA, least-priv permissions |
| Browser CDN | SRI or self-host |
| MCP / agent skills | read source, pin, session-scoped auth |
| The agent's config | narrow allowlists, never auto-approve secrets |
| Editor/browser extensions | vet like a dependency, audit periodically |
| Scraped data | safe parsers, escape on render, neutralize CSV |
| Datasets/binaries | record provenance + verify checksum/signature |
| Global installs | project-local, pin, read the script |
| Hosted builds | lockfiles + pins + narrow deploy tokens |

> The throughline: **pin what you can, verify what you can't, and never auto-trust anything published in the last few days.** Distance — vendoring, forking, or simply not taking the dependency — is the only defense that always works.
