---
id: 2026-06-miasma-immobiliarelabs-backstage-wave
title: "Miasma hits @immobiliarelabs Backstage GitLab/LDAP plugins — 22 versions, AI-assistant config persistence (June 2026)"
date_disclosed: 2026-06-26
last_updated: 2026-06-26
severity: critical
status: contained
ecosystems: [npm, backstage]
tools_affected: ["@immobiliarelabs/backstage-plugin-gitlab", "@immobiliarelabs/backstage-plugin-gitlab-backend", "@immobiliarelabs/backstage-plugin-ldap-auth", "@immobiliarelabs/backstage-plugin-ldap-auth-backend", "any Backstage internal developer portal using these plugins"]
tags: [supply-chain, worm, credential-theft, miasma-lineage, binding-gyp, backstage, ai-config-persistence, github-actions]
---

## TL;DR

Another wave of the **Miasma / Mini Shai-Hulud** worm lineage hit npm on **2026-06-26**, compromising **22 versions across four `@immobiliarelabs` Backstage plugin packages** (GitLab and LDAP-auth integrations for the Backstage internal developer portal) — all published within a **~30-second window**. The payload uses the same **`binding.gyp` "Phantom Gyp"** install-time trick as the June 3–4 wave, but adds a new twist for this repo: it **plants persistence hooks directly in AI coding assistant config files** (`.claude/settings.json`, Cursor, GitHub Copilot, VS Code, Aider). The suspected initial-access vector is a separate compromise of the `codfish/semantic-release-action` GitHub Action two days earlier.

## What happened

Socket and StepSecurity independently disclosed that four npm packages maintained by Immobiliare Labs — `@immobiliarelabs/backstage-plugin-gitlab`, `@immobiliarelabs/backstage-plugin-gitlab-backend`, `@immobiliarelabs/backstage-plugin-ldap-auth`, and `@immobiliarelabs/backstage-plugin-ldap-auth-backend` — had **22 malicious versions published as new patch releases across every supported major version series simultaneously**, all within roughly 30 seconds on **2026-06-26**. These plugins integrate GitLab data (merge requests, pipelines, contributors) and LDAP/Active Directory authentication into **Backstage**, the widely-used internal developer portal framework — meaning victims are disproportionately platform-engineering and internal-tooling teams at larger organizations.

The install-time execution mechanism is the same **`binding.gyp` / "Phantom Gyp"** technique used in the June 3–4 wave ([2026-06-phantom-gyp-miasma-wave4.md](2026-06-phantom-gyp-miasma-wave4.md)): a `binding.gyp` file's node-gyp command expansion invokes `node index.js` directly, running at native-addon-build time rather than through a `preinstall`/`postinstall` lifecycle hook — meaning `npm install --ignore-scripts` does **not** stop it. The dropped `index.js` payload (~5 MB per StepSecurity) is layered through three obfuscation passes — a ROT-2 Caesar-shift, AES-128-GCM decryption, and `obfuscator.io`-style string-table rotation — and downloads the Bun JavaScript runtime to execute a second stage, evading tooling that only monitors Node.js process execution.

The payload harvests a broad credential set consistent with the Miasma lineage: `.env` files, npm/PyPI/RubyGems/Artifactory tokens, GitHub tokens and Actions secrets, AWS/GCP/Azure cloud credentials, Kubernetes service-account tokens, HashiCorp Vault tokens, password-manager databases, SSH keys, Docker/Slack/Twilio credentials.

**New for this wave:** the payload's `infectHost` function specifically targets **AI coding assistant configuration files** — `.claude/settings.json` (Claude Code), and equivalent config for GitHub Copilot, Cursor, VS Code, and Aider — to establish persistence hooks, joining the growing list of Miasma-lineage waves that treat AI-tool config as a write target, not just a data source to read.

**Suspected root cause:** both sources flag the **`codfish/semantic-release-action`** GitHub Action as a high-priority lead for how the attacker gained publish access — two days before the `@immobiliarelabs` packages were poisoned. This is very likely the **same compromise already tracked** in [2026-06-miasma-leoplatform-go-wave.md](2026-06-miasma-leoplatform-go-wave.md): that advisory documents the attacker force-pushing a malicious "Run Copilot" workflow to `codfish/semantic-release-action` at **2026-06-24 15:39:06 UTC**, affecting 1,442 dependent repositories, as part of the same LeoPlatform/RStreams npm wave published earlier that day. If the `@immobiliarelabs` compromise traces back to the same `codfish/semantic-release-action` incident, this is a **third downstream consequence** of that single CI/CD compromise (LeoPlatform npm packages + the Go module + now the Backstage plugins), reinforcing that a poisoned widely-used GitHub Action is a one-to-many attack multiplier, not a one-off.

