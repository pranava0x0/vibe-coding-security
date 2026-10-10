---
id: 2026-09-tinacms-admin-preview-iframe-origin-bypass-editor-session-takeover
title: "TinaCMS admin frames an attacker origin from a URL fragment and trusts its GraphQL messages, so one crafted link gives the attacker a signed-in editor's read and write access (CVE-2026-108261, CVSS 9.3; tinacms < 3.14.0, @tinacms/app < 2.5.14)"
date_disclosed: 2026-09-16
last_updated: 2026-10-10
severity: high
status: patched
ecosystems: [npm, tinacms, nextjs, astro, headless-cms]
tools_affected: ["tinacms 3.9.3 to 3.13.0 (reporter-tested range; earlier releases untested)", "@tinacms/app 2.5.6 to 2.5.13", "any Next.js, Astro or Hugo site that ships the Tina admin at /admin, including self-hosted backends"]
tags: [cve, origin-validation, open-redirect, postmessage, iframe, headless-cms, nextjs, account-takeover, one-click, incomplete-fix]
---

## TL;DR
TinaCMS, the Git-backed headless CMS that many generated Next.js and Astro sites use for their `/admin` editing panel, built its preview iframe URL from the admin's hash-router path without checking that the result stayed on the site's own origin. A doubled slash after `/~/` becomes a protocol-relative URL, so the admin loads an attacker's page in the frame, and because the same unvalidated value also sets the origin the admin trusts for `postMessage`, the attacker's frame can send any GraphQL query or mutation and the admin runs it with the signed-in editor's token and posts the result back. One link, opened by one logged-in editor, is enough; the payload lives in the URL fragment and never reaches the server or its logs. GitHub's CNA scored it CVSS 3.1 9.3. The vendor advisory was published 2026-09-16 and the fix had shipped two days earlier as `tinacms@3.14.0` and `@tinacms/app@2.5.14`; the CVE arrived on 2026-10-09. A June fix (3.9.3 / 2.5.6) had added a sender-side origin check without validating the URL it compared against, so this is a bypass of an incomplete patch. Rated `high` here rather than `critical`: it needs a signed-in editor to open the link, and the blast radius is that editor's content access plus, on self-hosted backends, the password hashes in the `authentication` collection.

## What happened
The reporter, Thai Son Dinh of VinSOC Labs, traced the chain through three files. `packages/tinacms/src/admin/index.tsx` registers a `/~/*` route in every `tinacms build` output and in `tinacms dev`, and no configuration disables it. `packages/@tinacms/app/src/preview.tsx` turns the splat into the preview iframe's `src` without confirming it is a same-origin path, and the iframe carries no `sandbox` attribute while the admin bundle ships no Content Security Policy. `packages/@tinacms/app/src/lib/preview-origin.ts` derives `expectedOrigin` from that same value, and `graphql-reducer.ts` uses it as the only check on the admin-to-preview message channel. An attacker-controlled frame therefore passes both origin checks, sends GraphQL operations, and receives the responses at its own origin.

The reporter ran a local, non-destructive proof of concept with two loopback origins and a stubbed API call that confirmed the cross-origin frame load, the trusted-origin derivation, and delivery of a query result to the attacker's frame; attacker-supplied mutations also validated against a generated schema. A live backend was not tested. The consequence as the advisory states it: the attacker can read anything the editor can read, including an `authentication` collection holding password hashes on self-hosted setups, and can create, update or delete documents.

Dates, from the sources this sweep opened: the fixed versions were published to npm on 2026-09-14; the vendor advisory GHSA-x34j-47hf-4xg7 was published 2026-09-16; the GitHub Advisory Database row was updated and CVE-2026-108261 published on 2026-10-09 (CNA GitHub, CVSS 3.1 9.3, vector `AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`). The CVE record gives the affected ranges as `tinacms < 3.14.0` and `@tinacms/app < 2.5.14`; the reporter tested only 3.12.1 / 2.5.12 and found the vulnerable code identical across 123 commits, so the lower bound is unknown. `tinacms` had 45,364 weekly downloads in the week to 2026-10-08 and the npm `latest` tag was 3.14.2 on 2026-10-10.

