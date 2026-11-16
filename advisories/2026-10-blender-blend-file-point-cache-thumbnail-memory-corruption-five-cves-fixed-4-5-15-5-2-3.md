---
id: 2026-10-blender-blend-file-point-cache-thumbnail-memory-corruption-five-cves-fixed-4-5-15-5-2-3
title: "Blender before 4.5.15 and 5.x before 5.2.3: a crafted .blend, point cache or thumbnail can run code (five CVEs, three with code execution)"
date_disclosed: 2026-10-30
last_updated: 2026-11-16
severity: high
status: patched
ecosystems: [blender, 3d-modeling, desktop-apps, file-parsing]
tools_affected: ["Blender before 4.5.15", "Blender 5.0.0 to 5.2.2", "blender-thumbnailer and the Windows shell extension (thumbnail preview)", "any coding agent or MCP bridge that opens, appends or links a .blend file it did not create"]
tags: [cve, blender, blend-file, memory-corruption, file-parsing, vulncheck, 3d-modeling, agent-opened-file, backfill]
---

## TL;DR
Blender before 4.5.15, and 5.0.0 to 5.2.2, has five memory-safety bugs in the code that reads `.blend` files, point cache files and file thumbnails. Three of them (CVE-2026-119718, CVE-2026-119719, CVE-2026-119722) are scored CVSS 7.8 by VulnCheck and can crash Blender or run code as the user who opens the file. Blender fixed all five in one pull request, released in 4.5.15 and 5.2.3 on 2026-10-22. Upgrade to 4.5.15 or later on the 4.5 line, or to 5.2.3 or later. Do not open `.blend` files from a source you do not trust. Turning off Auto Run Python Scripts does not protect against these bugs.

## What happened

VulnCheck published five CVE records on 2026-10-30, all credited to Tristan Madani and all with the same affected range: every Blender before 4.5.15, and 5.0.0 up to but not including 5.2.3.

| CVE | Where | What a crafted file does | VulnCheck CVSS 3.1 / 4.0 |
|---|---|---|---|
| CVE-2026-119718 | `ptcache_data_alloc()`, point cache files read beside a `.blend` | heap buffer overflow, crash or code execution | 7.8 / 8.5 |
| CVE-2026-119719 | `thumb_data_vertical_flip()` in the thumbnail extractor | out-of-bounds write when `blender-thumbnailer` or the Windows shell extension previews the file | 7.8 / 8.5 |
| CVE-2026-119722 | `read_struct()` | heap out-of-bounds access, crash or code execution | 7.8 / 8.5 |
| CVE-2026-119721 | `blo_bhead_id_*` accessors in `readfile.cc` | heap over-read when the file is browsed or appended from, crash or memory disclosure | 6.1 / 6.9 |
| CVE-2026-119720 | `read_file_dna()` | out-of-bounds read, crash | 5.5 / 6.8 |

Every score is VulnCheck's, read from the CNA records on 2026-11-16. All five vectors are local with user interaction (`AV:L`, `UI:R`): someone, or an agent acting for them, has to open, browse, append from or preview the file.

All five records reference Blender pull request 164279, "Core: Harden blend file and point cache file reading". The Blender project's API shows it opened on 2026-09-24 and merged on 2026-10-13. Its description lists the fixes as crashes with corrupt thumbnails, corrupt blend files, too-short blocks and unexpected struct types. The part of the description read here calls them crash fixes and does not call them security fixes. The 4.5.15 and 5.2.3 builds appeared on `download.blender.org` on 2026-10-22. Builds 4.5.16 and 5.2.4 followed on 2026-11-10.

Red Hat's record for CVE-2026-119722 rates it Important, 7.8, and describes it as arbitrary code execution through a crafted `.blend` file.

**An older record on the same code.** CVE-2026-60103 (VulnCheck, 2026-07-13, credited to Saad ELHARAJ) is an out-of-bounds read in `sdna_expand_names()`, affecting Blender 3.0.0 through 5.1.2, scored 6.1. The record lists a fix commit and no fixed release number.

**Why this matters for agent users.** People now ask coding agents to "import this model" or "render this scene", and MCP bridges such as blender-mcp load assets from third-party libraries. In both cases the agent opens the file. Blender's manual says auto execution of scripts in a `.blend` is off by default and is controlled by the Auto Run Python Scripts preference and `--disable-autoexec`. Those controls cover scripts. These five bugs are in the file reader, which runs before any script setting applies.

## Am I affected?

