from datetime import datetime, date
import streamlit as st


def render_employee_pages(service):
    if st.session_state["page"] == "dashboard":
        render_employee_dashboard(service)

    elif st.session_state["page"] == "manage_appointments":
        render_manage_appointments(service)

    elif st.session_state["page"] == "inventory":
        render_inventory(service)

    elif st.session_state["page"] == "low_stock":
        render_low_stock(service)

    elif st.session_state["page"] == "manage_services":
        render_manage_services(service)

    elif st.session_state["page"] == "revenue_tracker":
        render_revenue_tracker(service)

    elif st.session_state["page"] == "review_feedback":
        render_review_feedback(service)


def get_employee_total_charge_with_tips(service, employee_name):
    total = 0

    for appt in service.get_completed_appointments():
        if appt.get("employee") == employee_name:
            total += service.get_appointment_total_charge(appt)

    return round(total, 2)


def render_employee_dashboard(service):
    employee_name = st.session_state["user"]["full_name"]
    employee_appts = service.get_employee_appointments(employee_name)

    todays_appointments = 0
    scheduled_appointments = 0
    completed_appointments = 0

    for appt in employee_appts:
        if appt["date"] == str(date.today()) and appt.get("status") != "Canceled":
            todays_appointments += 1

        if appt.get("status") == "Scheduled":
            scheduled_appointments += 1

        if appt.get("status") == "Completed":
            completed_appointments += 1

    low_stock_count = service.get_low_stock_count()
    employee_total_charge = get_employee_total_charge_with_tips(service, employee_name)

    pending_feedback_count = 0

    for feedback in service.store.feedback_list:
        if feedback.get("status") == "Pending":
            pending_feedback_count += 1

    st.title("Polished to Perfection")
    st.subheader("Employee Dashboard")
    st.divider()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        with st.container(border=True):
            st.success("Today's Appointments")
            st.markdown(f"### {todays_appointments}")
            st.caption("Scheduled today")

    with col2:
        with st.container(border=True):
            st.info("Scheduled")
            st.markdown(f"### {scheduled_appointments}")
            st.caption("Upcoming")

    with col3:
        with st.container(border=True):
            st.error("Completed")
            st.markdown(f"### {completed_appointments}")
            st.caption("Finished")

    with col4:
        with st.container(border=True):
            st.warning("Low Stock")
            st.markdown(f"### {low_stock_count}")
            st.caption("Items to restock")

    with col5:
        with st.container(border=True):
            st.success("Total Made")
            st.markdown(f"### ${employee_total_charge}")
            st.caption("Your services + tips")

    st.divider()

    col1, col2, col3 = st.columns([3, 2, 2])

    with col1:
        with st.container(border=True):
            st.markdown("### Assigned Appointments")

            active_employee_appts = []

            for appt in employee_appts:
                if appt.get("status") not in ["Completed", "Canceled"]:
                    active_employee_appts.append(appt)

            if len(active_employee_appts) > 0:
                for appt in active_employee_appts:
                    st.markdown(
                        f"**{appt['client']}** | {appt['service']} | {appt['date']} at {appt['time']} | {appt.get('status', 'Scheduled')}"
                    )
            else:
                st.info("No active appointments assigned yet.")

    with col2:
        with st.container(border=True):
            st.markdown("### Inventory Alerts")

            if low_stock_count > 0:
                for item in service.store.inventory:
                    if item["quantity"] <= item["low_stock_limit"]:
                        st.warning(f"{item['item_name']} is low on stock")
            else:
                st.success("No low stock items right now.")

    with col3:
        with st.container(border=True):
            st.markdown("### Feedback Alerts")
            st.warning(f"Pending Feedback: {pending_feedback_count}")

            if st.button("Review Feedback", key="dashboard_review_feedback_btn", type="primary", use_container_width=True):
                st.session_state["page"] = "review_feedback"
                st.rerun()


