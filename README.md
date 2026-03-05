# 🚨 Real-Time Fraud Detection Platform

A production-ready MLOps streaming architecture that demonstrates end-to-end fraud detection with machine learning inference, real-time alerting, and interactive monitoring.

---

## ⭐ Project Highlights

| Feature | Description |
|---------|-------------|
| **Real-time Streaming** | Kafka-powered event-driven architecture |
| **ML Inference** | Real-time fraud prediction using scikit-learn |
| **Model Registry** | MLflow for model versioning and staging |
| **Alert Service** | Instant fraud detection alerts |
| **Data Pipeline** | Apache NiFi for data ingestion |
| **Monitoring** | Streamlit fraud dashboard |
| **Containerized** | Fully Dockerized microservices |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MLOps Fraud Detection Pipeline                            │
└─────────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────────┐         ┌──────────────────┐
     │   Apache NiFi    │         │  Training        │
     │   (Data Gen)     │         │  Service         │
     │   Port: 8080     │         │  (One-time)      │
     └────────┬─────────┘         └────────┬─────────┘
              │                            │
              │ orders                     │ trained model
              ▼                            ▼
     ┌────────────────────────────────────────────────────┐
     │                    Kafka                            │
     │              (Message Broker)                      │
     │            bootstrap-server: 9092                   │
     └────────────────────┬───────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
     ┌──────────────────┐    ┌──────────────────┐
     │  Inference       │    │  MLflow          │
     │  Service         │    │  Server          │
     │  (Real-time)     │    │  Port: 5000      │
     └────────┬─────────┘    └──────────────────┘
              │
              │ predictions (with fraud score)
              ▼
     ┌──────────────────┐
     │  Alert           │
     │  Service         │
     │  (Real-time)     │
     └──────────────────┘
              │
              │ fraud_alerts
              ▼
     ┌──────────────────┐
     │  Streamlit       │
     │  Dashboard       │
     │  Port: 8501      │
     └──────────────────┘
```

---

## 📋 Project Overview

This MLOps POC demonstrates a complete machine learning pipeline:

1. **Data Ingestion**: Apache NiFi generates/produces synthetic transaction data
2. **Model Training**: Training service trains a RandomForest classifier
3. **Model Registry**: MLflow manages model versions and stages
4. **Real-time Inference**: Inference service predicts fraud in real-time
5. **Alerting**: Alert service detects and alerts on fraudulent transactions
6. **Monitoring**: Streamlit dashboard displays fraud analytics

---

## 🛠️ Prerequisites

- **Docker Engine** 20.10+
- **Docker Compose** v2.0+
- **At least 4GB RAM** available
- **Ports** 8080, 9092, 18080, 5000, 8501 available

### Directory Setup

```bash
# Create registry directories for NiFi Registry
mkdir -p registry/flow_storage
mkdir -p registry/database

# Set ownership for NiFi Registry (uses user 1000:1000)
sudo chown -R 1000:1000 registry
```

---

## 🚀 Quick Start

### 1. Start Infrastructure Services

```bash
# Start Kafka, MLflow, NiFi, and NiFi Registry
docker-compose up -d kafka mlflow nifi nifi-registry
```

Verify services are running:
```bash
docker-compose ps
```

### 2. Create Kafka Topics

```bash
# Create orders topic (raw order data)
docker exec -it kafka kafka-topics \
  --create \
  --topic orders \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

# Create predictions topic (fraud predictions)
docker exec -it kafka kafka-topics \
  --create \
  --topic predictions \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

# Create fraud_alerts topic (fraud alerts)
docker exec -it kafka kafka-topics \
  --create \
  --topic fraud_alerts \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

Verify topics:
```bash
docker exec -it kafka kafka-topics \
  --list \
  --bootstrap-server localhost:9092
```

### 3. Train the Model

```bash
# Run the training service
docker-compose run training
```

This will:
- Generate synthetic training data with features: `amount`, `country`, `device`
- Train a RandomForest classifier
- Log metrics to MLflow
- Register the model as `fraud_model`

Access MLflow UI at: **http://localhost:5000**

### 4. Start the Inference Pipeline

```bash
# Start Inference and Alert services
docker-compose up -d inference alert
```

### 5. Start the Dashboard

```bash
# Start Streamlit fraud dashboard
docker-compose up -d fraud_dashboard
```

Access the dashboard at: **http://localhost:8501**

---

## 📊 Testing the Pipeline

### Send a Test Transaction

Using Kafka CLI:
```bash
docker exec -it kafka kafka-console-producer \
  --topic orders \
  --bootstrap-server localhost:9092
```

Then enter a JSON message:

```json
{"order_id": "test001", "amount": 15000, "country": "US", "device": "mobile"}
```

### Monitor Logs

```bash
# View inference logs
docker-compose logs -f inference

# View alert logs
docker-compose logs -f alert
```

---

## 🧩 Kafka Topics

