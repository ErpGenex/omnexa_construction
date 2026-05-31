frappe.provide("omnexa_construction");

omnexa_construction.ProjectWizard = class ProjectWizard {
	constructor(page) {
		this.page = page;
		this.step = 1;
		this.setup_name = frappe.utils.get_query_params().setup || null;
		this.building_types = [];
		this.setup = {};
		this.make_layout();
		this.load();
	}

	make_layout() {
		this.wrapper = $(`<div class="construction-wizard"></div>`).appendTo(this.page.main);
		this.steps_bar = $(`<div class="wizard-steps mb-4"></div>`).appendTo(this.wrapper);
		this.body = $(`<div class="wizard-body"></div>`).appendTo(this.wrapper);
		this.footer = $(`<div class="wizard-footer mt-4 d-flex justify-content-between"></div>`).appendTo(
			this.wrapper
		);
		this.btn_prev = this.page.set_primary_action(__("Previous"), () => this.prev(), "prev-btn");
		this.page.btn_primary.hide();
		this.btn_save = this.page.add_inner_button(__("Save Draft"), () => this.save_draft(), __("Actions"));
		this.btn_edit = this.page.add_inner_button(__("Full Editor"), () => this.open_form(), __("Actions"));
		this.btn_next = this.page.add_inner_button(__("Next"), () => this.next(), __("Actions"));
		this.btn_generate = this.page.add_inner_button(__("Generate Project"), () => this.generate(), __("Actions"));
		this.btn_generate.hide();
		this.page.add_inner_button(
			__("عربي"),
			() => {
				omnexa_construction.i18n.set_lang("ar");
				this.render_steps_bar();
				this.render_step();
			},
			omnexa_construction.i18n.t("Language")
		);
		this.page.add_inner_button(
			__("EN"),
			() => {
				omnexa_construction.i18n.set_lang("en");
				this.render_steps_bar();
				this.render_step();
			},
			omnexa_construction.i18n.t("Language")
		);
		this.render_steps_bar();
	}

	render_steps_bar() {
		const labels = [
			omnexa_construction.i18n.t("Identity"),
			omnexa_construction.i18n.t("Asset Type"),
			omnexa_construction.i18n.t("Specifications"),
			omnexa_construction.i18n.t("Financials"),
			omnexa_construction.i18n.t("BOQ"),
			omnexa_construction.i18n.t("Phases & IPC"),
			omnexa_construction.i18n.t("Detail Pricing"),
			omnexa_construction.i18n.t("Assignments"),
			omnexa_construction.i18n.t("Generate"),
		];
		this.steps_bar.empty();
		labels.forEach((label, i) => {
			const n = i + 1;
			const cls = n === this.step ? "badge badge-primary" : n < this.step ? "badge badge-success" : "badge badge-secondary";
			this.steps_bar.append(`<span class="${cls} mr-2 p-2">${n}. ${label}</span>`);
		});
	}

	load() {
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.get_wizard_context",
			args: { setup_name: this.setup_name },
			freeze: true,
			callback: (r) => {
				if (!r.message) return;
				this.setup = r.message.setup;
				this.setup_name = this.setup.name;
				this.building_types = r.message.building_types || [];
				this.step = cint(this.setup.wizard_step) || 1;
				this.render_step();
			},
		});
	}

	save_step(callback) {
		const data = this.collect_step_data();
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.save_wizard_step",
			args: { setup_name: this.setup_name, step: this.step, data: data },
			freeze: true,
			callback: (r) => {
				if (r.message) {
					this.step = r.message.wizard_step;
				}
				callback && callback();
			},
		});
	}

	collect_step_data() {
		const d = {};
		this.body.find("[data-field]").each(function () {
			const $el = $(this);
			const key = $el.data("field");
			if ($el.is(":checkbox")) {
				d[key] = $el.is(":checked") ? 1 : 0;
			} else {
				d[key] = $el.val();
			}
		});
		return d;
	}

	render_step() {
		this.render_steps_bar();
		this.body.empty();
		this.btn_prev.toggle(this.step > 1);
		this.btn_next.toggle(this.step < 8);
		this.btn_generate.toggle(this.step === 8);

		if (this.step === 1) this.render_step1();
		else if (this.step === 2) this.render_step2();
		else if (this.step === 3) this.render_step3();
		else if (this.step === 4) this.render_step4_financials();
		else if (this.step === 5) this.render_step5_boq();
		else if (this.step === 6) this.render_step6_phases_ipc();
		else if (this.step === 7) this.render_step7_details();
		else if (this.step === 8) this.render_step8_generate();
	}

	field_row(label, html) {
		return `<div class="form-group col-md-6"><label class="control-label">${label}</label>${html}</div>`;
	}

	render_step1() {
		const s = this.setup;
		this.body.html(`
			<div class="row">
				${this.field_row(__("Company"), `<input class="form-control" data-field="company" value="${frappe.utils.escape_html(s.company || "")}" readonly>`)}
				${this.field_row(__("Branch"), `<input class="form-control" data-field="branch" value="${frappe.utils.escape_html(s.branch || "")}" readonly>`)}
				${this.field_row(__("Client"), `<input class="form-control" data-field="client" value="${frappe.utils.escape_html(s.client || "")}">`)}
				${this.field_row(__("Project Title"), `<input class="form-control" data-field="contract_title" value="${frappe.utils.escape_html(s.contract_title || "")}">`)}
				${this.field_row(__("Contract Type"), `<select class="form-control" data-field="contract_type">
					<option ${s.contract_type === "Turnkey (EPC)" ? "selected" : ""}>Turnkey (EPC)</option>
					<option ${s.contract_type === "Lump Sum" ? "selected" : ""}>Lump Sum</option>
					<option ${s.contract_type === "Unit Price" ? "selected" : ""}>Unit Price</option>
				</select>`)}
				${this.field_row(__("Site Location"), `<textarea class="form-control" data-field="site_location" rows="2">${frappe.utils.escape_html(s.site_location || "")}</textarea>`)}
			</div>
		`);
		this._link_field("client", "Customer", s.client);
	}

	render_step2() {
		const s = this.setup;
		const opts = (this.building_types || [])
			.map(
				(b) =>
					`<option value="${b.code}" ${s.building_type === b.code ? "selected" : ""}>${frappe.utils.escape_html(b.label_en)} / ${frappe.utils.escape_html(b.label_ar || "")}${b.has_template ? "" : " *"}</option>`
			)
			.join("");
		this.body.html(`
			<div class="row">
				${this.field_row(__("Building / Project Type"), `<select class="form-control" data-field="building_type"><option value=""></option>${opts}</select>`)}
				${this.field_row(__("BOQ Template"), `<input class="form-control" data-field="boq_template" value="${frappe.utils.escape_html(s.boq_template || "")}" readonly>`)}
				${this.field_row(__("Segment"), `<input class="form-control" data-field="project_segment" value="${frappe.utils.escape_html(s.project_segment || "")}" readonly>`)}
				${this.field_row(__("Governing Standard"), `<input class="form-control" data-field="governing_standard" value="${frappe.utils.escape_html(s.governing_standard || "")}">`)}
			</div>
			<p class="text-muted small mt-2">${__("Selecting a type loads the default BOQ template, phases, detail pricing, and delivery dates when you build the BOQ.")}</p>
		`);
		this.body.find('[data-field="building_type"]').on("change", () => {
			this.save_step(() => {
				frappe.call({
					method: "omnexa_construction.wizard.wizard_api.load_building_type_template",
					args: { setup_name: this.setup_name },
					callback: (r) => {
						if (r.message) {
							Object.assign(this.setup, r.message);
							this.render_step2();
						}
					},
				});
			});
		});
	}

	render_step3() {
		const s = this.setup;
		const is_road = ["urban_road", "highway"].includes(s.building_type);
		const building_fields = is_road
			? `
				${this.field_row(__("Road Length (m)"), `<input type="number" class="form-control" data-field="road_length_m" value="${s.road_length_m || 800}">`)}
				${this.field_row(__("Road Width (m)"), `<input type="number" class="form-control" data-field="road_width_m" value="${s.road_width_m || 12}">`)}
			`
			: `
				${this.field_row(__("Plot Area (m²)"), `<input type="number" class="form-control" data-field="plot_area_m2" value="${s.plot_area_m2 || 600}">`)}
				${this.field_row(__("Gross Floor Area (m²)"), `<input type="number" class="form-control" data-field="gross_floor_area_m2" value="${s.gross_floor_area_m2 || 450}">`)}
				${this.field_row(__("Floors"), `<input type="number" class="form-control" data-field="number_of_floors" value="${s.number_of_floors || 2}">`)}
				${this.field_row(__("Basements"), `<input type="number" class="form-control" data-field="basement_levels" value="${s.basement_levels || 0}">`)}
				${this.field_row(__("Units"), `<input type="number" class="form-control" data-field="unit_count" value="${s.unit_count || 1}">`)}
			`;
		this.body.html(`
			<div class="row">
				${this.field_row(__("Quality Tier"), `<select class="form-control" data-field="quality_tier">
					<option ${s.quality_tier === "Economy" ? "selected" : ""}>Economy</option>
					<option ${(!s.quality_tier || s.quality_tier === "Standard") ? "selected" : ""}>Standard</option>
					<option ${s.quality_tier === "Premium" ? "selected" : ""}>Premium</option>
					<option ${s.quality_tier === "Luxury" ? "selected" : ""}>Luxury</option>
				</select>`)}
				${building_fields}
			</div>
		`);
	}

	render_step4_financials() {
		const s = this.setup;
		this.body.html(`
			<div class="row">
				${this.field_row(__("Retention %"), `<input type="number" class="form-control" data-field="retention_percent" value="${s.retention_percent || 5}">`)}
				${this.field_row(__("Advance %"), `<input type="number" class="form-control" data-field="advance_payment_percent" value="${s.advance_payment_percent || 10}">`)}
				${this.field_row(__("Default IPC Discount %"), `<input type="number" class="form-control" data-field="default_discount_percent" value="${s.default_discount_percent || 0}">`)}
				${this.field_row(__("Contract LD / day"), `<input type="number" class="form-control" data-field="liquidated_damages_per_day" value="${s.liquidated_damages_per_day || 0}">`)}
				${this.field_row(__("LD cap % of contract"), `<input type="number" class="form-control" data-field="liquidated_damages_cap_percent" value="${s.liquidated_damages_cap_percent || 10}">`)}
				${this.field_row(__("Planned Start"), `<input type="date" class="form-control" data-field="planned_start" value="${s.planned_start || ""}">`)}
				${this.field_row(__("Planned Completion"), `<input type="date" class="form-control" data-field="planned_completion" value="${s.planned_completion || ""}">`)}
				${this.field_row(omnexa_construction.i18n.t("Regional Cost Factor"), `<input class="form-control" data-field="regional_cost_factor" value="${frappe.utils.escape_html(s.regional_cost_factor || "")}" placeholder="Link: Regional Cost Factor">`)}
				${this.field_row(omnexa_construction.i18n.t("Site Region Code"), `<input class="form-control" data-field="site_region" value="${frappe.utils.escape_html(s.site_region || "")}" placeholder="e.g. EG-CAIRO">`)}
			</div>
		`);
	}

	render_step5_boq() {
		const tpl = frappe.utils.escape_html(this.setup.boq_template || "");
		this.body.html(`<p>${__("Click Next to load the full default package for")} <b>${tpl}</b>: ${__("BOQ lines, delivery phases, handover dates, detail pricing, and IPC schedule.")}</p>`);
	}

	render_boq_table(lines) {
		let rows = (lines || [])
			.map((r) => {
				const indent = r.parent_cost_code ? "&nbsp;&nbsp;" : "";
				const cost = format_currency(r.planned_cost, this.setup.contract_currency);
				return `<tr><td>${indent}${frappe.utils.escape_html(r.cost_code)}</td><td>${frappe.utils.escape_html(r.item_description)}</td><td>${r.quantity || ""}</td><td>${cost}</td></tr>`;
			})
			.join("");
		return `<table class="table table-bordered table-sm"><thead><tr><th>${__("Code")}</th><th>${__("Description")}</th><th>${__("Qty")}</th><th>${__("Planned")}</th></tr></thead><tbody>${rows}</tbody></table>`;
	}

	render_phases_table(phases) {
		const rows = (phases || [])
			.map(
				(p) =>
					`<tr><td>${frappe.utils.escape_html(p.phase_code)}</td><td>${frappe.utils.escape_html(p.phase_name)}</td><td>${p.planned_finish || ""}</td><td>${p.handover_date || ""}</td><td>${p.weight_percent || ""}%</td></tr>`
			)
			.join("");
		return `<table class="table table-bordered table-sm"><thead><tr><th>${__("Phase")}</th><th>${__("Name")}</th><th>${__("Finish")}</th><th>${__("Handover")}</th><th>${__("Weight")}</th></tr></thead><tbody>${rows}</tbody></table>`;
	}

	render_ipc_table(ipc_plan) {
		const rows = (ipc_plan || [])
			.map(
				(i) =>
					`<tr><td>${i.ipc_number}</td><td>${i.ipc_date || ""}</td><td>${i.cumulative_completion_percent || ""}%</td><td>${format_currency(i.net_amount, this.setup.contract_currency)}</td><td>${i.retention_percent || ""}%</td><td>${i.discount_percent || 0}%</td></tr>`
			)
			.join("");
		return `<table class="table table-bordered table-sm"><thead><tr><th>#</th><th>${__("Date")}</th><th>${__("Cum. %")}</th><th>${__("Net")}</th><th>${__("Retention")}</th><th>${__("Discount")}</th></tr></thead><tbody>${rows}</tbody></table>`;
	}

	render_step6_phases_ipc() {
		const total = format_currency(this.setup.estimated_contract_value, this.setup.contract_currency);
		this.body.html(`
			<h5>${__("Contract Value")}: ${total}</h5>
			<h6>${__("Delivery Phases")}</h6>
			${this.render_phases_table(this.setup.phases)}
			<h6 class="mt-3">${__("IPC Payment Schedule")}</h6>
			${this.render_ipc_table(this.setup.ipc_plan)}
		`);
	}

	render_step7_details() {
		const lines = this.setup.boq_lines || [];
		const details = this.setup.boq_details || [];
		const total = format_currency(this.setup.estimated_contract_value, this.setup.contract_currency);
		this.body.html(`
			<h5>${__("Estimated Contract Value")}: ${total}</h5>
			<p>${__("{0} BOQ lines, {1} detail pricing rows with per-detail LD.", [lines.length, details.length])}</p>
			${this.render_boq_table(lines)}
			<div class="mt-3">
				<a class="btn btn-default btn-sm" href="/app/construction-project-setup/${this.setup_name}">
					${__("Edit details, LD per line, and unit rates in full form")}
				</a>
			</div>
		`);
	}

	render_assignments_table(assignments) {
		let rows = (assignments || [])
			.map(
				(a) =>
					`<tr><td>${frappe.utils.escape_html(a.trade_package_code || "")}</td><td>${frappe.utils.escape_html(a.scope_notes || "")}</td><td><input class="form-control form-control-sm assign-party" data-trade="${frappe.utils.escape_html(a.trade_package_code || "")}" placeholder="${__("Supplier link")}"></td></tr>`
			)
			.join("");
		return `<table class="table table-bordered table-sm"><thead><tr><th>${__("Trade")}</th><th>${__("Scope")}</th><th>${__("Subcontractor (Supplier)")}</th></tr></thead><tbody>${rows}</tbody></table>`;
	}

	render_step8_generate() {
		const total = format_currency(this.setup.estimated_contract_value, this.setup.contract_currency);
		this.body.html(`
			<div class="alert alert-info">
				<h5>${__("Ready to generate")}</h5>
				<p>${__("Project")}: <b>${frappe.utils.escape_html(this.setup.contract_title || "")}</b></p>
				<p>${__("Estimated value")}: <b>${total}</b></p>
				<p>${__("Creates: Contract, BOQ + detail breakdown, phases dates, LD per line/detail, draft IPCs with retention & discount, subcontracts, PRs, transmittal.")}</p>
			</div>
			${this.render_assignments_table(this.setup.assignments)}
		`);
	}

	save_draft() {
		this.save_step(() => {
			frappe.show_alert({ message: __("Draft saved: {0}", [this.setup_name]), indicator: "green" });
		});
	}

	open_form() {
		frappe.set_route("Form", "Construction Project Setup", this.setup_name);
	}

	_link_field(fieldname, doctype, value) {
		const $input = this.body.find(`[data-field="${fieldname}"]`);
		$input.attr("placeholder", __("Link {0}", [doctype]));
		if (value) return;
		$input.on("focus", () => {
			frappe.prompt(
				[{ fieldname, fieldtype: "Link", options: doctype, label: __(doctype), reqd: 1 }],
				(values) => {
					$input.val(values[fieldname]);
				},
				__("Select {0}", [doctype])
			);
		});
	}

	prev() {
		if (this.step <= 1) return;
		this.step -= 1;
		this.render_step();
	}

	next() {
		this.save_step(() => {
			if (this.step === 4) {
				frappe.call({
					method: "omnexa_construction.wizard.project_bundle.preview_boq",
					args: { setup_name: this.setup_name },
					freeze: true,
					callback: () => {
						this.reload_setup(() => {
							this.step = 5;
							this.render_step();
						});
					},
				});
				return;
			}
			if (this.step === 5) {
				this.step = 6;
				this.reload_setup(() => this.render_step());
				return;
			}
			if (this.step === 6) {
				this.step = 7;
				this.reload_setup(() => this.render_step());
				return;
			}
			if (this.step === 7) {
				frappe.call({
					method: "omnexa_construction.wizard.project_bundle.suggest_assignments",
					args: { setup_name: this.setup_name },
					freeze: true,
					callback: () => {
						this.step = 8;
						this.reload_setup(() => this.render_step());
					},
				});
				return;
			}
			if (this.step < 8) {
				this.step += 1;
				this.render_step();
			}
		});
	}

	reload_setup(callback) {
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.get_wizard_context",
			args: { setup_name: this.setup_name },
			callback: (r) => {
				if (r.message) {
					this.setup = r.message.setup;
				}
				callback && callback();
			},
		});
	}

	generate() {
		frappe.confirm(__("Create project documents now?"), () => {
			frappe.call({
				method: "omnexa_construction.wizard.project_bundle.create_project_bundle",
				args: { setup_name: this.setup_name },
				freeze: true,
				callback: (r) => {
					if (!r.message) return;
					frappe.msgprint({
						title: __("Project Created"),
						message: __("Contract {0} with {1} BOQ lines.", [
							r.message.project_contract,
							(r.message.boq_items || []).length,
						]),
						indicator: "green",
					});
					frappe.set_route("Form", "Project Contract", r.message.project_contract);
				},
			});
		});
	}
};