Why this belongs in this corpus: Tina is the editing panel a generator adds to a static or hybrid site so a non-developer can change content, which makes it the same class as [Payload CMS](2026-09-payload-cms-thirty-advisory-wave-form-builder-rce-sqli-mcp-plugin-takeover.md): a second application with its own session, its own API and its own CVE stream, living at `/admin` on a site whose owner thinks of it as "just a blog". The reporter is one of the VinSOC researchers who competed at [Pwn2Own Ireland 2026](2026-10-pwn2own-ireland-2026-ai-targets-codex-litellm-chroma-dynamo-zero-days.md) the same month.

## Am I affected?

```bash
# Is Tina in the tree, and at what version?
npm ls tinacms @tinacms/app 2>/dev/null
grep -E '"(tinacms|@tinacms/app)"' package.json package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null | head

# Fixed: tinacms >= 3.14.0 and @tinacms/app >= 2.5.14 (both published 2026-09-14; 3.14.2 is latest on 2026-10-10)
npm view tinacms version; npm view @tinacms/app version

# Is the admin deployed? The /~/ route ships in every build.
ls public/admin/index.html admin/index.html 2>/dev/null
```

You are exposed if the admin is deployed anywhere a signed-in editor might open a link from outside, which is every deployment. Self-hosted backends with an `authentication` collection have the larger blast radius because that collection holds password hashes.

## If you are affected
1. Upgrade both packages together (`tinacms` and `@tinacms/app` are released in lockstep) and rebuild and redeploy the admin; the fix is in the admin bundle, so a dependency bump without a rebuild changes nothing.
2. On self-hosted backends, rotate editor passwords and invalidate sessions, since the hashes were readable by anyone who got an editor to open a link. On Tina Cloud, review the project's recent content changes and connected editors.
3. Review the content repository's recent commits for edits no editor made; Tina writes through Git, so a malicious mutation leaves a commit.
4. If an editor reports an unexpected page inside the admin preview, treat the editor's session as compromised: [if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md).

## Prevention
Treat the generated admin panel as a product in its own right: it needs the same dependency-update cadence and the same review as the site, and its route list is part of your attack surface ([auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md), [supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)). Ship a Content Security Policy with a `frame-src` that names only your own origin, and sandbox any iframe whose URL is derived from user-reachable input.

## Sources
- [GitHub Advisory Database — GHSA-x34j-47hf-4xg7: TinaCMS admin preview iframe loads an attacker-controlled origin from the URL fragment](https://github.com/advisories/GHSA-x34j-47hf-4xg7) (fetched 2026-10-10; vendor advisory published 2026-09-16, updated 2026-10-09; CVSS 9.3; affected and patched versions; the three-file chain, the incomplete 3.9.3 / 2.5.6 fix, the proof-of-concept scope and the suggested fix; credits Thai Son Dinh, VinSOC Labs)
- [CVE Services record — CVE-2026-108261](https://cveawg.mitre.org/api/cve/CVE-2026-108261) (fetched 2026-10-10; CNA GitHub, published 2026-10-09T20:43Z, CVSS 3.1 9.3, affected `tinacms < 3.14.0` and `@tinacms/app < 2.5.14`; references PR 7522, commit `b57dbf4`, and the two release tags)
- npm registry `time` and `dist-tags` for `tinacms` and `@tinacms/app` (queried 2026-10-10: 3.13.0 / 2.5.13 published 2026-09-07, 3.14.0 / 2.5.14 published 2026-09-14, 3.9.3 published 2026-06-15, `latest` 3.14.2) and `api.npmjs.org` weekly downloads (45,364 for the week ending 2026-10-08)
