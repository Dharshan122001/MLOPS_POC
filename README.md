# MLOps Fraud Detection Pipeline

A complete end-to-end MLOps proof-of-concept (POC) for fraud detection using Kafka, MLflow, Apache NiFi, and scikit-learn. This project demonstrates a real-time fraud detection pipeline with model training, inference, and alerting capabilities.

## Table of Contents

- [Architecture](#architecture)
- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Services Overview](#services-overview)
- [Infrastructure Components](#infrastructure-components)
- [Kafka Topics](#kafka-topics)
- [Model Details](#model-details)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Stopping Services](#stopping-services)
- [Extending the Project](#extending-the-project)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MLOps Fraud Detection Pipeline                     │
└─────────────────────────────────────────────────────────────────────────────┘

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
     │              (Message Broker)                       │
     │            bootstrap-server: 9092                  │
     └────────────────────┬───────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
     ┌──────────────────┐    ┌──────────────────┐
     │  Inference       │    │  MLflow          │
     │  Service         │    │  Server          │
     │  (Real-time)     │    │  Port: 5000       │
     └────────┬─────────┘    └──────────────────┘
              │
              │ predictions (with fraud score)
              ▼
     ┌──────────────────┐
     │  Alert           │
     │  Service         │
     │  (Real-time)     │
     └──────────────────┘
```

---

## Project Overview

This MLOps POC demonstrates a complete machine learning pipeline:

1. **Data Generation**: Apache NiFi generates synthetic order data
2. **Model Training**: Training service trains a RandomForest classifier
3. **Model Registry**: MLflow manages model versions and stages
4. **Real-time Inference**: Inference service predicts fraud in real-time
5. **Alerting**: Alert service detects and alerts on fraudulent transactions

---

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- At least 4GB of RAM available
- Ports 8080, 9092, 18080, 5000 available

### Required Directory Setup

Before starting the services, create the necessary directories and set permissions:

```bash
# Create registry directories for NiFi Registry
mkdir -p registry/flow_storage
mkdir -p registry/database

# Set ownership for NiFi Registry (uses user 1000:1000)
sudo chown -R 1000:1000 registry
```

---

## Quick Start

### Step 1: Start Infrastructure Services

```bash
# Start Kafka and MLflow services
docker-compose up -d kafka mlflow
```

Verify services are running:
```bash
docker-compose ps
```

Wait for all services to show "healthy" status.

### Step 2: Create Kafka Topics

Create the required Kafka topics for data flow:

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
```

Verify topics were created:
```bash
docker exec -it kafka kafka-topics \
  --list \
  --bootstrap-server localhost:9092
```

### Step 3: Train the Model

```bash
# Run the training service
docker-compose run training
```

This will:
- Generate synthetic training data with features: `amount`, `country`, `device`
- Train a RandomForest classifier
- Log metrics to MLflow
- Register the model as `fraud_model`
- Model is registered in MLflow model registry

Access MLflow UI at: http://localhost:5000

### Step 4: Start the Data Pipeline

```bash
# Start NiFi, Inference, and Alert services
docker-compose up -d nifi nifi-registry inference alert
```

**Note**: The Alert service is not currently in docker-compose.yml but the code exists in `services/alert_service/`. You'll need to add it or run it manually.

### Step 5: Monitor Results

View inference logs:
```bash
docker-compose logs -f inference
```

View alert logs:
```bash
docker-compose logs -f alert
```

---

## Services Overview

| Service | Container Name | Port | Description | Dependencies |
|---------|---------------|------|-------------|--------------|
| **Kafka** | `kafka` | 9092 | Message broker for data streaming | - |
| **MLflow** | `mlflow` | 5000 | Model registry and tracking server | - |
| **NiFi** | `nifi` | 8080 | Data ingestion and generation | - |
| **NiFi Registry** | `nifi-registry` | 18080 | Flow version control | - |
| **Training** | `training` | - | Trains and registers fraud model | MLflow |
| **Inference** | `inference` | - | Consumes orders, runs predictions | Kafka, MLflow |
| **Alert** | `alert` | - | Listens for fraud predictions | Kafka |

---

## Infrastructure Components

### Apache Kafka (KRaft Mode)

- **Image**: `confluentinc/cp-kafka:7.8.3`
- **Port**: 9092
- **Mode**: KRaft (no Zookeeper required)
- **Purpose**: Message broker for real-time data streaming
- **Persistence**: Data stored in Docker volume `kafka_data`

### MLflow

- **Image**: `ghcr.io/mlflow/mlflow:v2.9.2`
- **Port**: 5000
- **Backend Store**: SQLite (`sqlite:////mlflow/mlflow.db`)
- **Artifact Store**: Docker volume `mlruns`
- **Purpose**: Model tracking, versioning, and registry

### Apache NiFi

- **Image**: `apache/nifi:1.23.2`
- **Port**: 8080
- **Purpose**: Generate synthetic order data and publish to Kafka
- **Registry**: Connected to NiFi Registry for flow version control

### NiFi Registry

- **Image**: `apache/nifi-registry:1.23.2`
- **Port**: 18080
- **Purpose**: Version control for NiFi data flows
- **Storage**: Local `./registry` directory

---

## Kafka Topics

### Topic: `orders`

- **Description**: Raw order data from NiFi producer
- **Partitions**: 1
- **Replication Factor**: 1
- **Message Format**: JSON

Example message:
```json
{
  "amount": 5000.00,
  "country": "US",
  "device": "mobile"
}
```

### Topic: `predictions`

- **Description**: Inference results with fraud prediction
- **Partitions**: 1
- **Replication Factor**: 1
- **Message Format**: JSON

Example message:
```json
{
  "amount": 5000.00,
  "country": "US",
  "device": "mobile",
  "prediction": 1
}
```

---

## Model Details

### Algorithm

- **Model**: RandomForest Classifier
- **Library**: scikit-learn

### Features

| Feature | Type | Description |
|---------|------|-------------|
| `amount` | Numeric | Transaction amount in USD |
| `country` | Categorical | Country code (US, IN, etc.) |
| `device` | Categorical | Device type (mobile, desktop) |

### Preprocessing

- **Numeric Features**: Passed through directly
- **Categorical Features**: OneHotEncoder with `handle_unknown="ignore"`

### Training Data

The training service generates synthetic data with the following fraud rules:
- High amount (> $5,000) combined with specific country/device combinations

### Model Registration

- **Model Name**: `fraud_model`
- **Registry**: MLflow Model Registry
- **Stage**: Production (loaded by inference service)

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MLFLOW_TRACKING_URI` | http://mlflow:5000 | MLflow server URL |
| `MODEL_NAME` | fraud_model | Registered model name |
| `MODEL_STAGE` | Production | Model stage to load |

---

## Troubleshooting

### Kafka Connection Issues

If inference service fails to connect to Kafka:
```bash
# Check Kafka is running
docker-compose ps kafka

# Check Kafka logs
docker-compose logs kafka

# Test Kafka connectivity
docker exec -it kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

### MLflow Model Not Found

If inference service can't load the model:
```bash
# Verify model is registered
docker exec -it mlflow mlflow models list -g 2>/dev/null || echo "Check MLflow UI at http://localhost:5000"

# Rebuild training service
docker-compose build training
docker-compose run training
```

### NiFi Flow Not Starting

Access NiFi UI at http://localhost:8080 and verify:
1. Processor is running
2. Kafka connection is configured
3. FlowFiles are being generated

### Port Conflicts

If ports are already in use:
```bash
# Check what's using the port
sudo lsof -i :8080
sudo lsof -i :9092
sudo lsof -i :5000
```

---

## Stopping Services

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

## Extending the Project

### Adding New Data Sources

To add new data sources:

1. **Use NiFi** (http://localhost:8080) for data ingestion
2. **Create a new producer service** in `services/`
3. **Use Kafka CLI** to produce messages:

```bash
docker exec -it kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic orders
```

### Adding More Models

1. Modify [`services/training_service/train.py`](services/training_service/train.py)
2. Change `registered_model_name` parameter
3. Update [`services/inference_service/inference.py`](services/inference_service/inference.py) to load the new model

### Adding Alert Integrations

Modify [`services/alert_service/alert.py`](services/alert_service/alert.py) to:
- Send emails
- Post to Slack
- Trigger webhooks
- Write to database

---

## File Structure

```
mlops-poc/
├── docker-compose.yml              # Main orchestration file
├── docs.txt                       # Setup notes
├── docs/
│   └── README.md                  # This documentation
├── registry/
│   ├── database/                  # NiFi Registry database
│   └── flow_storage/              # NiFi Registry flow storage
├── services/
│   ├── training_service/
│   │   ├── train.py               # Training script
│   │   ├── requirements.txt       # Python dependencies
│   │   └── Dockerfile             # Container image
│   ├── inference_service/
│   │   ├── inference.py           # Inference script
│   │   ├── requirements.txt       # Python dependencies
│   │   └── Dockerfile             # Container image
│   └── alert_service/
│       ├── alert.py               # Alert consumption script
│       ├── requirements.txt       # Python dependencies
│       └── Dockerfile             # Container image
└── data/                          # Data directory (empty)
```

---

## License

This project is provided as a proof-of-concept for educational purposes.

---

## References

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache NiFi Documentation](https://nifi.apache.org/docs.html)
- [scikit-learn Documentation](https://scikit-learn.org/stable/documentation.html)
