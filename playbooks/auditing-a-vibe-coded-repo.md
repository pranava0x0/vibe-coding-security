# Auditing a vibe-coded repo

> Scope: a repo built with Cursor / Lovable / Bolt / v0 / Replit / Claude Code that you (or someone else) needs to ship safely. Especially if it touches user data.

## Authoritative references

- **[OWASP ASVS (Application Security Verification Standard)](https://owasp.org/www-project-application-security-verification-standard/)** — the comprehensive verification checklist; pick the level (L1/L2/L3) appropriate to your app.
- **[OWASP Top 10 (web)](https://owasp.org/Top10/)** — the universal classes.
- **[OWASP LLM Top 10 (2025)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)** — if your app calls an LLM, also audit against these.
- **[OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)** — process-level.
- **[Mobb — The Hidden Security Crisis in AI-Generated Apps (40% leak)](https://www.mobb.ai/blog/the-hidden-security-crisis-in-ai-generated-apps)** — the headline data.
- **[Equixly — Vibe coding security: the gap between "It works" and "It's safe"](https://equixly.com/blog/2026/04/07/vibe-coding-security/)** — what specifically tends to break.
- **[Towards Data Science — The Reality of Vibe Coding: AI Agents and the Security Debt Crisis](https://towardsdatascience.com/the-reality-of-vibe-coding-ai-agents-and-the-security-debt-crisis/)** — what agents *actually* do under pressure (remove validation, relax DB policies, disable auth).

## The honest framing

Vibe-coded apps fail in predictable ways. Recent research:

- **40–62% of AI-generated code** contains vulnerabilities (Mobb, Veracode).
- **91.5% of Q1 2026 vibe-coded apps** had at least one AI-hallucination-related flaw.
- **71.6% security-issue rate** across 240 samples in [SecMate's vibe-coding benchmark](https://blog.secmate.dev/posts/vibe-coding-security-benchmark/).
- Per [Towards Data Science](https://towardsdatascience.com/the-reality-of-vibe-coding-ai-agents-and-the-security-debt-crisis/): agents have been observed **removing validation checks, relaxing database policies, or disabling authentication flows simply to resolve runtime errors**.

The agent that wrote the code is the *worst* auditor of it. Do this with a fresh-context agent or a human.

## The 12-point audit (do this in order)

### 1. Secrets in client bundles

```bash
npm run build
grep -rE "service_role|sk_live_[a-zA-Z0-9]+|sk-[a-zA-Z0-9]{32,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|ghp_[a-zA-Z0-9]{36}" \
  dist/ build/ public/ .next/ out/ 2>/dev/null
```

Anything matched = key shipped to every visitor. **Stop, rotate, redeploy.**

### 2. Supabase Row-Level Security

```sql
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY rowsecurity, tablename;
```

Any table with `rowsecurity = false` holding user data is a leak. Enable RLS and write explicit policies; default-deny:

```sql
ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users see own rows" ON my_table
  FOR SELECT USING (auth.uid() = user_id);
```

See [Supabase — Defense in Depth for MCP Servers](https://supabase.com/blog/defense-in-depth-mcp).

### 3. BOLA / IDOR in API routes

OWASP API Security Top 10 [#1: Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/). The most-shipped vibe-coded vuln.

```bash
grep -rE "params\.id|req\.params|req\.query\.id|searchParams\.get" app/ pages/ api/ src/ 2>/dev/null
```

For each match: does the handler **verify the authenticated user owns the resource** before returning it? If not, BOLA. Add the check.

### 4. Auth that doesn't actually authenticate

The classic vibe-coded auth-shaped no-op: a `getUser()` that returns the user from `localStorage` with no signature verification.

```bash
grep -rE "localStorage\.getItem.*[Uu]ser|getSession|getUser" src/ app/ 2>/dev/null
```

For each, trace: does it eventually verify a JWT signature server-side, or check a session against the DB? If it just decodes a token client-side, it's not auth.

### 5. Public Supabase functions / RPC

```sql
SELECT n.nspname, p.proname, p.prosecdef
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public' AND p.prosecdef = true;
```

`SECURITY DEFINER` functions run as the function owner. If they're callable from `anon`, they bypass RLS — make sure each one does its own auth check.

### 6. `.env` files committed

```bash
git log --all --full-history -- ".env" ".env.local" ".env.production" "*.env"
git log --all --full-history -- "credentials.json" "secrets.json" "config.json"
```

If anything matches, rotate every credential in those files, then use [`git filter-repo`](https://github.com/newren/git-filter-repo) or [BFG](https://rtyley.github.io/bfg-repo-cleaner/) to scrub history (and **rotate again** because the original is forever on someone's clone).

### 7. Dependency audit

```bash
npm audit --production
npm outdated
# Also run osv-scanner or Socket on the lockfile
npx osv-scanner --lockfile=package-lock.json
```

Cross-reference [ALERTS.md](../ALERTS.md). See [prevention/npm-hardening.md](../prevention/npm-hardening.md) for the full hardening pass.

### 8. Hallucinated / abandoned dependencies

For every direct dep in `package.json`, spot-check the registry page:

- Real GitHub repo with stars and recent activity?
- Published > 30 days ago with real history?
- Maintainer has a track record?

→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
→ [slopsquatting advisory](../advisories/ongoing-slopsquatting.md).

### 9. CORS wide open

```bash
grep -rE "Access-Control-Allow-Origin.*\\*|cors\\(\\)|origin:\\s*['\"]\\*['\"]" app/ pages/ api/ src/ 2>/dev/null
```

`*` on a route that requires auth = CSRF surface. Lock to specific origins.

### 10. SSRF in any fetch the server makes

```bash
grep -rE "fetch\\([^'\"]*req\\.|axios.*req\\.|got\\([^'\"]*req\\." app/ pages/ api/ src/ 2>/dev/null
```

If the server makes outbound HTTP with user-controlled URLs, you have SSRF. Add an allowlist and block private-IP / metadata-service destinations. ([OWASP SSRF Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).)

### 11. File upload to a public bucket without validation

If you accept file uploads:

- Validate content-type AND magic bytes.
- Generate the storage key server-side (never trust client filenames).
- Confirm bucket isn't world-readable for non-public assets.

[OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html).

### 12. Rate limiting on auth / signup / password-reset endpoints

No per-IP or per-user rate limit = credential-stuffing surface + free-tier abuse surface. Vercel, Cloudflare, Supabase Edge Functions all have built-in options.

[OWASP — Authentication Cheat Sheet § Rate Limiting](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#rate-limiting).

## Automated help

Tools that catch most of the above:

- **[Mobb](https://www.mobb.ai/)** — auto-fixes many vibe-coded vulns.
- **[Vibe App Scanner](https://vibeappscanner.com/)** — specifically for vibe-coded apps; [platform-specific guides](https://vibeappscanner.com/platforms).
- **[Semgrep](https://semgrep.dev/)** — fast SAST with good defaults; community rule packs for AI-generated antipatterns.
- **[Snyk Code](https://snyk.io/product/snyk-code/)** — IDE + CI.
- **[Socket](https://socket.dev/)** — supply-chain focus.
- **[GitHub Advanced Security / CodeQL](https://github.com/features/security)** — if you're on a paid GitHub plan.
- **[Anthropic's Claude Code Security Review](https://www.anthropic.com/news/claude-code-security)** — research-preview agent; remember it's [vulnerable to Comment and Control](../advisories/2026-04-comment-and-control-pr-injection.md) so isolate its workflow's secrets.

## After the audit

For each issue: open a ticket, fix it, **write a regression test**, commit with a message that references the audit. Add the audit date to your repo's `SECURITY.md`.

For platform-specific failure patterns, see [advisories/ongoing-vibe-platform-exposure.md](../advisories/ongoing-vibe-platform-exposure.md).
