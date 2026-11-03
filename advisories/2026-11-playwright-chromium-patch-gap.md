---
id: 2026-11-playwright-chromium-patch-gap
title: "Playwright 1.64.1 bundles Chromium from before the late October Chrome security fixes"
date_disclosed: 2026-11-02
last_updated: 2026-11-03
severity: high
status: mitigated
ecosystems: [npm, pypi, mcp]
tools_affected: ["Playwright Chromium launches, especially agents and scrapers visiting external pages"]
tags: [playwright, chromium, browser-automation, sandbox]
---

## TL;DR

Check which browser your automation actually launches. Playwright 1.64.1 ships a browser revision from before two Chrome security updates, and the Playwright library leaves Chromium sandboxing off unless the caller enables it. Prioritize agents, scrapers, link checkers and screenshot services that render other people's content.

## What happened

The [Playwright 1.64.1 browser manifest](https://github.com/microsoft/playwright/blob/v1.64.1/packages/playwright-core/browsers.json) maps both Chromium and its headless shell to revision 1248, version 156.0.8078.4. Updating desktop Chrome does not replace these downloads.

- [Chrome's October 27 desktop release](https://chromereleases.googleblog.com/2026/10/stable-channel-update-for-desktop_0562499947.html) fixed critical bugs in FileSystem (CVE-2026-118306), FileAPI (CVE-2026-118331), Skia (CVE-2026-118348) and Layout (CVE-2026-118344) in 156.0.8078.73/.74.
- [Chrome's October 29 desktop release](https://chromereleases.googleblog.com/2026/10/stable-channel-update-for-desktop_02107719452.html) fixed critical MediaStream memory corruption (CVE-2026-76024) in 156.0.8078.79 on Linux and .79/.80 on Windows and macOS. A check that accepts .73 misses this release.

This comparison establishes patch lag. It does not establish that a given page can exploit a particular build, that an attacker used Playwright, or that credentials were accessed. These are Chromium CVEs, not five flaws in the Playwright package.

## Am I affected?

Trace the launch call through to the URL and subresources it renders. A test serving fixed local fixtures with external requests blocked has much less exposure than a scraper following redirects or an agent opening supplied URLs. A lockfile's optional peer dependency alone does not launch a browser.

1. Check the executable or channel, the version reported by the running browser (`browser.version()` in JavaScript), and launch arguments. `channel: 'chromium'` does not select installed Google Chrome. Look for an omitted or false `chromiumSandbox` and explicit `--no-sandbox` flags.
2. Inspect the browser cache, including separate headless shells: `~/Library/Caches/ms-playwright` on macOS, `~/.cache/ms-playwright` on Linux, or `%LOCALAPPDATA%\ms-playwright` on Windows. Check custom `PLAYWRIGHT_BROWSERS_PATH` locations, Puppeteer's separately configured cache and baked container images. A cached copy is inventory; it only exposes a workload when launched.
3. Check the actual MCP server arguments and transport. Separately, [CVE-2025-9611](https://github.com/advisories/GHSA-6fg3-hvw7-2fwq) affects HTTP connections to Playwright MCP before 0.0.40. Switching browser channels does not fix that server bug.

## If you are affected

For external content, provision and update stable Google Chrome, use a fresh profile, and enable the [Chromium sandbox](https://playwright.dev/docs/api/class-browsertype#browser-type-launch-option-chromium-sandbox) explicitly:

```js
const browser = await chromium.launch({ channel: 'chrome', chromiumSandbox: true });
```

Python uses `chromium.launch(channel="chrome", chromium_sandbox=True)`. For an existing [Playwright MCP configuration](https://github.com/microsoft/playwright-mcp/blob/v0.0.84/README.md), pin a reviewed server version (e.g. `@playwright/mcp@0.0.84` as of November 3) and pass `--browser chrome --sandbox --isolated`. Remove conflicting flags. Check that the configured browser launches without `--no-sandbox`; if the runner cannot sandbox Chrome, fix the runner before it visits external pages.

## Prevention

Run untrusted browsing as a separate unprivileged user in a disposable VM or container without mounted credentials or a personal browser profile. For Linux containers, follow [Playwright's non-root and seccomp guidance](https://playwright.dev/docs/docker). Check browser updates independently of driver updates. Retire unused stale downloads after migrating callers; the next install of an unchanged pin can restore the same browser. Electron applications ship their own runtime: check the app vendor's update and [Electron's branch-specific releases](https://releases.electronjs.org/release), which may backport fixes independently of desktop Chrome.

## Sources

The [original warning](https://x.com/nisten/status/2117322879859568756) and [cache-cleanup follow-up](https://x.com/dave_deguzza/status/2117561292936606163) prompted this check. The browser manifest, vendor release notes and upstream documentation linked above are the basis for the version and configuration guidance.
