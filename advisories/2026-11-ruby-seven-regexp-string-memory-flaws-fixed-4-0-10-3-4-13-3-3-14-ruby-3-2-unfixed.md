---
id: 2026-11-ruby-seven-regexp-string-memory-flaws-fixed-4-0-10-3-4-13-3-3-14-ruby-3-2-unfixed
title: "Ruby 4.0.10, 3.4.13 and 3.3.14 fix seven memory flaws in Regexp and string case conversion; no CVE ids yet; Ruby 3.2 unfixed"
date_disclosed: 2026-11-18
last_updated: 2026-11-19
severity: high
status: patched
ecosystems: [ruby, rails, self-hosted, docker]
tools_affected: ["Ruby 4.0.0 through 4.0.9", "Ruby 3.4.0 through 3.4.12", "Ruby 3.3.13 and earlier", "Ruby 3.2 and earlier (end of life, no fix)"]
tags: [ruby, regexp, memory-corruption, heap-overflow, rce, no-cve, end-of-life, security-release]
---

## TL;DR
[Ruby's 2026-11-18 announcement](https://www.ruby-lang.org/en/news/2026/11/18/multiple-vulnerabilities-in-regexp-and-string) lists seven memory flaws in the regular expression engine and in string case conversion. The maintainers say proofs of concept show remote code execution "in some scenarios" for five of them. Upgrade to Ruby 4.0.10, 3.4.13 or 3.3.14. Ruby 3.2 and earlier are end of life and get no fix. No CVE ids exist yet, so track the GHSA ids.

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

## Sources

- [Ruby: Multiple vulnerabilities in Regexp and String case conversion](https://www.ruby-lang.org/en/news/2026/11/18/multiple-vulnerabilities-in-regexp-and-string), read 2026-11-19: the seven GHSA ids, the quoted wording, fixed versions, the end-of-life statement.
- [The Hacker News: Ruby Releases Fixes for 7 Regex and String Flaws](https://thehackernews.com/2026/11/ruby-releases-fixes-for-7-regex-and.html), 2026-11-19: ranges, per-advisory ratings, reachability.
- Single primary: the vendor. Not opened: the seven GitHub advisory pages and the release notes.