def render_manage_appointments(service):
    employee_name = st.session_state["user"]["full_name"]
    employee_appts = service.get_employee_appointments(employee_name)

    st.title("Manage Appointments")
    st.caption("Search, review, and update appointment statuses.")
    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        with st.container(border=True):
            search_name = st.text_input("Search by client name", key="appt_search_name")

        with st.container(border=True):
            status_filter = st.selectbox(
                "Status",
                ["All", "Scheduled", "Completed", "Canceled"],
                key="appointment_status_filter_box",
            )

            st.session_state["appointment_status_filter"] = status_filter

        filtered_appts = []

        for appt in employee_appts:
            matches_search = search_name.lower() in appt.get("client", "").lower()

            matches_status = (
                st.session_state["appointment_status_filter"] == "All"
                or appt.get("status", "Scheduled") == st.session_state["appointment_status_filter"]
            )

            if matches_search and matches_status:
                filtered_appts.append(appt)

        with st.container(border=True):
            st.markdown("### Appointment List")

            if len(filtered_appts) > 0:
                appointment_table = []

                for appt in filtered_appts:
                    appointment_table.append(
                        {
                            "Client": appt.get("client", "Unknown"),
                            "Service": appt["service"],
                            "Date": appt["date"],
                            "Time": appt["time"],
                            "Status": appt.get("status", "Scheduled"),
                            "Basic Charge": service.get_appointment_basic_charge(appt),
                            "20% Tip": service.get_appointment_tip(appt),
                            "Total Charge": service.get_appointment_total_charge(appt),
                        }
                    )

                st.dataframe(appointment_table, use_container_width=True)

                selected_appt_from_box = st.selectbox(
                    "Select Appointment",
                    filtered_appts,
                    format_func=lambda x: f"{x.get('client', 'Unknown')} | {x['service']} | {x['date']} {x['time']}",
                    key="manage_appt_selectbox",
                )

                if selected_appt_from_box:
                    st.session_state["selected_appointment_id"] = selected_appt_from_box["id"]

            else:
                st.info("No appointments assigned to you yet.")

    with col2:
        with st.container(border=True):
            st.markdown("### Appointment Details")

            selected_appt = None

            for appt in employee_appts:
                if appt["id"] == st.session_state["selected_appointment_id"]:
                    selected_appt = appt
                    break

            if selected_appt:
                st.markdown(f"**Client:** {selected_appt.get('client', 'Unknown')}")
                st.markdown(f"**Client Email:** {selected_appt.get('client_email', 'N/A')}")
                st.markdown(f"**Service:** {selected_appt['service']}")
                st.markdown(f"**Basic Charge:** ${service.get_appointment_basic_charge(selected_appt)}")
                st.markdown(f"**20% Tip:** ${service.get_appointment_tip(selected_appt)}")
                st.markdown(f"**Total Charge:** ${service.get_appointment_total_charge(selected_appt)}")
                st.markdown(f"**Date:** {selected_appt['date']}")
                st.markdown(f"**Time:** {selected_appt['time']}")
                st.markdown(f"**Status:** {selected_appt.get('status', 'Scheduled')}")

                status_options = ["Scheduled", "Completed", "Canceled"]
                current_status = selected_appt.get("status", "Scheduled")

                if current_status in status_options:
                    current_status_index = status_options.index(current_status)
                else:
                    current_status_index = 0

                selected_status = st.radio(
                    "Update Status",
                    status_options,
                    index=current_status_index,
                    key=f"status_radio_{selected_appt['id']}",
                )

                if st.button("Record Decision", key=f"save_status_{selected_appt['id']}", type="primary", use_container_width=True):
                    for appt in service.store.appointments:
                        if appt["id"] == selected_appt["id"]:
                            old_status = appt.get("status", "Scheduled")

                            if old_status != "Canceled" and selected_status == "Canceled":
                                service.update_inventory_for_service(appt["service"], "add")
                                appt["canceled_at"] = str(datetime.now())

                            if old_status == "Canceled" and selected_status in ["Scheduled", "Completed"]:
                                inventory_success = service.update_inventory_for_service(appt["service"], "subtract")

                                if not inventory_success:
                                    st.error("Not enough inventory to move this appointment back.")
                                    st.stop()

                            if selected_status == "Completed" and not appt.get("points_awarded", False):
                                service.add_reward_points_to_customer(appt["client_email"], 10)
                                appt["points_awarded"] = True

                            if "tip_amount" not in appt:
                                appt["tip_amount"] = service.calculate_tip(appt.get("price", 0))

                            if "total_charge" not in appt:
                                appt["total_charge"] = service.calculate_total_charge(appt.get("price", 0))

                            appt["status"] = selected_status
                            break

                    service.store.save_appointments()
                    service.store.save_inventory()

                    st.success("Information recorded.")
                    st.rerun()

            else:
                st.info("Select an appointment to view details.")


