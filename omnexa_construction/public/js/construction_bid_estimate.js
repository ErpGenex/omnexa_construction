frappe.ui.form.on("Construction Bid Estimate", {
	refresh(frm) {
		if (frm.is_new()) return;

		if (frm.doc.bid_package) {
			frm.add_custom_button(__("Compare Package Bids"), () => {
				frappe.set_route("query-report", "Construction Bid Comparison", {
					company: frm.doc.company,
					bid_package: frm.doc.bid_package,
				});
			});
		}

		frm.add_custom_button(__("Run Sensitivity Matrix"), () => {
			frappe.call({
				method: "omnexa_construction.bid_analysis.run_sensitivity_analysis",
				args: { bid_estimate: frm.doc.name },
				callback(r) {
					const rows = r.message || [];
					let html = "<table class='table table-bordered table-sm'><thead><tr><th>Scenario</th><th>Value</th><th>Cost</th><th>Margin %</th><th>Δ Margin</th></tr></thead><tbody>";
					rows.forEach((row) => {
						html += `<tr><td>${row.scenario}</td><td>${row.projected_contract_value}</td><td>${row.projected_cost}</td><td>${row.projected_margin_percent}</td><td>${row.margin_delta_vs_base}</td></tr>`;
					});
					html += "</tbody></table>";
					frappe.msgprint({ title: __("Sensitivity Analysis"), message: html, wide: true });
				},
			});
		});

		if (!["Awarded", "Negotiated"].includes(frm.doc.status)) return;
		if (frm.doc.linked_project_setup) return;

		frm.add_custom_button(__("Create Project Setup"), () => {
			frappe.call({
				method:
					"omnexa_construction.omnexa_construction.doctype.construction_bid_estimate.construction_bid_estimate.create_setup_from_bid_estimate",
				args: { bid_estimate: frm.doc.name },
				callback(r) {
					const setup = r.message?.setup_name;
					if (!setup) return;
					frappe.show_alert({
						message: __("Project Setup {0} created from this bid.", [setup]),
						indicator: "green",
					});
					frm.reload_doc();
				},
			});
		});
	},
});
