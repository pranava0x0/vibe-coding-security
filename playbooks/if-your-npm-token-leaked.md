# If your npm token leaked

> Scope: any time `~/.npmrc`, a `NPM_TOKEN` env var, or a CI npm token was readable by malware.

## Authoritative references

- **[npm Docs — Trusted publishing for npm packages](https://docs.npmjs.com/trusted-publishers/)** — the long-term fix: stop using long-lived tokens.
- **[GitHub Changelog — npm trusted publishing with OIDC GA (Jul 2025)](https://github.blog/changelog/2025-07-31-npm-trusted-publishing-with-oidc-is-generally-available/)** + **[bulk config (Feb 2026)](https://github.blog/changelog/2026-02-18-npm-bulk-trusted-publishing-config-and-script-security-now-generally-available/)**.
- **[npm Docs — Generating provenance statements](https://docs.npmjs.com/generating-provenance-statements/)**.
- **[Snyk — NPM Security Best Practices](https://snyk.io/articles/npm-security-best-practices-shai-hulud-attack/)** — post-Shai-Hulud guidance.

## Do this first (60 seconds)

Open [npmjs.com/settings/tokens](https://www.npmjs.com/settings/tokens) and click **Delete** on every token. All of them. Even ones you think you need.

This stops an attacker from publishing malicious versions of *your* packages — the exact pattern of [Shai-Hulud](../advisories/2025-09-shai-hulud-original.md) and the [qix compromise](../advisories/2025-09-qix-compromise.md).

## Triage

### What could the attacker do?

With a valid npm publish token:

- **Publish new versions of every package you maintain** with a payload. ← How [Shai-Hulud spread](../advisories/2025-09-shai-hulud-original.md).
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
2. **Enable hardware 2FA:** `npm profile enable-2fa auth-and-writes`.
3. **Switch to granular tokens.** Classic tokens have broad scope; granular tokens (npm 2024+) scope to specific packages and have expirations.
4. **For CI: migrate to [npm Trusted Publishing](https://docs.npmjs.com/trusted-publishers/).** GitHub Actions / GitLab CI publish via OIDC — no token in secrets, ever. Requires npm CLI ≥11.5.1. [How to migrate (Phil Nash)](https://philna.sh/blog/2026/01/28/trusted-publishing-npm/).
5. **Replace tokens in `.npmrc` files**, then `chmod 600 ~/.npmrc`.

## Verify nothing was published in your name

```bash
# What did you publish recently?
npm whoami
npm access list packages

# For any package you maintain, check recent versions
npm view <pkg> time --json | jq 'to_entries | sort_by(.value) | reverse | .[:5]'

# Also check npm's GHSA feed for advisories naming you
gh api '/advisories?ecosystem=npm&per_page=20' --jq '.[] | select(.identifiers[]?.value | test("YOUR_PACKAGE"))'
```

If there's a version you didn't publish:

1. **Deprecate it immediately:** `npm deprecate <pkg>@<version> "compromised, do not use"`.
2. Contact npm security: `security@npmjs.com`. Provide token leak details so they can unpublish.
3. Open a security advisory on your GitHub repo so downstream users find it. ([GitHub Docs — Repository security advisories](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/creating-a-repository-security-advisory))
4. Publish a clean version with a bumped patch, plus a `SECURITY.md` note.
5. Add the incident to [advisories/](../advisories/) (PR welcome).

## Prevention going forward

- **Best long-term move:** [trusted publishing](https://docs.npmjs.com/trusted-publishers/) eliminates long-lived tokens entirely. The phished qix token and the stolen Nx s1ngularity token would have been useless against a trusted-publishing setup.
- Pair with **[npm provenance](https://docs.npmjs.com/generating-provenance-statements/)** so consumers can verify which pipeline built each release. (Note the [TanStack Mini Shai-Hulud advisory](../advisories/2026-05-tanstack-mini-shai-hulud.md): provenance proves which pipeline, not that the pipeline was uncompromised — pair with workflow hardening.)
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
- → [prevention/npm-hardening.md](../prevention/npm-hardening.md) (the "If you publish packages" section).