def render_inventory(service):
    st.title("Salon Inventory")
    st.caption("View current stock and restock items.")
    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        with st.container(border=True):
            inventory_table = []

            for item in service.store.inventory:
                inventory_table.append(
                    {
                        "Item": item["item_name"],
                        "Category": item["category"],
                        "Quantity": item["quantity"],
                        "Low Stock Limit": item["low_stock_limit"],
                    }
                )

            if len(inventory_table) > 0:
                st.dataframe(inventory_table, use_container_width=True)

                selected_inventory_item = st.selectbox(
                    "Select Inventory Item",
                    service.store.inventory,
                    format_func=lambda x: f"{x['item_name']} | Qty: {x['quantity']}",
                    key="inventory_selectbox",
                )

                if selected_inventory_item:
                    st.session_state["restock_item_id"] = selected_inventory_item["id"]

            else:
                st.info("No inventory items available.")

    with col2:
        with st.container(border=True):
            st.markdown("### Restock Item")

            selected_item = None

            for item in service.store.inventory:
                if item["id"] == st.session_state["restock_item_id"]:
                    selected_item = item
                    break

            if selected_item:
                st.markdown(f"**Item:** {selected_item['item_name']}")
                st.markdown(f"**Current Quantity:** {selected_item['quantity']}")
                st.markdown(f"**Supplier:** {selected_item['supplier']}")

                restock_amount = st.number_input(
                    "Amount to Add",
                    min_value=1,
                    step=1,
                    key="restock_amount_input",
                )

                if st.button("Save Restock", key=f"save_restock_{selected_item['id']}", type="primary", use_container_width=True):
                    selected_item["quantity"] += restock_amount
                    service.store.save_inventory()

                    st.success("Inventory updated successfully.")
                    st.session_state["restock_item_id"] = None
                    st.rerun()

            else:
                st.info("Select an inventory item to restock.")


def render_low_stock(service):
    st.title("Low Stock Alerts")
    st.caption("See which salon items need to be restocked soon.")
    st.divider()

    low_stock_items = []

    for item in service.store.inventory:
        if item["quantity"] <= item["low_stock_limit"]:
            low_stock_items.append(item)

    if len(low_stock_items) > 0:
        for item in low_stock_items:
            with st.container(border=True):
                st.markdown(f"**Item:** {item['item_name']}")
                st.markdown(f"**Quantity:** {item['quantity']}")
                st.markdown(f"**Low Stock Limit:** {item['low_stock_limit']}")
                st.markdown(f"**Supplier:** {item['supplier']}")
                st.warning(f"{item['item_name']} needs to be restocked soon.")
    else:
        st.success("There are no low stock items right now.")


