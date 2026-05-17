# Rotating cloud credentials

> Scope: AWS, GCP, Azure, Kubernetes — when you suspect creds on your machine or in CI were exfiltrated.

## Authoritative playbooks (use these as the source of truth)

- **[AWS Customer Playbook Framework — Compromised IAM Credentials](https://github.com/aws-samples/aws-customer-playbook-framework/blob/main/docs/Compromised_IAM_Credentials.md)** — the official AWS-blessed incident response playbook.
- **[AWS Security Incident Response User Guide](https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/technique-access-containment.html)** — the framework.
- **[AWS Docs — Secure access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/securing_access-keys.html)**.
- **[AWS re:Post — Resolve unauthorized activity in AWS accounts](https://repost.aws/knowledge-center/potential-account-compromise)**.
- **[Datadog Security Labs — Known compromised IAM user access key](https://securitylabs.datadoghq.com/cloud-security-atlas/vulnerabilities/iam-user-known-compromise/)** — detection guidance.
- **[GCP — Investigate suspicious activity](https://cloud.google.com/iam/docs/best-practices-service-accounts#mitigate-suspicious-activity)**.
- **[Azure — Investigate sign-in risk](https://learn.microsoft.com/en-us/azure/active-directory/identity-protection/howto-identity-protection-investigate-risk)**.

## Do this first (60 seconds)

For each cloud you use:

- **AWS:** [console.aws.amazon.com/iam/home#/users](https://console.aws.amazon.com/iam/home#/users) → your user → **Security credentials** → **Make inactive** on every access key. (Don't delete yet — you may need the access key ID for log forensics.)
- **GCP:** [console.cloud.google.com/iam-admin/serviceaccounts](https://console.cloud.google.com/iam-admin/serviceaccounts) → revoke every key.
- **Azure:** [portal.azure.com](https://portal.azure.com) → Microsoft Entra ID → App registrations → revoke client secrets.
- **Kubernetes:** rotate service account tokens or kubeconfig credentials — see below.

**Inactivating before deleting is important:** an attacker spinning up resources leaves logs tied to the access key ID, which you want for forensics.

> If AWS detects your key was exposed (e.g., on GitHub), they auto-attach the `AWSCompromisedKeyQuarantineV2` managed policy to the affected IAM user. Check for that policy first — if it's there, AWS has already partially contained the incident.

## Triage — what could the attacker have done?

Cloud creds with admin scope can cost real money very fast (crypto miners, model training runs) and exfiltrate data. Even read-only creds can dump customer PII.

| Cred type | Worst case |
|---|---|
| AWS root user keys | Full account takeover. Delete root keys forever; use IAM users. |
| AWS IAM admin keys | Spin up EC2 fleets, dump S3, exfiltrate RDS, leave persistent backdoors. |
| GCP service account JSON with `roles/owner` | Same as AWS admin — full project compromise. |
| Azure service principal client secret with broad RBAC | Same. |
| Kubernetes admin kubeconfig | Run any container as cluster-admin; pivot to cloud creds via IMDS. |

## Rotate

### AWS

```bash
# List access keys for the affected IAM user
aws iam list-access-keys --user-name YOUR_USER

# Create a new key (write it down — only shown once)
aws iam create-access-key --user-name YOUR_USER

# Update your local config
aws configure  # or edit ~/.aws/credentials directly

# Delete the old key (once new one is confirmed working)
aws iam delete-access-key --user-name YOUR_USER --access-key-id AKIA_OLD
```

Also:

- **MFA:** confirm MFA is enabled on your IAM user.
- **Session tokens / SSO:** if you use AWS SSO or IAM Identity Center, `aws sso logout`.
- **Switch to short-lived creds.** Prefer SSO / `aws sts assume-role` over long-lived access keys. For CI, prefer **[GitHub OIDC ↔ AWS](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)** over stored keys.

### GCP

```bash
# List service account keys
gcloud iam service-accounts keys list --iam-account=SA@PROJECT.iam.gserviceaccount.com

# Delete each key
gcloud iam service-accounts keys delete KEY_ID --iam-account=SA@PROJECT.iam.gserviceaccount.com

# Sign out user creds locally
gcloud auth revoke --all
rm -rf ~/.config/gcloud
gcloud auth login
gcloud auth application-default login
```

Prefer **[Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)** over downloaded SA JSON keys.

### Azure

```bash
# List service principals
az ad sp list --display-name "YOUR_SP_NAME"

# Reset client secret
az ad sp credential reset --id <appId>

# Sign out
az logout
rm -rf ~/.azure
az login
```

Use **[Workload Identity Federation for Azure](https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation)** with GitHub Actions instead of long-lived client secrets.

### Kubernetes

```bash
# Find what creds your kubeconfig holds
kubectl config view --raw | grep -E "token|certificate"

# Rotate based on cred type:
# - exec'd cloud SA token: rotate the underlying cloud SA (see above)
# - long-lived SA token: kubectl delete secret <sa-token>; recreate
# - client cert: re-issue from your cluster CA
# - kubeconfig file: delete, regenerate, redistribute

rm ~/.kube/config
# Then re-obtain from your cluster (e.g., aws eks update-kubeconfig)
```

## Audit damage

Pull the audit log for the time window. Look for unfamiliar resources, IAM/role changes, and unusual API calls.

```bash
# AWS — CloudTrail recent events
aws cloudtrail lookup-events --start-time 2026-05-10 --max-items 100 --output table

# AWS — billing anomaly (the loudest signal)
# Check Cost Explorer for spend spikes; new EC2/SageMaker/Bedrock is usually crypto/AI abuse.

# GCP — admin activity logs
gcloud logging read 'logName="projects/PROJECT/logs/cloudaudit.googleapis.com%2Factivity"' \
  --limit 100 --freshness=7d

# Azure — Activity Log
az monitor activity-log list --start-time 2026-05-10 --max-events 100 -o table
```

For each unexpected resource: **document → delete → disclose if customer data was touched.**

## Prevention going forward

**Hard rules:**

- No long-lived cloud keys on developer machines. SSO + role assumption only.
- No long-lived keys in CI. **[OIDC federation](https://docs.github.com/en/actions/concepts/security/openid-connect)** for GitHub Actions / GitLab / etc.
- Keys that *must* exist (legacy systems): [1Password CLI](https://developer.1password.com/docs/cli/) or AWS Secrets Manager — never `~/.aws/credentials` plain text.
- **Set spend alerts.** A $500/day spike on a usually-quiet account is your loudest intrusion signal.
- Subscribe to **AWS GuardDuty** / **GCP Security Command Center** / **Azure Defender for Cloud** — they detect known-bad behaviors (impossible-travel logins, mass S3 reads, etc.) automatically.

→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) for the broader credential model.
