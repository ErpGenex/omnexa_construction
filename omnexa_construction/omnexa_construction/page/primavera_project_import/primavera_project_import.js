frappe.pages["primavera-project-import"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Primavera Project Import"),
		single_column: true,
	});

	const state = { file_url: null, projects: [] };

	const $layout = $(`
		<div class="primavera-import-page">
			<p class="text-muted">${__(
				"Import projects from a Primavera P6 XER export file. Each project creates a Project Contract and Schedule Baseline."
			)}</p>
			<div class="row">
				<div class="col-md-4">
					<div class="form-group">
						<label>${__("Company")}</label>
						<div class="company-field"></div>
					</div>
				</div>
				<div class="col-md-4">
					<div class="form-group">
						<label>${__("Branch")}</label>
						<div class="branch-field"></div>
					</div>
				</div>
				<div class="col-md-4">
					<div class="form-group">
						<label>${__("Client")}</label>
						<div class="client-field"></div>
					</div>
				</div>
			</div>
			<div class="row">
				<div class="col-md-4">
					<div class="form-group">
						<label>${__("Contract Type")}</label>
						<div class="contract-type-field"></div>
					</div>
				</div>
				<div class="col-md-4">
					<div class="form-group">
						<label>${__("Contract Status")}</label>
						<div class="contract-status-field"></div>
					</div>
				</div>
			</div>
			<div class="form-group">
				<label><input type="checkbox" class="create-wbs" checked /> ${__("Create PM WBS Tasks")}</label>
			</div>
			<div class="form-group">
				<label><input type="checkbox" class="submit-baseline" checked /> ${__("Submit Schedule Baseline")}</label>
			</div>
			<div class="form-group">
				<label><input type="checkbox" class="skip-existing" checked /> ${__("Skip already imported projects")}</label>
			</div>
			<div class="form-group">
				<button class="btn btn-secondary btn-sm btn-upload-xer">${__("Upload XER File")}</button>
				<span class="file-label text-muted ml-2"></span>
			</div>
			<div class="preview-area mt-4"></div>
			<div class="mt-3">
				<button class="btn btn-primary btn-import" disabled>${__("Import Selected Projects")}</button>
			</div>
			<div class="results-area mt-4"></div>
		</div>
	`);
	page.main.append($layout);

	const company = frappe.ui.form.make_control({
		parent: $layout.find(".company-field"),
		df: { fieldtype: "Link", options: "Company", fieldname: "company", reqd: 1 },
		render_input: true,
	});
	const branch = frappe.ui.form.make_control({
		parent: $layout.find(".branch-field"),
		df: { fieldtype: "Link", options: "Branch", fieldname: "branch", reqd: 1 },
		render_input: true,
	});
	const client = frappe.ui.form.make_control({
		parent: $layout.find(".client-field"),
		df: { fieldtype: "Link", options: "Customer", fieldname: "client", reqd: 1 },
		render_input: true,
	});
	const contract_type = frappe.ui.form.make_control({
		parent: $layout.find(".contract-type-field"),
		df: {
			fieldtype: "Select",
			fieldname: "contract_type",
			options: "Lump Sum\nUnit Price\nCost Plus\nTurnkey (EPC)",
			default: "Lump Sum",
		},
		render_input: true,
	});
	const contract_status = frappe.ui.form.make_control({
		parent: $layout.find(".contract-status-field"),
		df: {
			fieldtype: "Select",
			fieldname: "contract_status",
			options: "Draft\nActive\nSuspended\nClosed\nCancelled",
			default: "Active",
		},
		render_input: true,
	});

	frappe.db.get_value("Company", { is_group: 0 }, "name").then((r) => {
		if (r?.message?.name) company.set_value(r.message.name);
	});

	$layout.find(".btn-upload-xer").on("click", () => {
		new frappe.ui.FileUploader({
			allow_multiple: false,
			restrictions: { allowed_file_types: [".xer", ".XER", ".txt"] },
			on_success(file) {
				state.file_url = file.file_url;
				$layout.find(".file-label").text(file.file_name || file.file_url);
				preview_file();
			},
		});
	});

	function preview_file() {
		if (!state.file_url) return;
		frappe.call({
			method: "omnexa_construction.primavera_project_import.preview_primavera_xer_import",
			args: { file_url: state.file_url },
			freeze: true,
			callback(r) {
				state.projects = r.message?.projects || [];
				render_preview();
			},
		});
	}

	function render_preview() {
		const $area = $layout.find(".preview-area");
		if (!state.projects.length) {
			$area.html(`<p class="text-muted">${__("No projects found in file.")}</p>`);
			$layout.find(".btn-import").prop("disabled", true);
			return;
		}
		let html = `<h5>${__("Projects in file")}</h5>
			<table class="table table-bordered table-sm">
			<thead><tr>
				<th><input type="checkbox" class="select-all-projects" checked /></th>
				<th>${__("P6 ID")}</th>
				<th>${__("Name")}</th>
				<th>${__("Start")}</th>
				<th>${__("End")}</th>
				<th>${__("Tasks")}</th>
				<th>${__("Value")}</th>
				<th>${__("Status")}</th>
			</tr></thead><tbody>`;
		state.projects.forEach((p, i) => {
			const disabled = p.already_imported ? "disabled" : "";
			const checked = p.already_imported ? "" : "checked";
			html += `<tr>
				<td><input type="checkbox" class="proj-select" data-idx="${i}" ${checked} ${disabled} /></td>
				<td>${frappe.utils.escape_html(p.proj_id)}</td>
				<td>${frappe.utils.escape_html(p.name)}</td>
				<td>${p.start_date || ""}</td>
				<td>${p.end_date || ""}</td>
				<td>${p.task_count || 0}</td>
				<td>${frappe.format(p.contract_value || 0, { fieldtype: "Currency" })}</td>
				<td>${p.already_imported ? __("Already imported") : __("Ready")}</td>
			</tr>`;
		});
		html += "</tbody></table>";
		$area.html(html);
		$layout.find(".btn-import").prop("disabled", false);

		$area.find(".select-all-projects").on("change", function () {
			const on = $(this).is(":checked");
			$area.find(".proj-select:not(:disabled)").prop("checked", on);
		});
	}

	$layout.find(".btn-import").on("click", () => {
		if (!state.file_url) {
			frappe.msgprint(__("Upload an XER file first."));
			return;
		}
		const company_val = company.get_value();
		const branch_val = branch.get_value();
		const client_val = client.get_value();
		if (!company_val || !branch_val || !client_val) {
			frappe.msgprint(__("Company, Branch, and Client are required."));
			return;
		}
		const selected = [];
		$layout.find(".proj-select:checked").each(function () {
			const idx = $(this).data("idx");
			if (state.projects[idx]) selected.push(state.projects[idx].proj_id);
		});
		if (!selected.length) {
			frappe.msgprint(__("Select at least one project."));
			return;
		}
		frappe.call({
			method: "omnexa_construction.primavera_project_import.import_primavera_xer_projects",
			args: {
				file_url: state.file_url,
				company: company_val,
				branch: branch_val,
				client: client_val,
				project_ids: JSON.stringify(selected),
				create_wbs_tasks: $layout.find(".create-wbs").is(":checked") ? 1 : 0,
				submit_baseline: $layout.find(".submit-baseline").is(":checked") ? 1 : 0,
				skip_existing: $layout.find(".skip-existing").is(":checked") ? 1 : 0,
				contract_type: contract_type.get_value(),
				contract_status: contract_status.get_value(),
			},
			freeze: true,
			callback(r) {
				const msg = r.message || {};
				let html = `<h5>${__("Import Results")}</h5><ul>`;
				(msg.results || []).forEach((row) => {
					if (row.status === "success") {
						html += `<li class="text-success">${frappe.utils.escape_html(row.proj_id)} → 
							<a href="/app/project-contract/${row.project_contract}">${row.project_contract}</a>
							(${row.tasks_imported} ${__("tasks")})</li>`;
					} else if (row.status === "skipped") {
						html += `<li class="text-muted">${frappe.utils.escape_html(row.proj_id)} — ${__("skipped")}</li>`;
					} else {
						html += `<li class="text-danger">${frappe.utils.escape_html(row.proj_id)} — ${frappe.utils.escape_html(row.message || "")}</li>`;
					}
				});
				html += `</ul><p><b>${__("Imported")}:</b> ${msg.imported || 0}</p>`;
				$layout.find(".results-area").html(html);
				frappe.show_alert({
					message: __("Imported {0} project(s)", [msg.imported || 0]),
					indicator: "green",
				});
				preview_file();
			},
		});
	});
};
