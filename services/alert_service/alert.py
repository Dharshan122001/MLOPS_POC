import json
import time
from kafka import KafkaConsumer, KafkaProducer

print("🚨 Alert Service Starting...")

# Wait for Kafka container to start
time.sleep(10)

# Kafka Consumer (reads predictions)
consumer = KafkaConsumer(
    "predictions",
    bootstrap_servers="kafka:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="alert-group",
    consumer_timeout_ms=1000
)

# Kafka Producer (sends fraud alerts)
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)

print("🚨 Listening for Predictions...")

while True:
    for message in consumer:
        data = message.value

        print("📥 Received prediction:", data)

        if data["prediction"] == 1:
            print("🚨 FRAUD ALERT:", data)

            # Send fraud event to fraud_alerts topic
            producer.send("fraud_alerts", data)
            producer.flush()

        else:
            print("✅ Safe transaction:", data["order_id"])