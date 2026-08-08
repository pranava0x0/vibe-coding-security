---
id: 2026-07-postcss-tailwind-sourcemappingurl-file-read
title: "PostCSS sourceMappingURL arbitrary file read (CVE-2026-45623, CVSS 7.5) — reachable through Tailwind CSS's build pipeline"
date_disclosed: 2026-07-20
last_updated: 2026-08-08
severity: high
status: patched
ecosystems: [npm, javascript, css]
tools_affected: [postcss, tailwindcss]
tags: [path-traversal, arbitrary-file-read, information-disclosure, build-pipeline, css]
---

## TL;DR
PostCSS — the CSS transform engine underneath Tailwind CSS, Vite, and most modern frontend build pipelines — parsed the `/*# sourceMappingURL=PATH */` comment in any CSS it processed and read that path off the local filesystem with **no traversal check, allowlist, or scheme validation**, by default, no configuration needed. Anyone who can get untrusted CSS into a PostCSS `process()` call (user-uploaded themes, CMS templates, a build step over a third-party CSS file) can read arbitrary files the Node process can access and leak the first ~10 bytes of file content through a `JSON.parse` error message, plus get a precise file-existence oracle. **CVE-2026-45623**, GHSA-6g55-p6wh-862q, CVSS **7.5**. Fixed in **PostCSS 8.5.12** — Tailwind CSS projects pull PostCSS as a transitive dependency, so `npm update postcss` (or bumping Tailwind past whatever version pins the old PostCSS) is the fix.

## What happened
PostCSS's `PreviousMap` class parses source-map comments embedded in CSS — the standard `/*# sourceMappingURL=... */` annotation used to point a browser's devtools at the original, pre-build source file. In versions **8.5.11 and earlier**, `PreviousMap` took whatever path followed `sourceMappingURL=` and dereferenced it directly against the local filesystem, with no check that the path stayed inside the project directory, no scheme restriction (so `file://` and relative `../../` traversal both work), and no allowlist.

Because this runs by default with no opt-in flag, **any code path that hands attacker-influenced CSS to PostCSS's `process()`** is exploitable — this includes build tools that transform third-party or user-supplied stylesheets, CMS theme uploaders, "paste your CSS" playground tools, and any Tailwind CSS build that processes CSS from a source you don't fully control. The read isn't a clean file dump: PostCSS attempts to `JSON.parse()` the file contents as a source map, and the resulting `SyntaxError` message leaks roughly the first 10 bytes of the target file's content. Combined across many requests, an attacker can also use the technique as a precise file-existence oracle, and target large files to induce a denial-of-service by forcing repeated reads.

Fixed in **PostCSS 8.5.12**, published alongside the GHSA-6g55-p6wh-862q advisory on **2026-07-20**. Tailwind CSS itself doesn't ship a first-party CVE here — it's exposed purely through its PostCSS dependency — but because Tailwind's build pipeline is PostCSS-based by design, any project on Tailwind ≤ the version pinning PostCSS ≤ 8.5.11 inherits the vulnerability.

## Am I affected?

```bash
# Check your resolved PostCSS version
npm ls postcss 2>/dev/null | grep postcss

# Or check package-lock.json / pnpm-lock.yaml directly
grep -A2 '"postcss":' package-lock.json | grep '"version"'
```

You're affected if:
- Your resolved `postcss` version is **≤ 8.5.11**, and
- Your build pipeline (Tailwind CSS, Vite, or a custom PostCSS setup) processes any CSS you don't fully control — third-party themes, CSS pasted/uploaded by users, CSS pulled from an external URL, or CSS from a dependency you haven't audited.

## If you are affected
1. Upgrade PostCSS to **8.5.12 or later**: `npm install postcss@latest` (or update whatever version range your `package.json` / Tailwind version pins).
2. If you can't upgrade immediately, don't run untrusted CSS through any `postcss.process()` call — strip `sourceMappingURL` comments from third-party/user-supplied CSS before processing, or process it in an isolated environment with no filesystem access to sensitive paths.
3. Audit for exploitation: if you have logs of `JSON.parse` / source-map errors from your CSS build pipeline around requests containing unusual `sourceMappingURL` paths (especially ones referencing `../`, `/etc/`, `~/.ssh`, `.env`, or cloud-credential file locations), treat as a potential prior read attempt.

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
→ Don't feed untrusted/user-supplied content into any build-tool parser (CSS, SVG, YAML, etc.) without first checking whether that parser reads external resources by default — source-map comments are a recurring "resource reference hidden in plain content" pattern.

## Sources
- [GitHub Advisory Database — GHSA-6g55-p6wh-862q: PostCSS Arbitrary file read and information disclosure via attacker-controlled sourceMappingURL in CSS comments](https://github.com/advisories/GHSA-6g55-p6wh-862q) — canonical CVE/GHSA pairing, affected/patched version range, CWE classification.
- [SecureLayer7 Labs — CVE-2026-45623: PostCSS Arbitrary File Read via sourceMappingURL Path Traversal](https://securelayer7.net/lab/cve-2026-45623-postcss-sourcemappingurl-arbitrary-file-read) — independent technical writeup, exploitation mechanics (JSON.parse error leak, file-existence oracle, DoS via large files).
- [Miggo Vulnerability Database — CVE-2026-45623: PostCSS sourceMappingURL LFI](https://www.miggo.io/vulnerability-database/cve/CVE-2026-45623) — independent corroboration of affected/patched versions.
