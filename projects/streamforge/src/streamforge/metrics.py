from prometheus_client import Counter, Gauge, Histogram

EVENTS_CONSUMED = Counter("streamforge_events_consumed_total", "Kafka events consumed")
EVENTS_PERSISTED = Counter("streamforge_events_persisted_total", "Events persisted to sinks")
EVENTS_INVALID = Counter("streamforge_events_invalid_total", "Events rejected by validation")
EVENTS_ANOMALOUS = Counter("streamforge_events_anomalous_total", "Events flagged by anomaly rules")
BATCH_DURATION = Histogram("streamforge_batch_duration_seconds", "Batch processing duration")
BATCH_SIZE = Gauge("streamforge_last_batch_size", "Number of events in latest persisted batch")
