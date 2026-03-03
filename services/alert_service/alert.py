import json
from confluent_kafka import Consumer

print("🚨 Alert Service Starting...")

consumer_config = {
    "bootstrap.servers": "kafka:9092",
    "group.id": "alert-group",
    "auto.offset.reset": "earliest"
}

consumer = Consumer(consumer_config)
consumer.subscribe(["fraud_predictions"])

print("🚨 Listening for Fraud Alerts...")

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue

    if msg.error():
        print("❌ Kafka Error:", msg.error())
        continue

    prediction = json.loads(msg.value().decode("utf-8"))

    if prediction["prediction"] == 1:
        print("🚨 FRAUD ALERT:", prediction)