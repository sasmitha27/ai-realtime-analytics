import json
import time
from kafka import KafkaConsumer


def main():
    consumer = KafkaConsumer(
        "booking-events",
        bootstrap_servers="127.0.0.1:9092",
        auto_offset_reset="earliest",
        consumer_timeout_ms=1000,
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )

    print("Consumer started, waiting for messages...")
    start = time.time()
    received = 0
    # Wait up to 30 seconds for messages
    while time.time() - start < 30:
        for msg in consumer:
            print("Received:", msg.value)
            received += 1
            if received >= 5:
                break
        if received >= 5:
            break
        time.sleep(0.5)

    consumer.close()
    print(f"Consumer exiting after receiving {received} messages")


if __name__ == "__main__":
    main()