def render_manage_services(service):
    st.title("Manage Services")
    st.caption("Add new services, remove services, and update service prices.")
    st.divider()

    add_tab, update_tab, remove_tab = st.tabs(["Add Service", "Change Price", "Remove Service"])

    with add_tab:
        st.subheader("Add a New Service")

        new_service_name = st.text_input("Service Name", key="new_service_name").strip()

        new_service_price = st.number_input(
            "Service Price",
            min_value=1.0,
            step=1.0,
            key="new_service_price",
        )

        if st.button("Add Service", key="add_service_btn", type="primary", use_container_width=True):
            service_exists = False

            for salon_service in service.store.services:
                if salon_service["name"].lower() == new_service_name.lower():
                    service_exists = True
                    break

            if not new_service_name:
                st.error("Please enter a service name.")

            elif service_exists:
                st.error("This service already exists.")

            else:
                new_service = {
                    "name": new_service_name,
                    "price": new_service_price,
                }

                service.store.services.append(new_service)
                service.store.save_services()

                st.success("Service added successfully.")
                st.rerun()

    with update_tab:
        st.subheader("Change Service Price")

        if len(service.store.services) > 0:
            service_to_update = st.selectbox(
                "Choose Service",
                service.store.services,
                format_func=lambda x: f"{x['name']} - ${x['price']}",
                key="service_to_update",
            )

            updated_price = st.number_input(
                "New Price",
                min_value=1.0,
                step=1.0,
                value=float(service_to_update["price"]),
                key="updated_service_price",
            )

            if st.button("Update Price", key="update_service_price_btn", type="primary", use_container_width=True):
                for salon_service in service.store.services:
                    if salon_service["name"] == service_to_update["name"]:
                        salon_service["price"] = updated_price
                        break

                service.store.save_services()

                st.success("Service price updated successfully.")
                st.rerun()

        else:
            st.info("No services available to update.")

    with remove_tab:
        st.subheader("Remove a Service")

        if len(service.store.services) > 0:
            service_to_remove = st.selectbox(
                "Choose Service to Remove",
                service.store.services,
                format_func=lambda x: f"{x['name']} - ${x['price']}",
                key="service_to_remove",
            )

            service_has_existing_appointments = False

            for appt in service.store.appointments:
                if appt.get("service") == service_to_remove["name"]:
                    service_has_existing_appointments = True
                    break

            st.warning("Removing a service will stop customers from booking it in the future.")

            if service_has_existing_appointments:
                st.info("This service already has appointment history, but removing it will not delete old appointments.")

            if st.button("Remove Service", key="remove_service_btn", type="primary", use_container_width=True):
                service.store.services.remove(service_to_remove)
                service.store.save_services()

                st.success("Service removed successfully.")
                st.rerun()

        else:
            st.info("No services available to remove.")

    st.divider()
    st.markdown("### Current Services")

    if len(service.store.services) > 0:
        services_table = []

        for salon_service in service.store.services:
            services_table.append(
                {
                    "Service": salon_service["name"],
                    "Price": salon_service["price"],
                }
            )

        st.dataframe(services_table, use_container_width=True)

    else:
        st.info("No services have been added yet.")


