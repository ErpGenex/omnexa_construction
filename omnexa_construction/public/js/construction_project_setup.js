function export_setup_document_pack(frm) {
	frappe.call({
		method: "omnexa_construction.wizard.wizard_api.export_setup_document_pack",
		args: { setup_name: frm.doc.name },
		freeze: true,
		callback(r) {
			if (r.message && r.message.file_url) {
				window.open(r.message.file_url);
				frm.reload_doc();
			}
		},
	});
}

frappe.ui.form.on("Construction Project Setup", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.document_pack_file) {
			frm.add_custom_button(__("Download Document Pack (ZIP)"), () => {
				window.open(frappe.urllib.get_full_url(frm.doc.document_pack_file));
			}, __("Documents"));
		} else {
			frm.add_custom_button(__("Export Document Pack (ZIP)"), () => export_setup_document_pack(frm), __("Documents"));
		}

		if (frm.doc.status === "Completed" && frm.doc.project_contract) {
			frm.add_custom_button(
				__("Project Contract"),
				() => frappe.set_route("Form", "Project Contract", frm.doc.project_contract),
				__("Documents")
			);
			if (!frm.doc.document_pack_file) {
				frm.add_custom_button(
					__("Rebuild Document Pack"),
					() => export_setup_document_pack(frm),
					__("Documents")
				);
			}
		}

		if (frm.doc.status !== "Completed") {
			frm.add_custom_button(__("Open Wizard"), () => {
				frappe.set_route("construction-project-wizard", { setup: frm.doc.name });
			});
			frm.add_custom_button(__("Recalculate Pricing"), () => {
				frappe.call({
					method: "omnexa_construction.wizard.wizard_api.recalculate_pricing",
					args: { setup_name: frm.doc.name },
					freeze: true,
					callback(r) {
						if (r.message) {
							frappe.msgprint(
								__("Contract value: {0}", [
									format_currency(
										r.message.estimated_contract_value,
										frm.doc.contract_currency
									),
								])
							);
							frm.reload_doc();
						}
					},
				});
			});
			frm.add_custom_button(__("Expand BOQ Details"), () => {
				frappe.call({
					method: "omnexa_construction.wizard.wizard_api.expand_boq_details",
					args: { setup_name: frm.doc.name },
					freeze: true,
					callback() {
						frm.reload_doc();
					},
				});
			});
			frm.add_custom_button(__("Import Material Catalog"), () => {
				frappe.call({
					method: "omnexa_construction.wizard.wizard_api.ensure_material_catalog",
					args: { company: frm.doc.company },
					freeze: true,
					callback(r) {
						if (r.message) {
							frappe.msgprint(
								__("Created {0} items ({1} total in catalog).", [
									r.message.created,
									r.message.total,
								])
							);
						}
					},
				});
			});
			frm.add_custom_button(__("Apply Type Template"), () => {
				frappe.call({
					method: "omnexa_construction.wizard.wizard_api.apply_full_template",
					args: { setup_name: frm.doc.name },
					freeze: true,
					callback() {
						frm.reload_doc();
					},
				});
			});
			frm.add_custom_button(__("Suggest Phases & IPC"), () => {
				frappe.call({
					method: "omnexa_construction.wizard.wizard_api.suggest_phases_ipc",
					args: { setup_name: frm.doc.name },
					freeze: true,
					callback() {
						frm.reload_doc();
					},
				});
			});
			frm.add_custom_button(__("Generate Project"), () => {
				frappe.confirm(__("Create all project documents?"), () => {
					frappe.call({
						method: "omnexa_construction.wizard.project_bundle.create_project_bundle",
						args: { setup_name: frm.doc.name },
						freeze: true,
						callback(r) {
							if (r.message && r.message.project_contract) {
								frappe.set_route("Form", "Project Contract", r.message.project_contract);
							}
						},
					});
				});
			});
		}

		frm.set_df_property("boq_details", "cannot_add_rows", frm.doc.status === "Completed");
		frm.set_df_property("ipc_plan", "cannot_add_rows", frm.doc.status === "Completed");
	},
});
