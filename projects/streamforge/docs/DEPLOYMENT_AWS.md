# AWS deployment guide

## What this deploys today

The current Terraform module deploys the **data-lake storage foundation only** in `eu-central-1`:

- Three private S3 buckets: bronze, silver and gold
- S3 versioning
- KMS server-side encryption and key rotation
- S3 public-access blocks
- Expiration of noncurrent object versions after 90 days

It does **not** deploy Kafka/MSK, PostgreSQL/RDS, ECS/Fargate, a VPC, a load balancer, API/worker services, IAM runtime roles or a public endpoint. The local Docker Compose environment is the currently runnable application deployment.

## Prerequisites

- An AWS account with permission to create S3 buckets and KMS keys
- AWS CLI v2 and Terraform >= 1.7
- An AWS IAM Identity Center profile or another short-lived credential mechanism
- A reviewed budget and AWS cost alert

Authenticate with SSO, for example:

```bash
aws configure sso
aws sso login --profile streamforge-dev
export AWS_PROFILE=streamforge-dev
aws sts get-caller-identity
```

Never put access keys in source files, `.env`, Terraform variables or GitHub commits.

## Plan and apply

```bash
cd infra/terraform
terraform init
terraform plan -var="project_name=streamforge" -var="environment=dev"
```

Inspect the plan carefully. Applying provisions a KMS key and three S3 buckets, which may incur storage, request and KMS charges:

```bash
terraform apply -var="project_name=streamforge" -var="environment=dev"
terraform output
```

Keep the Terraform state private and backed up. For a team deployment, configure a remote encrypted state backend with locking before sharing ownership.

## Cleanup

After exporting or deleting data intentionally, run:

```bash
terraform destroy -var="project_name=streamforge" -var="environment=dev"
```

The default `force_destroy=false` is deliberate: Terraform will not silently empty non-empty buckets. KMS key deletion is scheduled with a seven-day waiting period.

## Production runtime still required

Before calling this a deployed production platform, add and review:
- VPC private subnets, routing, security groups and VPC endpoints
- Managed Kafka (MSK) with TLS/SASL IAM authentication and topic ACLs
- RDS PostgreSQL with encryption, backups and private connectivity
- ECS/Fargate API and worker services, ECR image publishing and deployment pipeline
- IAM task roles scoped to the exact buckets, topics and secrets
- Secrets Manager, CloudWatch logs/alarms, tracing and operational dashboards
- WAF/authentication/rate limiting for any public API
- Load tests, recovery drills, budget alarms and a rollback strategy

Do not deploy the local plaintext Kafka listener, MinIO credentials or demo PostgreSQL password into AWS.
