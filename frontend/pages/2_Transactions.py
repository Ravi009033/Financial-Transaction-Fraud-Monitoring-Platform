import pandas as pd
import streamlit as st

from api_client import APIClient


st.set_page_config(
    page_title="Transactions | Fraud Monitoring",
    page_icon="💳",
    layout="wide",
)


st.title("💳 Transactions")


if (
    "token" not in st.session_state
    or not st.session_state.token
):
    st.warning("Please login first.")
    st.stop()


client = APIClient(
    token=st.session_state.token
)


# --------------------------------
# Filters
# --------------------------------

col1, col2, col3 = st.columns(
    [2, 2, 1]
)


with col1:

    status = st.selectbox(
        "Transaction Status",
        [
            "All",
            "approved",
            "review",
            "blocked",
            "pending",
        ],
    )


with col2:

    page_size = st.selectbox(
        "Transactions per page",
        [10, 20, 50],
        index=0,
    )


with col3:

    st.write("")
    st.write("")

    refresh = st.button(
        "🔄 Refresh",
        use_container_width=True,
    )


if refresh:
    st.rerun()


# --------------------------------
# Pagination
# --------------------------------

if "transaction_page" not in st.session_state:
    st.session_state.transaction_page = 1


page = st.session_state.transaction_page


# --------------------------------
# API Request
# --------------------------------

try:

    endpoint = (
        f"/transactions/"
        f"?page={page}"
        f"&page_size={page_size}"
    )

    if status != "All":
        endpoint += f"&status={status}"

    response = client.get(endpoint)

except Exception as exc:

    st.error(
        f"Unable to load transactions: {exc}"
    )

    st.stop()


transactions = response.get(
    "items",
    []
)

total = response.get(
    "total",
    0,
)

total_pages = response.get(
    "total_pages",
    1,
)


# --------------------------------
# Summary
# --------------------------------

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Transactions",
    total,
)

col2.metric(
    "Current Page",
    f"{page} / {total_pages}",
)

col3.metric(
    "Page Size",
    page_size,
)


# --------------------------------
# Transaction Table
# --------------------------------

st.subheader("Transaction Records")


if not transactions:

    st.info(
        "No transactions found for the selected filter."
    )

else:

    df = pd.DataFrame(transactions)

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
        "model_version",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in df.columns
    ]

    df = df[available_columns].copy()

    if "id" in df.columns:
        df["id"] = (
            df["id"]
            .astype(str)
            .str[:8]
            + "..."
        )

    if "amount" in df.columns:

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce",
        ).map(
            lambda x: (
                f"₹{x:,.2f}"
                if pd.notna(x)
                else ""
            )
        )

    if "fraud_score" in df.columns:

        df["fraud_score"] = pd.to_numeric(
            df["fraud_score"],
            errors="coerce",
        ).map(
            lambda x: (
                f"{x:.4f}"
                if pd.notna(x)
                else ""
            )
        )

    if "timestamp" in df.columns:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
        ).dt.strftime(
            "%Y-%m-%d %H:%M"
        )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------
# Pagination controls
# --------------------------------

st.divider()

previous_col, page_col, next_col = st.columns(
    [1, 2, 1]
)


with previous_col:

    if st.button(
        "← Previous",
        disabled=page <= 1,
        use_container_width=True,
    ):

        st.session_state.transaction_page -= 1
        st.rerun()


with page_col:

    st.markdown(
        f"<div style='text-align:center'>"
        f"Page <b>{page}</b> of <b>{total_pages}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )


with next_col:

    if st.button(
        "Next →",
        disabled=page >= total_pages,
        use_container_width=True,
    ):

        st.session_state.transaction_page += 1
        st.rerun()