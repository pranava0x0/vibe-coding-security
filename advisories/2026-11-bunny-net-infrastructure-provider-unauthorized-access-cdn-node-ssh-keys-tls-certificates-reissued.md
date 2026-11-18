---
id: 2026-11-bunny-net-infrastructure-provider-unauthorized-access-cdn-node-ssh-keys-tls-certificates-reissued
title: "bunny.net: unauthorized SSH keys added to a CDN node through a hosting provider; TLS certificates reissued, replace custom certificates"
date_disclosed: 2026-11-18
last_updated: 2026-11-18
severity: medium
status: contained
ecosystems: [cdn, hosting, tls]
tools_affected: ["bunny.net CDN Pull Zones", "sites that uploaded their own TLS certificate to bunny.net"]
tags: [vendor-incident, cdn, tls-certificates, hosting-provider, third-party, single-source-vendor]
---

## TL;DR
[bunny.net](https://status.bunny.net/incidents/80vrzxmcs7s5) says unauthorized SSH keys were added to one of its CDN nodes through a hosting provider's virtualization layer. It found no evidence the keys were used and cannot rule out that data was copied. The node could hold cached content, Pull Zone configurations and TLS certificates. bunny.net is reissuing the certificates it manages. If you uploaded your own certificate, replace it with a new private key and have the old one revoked.

## What happened

bunny.net posted the notice on 2026-11-18 at 12:25 UTC. It is the second such notice in three weeks.

**2026-11-17, node in Pakistan.** A provider reported "unauthorized access involving third-party server management software". One bunny.net CDN node was on an affected server. bunny.net says the node had been out of traffic rotation for over a week and was removed within 8 minutes of the alert. Its investigation "confirmed that unauthorized SSH keys had been added to the server through the provider's virtualization layer." It adds: "We found no evidence that these keys were used to access the server or perform any further actions. However, we cannot rule out the possibility that data was accessed or copied through the virtualization layer."

**Reported 2026-10-28, node in Armenia.** An [earlier notice](https://status.bunny.net/incidents/p6gf1by9kr7m) used the same description for a different provider's server. That notice said neither bunny.net nor the provider found evidence the node was accessed. bunny.net closed it on 2026-11-09 after reissuing its managed certificates and revoking the old ones with the reason "key compromise". It said the provider's root-cause investigation was still open.

The 2026-11-18 notice says the two incidents involve "separate infrastructure providers". Neither notice names a provider or the server management software. No source ties these notices to any other hosting incident.

For both incidents bunny.net lists the same data as potentially exposed: "temporarily cached CDN content, Pull Zone configurations, and TLS certificates stored on that server." It says account data was not on the servers and internal systems were not affected.

## Am I affected?

You are in scope if you serve a site through a bunny.net Pull Zone.

- **Managed certificates.** bunny.net reissued certificates for its platform domains and says custom-domain managed certificates will be reissued within 24 hours of the notice. No action is needed.
- **Your own uploaded certificate.** bunny.net cannot revoke it for you. Check the certificate's issue date. One issued before 2026-11-17 and uploaded to bunny.net is in scope. One issued before 2026-10-28 and never replaced is in scope for both incidents.

```bash
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -noout -issuer -startdate -serial
```

- **Pull Zone configuration.** Check whether any Pull Zone holds an origin credential, such as a token header or a storage key.

## If you are affected

- Issue a new certificate with a new private key, upload it, and ask the certificate authority to revoke the old one.
- Rotate any origin credential stored in a Pull Zone configuration.
- Treat cached private content as possibly read. Rotate signed-URL keys if you use them.
- Read the status page until bunny.net posts the reissuance update it promised.
- See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Prefer short-lived managed certificates on a CDN over a long-lived certificate you upload.
- Do not cache responses that carry personal data or session tokens.
- Keep origin secrets out of edge configuration where the platform offers a secret store. See [credential hygiene](../prevention/credential-hygiene.md).

## Sources

- [bunny.net status incident 80vrzxmcs7s5](https://status.bunny.net/incidents/80vrzxmcs7s5): vendor notice, 2026-11-18 12:25 UTC, state "monitoring" when read on 2026-11-18. Quoted from the page's JSON copy. Single source: the vendor.
- [bunny.net status incident p6gf1by9kr7m](https://status.bunny.net/incidents/p6gf1by9kr7m): the earlier notice, opened 2026-10-28, closed 2026-11-09, five updates.
- [Hacker News item 50545600](https://news.ycombinator.com/item?id=50545600): the submission that surfaced the notice, 2026-11-18.
