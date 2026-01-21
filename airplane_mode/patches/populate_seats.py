import frappe

"""
Patch: populate seat field for existing Airplane Ticket documents.

Rule used:
- For each flight, assign seats sequentially (deterministic) to tickets that don't
    have a seat yet, ordered by creation time.
- Seats are assigned in rows of 6 seats labeled A..F, e.g. 1A, 1B ... 2A, ...
- This is idempotent and only touches tickets where seat is empty/NULL.

Place this file in:
    airplane_mode/patches/populate_seats.py
"""


SEATS_PER_ROW = 6
SEAT_LETTERS = [chr(ord("A") + i) for i in range(SEATS_PER_ROW)]


def _ticket_missing_seat(ticket):
        # consider None or empty string " " as missing
        seat = ticket.get("seat")
        return seat is None or (isinstance(seat, str) and seat.strip() == "")


def execute():
        frappe.logger().info("airplane_mode: populate_seats patch starting")

        # Fetch all tickets, with flight and creation for deterministic ordering
        tickets = frappe.get_all(
                "Airplane Ticket",
                fields=["name", "flight", "creation", "seat"],
                order_by="flight, creation, name",
        )

        # Group tickets by flight
        tickets_by_flight = {}
        for t in tickets:
                flight = t.get("flight") or "_NO_FLIGHT_"
                tickets_by_flight.setdefault(flight, []).append(t)

        updated = 0
        for flight, tlist in tickets_by_flight.items():
                # Filter only tickets missing seat
                missing = [t for t in tlist if _ticket_missing_seat(t)]
                if not missing:
                        continue

                # Assign seats sequentially
                for idx, t in enumerate(missing):
                        row = (idx // SEATS_PER_ROW) + 1
                        letter = SEAT_LETTERS[idx % SEATS_PER_ROW]
                        seat = f"{row}{letter}"

                        try:
                                frappe.db.set_value("Airplane Ticket", t["name"], "seat", seat)
                                updated += 1
                        except Exception:
                                frappe.logger().error(
                                        f"airplane_mode: failed to set seat for {t['name']}", exc_info=True
                                )

        # commit once at the end
        frappe.db.commit()
        frappe.logger().info(f"airplane_mode: populate_seats patch finished, updated {updated} tickets")