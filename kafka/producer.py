import json
import time
import uuid
import random
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers="127.0.0.1:9092",  # <-- change this
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

while True:
    event = {
        "event_id": str(uuid.uuid4()),
        "user_id": random.randint(1, 100),
        "hotel_id": random.randint(1, 20),
        "amount": round(random.uniform(50, 500), 2),
        "event_time": datetime.utcnow().isoformat()
    }

    producer.send("booking-events", event)
    print(event)
    time.sleep(1)
