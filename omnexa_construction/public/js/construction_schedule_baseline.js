frappe.ui.form.on("Construction Schedule Baseline", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Load Tasks from BOQ"), () => {
			frappe.call({
				method: "omnexa_construction.schedule_gantt.load_baseline_tasks_from_boq",
				args: { baseline_name: frm.doc.name },
				callback(r) {
					frappe.show_alert({
						message: __("Added {0} task(s)", [r.message?.added || 0]),
						indicator: "green",
					});
					frm.reload_doc();
				},
			});
		});
		frm.add_custom_button(__("Export MS Project XML"), () => {
			frappe.call({
				method: "omnexa_construction.schedule_msp_export.export_baseline_msp_xml",
				args: { baseline_name: frm.doc.name },
				callback(r) {
					if (r.message?.file_url) {
						window.open(r.message.file_url, "_blank");
					}
				},
			});
		});
		frm.add_custom_button(__("Open Gantt View"), () => {
			frappe.route_options = { project_contract: frm.doc.project_contract };
			frappe.set_route("construction-schedule-gantt");
		});
	},
});
