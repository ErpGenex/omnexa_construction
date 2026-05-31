frappe.ui.form.on("Project WIP Snapshot", {
	refresh(frm) {
		if (!frm.doc.project_contract) {
			return;
		}
		frm.add_custom_button(__("Load from BOQ/IPC"), () => {
			frappe.call({
				method: "omnexa_construction.wip_gl.create_wip_snapshot_from_project",
				args: {
					project_contract: frm.doc.project_contract,
					snapshot_date: frm.doc.snapshot_date,
					update_existing: frm.doc.__islocal ? 0 : 1,
				},
				callback(r) {
					if (r.message && r.message.name && r.message.name !== frm.doc.name) {
						frappe.set_route("Form", "Project WIP Snapshot", r.message.name);
					} else {
						frm.reload_doc();
					}
				},
			});
		});
	},
});
