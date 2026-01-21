# Copyright (c) 2026, Muqeet Mughal and contributors
# For license information, please see license.txt
import frappe


def build_columns():
    return [
        {
            "fieldname": "airline",
            "label": "Airline",
            "fieldtype": "Link",
            "options": "Airline",
            "width": 120,
        },
        {
            "fieldname": "revenue",
            "label": "Revenue",
            "fieldtype": "Currency",
            "width": 120,
        },
    ]


def fetch_airline_revenue():
    airlines = frappe.get_all("Airline", pluck="name")

    if not airlines:
        return []

    revenue_map = frappe.db.sql(
        """
        SELECT
            ap.airline AS airline,
            SUM(at.flight_price) +
            SUM(COALESCE(addons.addon_total, 0)) AS revenue
        FROM `tabAirplane Ticket` at
        INNER JOIN `tabAirplane Flight` fl ON fl.name = at.flight
        INNER JOIN `tabAirplane` ap ON ap.name = fl.airplane
        LEFT JOIN (
            SELECT parent, SUM(amount) AS addon_total
            FROM `tabAirplane Ticket Add-on Item`
            GROUP BY parent
        ) addons ON addons.parent = at.name
        GROUP BY ap.airline
        """,
        as_dict=True,
    )

    revenue_lookup = {row.airline: row.revenue or 0 for row in revenue_map}

    return [[airline, revenue_lookup.get(airline, 0)] for airline in airlines]


def prepare_chart(rows):
    return {
        "type": "donut",
        "data": {
            "labels": [r[0] for r in rows],
            "datasets": [
                {
                    "name": "Revenue",
                    "values": [r[1] for r in rows],
                }
            ],
        },
    }


def execute(filters=None):
    columns = build_columns()
    rows = fetch_airline_revenue()

    total = sum(r[1] for r in rows)
    rows.append(["Total Revenue", total])

    summary = [
        {
            "label": "Total Revenue",
            "value": frappe.format_value(total, "Currency"),
        }
    ]

    chart = prepare_chart(rows[:-1])

    return columns, rows, None, chart, summary