# Package vetting checklist

> 60 seconds before any new install. Print this, tape it next to your monitor, do it every time.

## When to run this checklist

- An LLM suggests `npm install X` or `pip install X` and X is unfamiliar.
- You're about to add a dependency a tutorial / blog mentioned.
- You're about to upgrade across a major version boundary.
- You're adding *any* MCP server. (See also [mcp-hygiene.md](mcp-hygiene.md).)

## The 60-second check

### 1. Does the package exist? Is the name *exactly* what the LLM said?

```bash
npm view <name>          # or
pip show <name>          # or
pip index versions <name>
```

If the name doesn't exist, **don't take the LLM's suggested fix**. It hallucinated. Search for the real name. → [slopsquatting advisory](../advisories/ongoing-slopsquatting.md).

### 2. Open the registry page

- npm: `https://www.npmjs.com/package/<name>`
- PyPI: `https://pypi.org/project/<name>/`

Check:

- [ ] **Weekly downloads** — 5/week for a 3-year-old package is a red flag.
- [ ] **Repository link** — does it go to a real GitHub repo with stars and recent commits?
- [ ] **Homepage** — does it look like a real project, or a parked domain?
- [ ] **Maintainer** — known name? Their other packages look reasonable?
- [ ] **Published version history** — multi-year organic releases, or "1.0.0 yesterday, 0 downloads"?

### 3. Check Socket / OSV / npq

```bash
# Socket (uses socket.dev's reputation engine; flags typosquats, install scripts,
# obfuscated code, network calls, environment access, etc.)
npx socket-security scan-package <name>

# OSV-Scanner (Google, all-ecosystem)
osv-scanner --lockfile=package-lock.json

# Or use npq as a wrapper around `npm install`
npx npq install <name>
```

[Socket's supply-chain risk indicators](https://docs.socket.dev/docs/supply-chain-risk) explicitly look for: new install scripts, network requests, environment variable access, telemetry calls, suspicious strings, obfuscated code, and dozens of other signals. Their typosquat heuristic flags packages whose names are 1–2 characters from a more popular package with 1,000× the downloads.

### 4. Skim the source

Yes, really. For a small library it takes 2 minutes. Look for:

- [ ] **Postinstall scripts** in `package.json` — if present, read what they do.
- [ ] **Network calls** — `fetch`, `http.request`, `axios`. Endpoints should match purpose.
- [ ] **Filesystem reads outside the package dir** — `readFile`, `homedir()`, `process.env.HOME`.
- [ ] **`child_process.exec` / `eval`** — justified or weird?
- [ ] **Obfuscated code** — minified-only source with no human-readable repo is a no-go.

### 5. Search for known issues

```bash
# Quick searches
gh search repos "<name> compromised"
gh api "/advisories?ecosystem=npm&affects=<name>" --jq '.[] | .ghsa_id'
# Plus Google: "<name> npm advisory" / "<name> CVE"
```

Cross-check [ALERTS.md](../ALERTS.md) and [advisories/](../advisories/) for matches.

### 6. Install with safeguards

```bash
# Disable scripts unless you've explicitly audited
npm install --ignore-scripts --save-exact <name>
```

`--save-exact` writes an exact pin to `package.json`. Combine with `npm ci` in CI. See [npm-hardening.md](npm-hardening.md) for the full picture.

### 7. Verify what landed

```bash
# What got pulled in?
npm ls <name>

# Diff your lockfile vs. before
git diff package-lock.json | head -40
```

If 200 transitive deps just appeared, audit that. A "small" package shouldn't pull half the registry.

## Make it a habit

- Alias `npm install` to `npq install` or to a wrapper that prompts.
- Add a pre-commit hook that blocks lockfile changes without an issue/PR description explaining the new deps.
- Tell your AI agent in your system prompt / `CLAUDE.md`:
  > *"Before suggesting any install, output the registry URL and the publisher name so I can verify. Never run install commands automatically."*

## What this catches

| Attack | Caught? |
|---|---|
| Slopsquatting (LLM-hallucinated names) | ✅ step 1 |
| Typo-squatting | ✅ steps 2–3 (publisher mismatch, Socket flag) |
| Brand-new malicious package | ✅ steps 2–3 (low downloads, no history, Socket flag) |
| Backdoored popular package ([qix](../advisories/2025-09-qix-compromise.md), [Axios](../advisories/2026-03-axios-compromise.md)) | ❌ — relies on Socket / CVE feed timing. Step 3 helps. Add a [release cooldown](npm-hardening.md#add-a-release-cooldown-most-underused-defense). |
| Maintainer compromise ([Shai-Hulud](../advisories/2025-09-shai-hulud-original.md)) | ❌ — same. Mitigation is `--ignore-scripts` + registry proxy cooldown. |

The checklist catches almost all *new-package* attacks. For *compromised popular package* attacks you also need [npm-hardening.md](npm-hardening.md).

## Authoritative references

- **[OWASP NPM Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/NPM_Security_Cheat_Sheet.html)** — section 2 covers consumer-side vetting.
- **[Socket — Supply Chain Risk indicators](https://docs.socket.dev/docs/supply-chain-risk)** — what to grep for and why.
- **[Snyk — NPM Security Best Practices](https://snyk.io/articles/npm-security-best-practices-shai-hulud-attack/)** — post-Shai-Hulud refresh.
- **[Lirantal — `npq`](https://github.com/lirantal/npq)** — the wrapper that does most of this for you.
