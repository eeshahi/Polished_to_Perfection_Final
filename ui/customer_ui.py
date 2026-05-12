from datetime import datetime, date
import streamlit as st


def render_customer_pages(service):
    user = st.session_state["user"]
    user_appts = service.get_user_appointments(user["email"])

    if st.session_state["page"] == "dashboard":
        render_customer_dashboard(service, user_appts)

    elif st.session_state["page"] == "book_appointment":
        render_book_appointment(service)

    elif st.session_state["page"] == "my_appointments":
        render_my_appointments(service, user_appts)

    elif st.session_state["page"] == "rewards":
        render_rewards(service)

    elif st.session_state["page"] == "feedback_form":
        render_feedback_form(service, user_appts)

    elif st.session_state["page"] == "penny_chat":
        render_penny_chat(service)


def render_customer_dashboard(service, user_appts):
    upcoming_count = 0
    old_count = 0
    canceled_count = 0
    customer_feedback_count = 0

    for appt in user_appts:
        if appt.get("status") == "Canceled":
            canceled_count += 1
        elif appt.get("status") == "Completed":
            old_count += 1
        elif service.is_past_appointment(appt):
            old_count += 1
        else:
            upcoming_count += 1

    for feedback in service.store.feedback_list:
        if feedback.get("customer_email") == st.session_state["user"]["email"]:
            customer_feedback_count += 1

    reward_points = st.session_state["user"].get("reward_points", 0)

    st.title("Polished to Perfection")
    st.subheader("Customer Dashboard")
    st.divider()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        with st.container(border=True):
            st.success("Upcoming")
            st.markdown(f"### {upcoming_count}")
            st.caption("Scheduled")

    with col2:
        with st.container(border=True):
            st.info("Old")
            st.markdown(f"### {old_count}")
            st.caption("Past")

    with col3:
        with st.container(border=True):
            st.error("Canceled")
            st.markdown(f"### {canceled_count}")
            st.caption("Canceled visits")

    with col4:
        with st.container(border=True):
            st.warning("Rewards")
            st.markdown(f"### {reward_points}")
            st.caption("Reward points")

    with col5:
        with st.container(border=True):
            st.info("Feedback")
            st.markdown(f"### {customer_feedback_count}")
            st.caption("Submitted forms")

    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        with st.container(border=True):
            st.markdown("### Quick Overview")

            if len(user_appts) > 0:
                for appt in user_appts:
                    st.markdown(
                        f"**{appt['service']}** | {appt['date']} at {appt['time']} | {appt.get('status', 'Scheduled')}"
                    )
            else:
                st.info("No appointments found.")

    with col2:
        with st.container(border=True):
            st.markdown("### Customer Actions")
            st.write("Earn 10 points for every completed appointment.")
            st.write("A 20% tip is automatically added to every appointment.")
            st.write("Submit feedback or complaints using the feedback form.")
            st.write(f"Your current points: {reward_points}")

            if st.button("Open Feedback Form", key="dashboard_feedback_btn", type="primary", use_container_width=True):
                st.session_state["page"] = "feedback_form"
                st.rerun()


