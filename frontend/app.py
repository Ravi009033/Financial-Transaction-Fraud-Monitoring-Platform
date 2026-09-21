import streamlit as st


st.set_page_config(
    page_title="Fraud Monitoring Platform",
    page_icon="🔐",
    layout="wide",
)


st.title("🔐 Fraud Monitoring Platform")

st.write(
    "Fraud detection, transaction monitoring, "
    "and machine learning analytics."
)


if "token" not in st.session_state:
    st.session_state.token = None


if st.session_state.token:

    st.success(
        "You are logged in. "
        "Use the Dashboard page from the sidebar."
    )

else:

    st.info(
        "Please open the Login page from the sidebar."
    )