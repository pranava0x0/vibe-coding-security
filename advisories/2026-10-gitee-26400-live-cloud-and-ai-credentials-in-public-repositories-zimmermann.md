---
id: 2026-10-gitee-26400-live-cloud-and-ai-credentials-in-public-repositories-zimmermann
title: "26,400 working credentials in 7.25 million public Gitee repositories: 9,473 Alibaba Cloud keys, 3,170 DeepSeek, about 1,350 OpenAI; revocation unconfirmed"
date_disclosed: 2026-10-28
last_updated: 2026-10-29
severity: medium
status: ongoing
ecosystems: [gitee, git-hosting, api-keys, cloud]
tools_affected: ["anyone who has pushed an Alibaba Cloud, DeepSeek, Zhipu BigModel, OpenAI, OpenRouter, LangSmith, Hugging Face or similar key to a public Gitee repository at any point in its history", "the issuing providers, who hold the only reliable revocation path"]
tags: [secret-scanning, leaked-credentials, api-keys, gitee, alibaba-cloud, deepseek, openai, zhipu, research-study, kingfisher, trufflehog, revocation]
---

## TL;DR
Independent researcher Ben Zimmermann, writing on MongoDB's blog on 2026-10-28, scanned the full commit history of 7,256,531 public Gitee repositories over about a month and verified 26,400 unique credentials that still worked at the issuing service: 9,473 Alibaba Cloud AccessKey pairs, 3,805 YouTube API keys, 3,170 DeepSeek keys, 1,489 Zhipu BigModel keys, about 1,350 OpenAI keys, plus LangSmith, OpenRouter, Hugging Face, Stripe, Slack and database credentials. He sent each high-volume vendor its list; developers were not contacted and no revocation was confirmed at publication. A key that was ever in a public repository is live until the issuer revokes it; deleting the file or rewriting history does not.

## What happened

**Method.** Zimmermann ran TruffleHog and Kingfisher (MongoDB's scanner, whose team worked with him on the post) across full commit histories on Modal serverless compute (up to 350 containers, 50 batches of about 150K repositories, $3,097.64 of compute). Each candidate was tested against its issuing service and kept only if it authenticated; results were deduplicated by raw secret value. TruffleHog found 12,737 live credentials and Kingfisher 14,664, with 1,001 found by both, so either tool alone would have caught about half. Coverage was complementary: TruffleHog led on Alibaba Cloud (9,428 to 993), Kingfisher on DeepSeek (2,940 to 230), OpenAI (1,198 to 150), Hugging Face (154 to 1) and Zhipu (1,489 to 0, because TruffleHog has no detector for it).

**Figures.** 26,400 live credentials across 7,256,531 repositories, 3.64 per 1,000 (1.76 per 1,000 on TruffleHog alone). Alibaba Cloud keys appeared in about one repository in 766. By commit year, 2025 alone accounts for 12,242 of the credentials; the chart runs from 2008 to 2025. Committer addresses were mostly personal mail providers; corporate domains with the most hits were huawei.com (32), microsoft.com (22) and bytedance.com (22), which the author calls a floor. For comparison he cites earlier TruffleSecurity scans of GitLab (17,430 live in about 5.6 million repositories, 3.11 per 1,000) and Bitbucket (6,212 in about 2.6 million, 2.39 per 1,000), noting those used one scanner. The Hacker News (2026-10-29, Swati Khandelwal) adds that one credential was an active organization-admin credential for an unnamed major enterprise AI platform.

**Disclosure.** Vendors with the highest exposure received coordinated reports with their full list and source-repository metadata. Individual committers were not notified; the author's position is that vendor-side revocation needs no action from the person who leaked the key. As of publication, revocation status was not confirmed. The post notes that many Chinese providers have no security contact or bounty programme, so some leaked credentials have no clear remediation path. Nothing in either source says any credential was abused.

**Why it matters here.** The counts for DeepSeek, Zhipu, OpenAI, OpenRouter, LangSmith and Hugging Face are AI-provider keys, the credential class this audience creates most often and pastes into agent configs, `.env` files and notebooks. A verified-live rate of 3.64 per 1,000 repositories is a measurement of how often those files reach a public remote. The study is about Gitee, but the two earlier scans it compares against are GitLab and Bitbucket, and the mechanism is the same on GitHub.

## Am I affected?

```bash
git log -p --all | grep -nE 'sk-[A-Za-z0-9]{20,}|LTAI[A-Za-z0-9]{12,}|hf_[A-Za-z0-9]{30,}|sk-or-v1-|lsv2_' | head   # OpenAI, Alibaba Cloud, Hugging Face, OpenRouter, LangSmith shapes in history
pip install -q kingfisher 2>/dev/null || true; trufflehog git file://. --only-verified 2>/dev/null | head           # either scanner; run both if you can
```

- Any match in a repository that was ever public, on any host, is a credential to revoke at the issuer, whether or not the current tree still contains it.
- The providers named received lists; a key you leaked may be revoked by the vendor without notice to you. An unexplained authentication failure on one of these services is a reason to check history, not to mint a replacement and move on.

## If you are affected

1. Revoke at the issuer, then rotate: [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md). For Alibaba Cloud, create a new AccessKey pair, migrate, then disable and delete the old one and review ActionTrail; for OpenAI and OpenRouter, rotate and set spend limits; for Hugging Face and LangSmith, revoke the token in account settings.
2. Check the provider's usage logs for the window since the commit; an AI key is typically abused for inference at your expense.
3. Only after revocation, remove the secret from history if the repository stays public; this prevents re-discovery, not use.

## Prevention

- [Credential hygiene](../prevention/credential-hygiene.md): pre-commit scanning, `.env` in `.gitignore` from the first commit, and one scanner is not enough.
- [Auditing a vibe-coded repo](../playbooks/auditing-a-vibe-coded-repo.md): scan history, not only the working tree.

## Sources
- [MongoDB — Scanning 7.25 Million Public Repositories on China's Largest Git Platform for Secrets](https://www.mongodb.com/company/blog/technical/scanning-7-point-25-million-public-repositories-chinas-largest-git-platform-for-secrets) — fetched 2026-10-29 (2026-10-28, Ben Zimmermann): the repository count, the per-scanner and per-provider counts, the overlap, the compute and cost, the commit-year distribution, the committer domains, the platform comparison, the disclosure actions and the unconfirmed revocation status.
- [The Hacker News — 26,400 Valid Cloud and AI Credentials Found Exposed in Public Gitee Repositories](https://thehackernews.com/2026/10/26400-valid-cloud-and-ai-credentials.html) — fetched 2026-10-29 (Swati Khandelwal): the organization-admin credential, the per-provider rotation steps quoted above, the density comparison caveat.
- Related in this corpus: [AI coding agents and secret leaks on GitHub](ongoing-vibe-platform-exposure.md) for the pattern this measures.
