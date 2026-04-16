frappe.ui.form.on("Subcontract Payment Certificate", {
	refresh(frm) {
		if (frm.doc.docstatus !== 1 || frm.doc.status === "Retention Released") {
			return;
		}
		frm.add_custom_button(__("Release Retention"), () => {
			const d = new frappe.ui.Dialog({
				title: __("Release Retention"),
				fields: [
					{ fieldtype: "Date", fieldname: "retention_release_date", label: __("Retention Release Date"), reqd: 1, default: frappe.datetime.get_today() },
					{ fieldtype: "Link", fieldname: "retention_mode_of_payment", label: __("Retention Mode of Payment"), options: "Mode of Payment" },
					{ fieldtype: "Link", fieldname: "retention_bank_account", label: __("Retention Bank Account"), options: "Bank Account" },
				],
				primary_action_label: __("Release"),
				primary_action(values) {
					frappe.call({
						method: "omnexa_construction.omnexa_construction.doctype.subcontract_payment_certificate.subcontract_payment_certificate.release_retention",
						args: { name: frm.doc.name, ...values },
						callback: () => {
							d.hide();
							frm.reload_doc();
						},
					});
				},
			});
			d.show();
		});
	},
});

