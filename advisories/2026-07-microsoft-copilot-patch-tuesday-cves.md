---
id: 2026-07-microsoft-copilot-patch-tuesday-cves
title: "Microsoft July 2026 Patch Tuesday — GitHub Copilot JetBrains plugin CVE-2026-50510 + M365 Copilot mobile CVE-2026-48561 + M365 Copilot cross-tenant EoP CVE-2026-41106 (all patched)"
date_disclosed: 2026-07-14
last_updated: 2026-07-21
severity: high
status: patched
ecosystems: [github-copilot, m365-copilot]
tools_affected: [github-copilot-jetbrains, microsoft-365-copilot-ios, microsoft-365-copilot-android, edge-android, microsoft-365-copilot]
tags: [cve, patch-tuesday, github-copilot, microsoft-365-copilot, prompt-injection, jetbrains, cross-tenant]
---

## TL;DR
Microsoft's **July 2026 Patch Tuesday** (2026-07-14, 622 CVEs total — the largest single Patch Tuesday on record) shipped fixes for three unrelated Copilot-family flaws: **CVE-2026-50510** (CVSS 7.8) — the **GitHub Copilot plugin for JetBrains IDEs** mishandled resource names (CWE-641) in a way that, with user interaction, allows full local compromise; **CVE-2026-48561** (CVSS 9.6) — **Microsoft 365 Copilot for iOS/Android**, reachable via **Microsoft Edge for Android**, would silently accept and act on prompts injected by a malicious website with no confirmation and no origin check; and **CVE-2026-41106** (CVSS 9.3, critical) — an **elevation-of-privilege flaw in Microsoft 365 Copilot itself** where a URL-redirection-to-untrusted-site weakness (CWE-601) could let an attacker cross tenant-isolation boundaries. All three were addressed by the same Patch Tuesday date, and Microsoft says none were exploited in the wild. No action needed beyond updating (CVE-2026-41106 was fixed server-side with zero customer action required) — but all three are useful reminders that "Copilot" now spans multiple, independently-vulnerable surfaces (IDE plugin, mobile app, browser integration, core cloud service) that each need their own security tracking.

## What happened

### CVE-2026-50510 — GitHub Copilot JetBrains plugin
An improper restriction of names for files/resources (CWE-641) in the **GitHub Copilot plugin for JetBrains IDEs** (IntelliJ IDEA, PyCharm, WebStorm, Rider, Android Studio, and others) allows an attacker who can get a developer to interact with malicious content — a repository, a pull request, or a package — to achieve full compromise of confidentiality, integrity, and availability on the local machine. It requires local access and user interaction (not remotely exploitable on its own), consistent with content-based attack chains this repo has tracked elsewhere (a poisoned repo/PR is the delivery vector, same shape as [GuardFall](2026-06-guardfall-shell-injection-agents.md) and [IDEsaster](2026-06-idessaster-ai-ide-cve-cluster.md)). **All plugin versions before 1.13.0-251 are affected; fixed in 1.13.0-251.**

### CVE-2026-48561 — Microsoft 365 Copilot mobile, via Edge for Android
Independent researcher **Ofek Levin of Enclave** found that Microsoft 365 Copilot's mobile apps (iOS and Android) would accept prompts delivered through **Microsoft Edge for Android** without confirming where they came from. A malicious website, visited in Edge on Android, could silently issue crafted prompts to Copilot — reading or modifying the victim's data with no click beyond visiting the page and no visible confirmation dialog. Microsoft rated this **CVSS 9.6 (critical)** and confirmed it was **never exploited in the wild**, with exploitation assessed as unlikely. Fixed the same day (2026-07-14); Edge for Android ≥ **150.0.4078.65** (released 2026-07-13) closes the vector, alongside the Copilot app updates.