def render_book_appointment(service):
    service_prices = service.get_service_prices()

    st.title("Book Appointment")
    st.caption("Choose your service, nail tech, date, and time.")
    st.divider()

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        with st.container(border=True):
            if len(service_prices) == 0:
                st.error("There are no services available right now.")
            else:
                nail_service = st.selectbox("Service", list(service_prices.keys()), key="service_select")
                employee = st.selectbox("Employee Name", service.employee_names, key="employee_select")
                selected_date = st.date_input("Date", key="date_select")

                booked_times = []

                for appt in service.store.appointments:
                    if (
                        appt["employee"] == employee
                        and appt["date"] == str(selected_date)
                        and appt.get("status") != "Canceled"
                    ):
                        booked_times.append(appt["time"])

                available_times = []

                for appt_time in service.all_times:
                    if appt_time not in booked_times:
                        available_times.append(appt_time)

                if len(available_times) > 0:
                    selected_time = st.selectbox("Time", available_times, key="time_select")
                else:
                    selected_time = None
                    st.warning("No available times for this employee on this date.")

                basic_price = service_prices[nail_service]
                tip_amount = service.calculate_tip(basic_price)
                total_charge = service.calculate_total_charge(basic_price)

                st.success(f"Basic Charge: ${basic_price}")
                st.info(f"20% Tip: ${tip_amount}")
                st.warning(f"Total Charge: ${total_charge}")

                if st.button("Book Appointment", key="book_appointment_submit_btn", type="primary", use_container_width=True):
                    if selected_date < date.today():
                        st.error("You cannot book an appointment in the past.")

                    elif not selected_time:
                        st.error("Please choose a date with an available time.")

                    elif not service.has_inventory_for_service(nail_service):
                        st.error("Not enough inventory available to book this appointment.")

                    else:
                        new_appt = {
                            "id": service.get_next_appointment_id(),
                            "service": nail_service,
                            "price": basic_price,
                            "tip_amount": tip_amount,
                            "total_charge": total_charge,
                            "date": str(selected_date),
                            "time": selected_time,
                            "employee": employee,
                            "client": st.session_state["user"]["full_name"],
                            "client_email": st.session_state["user"]["email"],
                            "status": "Scheduled",
                            "created_at": str(datetime.now()),
                            "canceled_at": "",
                        }

                        subtract_success = service.update_inventory_for_service(nail_service, "subtract")

                        if subtract_success:
                            service.store.appointments.append(new_appt)
                            service.store.save_appointments()
                            service.store.save_inventory()

                            st.success("Appointment booked successfully.")
                            st.session_state["page"] = "my_appointments"
                            st.rerun()
                        else:
                            st.error("Inventory could not be updated for this appointment.")