```bash
blender --version                                              # Linux, or any install on PATH
/Applications/Blender.app/Contents/MacOS/Blender --version     # macOS default location
```

- Affected: any version before 4.5.15, and 5.0.0 through 5.2.2.
- Not affected by these five ids: 4.5.15 and later on the 4.5 line, 5.2.3 and later.
- Distribution packages can lag the upstream release. Check the package version, not only the upstream number.
- Thumbnail previews count. On an affected version, a file manager that calls `blender-thumbnailer`, or the Windows shell extension, reads the file when the folder is viewed (CVE-2026-119719).

## If you are affected

- Upgrade to 5.2.3 or later, or 4.5.15 or later on the LTS line. Verify the download against the checksum Blender publishes beside it.
- If you opened `.blend` files from a marketplace, a forum or an unknown sender on an affected version, treat that machine as you would after running untrusted code. See [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md) and [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
- None of the sources below reports exploitation in the wild.

## Prevention

- Open only `.blend` files you created or that come from a source you trust.
- Keep Auto Run Python Scripts off. It does not stop these bugs, and it does stop the script-based route.
- When an agent or a render script drives Blender, run it in the background with `--factory-startup`, `--disable-autoexec` and `--offline-mode`, on files the project generated. Blender's manual documents all three flags.
- Give an agent that handles downloaded assets a working directory with no credentials in reach. See [agent sandboxing](../prevention/agent-sandboxing.md) and [MCP hygiene](../prevention/mcp-hygiene.md).

## Sources
- [CVE Services: CVE-2026-119718](https://cveawg.mitre.org/api/cve/CVE-2026-119718), fetched 2026-11-16: VulnCheck CNA, published 2026-10-30, the affected ranges, point cache overflow, 7.8 and 8.5, credit Tristan Madani, reference to pull request 164279.
- [CVE Services: CVE-2026-119719](https://cveawg.mitre.org/api/cve/CVE-2026-119719), fetched 2026-11-16: thumbnail extractor overflow, `blender-thumbnailer` and the Windows shell extension, 7.8 and 8.5.
- [CVE Services: CVE-2026-119720](https://cveawg.mitre.org/api/cve/CVE-2026-119720), fetched 2026-11-16: `read_file_dna()` out-of-bounds read, 5.5 and 6.8.
- [CVE Services: CVE-2026-119721](https://cveawg.mitre.org/api/cve/CVE-2026-119721), fetched 2026-11-16: `blo_bhead_id_*` over-read, 6.1 and 6.9.
- [CVE Services: CVE-2026-119722](https://cveawg.mitre.org/api/cve/CVE-2026-119722), fetched 2026-11-16: `read_struct()` out-of-bounds access, 7.8 and 8.5.
- [CVE Services: CVE-2026-60103](https://cveawg.mitre.org/api/cve/CVE-2026-60103), fetched 2026-11-16: VulnCheck CNA, published 2026-07-13, Blender 3.0.0 through 5.1.2, 6.1, a fix commit and no release number.
- [Blender project API: pull request 164279](https://projects.blender.org/api/v1/repos/blender/blender/pulls/164279), fetched 2026-11-16: title "Core: Harden blend file and point cache file reading", created 2026-09-24, merged 2026-10-13, the list of fixes. The HTML page for the same pull request returned 403.
- [Blender download index, 5.2 line](https://download.blender.org/release/Blender5.2/), fetched 2026-11-16: 5.2.3 builds dated 2026-10-22, 5.2.4 builds dated 2026-11-10.
- [Blender download index, 4.5 line](https://download.blender.org/release/Blender4.5/), fetched 2026-11-16: 4.5.15 builds dated 2026-10-22, 4.5.16 builds dated 2026-11-10.
- [Red Hat CVE data: CVE-2026-119722](https://access.redhat.com/hydra/rest/securitydata/cve/CVE-2026-119722.json), fetched 2026-11-16: Important, 7.8, "Arbitrary code execution via crafted .blend file". Red Hat's record repeats the CNA's finding and is not an independent test.
- [Blender manual: Scripting and Security](https://docs.blender.org/manual/en/latest/advanced/scripting/security.html), fetched 2026-11-16: auto execution, the Auto Run Python Scripts preference, Trusted Source.
- [Blender manual: command line arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html), fetched 2026-11-16: `--version`, `--factory-startup`, `--disable-autoexec` (the default), `--offline-mode`.
- Not opened: the VulnCheck advisory pages the records reference, and Blender's release notes for 5.2.3 and 4.5.15 (`blender.org` returned 403).
