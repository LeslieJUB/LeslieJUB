# Architecture decision records

## ADR-001: Kafka as event backbone
Use Apache Kafka in KRaft mode locally to demonstrate partitions, consumer groups and offsets without ZooKeeper. The single-broker Compose environment is for development, not high availability.

## ADR-002: At-least-once delivery with idempotent database writes
Disable automatic offset commits and commit after sink persistence. If a worker crashes before committing, Kafka can redeliver. PostgreSQL's event UUID primary key and upsert avoid duplicate database rows. A crash between object-store upload and offset commit may duplicate lake files; production hardening needs deterministic batch IDs and a manifest/reconciliation protocol.

## ADR-003: S3-compatible local object storage
Use MinIO locally and S3 in AWS through boto3's S3 API.

## ADR-004: Bronze and silver zones
Keep source event records separate from enriched analytical records to support replay and lineage. Gold storage is provisioned in AWS but gold models are not implemented yet.

## ADR-005: Explicit anomaly rules
Use configurable amount and quantity thresholds in the first milestone. These are transparent demo rules, not machine-learning fraud detection.
