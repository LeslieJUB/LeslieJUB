# StreamForge operations runbook

## Local startup
1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build -d`.
3. Wait for Kafka, PostgreSQL and MinIO health checks.
4. Check `/health`, `/ready` and Prometheus targets.
5. Publish a small test batch with `docker compose run --rm producer --count 100 --rate 20`.

## Normal operations
- API liveness: `GET /health`
- API/database readiness: `GET /ready`
- Worker metrics: `http://localhost:9101/metrics`
- API metrics: `http://localhost:8000/metrics`
- Analytics summary: `GET /v1/analytics/summary`
- Rejected messages: Kafka topic `commerce.orders.dlq.v1`

## Failure handling
- **Invalid event:** validation failure increments `streamforge_events_invalid_total`; the original key/value and source topic/partition/offset are published to the DLQ. The consumer commits only after DLQ delivery is acknowledged.
- **PostgreSQL failure:** batch processing raises; no offsets are committed. Kafka will redeliver after restart/rebalance.
- **Object storage failure:** offsets are not committed. PostgreSQL upsert makes the database replay idempotent. Object-store objects may be duplicated if failure occurs after an upload; reconcile using batch timestamps and source metadata before replaying at scale.
- **Worker restart:** inspect logs, confirm Kafka group offsets and verify persisted event IDs before restarting producers.
- **Kafka unavailable:** stop event generation, restore broker connectivity, then restart worker. Do not reset consumer offsets unless replay has been planned.
- **DLQ unavailable:** consumer intentionally does not commit affected offsets. Restore the DLQ broker/topic before resuming.

## Recovery commands
```bash
docker compose ps
docker compose logs --tail=200 worker
docker compose logs --tail=200 kafka
docker compose exec kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka:9092 --describe --group streamforge-consumer
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --describe --topic commerce.orders.dlq.v1
```

## Data retention and reset
Local state is held in Docker volumes. `docker compose down -v` permanently removes local PostgreSQL and MinIO data; use only when intentionally resetting the development environment.

## Production release checklist
- Use private networking, IAM task roles and managed secrets; never use local demo credentials.
- Enable TLS/SASL and IAM authorization for managed Kafka.
- Configure S3 bucket policies, KMS key policies and lifecycle/retention with data-owner approval.
- Add database backups, point-in-time recovery, connection limits and migrations.
- Add DLQ retention, alerting and a reviewed replay tool.
- Load-test with representative event distributions and failure injection.
- Define SLOs for event freshness, consumer lag, API availability and data loss.
- Review AWS cost estimates, budgets and alarms before provisioning.
