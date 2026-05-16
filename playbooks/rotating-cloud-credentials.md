# Rotating cloud credentials

> Scope: AWS, GCP, Azure, Kubernetes — when you suspect creds on your machine or in CI were exfiltrated.

## Do this first (60 seconds)

For each cloud you use:

- **AWS:** [console.aws.amazon.com/iam/home#/users](https://console.aws.amazon.com/iam/home#/users) → your user → **Security credentials** → **Make inactive** on every access key. (Don't delete yet — you may need the access key ID for log forensics.)
- **GCP:** [console.cloud.google.com/iam-admin/serviceaccounts](https://console.cloud.google.com/iam-admin/serviceaccounts) → revoke every key.
- **Azure:** [portal.azure.com](https://portal.azure.com) → Azure AD → App registrations → revoke client secrets.
- **Kubernetes:** rotate the service account tokens or kubeconfig credentials — see below.

Inactivating before deleting is important: an attacker spinning up resources will leave logs tied to the access key ID, which you'll want for forensics.

## Triage — what could the attacker have done?

Cloud creds with admin scope can cost real money very fast (crypto miners, training runs) and exfiltrate data. Even read-only creds can dump customer PII.

| Cred type | Worst case |
|---|---|
| AWS root user keys | Full account takeover. Delete root keys forever, use IAM users. |
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

# Delete the old key (once you've confirmed nothing breaks with the new one)
aws iam delete-access-key --user-name YOUR_USER --access-key-id AKIA_OLD
```

Also:
- **MFA:** confirm MFA is enabled on your IAM user.
- **Session tokens / SSO:** if you use AWS SSO or IAM Identity Center, sign out all sessions: `aws sso logout`.
- **Switch to short-lived creds.** Prefer SSO / `aws sts assume-role` over long-lived access keys. For CI, prefer OIDC (GitHub Actions ↔ AWS) over stored keys.

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

Prefer **Workload Identity Federation** over downloaded SA JSON keys.

### Azure

```bash
# List app registrations / service principals
az ad sp list --display-name "YOUR_SP_NAME"

# Reset client secret
az ad sp credential reset --id <appId>

# Sign out
az logout
rm -rf ~/.azure
az login
```

### Kubernetes

```bash
# Find what creds your kubeconfig holds
kubectl config view --raw | grep -E "token|certificate"

# Rotate based on cred type:
# - exec'd cloud SA token: rotate the underlying cloud SA (see above)
# - long-lived service account token: kubectl delete secret <sa-token>; recreate
# - client cert: re-issue from your cluster CA
# - kubeconfig file: delete, regenerate, redistribute

rm ~/.kube/config
# Then re-obtain from your cluster (e.g., aws eks update-kubeconfig, gcloud container clusters get-credentials)
```

## Audit damage

Pull the audit log for the time window from the compromise to now. Look for resources you didn't create, IAM/role changes, and unusual API calls.

```bash
# AWS — CloudTrail recent events
aws cloudtrail lookup-events --start-time 2026-05-10 --max-items 100 --output table

# AWS — billing anomaly (the loudest signal)
# Check Cost Explorer for spend spikes; new EC2/SageMaker/Bedrock is usually crypto/AI abuse.

# GCP — admin activity logs
gcloud logging read 'logName="projects/PROJECT/logs/cloudaudit.googleapis.com%2Factivity"' --limit 100 --freshness=7d

# Azure — Activity Log
az monitor activity-log list --start-time 2026-05-10 --max-events 100 -o table
```

For each unexpected resource:
1. Document it (resource ID, region, creation time).
2. Delete it.
3. If it pushed data out, you need to disclose to affected customers.

## Prevention going forward
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

**Hard rules:**
- No long-lived cloud keys on developer machines. SSO + role assumption only.
- No long-lived keys in CI. OIDC federation (GitHub Actions / GitLab / etc.).
- Keys that *must* exist (legacy systems): 1Password CLI or AWS Secrets Manager, never `~/.aws/credentials` plain text.
- Set spend alerts. A $500/day spike on a usually-quiet account is your loudest intrusion signal.
