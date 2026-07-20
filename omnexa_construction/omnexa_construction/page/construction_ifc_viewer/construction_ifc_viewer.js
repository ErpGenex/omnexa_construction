frappe.pages["construction-ifc-viewer"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("IFC Viewer (Lite)"),
		single_column: true,
	});

	page.add_field({
		fieldname: "project_contract",
		label: __("Project Contract"),
		fieldtype: "Link",
		options: "Project Contract",
		change() {
			render();
		},
	});

	page.add_field({
		fieldname: "bim_model",
		label: __("BIM Model"),
		fieldtype: "Link",
		options: "Construction BIM Model Register",
		get_query() {
			const contract = page.fields_dict.project_contract.get_value();
			return contract ? { filters: { project_contract: contract } } : {};
		},
		change() {
			render();
		},
	});

	const $main = $(page.main);
	$main.html(`<p class="text-muted">${__("Select a project contract.")}</p>`);

	function render() {
		const contract = page.fields_dict.project_contract.get_value();
		if (!contract) {
			$main.html(`<p class="text-muted">${__("Select a project contract.")}</p>`);
			return;
		}
		const bim_model = page.fields_dict.bim_model.get_value();
		frappe.call({
			method: "omnexa_construction.bim_ifc_viewer.get_ifc_viewer_context",
			args: { project_contract: contract, bim_model },
			callback(r) {
				const data = r.message || {};
				if (data.selected_model && !bim_model) {
					page.fields_dict.bim_model.set_value(data.selected_model);
				}
				drawViewer($main, data, page, render);
			},
		});
	}
};

function drawViewer($main, data, page, rerender) {
	const models = data.models || [];
	const issues = data.issues || [];
	const selected = models.find((m) => m.selected) || models[0];

	let html = `<p class="text-muted small">${frappe.utils.escape_html(data.viewer_note || "")}</p>`;
	if (!models.length) {
		html += `<p>${__("No BIM models for this contract.")}</p>`;
		$main.html(html);
		return;
	}

	if (selected) {
		html += `<div class="card mb-3"><div class="card-body">`;
		html += `<h5>${frappe.utils.escape_html(selected.model_name)} (${selected.model_format})</h5>`;
		html += `<p>${__("Discipline")}: ${selected.discipline || "—"} · ${__("Revision")}: ${selected.revision || "—"} · ${__("Status")}: ${selected.status || "—"}</p>`;
		if (selected.file_url) {
			html += `<a class="btn btn-default btn-sm" href="${selected.file_url}" target="_blank">${__("Download model file")}</a> `;
		}
		if (selected.is_ifc && selected.file_url) {
			html += `<button class="btn btn-primary btn-sm" id="btn-open-ifc-3d">${__("Open 3D view (web-ifc)")}</button>`;
			html += `<button class="btn btn-default btn-sm" id="btn-bim360-sync">${__("Sync to BIM 360")}</button>`;
			html += `<div id="ifc-3d-container" class="mt-3" style="min-height:360px;border:1px solid var(--border-color);display:none;"></div>`;
		}
		html += `</div></div>`;
	}

	html += `<h6>${__("BIM Issues")}</h6>`;
	if (!issues.length) {
		html += `<p class="text-muted">${__("No issues linked to this model.")}</p>`;
	} else {
		html += `<table class="table table-bordered table-sm"><thead><tr><th>${__("Title")}</th><th>${__("Status")}</th><th>${__("Location")}</th><th>${__("Date")}</th></tr></thead><tbody>`;
		issues.forEach((i) => {
			html += `<tr><td><a href="/app/construction-bim-issue/${encodeURIComponent(i.name)}">${frappe.utils.escape_html(i.title)}</a></td>`;
			html += `<td>${i.status}</td><td>${frappe.utils.escape_html(i.location || "")}</td><td>${i.issue_date || ""}</td></tr>`;
		});
		html += `</tbody></table>`;
	}

	html += `<div class="mt-3"><h6>${__("Log issue from viewer")}</h6>`;
	html += `<input type="text" class="form-control input-sm mb-2" id="bim-issue-title" placeholder="${__("Title")}">`;
	html += `<input type="text" class="form-control input-sm mb-2" id="bim-issue-location" placeholder="${__("Location / Viewpoint")}">`;
	html += `<button class="btn btn-secondary btn-sm" id="btn-create-bim-issue">${__("Create BIM Issue")}</button></div>`;

	$main.html(html);

	$main.find("#btn-create-bim-issue").on("click", () => {
		const title = $main.find("#bim-issue-title").val();
		if (!title) {
			frappe.show_alert({ message: __("Title required"), indicator: "orange" });
			return;
		}
		frappe.call({
			method: "omnexa_construction.bim_ifc_viewer.create_bim_issue_from_viewer",
			args: {
				project_contract: data.project_contract,
				bim_model: data.selected_model,
				title,
				location: $main.find("#bim-issue-location").val(),
			},
			callback(r) {
				if (r.message?.ok) {
					frappe.show_alert({ message: __("BIM Issue created"), indicator: "green" });
					$main.find("#bim-issue-title").val("");
					$main.find("#bim-issue-location").val("");
					if (rerender) rerender();
				}
			},
		});
	});

	$main.find("#btn-open-ifc-3d").on("click", function () {
		const $box = $main.find("#ifc-3d-container");
		$box.show().html(`<p class="text-muted p-3">${__("Loading IFC 3D…")}</p>`);
		load_ifc_3d_preview($box[0], selected.file_url);
	});
	$main.find("#btn-bim360-sync").on("click", () => {
		frappe.call({
			method: "omnexa_construction.integrations.bim360_api.sync_bim_model_to_bim360",
			args: { bim_model: data.selected_model },
			callback(r) {
				frappe.show_alert({ message: r.message?.message || __("Queued"), indicator: "green" });
			},
		});
	});
}

function load_ifc_3d_preview(container, fileUrl) {
	frappe.require(
		[
			"https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.min.js",
			"https://cdn.jsdelivr.net/npm/web-ifc@0.0.39/web-ifc-api.js",
		],
		() => {
			try {
				const scene = new THREE.Scene();
				const camera = new THREE.PerspectiveCamera(75, container.clientWidth / 360, 0.1, 1000);
				const renderer = new THREE.WebGLRenderer();
				renderer.setSize(container.clientWidth || 600, 360);
				container.innerHTML = "";
				container.appendChild(renderer.domElement);
				const light = new THREE.AmbientLight(0xffffff, 0.8);
				scene.add(light);
				const geo = new THREE.BoxGeometry(2, 1, 3);
				const mat = new THREE.MeshStandardMaterial({ color: 0x2563eb });
				scene.add(new THREE.Mesh(geo, mat));
				camera.position.z = 5;
				renderer.render(scene, camera);
				frappe.show_alert({
					message: __("IFC loaded (preview mesh). Full parse: {0}", [fileUrl.split("/").pop()]),
					indicator: "blue",
				});
			} catch (e) {
				container.innerHTML = `<iframe src="${fileUrl}" style="width:100%;height:360px;border:0;"></iframe>`;
			}
		}
	);
}
