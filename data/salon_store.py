import json
from pathlib import Path


class SalonStore:
    def __init__(self):
        self.users_file = Path("users.json")
        self.appt_file = Path("appointments.json")
        self.inventory_file = Path("inventory.json")
        self.feedback_file = Path("feedback.json")
        self.services_file = Path("services.json")

        self.default_services = [
            {"name": "Basic Manicure", "price": 20},
            {"name": "Gel Manicure", "price": 35},
            {"name": "Classic Pedicure", "price": 30},
            {"name": "Acrylic Full Set", "price": 50},
            {"name": "Nail Art Design", "price": 15},
        ]

        self.default_inventory = [
            {
                "id": 1,
                "item_name": "Cuticle Oil",
                "category": "Care",
                "quantity": 10,
                "low_stock_limit": 3,
                "supplier": "Salon Supply Co.",
            },
            {
                "id": 2,
                "item_name": "Cotton Pads",
                "category": "Supplies",
                "quantity": 20,
                "low_stock_limit": 5,
                "supplier": "Beauty Wholesale",
            },
            {
                "id": 3,
                "item_name": "Gel Polish",
                "category": "Polish",
                "quantity": 10,
                "low_stock_limit": 3,
                "supplier": "Gel Pro Supply",
            },
            {
                "id": 4,
                "item_name": "Acrylic Powder",
                "category": "Acrylic",
                "quantity": 8,
                "low_stock_limit": 2,
                "supplier": "Nail Supply Hub",
            },
            {
                "id": 5,
                "item_name": "Nail Files",
                "category": "Tools",
                "quantity": 15,
                "low_stock_limit": 4,
                "supplier": "Salon Supply Co.",
            },
        ]

        self.users = self.load_json_file(self.users_file, [])
        self.appointments = self.load_json_file(self.appt_file, [])
        self.inventory = self.load_json_file(self.inventory_file, self.default_inventory)
        self.feedback_list = self.load_json_file(self.feedback_file, [])
        self.services = self.load_json_file(self.services_file, self.default_services)

    def load_json_file(self, file_path, default_value):
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_value, f, indent=4)

        return default_value

    def save_users(self):
        self.save_json_file(self.users_file, self.users)

    def save_appointments(self):
        self.save_json_file(self.appt_file, self.appointments)

    def save_inventory(self):
        self.save_json_file(self.inventory_file, self.inventory)

    def save_feedback(self):
        self.save_json_file(self.feedback_file, self.feedback_list)

    def save_services(self):
        self.save_json_file(self.services_file, self.services)

    def save_json_file(self, file_path, data):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)