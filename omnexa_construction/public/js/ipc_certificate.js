frappe.ui.form.on("IPC Certificate", {
	refresh(frm) {
		if (!frm.doc.project_contract || frm.doc.status === "Cancelled") {
			return;
		}
		if (!frm.doc.sales_invoice && frm.doc.status !== "Posted") {
			frm.add_custom_button(
				__("Suggest from BOQ"),
				() => {
					frappe.call({
						method:
							"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.suggest_boq_completion_percent",
						args: { project_contract: frm.doc.project_contract },
						callback(r) {
							if (r.message != null) {
								frm.set_value("boq_completion_percent", r.message);
							}
						},
					});
				},
				__("Progress")
			);
		}
		if (!frm.doc.sales_invoice && flt(frm.doc.net_amount) > 0) {
			frm.add_custom_button(
				__("Create Draft Sales Invoice"),
				() => {
					frappe.call({
						method: "omnexa_construction.ipc_revenue.create_draft_sales_invoice",
						args: { ipc_name: frm.doc.name },
						callback() {
							frm.reload_doc();
						},
					});
				},
				__("Billing")
			);
		}
		if (frm.doc.sales_invoice) {
			frm.add_custom_button(
				__("Sales Invoice"),
				() => frappe.set_route("Form", "Sales Invoice", frm.doc.sales_invoice),
				__("Billing")
			);
		}
	},
});
