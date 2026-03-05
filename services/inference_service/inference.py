import json
import time
import mlflow
import mlflow.pyfunc
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer

# Wait for services to start
time.sleep(10)

print("Connecting to MLflow...")
mlflow.set_tracking_uri("http://mlflow:5000")

model = None

# Retry loading model from MLflow
for i in range(10):
    try:
        print("Attempting to load Production model...")
        model = mlflow.pyfunc.load_model("models:/fraud_model/Production")
        print("✅ Model loaded successfully.")
        break
    except Exception:
        print(f"Model not ready yet. Retry {i+1}/10")
        time.sleep(5)

if model is None:
    raise Exception("❌ Failed to load Production model after retries.")

# Kafka Consumer (orders topic)
consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="kafka:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="inference-group"
)

# Kafka Producer (optimized settings)
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    linger_ms=10,
    batch_size=16384,
    acks="all"
)

print("🚀 Started consuming from orders topic...")

for message in consumer:
    try:
        data = message.value
        print("📥 Received order:", data)

        # Convert to DataFrame for model prediction
        df = pd.DataFrame([{
            "amount": data["amount"],
            "country": data["country"],
            "device": data["device"]
        }])

        # Predict fraud
        prediction = int(model.predict(df)[0])

        # Append prediction to original message
        data["prediction"] = prediction

        # Send prediction to Kafka
        producer.send("predictions", data)

        print("📤 Sent prediction:", data)

    except Exception as e:
        print("❌ Error processing message:", e)