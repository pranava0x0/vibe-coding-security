# If your GitHub PAT leaked

> Scope: any GitHub Personal Access Token (PAT), `gh` CLI session, or SSH key that was on disk when malware ran.

## Authoritative references

- **[GitHub Docs — Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)** — official UI walkthrough.
- **[GitHub Docs — Reviewing your authorized integrations](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/reviewing-your-authorized-integrations)**.
- **[GitHub Docs — Token expiration and revocation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/token-expiration-and-revocation)**.
- **[GitHub Docs — Best practices for GitHub Actions security](https://docs.github.com/en/actions/reference/security/secure-use)**.
- **[Wiz — Hardening GitHub Actions: Lessons from Recent Attacks](https://www.wiz.io/blog/github-actions-security-guide)**.
- **[GitGuardian — How Hackers Used Stolen GitHub OAuth Tokens](https://blog.gitguardian.com/how-hackers-used-stolen-github-oauth-tokens/)** — real attack walkthrough.

## Do this first (60 seconds)

1. [github.com/settings/tokens](https://github.com/settings/tokens) → **Revoke all**.
2. [github.com/settings/tokens?type=beta](https://github.com/settings/tokens?type=beta) → revoke fine-grained tokens too.
3. [github.com/settings/applications](https://github.com/settings/applications) → review authorized OAuth apps.
4. [github.com/settings/security-log](https://github.com/settings/security-log) → look for suspicious activity in the last 24 hours.

## Triage

### What could the attacker do?

With a valid PAT:

- **Flip your private repos public.** [Shai-Hulud did this on first execution.](../advisories/2025-09-shai-hulud-original.md) Source code + committed secrets become world-readable.
- **Clone every private repo** you have access to (yours + every org you're in).
- **Create new repos** in your account to dump exfiltrated data (the `Shai-Hulud` repos / [Dune-themed names from Mini Shai-Hulud](../advisories/2026-05-tanstack-mini-shai-hulud.md)).
- **Push to your repos**, including malicious commits, force-pushes, release artifacts.
- **Add SSH keys / deploy keys** for persistent access.
- **Read/write GitHub Actions secrets** in repos where you have permissions.

### Find every place the token lives

```bash
# gh CLI session
gh auth status

# Common token locations
cat ~/.config/gh/hosts.yml | grep -i token
grep -rE "ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82}" ~/.zshrc ~/.bashrc ~/.profile ~/.envrc 2>/dev/null

# Env vars in current shell
env | grep -i -E "GH_|GITHUB_"

# SSH keys
ls -la ~/.ssh/
```

## Rotate

1. **Revoke every PAT** (classic + fine-grained).
2. **Sign out everywhere:** [github.com/settings/security](https://github.com/settings/security) → "Sessions" → revoke all.
3. **Rotate SSH keys.** Generate a new key, add to GitHub, delete the old one from `Settings → SSH and GPG keys`.
4. **Re-authenticate `gh`:** `gh auth logout && gh auth login` — prefer browser-based login with 2FA over PATs.
5. **Audit deploy keys** on every repo you own: `Settings → Deploy keys` — delete any you didn't add.
6. **Rotate GitHub Actions secrets** in every repo. `gh secret list -R OWNER/REPO` to enumerate.
7. **Check organization access.** If you're in an org, the attacker may have changed your role or added themselves; ask the org owner to review the [audit log](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization).

## Audit damage

### Were private repos flipped public?

```bash
gh repo list YOUR_USER --limit 100 --json name,visibility,createdAt,updatedAt | \
  jq '.[] | select(.visibility == "PUBLIC") | {name, updatedAt}' | head -50
```

Look for repos that should be private. Flip them back: `gh repo edit YOUR_USER/REPO --visibility private`.

If a private repo was public for more than a few seconds, **assume forks exist**. Search:

```bash
gh api "/search/repositories?q=fork:true+REPO_NAME+user:YOUR_USER" --jq '.items[] | .full_name'
```

### Were new public repos created with exfil data?

```bash
gh api /user/repos --paginate --jq '.[] | select(.created_at > "DATE_OF_COMPROMISE") | {name, private, html_url}'
```

For any unexpected repo (Shai-Hulud, Mini Shai-Hulud Dune-themed, or generic exfil dumps), **delete it** (`gh repo delete`) but **first** download its contents — those are the secrets you now know to rotate.

### Were secrets pushed as commits?

```bash
# In each repo, look for new commits authored from unfamiliar emails / times
git log --since="DATE_OF_COMPROMISE" --pretty=format:'%h %an <%ae> %ad %s'
```

## Verify cloud creds too

Anything in `.env` files or env vars on the machine → [rotating-cloud-credentials.md](rotating-cloud-credentials.md).

## Prevention going forward

**Best long-term moves:**

- Use **[fine-grained PATs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)** with explicit repo + permission scopes, never classic PATs.
- Set token expirations (≤90 days).
- For automation, use **[GitHub Apps](https://docs.github.com/en/apps)** with installation tokens (short-lived) instead of PATs.
- Enable **mandatory 2FA** on your org if you have one.
- For CI publishing: use **OIDC federation** to cloud providers and **[npm trusted publishing](https://docs.npmjs.com/trusted-publishers/)** instead of stored PATs.
- Subscribe to **[GitHub secret scanning push protection](https://docs.github.com/en/code-security/secret-scanning/push-protection-for-repositories-and-organizations)** — blocks commits that contain known token patterns.
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
