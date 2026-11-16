---
id: 2026-07-freecad-fcstd-document-code-execution-file-write-xxe-nine-advisories-fixed-1-1-4
title: "FreeCAD before 1.1.4: opening a crafted FCStd document can run code or write files (nine advisories, six CVEs)"
date_disclosed: 2026-07-23
last_updated: 2026-11-16
severity: high
status: patched
ecosystems: [freecad, 3d-modeling, cad, desktop-apps, file-parsing]
tools_affected: ["FreeCAD 0.19 to 1.1.0 (two eval() advisories)", "FreeCAD 1.1.1 and earlier (four advisories)", "FreeCAD 1.1.3 and earlier (two file-write advisories, no CVE)", "any coding agent or MCP bridge that opens an .FCStd file it did not create"]
tags: [cve, freecad, fcstd, cad, code-execution, path-traversal, xxe, file-parsing, 3d-modeling, agent-opened-file, backfill]
---

## TL;DR
FreeCAD's repository lists nine security advisories published between 2026-07-23 and 2026-09-29. Eight involve a crafted `.FCStd` document. Three run code, three write files outside the document and one reads local files through XML entities. The eighth runs Python from a FEM formula when the user accepts a constraint dialog in the document. Upgrade to FreeCAD 1.1.4 or later, which is the first release that fixes all eight. Do not open `.FCStd` files from a source you do not trust. The ninth, a DLL search-path issue in `FreeCAD.exe`, lists 26.3.0 as its fix, and only release candidates of 26.3 were published when read.

## What happened

All rows are from the advisory tab of `FreeCAD/FreeCAD`, read through the GitHub API on 2026-11-16. Severity is the vendor's label.

| Advisory | CVE | Vendor severity | What it is | Affected | Fixed |
|---|---|---|---|---|---|
| GHSA-8rfj-7956-6gwf | CVE-2026-34398 | high | `eval()` on `.FCStd` metadata in BIM Project Manager | 0.19 to 1.1.0 | 1.1.1 |
| GHSA-chv4-vm6r-wjqj | CVE-2026-34399 | high | `eval()` on an SVG template scale field in BIM TechDraw Page | 0.19 to 1.1.0 | 1.1.1 |
| GHSA-493w-pp4h-h77v | CVE-2026-34789 | high | module import in `PropertyPythonObject::Restore` | 1.1.1 and earlier | 1.1.2 |
| GHSA-5vqh-3v38-jw2r | CVE-2026-73234 | high | path traversal file write in `PropertyFileIncluded::Restore()` | 1.1.1 and earlier | 1.1.2 |
| GHSA-2rq3-gx3h-489q | CVE-2026-73233 | medium | FEM formula incomplete escape, runs when the user accepts the constraint dialog | 1.1.1 and earlier | 1.1.2 |
| GHSA-cp6c-87x9-xf49 | CVE-2026-73235 | medium | XML external entity file read and SSRF in the `Document.xml` parser | 1.1.1 and earlier | 1.1.2 |
| GHSA-9624-pf2m-8cgg | none | high | VRML resources in an FCStd write files on open | 1.1.3 and earlier | 1.1.4 |
| GHSA-9vjf-h8f4-c229 | none | high | Zip-Slip file write in `PropertyPostDataObject::RestoreDocFile()` | 1.1.3 and earlier | 1.1.4 |
| GHSA-2mfq-2h69-c873 | none | high | DLL search path in `FreeCAD.exe` | before 26.3.0 | 26.3.0 |

**Scores.** The CVE records for the three ids fetched for this file are from GitHub's CNA, published 2026-08-11. CVE-2026-73234 is 7.8 (CVSS 3.1) and CVE-2026-73235 is 6.1 (CVSS 3.1), the same as the vendor pages. CVE-2026-73233 is 8.5 High (CVSS 4.0) in the CNA record, while the vendor page says medium and gives no score. The records for CVE-2026-34398 (7.8), CVE-2026-34399 (7.8) and CVE-2026-34789 (7.0) match the vendor's ranges and fixed versions. Not checked: the exact trigger for each of the other seven.

**Releases.** 1.1.1 is dated 2026-04-14, 1.1.2 2026-07-23, 1.1.3 2026-07-25 and 1.1.4 2026-09-28. The two no-CVE advisories were published on 2026-09-29, so a scanner keyed on CVE ids reports 1.1.2 and 1.1.3 as clean. For 26.3 the releases list held `26.3rc1` (2026-10-08) and `26.3rc2` (2026-10-18) and no stable tag.

**Why this matters for agent users.** An `.FCStd` file is a zip archive with XML and embedded resources. An agent or an MCP bridge asked to open, convert or inspect one runs the same restore code.

## Am I affected?

- Open FreeCAD and read the version in Help, About FreeCAD, or check the version of the package your system installed. Anything before 1.1.4 is affected by at least two advisories.
- Versions 1.1.2 and 1.1.3 fix the six CVEs and are still affected by the two no-CVE file-write advisories.
- You are exposed when FreeCAD opens an `.FCStd` file from someone else.

## If you are affected

- Upgrade to 1.1.4 or later.
- If an affected version opened documents from an untrusted source, treat the machine as you would after running untrusted code. See [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).
- None of the sources below reports exploitation in the wild. CISA's entries on CVE-2026-73233 and CVE-2026-73234 mark a proof of concept as existing.

## Prevention

- Open only CAD documents you created or that come from a source you trust.
- Run agent-driven CAD conversion in a directory and account with no credentials. See [agent sandboxing](../prevention/agent-sandboxing.md) and [MCP hygiene](../prevention/mcp-hygiene.md).
- Watch the project's advisory tab. Three of its nine advisories have no CVE.

## Sources
- [FreeCAD security advisories tab](https://github.com/FreeCAD/FreeCAD/security/advisories), read through the GitHub API (`repos/FreeCAD/FreeCAD/security-advisories`) on 2026-11-16: the nine rows above with ids, severities, ranges, patched versions and publication dates.
- [CVE Services: CVE-2026-73233](https://cveawg.mitre.org/api/cve/CVE-2026-73233), fetched 2026-11-16: GitHub CNA, published 2026-08-11, affected before 1.1.2, CVSS 4.0 8.5, CISA entry marks a proof of concept.
- [CVE Services: CVE-2026-73234](https://cveawg.mitre.org/api/cve/CVE-2026-73234), fetched 2026-11-16: affected before 1.1.2, CVSS 3.1 7.8, CISA entry marks a proof of concept.
- [CVE Services: CVE-2026-73235](https://cveawg.mitre.org/api/cve/CVE-2026-73235), fetched 2026-11-16: affected before 1.1.2, CVSS 3.1 6.1.
- FreeCAD releases, read through the GitHub API on 2026-11-16: the release dates above, and no stable 26.3 tag.
- CVE Services records for CVE-2026-34398, CVE-2026-34399 and CVE-2026-34789, fetched 2026-11-16: 7.8, 7.8 and 7.0.
- Not opened: the fix pull requests and commits the records reference.
