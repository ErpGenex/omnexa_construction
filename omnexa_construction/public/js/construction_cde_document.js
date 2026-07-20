frappe.ui.form.on("Construction CDE Document", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Revision Chain"), () => {
			frappe.call({
				method: "omnexa_construction.transmittal_revision.get_cde_revision_chain",
				args: { document_name: frm.doc.name },
				callback(r) {
					const rows = r.message || [];
					if (!rows.length) {
						frappe.msgprint(__("No revision history."));
						return;
					}
					const html = rows
						.map(
							(row) =>
								`<tr><td>${row.revision}</td><td>${row.approval_status}</td><td>${row.issued_date || ""}</td><td>${row.superseded_by || ""}</td></tr>`
						)
						.join("");
					frappe.msgprint({
						title: __("Revision Chain"),
						message: `<table class="table table-bordered table-sm"><thead><tr><th>${__("Rev")}</th><th>${__("Status")}</th><th>${__("Issued")}</th><th>${__("Superseded By")}</th></tr></thead><tbody>${html}</tbody></table>`,
					});
				},
			});
		});
	},
});

frappe.ui.form.on("Construction Document Transmittal", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Compare with Previous"), () => {
			frappe.prompt(
				[
					{
						fieldname: "other_transmittal",
						fieldtype: "Link",
						label: __("Other Transmittal"),
						options: "Construction Document Transmittal",
						reqd: 1,
						get_query() {
							return { filters: { project_contract: frm.doc.project_contract, name: ["!=", frm.doc.name] } };
						},
					},
				],
				(values) => {
					frappe.call({
						method: "omnexa_construction.transmittal_revision.compare_transmittal_revisions",
						args: { transmittal_a: values.other_transmittal, transmittal_b: frm.doc.name },
						callback(r) {
							const d = r.message || {};
							frappe.msgprint({
								title: __("Revision Comparison"),
								message: `<pre>${JSON.stringify(d, null, 2)}</pre>`,
							});
						},
					});
				},
				__("Compare Transmittals")
			);
		});
	},
});
