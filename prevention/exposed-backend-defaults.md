# Your backend is public by default

> Before you share the link: check that your database answers only the people it should, because right now it may answer everyone.

## Why this matters

AI builders (Lovable, Bolt, Replit, v0, Cursor) generate apps whose data layer works on the first try because the defaults are permissive. The app reads and writes fine in preview, so it ships. Three defaults account for most of the damage:

1. **Supabase row-level security (RLS) is off.** The anonymous key in your client code is public by design. RLS is the only thing deciding what that key can read. With RLS off, anyone with the key (it is in your shipped JavaScript) can read the whole table through the public API. This is CVE-2025-48757: in one study, 170 of 1,645 Lovable apps had data exposed this way.
2. **A privileged key is in the browser.** The Supabase `service_role` key bypasses RLS entirely. If it is in client code, whoever downloads the bundle has admin access to the database. AI assistants reach for it because it makes every permission error stop.
3. **Firebase rules are the starter rules.** `"rules": { ".read": true, ".write": true }` is the configuration tutorials start with. Left in place at launch, the database is public at a URL printed in your own client config.

None of these is a bug in your code. Your testing will never show them, because every key you try reads the data, including the one everyone else has.

## What to do

1. **Test your app as a stranger.** Take the anonymous key from your own client code and ask for a protected table:

   ```
   curl "https://<project>.supabase.co/rest/v1/users?select=*" \
     -H "apikey: <anon-key>" -H "Authorization: Bearer <anon-key>"
   ```

   If real rows come back, the table is public. Repeat for every table holding user data.
2. **Turn RLS on and scope the policies.** Enable row-level security on every table, then add policies that limit reads to the owner, usually `auth.uid() = user_id`. Re-run step 1: the anonymous read should return nothing.
3. **Grep your shipped bundle for the service key.**

   ```
   grep -r "service_role" dist/ build/ .next/ 2>/dev/null
   ```

   If it appears, rotate the key (it is public, treat it as burned), move privileged operations behind a server-side function holding the new key, and let the browser use the anonymous key with RLS guarding it.
4. **Read your Firebase rules as an attacker.** If `.read` or `.write` is `true` at the root, or Firestore rules grant read without an auth check, replace them with authenticated, owner-scoped rules before anything else.
5. **Automate the check.** [ProofForge](https://proofforge.live) runs the checks above against a live URL, plus a fourth for missing security headers (free, read-only, no repo access; the checks are published as [open rules](https://github.com/zambodotdev/proofforge/tree/main/rules)). Run it, or the manual steps above, after every change to rules, policies, or environment variables, not just at launch.

## What this stops / doesn't stop

**Stops:** anonymous bulk reads of your tables, admin-key takeover from a leaked bundle, and the public-database harvest that open Firebase instances get swept into.

**Doesn't stop:** an attacker with a real user account abusing overly broad per-user policies, leaks from your server-side code or logs, or anything in the supply-chain categories the rest of this repo tracks. RLS on is the floor, not the ceiling: policies still need to say the right thing per table.

## Sources

- [CVE-2025-48757 / GHSA-773x-pxjg-gxgx](https://github.com/advisories/GHSA-773x-pxjg-gxgx): missing RLS on Supabase tables in Lovable-generated apps.
- [Discoverer's write-up](https://gist.github.com/lhchavez/625ee42a6c408a850d35e50f8e649de9): how the exposed apps were found and counted (170 of 1,645).
