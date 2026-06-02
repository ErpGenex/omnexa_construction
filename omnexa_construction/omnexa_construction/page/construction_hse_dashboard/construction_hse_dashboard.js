frappe.pages["construction-hse-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("HSE KPI Dashboard (ISO 45001)"),
		single_column: true,
	});
	page.add_field({
		fieldname: "company",
		fieldtype: "Link",
		options: "Company",
		label: __("Company"),
		default: frappe.defaults.get_user_default("Company"),
		change: () => load(page),
	});
	page.add_field({
		fieldname: "branch",
		fieldtype: "Link",
		options: "Branch",
		label: __("Branch"),
		change: () => load(page),
	});
	const $b = $(page.body);
	function load(page) {
		const company = page.fields_dict.company.get_value();
		if (!company) return;
		frappe.call({
			method: "omnexa_construction.hse_kpi_dashboard.get_hse_kpi_dashboard",
			args: { company, branch: page.fields_dict.branch.get_value() },
			callback(r) {
				const d = r.message || {};
				let html = '<div class="row">';
				[
					[__("ISO 45001 Score"), d.iso_45001_score],
					[__("Open NCR"), d.open_ncr],
					[__("SLA Breached"), d.ncr_sla_breached],
					[__("HSE Incidents"), d.hse_incidents_ytd],
					[__("Open PTW"), d.open_ptw],
					[__("LTIFR est."), d.ltifr_estimate],
				].forEach(([l, v]) => {
					html += `<div class="col-md-4 mb-3"><div class="card"><div class="card-body"><div class="text-muted small">${l}</div><div class="h4">${v}</div></div></div></div>`;
				});
				html += "</div>";
				$b.html(html);
			},
		});
	}
	load(page);
};
