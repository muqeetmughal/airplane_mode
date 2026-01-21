// Copyright (c) 2025, Muqeet Mughal and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airline", {
	refresh(frm) {
		if (frm.doc.website) {
			frm.add_web_link("Visit Website", frm.doc.website);
		}
	},
});
