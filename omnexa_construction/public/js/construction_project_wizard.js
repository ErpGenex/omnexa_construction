frappe.provide("omnexa_construction");

omnexa_construction.ProjectWizard = class ProjectWizard {
	constructor(page) {
		this.page = page;
		this.step = 1;
		this.setup_name = frappe.utils.get_query_params().setup || null;
		this.building_types = [];
		this.setup = {};
		this.t = (key) => omnexa_construction.i18n.t(key);
		this._busy = false;
		this._frozen = false;
		this.make_layout();
		this.render_loading_skeleton();
		this.load();
	}

	wizard_context_args() {
		// Company/branch are resolved on the server from desk session context.
		return {
			setup_name: this.setup_name || null,
		};
	}

	clear_setup_query_param() {
		if (!window.history || !window.history.replaceState) {
			return;
		}
		const params = frappe.utils.get_query_params();
		if (!params.setup) {
			return;
		}
		delete params.setup;
		const qs = $.param(params);
		const path = window.location.pathname + (qs ? `?${qs}` : "");
		window.history.replaceState({}, "", path);
	}

	server_error_message(r, fallback) {
		if (r && typeof r.message === "string" && r.message.trim()) {
			return r.message;
		}
		if (r && r.message && typeof r.message === "object" && r.message.exc) {
			return r.message.exc;
		}
		if (r && r._server_messages) {
			try {
				const rows = JSON.parse(r._server_messages);
				for (const row of rows) {
					const parsed = typeof row === "string" ? JSON.parse(row) : row;
					if (parsed && parsed.message) {
						return parsed.message;
					}
				}
			} catch (e) {
				/* ignore parse errors */
			}
		}
		return fallback;
	}

	render_loading_skeleton() {
		this.body.html(`
			<div class="wizard-loading text-muted">
				<p class="mb-2"><i class="fa fa-spinner fa-spin"></i> ${this.t("Loading wizard...")}</p>
			</div>
		`);
	}

	set_busy(is_busy, message) {
		this._busy = Boolean(is_busy);
		if (this.$btn_next) {
			this.$btn_next.prop("disabled", this._busy);
		}
		if (this.$btn_prev) {
			this.$btn_prev.prop("disabled", this._busy);
		}
		if (this.$btn_generate) {
			this.$btn_generate.prop("disabled", this._busy);
		}
		if (this._busy) {
			if (!this._frozen) {
				frappe.dom.freeze(message || "");
				this._frozen = true;
			}
			return;
		}
		if (this._frozen) {
			frappe.dom.unfreeze();
			this._frozen = false;
		}
	}

	switch_lang(lang) {
		omnexa_construction.i18n.set_lang(lang);
		this.page.set_title(this.t("Construction Project Wizard"));
		omnexa_construction.i18n.apply_page_direction(this.wrapper);
		this.refresh_action_labels();
		this.render_steps_bar();
		this.render_step();
	}

	refresh_action_labels() {
		if (this.$btn_prev) {
			this.$btn_prev.text(this.t("Previous"));
		}
		if (this.btn_save) {
			this.btn_save.text(this.t("Save Draft"));
		}
		if (this.btn_edit) {
			this.btn_edit.text(this.t("Full Editor"));
		}
		if (this.$btn_next) {
			const arrow = omnexa_construction.i18n.get_lang() === "ar" ? "← " : " →";
			this.$btn_next.text(
				omnexa_construction.i18n.get_lang() === "ar"
					? `${arrow}${this.t("Next")}`
					: `${this.t("Next")}${arrow}`
			);
		}
		if (this.$btn_generate) {
			this.$btn_generate.text(this.t("Generate Project"));
		}
	}

	update_footer_buttons() {
		if (!this.$btn_prev || !this.$btn_next || !this.$btn_generate) {
			return;
		}
		this.$btn_prev.toggle(this.step > 1);
		this.$btn_next.toggle(this.step < 8);
		this.$btn_generate.toggle(this.step === 8);
		this.refresh_action_labels();
	}

	make_layout() {
		this.wrapper = $(`<div class="construction-wizard"></div>`).appendTo(this.page.main);
		this.steps_bar = $(`<div class="wizard-steps mb-4"></div>`).appendTo(this.wrapper);
		this.body = $(`<div class="wizard-body"></div>`).appendTo(this.wrapper);

		this.footer_bar = $(`
			<div class="wizard-footer-bar">
				<div class="footer-left">
					<button type="button" class="btn btn-default btn-lg wizard-btn-prev">${this.t("Previous")}</button>
				</div>
				<div class="footer-right">
					<button type="button" class="btn btn-primary btn-lg wizard-btn-next">${this.t("Next")} →</button>
					<button type="button" class="btn btn-success btn-lg wizard-btn-generate">${this.t("Generate Project")}</button>
				</div>
			</div>
		`).appendTo(this.wrapper);

		this.$btn_prev = this.footer_bar.find(".wizard-btn-prev");
		this.$btn_next = this.footer_bar.find(".wizard-btn-next");
		this.$btn_generate = this.footer_bar.find(".wizard-btn-generate");
		this.$btn_prev.on("click", () => this.prev());
		this.$btn_next.on("click", () => this.next());
		this.$btn_generate.on("click", () => this.generate());

		if (this.page.btn_primary) {
			this.page.btn_primary.hide();
		}
		this.btn_save = this.page.add_inner_button(this.t("Save Draft"), () => this.save_draft(), this.t("Actions") || __("Actions"));
		this.btn_edit = this.page.add_inner_button(this.t("Full Editor"), () => this.open_form(), this.t("Actions") || __("Actions"));
		this.page.add_inner_button(this.t("Arabic"), () => this.switch_lang("ar"), this.t("Language"));
		this.page.add_inner_button(this.t("English"), () => this.switch_lang("en"), this.t("Language"));
		omnexa_construction.i18n.apply_page_direction(this.wrapper);
		this.render_steps_bar();
		this.update_footer_buttons();
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
			omnexa_construction.i18n.t("Generate"),
		];
		this.steps_bar.empty();
		labels.forEach((label, i) => {
			const n = i + 1;
			const cls = n === this.step ? "badge badge-primary" : n < this.step ? "badge badge-success" : "badge badge-secondary";
			this.steps_bar.append(`<span class="${cls} mr-2 p-2">${n}. ${label}</span>`);
		});
	}

	show_wizard_error(r, fallback) {
		frappe.msgprint({
			title: this.t("Wizard"),
			message: this.server_error_message(r, fallback),
			indicator: "red",
		});
	}

	load() {
		this.set_busy(true, this.t("Loading wizard..."));
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.get_wizard_context",
			args: this.wizard_context_args(),
			freeze: false,
			callback: (r) => this.handle_load_response(r),
			error: (r) => {
				this.set_busy(false);
				this.render_load_error(r);
			},
		});
	}

	handle_load_response(r) {
		this.set_busy(false);
		try {
			if (r.exc) {
				this.render_load_error(r);
				return;
			}
			const payload =
				r.message && typeof r.message === "object" && !Array.isArray(r.message) ? r.message : null;
			if (!payload || !payload.setup) {
				if (this.setup_name) {
					this.setup_name = null;
					this.clear_setup_query_param();
					this.load();
					return;
				}
				this.render_load_error(r);
				return;
			}
			this.setup = payload.setup || {};
			this.setup_name = this.setup.name || this.setup_name;
			if (!this.setup_name) {
				this.render_load_error(r);
				return;
			}
			this.building_types = payload.building_types || [];
			this.step = Math.min(8, Math.max(1, frappe.utils.cint(this.setup.wizard_step) || 1));
			if (this.step >= 3 && !this.setup.building_type) {
				this.step = 2;
			}
			this.render_step();
		} catch (e) {
			console.error("Construction wizard load failed", e);
			this.setup = this.setup || {};
			this.show_wizard_error(
				r,
				this.t("Could not load the wizard. Check company/branch context and try again.")
			);
			this.step = 1;
			this.render_step();
		}
	}

	render_load_error(r) {
		this.set_busy(false);
		this.show_wizard_error(
			r,
			this.t("Could not load the wizard. Check company/branch context and try again.")
		);
		this.setup = this.setup || {};
		this.step = 1;
		this.render_step();
	}

	save_step(callback, opts = {}) {
		const data = this.merge_persisted_fields(this.collect_step_data());
		const advance = Boolean(opts && opts.advance);
		const step_to_save = advance ? this.step + 1 : this.step;
		return this._call_save_step(step_to_save, data, callback, { freeze: true, advance });
	}

	_call_save_step(step_to_save, data, callback, opts = {}) {
		const freeze = opts.freeze !== false;
		const rollback_step = opts.rollback_step;
		const on_fail = opts.on_fail;
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.save_wizard_step",
			args: { setup_name: this.setup_name, step: step_to_save, data: data },
			freeze,
			callback: (r) => {
				if (r.exc) {
					on_fail && on_fail();
					if (rollback_step) {
						this.step = rollback_step;
						this.render_step();
					}
					const msgs = r._server_messages ? JSON.parse(r._server_messages) : [];
					frappe.msgprint({
						title: this.t("Wizard"),
						message:
							(msgs[0] && msgs[0].message) ||
							this.t("Could not save this step. Check required fields and try again."),
						indicator: "red",
					});
					return;
				}
				if (r.message) {
					this.step = frappe.utils.cint(r.message.wizard_step) || this.step;
				}
				Object.assign(this.setup, data);
				callback && callback();
			},
			error: () => {
				on_fail && on_fail();
				if (rollback_step) {
					this.step = rollback_step;
					this.render_step();
				}
				frappe.msgprint({
					title: this.t("Wizard"),
					message: this.t("Could not save this step. Check required fields and try again."),
					indicator: "red",
				});
			},
		});
	}

	merge_persisted_fields(data) {
		const keys = [
			"company",
			"branch",
			"client",
			"contract_title",
			"contract_type",
			"site_location",
			"building_type",
			"boq_template",
			"project_segment",
			"governing_standard",
		];
		keys.forEach((key) => {
			const incoming = data[key];
			const missing = incoming == null || String(incoming).trim() === "";
			if (this.setup[key] != null && this.setup[key] !== "" && missing) {
				data[key] = this.setup[key];
			}
		});
		return data;
	}

	num_or_default(value, fallback, allow_zero = false) {
		if (value === 0 || value === "0") {
			return allow_zero ? 0 : fallback;
		}
		const n = frappe.utils.flt(value);
		if (allow_zero && n === 0) {
			return 0;
		}
		return n > 0 ? n : fallback;
	}

	ensure_step3_defaults() {
		if (this.step !== 3) {
			return;
		}
		const bt = this.building_type_code();
		const set_if_empty = (field, val) => {
			const $el = this.body.find(`[data-field="${field}"]`);
			if (!$el.length) {
				return;
			}
			const raw = ($el.val() || "").toString().trim();
			if (raw === "" || frappe.utils.flt(raw) <= 0) {
				$el.val(val);
			}
		};
		if (this.is_road_type(bt)) {
			set_if_empty("road_length_m", 800);
			set_if_empty("road_width_m", 12);
		} else if (this.is_pipeline_type(bt)) {
			set_if_empty("pipe_network_km", 5);
		} else {
			set_if_empty("plot_area_m2", 600);
			set_if_empty("gross_floor_area_m2", 450);
			set_if_empty("number_of_floors", 2);
			set_if_empty("unit_count", 1);
			const $basement = this.body.find('[data-field="basement_levels"]');
			if ($basement.length && ($basement.val() || "").toString().trim() === "") {
				$basement.val(0);
			}
			if (bt === "hotel") {
				set_if_empty("key_count", 120);
			}
			if (bt === "hospital") {
				set_if_empty("bed_count", 200);
			}
		}
	}

	spec_number(field, fallback) {
		const $el = this.body.find(`[data-field="${field}"]`);
		if ($el.length) {
			const raw = ($el.val() || "").toString().trim();
			if (raw !== "") {
				return frappe.utils.flt(raw);
			}
		}
		const stored = this.setup[field];
		if (stored != null && String(stored).trim() !== "") {
			return frappe.utils.flt(stored);
		}
		return frappe.utils.flt(fallback);
	}

	building_type_code() {
		return (
			(this.body.find('[data-field="building_type"]').val() || this.setup.building_type || "").trim()
		);
	}

	is_road_type(code) {
		return ["urban_road", "highway"].includes(code);
	}

	is_pipeline_type(code) {
		return ["water_network", "sewer_network", "gas_network", "telecom_fiber"].includes(code);
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
		if (this.client_control) {
			d.client = this.client_control.get_value() || d.client || "";
		}
		return d;
	}

	collect_assignments() {
		const rows = [];
		this.body.find(".assign-party").each(function () {
			const $el = $(this);
			rows.push({
				trade_package_code: $el.data("trade"),
				party: ($el.val() || "").trim(),
			});
		});
		return rows;
	}

	validate_step() {
		if (this._busy) {
			return false;
		}
		if (!this.setup_name) {
			frappe.msgprint(this.t("Wizard is still loading. Please wait."));
			return false;
		}
		const s = this.setup;
		if (this.step === 1) {
			const client_val =
				(this.client_control && this.client_control.get_value()) ||
				this.body.find('[data-field="client"]').val() ||
				s.client ||
				"";
			if (!String(client_val).trim()) {
				frappe.msgprint(this.t("Client is required."));
				return false;
			}
			if (!(this.body.find('[data-field="contract_title"]').val() || s.contract_title || "").trim()) {
				frappe.msgprint(this.t("Project Title is required."));
				return false;
			}
		}
		if (this.step === 2) {
			const bt =
				this.body.find('[data-field="building_type"]').val() ||
				this.setup.building_type ||
				"";
			if (!bt) {
				frappe.msgprint(this.t("Building type is required."));
				this.body.find(".selected-type-summary").addClass("empty");
				this.body.find(".building-type-grid")[0]?.scrollIntoView({ behavior: "smooth", block: "start" });
				return false;
			}
			const meta = (this.building_types || []).find((t) => t.code === bt);
			if (meta && !meta.has_template) {
				frappe.msgprint(this.t("No BOQ template for this building type. Choose another type."));
				return false;
			}
		}
		if (this.step === 3) {
			this.ensure_step3_defaults();
			const bt = this.building_type_code();
			if (!bt) {
				frappe.show_alert({
					message: this.t("Complete step 2 and select a building type before continuing."),
					indicator: "orange",
				});
				frappe.msgprint({
					title: this.t("Specifications"),
					message: this.t("Complete step 2 and select a building type before continuing."),
					indicator: "orange",
				});
				return false;
			}
		}
		return true;
	}

	render_step() {
		this.render_steps_bar();
		this.body.empty();
		this.update_footer_buttons();
		omnexa_construction.i18n.apply_page_direction(this.wrapper);

		try {
			if (this.step === 1) this.render_step1();
			else if (this.step === 2) this.render_step2();
			else if (this.step === 3) this.render_step3();
			else if (this.step === 4) this.render_step4_financials();
			else if (this.step === 5) this.render_step5_boq();
			else if (this.step === 6) this.render_step6_phases_ipc();
			else if (this.step === 7) this.render_step7_details();
			else if (this.step === 8) this.render_step8_generate();
			else this.render_step1();
		} catch (e) {
			console.error("Construction wizard render failed", e);
			this.step = 1;
			this.render_step1();
		}
	}

	init_client_control(value) {
		const $parent = this.body.find(".client-link-field");
		if (!$parent.length) {
			return;
		}
		const fallback = () => {
			$parent.html(
				`<input class="form-control" data-field="client" value="${frappe.utils.escape_html(value || "")}">`
			);
		};
		try {
			if (!frappe.ui.form || !frappe.ui.form.make_control) {
				fallback();
				return;
			}
			this.client_control = frappe.ui.form.make_control({
				df: {
					fieldtype: "Link",
					options: "Customer",
					fieldname: "client",
					label: this.t("Client"),
				},
				parent: $parent,
				render_input: true,
				only_input: true,
			});
			if (!this.client_control || !this.client_control.set_value) {
				fallback();
				return;
			}
			this.client_control.set_value(value || "");
			if (this.client_control.$input) {
				this.client_control.$input.attr("data-field", "client");
			}
		} catch (e) {
			console.error("Client link control failed", e);
			fallback();
		}
	}

	field_row(label, html) {
		return `<div class="form-group col-md-6"><label class="control-label">${label}</label>${html}</div>`;
	}

	render_step1() {
		const s = this.setup;
		const ctx = (frappe.boot && frappe.boot.omnexa_view_context) || {};
		const company_readonly = Boolean(s.company) && !ctx.can_switch;
		const company_input = company_readonly
			? `<input class="form-control" data-field="company" value="${frappe.utils.escape_html(s.company || "")}" readonly>`
			: `<input class="form-control" data-field="company" value="${frappe.utils.escape_html(s.company || "")}">`;
		const branch_input = s.branch
			? `<input class="form-control" data-field="branch" value="${frappe.utils.escape_html(s.branch || "")}" readonly>`
			: `<input class="form-control" data-field="branch" value="${frappe.utils.escape_html(s.branch || "")}">`;
		this.body.html(`
			<div class="row">
				${this.field_row(this.t("Company"), company_input)}
				${this.field_row(this.t("Branch"), branch_input)}
				${this.field_row(this.t("Client"), `<div class="client-link-field"></div>`)}
				${this.field_row(this.t("Project Title"), `<input class="form-control" data-field="contract_title" value="${frappe.utils.escape_html(s.contract_title || "")}">`)}
				${this.field_row(this.t("Contract Type"), `<select class="form-control" data-field="contract_type">
					<option ${s.contract_type === "Turnkey (EPC)" ? "selected" : ""}>Turnkey (EPC)</option>
					<option ${s.contract_type === "Lump Sum" ? "selected" : ""}>Lump Sum</option>
					<option ${s.contract_type === "Unit Price" ? "selected" : ""}>Unit Price</option>
				</select>`)}
				${this.field_row(this.t("Site Location"), `<textarea class="form-control" data-field="site_location" rows="2">${frappe.utils.escape_html(s.site_location || "")}</textarea>`)}
			</div>
		`);
		this.init_client_control(s.client || "");
	}

	render_step2() {
		const s = this.setup;
		const selected = s.building_type || "";
		const lang = omnexa_construction.i18n.get_lang();
		const cards = (this.building_types || [])
			.map((b) => {
				const is_sel = selected === b.code;
				const title = lang === "ar" ? b.label_ar || b.label_en : b.label_en;
				const subtitle = lang === "ar" ? b.label_en : b.label_ar || "";
				return `
					<div class="building-type-card ${is_sel ? "selected" : ""}" data-code="${frappe.utils.escape_html(b.code)}" role="button" tabindex="0">
						<div class="card-title-ar">${frappe.utils.escape_html(title)}</div>
						<div class="card-title-en">${frappe.utils.escape_html(subtitle)}</div>
						${b.has_template ? "" : `<span class="badge badge-warning badge-no-tpl">${__("No template")}</span>`}
					</div>`;
			})
			.join("");

		const sel_meta = (this.building_types || []).find((b) => b.code === selected);
		const sel_label = sel_meta
			? lang === "ar"
				? sel_meta.label_ar || sel_meta.label_en
				: sel_meta.label_en
			: "";

		this.body.html(`
			<input type="hidden" data-field="building_type" value="${frappe.utils.escape_html(selected)}">
			<p class="step2-hint">${this.t("Select a building type below")}</p>
			<div class="building-type-grid">${cards || `<p class="text-muted">${__("No building types available.")}</p>`}</div>
			<div class="selected-type-summary ${selected ? "" : "empty"}">
				${selected
					? `<strong>${this.t("Building / Project Type")}:</strong> ${frappe.utils.escape_html(sel_label)}<br>
					   <strong>${this.t("BOQ Template")}:</strong> ${frappe.utils.escape_html(s.boq_template || "—")}`
					: this.t("Building type is required.")}
			</div>
			<div class="row mt-3">
				${this.field_row(this.t("Segment"), `<input class="form-control" data-field="project_segment" value="${frappe.utils.escape_html(s.project_segment || "")}" readonly>`)}
				${this.field_row(this.t("Governing Standard"), `<input class="form-control" data-field="governing_standard" value="${frappe.utils.escape_html(s.governing_standard || "")}">`)}
			</div>
		`);

		const select_type = (code) => {
			if (!code || this._busy) {
				return;
			}
			if (!this.setup_name) {
				this.show_wizard_error(
					null,
					this.t("Wizard is still loading. Please wait.")
				);
				return;
			}
			if (code === this.setup.building_type && this.setup.boq_template) {
				this.body.find(".building-type-card").removeClass("selected");
				this.body.find(`.building-type-card[data-code="${code}"]`).addClass("selected");
				return;
			}
			this.body.find('[data-field="building_type"]').val(code);
			this.setup.building_type = code;
			this.body.find(".building-type-card").removeClass("selected");
			this.body.find(`.building-type-card[data-code="${code}"]`).addClass("selected");

			this.set_busy(true, this.t("Loading template..."));
			frappe.call({
				method: "omnexa_construction.wizard.wizard_api.select_building_type",
				args: { setup_name: this.setup_name, building_type: code },
				freeze: false,
				callback: (r) => {
					this.set_busy(false);
					if (r.exc || !r.message) {
						this.show_wizard_error(
							r,
							this.t("No BOQ template for this building type. Choose another type.")
						);
						return;
					}
					Object.assign(this.setup, r.message);
					this.setup.building_type = code;
					this.step = 2;
					this.render_step2();
					frappe.show_alert({ message: this.t("Template loaded"), indicator: "green" });
				},
				error: (r) => {
					this.set_busy(false);
					this.show_wizard_error(
						r,
						this.t("No BOQ template for this building type. Choose another type.")
					);
				},
			});
		};

		this.body.find(".building-type-card").on("click", function () {
			select_type($(this).data("code"));
		});
		this.body.find(".building-type-card").on("keydown", function (e) {
			if (e.key === "Enter" || e.key === " ") {
				e.preventDefault();
				select_type($(this).data("code"));
			}
		});
	}

	render_step3() {
		const s = this.setup;
		const bt = s.building_type || "";
		const lang = omnexa_construction.i18n.get_lang();
		const meta = (this.building_types || []).find((b) => b.code === bt);
		const type_label = meta
			? lang === "ar"
				? meta.label_ar || meta.label_en
				: meta.label_en
			: bt || this.t("Building type is required.");
		const is_road = this.is_road_type(bt);
		const is_pipeline = this.is_pipeline_type(bt);
		const building_fields = is_road
			? `
				${this.field_row(this.t("Road Length (m)"), `<input type="number" min="1" step="1" class="form-control" data-field="road_length_m" value="${this.num_or_default(s.road_length_m, 800)}">`)}
				${this.field_row(this.t("Road Width (m)"), `<input type="number" min="1" step="0.5" class="form-control" data-field="road_width_m" value="${this.num_or_default(s.road_width_m, 12)}">`)}
			`
			: is_pipeline
				? `
				${this.field_row(this.t("Pipe Network (km)"), `<input type="number" min="0.1" step="0.1" class="form-control" data-field="pipe_network_km" value="${this.num_or_default(s.pipe_network_km, 5)}">`)}
			`
				: `
				${this.field_row(this.t("Plot Area (m²)"), `<input type="number" min="1" class="form-control" data-field="plot_area_m2" value="${this.num_or_default(s.plot_area_m2, 600)}">`)}
				${this.field_row(this.t("Gross Floor Area (m²)"), `<input type="number" min="1" class="form-control" data-field="gross_floor_area_m2" value="${this.num_or_default(s.gross_floor_area_m2, 450)}">`)}
				${this.field_row(this.t("Floors"), `<input type="number" min="1" class="form-control" data-field="number_of_floors" value="${this.num_or_default(s.number_of_floors, 2)}">`)}
				${this.field_row(this.t("Basements"), `<input type="number" min="0" class="form-control" data-field="basement_levels" value="${this.num_or_default(s.basement_levels, 0, true)}">`)}
				${this.field_row(this.t("Units"), `<input type="number" min="1" class="form-control" data-field="unit_count" value="${this.num_or_default(s.unit_count, 1)}">`)}
				${["hotel"].includes(bt) ? this.field_row(this.t("Keys / Rooms"), `<input type="number" min="1" class="form-control" data-field="key_count" value="${this.num_or_default(s.key_count, 120)}">`) : ""}
				${["hospital"].includes(bt) ? this.field_row(this.t("Bed Count"), `<input type="number" min="1" class="form-control" data-field="bed_count" value="${this.num_or_default(s.bed_count, 200)}">`) : ""}
			`;
		this.body.html(`
			<input type="hidden" data-field="building_type" value="${frappe.utils.escape_html(bt)}">
			<div class="step3-type-banner ${bt ? "" : "empty"}">
				<strong>${this.t("Building / Project Type")}:</strong> ${frappe.utils.escape_html(type_label)}
				${bt ? "" : `<div class="mt-2"><button type="button" class="btn btn-sm btn-default wizard-goto-step2">${this.t("Back to Asset Type")}</button></div>`}
			</div>
			<div class="row">
				${this.field_row(this.t("Quality Tier"), `<select class="form-control" data-field="quality_tier">
					<option ${s.quality_tier === "Economy" ? "selected" : ""}>Economy</option>
					<option ${(!s.quality_tier || s.quality_tier === "Standard") ? "selected" : ""}>Standard</option>
					<option ${s.quality_tier === "Premium" ? "selected" : ""}>Premium</option>
					<option ${s.quality_tier === "Luxury" ? "selected" : ""}>Luxury</option>
				</select>`)}
				${building_fields}
			</div>
		`);
		this.body.find(".wizard-goto-step2").on("click", () => {
			this.step = 2;
			this.render_step();
		});
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
					`<tr><td>${frappe.utils.escape_html(a.trade_package_code || "")}</td><td>${frappe.utils.escape_html(a.scope_notes || "")}</td><td><input class="form-control form-control-sm assign-party" data-trade="${frappe.utils.escape_html(a.trade_package_code || "")}" value="${frappe.utils.escape_html(a.party || "")}" placeholder="${__("Subcontractor link")}"></td></tr>`
			)
			.join("");
		return `<table class="table table-bordered table-sm"><thead><tr><th>${__("Trade")}</th><th>${__("Scope")}</th><th>${__("Subcontractor")}</th></tr></thead><tbody>${rows}</tbody></table>`;
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
			<h6>${omnexa_construction.i18n.t("Assignments")}</h6>
			${this.render_assignments_table(this.setup.assignments)}
		`);
		this.body.find(".assign-party").each((_, el) => {
			const $el = $(el);
			$el.on("focus", () => {
				if ($el.data("linked")) return;
				$el.data("linked", 1);
				frappe.prompt(
					[
						{
							fieldname: "party",
							fieldtype: "Link",
							options: "Supplier",
							label: __("Subcontractor"),
							default: $el.val(),
						},
					],
					(values) => {
						$el.val(values.party || "");
					},
					__("Select Subcontractor")
				);
			});
		});
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
		if (!this.validate_step()) {
			return;
		}
		const from_step = this.step;

		// Steps 1–3: navigate immediately, persist in background (fixes stuck Next on Specifications)
		if (from_step <= 3) {
			if (from_step === 3) {
				this.ensure_step3_defaults();
			}
			const next_step = from_step + 1;
			const data = this.merge_persisted_fields(this.collect_step_data());
			Object.assign(this.setup, data);
			this.step = next_step;
			this.render_step();
			this._call_save_step(next_step, data, null, { freeze: false, rollback_step: from_step });
			return;
		}

		this.save_step(() => {
			this.advance_after_save(from_step);
		}, { advance: true });
	}

	advance_after_save(from_step) {
		if (from_step === 4) {
			this.set_busy(true, this.t("Loading BOQ preview..."));
			frappe.call({
				method: "omnexa_construction.wizard.project_bundle.preview_boq",
				args: { setup_name: this.setup_name },
				freeze: false,
				callback: (r) => {
					this.set_busy(false);
					if (r.exc) {
						return;
					}
					this.reload_setup(() => {
						this.step = 5;
						this.render_step();
					});
				},
				error: () => {
					this.set_busy(false);
					frappe.msgprint({
						title: this.t("BOQ"),
						message: this.t("Could not load BOQ preview. Check building type and specifications."),
						indicator: "red",
					});
				},
			});
			return;
		}
		if (from_step === 5) {
			this.step = 6;
			this.reload_setup(() => this.render_step());
			return;
		}
		if (from_step === 6) {
			this.step = 7;
			this.reload_setup(() => this.render_step());
			return;
		}
		if (from_step === 7) {
			this.set_busy(true);
			frappe.call({
				method: "omnexa_construction.wizard.project_bundle.suggest_assignments",
				args: { setup_name: this.setup_name },
				freeze: false,
				callback: (r) => {
					this.set_busy(false);
					if (r.exc) {
						return;
					}
					this.step = 8;
					this.reload_setup(() => this.render_step());
				},
				error: () => this.set_busy(false),
			});
			return;
		}
		if (from_step < 8) {
			this.step = from_step + 1;
			this.render_step();
		}
	}

	reload_setup(callback) {
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.get_wizard_context",
			args: this.wizard_context_args(),
			callback: (r) => {
				if (r.message && r.message.setup) {
					this.setup = r.message.setup;
					this.setup_name = this.setup.name || this.setup_name;
					this.building_types = r.message.building_types || this.building_types;
				}
				callback && callback();
			},
		});
	}

	generate() {
		frappe.confirm(this.t("Create project documents now?"), () => {
			const run_bundle = () => {
				frappe.call({
					method: "omnexa_construction.wizard.project_bundle.create_project_bundle",
					args: { setup_name: this.setup_name },
					freeze: true,
					callback: (r) => {
						if (!r.message) return;
						frappe.msgprint({
							title: this.t("Project Created"),
							message: __("Contract {0} with {1} BOQ lines.", [
								r.message.project_contract,
								(r.message.boq_items || []).length,
							]),
							indicator: "green",
						});
						frappe.set_route("Form", "Project Contract", r.message.project_contract);
					},
				});
			};
			frappe.call({
				method: "omnexa_construction.wizard.project_bundle.save_wizard_assignments",
				args: {
					setup_name: this.setup_name,
					assignments: this.collect_assignments(),
				},
				freeze: true,
				callback: () => run_bundle(),
			});
		});
	}
};
