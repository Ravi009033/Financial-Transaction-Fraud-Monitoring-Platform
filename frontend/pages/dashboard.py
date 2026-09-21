import streamlit as st
import pandas as pd
from api_client import APIClient


st.set_page_config(
    page_title="Dashboard | Fraud Monitoring",
    page_icon="📊",
    layout="wide",
)


st.title("📊 Fraud Monitoring Dashboard")


if "token" not in st.session_state or not st.session_state.token:

    st.warning(
        "Please login before accessing the dashboard."
    )

    st.stop()


client = APIClient(
    token=st.session_state.token
)


try:

    summary = client.get(
        "/dashboard/summary"
    )

    trends = client.get(
        "/dashboard/transaction-trends"
    )

    distribution = client.get(
        "/dashboard/fraud-distribution"
    )

except Exception as exc:

    st.error(
        f"Unable to load dashboard: {exc}"
    )

    st.stop()


# -----------------------------
# KPI Cards
# -----------------------------

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Total Transactions",
    summary["total_transactions"],
)


col2.metric(
    "Total Amount",
    f"₹{float(summary['total_amount']):,.2f}",
)


col3.metric(
    "Suspicious Transactions",
    summary["fraud_transactions"],
)


col4.metric(
    "Suspicious Rate",
    f"{summary['fraud_rate']:.2f}%",
)


st.divider()


# -----------------------------
# Transaction Status
# -----------------------------

st.subheader("Transaction Status")


status_col1, status_col2, status_col3, status_col4 = st.columns(4)


status_col1.metric(
    "Approved",
    summary["approved_transactions"],
)


status_col2.metric(
    "Review",
    summary["review_transactions"],
)


status_col3.metric(
    "Blocked",
    summary["blocked_transactions"],
)


status_col4.metric(
    "Pending",
    summary["pending_transactions"],
)


st.divider()


# -----------------------------
# Transaction Trends
# -----------------------------

st.subheader("Transaction Trends")


trend_data = trends.get("data", [])


if trend_data:

    import pandas as pd

    trend_df = pd.DataFrame(trend_data)

    trend_df["date"] = pd.to_datetime(
        trend_df["date"]
    )

    trend_df = trend_df.set_index("date")

    st.line_chart(
        trend_df[["transactions"]]
    )

    st.subheader("Transaction Amount")

    st.bar_chart(
        trend_df[["amount"]]
    )

else:

    st.info(
        "No transaction trend data available."
    )


# -----------------------------
# Fraud Distribution
# -----------------------------

st.subheader("Transaction Status Distribution")


distribution_data = distribution.get(
    "data",
    []
)


if distribution_data:

    distribution_df = pd.DataFrame(
        distribution_data
    )

    distribution_df = distribution_df.set_index(
        "status"
    )

    st.bar_chart(
        distribution_df[["count"]]
    )

else:

    st.info(
        "No transaction distribution data available."
    )

# -----------------------------
# Recent Transactions
# -----------------------------

st.divider()

st.subheader("Recent Transactions")

try:
    transaction_response = client.get(
        "/transactions/?page=1&page_size=10"
    )

    transactions = transaction_response.get(
        "items",
        []
    )

except Exception as exc:

    st.error(
        f"Unable to load recent transactions: {exc}"
    )

    transactions = []


if transactions:

    transaction_df = pd.DataFrame(
        transactions
    )

    # Keep the dashboard table focused on
    # the most useful monitoring fields.
    display_columns = [
        "id",
        "amount",
        "merchant",
        "location",
        "transaction_type",
        "timestamp",
        "status",
        "fraud_score",
        "fraud_decision",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in transaction_df.columns
    ]

    transaction_df = transaction_df[
        available_columns
    ].copy()

    # Format timestamp for readability.
    if "timestamp" in transaction_df.columns:

        transaction_df["timestamp"] = pd.to_datetime(
            transaction_df["timestamp"],
            errors="coerce",
        ).dt.strftime(
            "%Y-%m-%d %H:%M"
        )

    # Format amount.
    if "amount" in transaction_df.columns:

        transaction_df["amount"] = pd.to_numeric(
            transaction_df["amount"],
            errors="coerce",
        ).map(
            lambda value: (
                f"₹{value:,.2f}"
                if pd.notna(value)
                else ""
            )
        )

    # Format fraud score.
    if "fraud_score" in transaction_df.columns:

        transaction_df["fraud_score"] = pd.to_numeric(
            transaction_df["fraud_score"],
            errors="coerce",
        ).map(
            lambda value: (
                f"{value:.4f}"
                if pd.notna(value)
                else ""
            )
        )

    # Don't expose the full UUID in the dashboard.
    if "id" in transaction_df.columns:

        transaction_df["id"] = (
            transaction_df["id"]
            .astype(str)
            .str[:8]
            + "..."
        )

    st.dataframe(
        transaction_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No transactions available."
    )