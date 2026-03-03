import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# Set tracking URI
mlflow.set_tracking_uri("http://mlflow:5000")

# Dummy dataset
data = pd.DataFrame({
    "amount": [100, 2000, 150, 5000, 7000, 300],
    "country": ["US", "IN", "US", "US", "IN", "US"],
    "device": ["mobile", "desktop", "mobile", "desktop", "mobile", "desktop"],
    "fraud": [0, 1, 0, 1, 1, 0]
})

X = data[["amount", "country", "device"]]
y = data["fraud"]

# Preprocessing
categorical_features = ["country", "device"]
numeric_features = ["amount"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ],
    remainder="passthrough"
)

# Full pipeline
pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", RandomForestClassifier())
])

# Train
pipeline.fit(X, y)

# Log to MLflow
with mlflow.start_run():
    mlflow.sklearn.log_model(
        pipeline,
        artifact_path="model",
        registered_model_name="fraud_model"
    )

print("Model trained and registered successfully.")