# AWS data-lake foundation

Provisions three private S3 buckets (bronze, silver, gold), versioning, KMS server-side encryption, public access blocks and lifecycle expiry for noncurrent object versions.

Default region: eu-central-1 (Frankfurt).

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -var="project_name=streamforge" -var="environment=dev"
```

Use AWS profile or environment credentials; never commit secrets. Review the plan and AWS pricing before apply. These resources can incur charges. Destroy resources when no longer needed.

This is only the storage foundation. ECS/Fargate, MSK, VPC networking, IAM task roles, Secrets Manager, alarms and cost controls are planned next.
