import streamlit as st


def render_sidebar(service):
    if not st.session_state["logged_in"]:
        return

    refresh_logged_in_user(service)

    with st.sidebar:
        st.markdown("## Polished to Perfection")
        st.caption("Salon Management System")
        st.info("Book appointments, manage rewards, track revenue, and manage salon feedback.")

        st.write(f"Logged in as: {st.session_state['user']['full_name']}")
        st.write(f"Role: {st.session_state['role']}")

        st.divider()

        if st.session_state["role"] == "Customer":
            customer_nav_button("Customer Dashboard", "dashboard", "customer_dashboard_btn")
            customer_nav_button("Book Appointment", "book_appointment", "book_appointment_btn")
            customer_nav_button("My Appointments", "my_appointments", "my_appointments_btn")
            customer_nav_button("Rewards", "rewards", "rewards_btn")
            customer_nav_button("Feedback Form", "feedback_form", "feedback_form_btn")
            customer_nav_button("Penny the Polish Pro", "penny_chat", "penny_chat_btn")

        elif st.session_state["role"] == "Employee":
            customer_nav_button("Employee Dashboard", "dashboard", "employee_dashboard_btn")
            customer_nav_button("Manage Appointments", "manage_appointments", "manage_appointments_btn")
            customer_nav_button("Inventory", "inventory", "inventory_btn")
            customer_nav_button("Low Stock Alerts", "low_stock", "low_stock_btn")
            customer_nav_button("Manage Services", "manage_services", "manage_services_btn")
            customer_nav_button("Revenue Tracker", "revenue_tracker", "revenue_tracker_btn")
            customer_nav_button("Review Feedback", "review_feedback", "review_feedback_btn")

        st.divider()

        if st.button("Logout", key="logout_btn", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.session_state["page"] = "dashboard"
            st.session_state["selected_appointment_id"] = None
            st.session_state["restock_item_id"] = None
            st.session_state["messages"] = []
            st.rerun()


def customer_nav_button(label, page, key):
    if st.button(label, key=key, type="primary", use_container_width=True):
        st.session_state["page"] = page
        st.rerun()


def refresh_logged_in_user(service):
    if st.session_state["user"] is not None:
        for user in service.store.users:
            if user["id"] == st.session_state["user"]["id"]:
                st.session_state["user"] = user
                break