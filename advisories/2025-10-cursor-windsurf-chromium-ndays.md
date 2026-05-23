---
id: 2025-10-cursor-windsurf-chromium-ndays
title: "Cursor & Windsurf ship stale Chromium — 94+ n-day vulns, 1.8M devs (Oct 2025)"
date_disclosed: 2025-10-21
last_updated: 2026-05-23
severity: high
status: active
ecosystems: [cursor, windsurf, electron]
tools_affected: [cursor, windsurf, any-vscode-fork-on-old-electron]
tags: [n-day, chromium, electron, v8, ai-ide, patch-lag, vendor-disputed]
---

## TL;DR
OX Security ("Forked and Forgotten") showed that **Cursor and Windsurf** — built on **outdated VS Code → outdated Electron → outdated Chromium/V8** — are exposed to **94+ known (n-day) Chromium vulnerabilities already patched upstream**, affecting **~1.8M developers**. They weaponized one of them, **CVE-2025-7656** (a V8 integer-overflow fixed in Chrome on 2025-07-15), against the **latest** versions of both IDEs. The fix is mostly outside your hands — it requires the vendors to keep Chromium current — and the vendor response was poor: **Windsurf didn't respond; Cursor dismissed the PoC** as "self-inflicted DoS, out of scope." Treat your AI IDE's embedded browser as an **outdated, attacker-reachable Chromium** and keep the app on the newest release.

## What happened
AI IDEs like Cursor and Windsurf are forks of VS Code, which is an **Electron** app — and Electron **embeds Chromium and V8**. When a fork lags behind upstream VS Code/Electron (as these do), it inherits **every Chromium/V8 vulnerability patched after its bundled version** — "n-day" bugs that are public, fixed upstream, and trivially weaponizable.

OX Security catalogued **94+** such n-days reachable in current Cursor/Windsurf builds and demonstrated exploitation with **CVE-2025-7656**, a V8 integer overflow that Google fixed in Chrome on **2025-07-15** but which remained live in the IDEs' stale V8. The exposure surface is anywhere the IDE **renders attacker-influenced web content** in its Chromium context — built-in browser/preview panes, webview-based extensions, markdown/HTML previews, and content fetched by the agent. Depending on the bug, impact ranges from renderer crashes (DoS) up to memory-corruption RCE in the IDE's process.

**Vendor response (the actionable part):**
- OX disclosed to both vendors on **2025-10-12**.
- **Windsurf** — no response.
- **Cursor** — dismissed the PoC, characterizing it as **self-inflicted DoS and out of scope**.

Because neither vendor committed to tracking upstream Chromium, this is a **standing, recurring exposure**, not a one-time CVE — every new Chromium security release widens the gap until the IDE rebases. (Related but distinct from the [Cursor open-folder/autorun RCEs](2026-05-cursor-open-folder-autorun.md) and the [OpenVSX recommended-extension hijack](2026-01-vscode-fork-recommended-extension-hijack.md) — same audience, different layer of the stack.)

## Am I affected?
You're exposed if you use **Cursor or Windsurf** (or another VS Code fork lagging on Electron) and ever render untrusted web content in it — previews, webviews, agent-fetched pages.

```bash
# Check the bundled Electron/Chromium of your IDE (Help → About, or:)
cursor --version 2>/dev/null
windsurf --version 2>/dev/null
# In the app: Help → Toggle Developer Tools → console → process.versions.chrome / .electron
```

Compare the reported Chrome version against the current stable Chrome release — a multi-version gap means known n-days are live. There is **no per-bug patch you can apply**; mitigation is keeping the IDE on its newest build and limiting untrusted web content rendered inside it.

### Facts

| Type | Value |
|---|---|
| Researcher | OX Security ("Forked and Forgotten") |
| Affected | Cursor, Windsurf (outdated VS Code/Electron/Chromium/V8) |
| Exposure | **94+** n-day Chromium/V8 vulnerabilities |
| Weaponized PoC | **CVE-2025-7656** (V8 integer overflow; Chrome-fixed 2025-07-15) |
| Population | ~1.8M developers |
| Disclosed to vendors | 2025-10-12 |
| Vendor response | Windsurf: none. Cursor: "self-inflicted DoS, out of scope." |

## If you are affected
→ Keep Cursor/Windsurf on the **latest release** (newer builds rebase Electron and close some n-days silently — cf. "latest carries undisclosed security fixes").
→ Avoid opening untrusted links / previews inside the IDE's embedded browser; open them in a real, up-to-date browser instead.
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — run the IDE/agent with least privilege so a renderer compromise has less to reach.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Prefer IDEs/vendors with a **published Electron/Chromium update cadence**; treat "how current is the bundled Chromium?" as a procurement question for AI dev tools.
→ Don't render attacker-controlled web content in an Electron app you can't keep patched.

## Sources
- [OX Security — Forked and Forgotten: 94 Vulnerabilities in Cursor and Windsurf Put 1.8M Developers at Risk](https://www.ox.security/blog/94-vulnerabilities-in-cursor-and-windsurf-put-1-8m-developers-at-risk/) — canonical research, CVE-2025-7656 PoC, vendor responses.
- [BleepingComputer — Cursor, Windsurf IDEs riddled with 94+ n-day Chromium vulnerabilities](https://www.bleepingcomputer.com/news/security/cursor-windsurf-ides-riddled-with-94-plus-n-day-chromium-vulnerabilities/)
- [Tenable — CVE-2025-7656 (V8 integer overflow)](https://www.tenable.com/cve/CVE-2025-7656)
- [Cursor Community Forum — "Fix your known 94 vulnerabilities"](https://forum.cursor.com/t/fix-your-know-94-vulnerabilities-you-selfish-devs/138479) — user pressure thread.
