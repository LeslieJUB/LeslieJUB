import argparse
import json
import random
import time
from datetime import datetime, timezone
from uuid import uuid4
from confluent_kafka import Producer
from .config import get_settings

def build_event(index: int, rng: random.Random | None = None) -> dict:
    rng = rng or random.Random()
    amount, quantity = round(rng.uniform(8, 800), 2), rng.randint(1, 8)
    if index and index % 97 == 0:
        amount = 7500.0
    if index and index % 131 == 0:
        quantity = 150
    return {
        "event_id": str(uuid4()), "order_id": f"ORD-{index:09d}",
        "customer_id": f"CUST-{rng.randint(1, 50000):06d}",
        "event_time": datetime.now(timezone.utc).isoformat(),
        "amount": amount, "currency": "EUR", "quantity": quantity,
        "source": "synthetic-commerce",
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Publish synthetic commerce events")
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--rate", type=float, default=100)
    args = parser.parse_args()
    if args.count < 1 or args.rate <= 0:
        parser.error("--count and --rate must be positive")
    settings = get_settings()
    producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers, "enable.idempotence": True})
    for index in range(args.count):
        event = build_event(index)
        producer.produce(settings.kafka_topic, key=event["order_id"], value=json.dumps(event).encode())
        producer.poll(0)
        time.sleep(1 / args.rate)
    producer.flush(30)
    print(f"Published {args.count} events to {settings.kafka_topic}")

if __name__ == "__main__":
    main()
