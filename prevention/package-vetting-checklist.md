# Package vetting checklist

> 60 seconds before any new install. Print this out, tape it next to your monitor, do it every time.

## When to run this checklist

- An LLM suggests `npm install X` or `pip install X` and X is unfamiliar to you.
- You're about to add a dependency a tutorial / blog mentioned.
- You're about to upgrade across a major version boundary.
- You're adding *any* MCP server.

## The 60-second check

### 1. Does the package exist? Is the name *exactly* what the LLM said?

```bash
npm view <name>          # or
pip show <name>          # or
pip index versions <name>
```

If the name doesn't exist, **don't take the LLM's suggested fix**. It hallucinated. Search for the real name.

### 2. Open the registry page

- npm: `https://www.npmjs.com/package/<name>`
- PyPI: `https://pypi.org/project/<name>/`

Look at:
- [ ] **Weekly downloads** — 5/week for a 3-year-old package is a red flag.
- [ ] **Repository link** — does it go to a real GitHub repo with stars and recent commits?
- [ ] **Homepage** — does it look like a real project, or a parked domain?
- [ ] **Maintainer** — known name? Their other packages look reasonable?
- [ ] **Published version history** — does it look organic (multiple releases over years) or suspicious (1.0.0 yesterday, 0 downloads)?

### 3. Check Socket / npq

```bash
# Socket (uses socket.dev's reputation engine)
npx socket-security scan-package <name>

# Or use the npq wrapper instead of npm install
npx npq install <name>
```

If either flags it, stop and investigate.

### 4. Skim the source

Yes, really. For a small library it takes 2 minutes. Look for:

- [ ] **Postinstall scripts** in `package.json`. If present, read what they do.
- [ ] **Network calls.** Grep for `fetch`, `http.request`, `axios`. Endpoints should match purpose.
- [ ] **Filesystem reads outside the package dir.** `readFile`, `homedir()`, `process.env.HOME`.
- [ ] **`child_process.exec` / `eval`.** Justified? Or weird?
- [ ] **Obfuscated code.** Minified-only source with no human-readable repo is a no-go.

### 5. Search for known issues

```bash
# Quick search
gh search repos "<name> compromised"
# Plus a Google: "<name> npm advisory" / "<name> CVE"
```

Check [ALERTS.md](../ALERTS.md) and [advisories/](../advisories/) for any matches.

### 6. Install with safeguards

```bash
# Disable scripts unless you've explicitly audited and need them
npm install --ignore-scripts --save-exact <name>
```

`--save-exact` writes an exact pin to `package.json` (no `^` or `~`). Combine with `npm ci` in CI.

### 7. Verify what landed

```bash
# What got pulled?
npm ls <name>

# Diff your lockfile vs. before
git diff package-lock.json | head -40
```

If 200 transitive dependencies just appeared, audit that. A "small" package shouldn't pull half the registry.

## When to skip this checklist

Never. Even for `react` or `express`, do step 6 (`--save-exact`, no scripts unless audited).

## How to make this a habit

- Alias `npm install` to `npq install` or to a wrapper that prompts.
- Pre-commit hook that blocks lockfile changes without an issue/PR description explaining the new deps.
- Tell your AI agent (in your system prompt / `CLAUDE.md`): *"Before suggesting any install, output the registry URL and the publisher name so I can verify. Never run install commands automatically."*

## What this catches

| Attack | Caught? |
|---|---|
| Slopsquatting (LLM-hallucinated names) | ✅ step 1 |
| Typo-squatting | ✅ step 2 (publisher mismatch) |
| Brand-new malicious package | ✅ step 2 (low downloads, no history) |
| Backdoored popular package (qix, axios) | ❌ — relies on Socket / CVE feed timing. Step 3 helps.
| Maintainer compromise (Shai-Hulud) | ❌ — same. Mitigation is `--ignore-scripts` + a registry proxy hold-window.

The checklist catches almost all *new-package* attacks. For *compromised popular package* attacks you need [npm-hardening.md](npm-hardening.md) on top.
