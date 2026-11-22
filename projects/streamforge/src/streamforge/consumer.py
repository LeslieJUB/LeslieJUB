import json
import logging
import time
from confluent_kafka import Consumer, KafkaError
from pydantic import ValidationError
from prometheus_client import start_http_server
from .config import get_settings
from .db import initialise_database, make_engine
from .metrics import BATCH_DURATION, BATCH_SIZE, EVENTS_ANOMALOUS, EVENTS_CONSUMED, EVENTS_INVALID, EVENTS_PERSISTED
from .persistence import persist_batch
from .schemas import OrderEvent
from .storage import write_batch
from .transforms import enrich_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("streamforge.consumer")

def process_batch(engine, records: list[dict]) -> None:
    if not records:
        return
    started = time.perf_counter()
    persist_batch(engine, records)
    write_batch(records)
    EVENTS_PERSISTED.inc(len(records))
    EVENTS_ANOMALOUS.inc(sum(1 for row in records if row["is_anomaly"]))
    BATCH_SIZE.set(len(records))
    BATCH_DURATION.observe(time.perf_counter() - started)
    log.info("Persisted batch size=%d", len(records))

def main() -> None:
    settings = get_settings()
    start_http_server(9101)
    engine = make_engine()
    initialise_database(engine)
    consumer = Consumer({
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "group.id": settings.kafka_group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "max.poll.interval.ms": 300000,
    })
    consumer.subscribe([settings.kafka_topic])
    batch = []
    last_flush = time.monotonic()
    log.info("Consuming topic=%s", settings.kafka_topic)
    try:
        while True:
            message = consumer.poll(1.0)
            if message is not None:
                if message.error():
                    if message.error().code() != KafkaError._PARTITION_EOF:
                        log.error("Kafka error: %s", message.error())
                else:
                    EVENTS_CONSUMED.inc()
                    try:
                        event = OrderEvent.model_validate_json(message.value())
                        batch.append(enrich_event(event, settings))
                    except (ValidationError, ValueError, json.JSONDecodeError):
                        EVENTS_INVALID.inc()
                        log.exception("Rejected invalid event at offset=%s", message.offset())
                    if len(batch) >= settings.batch_size:
                        process_batch(engine, batch)
                        consumer.commit(asynchronous=False)
                        batch.clear()
                        last_flush = time.monotonic()
            if batch and time.monotonic() - last_flush >= settings.batch_flush_seconds:
                process_batch(engine, batch)
                consumer.commit(asynchronous=False)
                batch.clear()
                last_flush = time.monotonic()
    except KeyboardInterrupt:
        log.info("Shutdown requested")
    finally:
        if batch:
            process_batch(engine, batch)
            consumer.commit(asynchronous=False)
        consumer.close()

if __name__ == "__main__":
    main()
