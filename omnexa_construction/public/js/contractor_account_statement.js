frappe.ui.form.on("Contractor Account Statement", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Load from IPCs"), () => {
				frappe.call({
					method: "omnexa_construction.omnexa_construction.doctype.contractor_account_statement.contractor_account_statement.load_lines_from_ipc",
					args: { statement_name: frm.doc.name },
					freeze: true,
					callback() {
						frm.reload_doc();
					},
				});
			});
		}
	},
});
