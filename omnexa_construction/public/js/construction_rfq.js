frappe.ui.form.on("Construction RFQ", {
	refresh(frm) {
		if (frm.doc.docstatus === 1) return;
		if (frm.doc.purchase_request) {
			frm.add_custom_button(__("Open Purchase Request"), () => {
				frappe.set_route("Form", "Purchase Request", frm.doc.purchase_request);
			});
		}
		if (!frm.is_new() && frm.doc.supplier_quotes && frm.doc.supplier_quotes.length) {
			frm.add_custom_button(__("Evaluate Quotes"), () => {
				frappe.call({
					method: "omnexa_construction.wizard.wizard_api.evaluate_construction_rfq",
					args: { rfq_name: frm.doc.name },
					freeze: true,
					callback(r) {
						if (r.message && r.message.recommended_supplier) {
							frappe.msgprint(
								__("Recommended: {0}", [r.message.recommended_supplier])
							);
						}
						frm.reload_doc();
					},
				});
			});
		}
	},
});
