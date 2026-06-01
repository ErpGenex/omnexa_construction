frappe.pages["construction-executive-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Construction Executive Dashboard"),
		single_column: true,
	});

	page.add_field({
		fieldtype: "Link",
		fieldname: "company",
		label: __("Company"),
		options: "Company",
		reqd: 1,
		default: frappe.defaults.get_user_default("Company"),
		change() {
			load_dashboard(page);
		},
	});

	page.add_field({
		fieldtype: "Link",
		fieldname: "branch",
		label: __("Branch"),
		options: "Branch",
		change() {
			load_dashboard(page);
		},
	});

	const $body = $(page.body);
	$body.html('<div class="construction-exec-dashboard text-muted">' + __("Loading…") + "</div>");

	load_dashboard(page);

	function load_dashboard(page) {
		const company = page.fields_dict.company?.get_value();
		if (!company) {
			return;
		}
		const branch = page.fields_dict.branch?.get_value();
		frappe.call({
			method: "omnexa_construction.api.get_portfolio_dashboard",
			args: { company, branch },
			callback(r) {
				render_dashboard($body, r.message || {});
			},
		});
	}
};

function render_dashboard($body, data) {
	const cards = [
		{ label: __("Contracts"), value: data.contract_count || 0 },
		{ label: __("Portfolio BAC"), value: format_currency(data.total_bac) },
		{ label: __("Earned Value"), value: format_currency(data.total_ev) },
		{ label: __("Portfolio SPI"), value: (data.portfolio_spi || 0).toFixed(2) },
		{ label: __("Open IPC"), value: data.open_ipc || 0 },
		{ label: __("Open NCR"), value: data.open_ncr || 0 },
		{ label: __("Open RFI"), value: data.open_rfi || 0 },
		{ label: __("FIDIC Overdue"), value: data.fidic_overdue || 0 },
		{ label: __("Open Disputes"), value: data.open_disputes || 0 },
		{ label: __("Open EW (NEC4)"), value: data.open_early_warnings || 0 },
	];

	let html = '<div class="row">';
	cards.forEach((c) => {
		html +=
			'<div class="col-sm-6 col-md-4 col-lg-3 mb-3">' +
			'<div class="card"><div class="card-body">' +
			'<div class="text-muted small">' +
			c.label +
			"</div>" +
			'<div class="h4 mb-0">' +
			c.value +
			"</div></div></div></div>";
	});
	html += "</div>";

	if (data.contracts && data.contracts.length) {
		html += '<table class="table table-bordered table-sm mt-3"><thead><tr>' +
			"<th>" + __("Contract") + "</th><th>" + __("BAC") + "</th><th>EV</th><th>CPI</th><th>SPI</th><th>" + __("Status") + "</th>" +
			"</tr></thead><tbody>";
		data.contracts.forEach((row) => {
			html +=
				"<tr><td>" +
				(row.contract_title || row.project_contract) +
				"</td><td>" +
				format_currency(row.bac) +
				"</td><td>" +
				format_currency(row.ev) +
				"</td><td>" +
				(row.cpi || 0).toFixed(2) +
				"</td><td>" +
				(row.spi || 0).toFixed(2) +
				"</td><td>" +
				(row.status || "") +
				"</td></tr>";
		});
		html += "</tbody></table>";
	}

	$body.html(html);
}

function format_currency(value) {
	return frappe.format(value || 0, { fieldtype: "Currency" });
}
