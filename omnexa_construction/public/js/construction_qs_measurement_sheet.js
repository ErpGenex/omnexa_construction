frappe.ui.form.on("Construction QS Measurement Sheet", {
	refresh(frm) {
		if (frm.is_new() || !frm.doc.project_contract) {
			return;
		}
		frm.add_custom_button(__("Load BOQ Lines"), () => {
			frappe.call({
				method:
					"omnexa_construction.construction_forms.qs_helpers.load_boq_measurement_lines",
				args: { project_contract: frm.doc.project_contract },
				callback(r) {
					(r.message || []).forEach((row) => frm.add_child("lines", row));
					frm.refresh_field("lines");
				},
			});
		});
	},
});
