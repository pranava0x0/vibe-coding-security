# npm hardening

> Reduce the blast radius of `npm install` so that a compromised package can't trivially own you.

## Canonical playbooks (read first)

If you take the time to read one thing, read these. The rest of this doc summarizes and adapts their advice for vibe coders.

- **[OWASP NPM Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/NPM_Security_Cheat_Sheet.html)** — the foundational reference.
- **[Snyk — NPM Security Best Practices After the Shai-Hulud Attack](https://snyk.io/articles/npm-security-best-practices-shai-hulud-attack/)** — updated specifically for the 2025–2026 worm wave.
- **[npm Docs — Trusted publishing for npm packages](https://docs.npmjs.com/trusted-publishers/)** — official, kill long-lived publish tokens.
- **[Lirantal — npm-security-best-practices](https://github.com/lirantal/npm-security-best-practices)** — `npq` author, Node.js Security Working Group lead.
- **[bodadotsh — npm-security-best-practices](https://github.com/bodadotsh/npm-security-best-practices)** — continuously updated post-incident.
- **[Mondoo — npm Supply Chain Security in 2026](https://mondoo.com/blog/npm-supply-chain-security-package-manager-defenses-2026)** — what `npm` does and does not protect you from.
- **[Lessons from the Spring 2026 OSS Incidents](https://dev.to/trknhr/lessons-from-the-spring-2026-oss-incidents-hardening-npm-pnpm-and-github-actions-against-1jnp)** — npm + pnpm + GitHub Actions hardening, post-TanStack.

## The single highest-leverage setting

```bash
npm config set ignore-scripts true
```

Globally disables `preinstall` / `install` / `postinstall` scripts. **Shai-Hulud, Nx s1ngularity, and most npm worms execute via `postinstall`** — this neuters the most common attack vector with one line. (Per Snyk and Mondoo, this is the #1 recommended setting.)

Trade-off: a few legitimate packages need install scripts (`esbuild`, `sharp`, `node-sass`). For those, audit what they do, then enable per-install:

```bash
npm install <pkg> --foreground-scripts --ignore-scripts=false
```

Or maintain a per-project `.npmrc` re-enabling scripts only in projects you've vetted.

## Use `npm ci`, not `npm install`, in CI

`npm install` resolves versions live and can pull a freshly-published malicious version. `npm ci` installs *exactly* what's in `package-lock.json` — same SHAs, every time. ([Snyk](https://snyk.io/articles/npm-security-best-practices-shai-hulud-attack/), [Mondoo](https://mondoo.com/blog/npm-supply-chain-security-package-manager-defenses-2026).)

```bash
# In every CI job
npm ci --ignore-scripts
```

## Add a release cooldown (most underused defense)

Malicious packages are usually discovered and unpublished within hours or days. Skipping any version published in the last 3 days gives the community time to catch problems before they reach you — see [Mondoo's writeup](https://mondoo.com/blog/npm-supply-chain-security-package-manager-defenses-2026).

```bash
# npm
npm config set before "$(date -u -d '3 days ago' +%Y-%m-%dT%H:%M:%SZ)"

# pnpm has a built-in minimumReleaseAge setting
echo 'minimum-release-age=4320' >> .npmrc  # 4320 minutes = 3 days
```

For organizations: enforce the cooldown at a **registry proxy** (Cloudsmith, JFrog Xray, Sonatype Nexus Firewall). New tarballs are held for 24–72h before sync, blocking install during the typical detection-and-takedown window.

## Pin exactly, not loosely

Avoid `^` and `~` for security-relevant deps (build tools, HTTP clients, IPC libs). Pin exact:

```json
{
  "dependencies": {
    "axios": "1.7.4",        // not "^1.7.4"
    "node-ipc": "9.2.1"      // not "~9.2.1"
  }
}
```

The lockfile already pins SHAs, but a fresh `npm install` (vs `npm ci`) can resolve a new in-range version and replace the lock entry — including the malicious one if you're unlucky.

## Use `overrides` to block known-bad versions

When an advisory hits, block the bad version range across the entire transitive tree:

```json
{
  "overrides": {
    "axios": "1.7.4",
    "node-ipc": "9.2.1"
  }
}
```

For yarn use `resolutions`. For pnpm use `pnpm.overrides`.

## Validate lockfile integrity

[`lockfile-lint`](https://github.com/lirantal/lockfile-lint) validates that package sources come from trusted registries and no malicious modifications were introduced. Run in pre-commit:

```bash
npx lockfile-lint --path package-lock.json \
  --allowed-hosts npm \
  --validate-https \
  --validate-package-names \
  --validate-integrity
```

## Scan before merge

Wire these into pre-commit and CI:

- **[Socket](https://socket.dev/)** — reputation per package + [supply-chain risk indicators](https://docs.socket.dev/docs/supply-chain-risk). Free for open source.
- **[OSV-Scanner](https://github.com/google/osv-scanner)** — Google's all-ecosystem scanner backed by [osv.dev](https://osv.dev/).
- **[Snyk Open Source](https://snyk.io/product/open-source-security-management/)** — known CVEs in deps.
- **[`npq`](https://github.com/lirantal/npq)** — wraps `npm install` and prompts before installing low-reputation packages.

> **About `npm audit`:** useful but limited. It checks known advisories from GHSA; it can't detect novel typosquats, account takeovers, or freshly-injected malware. Don't rely on it alone — see [Why npm Audit Is Broken](https://www.pkgpulse.com/guides/why-npm-audit-is-broken).

## If you publish packages: enable trusted publishing

Stop storing long-lived npm tokens in CI. **[Trusted publishing](https://docs.npmjs.com/trusted-publishers/)** (npm CLI ≥11.5.1) lets your GitHub Actions or GitLab CI workflow publish via OIDC — no token in secrets, ever. [GA'd July 2025](https://github.blog/changelog/2025-07-31-npm-trusted-publishing-with-oidc-is-generally-available/); [bulk config GA'd Feb 2026](https://github.blog/changelog/2026-02-18-npm-bulk-trusted-publishing-config-and-script-security-now-generally-available/). The phished `qix` token and Nx s1ngularity token would both have been useless with trusted publishing.

Pair with **[npm provenance](https://docs.npmjs.com/generating-provenance-statements/)** so consumers can verify the build pipeline produced the artifact:

```bash
npm publish --provenance
```

Note the [TanStack Mini Shai-Hulud advisory](../advisories/2026-05-tanstack-mini-shai-hulud.md): valid SLSA provenance proves *which pipeline* built the artifact, not that the pipeline was uncompromised. Provenance is necessary but not sufficient — combine with workflow hardening below.

## Audit the lockfile diff in every PR

Code review: when a PR touches `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml`, **read the new entries**. A PR titled "fix typo" that adds 47 transitive deps is a flag.

## For consumers downstream of CI/CD

Harden your GitHub Actions workflows — most modern npm worms (Shai-Hulud 2.0, TanStack Mini) propagate via compromised CI:

- **[GitHub's official Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)**
- **[Wiz — Hardening GitHub Actions: Lessons from Recent Attacks](https://www.wiz.io/blog/github-actions-security-guide)**
- **[`zizmor`](https://github.com/woodruffw/zizmor)** — static analysis for Actions workflows; catches the Pwn Request pattern that hit TanStack
- **[StepSecurity Harden-Runner](https://github.com/step-security/harden-runner)** — runtime egress allowlist for Actions
- Pin actions to **commit SHAs**, not version tags. (`uses: foo/bar@abc1234…` not `uses: foo/bar@v1`.)

## What this stack stops

| Attack | Mitigation |
|---|---|
| Shai-Hulud, Nx s1ngularity (postinstall) | `ignore-scripts` |
| Axios, qix (auto-update to bad version) | `npm ci` + exact pins + cooldown |
| Brand-new malicious package | cooldown + Socket pre-install check |
| Transitive bad versions | `overrides` / `resolutions` |
| Maintainer phishing → publish-as-you | trusted publishing + hardware 2FA |
| TanStack-style CI-pipeline compromise | hardened Actions + cooldown + Socket alerts |
| Lockfile tampering | `lockfile-lint` |

## What it doesn't stop

- A legitimately-trusted maintainer's account compromised AND your scanner not yet flagging it AND your cooldown not yet elapsed. This is the irreducible residual risk — the only real mitigation is **distance** (vendor the dep, fork it, or don't depend on it).
- Provenance-signed but pipeline-compromised packages (the TanStack pattern). Defense-in-depth still helps: registry proxy hold-window + Socket alerts catch most of these within hours.

## Reference frameworks

For teams formalizing this:

- **[SLSA — Supply-chain Levels for Software Artifacts](https://slsa.dev/)** ([OpenSSF project](https://openssf.org/projects/slsa/)) — incrementally adoptable supply-chain integrity levels. npm has the deepest SLSA integration of any package ecosystem.
- **[NIST SSDF (SP 800-218)](https://csrc.nist.gov/Projects/ssdf)** — Secure Software Development Framework.
- **[CISA — Defending Against Software Supply Chain Attacks](https://www.cisa.gov/resources-tools/resources/defending-against-software-supply-chain-attacks)**.
- **[OpenSSF Scorecard](https://github.com/ossf/scorecard)** + **[Allstar](https://github.com/ossf/allstar)** — auto-score and enforce baseline security policies on your repos.
