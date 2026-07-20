frappe.ui.form.on("IPC Certificate", {
	refresh(frm) {
		if (!frm.doc.project_contract || frm.doc.status === "Cancelled") {
			return;
		}
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(
				__("Calculate Deductions"),
				() => {
					frappe.call({
						method: "omnexa_construction.liquidated_damages.apply_deductions_to_ipc",
						args: { ipc_name: frm.doc.name, use_suggested: 1 },
						callback() {
							frm.reload_doc();
							frappe.show_alert({ message: __("Deductions updated"), indicator: "green" });
						},
					});
				},
				__("Commercial")
			);
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
			frm.add_custom_button(
				__("Suggest from Schedule"),
				() => {
					frappe.call({
						method:
							"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.suggest_completion_percent_from_schedule",
						args: {
							project_contract: frm.doc.project_contract,
							pm_wbs_task: frm.doc.pm_wbs_task || null,
						},
						callback(r) {
							if (r.message && r.message.suggested_percent != null) {
								const sourceMap = {
									schedule_wbs: __("Schedule (WBS)"),
									schedule_baseline: __("Schedule Baseline"),
									boq: __("BOQ"),
									none: __("None"),
								};
								frm.set_value("boq_completion_percent", r.message.suggested_percent);
								frappe.show_alert({
									message: __(
										"Suggested {0}% from {1} (Schedule: {2}%, BOQ: {3}%)",
										[
											r.message.suggested_percent,
											sourceMap[r.message.source] || r.message.source,
											r.message.schedule_percent,
											r.message.boq_percent,
										]
									),
									indicator: "blue",
								});
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
