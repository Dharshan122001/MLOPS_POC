import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fraud Monitoring Dashboard", layout="wide")

st.title("🚨 Real-Time Fraud Detection Dashboard")



# PostgreSQL connection
DATABASE_URL = "postgresql://neondb_owner:npg_hKGuPYZ2cl5O@ep-falling-leaf-aiscvw2e-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)

# Load transactions
df = pd.read_sql(
    "SELECT * FROM fraud_transactions ORDER BY created_at DESC LIMIT 500",
    engine
)

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------

st.sidebar.header("Filters")

prediction_filter = st.sidebar.selectbox(
    "Transaction Type",
    ["All", "Fraud Only", "Genuine Only"]
)

device_filter = st.sidebar.multiselect(
    "Device",
    df["device"].unique()
)

country_filter = st.sidebar.multiselect(
    "Country",
    df["country"].unique()
)

# ----------------------------
# APPLY FILTERS
# ----------------------------

filtered_df = df.copy()

if prediction_filter == "Fraud Only":
    filtered_df = filtered_df[filtered_df["prediction"] == 1]

elif prediction_filter == "Genuine Only":
    filtered_df = filtered_df[filtered_df["prediction"] == 0]

if device_filter:
    filtered_df = filtered_df[filtered_df["device"].isin(device_filter)]

if country_filter:
    filtered_df = filtered_df[filtered_df["country"].isin(country_filter)]

# ----------------------------
# METRICS
# ----------------------------

total_transactions = len(filtered_df)
fraud_count = len(filtered_df[filtered_df["prediction"] == 1])
genuine_count = len(filtered_df[filtered_df["prediction"] == 0])

fraud_rate = 0
if total_transactions > 0:
    fraud_rate = (fraud_count / total_transactions) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Transactions", total_transactions)
col2.metric("Fraud Transactions", fraud_count)
col3.metric("Genuine Transactions", genuine_count)
col4.metric("Fraud Rate", f"{fraud_rate:.2f}%")

st.divider()

# ----------------------------
# CHARTS
# ----------------------------

col1, col2, col3 = st.columns(3)

# Fraud vs Genuine Pie
with col1:
    st.subheader("Fraud vs Genuine")

    labels = ["Fraud", "Genuine"]
    values = [fraud_count, genuine_count]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%')
    ax.axis("equal")

    st.pyplot(fig)

# Device chart
with col2:
    st.subheader("Transactions by Device")

    device_stats = filtered_df["device"].value_counts()

    st.bar_chart(device_stats)

# Country chart
with col3:
    st.subheader("Transactions by Country")

    country_stats = filtered_df["country"].value_counts()

    st.bar_chart(country_stats)

st.divider()

# ----------------------------
# FRAUD TABLE
# ----------------------------

st.subheader("🚨 Fraud Transactions")

fraud_df = filtered_df[filtered_df["prediction"] == 1]

st.dataframe(
    fraud_df,
    use_container_width=True
)

st.divider()
