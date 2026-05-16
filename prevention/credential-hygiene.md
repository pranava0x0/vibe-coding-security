# Credential hygiene

> Where your credentials live determines how bad a compromise is. The goal: nothing high-value sitting in plaintext on disk, ever.

## The threat model

Most modern malware (Shai-Hulud, Nx s1ngularity, Mini Shai-Hulud variants) does the same first three things:

1. Read `~/.npmrc`, `~/.aws/credentials`, `~/.config/gcloud/`, `~/.kube/config`, `~/.ssh/`.
2. Grep `~/.zshrc`, `~/.bashrc`, `~/.envrc`, every `.env` file.
3. Dump the host's env vars.

So: anything you keep in those locations is one bad `npm install` away from being on a public GitHub repo.

## What to do

### Tier 1 — never on disk

- **Production credentials.** Cloud keys, prod DB passwords, payment API keys.
  - Use **SSO + short-lived assumed roles** (AWS IAM Identity Center, GCP Workload Identity, Azure Entra).
  - For CI: **OIDC federation** (GitHub Actions ↔ AWS/GCP), no stored long-lived keys.

### Tier 2 — in a password manager, not files

- **API keys you must use locally** (Anthropic, OpenAI, Stripe test, etc.).
  - Use **[1Password CLI](https://developer.1password.com/docs/cli/)** or **[Bitwarden CLI](https://bitwarden.com/help/cli/)** with `op run --env-file=.env.template -- <cmd>` style invocation.
  - The key lives in your password vault, gets injected into the process env at runtime, and is never written to disk.

Example:
```bash
# .env.template (commit this)
ANTHROPIC_API_KEY=op://Private/Anthropic/credential
OPENAI_API_KEY=op://Private/OpenAI/credential

# Run command with creds injected
op run --env-file=.env.template -- python my_script.py
```

### Tier 3 — fine on disk, but scoped

- **Dev-only credentials** (local DB password, dev API keys with sandbox scope).
  - In `.env` files that are `.gitignore`d.
  - File permissions: `chmod 600 .env`.
  - **Never** the same key as production.

### Make sure `.gitignore` is comprehensive

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

And run this on every repo:

```bash
git diff --cached | grep -iE "apikey|api_key|password|token|secret|AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{32,}|sk_live_|ghp_[a-zA-Z0-9]{36}"
```

Add it to a pre-commit hook.

## Never paste credentials into a chat window

Vibe coders' #1 own-goal. The chat (Cursor, Claude Code, ChatGPT, Lovable) keeps a transcript. The transcript may be:
- Synced to the cloud.
- Used for training (depending on your settings).
- Read by an MCP server connected to the agent later.
- Stored in a `.cursor/` cache file that ends up in a repo.

If you absolutely must, mark the key as **revoked** afterward and rotate it.

## Never let an agent autocomplete a credential into source

If the agent writes `STRIPE_SECRET = "sk_live_..."` into a file, even if it's `.env.example`, **the key may be valid**. Some agents have hallucinated real keys from training data. Search every generated file before committing.

## For maintainers (you publish packages)

If anyone depends on packages you publish:

- **Hardware 2FA** on npm (`npm profile enable-2fa auth-and-writes`), GitHub, Google.
- **Granular npm tokens** with package scope, not classic tokens.
- **OIDC publishing** from GitHub Actions instead of stored tokens.
- **Email forwarding off `npmjs.com`** to a personal address with phish-resistant 2FA — qix was phished via a look-alike domain.
- **Subscribe to your own security@ email** alias so npm security notices don't go to spam.

## Verify periodically

Quarterly, walk through:
- What credentials do I have on disk? (`find ~ -name ".env" -type f 2>/dev/null`)
- What's in my password manager I no longer use? (Cull.)
- What tokens does my GitHub account have? Rotate / delete unused.
- What OAuth apps have access to my GitHub / Google / AWS accounts? Revoke unused.

A 30-minute audit every quarter is cheaper than one incident.
