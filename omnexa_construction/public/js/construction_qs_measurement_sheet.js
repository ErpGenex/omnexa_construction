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
		frm.add_custom_button(__("Import Takeoff CSV"), () => {
			frappe.prompt(
				[
					{
						fieldname: "csv_text",
						fieldtype: "Long Text",
						label: __("CSV Rows"),
						reqd: 1,
						description: __("Headers: cost_code, measured_qty, description, uom"),
					},
				],
				(values) => {
					frappe.call({
						method:
							"omnexa_construction.omnexa_construction.doctype.construction_qs_measurement_sheet.construction_qs_measurement_sheet.import_takeoff_csv",
						args: {
							project_contract: frm.doc.project_contract,
							csv_text: values.csv_text,
						},
						callback(r) {
							(r.message || []).forEach((row) => frm.add_child("lines", row));
							frm.refresh_field("lines");
						},
					});
				},
				__("Import Takeoff CSV"),
				__("Import")
			);
		});
	},
});
