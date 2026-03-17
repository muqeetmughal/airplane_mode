# Copyright (c) 2025, Muqeet Mughal and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class AirplaneFlight(WebsiteGenerator):
    def on_submit(self):
        # set Status to Completed after submission
        self.db_set("status", "Completed")
        


def sync_gate_number(doc, method):
    frappe.enqueue(
        _sync_gate_number_task,
        doc_name=doc.name,
        gate_number=doc.gate_number,
        queue='default',
        timeout=300
    )


def _sync_gate_number_task(doc_name, gate_number):
    # Find all Airplane Ticket documents linked to the flight
    tickets = frappe.get_all("Airplane Ticket", filters={
                             "flight": doc_name}, fields=["name"])

    for ticket in tickets:
        # Load the Airplane Ticket document
        ticket_doc = frappe.get_doc("Airplane Ticket", ticket["name"])

        # Update the gate_number and save the ticket
        ticket_doc.gate_number = gate_number
        ticket_doc.save()

    frappe.msgprint(
        f"Gate number updated in all linked tickets for flight {doc_name}.")
