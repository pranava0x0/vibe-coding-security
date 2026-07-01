---
id: 2026-05-svelte-dom-clobbering-xss
title: "Svelte CVE-2026-42573 — DOM clobbering of internal framework state leads to XSS (May 2026)"
date_disclosed: 2026-05-14
last_updated: 2026-07-01
severity: medium
status: patched
ecosystems: [npm, svelte]
tools_affected: [Svelte <= 5.55.6]
tags: [xss, dom-clobbering, svelte, frontend, unauthenticated]
---

## TL;DR

**CVE-2026-42573** — Svelte `<= 5.55.6` is vulnerable to **DOM clobbering** of its internal framework state: attacker-controlled `id`/`name` attributes on form elements can shadow the properties Svelte relies on internally, letting injected markup be treated as trusted and executed as script. Fixed in **Svelte 5.55.7**.

## What happened

Svelte attaches internal reactivity/framework state directly to DOM elements at runtime rather than keeping it fully isolated in JavaScript objects. According to the GitHub Security Advisory ([GHSA-rcqx-6q8c-2c42](https://github.com/advisories/GHSA-rcqx-6q8c-2c42)), exploitation requires three conditions at once: (1) attribute spreading on a `<form>` element, (2) attribute spreading or a dynamic `name` value on an `<input>`/`<button>` element inside that form, and (3) attacker control over both elements' attributes. When those line up, an attacker can craft `id`/`name` values that **DOM-clobber** the property lookups Svelte's runtime expects, causing Svelte's rendering/reactivity path to treat attacker-supplied data as trusted internal state — resulting in arbitrary JavaScript execution in the victim's browser (session theft, credential capture, actions taken as the logged-in user).

This is a **medium-severity, narrow-precondition** bug rather than a mass-exploited worm — no reports of in-the-wild exploitation as of this sweep — but Svelte is one of the frameworks explicitly in scope for the vibe-coding stack, and DOM clobbering is a recurring class in component frameworks that spread arbitrary attributes onto DOM nodes (a pattern common in vibe-coded component libraries).

The vulnerability was published to the GitHub Advisory Database on **2026-05-14** and to NVD on **2026-06-09**; CVSS assessments vary by scorer — NVD scores it 6.1 (medium), Red Hat's independent assessment scores it 8.1 (high), both under CWE-79 (Cross-site Scripting).

## Am I affected?

```bash
npm ls svelte 2>/dev/null | grep svelte
# Vulnerable if svelte <= 5.55.6
```

You're at risk if your app spreads user-influenced attributes (`{...someProps}`) onto `<form>` elements and onto `<input>`/`<button>` elements nested inside that form — a pattern common in dynamically generated forms, form builders, or any component that lets end users control field names/ids (e.g., CMS-driven forms, no-code form builders built on Svelte/SvelteKit).

## If you are affected

1. **Upgrade immediately**: `npm install svelte@^5.55.7` (or later).
2. Until patched, avoid spreading attacker-influenced attributes directly onto form/input/button elements; explicitly allowlist which attributes you forward.
3. Review any user-submitted `id`/`name` values rendered into forms for injection potential, even after patching, as defense in depth.
4. See [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) if you have evidence of exploitation (unexpected script execution, unexplained session takeovers) predating the patch.

## Prevention

- Keep frontend framework dependencies current — `npm outdated svelte` as part of routine maintenance, not just after a breach headline.
- Never spread unvalidated user-controlled objects directly onto DOM-producing elements; allowlist attribute names.
- Sanitize any HTML you pass through `{@html ...}` with a library like DOMPurify, and strip `id`/`name` attributes from untrusted HTML before rendering — DOM clobbering defenses apply broadly, not just to this one CVE.
- See [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) for routine dependency-freshness habits.

## Sources

- [GitHub Advisory Database — GHSA-rcqx-6q8c-2c42 (CVE-2026-42573)](https://github.com/advisories/GHSA-rcqx-6q8c-2c42) — canonical advisory: affected/patched versions, exploitation preconditions, publish date.
- [NVD — CVE-2026-42573](https://nvd.nist.gov/vuln/detail/CVE-2026-42573) — official CVE record, CVSS score, CWE classification, NVD publish date.
