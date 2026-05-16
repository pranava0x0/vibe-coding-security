# If your npm token leaked

> Scope: any time `~/.npmrc`, a `NPM_TOKEN` env var, or a CI npm token was readable by malware.

## Do this first (60 seconds)

Open [npmjs.com/settings/tokens](https://www.npmjs.com/settings/tokens) and click **Delete** on every token. All of them. Even ones you think you need.

This stops an attacker from publishing malicious versions of *your* packages.

## Triage

### What could the attacker do?
With a valid npm publish token:

- **Publish new versions of every package you maintain** with a payload. This is exactly how Shai-Hulud and the qix compromise spread.
- **Read your private packages** (if the token has read access).
- **Add themselves as a maintainer** on packages (if the token is classic / not granular).

### Find every place the token lives

```bash
# User-level
cat ~/.npmrc

# Project-level
find . -name ".npmrc" -not -path "*/node_modules/*"

# Env vars in shell rc files
grep -E "NPM_TOKEN|npm_token" ~/.zshrc ~/.bashrc ~/.profile ~/.envrc 2>/dev/null

# CI/CD secrets
gh secret list -R YOUR_OWNER/YOUR_REPO
```

## Rotate

1. **Delete every token** at [npmjs.com/settings/tokens](https://www.npmjs.com/settings/tokens).
2. **Enable hardware 2FA** if you haven't: `npm profile enable-2fa auth-and-writes`.
3. **Switch to granular tokens.** Classic tokens have broad scope. Granular tokens (npm 2024+) can be scoped to specific packages and expirations.
4. **For CI:** prefer **npm OIDC** (Trusted Publishing) over long-lived tokens. GitHub Actions can publish to npm without any token in secrets.
5. **Replace tokens in `.npmrc` files**, then `chmod 600 ~/.npmrc`.

## Verify nothing was published in your name

```bash
# What did you publish recently?
npm whoami
npm access list packages
# Then for any package you maintain:
npm view <pkg> time --json | jq 'to_entries | sort_by(.value) | reverse | .[:5]'
```

If there's a version you didn't publish:

1. **Deprecate it immediately:** `npm deprecate <pkg>@<version> "compromised, do not use"`.
2. Contact npm security: `security@npmjs.com`. Provide token leak details so they can unpublish.
3. Open a security advisory on your GitHub repo so downstream users find it.
4. Publish a clean version with a bumped patch, plus a `SECURITY.md` note.
5. Add the incident to [advisories/](../advisories/) (or this repo, via PR).

## Prevention going forward
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

**Best long-term move:** stop storing npm tokens on disk entirely. Use OIDC for publishing from CI, and `npm login` interactively (with hardware 2FA) for local one-off publishes.
