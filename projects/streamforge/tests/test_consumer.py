from confluent_kafka import TopicPartition

from streamforge import consumer as worker


class FakeProducer:
    def __init__(self):
        self.messages = []
        self.flushed = 0

    def produce(self, topic, **kwargs):
        self.messages.append((topic, kwargs))

    def poll(self, timeout):
        return 0

    def flush(self, timeout):
        self.flushed += 1
        return 0


class FakeConsumer:
    def __init__(self):
        self.committed = None

    def commit(self, offsets, asynchronous):
        self.committed = offsets


def test_dead_letter_publisher_preserves_source_metadata():
    producer = FakeProducer()
    record = {
        "key": b"order-1",
        "value": b"{not-json",
        "source_topic": "commerce.orders.v1",
        "partition": 2,
        "offset": 91,
        "reason": "invalid JSON",
    }

    worker.publish_dead_letters(producer, "commerce.orders.dlq.v1", [record])

    topic, message = producer.messages[0]
    assert topic == "commerce.orders.dlq.v1"
    assert message["key"] == b"order-1"
    assert message["value"] == b"{not-json"
    assert ("source_offset", b"91") in message["headers"]
    assert producer.flushed == 1


def test_batch_commits_next_offset_only_after_all_sinks(monkeypatch):
    calls = []
    monkeypatch.setattr(worker, "persist_batch", lambda engine, rows: calls.append("postgres"))
    monkeypatch.setattr(worker, "write_batch", lambda rows: calls.append("object-storage"))
    monkeypatch.setattr(
        worker, "publish_dead_letters", lambda producer, topic, rows: calls.append("dlq")
    )

    consumer = FakeConsumer()
    offsets = {("commerce.orders.v1", 1): 17}
    worker.flush_batch(
        engine=object(),
        producer=FakeProducer(),
        dlq_topic="commerce.orders.dlq.v1",
        consumer=consumer,
        records=[{"is_anomaly": False}],
        dead_letters=[{"value": b"bad"}],
        offsets=offsets,
    )

    assert calls == ["postgres", "object-storage", "dlq"]
    assert consumer.committed == [TopicPartition("commerce.orders.v1", 1, 18)]


def test_batch_does_not_commit_when_sink_fails(monkeypatch):
    def fail_storage(rows):
        raise RuntimeError("object store unavailable")

    monkeypatch.setattr(worker, "persist_batch", lambda engine, rows: None)
    monkeypatch.setattr(worker, "write_batch", fail_storage)
    consumer = FakeConsumer()

    try:
        worker.flush_batch(
            engine=object(),
            producer=FakeProducer(),
            dlq_topic="commerce.orders.dlq.v1",
            consumer=consumer,
            records=[{"is_anomaly": False}],
            dead_letters=[],
            offsets={("commerce.orders.v1", 0): 4},
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected storage failure to propagate")

    assert consumer.committed is None
