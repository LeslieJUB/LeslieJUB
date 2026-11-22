import json
import logging
import time
from collections import defaultdict

from confluent_kafka import Consumer, KafkaError, Producer, TopicPartition
from pydantic import ValidationError
from prometheus_client import start_http_server

from .config import get_settings
from .db import initialise_database, make_engine
from .metrics import (
    BATCH_DURATION,
    BATCH_SIZE,
    EVENTS_ANOMALOUS,
    EVENTS_CONSUMED,
    EVENTS_INVALID,
    EVENTS_PERSISTED,
)
from .persistence import persist_batch
from .schemas import OrderEvent
from .storage import write_batch
from .transforms import enrich_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("streamforge.consumer")


def publish_dead_letters(producer: Producer, topic: str, records: list[dict]) -> None:
    """Publish rejected source messages and fail the batch if delivery is uncertain."""
    delivery_errors = []

    def on_delivery(error, message):
        if error is not None:
            delivery_errors.append(str(error))

    for record in records:
        producer.produce(
            topic,
            key=record["key"],
            value=record["value"],
            headers=[
                ("source_topic", record["source_topic"].encode()),
                ("source_partition", str(record["partition"]).encode()),
                ("source_offset", str(record["offset"]).encode()),
                ("validation_error", record["reason"].encode()),
            ],
            on_delivery=on_delivery,
        )
        producer.poll(0)

    outstanding = producer.flush(15)
    if outstanding or delivery_errors:
        raise RuntimeError(
            f"Dead-letter delivery incomplete: outstanding={outstanding}, errors={delivery_errors}"
        )


def flush_batch(
    engine,
    producer: Producer,
    dlq_topic: str,
    consumer: Consumer,
    records: list[dict],
    dead_letters: list[dict],
    offsets: dict[tuple[str, int], int],
) -> None:
    """Commit only after every sink has durably accepted the current batch."""
    if not records and not dead_letters:
        return

    started = time.perf_counter()
    if records:
        persist_batch(engine, records)
        write_batch(records)

    if dead_letters:
        publish_dead_letters(producer, dlq_topic, dead_letters)

    commit_offsets = [
        TopicPartition(topic, partition, offset + 1)
        for (topic, partition), offset in offsets.items()
    ]
    if commit_offsets:
        consumer.commit(offsets=commit_offsets, asynchronous=False)

    EVENTS_PERSISTED.inc(len(records))
    EVENTS_ANOMALOUS.inc(sum(1 for row in records if row["is_anomaly"]))
    BATCH_SIZE.set(len(records))
    BATCH_DURATION.observe(time.perf_counter() - started)
    log.info(
        "Committed batch valid=%d dead_letter=%d partitions=%d",
        len(records), len(dead_letters), len(commit_offsets),
    )


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
    producer = Producer({
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "enable.idempotence": True,
        "acks": "all",
    })

    consumer.subscribe([settings.kafka_topic])
    records: list[dict] = []
    dead_letters: list[dict] = []
    offsets: dict[tuple[str, int], int] = defaultdict(lambda: -1)
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
                    offsets[(message.topic(), message.partition())] = max(
                        offsets[(message.topic(), message.partition())], message.offset()
                    )
                    try:
                        event = OrderEvent.model_validate_json(message.value())
                        records.append(enrich_event(event, settings))
                    except (ValidationError, ValueError, json.JSONDecodeError) as exc:
                        EVENTS_INVALID.inc()
                        dead_letters.append({
                            "key": message.key(),
                            "value": message.value(),
                            "source_topic": message.topic(),
                            "partition": message.partition(),
                            "offset": message.offset(),
                            "reason": str(exc)[:4000],
                        })
                        log.warning(
                            "Rejected event topic=%s partition=%d offset=%d: %s",
                            message.topic(), message.partition(), message.offset(), exc,
                        )

            batch_due = (
                len(records) + len(dead_letters) >= settings.batch_size
                or (records or dead_letters)
                and time.monotonic() - last_flush >= settings.batch_flush_seconds
            )
            if batch_due:
                flush_batch(
                    engine, producer, settings.kafka_dlq_topic, consumer,
                    records, dead_letters, offsets,
                )
                records.clear()
                dead_letters.clear()
                offsets.clear()
                last_flush = time.monotonic()

    except KeyboardInterrupt:
        log.info("Shutdown requested")
    finally:
        if records or dead_letters:
            flush_batch(
                engine, producer, settings.kafka_dlq_topic, consumer,
                records, dead_letters, offsets,
            )
        consumer.close()
        producer.flush(15)


if __name__ == "__main__":
    main()
