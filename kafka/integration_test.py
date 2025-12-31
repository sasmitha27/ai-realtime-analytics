"""Integration test: start a consumer thread, send messages, assert roundtrip."""
import json
import uuid
import random
import time
import threading
from kafka import KafkaProducer, KafkaConsumer

TOPIC = "booking-events"
BOOTSTRAP = "127.0.0.1:9092"
NUM_MESSAGES = 10

received = []
recv_lock = threading.Lock()
done = threading.Event()


def consumer_worker():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    start = time.time()
    timeout = 25
    try:
        while time.time() - start < timeout:
            records = consumer.poll(timeout_ms=1000)
            if not records:
                continue
            for tp, msgs in records.items():
                for m in msgs:
                    with recv_lock:
                        received.append(m.value)
                        if len(received) >= NUM_MESSAGES:
                            break
                if len(received) >= NUM_MESSAGES:
                    break
            if len(received) >= NUM_MESSAGES:
                break
    finally:
        consumer.close()
        done.set()


def produce_messages(n):
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    for _ in range(n):
        event = {
            "event_id": str(uuid.uuid4()),
            "user_id": random.randint(1, 100),
            "hotel_id": random.randint(1, 20),
            "amount": round(random.uniform(50, 500), 2),
            "event_time": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        }
        producer.send(TOPIC, event)
        producer.flush()
    producer.close()


if __name__ == "__main__":
    t = threading.Thread(target=consumer_worker, daemon=True)
    t.start()

    # Give consumer a moment to subscribe
    time.sleep(1)

    produce_messages(NUM_MESSAGES)

    # Wait for messages to be received
    success = done.wait(timeout=20)

    with recv_lock:
        got = len(received)

    print(f"Sent {NUM_MESSAGES} messages. Received {got} messages.")

    if not success or got != NUM_MESSAGES:
        print("Integration test FAILED")
        raise SystemExit(2)

    print("Integration test PASSED")
    raise SystemExit(0)