def render_my_appointments(service, user_appts):
    st.title("My Appointments")
    st.caption("View upcoming, old, and canceled appointments.")
    st.divider()

    history_search = st.text_input("Search by service", key="customer_history_search")

    history_filter = st.selectbox(
        "Status",
        ["All", "Upcoming", "Old", "Canceled"],
        key="customer_history_filter_box",
    )

    st.session_state["customer_history_filter"] = history_filter

    upcoming_tab, old_tab, canceled_tab = st.tabs(["Upcoming", "Old", "Canceled"])

    with upcoming_tab:
        upcoming_appointments = []

        for appt in user_appts:
            matches_search = history_search.lower() in appt["service"].lower()
            is_upcoming = appt.get("status") not in ["Canceled", "Completed"] and not service.is_past_appointment(appt)
            matches_filter = st.session_state["customer_history_filter"] in ["All", "Upcoming"]

            if matches_search and is_upcoming and matches_filter:
                upcoming_appointments.append(appt)

        col1, col2 = st.columns([3, 2])

        with col1:
            with st.container(border=True):
                st.markdown("### Appointment List")

                if len(upcoming_appointments) > 0:
                    appointment_table = []

                    for appt in upcoming_appointments:
                        appointment_table.append(
                            {
                                "Service": appt["service"],
                                "Date": appt["date"],
                                "Time": appt["time"],
                                "Employee": appt["employee"],
                                "Status": appt.get("status", "Scheduled"),
                                "Basic Charge": service.get_appointment_basic_charge(appt),
                                "20% Tip": service.get_appointment_tip(appt),
                                "Total Charge": service.get_appointment_total_charge(appt),
                            }
                        )

                    st.dataframe(appointment_table, use_container_width=True)

                    selected_upcoming_appt = st.selectbox(
                        "Select Appointment",
                        upcoming_appointments,
                        format_func=lambda x: f"{x['service']} | {x['date']} {x['time']} | {x['employee']}",
                        key="customer_upcoming_selectbox",
                    )

                    if selected_upcoming_appt:
                        st.session_state["selected_appointment_id"] = selected_upcoming_appt["id"]

                else:
                    st.info("No upcoming appointments found.")

        with col2:
            with st.container(border=True):
                st.markdown("### Appointment Details")

                selected_appt = None

                for appt in upcoming_appointments:
                    if appt["id"] == st.session_state["selected_appointment_id"]:
                        selected_appt = appt
                        break

                if selected_appt:
                    st.markdown(f"**Service:** {selected_appt['service']}")
                    st.markdown(f"**Basic Charge:** ${service.get_appointment_basic_charge(selected_appt)}")
                    st.markdown(f"**20% Tip:** ${service.get_appointment_tip(selected_appt)}")
                    st.markdown(f"**Total Charge:** ${service.get_appointment_total_charge(selected_appt)}")
                    st.markdown(f"**Date:** {selected_appt['date']}")
                    st.markdown(f"**Time:** {selected_appt['time']}")
                    st.markdown(f"**Employee:** {selected_appt['employee']}")
                    st.markdown(f"**Status:** {selected_appt.get('status', 'Scheduled')}")

                    if service.is_past_appointment(selected_appt):
                        st.warning("This appointment has already passed and can no longer be canceled.")

                    else:
                        if st.button(
                            "Cancel Appointment",
                            key=f"cancel_appointment_{selected_appt['id']}",
                            type="primary",
                            use_container_width=True,
                        ):
                            for appt in service.store.appointments:
                                if appt["id"] == selected_appt["id"]:
                                    appt["status"] = "Canceled"
                                    appt["canceled_at"] = str(datetime.now())
                                    service.update_inventory_for_service(appt["service"], "add")
                                    break

                            service.store.save_appointments()
                            service.store.save_inventory()

                            st.success("Appointment canceled successfully.")
                            st.session_state["selected_appointment_id"] = None
                            st.rerun()

                else:
                    st.info("Select an appointment to view details.")

    with old_tab:
        old_appointments = []

        for appt in user_appts:
            matches_search = history_search.lower() in appt["service"].lower()
            is_old = appt.get("status") == "Completed" or (
                service.is_past_appointment(appt) and appt.get("status") != "Canceled"
            )
            matches_filter = st.session_state["customer_history_filter"] in ["All", "Old"]

            if matches_search and is_old and matches_filter:
                old_appointments.append(appt)

        if len(old_appointments) > 0:
            old_table = []

            for appt in old_appointments:
                display_status = appt.get("status", "Scheduled")

                if display_status == "Scheduled" and service.is_past_appointment(appt):
                    display_status = "Completed"

                old_table.append(
                    {
                        "Service": appt["service"],
                        "Date": appt["date"],
                        "Time": appt["time"],
                        "Employee": appt["employee"],
                        "Status": display_status,
                        "Basic Charge": service.get_appointment_basic_charge(appt),
                        "20% Tip": service.get_appointment_tip(appt),
                        "Total Charge": service.get_appointment_total_charge(appt),
                    }
                )

            st.dataframe(old_table, use_container_width=True)

        else:
            st.info("No old appointments found.")

    with canceled_tab:
        canceled_appointments = []

        for appt in user_appts:
            matches_search = history_search.lower() in appt["service"].lower()
            is_canceled = appt.get("status") == "Canceled"
            matches_filter = st.session_state["customer_history_filter"] in ["All", "Canceled"]

            if matches_search and is_canceled and matches_filter:
                canceled_appointments.append(appt)

        if len(canceled_appointments) > 0:
            canceled_table = []

            for appt in canceled_appointments:
                canceled_table.append(
                    {
                        "Service": appt["service"],
                        "Date": appt["date"],
                        "Time": appt["time"],
                        "Employee": appt["employee"],
                        "Status": appt.get("status", "Canceled"),
                        "Basic Charge": service.get_appointment_basic_charge(appt),
                        "20% Tip": service.get_appointment_tip(appt),
                        "Total Charge": service.get_appointment_total_charge(appt),
                    }
                )

            st.dataframe(canceled_table, use_container_width=True)

        else:
            st.info("No canceled appointments found.")


