# StreamForge security notes and threat model

## Assets
- Commerce event payloads and customer identifiers
- Kafka topics, consumer offsets and DLQ records
- PostgreSQL event store
- Bronze/silver/gold object storage
- AWS credentials, KMS keys and deployment configuration

## Trust boundaries
- Producer to Kafka: treat every event as untrusted input.
- Kafka to consumer: validate schema, bounds and timestamp timezone before processing.
- Consumer to sinks: use least-privilege database and object-store identities.
- Public API to data store: expose only read-only aggregate/event endpoints; production requires authentication, rate limiting and network restrictions.
- CI to cloud: use short-lived OIDC federation rather than long-lived AWS access keys.

## Controls in this foundation
- Pydantic validation, strict extra-field rejection and bounded numeric/string fields.
- Manual Kafka commits after successful sink operations.
- Idempotent PostgreSQL primary key/upsert.
- Dead-letter routing with source topic, partition and offset metadata.
- Terraform S3 public-access blocks, versioning and KMS encryption.
- CI read-only repository permission and dependency audit.

## Known gaps before production
- Local Compose passwords are development-only and must never be reused.
- API has no authentication or authorization; do not expose it publicly without an identity layer and rate limiting.
- Kafka local listener is plaintext and single-broker.
- DLQ payloads may contain sensitive source data; apply retention, access controls and redaction policy.
- Database schema is currently created on startup; replace with reviewed Alembic migrations before production.
- No formal PII classification, deletion workflow, audit log or privacy impact assessment exists yet.
- AWS runtime IAM, network policy, Secrets Manager, private subnets and centralized alerting are not yet deployed.
