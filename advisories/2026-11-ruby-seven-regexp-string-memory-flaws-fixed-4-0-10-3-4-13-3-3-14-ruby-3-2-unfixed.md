---
id: 2026-11-ruby-seven-regexp-string-memory-flaws-fixed-4-0-10-3-4-13-3-3-14-ruby-3-2-unfixed
title: "Ruby 4.0.10, 3.4.13 and 3.3.14 fix seven memory flaws in Regexp and string case conversion, one now CVE-2026-132825 (Ruby2Shell); Ruby 3.2 unfixed"
date_disclosed: 2026-11-18
last_updated: 2026-11-20
severity: high
status: patched
ecosystems: [ruby, rails, self-hosted, docker]
tools_affected: ["Ruby 4.0.0 through 4.0.9", "Ruby 3.4.0 through 3.4.12", "Ruby 3.3.13 and earlier", "Ruby 3.2 and earlier (end of life, no fix)"]
tags: [ruby, regexp, memory-corruption, heap-overflow, rce, ruby2shell, end-of-life, security-release]
---

## TL;DR
[Ruby's 2026-11-18 announcement](https://www.ruby-lang.org/en/news/2026/11/18/multiple-vulnerabilities-in-regexp-and-string) lists seven memory flaws in the regular expression engine and in string case conversion. The maintainers say proofs of concept show remote code execution "in some scenarios" for five of them. Upgrade to Ruby 4.0.10, 3.4.13 or 3.3.14. Ruby 3.2 and earlier are end of life and get no fix. One flaw is CVE-2026-132825. The other six have no CVE id as of 2026-11-20, so track the GHSA ids.

## What happened

| GHSA | Flaw, in the announcement's words | Proof of concept, per the announcement |
|---|---|---|
| GHSA-34m4-m9fh-gqp5 | Heap buffer overflow in case conversion of strings | code execution in some scenarios |
| GHSA-87fm-7w84-j2px | Integer overflow in case conversion of strings | code execution in some scenarios |
| GHSA-7x2q-68qv-6p8x | Double free in regular expression compilation | code execution in some scenarios |
| GHSA-3p8q-wmhx-vm2w | Heap buffer overflow in regular expression compilation | code execution in some scenarios |
| GHSA-7whj-cfh7-xgm4 | Heap buffer overflow in Regexp#to_s | code execution in some scenarios |
| GHSA-wpqw-5qxg-m68r | Out-of-bounds read in case-insensitive regular expression matching | memory corruption in an attacker-controlled way |
| GHSA-pvgc-g7gj-pv6h | Out-of-bounds read in case-insensitive backreference matching | none stated. "may disclose memory contents or crash the process" |

The announcement says CVE identifiers "have been requested for these vulnerabilities but have not been assigned yet".

Reachability, as the announcement and [The Hacker News](https://thehackernews.com/2026/11/ruby-releases-fixes-for-7-regex-and.html) describe it:

- The four compilation and matching flaws need an application that compiles or runs a pattern an attacker controls.
- The two case-conversion flaws need an application that changes the case of a crafted string. The Hacker News says GHSA-87fm-7w84-j2px needs a result larger than 4 GiB.
- GHSA-pvgc-g7gj-pv6h fires on a crafted subject string matched against a fixed pattern with a case-insensitive backreference.

The Hacker News reports that the advisories rate three flaws critical, three high and one moderate. Those advisory pages were not opened, so this file rates the batch `high`. It reports no attacks.

The announcement page prints "Posted by mame on 18 Nov 2026" and "Originally published at 2026-11-19 00:00:00 (UTC)".

## Am I affected?

- Run `ruby -v` on application servers, background workers and in container images.
- Affected: 4.0.0 through 4.0.9, 3.4.0 through 3.4.12, 3.3.13 and earlier. The Hacker News gives these ranges.
- Ruby 3.2 and earlier are affected and will not be fixed.
- Search the code for regular expressions built from request data, and for case conversion over imported text.

## If you are affected

1. Upgrade the interpreter to 4.0.10, 3.4.13 or 3.3.14, then restart or rebuild. Updating gems does not replace the interpreter.
2. On Ruby 3.2 or earlier, move to a supported line.
3. Until then, stop building regular expressions from untrusted input.

## Prevention

- Pin the Ruby version in images and rebuild on security releases. The project's previous Regexp fixes shipped on 2026-10-23.
- Scanners keyed on CVE ids will not flag these until ids are assigned. Inventory by interpreter version.

## Update 2026-11-20: one flaw is now CVE-2026-132825 (Ruby2Shell), scored 7.4; six still have no CVE

[CVE-2026-132825](https://cveawg.mitre.org/api/cve/CVE-2026-132825) was published on 2026-11-19 by MITRE for GHSA-34m4-m9fh-gqp5, the one-byte heap overflow in string case conversion. The record scores it 7.4 with a local attack vector, `CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H`. It names ISO-8859-1 and Windows-1252 as example encodings.

[SecurityWeek](https://www.securityweek.com/ruby-patches-ruby2shell-vulnerability-that-could-lead-to-rce/) reports on 2026-11-20:

- The flaw is called Ruby2Shell. Veria Labs says unauthenticated attackers could trigger it from Rails and classic-style Sinatra in default Ruby configurations.
- WatchTowr says any Ruby application that changes the case of external text in a single-byte encoding is affected. Its analyst told SecurityWeek that code execution in production is likely to be hard, and that denial of service is the likely result.
- Chatwoot, GitLab, Mastodon, OpenProject and the Discourse base image have patched. Veria Labs says GitHub Enterprise Server is affected.
- CVE ids for the other flaws were requested and not assigned.

Ruby's announcement, re-read on 2026-11-20, still says no CVE ids are assigned. It credits Stephan Lipp of Ada Logics and Anthropic for four of the seven flaws. [AWS bulletin 2026-193](https://aws.amazon.com/security/security-bulletins/2026-193-aws/) says applications built on Rack, including Rails and Sinatra, "might be reachable through default request handling". Elastic Beanstalk Ruby platform version 4.15.4, released 2026-11-19, carries the fixed interpreters.

The severity stays `high`. The record's vector is local while two research firms describe a remote path, and no source reports an attack.

## Sources

- [Ruby: Multiple vulnerabilities in Regexp and String case conversion](https://www.ruby-lang.org/en/news/2026/11/18/multiple-vulnerabilities-in-regexp-and-string), read 2026-11-19: the seven GHSA ids, the quoted wording, fixed versions, the end-of-life statement.
- [The Hacker News: Ruby Releases Fixes for 7 Regex and String Flaws](https://thehackernews.com/2026/11/ruby-releases-fixes-for-7-regex-and.html), 2026-11-19: ranges, per-advisory ratings, reachability.
- Single primary: the vendor. Not opened: the seven GitHub advisory pages and the release notes.
- [CVE-2026-132825, CVE Services record (MITRE)](https://cveawg.mitre.org/api/cve/CVE-2026-132825): published 2026-11-19, read 2026-11-20. Score, vector, range, the GHSA reference.
- [SecurityWeek: Ruby Patches Ruby2Shell Vulnerability That Could Lead to RCE](https://www.securityweek.com/ruby-patches-ruby2shell-vulnerability-that-could-lead-to-rce/), 2026-11-20: the name, Veria Labs, WatchTowr and Previdian statements, patched downstream projects. The three firms' pages were not opened.
- [AWS security bulletin 2026-193](https://aws.amazon.com/security/security-bulletins/2026-193-aws/), updated 2026-11-19: Rack reachability, Elastic Beanstalk platform version.
