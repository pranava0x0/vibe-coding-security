---
id: 2026-11-rackspace-spot-breach-kubernetes-secrets-tokens-service-shutdown-2026-12-08
title: "Rackspace Spot: intruders gained access to Kubernetes Secrets on 2026-11-17; service shuts down 2026-12-08; rotate every secret in affected clusters"
date_disclosed: 2026-11-24
last_updated: 2026-11-26
severity: high
status: active
ecosystems: [kubernetes, rackspace-spot, cloud-hosting, saas]
tools_affected: ["Rackspace Spot Kubernetes clusters", "Spot API tokens and refresh tokens", "kubeconfig files issued by Rackspace Spot", "credentials stored as Kubernetes Secrets in Spot clusters"]
tags: [incident, vendor-incident, hosting-provider, kubernetes-secrets, api-tokens, compromised-credential, observability-system, service-shutdown, active]
---

## TL;DR

[The Register reports](https://www.theregister.com/cyber-crime/2026/11/26/rackspace-pulls-plug-on-spot-cloud-service-after-security-breach/5312352) that intruders used leaked credentials to reach parts of Rackspace Spot on 2026-11-17, created pods in customer Kubernetes clusters and gained access to Kubernetes Secrets. Rackspace is closing the service on 2026-12-08 at 23:00 UTC. If you ran workloads on Spot, rotate every credential stored in those clusters, reissue API tokens and move your data before the deadline.

## What happened

All of the following is The Register's account of a Rackspace notice and of a customer notification it says it saw. Neither document was opened for this file.

- The intruders had access for almost 22 hours on 2026-11-17. Rackspace learned of it the next day, after a customer raised the alarm.
- The intruders impersonated legitimate users, created pods in customer clusters, gained access to Kubernetes Secrets, and listed nodes and storage volumes.
- The notification says: "With that access, they could have read any Secret in an affected user's clusters, and any Spot API token or refresh token that user held."
- Rackspace revoked the affected tokens and sessions, removed the pods the intruders created, and changed the affected platform and storage keys.
- The wind-down notice says the service ceases at 17:00 Central Time on 2026-12-08, which The Register gives as 23:00 UTC. Workloads still running are terminated and data is no longer accessible.

The Register says the notice was posted on Tuesday, which is 2026-11-24. It says Rackspace has not said how many customers were affected and did not answer its questions.

In [a discussion on the Spot repository](https://github.com/rackerlabs/spot/discussions/510) on 2026-11-20, a customer asked about an outage then 24 hours old. The account `sirishkr` replied that the root cause was an observability system breached using a compromised credential, and that changes to the underlying infrastructure clusters were extending the outage. The Register identifies the author as Sirish Raghuram, a co-founder of Platform9, which it says co-developed Spot with Rackspace.

No source says how the credential was compromised. The Register calls the credentials "leaked".

## Am I affected?

- You are in scope if you had a Rackspace Spot account with clusters on 2026-11-17. The Register's account does not say how Rackspace decided which users were affected.
- As a check beyond the report, look in each cluster for pods, service accounts and role bindings you did not create, dated 2026-11-17 or later.
- Any Secret in an affected user's clusters may have been read, per the notification. That includes database passwords and third-party API keys your workloads mounted.

## If you are affected

The Register says customers must:

1. Reissue Spot API tokens.
2. Download new Kubernetes configuration files.
3. Rotate credentials stored in the clusters, "including database passwords and third-party API keys".

As a caution beyond the report, rotate at the service that issued each credential and review that service's logs from 2026-11-17 onward. See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).

Move workloads and copy data out before 2026-12-08 23:00 UTC.

## Prevention

- A managed Kubernetes provider's control plane can read every Secret in the cluster. Keep high-value credentials in an external secret manager with short-lived access. See [credential hygiene](../prevention/credential-hygiene.md).
- Keep backups of cluster data outside the provider.

## Sources

- [The Register, 2026-11-26](https://www.theregister.com/cyber-crime/2026/11/26/rackspace-pulls-plug-on-spot-cloud-service-after-security-breach/5312352): the wind-down notice, the customer notification, dates and quotations.
- [rackerlabs/spot discussion 510](https://github.com/rackerlabs/spot/discussions/510), 2026-11-20, read 2026-11-26 through a summarizing fetch. The root-cause reply is paraphrased here.
- Not readable: `status.spot.rackspace.com` returned a page title and no incident text to two fetch methods on 2026-11-26. Not opened: the Rackspace notice and the customer notification.
