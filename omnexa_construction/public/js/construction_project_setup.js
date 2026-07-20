frappe.ui.form.on("Construction Project Setup", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		const locked = frm.doc.approval_status === "Approved";
		const completed = frm.doc.status === "Completed";
		const editable = !locked;

		if (locked) {
			frm.set_intro(
				__(
					"Approved setup (revision {0}) — locked. Project Manager can reopen for revision.",
					[frm.doc.setup_revision || 1]
				),
				"blue"
			);
		} else if (completed) {
			frm.set_intro(
				__(
					"Project generated — you may edit all fields until manager approval. Sync changes to contract before approving."
				),
				"orange"
			);
		}

		if (frm.doc.document_pack_file) {
			frm.add_custom_button(__("Download Document Pack (ZIP)"), () => {
				window.open(frappe.urllib.get_full_url(frm.doc.document_pack_file));
			}, __("Documents"));
		} else {
			frm.add_custom_button(__("Export Document Pack (ZIP)"), () => export_setup_document_pack(frm), __("Documents"));
		}

		if (completed && frm.doc.project_contract) {
			frm.add_custom_button(
				__("Project Contract"),
				() => frappe.set_route("Form", "Project Contract", frm.doc.project_contract),
				__("Documents")
			);
		}

		if (editable) {
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
									format_currency(r.message.estimated_contract_value, frm.doc.contract_currency),
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

			frm.add_custom_button(__("Suggest Contract Terms"), () => {
				frappe.call({
					method: "omnexa_construction.wizard.setup_approval.suggest_setup_contract_terms",
					args: { setup_name: frm.doc.name, replace: 1 },
					freeze: true,
					callback(r) {
						if (r.message) {
							frappe.show_alert({
								message: __("Generated {0} contract clauses", [r.message.terms]),
								indicator: "green",
							});
							frm.reload_doc();
						}
					},
				});
			}, __("Contract"));

			if (completed && frm.doc.project_contract) {
				frm.add_custom_button(
					__("Sync to Contract"),
					() => {
						frappe.call({
							method: "omnexa_construction.wizard.setup_approval.resync_contract_from_setup",
							args: { setup_name: frm.doc.name },
							freeze: true,
							callback(r) {
								if (r.message) {
									frappe.msgprint(__("Contract {0} updated.", [r.message.contract]));
									frm.reload_doc();
								}
							},
						});
					},
					__("Contract")
				);
			}

			if (!completed) {
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
		}

		if (editable && completed && frm.doc.approval_status !== "Pending Approval") {
			frm.add_custom_button(__("Submit for Approval"), () => {
				frappe.call({
					method: "omnexa_construction.wizard.setup_approval.submit_setup_for_approval",
					args: { setup_name: frm.doc.name },
					freeze: true,
					callback() {
						frm.reload_doc();
					},
				});
			}, __("Approval"));
		}

		if (
			frappe.user.has_role("Project Manager") ||
			frappe.user.has_role("System Manager")
		) {
			if (frm.doc.approval_status === "Pending Approval" || (completed && frm.doc.approval_status === "Open")) {
				frm.add_custom_button(
					__("Approve Setup"),
					() => {
						frappe.prompt(
							[
								{
									fieldname: "notes",
									fieldtype: "Small Text",
									label: __("Approval Notes"),
								},
							],
							(values) => {
								frappe.call({
									method: "omnexa_construction.wizard.setup_approval.approve_project_setup",
									args: {
										setup_name: frm.doc.name,
										notes: values.notes,
										resync_boq: 1,
									},
									freeze: true,
									callback(r) {
										if (r.message) {
											frappe.msgprint(__("Setup approved and attached to contract."));
											frm.reload_doc();
										}
									},
								});
							},
							__("Approve Project Setup"),
							__("Approve")
						);
					},
					__("Approval")
				);
			}
			if (frm.doc.approval_status === "Pending Approval") {
				frm.add_custom_button(
					__("Reject"),
					() => {
						frappe.prompt(
							[{ fieldname: "notes", fieldtype: "Small Text", label: __("Reason"), reqd: 1 }],
							(values) => {
								frappe.call({
									method: "omnexa_construction.wizard.setup_approval.reject_project_setup",
									args: { setup_name: frm.doc.name, notes: values.notes },
									callback() {
										frm.reload_doc();
									},
								});
							},
					__("Reject Setup"),
					__("Reject")
						);
					},
					__("Approval")
				);
			}
			if (locked) {
				frm.add_custom_button(
					__("Reopen for Revision"),
					() => {
						frappe.prompt(
							[{ fieldname: "reason", fieldtype: "Small Text", label: __("Reason") }],
							(values) => {
								frappe.call({
									method: "omnexa_construction.wizard.setup_approval.reopen_setup_for_revision",
									args: { setup_name: frm.doc.name, reason: values.reason },
									callback() {
										frm.reload_doc();
									},
								});
							},
							__("Reopen Setup"),
							__("Reopen")
						);
					},
					__("Approval")
				);
			}
		}

		frm.set_df_property("boq_details", "cannot_add_rows", locked);
		frm.set_df_property("ipc_plan", "cannot_add_rows", locked);
		frm.set_df_property("contract_terms", "cannot_add_rows", locked);
	},
});

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
