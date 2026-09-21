import streamlit as st

from api_client import APIClient


st.set_page_config(
    page_title="Login | Fraud Monitoring",
    page_icon="🔐",
    layout="centered",
)


st.title("🔐 Fraud Monitoring Platform")
st.subheader("Login")


if "token" not in st.session_state:
    st.session_state.token = None


if st.session_state.token:
    st.success("You are already logged in.")

    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()

    st.stop()


with st.form("login_form"):

    email = st.text_input(
        "Email",
        placeholder="Enter your email",
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
    )

    submitted = st.form_submit_button(
        "Login",
        use_container_width=True,
    )


if submitted:

    if not email or not password:
        st.error("Please enter email and password.")
        st.stop()

    client = APIClient()

    try:

        result = client.login(
            email=email,
            password=password,
        )

        st.session_state.token = result["access_token"]

        st.success("Login successful!")

        st.rerun()

    except Exception as exc:

        st.error(
            f"Login failed: {exc}"
        )