def render_revenue_tracker(service):
    st.title("Revenue Tracker")
    st.caption("Track basic service revenue, tips, and total revenue from completed appointments.")
    st.divider()

    completed_appts = service.get_completed_appointments()

    st.markdown("### Filters")

    employee_options = ["All Employees"] + sorted(
        list(set([appt.get("employee", "Unknown") for appt in completed_appts]))
    )

    service_options = ["All Services"] + sorted(
        list(set([appt.get("service", "Unknown") for appt in completed_appts]))
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        employee_filter = st.selectbox(
            "Employee",
            employee_options,
            key="revenue_employee_filter",
        )

    with col2:
        service_filter = st.selectbox(
            "Service",
            service_options,
            key="revenue_service_filter",
        )

    with col3:
        date_filter = st.selectbox(
            "Date Filter",
            ["All Dates", "Today Only", "Past Dates Only"],
            key="revenue_date_filter",
        )

    filtered_revenue_appts = []

    for appt in completed_appts:
        matches_employee = (
            employee_filter == "All Employees"
            or appt.get("employee", "Unknown") == employee_filter
        )

        matches_service = (
            service_filter == "All Services"
            or appt.get("service", "Unknown") == service_filter
        )

        matches_date = True

        if date_filter == "Today Only":
            matches_date = appt.get("date") == str(date.today())

        elif date_filter == "Past Dates Only":
            matches_date = appt.get("date") < str(date.today())

        if matches_employee and matches_service and matches_date:
            filtered_revenue_appts.append(appt)

    basic_revenue = round(
        sum(service.get_appointment_basic_charge(appt) for appt in filtered_revenue_appts),
        2,
    )

    tip_revenue = round(
        sum(service.get_appointment_tip(appt) for appt in filtered_revenue_appts),
        2,
    )

    total_revenue = round(
        sum(service.get_appointment_total_charge(appt) for appt in filtered_revenue_appts),
        2,
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.info("Revenue from Basic Service")
            st.markdown(f"## ${basic_revenue}")
            st.caption("Service prices only")

    with col2:
        with st.container(border=True):
            st.success("Revenue from Tips")
            st.markdown(f"## ${tip_revenue}")
            st.caption("20% tips")

    with col3:
        with st.container(border=True):
            st.warning("Total Revenue")
            st.markdown(f"## ${total_revenue}")
            st.caption("Basic service revenue + tips")

    st.divider()
    st.markdown("### Completed Appointment Revenue")

    revenue_table = []

    for appt in filtered_revenue_appts:
        revenue_table.append(
            {
                "Client": appt.get("client", "Unknown"),
                "Employee": appt.get("employee", "Unknown"),
                "Service": appt.get("service", "Unknown"),
                "Date": appt.get("date", ""),
                "Time": appt.get("time", ""),
                "Basic Service Revenue": service.get_appointment_basic_charge(appt),
                "Tip Revenue": service.get_appointment_tip(appt),
                "Total Revenue": service.get_appointment_total_charge(appt),
            }
        )

    if len(revenue_table) > 0:
        st.dataframe(revenue_table, use_container_width=True)
    else:
        st.info("No completed appointment revenue found for these filters.")


def render_review_feedback(service):
    st.title("Review Feedback")
    st.caption("Review customer feedback and approve or reject submissions.")
    st.divider()

    feedback_status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Pending", "Approved", "Rejected"],
        key="feedback_status_filter",
    )

    filtered_feedback = []

    for feedback in service.store.feedback_list:
        matches_status = (
            feedback_status_filter == "All"
            or feedback.get("status") == feedback_status_filter
        )

        if matches_status:
            filtered_feedback.append(feedback)

    if len(filtered_feedback) > 0:
        for feedback in filtered_feedback:
            with st.container(border=True):
                st.markdown(f"### {feedback['feedback_type']}")
                st.markdown(f"**Customer:** {feedback['customer_name']}")
                st.markdown(f"**Email:** {feedback['customer_email']}")

                st.markdown(
                    f"**Appointment:** {feedback.get('related_service', 'N/A')} | "
                    f"{feedback.get('appointment_date', 'N/A')} at {feedback.get('appointment_time', 'N/A')}"
                )

                st.markdown(f"**Appointment Employee:** {feedback.get('appointment_employee', 'N/A')}")
                st.markdown(f"**Message:** {feedback['message']}")
                st.markdown(f"**Status:** {feedback['status']}")
                st.caption(f"Submitted at: {feedback['submitted_at']}")

                if feedback["status"] == "Pending":
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            "Approve",
                            key=f"approve_feedback_{feedback['id']}",
                            type="primary",
                            use_container_width=True,
                        ):
                            feedback["status"] = "Approved"
                            feedback["reviewed_by"] = st.session_state["user"]["full_name"]
                            feedback["reviewed_at"] = str(datetime.now())

                            service.store.save_feedback()

                            st.success("Feedback approved.")
                            st.rerun()

                    with col2:
                        if st.button(
                            "Reject",
                            key=f"reject_feedback_{feedback['id']}",
                            use_container_width=True,
                        ):
                            feedback["status"] = "Rejected"
                            feedback["reviewed_by"] = st.session_state["user"]["full_name"]
                            feedback["reviewed_at"] = str(datetime.now())

                            service.store.save_feedback()

                            st.warning("Feedback rejected.")
                            st.rerun()

                else:
                    st.info(
                        f"Reviewed by {feedback.get('reviewed_by', 'Unknown')} on {feedback.get('reviewed_at', '')}"
                    )

    else:
        st.info("No feedback found.")