frappe.pages["construction-schedule-gantt"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Schedule Gantt"),
		single_column: true,
	});

	page.add_field({
		fieldname: "project_contract",
		label: __("Project Contract"),
		fieldtype: "Link",
		options: "Project Contract",
		change() {
			render_gantt(page);
		},
	});

	page.add_inner_button(__("Import XER"), () => open_xer_import(page));
	$(page.main).html(`<div class="gantt-page-wrap"></div>`);

	function render_gantt(page) {
		const contract = page.fields_dict.project_contract.get_value();
		const $wrap = $(page.main).find(".gantt-page-wrap");
		if (!contract) {
			$wrap.html(`<p class="text-muted">${__("Select a project contract.")}</p>`);
			return;
		}
		frappe.call({
			method: "omnexa_construction.schedule_gantt.get_schedule_gantt_data",
			args: { project_contract: contract },
			callback(r) {
				const data = r.message || {};
				draw_gantt($wrap, data);
			},
		});
	}
};

function draw_gantt($wrap, data) {
	const tasks = data.tasks || [];
	let html = `<h5>${frappe.utils.escape_html(data.baseline?.baseline_name || __("No active baseline"))}</h5>`;
	if (data.critical_path?.length) {
		html += `<p class="text-muted small">${__("Critical path")}: ${data.critical_path.map(frappe.utils.escape_html).join(" → ")}</p>`;
	}
	if (!tasks.length) {
		html += `<p class="text-muted">${__("No baseline tasks. Load from BOQ or import XER on Schedule Baseline.")}</p>`;
		$wrap.html(html);
		return;
	}

	html += `<div class="gantt-chart-area gantt-modern mb-3" style="min-height:320px;"></div>`;
	html += `<table class="table table-bordered table-sm"><thead><tr><th>${__("Task")}</th><th>${__("Start")}</th><th>${__("End")}</th><th>${__("Progress")}</th><th>${__("Critical")}</th></tr></thead><tbody>`;
	tasks.forEach((t) => {
		html += `<tr class="${t.is_critical ? "table-danger" : ""}"><td>${frappe.utils.escape_html(t.name)}</td><td>${t.start}</td><td>${t.end}</td><td>${t.progress || 0}%</td><td>${t.is_critical ? __("Yes") : ""}</td></tr>`;
	});
	html += "</tbody></table>";
	$wrap.html(html);

	const ganttTasks = tasks.map((t) => ({
		id: t.id,
		name: t.name,
		start: t.start,
		end: t.end,
		progress: t.progress || 0,
		dependencies: t.dependencies || "",
		custom_class: t.is_critical ? "bar-critical" : t.is_milestone ? "bar-milestone" : "",
	}));

	frappe.require(
		[
			"/assets/frappe/node_modules/frappe-gantt/dist/frappe-gantt.css",
			"/assets/frappe/node_modules/frappe-gantt/dist/frappe-gantt.min.js",
		],
		() => {
			const el = $wrap.find(".gantt-chart-area")[0];
			if (!el || typeof Gantt === "undefined") return;
			el.innerHTML = "";
			new Gantt(el, ganttTasks, {
				bar_height: 28,
				view_mode: "Week",
				date_format: "YYYY-MM-DD",
			});
		}
	);
}

function open_xer_import(page) {
	const contract = page.fields_dict.project_contract.get_value();
	if (!contract) {
		frappe.msgprint(__("Select a project contract first."));
		return;
	}
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Construction Schedule Baseline",
			filters: { project_contract: contract, is_active: 1, docstatus: 1 },
			fieldname: "name",
		},
		callback(r) {
			const baseline = r.message?.name;
			if (!baseline) {
				frappe.msgprint(__("No active Schedule Baseline for this contract."));
				return;
			}
			new frappe.ui.FileUploader({
				doctype: "Construction Schedule Baseline",
				docname: baseline,
				on_success(file) {
					frappe.call({
						method: "omnexa_construction.schedule_xer_import.import_xer_to_baseline",
						args: { baseline_name: baseline, file_url: file.file_url },
						callback(res) {
							frappe.show_alert({
								message: __("Imported {0} tasks", [res.message?.imported || 0]),
								indicator: "green",
							});
							frappe.pages["construction-schedule-gantt"].on_page_load(page.parent);
						},
					});
				},
			});
		},
	});
}
