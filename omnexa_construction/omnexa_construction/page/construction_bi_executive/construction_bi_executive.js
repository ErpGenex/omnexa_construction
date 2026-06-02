frappe.pages["construction-bi-executive"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Executive BI"),
		single_column: true,
	});

	page.add_field({
		fieldname: "company",
		label: __("Company"),
		fieldtype: "Link",
		options: "Company",
		reqd: 1,
		default: frappe.defaults.get_user_default("Company"),
		change() {
			load(page);
		},
	});

	page.add_field({
		fieldname: "branch",
		label: __("Branch"),
		fieldtype: "Link",
		options: "Branch",
		change() {
			load(page);
		},
	});

	const $body = $(page.body);
	$body.html(`<p class="text-muted">${__("Loading BI…")}</p>`);

	function load(page) {
		const company = page.fields_dict.company.get_value();
		if (!company) return;
		frappe.call({
			method: "omnexa_construction.executive_bi.get_executive_bi_dashboard",
			args: { company, branch: page.fields_dict.branch.get_value() },
			callback(r) {
				const d = r.message || {};
				let html = '<div class="row">';
				[
					[__("Contracts"), d.contract_count],
					[__("Portfolio BAC"), format_currency(d.total_bac)],
					[__("High risk (forecast)"), d.high_risk_contracts],
					[__("Open FIDIC"), d.open_fidic_notices],
					[__("Portfolio SPI"), (d.portfolio_spi || 0).toFixed(2)],
				].forEach(([label, val]) => {
					html += `<div class="col-md-4 mb-3"><div class="card"><div class="card-body"><div class="text-muted small">${label}</div><div class="h4">${val}</div></div></div></div>`;
				});
				html += "</div>";
				if (d.forecast_sample?.length) {
					html += `<h6 class="mt-3">${__("Cost / schedule forecast (sample)")}</h6>`;
					html += `<table class="table table-sm table-bordered"><thead><tr><th>${__("Contract")}</th><th>${__("EAC")}</th><th>${__("Cost risk")}</th><th>${__("Schedule risk")}</th></tr></thead><tbody>`;
					d.forecast_sample.forEach((f) => {
						html += `<tr><td>${f.project_contract}</td><td>${f.eac}</td><td>${f.cost_overrun_risk}</td><td>${f.schedule_overrun_risk}</td></tr>`;
					});
					html += "</tbody></table>";
				}
				$body.html(html);
			},
		});
	}

	load(page);
};
