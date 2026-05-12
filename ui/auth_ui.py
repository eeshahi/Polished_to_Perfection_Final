import uuid
from datetime import datetime
import streamlit as st


def render_auth_page(service):
    st.title("Polished to Perfection")
    st.caption("Salon Management System")
    st.info("Welcome! Create an account or log in to manage appointments, rewards, feedback, revenue, and inventory.")
    st.divider()

    register_tab, login_tab = st.tabs(["Register", "Login"])

    with register_tab:
        render_register(service)

    with login_tab:
        render_login(service)


def render_register(service):
    st.subheader("Create Account")

    reg_email = st.text_input("Email", key="reg_email").strip().lower()
    reg_name = st.text_input("Full Name", key="reg_name").strip()
    reg_password = st.text_input("Password", type="password", key="reg_password")
    reg_role = st.selectbox("Role", ["Customer", "Employee"], key="reg_role")

    if st.button("Create Account", key="create_account_btn", type="primary", use_container_width=True):
        if not reg_email or not reg_name or not reg_password:
            st.error("Please fill in all fields.")
        elif "@" not in reg_email or "." not in reg_email:
            st.error("Please enter a valid email address.")
        elif len(reg_password) < 6:
            st.error("Password must be at least 6 characters long.")
        elif email_exists(service, reg_email):
            st.error("An account with that email already exists.")
        else:
            new_user = {
                "id": str(uuid.uuid4()),
                "email": reg_email,
                "full_name": reg_name,
                "password": reg_password,
                "role": reg_role,
                "registered_at": str(datetime.now()),
                "reward_points": 0,
                "reward_history": [],
            }

            service.store.users.append(new_user)
            service.store.save_users()

            st.success("Account created successfully. You can now log in.")


def render_login(service):
    st.subheader("Login")

    login_email = st.text_input("Email", key="login_email").strip().lower()
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log In", key="login_btn", type="primary", use_container_width=True):
        user_found = None

        for user in service.store.users:
            if user["email"].lower() == login_email and user["password"] == login_password:
                user_found = user
                break

        if user_found:
            st.session_state["logged_in"] = True
            st.session_state["user"] = user_found
            st.session_state["role"] = user_found["role"]
            st.session_state["page"] = "dashboard"
            st.session_state["messages"] = []

            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials.")


def email_exists(service, email):
    for user in service.store.users:
        if user["email"].lower() == email.lower():
            return True
    return False