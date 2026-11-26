---
id: 2026-11-nuget-fake-dotnet-assessment-packages-remove-and-rotate
title: "13 malicious NuGet packages in fake .NET take-home assessments: remove them, reimage the machine and rotate developer credentials"
kind: malicious-artifact
date_disclosed: 2026-11-23
last_updated: 2026-11-26
severity: high
status: contained
ecosystems: [nuget, npm, dotnet]
tools_affected: [".NET developers who built a take-home assessment project", "projects referencing the 13 NuGet package ids below", "projects that installed the six related npm packages in July 2026"]
tags: [supply-chain, malicious-package, nuget, npm, fake-job-assessment, social-engineering, contained]
---

## TL;DR

[Socket](https://socket.dev/blog/malicious-nuget-packages-fake-job-assessments) lists 13 malicious NuGet package ids delivered through fake .NET job assessments, and six related npm packages from July 2026. Remove them. If you built a project that used one, reimage the machine and rotate browser-saved passwords and sessions, GitHub tokens, registry tokens and cloud credentials from a clean device.

## Packages and versions

Versions, publishers and removal dates are Socket's. Registry state was read on 2026-11-26: `api.nuget.org/v3-flatcontainer/<id>/index.json` returned 404 for all 13 ids.

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| NuGet | `VS_Builder.MSBuildAnalyzer` | 1.0.1, 1.0.2, 1.0.8, 1.1.2, 1.1.3, and a 1.2.7 copy in the assessment repository | remove; no clean release | 404 (2026-11-26); Socket says deleted 2026-11-02 | Socket |
| NuGet | `VS_Builder.WinUI3Controls` | 1.0.6, 1.0.7 | remove; no clean release | 404 (2026-11-26) | Socket |
| NuGet | `HappyOne.MSBuildAnalyzer` | 1.2.8, 1.2.9, 1.3.0 | remove; no clean release | 404 (2026-11-26); Socket says deleted 2026-11-06 | Socket |
| NuGet | `HappyOne.WinUI3Controls` | 1.0.9, 1.1.0 | remove; no clean release | 404 (2026-11-26); Socket says deleted 2026-11-06 | Socket |
| NuGet | `WinUI.Button` | 1.0.0 | remove; no clean release | 404 (2026-11-26); Socket says still listed on 2026-11-23 | Socket |
| NuGet | `WinUI3IconButton` | 1.1.4 and later | remove; no clean release | 404 (2026-11-26) | Socket |
| NuGet | `RevertButtonIcon` | 1.0.1 and others | remove; no clean release | 404 (2026-11-26) | Socket |
| NuGet | `StyledComponent` | 1.0.0 | remove; no clean release | 404 (2026-11-26) | Socket |
| NuGet | `Web3TotalButton`, `WindowsAccentColorName`, `SetButtonColor`, `InitializeCustomButton`, `StyledAppButton` | not stated | remove; no clean release | 404 (2026-11-26) | Socket |
| npm | `axios-test-one` | 1.18.1 through 1.19.7 | remove; unpublished | unpublished 2026-07-16 (2026-11-26) | MAL-2026-10727 |
| npm | `telemetry-metrics` | 0.2.1 through 0.2.5 | remove; unpublished | unpublished 2026-07-16 (2026-11-26) | MAL-2026-10750 |
| npm | `telemetry-axios` | all; last version 0.1.6 | remove | security placeholder since 2026-07-17 (2026-11-26) | MAL-2026-10773 |
| npm | `axios-native` | all; last version 1.16.4 | remove | security placeholder since 2026-07-17 (2026-11-26) | MAL-2026-10772 |
| npm | `fs-extra-core` | all; last version 1.3.4 | remove | security placeholder since 2026-07-23 (2026-11-26) | MAL-2026-11027 |
| npm | `vitest-axios` | all; last version 1.0.4 | remove | security placeholder since 2026-07-23 (2026-11-26) | MAL-2026-11030 |

Socket counts 28 versions across the 13 NuGet ids. It reports about 160 downloads for `WinUI.Button` and says the figure includes mirrors and scanners. NuGet publisher accounts named by Socket: `VS_Builder`, `HappyOne`, `Carol-White-Super` and `Steven-White-Super`. npm publisher accounts: `gsanbus`, `jasonsayman` and `jasonsuperstar`.

## Am I affected?

- Search `.csproj` files, `Directory.Packages.props`, lock files and `obj/project.assets.json` for the 13 ids. Check the local NuGet package cache too.
- Look for a project folder named `WinUI3_Home_Assessment`.
- Look for `build/VS_Builder.MsBuildAnalyzer.targets` or `build/HappyOne.MsBuildAnalyzer.targets` in packages or caches.
- On Windows, look for `%LOCALAPPDATA%\osk\` holding `OskSupport.dll` and `osk.exe`, and for `%TEMP%\Launcher.exe`.
- Search lockfiles for the six npm names.
- You are at risk if you built an assessment project a recruiter sent you between July and November 2026.

## If you are affected

1. Isolate the machine and reimage it. Socket recommends this if you built or ran an affected project.
2. From a clean device, rotate browser-saved passwords and end browser sessions.
3. Rotate GitHub tokens, NuGet and npm registry tokens, and cloud provider credentials. See [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md), [if your npm token leaked](../playbooks/if-your-npm-token-leaked.md) and [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
4. Remove the packages from project files, lock files and local caches.
5. For the npm packages, follow [if you installed a bad npm package](../playbooks/if-you-installed-a-bad-npm-package.md).

## Prevention

- Build take-home assessments in a disposable virtual machine with no access to your credentials.
- Before building, check a project for extra package feeds, committed package files and unfamiliar package references.
- Restrict which feeds a project can restore from with NuGet package source mapping.
- See the [package vetting checklist](../prevention/package-vetting-checklist.md) and [credential hygiene](../prevention/credential-hygiene.md).

## Sources

- [Socket: 13 Malicious NuGet Packages Target .NET Developers With Fake Job Assessments](https://socket.dev/blog/malicious-nuget-packages-fake-job-assessments), Kush Pandya, 2026-11-23, read 2026-11-26. Package ids, versions, publishers, removal dates, file names and remediation.
- [The Hacker News, 2026-11-26](https://thehackernews.com/2026/11/13-malicious-nuget-packages-turn-fake.html): coverage of Socket's post. It adds no second researcher.
- Registry side, read 2026-11-26: the NuGet flat-container index returned 404 for all 13 ids. `registry.npmjs.org` showed the six npm packages unpublished or replaced by a security placeholder. `api.osv.dev` returned one `MAL-` record for each npm name.
