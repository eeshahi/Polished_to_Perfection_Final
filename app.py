import streamlit as st

from data.salon_store import SalonStore
from services.salon_service import SalonService
from ui.auth_ui import render_auth_page
from ui.sidebar_ui import render_sidebar
from ui.customer_ui import render_customer_pages
from ui.employee_ui import render_employee_pages



# -----------------------------
# Session State
# -----------------------------
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if "role" not in st.session_state:
        st.session_state["role"] = None

    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard"

    if "selected_appointment_id" not in st.session_state:
        st.session_state["selected_appointment_id"] = None

    if "restock_item_id" not in st.session_state:
        st.session_state["restock_item_id"] = None

    if "appointment_status_filter" not in st.session_state:
        st.session_state["appointment_status_filter"] = "All"

    if "customer_history_filter" not in st.session_state:
        st.session_state["customer_history_filter"] = "All"

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

def main():
    st.set_page_config(
        page_title="Polished to Perfection",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    store = SalonStore()
    service = SalonService(store)

    render_sidebar(service)

    if not st.session_state["logged_in"]:
        render_auth_page(service)

    elif st.session_state["role"] == "Customer":
        render_customer_pages(service)

    elif st.session_state["role"] == "Employee":
        render_employee_pages(service)

main()