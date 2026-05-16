# Auditing a vibe-coded repo

> Scope: a repo built with Cursor / Lovable / Bolt / v0 / Replit / Claude Code that you (or someone else) needs to ship safely. Especially if it touches user data.

## The honest framing

Vibe-coded apps fail in predictable ways. Recent research (Mobb, Vibe Eval, RedAccess): **40–62% of AI-generated code contains vulnerabilities**, **91.5% of Q1 2026 vibe-coded apps had at least one AI-hallucination-related flaw**. Most issues are not exotic — they're missing auth, broken RLS, leaked keys.

The agent that wrote the code is the *worst* auditor of it. Do this with a fresh-context agent or a human.

## The 12-point audit (do this in order)

### 1. Secrets in client bundles

```bash
# Build the production bundle, then grep it
npm run build
grep -rE "service_role|sk_live_[a-zA-Z0-9]+|sk-[a-zA-Z0-9]{32,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|ghp_[a-zA-Z0-9]{36}" \
  dist/ build/ public/ .next/ out/ 2>/dev/null
```

Anything matched = key shipped to every visitor. **Stop, rotate, redeploy.**

### 2. Supabase Row-Level Security

Run in Supabase SQL editor:

```sql
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY rowsecurity, tablename;
```

Any table with `rowsecurity = false` that holds user data is a leak. Enable RLS and write explicit policies; default-deny.

```sql
ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users see own rows" ON my_table
  FOR SELECT USING (auth.uid() = user_id);
```

### 3. BOLA / IDOR in API routes

For every API route that takes a resource ID:

```bash
# Find routes
grep -rE "params\.id|req\.params|req\.query\.id|searchParams\.get" app/ pages/ api/ src/ 2>/dev/null
```

For each match: does the handler verify the **authenticated user owns the resource** before returning it? If not, BOLA. Add the check.

### 4. Auth that doesn't actually authenticate

The classic vibe-coded auth-shaped no-op: a `getUser()` call that returns the user from `localStorage` or a cookie, with no signature verification. Look for:

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

### 6. .env files committed

```bash
git log --all --full-history -- ".env" ".env.local" ".env.production" "*.env"
git log --all --full-history -- "credentials.json" "secrets.json" "config.json"
```

If anything matches, rotate every credential in those files, then use `git filter-repo` or BFG to scrub history (and **rotate again** because the original is forever on someone's clone).

### 7. Dependency audit

```bash
npm audit --production
npm outdated
# Run socket.dev or snyk on the lockfile too
```

Cross-reference against [ALERTS.md](../ALERTS.md) — anything matching = check the relevant advisory.

### 8. Hallucinated / abandoned dependencies

For every direct dep in `package.json`, spot-check:
- Does the registry page link to a real GitHub repo with stars and recent activity?
- Was the package published in the last 30 days with no history? Suspicious.
- Does the maintainer have a track record?

→ [advisories/ongoing-slopsquatting.md](../advisories/ongoing-slopsquatting.md)

### 9. CORS wide open

```bash
grep -rE "Access-Control-Allow-Origin.*\\*|cors\\(\\)|origin:\\s*['\"]\\*['\"]" app/ pages/ api/ src/ 2>/dev/null
```

`*` on a route that requires auth = CSRF surface. Lock to specific origins.

### 10. SSRF in any fetch the server makes

```bash
grep -rE "fetch\\([^'\"]*req\\.|axios.*req\\.|got\\([^'\"]*req\\." app/ pages/ api/ src/ 2>/dev/null
```

If the server makes outbound HTTP using user-controlled URLs, you have SSRF. Add an allowlist and block private-IP/metadata-service destinations.

### 11. File upload to a public bucket without validation

If you accept file uploads:
- Validate content-type AND magic bytes.
- Generate the storage key server-side (never trust client filenames).
- Confirm bucket isn't world-readable for non-public assets.

### 12. Rate limiting on auth / signup / password-reset endpoints

If there's no per-IP or per-user rate limit, you have a credential-stuffing surface and a free-tier-abuse surface. Add limits — Vercel, Cloudflare, Supabase Edge Functions all have built-in options.

## Automated help

Tools that catch most of the above:
- [Mobb](https://www.mobb.ai/) — auto-fixes a lot of these.
- [Vibe App Scanner](https://vibeappscanner.com/) — specifically for vibe-coded apps.
- [Semgrep](https://semgrep.dev/) — fast SAST with good defaults.
- [Snyk](https://snyk.io/) — dependency + code.
- [Socket](https://socket.dev/) — supply-chain focus.

## After the audit

For each issue: open a ticket, fix it, write a regression test, commit with a message that references the audit. Add the audit date to your repo's `SECURITY.md`.