This is a **different flaw** from this repo's already-tracked **[Microsoft 365 Copilot SearchLeak](2026-06-copilot-searchleak-cve-2026-42824.md)** (CVE-2026-42824, a `q=`-parameter-to-prompt-injection chain exfiltrating email/OneDrive data via a CSP/Bing-SSRF bypass, patched 2026-06-15) — but it's the same recurring class this repo flagged when writing up SearchLeak: **treating a URL, query parameter, or cross-app message as a trusted user prompt rather than untrusted input.** Two distinct CVEs against two distinct M365 Copilot surfaces in five weeks is a pattern worth tracking, not a coincidence.

### CVE-2026-41106 — Microsoft 365 Copilot cross-tenant elevation of privilege (update 2026-07-21)
A **critical (CVSS 9.3)** elevation-of-privilege flaw in the core Microsoft 365 Copilot service itself: a URL-redirection-to-untrusted-site weakness (CWE-601) undermined tenant-isolation trust boundaries. Reporting describes an authenticated attacker with some existing M365 access potentially able to reach Copilot's integrations with SharePoint and Entra ID to access data across organizational (tenant) boundaries — a third, distinct Copilot-family CVE from the same July 14 Patch Tuesday batch that this advisory hadn't originally captured. This is a **cloud-service-side fix**: Microsoft applied the patch on its own infrastructure, so **no customer action is required** and there is no client version to check. Microsoft reports no evidence of in-the-wild exploitation.

## Am I affected?
- **GitHub Copilot JetBrains plugin:** check your plugin version in `Settings → Plugins → GitHub Copilot`. If it's below **1.13.0-251**, update immediately.
- **Microsoft 365 Copilot mobile / Edge for Android:** update both apps from your platform's app store. Confirm Edge for Android is **≥ 150.0.4078.65**.
- **Microsoft 365 Copilot (CVE-2026-41106):** no client-side action possible or needed — the fix is already live service-side. If you operate a multi-tenant M365 environment, this is a good prompt to review Copilot permission scopes, SharePoint external-sharing settings, and Entra ID cross-tenant access policies as defense-in-depth.

None of the three flaws has a known IOC set or confirmed in-the-wild exploitation — there's no forensic triage step beyond confirming you're on the patched client versions (and, for CVE-2026-41106, nothing to confirm at all).

## If you are affected
Update is the fix for the two client-side CVEs; there is no rotation or containment step required since Microsoft reports no exploitation occurred for any of the three, and CVE-2026-41106 required no customer action in the first place.

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — for the JetBrains plugin flaw, the same discipline that applies to any "don't blindly open unfamiliar repos/PRs in an AI-integrated IDE" guidance applies here.
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — treat any AI assistant reachable from a mobile browser or cross-app message channel as attacker-reachable input, not just chat-box input.

## Why this matters for vibe coders
"GitHub Copilot" and "Microsoft 365 Copilot" are different products with different attack surfaces, and both had CVEs land in the same Patch Tuesday — a useful reminder to patch every Copilot-branded surface you use (IDE plugin, desktop, mobile, browser integration) independently rather than assuming one update covers them all.

## Sources
- [Windows News — A high-risk Copilot flaw can hijack your JetBrains IDE, Microsoft urges immediate patch](https://windowsnews.ai/article/a-high-risk-copilot-flaw-can-hijack-your-jetbrains-ide-microsoft-urges-immediate-patch.438594)
- [Windows News — July Patch Tuesday: Visual Studio Code update to fix security feature bypass and more](https://windowsnews.ai/article/july-patch-tuesday-update-visual-studio-code-now-to-fix-security-feature-bypass-and-more.438185)
- [NotebookCheck — Microsoft Copilot: Websites could secretly issue commands to the AI](https://www.notebookcheck.net/Microsoft-Copilot-Websites-could-secretly-issue-commands-to-the-AI.1343346.0.html)
- [Windows News — Microsoft flags CVE-2026-41106: Copilot privilege escalation could cross tenant boundaries](https://windowsnews.ai/article/microsoft-flags-cve-2026-41106-copilot-privilege-escalation-could-cross-tenant-boundaries.433548)
- [SOCRadar — July 2026 Patch Tuesday: 622 Vulnerabilities, 3 Zero-Days](https://socradar.io/blog/july-2026-patch-tuesday-zero-day/)
