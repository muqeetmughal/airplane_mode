# Copyright (c) 2026, Muqeet Mughal
# Refer to license.txt for license information

import frappe
from frappe.model.document import Document
import random


class AirplaneTicket(Document):

    
    def before_save(self):
        addon_total = sum(row.amount for row in self.add_ons or [])
        self.total_amount = (self.flight_price or 0) + addon_total

    def validate(self):
        seen_items = set()
        duplicates = []

        for row in list(self.add_ons):
            if row.item in seen_items:
                duplicates.append(row.item)
                self.remove(row)
            else:
                seen_items.add(row.item)

        if duplicates:
            frappe.msgprint(
                title="Duplicate Add-ons Removed",
                msg="Add-ons must be unique. Removed: " + ", ".join(set(duplicates)),
                alert=True,
            )

    def before_submit(self):
        if self.status != "Boarded":
            frappe.throw(
                f"Submission blocked: Ticket status must be 'Boarded' (current: {self.status})."
            )

    def before_insert(self):
        self.seat = self._generate_seat()

        flight_doc = frappe.get_doc("Airplane Flight", self.flight)
        airplane_doc = frappe.get_doc("Airplane", flight_doc.airplane)

        issued_tickets = frappe.db.count(
            "Airplane Ticket",
            filters={"flight": self.flight},
        )

        if issued_tickets >= airplane_doc.capacity:
            frappe.throw(
                f"Capacity exceeded for airplane {airplane_doc.name}. "
                f"Maximum allowed seats: {airplane_doc.capacity}."
            )

    def _generate_seat(self):
        number = random.randrange(1, 100)
        letter = random.choice(["A", "B", "C", "D", "E"])
        return f"{number}{letter}"
