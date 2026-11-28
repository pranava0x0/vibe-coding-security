---
id: 2026-11-vast-ai-cloud-sync-renter-to-host-root-write-patched-2026-11-04-eighth-rank
title: "Vast.ai: a renter could write files as root on the host machine through Cloud Sync, per Eighth Rank; patched 2026-11-04"
date_disclosed: 2026-11-19
last_updated: 2026-11-28
severity: high
status: unconfirmed
ecosystems: [gpu-cloud, ai-infrastructure, docker]
tools_affected: ["Vast.ai host machines running the vendor's host daemon before the 2026-11-04 patch", "workloads on a Vast.ai host shared with other renters before that date"]
tags: [gpu-marketplace, tenant-isolation, container-escape, researcher-report, no-cve, single-source]
---

## TL;DR

[Eighth Rank reports](https://8rank.ai/game/vast-cloud-sync-host-write) that a Vast.ai customer renting a GPU could write files as root on the host machine through the Cloud Sync feature, and so run code as root there. The researchers say Vast.ai patched it on 2026-11-04. Their page is the only source. No CVE id and no Vast.ai statement were found. Hosts should confirm their daemon is current.

## What happened

Vast.ai is a marketplace where independent hosts rent out GPUs. A renter gets a Docker container on the host's machine. The vendor's daemon on that machine runs with root privileges.

Dario Pasquini and Michał Bazyli published their write-up dated 2026-11-19. It says the Cloud Sync copy from cloud storage to an instance ran on the host, outside the renter's container. The destination path was checked as a string and symbolic links inside the container were followed. The write-up rates the finding 9.9 with the vector `AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`. That score is the researchers' own.

The write-up describes a second finding. The daemon version they tested, 303, retried a failed TLS connection to Vast.ai in cleartext. They say an attacker on the network path between a host and Vast.ai could run commands on that host. They ran this in an isolated lab and did not run the last step to root.

| Date | Event, per the write-up |
|---|---|
| 2026-08-31 | findings made |
| 2026-09-01 | verified and reported to Vast.ai |
| 2026-11-04 | "officially patched" |
| 2026-11-19 | write-up dated |

The write-up names no fixed daemon version. It does not say whether the flaw was used by anyone else. It says Vast.ai managed 20,000 GPUs when it was written.

## Am I affected?

- **You host on Vast.ai.** Your machine was exposed to any renter until the patch. The write-up does not say how hosts receive daemon updates or how to read the installed version.
- **You rented on Vast.ai before 2026-11-04.** Another renter on the same host could have reached the host as root, and from there your container. No source says this happened.

## If you are affected

These steps are a cautious reading. No vendor guidance was found.

- Hosts: confirm with Vast.ai that the daemon on each machine includes the 2026-11-04 patch. Review root's crontab and the daemon's directory for files you did not expect.
- Renters: treat API keys, model weights and datasets placed on a shared host before 2026-11-04 as readable by the host. Rotate keys that were stored in an instance. See [credential hygiene](../prevention/credential-hygiene.md).

## Prevention

- On a GPU marketplace the host operator and other tenants are outside your trust boundary. Pass short-lived, narrowly scoped credentials to rented instances and remove them when the job ends.
- See [agent sandboxing](../prevention/agent-sandboxing.md).

## Sources

- [Eighth Rank, "Remote code execution on Vast.ai host via cloud-sync symlink abuse"](https://8rank.ai/game/vast-cloud-sync-host-write), dated 2026-11-19, read 2026-11-28. Single source: the researchers. Every fact above.
- [Hacker News item 50676292](https://news.ycombinator.com/item?id=50676292), 3 points on 2026-11-28. Where the sweep found the write-up.
- Not opened: any Vast.ai page. No vendor advisory or changelog entry was searched for beyond the feeds read in this run.
