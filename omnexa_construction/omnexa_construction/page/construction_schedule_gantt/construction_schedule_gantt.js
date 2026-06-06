frappe.pages["construction-schedule-gantt"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Schedule Gantt"),
		single_column: true,
	});

	const $body = $(page.body);
	const $toolbar = $(`<div class="construction-gantt-toolbar" style="margin-bottom:12px"></div>`).appendTo($body);
	const $wrap = $(`<div class="gantt-page-wrap"></div>`).appendTo($body);

	const project_control = frappe.ui.form.make_control({
		parent: $toolbar,
		df: {
			fieldtype: "Link",
			options: "Project Contract",
			label: __("Project Contract"),
			fieldname: "project_contract",
			reqd: 1,
		},
		render_input: true,
	});
	project_control.$wrapper.appendTo($toolbar);
	project_control.refresh();

	if (frappe.route_options && frappe.route_options.project_contract) {
		project_control.set_value(frappe.route_options.project_contract);
	}

	page.set_primary_action(__("Load schedule"), () => render_gantt());
	page.add_inner_button(__("Import XER"), () => open_xer_import(project_control));

	project_control.$input.on("change", () => render_gantt());

	function render_gantt() {
		const contract = project_control.get_value();
		if (!contract) {
			$wrap.html(`<p class="text-muted">${__("Select a project contract.")}</p>`);
			return;
		}
		frappe.call({
			method: "omnexa_construction.schedule_gantt.get_schedule_gantt_data",
			args: { project_contract: contract },
			freeze: true,
			callback(r) {
				draw_gantt($wrap, r.message || {});
			},
		});
	}

	if (project_control.get_value()) {
		render_gantt();
	}
};

function draw_gantt($wrap, data) {
	const tasks = (data.tasks || []).filter((t) => t.start && t.end && t.start !== "None" && t.end !== "None");
	let html = `<h5>${frappe.utils.escape_html(data.baseline?.baseline_name || data.baseline?.name || __("No baseline"))}</h5>`;
	if (data.baseline_is_draft) {
		html += `<p class="text-warning small">${__(
			"Showing draft baseline — submit the baseline to lock it for production reporting."
		)}</p>`;
	}
	if (data.critical_path?.length) {
		html += `<p class="text-muted small">${__("Critical path")}: ${data.critical_path
			.map(frappe.utils.escape_html)
			.join(" → ")}</p>`;
	}
	if (!tasks.length) {
		html += `<p class="text-muted">${__(
			"No baseline tasks. Open Schedule Baseline → Load Tasks from BOQ, or import XER."
		)}</p>`;
		$wrap.html(html);
		return;
	}

	html += `<div class="construction-gantt-chart mb-3"></div>`;
	html += `<table class="table table-bordered table-sm"><thead><tr><th>${__("Task")}</th><th>${__("Start")}</th><th>${__("End")}</th><th>${__("Progress")}</th><th>${__("Critical")}</th></tr></thead><tbody>`;
	tasks.forEach((t) => {
		html += `<tr class="${t.is_critical ? "table-danger" : ""}"><td>${frappe.utils.escape_html(
			t.name
		)}</td><td>${t.start}</td><td>${t.end}</td><td>${t.progress || 0}%</td><td>${
			t.is_critical ? __("Yes") : ""
		}</td></tr>`;
	});
	html += "</tbody></table>";
	$wrap.html(html);

	render_bar_chart($wrap.find(".construction-gantt-chart"), tasks);
}

function render_bar_chart($chart, tasks) {
	$chart.empty();
	let t0 = tasks[0].start;
	let t1 = tasks[0].end;
	tasks.forEach((t) => {
		if (t.start < t0) t0 = t.start;
		if (t.end > t1) t1 = t.end;
	});
	const rangeDays = Math.max(1, frappe.datetime.get_diff(t1, t0) + 1);

	tasks.forEach((task) => {
		const startOff = frappe.datetime.get_diff(task.start, t0);
		const barDays = Math.max(1, frappe.datetime.get_diff(task.end, task.start) + 1);
		const leftPct = (startOff / rangeDays) * 100;
		const widthPct = Math.max(0.4, (barDays / rangeDays) * 100);
		const row = $(`<div class="construction-gantt-row"></div>`).css({
			display: "flex",
			"align-items": "center",
			margin: "6px 0",
			"border-bottom": "1px solid var(--border-color)",
		});
		row.append(
			$("<div></div>")
				.css({ width: "220px", "flex-shrink": 0, "padding-right": "10px" })
				.html(`<strong>${frappe.utils.escape_html(task.name)}</strong>`)
		);
		const track = $("<div></div>").css({
			flex: 1,
			position: "relative",
			height: "24px",
			background: "var(--control-bg)",
			"border-radius": "4px",
		});
		const color = task.is_critical ? "var(--red-500)" : task.is_milestone ? "var(--orange-500)" : "var(--blue-500)";
		track.append(
			$("<div></div>").css({
				position: "absolute",
				left: leftPct + "%",
				width: widthPct + "%",
				height: "100%",
				background: color,
				opacity: 0.88,
				"border-radius": "3px",
			}).attr("title", `${task.start} → ${task.end} · ${task.progress || 0}%`)
		);
		row.append(track);
		$chart.append(row);
	});
}

function open_xer_import(project_control) {
	const contract = project_control.get_value();
	if (!contract) {
		frappe.msgprint(__("Select a project contract first."));
		return;
	}
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Construction Schedule Baseline",
			filters: { project_contract: contract, is_active: 1 },
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
							frappe.set_route("construction-schedule-gantt", { project_contract: contract });
						},
					});
				},
			});
		},
	});
}
