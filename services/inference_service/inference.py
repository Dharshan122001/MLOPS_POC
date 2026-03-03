import json
import time
import mlflow
import time
import mlflow.pyfunc
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer

# Wait for Kafka to be ready
time.sleep(10)

print("Connecting to MLflow...")
mlflow.set_tracking_uri("http://mlflow:5000")

model = None

for i in range(10):
    try:
        print("Attempting to load Production model...")
        model = mlflow.pyfunc.load_model("models:/fraud_model/Production")
        print("Model loaded successfully.")
        break
    except Exception as e:
        print(f"Model not ready yet. Retry {i+1}/10")
        time.sleep(5)

if model is None:
    raise Exception("Failed to load Production model after retries.")
# Kafka Consumer (orders topic)
consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="kafka:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="inference-group"
)

# Kafka Producer (predictions topic)
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)

print("Started consuming from orders topic...")

for message in consumer:
    data = message.value
    print("Received:", data)

    # Convert to DataFrame
    df = pd.DataFrame([{
        "amount": data["amount"],
        "country": data["country"],
        "device": data["device"]
    }])

    # Predict
    prediction = int(model.predict(df)[0])

    # Append prediction
    data["prediction"] = prediction

    # Send to predictions topic
    producer.send("predictions", data)
    producer.flush()

    print("Sent prediction:", data)