def render_rewards(service):
    reward_points = st.session_state["user"].get("reward_points", 0)
    reward_history = st.session_state["user"].get("reward_history", [])

    st.title("Rewards Program")
    st.caption("Redeem your points for salon rewards.")
    st.divider()

    redeem_tab, history_tab = st.tabs(["Redeem Reward", "Reward History"])

    with redeem_tab:
        col1, col2, col3 = st.columns([1, 3, 1])

        with col2:
            with st.container(border=True):
                st.markdown("### Available Rewards")
                st.warning(f"Current Points: {reward_points}")
                st.divider()

                for reward in service.reward_options:
                    with st.container(border=True):
                        st.markdown(f"**Reward:** {reward['name']}")
                        st.markdown(f"**Points Required:** {reward['points']}")

                        if reward_points >= reward["points"]:
                            if st.button(
                                f"Redeem {reward['name']}",
                                key=f"redeem_{reward['name']}",
                                type="primary",
                                use_container_width=True,
                            ):
                                redeemed = service.redeem_reward_for_customer(
                                    st.session_state["user"]["id"],
                                    reward["name"],
                                    reward["points"],
                                )

                                if redeemed:
                                    st.success(f"{reward['name']} redeemed successfully.")
                                    st.rerun()
                        else:
                            st.warning("Not enough points for this reward.")

    with history_tab:
        col1, col2, col3 = st.columns([1, 3, 1])

        with col2:
            with st.container(border=True):
                st.markdown("### Reward History")

                if len(reward_history) > 0:
                    for reward_item in reward_history:
                        with st.container(border=True):
                            st.markdown(f"**Reward:** {reward_item['reward_name']}")
                            st.markdown(f"**Points Used:** {reward_item['points_used']}")
                            st.markdown(f"**Redeemed At:** {reward_item['redeemed_at']}")
                            st.markdown(f"**Status:** {reward_item['status']}")
                else:
                    st.info("No rewards redeemed yet.")


def render_feedback_form(service, user_appts):
    st.title("Feedback Form")
    st.caption("Pick an appointment and submit feedback, complaints, or concerns about that visit.")
    st.divider()

    customer_appointments_for_feedback = []

    for appt in user_appts:
        if appt.get("status") != "Canceled":
            customer_appointments_for_feedback.append(appt)

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        with st.container(border=True):
            if len(customer_appointments_for_feedback) > 0:
                selected_feedback_appt = st.selectbox(
                    "Choose Appointment for Feedback",
                    customer_appointments_for_feedback,
                    format_func=lambda x: f"{x['service']} | {x['date']} at {x['time']} | {x['employee']} | {x.get('status', 'Scheduled')}",
                    key="feedback_appointment_select",
                )

                st.markdown("### Appointment Selected")
                st.markdown(f"**Service:** {selected_feedback_appt['service']}")
                st.markdown(f"**Date:** {selected_feedback_appt['date']}")
                st.markdown(f"**Time:** {selected_feedback_appt['time']}")
                st.markdown(f"**Employee:** {selected_feedback_appt['employee']}")
                st.markdown(f"**Status:** {selected_feedback_appt.get('status', 'Scheduled')}")

                feedback_type = st.selectbox(
                    "Feedback Type",
                    ["General Feedback", "Complaint", "Service Issue", "Employee Compliment"],
                    key="feedback_type_select",
                )

                feedback_message = st.text_area(
                    "Write your feedback here",
                    key="feedback_message_input",
                )

                if st.button("Submit Feedback", key="submit_feedback_btn", type="primary", use_container_width=True):
                    if not feedback_message.strip():
                        st.error("Please write your feedback before submitting.")
                    else:
                        new_feedback = {
                            "id": service.get_next_feedback_id(),
                            "appointment_id": selected_feedback_appt["id"],
                            "customer_name": st.session_state["user"]["full_name"],
                            "customer_email": st.session_state["user"]["email"],
                            "feedback_type": feedback_type,
                            "message": feedback_message,
                            "related_service": selected_feedback_appt["service"],
                            "appointment_date": selected_feedback_appt["date"],
                            "appointment_time": selected_feedback_appt["time"],
                            "appointment_employee": selected_feedback_appt["employee"],
                            "appointment_status": selected_feedback_appt.get("status", "Scheduled"),
                            "status": "Pending",
                            "submitted_at": str(datetime.now()),
                            "reviewed_by": "",
                            "reviewed_at": "",
                        }

                        service.store.feedback_list.append(new_feedback)
                        service.store.save_feedback()

                        st.success("Your feedback was submitted successfully.")
                        st.rerun()
            else:
                st.info("You do not have any appointments available for feedback yet.")

    st.divider()
    st.markdown("### My Submitted Feedback")

    user_feedback = []

    for feedback in service.store.feedback_list:
        if feedback.get("customer_email") == st.session_state["user"]["email"]:
            user_feedback.append(feedback)

    if len(user_feedback) > 0:
        for feedback in user_feedback:
            with st.container(border=True):
                st.markdown(
                    f"**Appointment:** {feedback.get('related_service', 'N/A')} | "
                    f"{feedback.get('appointment_date', 'N/A')} at {feedback.get('appointment_time', 'N/A')}"
                )
                st.markdown(f"**Employee:** {feedback.get('appointment_employee', 'N/A')}")
                st.markdown(f"**Type:** {feedback['feedback_type']}")
                st.markdown(f"**Message:** {feedback['message']}")
                st.markdown(f"**Status:** {feedback['status']}")
                st.caption(f"Submitted at: {feedback['submitted_at']}")
    else:
        st.info("You have not submitted any feedback yet.")


