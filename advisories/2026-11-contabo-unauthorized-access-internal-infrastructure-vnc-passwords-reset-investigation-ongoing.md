---
id: 2026-11-contabo-unauthorized-access-internal-infrastructure-vnc-passwords-reset-investigation-ongoing
title: "Contabo: unauthorized access to internal infrastructure on 2026-11-13 and 11-14, all VNC passwords reset; investigation ongoing"
date_disclosed: 2026-11-16
last_updated: 2026-11-17
severity: medium
status: active
ecosystems: [hosting, vps, cloud, self-hosted]
tools_affected: ["Contabo virtual and dedicated servers", "self-hosted agents, gateways and apps that run on Contabo servers"]
tags: [vendor-incident, hosting-provider, vps, vnc, unauthorized-access, investigation-ongoing, single-source-vendor]
---

## TL;DR
[Contabo](https://help.contabo.com/en/support/solutions/articles/103000426255-potential-security-incident-of-14-november) says a third party had access to part of its internal infrastructure from 2026-11-13 15:29 CET to 2026-11-14 11:28 CET. Contabo reset all VNC passwords and rotated internal credentials. It says there are "no indications that personal data was leaked" and the investigation continues. If you run servers there, set a new VNC password, review logins for that window and rotate secrets stored on the servers if you find access you cannot explain.

## What happened

Contabo published the notice on 2026-11-16 at 21:00 CET and updated it on 2026-11-17 at 13:45 CET. The page status is "Investigation ongoing", with updates promised daily by 14:00 CET.

- Contabo detected the access on Saturday 2026-11-14.
- The update gives the window as 2026-11-13 15:29 CET to 2026-11-14 11:28 CET. It says "A part of our internal infrastructure was accessible to an unauthorized third-party during that time."
- Contabo says the access was stopped. It lists three steps: "Reset all VNC passwords and blocked the known access paths", rotated internal access credentials, and added monitoring and forensics. An outside forensics firm is working on the investigation.
- Both versions of the notice say Contabo has no indication that personal data was leaked.

The notice does not name the internal systems, say how the access happened, or say whether customer servers or their consoles were reached. No source says why the VNC passwords were reset. The notice is the only source, and it is the vendor's own.

Contabo hosts virtual and dedicated servers. A rented server of this kind often runs a self-hosted agent, a model gateway or a generated app. VNC is a console path to a server that does not pass through its SSH configuration.

## Am I affected?

You are in scope if you had a Contabo server between 2026-11-13 15:29 CET and 2026-11-14 11:28 CET. On each server:

```bash
last -F | head -50                       # logins, compare with the window
sudo lastb -F 2>/dev/null | head -50     # failed logins
sudo journalctl --since "2026-11-13 14:00" --until "2026-11-14 12:00" -u ssh -u sshd --no-pager | tail -100
sudo find /etc /root /home -newermt "2026-11-13 14:00" ! -newermt "2026-11-14 12:00" -type f 2>/dev/null | head -100
```

The times above are in the server's own time zone. CET is UTC+1.

## If you are affected

- Set a new VNC password for each server, or disable VNC if you do not use it.
- Follow Contabo's list: review credentials and access permissions, change default passwords, enable multi-factor authentication on the customer account, and treat unexpected messages about the incident as phishing.
- If the logs show a console or root session you cannot explain, treat the server as compromised. Rotate every secret on it, including AI provider keys, database passwords and deploy tokens, and rebuild it from a clean image.
- Read the notice again each day until Contabo closes it.
- See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) and [if your web app was compromised](../playbooks/if-your-webapp-was-compromised.md).

## Prevention

- Disable provider console access you do not use, and set a root password that differs from the one the provider issued.
- Keep provider keys and other long-lived secrets out of files on a rented server where a secrets manager is available. See [credential hygiene](../prevention/credential-hygiene.md).
- Encrypt disks that hold secrets when the provider supports it.

## Sources

- [Contabo: Potential security incident of 14 November 2026](https://help.contabo.com/en/support/solutions/articles/103000426255-potential-security-incident-of-14-november): the vendor notice, first published 2026-11-16 21:00 CET, update of 2026-11-17 13:45 CET read on 2026-11-17. Single source: the vendor.
- [Hacker News item 50528682](https://news.ycombinator.com/item?id=50528682): the submission that surfaced the notice, 2026-11-17.
