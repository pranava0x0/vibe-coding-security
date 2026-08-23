# Credential hygiene

> Where your credentials live determines how bad a compromise is. The goal: nothing high-value sitting in plaintext on disk, ever.

## Canonical references

- **[OWASP — Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)** — the authoritative reference.
- **[OWASP DevSecOps Guideline — Secrets Management](https://owasp.org/www-project-devsecops-guideline/latest/01a-Secrets-Management)**.
- **[AWS — Secure access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/securing_access-keys.html)** + **[AWS Customer Playbook Framework — Compromised IAM Credentials](https://github.com/aws-samples/aws-customer-playbook-framework/blob/main/docs/Compromised_IAM_Credentials.md)**.
- **[GitHub Docs — OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect)** — replace long-lived cloud secrets with short-lived OIDC tokens.

## The threat model

Most modern malware (Shai-Hulud, Nx s1ngularity, Mini Shai-Hulud variants) does the same first three things:

1. Read `~/.npmrc`, `~/.aws/credentials`, `~/.config/gcloud/`, `~/.kube/config`, `~/.ssh/`.
2. Grep `~/.zshrc`, `~/.bashrc`, `~/.envrc`, every `.env` file.
3. Dump the host's env vars.

Anything in those locations is **one bad `npm install` away from a public GitHub repo**.

## Apply OWASP's three core principles

Per the [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html):

1. **Secrets pipeline.** Automate creation, rotation, distribution.
2. **Dynamic secrets.** Generate on-demand at session start, expire automatically.
3. **Least-privilege everywhere.** Fine-grained access at the individual secret level.

For solo / small-team vibe coders, this maps to:

### Tier 1 — never on disk

- **Production credentials.** Cloud keys, prod DB passwords, payment API keys.
- Use **SSO + short-lived assumed roles** (AWS IAM Identity Center, GCP Workload Identity, Azure Entra).
- For CI: **OIDC federation** (GitHub Actions ↔ AWS/GCP/Azure) — see [GitHub's OIDC docs](https://docs.github.com/en/actions/concepts/security/openid-connect). No stored long-lived keys.
- For npm publishing: **[npm trusted publishing](https://docs.npmjs.com/trusted-publishers/)** with OIDC.

### Tier 2 — in a password manager, not files

- **API keys you must use locally** (Anthropic, OpenAI, Stripe test, etc.).
- Use **[1Password CLI](https://developer.1password.com/docs/cli/)**, **[Bitwarden CLI](https://bitwarden.com/help/cli/)**, **[Doppler](https://www.doppler.com/)**, or **[Infisical](https://infisical.com/)**.
- The key lives in your vault, gets injected into the process env at runtime, **never written to disk**.

Example:

```bash
# .env.template (commit this — references, not values)
ANTHROPIC_API_KEY=op://Private/Anthropic/credential
OPENAI_API_KEY=op://Private/OpenAI/credential

# Run command with creds injected at process start
op run --env-file=.env.template -- python my_script.py
```

### Tier 3 — fine on disk, but scoped

- **Dev-only credentials** (local DB password, dev API keys with sandbox scope).
- In `.env` files that are `.gitignore`d.
- File permissions: `chmod 600 .env`.
- **Never** the same key as production.

## Make `.gitignore` comprehensive

```gitignore
# Secrets
.env
.env.*
!.env.example
!.env.template
credentials.json
secrets/
*.pem
*.p12
*.pfx

# Cloud creds (in case you accidentally cd into the repo root)
.aws/
.kube/

# Common AI-tool dropouts
.claude/credentials.json
.cursor/credentials
```

## Pre-commit secret scanning

Don't rely on memory:

- **[`gitleaks`](https://github.com/gitleaks/gitleaks)** — pre-commit secret scanner.
- **[`trufflehog`](https://github.com/trufflesecurity/trufflehog)** — repo + filesystem scanner. Also what [Shai-Hulud 2.0](../advisories/2025-11-shai-hulud-second-coming.md) uses against *you* — running it on your own assets first is good defense.
- **[GitGuardian](https://www.gitguardian.com/)** + **[GitHub secret scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)** — server-side post-commit detection.

Pre-commit hook example:

```bash
#!/bin/bash
git diff --cached | grep -iE "apikey|api_key|password|token|secret|AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{32,}|sk_live_|ghp_[a-zA-Z0-9]{36}" && {
  echo "Potential secret in staged changes. Aborting commit."
  exit 1
}
```

## Never paste credentials into a chat window

Vibe coders' #1 own-goal. The chat (Cursor, Claude Code, ChatGPT, Lovable) keeps a transcript. The transcript may be:

- Synced to the cloud.
- Used for training (depending on your settings).
- Read by an MCP server connected to the agent later.
- Stored in a `.cursor/` cache file that ends up in a repo.

If you absolutely must, **mark the key as revoked afterward and rotate it**. Stripe, Anthropic, OpenAI, GitHub all support detect-and-auto-rotate for committed keys — that's the safety net, not the plan.

## Never let an agent autocomplete a credential into source

If the agent writes `STRIPE_SECRET = "sk_live_..."` into a file, even if it's `.env.example`, **the key may be valid**. Some agents have hallucinated real keys from training data. Search every generated file before committing — see the `gitleaks` hook above.

## For maintainers (you publish packages)

If anyone depends on packages you publish:

- **Hardware 2FA** on npm (`npm profile enable-2fa auth-and-writes`), GitHub, Google.
- **Granular npm tokens** with package scope, not classic tokens.
- **[Trusted publishing (OIDC)](https://docs.npmjs.com/trusted-publishers/)** from GitHub Actions or GitLab CI instead of stored tokens — would have stopped the [qix phishing compromise](../advisories/2025-09-qix-compromise.md).
- **Email forwarding off `npmjs.com`** to a personal address with phish-resistant 2FA — qix was phished via the `npmjs.help` look-alike domain.
- **Subscribe to your own `security@` alias** so npm security notices don't go to spam.

## Quarterly audit

A 30-minute audit every quarter is cheaper than one incident:

- What credentials do I have on disk? `find ~ -name ".env" -type f 2>/dev/null`
- What's in my password manager I no longer use? Cull.
- What tokens does my GitHub account have? Rotate / delete unused. [github.com/settings/tokens](https://github.com/settings/tokens)
- What OAuth apps have access to my GitHub / Google / AWS / Stripe accounts? Revoke unused.
- What backend/database projects (Supabase, Firebase, PlanetScale, Neon, Railway, etc.) are still running for apps I no longer actively ship or link to? Pause or delete the ones nothing points at anymore, and rotate any public/anon key that was ever committed or bundled before you do — see [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md).
- Run [`trufflehog filesystem ~`](https://github.com/trufflesecurity/trufflehog#filesystem-scan) to find creds you forgot.
