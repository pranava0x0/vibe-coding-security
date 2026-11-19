---
id: 2026-11-php-november-19-security-release-eight-cves-fpm-request-smuggling-session-code-execution-fixed-8-5-13
title: "PHP 8.5.13, 8.4.28, 8.3.37 and 8.2.36 fix eight CVEs, seven scored 9.2: PHP-FPM request smuggling, session and use-after-free code execution"
date_disclosed: 2026-11-19
last_updated: 2026-11-19
severity: critical
status: patched
ecosystems: [php, self-hosted, web-server, docker]
tools_affected: ["PHP 8.5 before 8.5.13", "PHP 8.4 before 8.4.28", "PHP 8.3 before 8.3.37", "PHP 8.2 before 8.2.36", "PHP-FPM behind nginx, Apache or HAProxy with backend connection reuse"]
tags: [cve, php, php-fpm, request-smuggling, session, use-after-free, unauthenticated, rce, security-release]
---

## TL;DR
[PHP released 8.5.13, 8.4.28, 8.3.37 and 8.2.36](https://www.php.net/archive/2026.php) on 2026-11-19 as security releases. The PHP Group's CNA records cover eight CVEs, seven scored 9.2. [CVE-2026-129289](https://cveawg.mitre.org/api/cve/CVE-2026-129289) lets an unauthenticated request forge a second PHP-FPM request when the front end reuses backend connections, which is not the nginx or Apache default. Upgrade and restart PHP.

## What happened

All eight records were published on 2026-11-19 by the PHP Group. Scores are CVSS 4.0 and are the PHP Group's.

| CVE | Title on the record | Affected lines | Score |
|---|---|---|---|
| [CVE-2026-129289](https://cveawg.mitre.org/api/cve/CVE-2026-129289) | PHP-FPM request smuggling through an unread HTTP request body | 8.2, 8.3, 8.4, 8.5 | 9.2 |
| [CVE-2026-115560](https://cveawg.mitre.org/api/cve/CVE-2026-115560) | Session serializer mismatch can lead to remote code execution | 8.2, 8.3, 8.4, 8.5 | 9.2 |
| [CVE-2026-126714](https://cveawg.mitre.org/api/cve/CVE-2026-126714) | Partially overwritten session files can lead to remote code execution | 8.2, 8.3, 8.4, 8.5 | 9.2 |
| [CVE-2026-129496](https://cveawg.mitre.org/api/cve/CVE-2026-129496) | Timezone cache use-after-free can lead to remote code execution | 8.2, 8.3, 8.4, 8.5 | 9.2 |
| [CVE-2026-129481](https://cveawg.mitre.org/api/cve/CVE-2026-129481) | Use-after-free after interrupted session shutdown | 8.3, 8.4, 8.5 | 9.2 |
| [CVE-2026-129182](https://cveawg.mitre.org/api/cve/CVE-2026-129182) | Use-after-free via repopulation of last_fatal_error_backtrace global after shutdown | 8.5 | 9.2 |
| [CVE-2026-129474](https://cveawg.mitre.org/api/cve/CVE-2026-129474) | Use-after-free in magic method backtraces can lead to remote code execution | 8.5 | 9.2 |
| [CVE-2026-129291](https://cveawg.mitre.org/api/cve/CVE-2026-129291) | PHP-FPM epoll use-after-free can lead to local privilege escalation | 8.2.7 onward, 8.3, 8.4, 8.5 | 8.8 |

The fixed versions on every record are 8.2.36, 8.3.37, 8.4.28 and 8.5.13 for the lines it lists.

Conditions the records and [The Hacker News](https://thehackernews.com/2026/11/php-fixes-7-critical-flaws-including.html) state:

- **CVE-2026-129289.** The application opens `php://input` without reading it to the end, and the front end reuses backend connections. The record gives nginx with `fastcgi_keep_conn on` and Apache mod_proxy_fcgi with `enablereuse=on` as examples.
- **CVE-2026-115560.** Session upload progress is enabled, and the same session is later read with a different serializer. Code execution needs a gadget chain in the reading application.
- **CVE-2026-126714.** The Hacker News says it needs influence over session data, an interrupted write and a gadget chain. It affects applications with file-based sessions. Depthfirst named it phpAfterShell.
- **CVE-2026-129291.** Local. It needs code already running in an FPM worker.

No source read reports an attack. This is the second PHP security release in a month. The October one is in [the PHP2Shell advisory](2026-10-php2shell-cve-2026-109618-109619-unauthenticated-rce-embargo-break-pre-disclosure-exploitation.md).

## Am I affected?

- Run `php -v` on every host and in every container image, including PHP bundled inside other software.
- Any 8.2, 8.3, 8.4 or 8.5 release below the fixed versions is affected by at least four of the ids.
- For the request smuggling bug, search the proxy configuration for `fastcgi_keep_conn on` or `enablereuse=on`.
- The records list no line older than 8.2. No source read says whether older lines are affected.

## If you are affected

1. Upgrade to 8.5.13, 8.4.28, 8.3.37 or 8.2.36 and restart PHP-FPM or the web server.
2. If you cannot upgrade yet, The Hacker News relays one step: turn off session upload progress. CVE-2026-129289 needs backend connection reuse, so leave that off in the proxy.
3. A distribution package can carry the fix under an older version string. Check its changelog for the CVE ids.
4. For a server you think was reached, see [if your web app was compromised](../playbooks/if-your-webapp-was-compromised.md).

## Prevention

- Rebuild PHP base images on every security release. The project pre-announces them on [php.net](https://www.php.net/archive/2026.php).
- Keep one application per session store. Two applications that share a store with different serializers create the condition for CVE-2026-115560.

## Sources

- [php.net news archive, 2026](https://www.php.net/archive/2026.php), read 2026-11-19: the four releases, each dated 19 Nov 2026 and labelled a security release.
- [CVE-2026-129289](https://cveawg.mitre.org/api/cve/CVE-2026-129289), [CVE-2026-115560](https://cveawg.mitre.org/api/cve/CVE-2026-115560), [CVE-2026-126714](https://cveawg.mitre.org/api/cve/CVE-2026-126714), [CVE-2026-129496](https://cveawg.mitre.org/api/cve/CVE-2026-129496), [CVE-2026-129481](https://cveawg.mitre.org/api/cve/CVE-2026-129481), [CVE-2026-129182](https://cveawg.mitre.org/api/cve/CVE-2026-129182), [CVE-2026-129474](https://cveawg.mitre.org/api/cve/CVE-2026-129474), [CVE-2026-129291](https://cveawg.mitre.org/api/cve/CVE-2026-129291): PHP Group CNA records, read 2026-11-19.
- [The Hacker News: PHP Fixes 7 Critical Flaws](https://thehackernews.com/2026/11/php-fixes-7-critical-flaws-including.html), 2026-11-19: conditions, Depthfirst's name for CVE-2026-126714, the interim step.
- Not opened: the eight php-src advisory pages the records reference, the per-version changelogs, and Depthfirst's post.
