frappe.ui.form.on("Project Contract", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("PM Schedule (Gantt)"), () => {
			frappe.set_route("page", "pm_schedule_gantt", { project: frm.doc.name });
		}, __("Schedule"));

		frm.add_custom_button(
			__("Sync WBS from BOQ"),
			() => {
				frappe.call({
					method: "omnexa_projects_pm.wbs_schedule.sync_wbs_from_boq",
					args: { project_contract: frm.doc.name, chain_dependencies: 1 },
					freeze: true,
					callback(r) {
						const m = r.message || {};
						frappe.show_alert({
							message: __("WBS: {0} created, {1} updated, {2} tasks", [
								m.created || 0,
								m.updated || 0,
								m.tasks || 0,
							]),
							indicator: "green",
						});
						frm.reload_doc();
					},
				});
			},
			__("Schedule")
		);

		const forms = [
			["Construction Work Approval Request", __("Work Approval")],
			["Construction Material Approval Request", __("Material Approval")],
			["Contractor Account Statement", __("Account Statement")],
			["Construction Fines Statement", __("Fines Statement")],
			["Construction Work Delay Notice", __("Delay Notice")],
			["IPC Certificate", __("IPC / Progress")],
		];
		forms.forEach(([doctype, label]) => {
			frm.add_custom_button(
				label,
				() => {
					frappe.new_doc(doctype, { project_contract: frm.doc.name });
				},
				__("Site Forms")
			);
		});

		const phase6 = [
			["Construction QS Measurement Sheet", __("QS Measurement")],
			["Construction FIDIC Notice", __("FIDIC Notice")],
			["Construction Final Account Statement", __("Final Account")],
			["Construction DLP Record", __("DLP")],
			["Construction Inspection Test Plan", __("ITP")],
		];
		phase6.forEach(([doctype, label]) => {
			frm.add_custom_button(
				label,
				() => frappe.new_doc(doctype, { project_contract: frm.doc.name }),
				__("QS & Close-out")
			);
		});

		const phase7 = [
			["Construction CDE Document", __("CDE Document")],
			["Construction Equipment Usage", __("Equipment Usage")],
			["Project WIP Snapshot", __("WIP Snapshot")],
		];
		phase7.forEach(([doctype, label]) => {
			frm.add_custom_button(
				label,
				() => {
					if (doctype === "Project WIP Snapshot") {
						frappe.new_doc(doctype, {
							project_contract: frm.doc.name,
							snapshot_date: frappe.datetime.get_today(),
						});
					} else {
						frappe.new_doc(doctype, { project_contract: frm.doc.name });
					}
				},
				__("Cost & CDE")
			);
		});

		if (["villa", "residential_building", "social_housing"].includes(frm.doc.building_type)) {
			frm.add_custom_button(
				__("Plot / Unit Inventory"),
				() => frappe.set_route("List", "Construction Residential Unit", { project_contract: frm.doc.name }),
				__("Residential")
			);
		}

		if (frm.doc.wizard_setup) {
			frm.add_custom_button(
				__("Wizard Setup"),
				() => frappe.set_route("Form", "Construction Project Setup", frm.doc.wizard_setup),
				__("Contract")
			);
		}
		if (frm.doc.approved_setup_attachment) {
			frm.add_custom_button(
				__("Approved Setup Pack"),
				() => window.open(frappe.urllib.get_full_url(frm.doc.approved_setup_attachment)),
				__("Contract")
			);
		}
		frm.add_custom_button(
			__("Print Full Contract"),
			() => frappe.ui.get_print("Project Contract", frm.doc.name, "Project Contract — Full (عقد متكامل)"),
			__("Contract")
		);
	},
});