## Am I affected?

```bash
# Check installed versions
npm ls @immobiliarelabs/backstage-plugin-gitlab @immobiliarelabs/backstage-plugin-gitlab-backend \
       @immobiliarelabs/backstage-plugin-ldap-auth @immobiliarelabs/backstage-plugin-ldap-auth-backend 2>/dev/null

# Compromised versions (published 2026-06-26):
# backstage-plugin-gitlab:          1.0.1, 2.1.2, 3.0.3, 4.0.2, 5.2.1, 6.13.1, 7.0.2
# backstage-plugin-gitlab-backend:  3.0.3, 4.0.2, 5.2.1, 6.13.1, 7.0.2
# backstage-plugin-ldap-auth:       1.1.4, 2.0.5, 3.0.2, 4.3.2, 5.2.1
# backstage-plugin-ldap-auth-backend: 1.1.3, 2.0.5, 3.0.2, 4.3.2, 5.2.1

# Check for the AI-assistant persistence hook
grep -l "infectHost\|Phantom Gyp" .claude/settings.json .cursor/*.json ~/.aider* 2>/dev/null

# binding.gyp presence is itself a red flag for any of these packages
find node_modules/@immobiliarelabs -name "binding.gyp" 2>/dev/null
```

If you run a Backstage instance and use any of the above plugins, check your lockfile for the listed versions regardless of `--ignore-scripts` usage — this install primitive bypasses that flag.

## If you are affected

1. **Downgrade or remove** the affected `@immobiliarelabs` packages immediately; reinstall only from a version predating 2026-06-26 or a version confirmed clean by the maintainer's post-incident release.
2. **Audit and restore AI assistant config files** — `.claude/settings.json`, `.cursor/`, VS Code settings, Aider config — for unauthorized hooks or modifications. Diff against version control.
3. **Rotate every credential class the payload targets**: npm/PyPI/RubyGems tokens, GitHub PATs and Actions secrets, cloud IAM credentials (AWS/GCP/Azure), Kubernetes service-account tokens, Vault tokens, SSH keys.
4. **If you use `codfish/semantic-release-action`** in any workflow, treat it as compromised for any run between 2026-06-24 and its confirmed remediation — rotate any secrets exposed to those workflow runs.
5. Treat the host as fully compromised if any affected version was installed and executed — follow the full server/workstation-compromise playbook, not just a credential rotation.

→ [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)

## Prevention

- **`--ignore-scripts` does not stop `binding.gyp`-triggered execution.** Pin `allow-scripts=false` in `.npmrc` (npm ≥ 11.16.0) or upgrade to npm v12, which blocks the native-addon build step by default alongside lifecycle scripts.
- **Diff AI-assistant config files on every dependency change**, the same discipline recommended for `.cursorrules`/`CLAUDE.md` in the TrapDoor advisory — treat them as a write target, not just developer-authored state.
- **Pin GitHub Actions to full commit SHAs**, not floating tags — the suspected initial-access path here was a compromised third-party Action.
- If you maintain a Backstage instance, treat internal-developer-portal plugins with the same supply-chain scrutiny as production dependencies; they often run with elevated access to your GitLab/LDAP/AD infrastructure.

→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)

## Sources

- [Socket — Miasma Mini Shai-Hulud Hits ImmobiliareLabs npm Packages](https://socket.dev/blog/miasma-mini-shai-hulud-hits-immobiliarelabs-npm-packages) — primary disclosure; affected package/version list, Phantom Gyp mechanism, `codfish/semantic-release-action` root-cause lead.
- [StepSecurity — Compromised @immobiliarelabs npm Packages](https://www.stepsecurity.io/blog/immobiliarelabs-npm-packages-compromised) — independent confirmation of package list, 30-second publish window, payload obfuscation layers, and the AI-coding-assistant `infectHost` persistence detail.
- Cross-reference: [2026-06-phantom-gyp-miasma-wave4.md](2026-06-phantom-gyp-miasma-wave4.md) — same `binding.gyp` install primitive, prior wave in the Miasma lineage.
- Cross-reference: [2026-06-miasma-wave5-microsoft-azure-github.md](2026-06-miasma-wave5-microsoft-azure-github.md) — sibling wave using source-repo/CI compromise rather than direct npm-account takeover.
