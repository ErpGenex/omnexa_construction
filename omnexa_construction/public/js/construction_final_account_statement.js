frappe.ui.form.on("Construction Final Account Statement", {
	refresh(frm) {
		if (!frm.doc.project_contract || frm.doc.__islocal) {
			return;
		}
		frm.add_custom_button(__("Recalculate"), () => frm.save());
	},
});