| Topic | Purpose | Message Format |
|-------|---------|----------------|
| `orders` | Raw incoming transactions | `{"order_id": "...", "amount": 5000, "country": "US", "device": "mobile"}` |
| `predictions` | ML prediction results | `{"order_id": "...", "amount": 5000, "country": "US", "device": "mobile", "prediction": 1}` |
| `fraud_alerts` | Fraud alert events | Same as predictions but filtered for fraud (prediction=1) |

---

## 💻 Services Overview

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| **Kafka** | `kafka` | 9092 | Message broker for streaming |
| **MLflow** | `mlflow` | 5000 | Model registry & tracking |
| **NiFi** | `nifi` | 8080 | Data ingestion & generation |
| **NiFi Registry** | `nifi-registry` | 18080 | Flow version control |
| **Training** | `training` | - | Model training (one-time) |
| **Inference** | `inference` | - | Real-time predictions |
| **Alert** | `alert` | - | Fraud alerting |
| **Dashboard** | `fraud_dashboard` | 8501 | Monitoring UI |

---

## 🤖 Model Details

### Algorithm
- **Model**: RandomForest Classifier
- **Library**: scikit-learn

### Features

| Feature | Type | Description |
|---------|------|-------------|
| `amount` | Numeric | Transaction amount in USD |
| `country` | Categorical | Country code (US, IN, UK, etc.) |
| `device` | Categorical | Device type (mobile, desktop) |

### Preprocessing
- **Numeric Features**: Passed through directly
- **Categorical Features**: OneHotEncoder with `handle_unknown="ignore"`

### Fraud Detection Rules (Training Data)
- High amount (> $5,000) combined with certain country/device combinations are labeled as fraud

### Model Registration
- **Model Name**: `fraud_model`
- **Registry**: MLflow Model Registry
- **Stage**: Production

---

## 📂 Project Structure

```
mlops-poc/
├── docker-compose.yml              # Main orchestration file
├── README.md                       # This documentation
├── docs/
│   └── docs.txt                    # Setup notes
├── registry/
│   ├── database/                  # NiFi Registry database
│   ├── flow_storage/              # NiFi Registry flow storage
│   └── postgresql-42.7.3.jar      # PostgreSQL JDBC driver for NiFi
├── services/
│   ├── training_service/
│   │   ├── train.py               # Training script
│   │   ├── requirements.txt       # Python dependencies
│   │   └── Dockerfile             # Container image
│   ├── inference_service/
│   │   ├── inference.py           # Inference script
│   │   ├── requirements.txt       # Python dependencies
│   │   └── Dockerfile             # Container image
│   ├── alert_service/
│   │   ├── alert.py               # Alert consumption script
│   │   ├── requirements.txt       # Python dependencies
│   │   └── Dockerfile             # Container image
│   └── Fraud_Dashboard/
│       ├── Dashboard.py           # Streamlit dashboard
│       ├── requirements.txt       # Python dependencies
│       └── Dockerfile             # Container image
└── data/                          # Data directory (empty)
```

---

## 🌐 Access Services

| Service | URL |
|---------|-----|
| MLflow | http://localhost:5000 |
| NiFi | http://localhost:8080/nifi |
| NiFi Registry | http://localhost:18080 |
| Fraud Dashboard | http://localhost:8501 |

---

## 🔧 Troubleshooting

### Kafka Connection Issues
```bash
# Check Kafka is running
docker-compose ps kafka

# Check Kafka logs
docker-compose logs kafka

# Test Kafka connectivity
docker exec -it kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

### MLflow Model Not Found
```bash
# Verify model is registered
# Access MLflow UI at http://localhost:5000

# Rebuild training service
docker-compose build training
docker-compose run training
```

### NiFi Flow Not Starting
1. Access NiFi UI at http://localhost:8080
2. Verify Processor is running
3. Check Kafka connection is configured
4. Verify FlowFiles are being generated

### Port Conflicts
```bash
# Check what's using the port
sudo lsof -i :8080
sudo lsof -i :9092
sudo lsof -i :5000
sudo lsof -i :8501
```

---

## ⏹️ Stopping Services

### Stop all services (preserve data)
```bash
docker-compose down
```

### Stop and remove volumes (lose all data)
```bash
docker-compose down -v
```

### Stop specific service
```bash
docker-compose stop inference
```

### Restart a service
```bash
docker-compose restart inference
```

---

## 🔮 Future Improvements

- [ ] CI/CD pipeline for automated model deployment
- [ ] Terraform infrastructure provisioning
- [ ] Kafka Dead Letter Queue (DLQ)
- [ ] Slack/Email fraud alert notifications
- [ ] Model monitoring and drift detection
- [ ] Local PostgreSQL database (currently using NeonDB cloud)

---

## 📄 License

This project is provided as a proof-of-concept for educational purposes.

---

## 👨‍💻 Author

**Dharshan**

MLOps / Data Platform Engineering Project
