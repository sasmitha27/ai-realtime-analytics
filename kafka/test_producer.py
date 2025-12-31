import json
import uuid
import random
from datetime import datetime
from kafka import KafkaProducer


def make_event():
    return {
        "event_id": str(uuid.uuid4()),
        "user_id": random.randint(1, 100),
        "hotel_id": random.randint(1, 20),
        "amount": round(random.uniform(50, 500), 2),
        "event_time": datetime.utcnow().isoformat()
    }


def main():
    producer = KafkaProducer(
        bootstrap_servers="127.0.0.1:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    for i in range(5):
        event = make_event()
        producer.send("booking-events", event)
        print("Sent:", event)
        producer.flush()

    producer.close()


if __name__ == "__main__":
    main()
