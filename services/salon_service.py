from datetime import datetime


class SalonService:
    def __init__(self, store):
        self.store = store

        self.service_inventory_map = {
            "Basic Manicure": ["Cuticle Oil", "Cotton Pads"],
            "Gel Manicure": ["Gel Polish", "Cuticle Oil", "Cotton Pads"],
            "Classic Pedicure": ["Cuticle Oil", "Cotton Pads"],
            "Acrylic Full Set": ["Acrylic Powder", "Nail Files", "Cotton Pads"],
            "Nail Art Design": ["Nail Files", "Cotton Pads"],
        }

        self.reward_options = [
            {"name": "10% Off Next Service", "points": 50},
            {"name": "Free Nail Art Design", "points": 100},
            {"name": "Free Basic Manicure", "points": 250},
            {"name": "Free Gel Manicure", "points": 400},
        ]

        self.employee_names = ["Marissa", "Jackie", "Eesha Shahi"]

        self.all_times = [
            "9:00 AM",
            "10:00 AM",
            "11:00 AM",
            "12:00 PM",
            "1:00 PM",
            "2:00 PM",
            "3:00 PM",
            "4:00 PM",
            "5:00 PM",
        ]

    def get_service_prices(self):
        prices = {}
        for service in self.store.services:
            prices[service["name"]] = service["price"]
        return prices

    def ensure_user_reward_fields(self, user):
        updated = False

        if "reward_points" not in user:
            user["reward_points"] = 0
            updated = True

        if "reward_history" not in user:
            user["reward_history"] = []
            updated = True

        return updated

    def get_next_appointment_id(self):
        if len(self.store.appointments) == 0:
            return 1

        max_id = 0
        for appt in self.store.appointments:
            if appt["id"] > max_id:
                max_id = appt["id"]

        return max_id + 1

    def get_next_feedback_id(self):
        if len(self.store.feedback_list) == 0:
            return 1

        max_id = 0
        for feedback in self.store.feedback_list:
            if feedback["id"] > max_id:
                max_id = feedback["id"]

        return max_id + 1

    def calculate_tip(self, price):
        return round(price * 0.20, 2)

    def calculate_total_charge(self, price):
        return round(price + self.calculate_tip(price), 2)

    def get_item_by_name(self, item_name):
        for item in self.store.inventory:
            if item["item_name"] == item_name:
                return item
        return None

    def has_inventory_for_service(self, service_name):
        required_items = self.service_inventory_map.get(service_name, [])

        for required_item in required_items:
            item = self.get_item_by_name(required_item)

            if item is None or item["quantity"] < 1:
                return False

        return True

    def update_inventory_for_service(self, service_name, action):
        required_items = self.service_inventory_map.get(service_name, [])

        if action == "subtract":
            for required_item in required_items:
                item = self.get_item_by_name(required_item)
                if item is None or item["quantity"] < 1:
                    return False

            for required_item in required_items:
                item = self.get_item_by_name(required_item)
                item["quantity"] -= 1

            return True

        if action == "add":
            for required_item in required_items:
                item = self.get_item_by_name(required_item)
                if item:
                    item["quantity"] += 1

            return True

        return False

    def get_user_appointments(self, user_email):
        user_appts = []

        for appt in self.store.appointments:
            if appt.get("client_email") == user_email:
                user_appts.append(appt)

        return user_appts

    def get_employee_appointments(self, employee_name):
        employee_appts = []

        for appt in self.store.appointments:
            if appt.get("employee") == employee_name:
                employee_appts.append(appt)

        return employee_appts

    def is_past_appointment(self, appt):
        appointment_datetime = datetime.strptime(
            f"{appt['date']} {appt['time']}",
            "%Y-%m-%d %I:%M %p",
        )

        return appointment_datetime < datetime.now()

    def get_low_stock_count(self):
        count = 0

        for item in self.store.inventory:
            if item["quantity"] <= item["low_stock_limit"]:
                count += 1

        return count

    def get_completed_appointments(self):
        completed = []

        for appt in self.store.appointments:
            if appt.get("status") == "Completed":
                completed.append(appt)

        return completed

    def get_appointment_basic_charge(self, appt):
        return round(appt.get("price", 0), 2)

    def get_appointment_tip(self, appt):
        basic_charge = self.get_appointment_basic_charge(appt)
        return round(appt.get("tip_amount", self.calculate_tip(basic_charge)), 2)

    def get_appointment_total_charge(self, appt):
        basic_charge = self.get_appointment_basic_charge(appt)
        return round(appt.get("total_charge", self.calculate_total_charge(basic_charge)), 2)

    def add_reward_points_to_customer(self, customer_email, points_to_add):
        for user in self.store.users:
            if user["email"] == customer_email:
                self.ensure_user_reward_fields(user)
                user["reward_points"] += points_to_add
                break

        self.store.save_users()

    def redeem_reward_for_customer(self, user_id, reward_name, reward_cost):
        for user in self.store.users:
            if user["id"] == user_id:
                self.ensure_user_reward_fields(user)

                if user["reward_points"] >= reward_cost:
                    user["reward_points"] -= reward_cost
                    user["reward_history"].append(
                        {
                            "reward_name": reward_name,
                            "points_used": reward_cost,
                            "redeemed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "status": "Available",
                        }
                    )

                    self.store.save_users()
                    return True

        return False