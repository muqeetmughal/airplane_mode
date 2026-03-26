// Copyright (c) 2026, Muqeet Mughal and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shop", {
	refresh(frm) {
		frm.add_custom_button(
			__("List Tenants"),
			function () {
				frappe.db.get_list("Shop Contract", {
                    fields: ["*"],
                    filters: { shop: frm.doc.name },
                }).then((contracts) => {
                    // console.log("Contracts in shop:", contracts);
                    if (contracts.length > 0) {
                        let tenant_list = contracts
                            .map((contract) => `<li>${contract.tenant} (${contract.name})</li>`)
                            .join("");
                        frappe.msgprint(
                            `<h4>Tenants in ${frm.doc.shop_name}:</h4><ul>${tenant_list}</ul>`
                        );
                    } else {
                        frappe.msgprint(`No tenants found for ${frm.doc.shop_name}.`);
                    }
                });
			},
		);
		frm.set_query("shop_type", function () {
			return {
				filters: {
					enabled: 1,
				},
			};
		});
	},
});