def render_penny_chat(service):
    reward_points = st.session_state["user"].get("reward_points", 0)

    st.title("Penny the Polish Pro")
    st.caption("Your AI salon assistant.")
    st.divider()

    st.info("Ask Penny about appointments, booking, cancellations, services, rewards, and nail tech information.")

    if st.button("Clear Chat", key="clear_customer_chat", type="primary"):
        st.session_state["messages"] = []
        st.rerun()

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input(
        "Ask Penny the Polish Pro, our AI salon assistant, something...",
        key="customer_chat_input",
    )

    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})

        prompt_lower = prompt.lower()

        user_appts_for_chat = []

        for appt in service.store.appointments:
            if "client_email" in appt and appt["client_email"] == st.session_state["user"]["email"]:
                user_appts_for_chat.append(appt)

        if "appointment" in prompt_lower and "have" in prompt_lower:
            if user_appts_for_chat:
                response = "You currently have these appointments:\n"

                for appt in user_appts_for_chat:
                    response += f"- {appt['date']} at {appt['time']} for {appt['service']} with {appt['employee']}\n"
            else:
                response = "You do not have any appointments booked right now."

        elif "cancel" in prompt_lower:
            response = "To cancel an appointment, go to the My Appointments section and select your appointment in the Upcoming tab."

        elif "service" in prompt_lower:
            response = "Available services are:\n"

            for salon_service in service.store.services:
                response += f"- {salon_service['name']}: ${salon_service['price']}\n"

        elif "status" in prompt_lower:
            if user_appts_for_chat:
                response = "Here are your current appointment statuses:\n"

                for appt in user_appts_for_chat:
                    response += f"- {appt['service']} on {appt['date']} is {appt.get('status', 'Scheduled')}\n"
            else:
                response = "You do not have any appointment statuses to check right now."

        elif "employee" in prompt_lower or "tech" in prompt_lower:
            response = "Current nail techs are Marissa, Jackie, and Eesha."

        elif "book" in prompt_lower or "schedule" in prompt_lower:
            response = "To book an appointment, go to the Book Appointment section, choose a service, employee, date, and time, then click Book Appointment."

        elif "reward" in prompt_lower or "points" in prompt_lower:
            response = f"You currently have {reward_points} reward points. You earn 10 points for each completed appointment."

        elif "tip" in prompt_lower or "price" in prompt_lower or "cost" in prompt_lower:
            response = "Each appointment includes the basic service charge plus a 20% tip."

        elif "hello" in prompt_lower or "hi" in prompt_lower:
            response = "Hi! I am Penny the Polish Pro. I can help with appointments, services, rewards, cancellations, and nail tech information."

        else:
            response = "I can help with appointments, booking, cancellations, services, rewards, prices, and nail tech information."

        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.rerun()