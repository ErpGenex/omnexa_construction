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
		this._save_seq = 0;
		this._save_chain = Promise.resolve();
		this._wizard_loaded = false;
		this._selected_building_type = null;
		this._step3_prepare_seq = 0;
		this._step3_prepared_key = null;
		this._step3_prepare_pending = null;
		this._last_rendered_step = null;
		this.regional_cost_options = [];
		this.site_region_codes = [];
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

	format_money(value, currency) {
		const cur = currency || this.setup.contract_currency || frappe.defaults.get_default("currency");
		if (typeof format_currency === "function") {
			return format_currency(value, cur);
		}
		return frappe.format(value, { fieldtype: "Currency", options: cur });
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
			<div class="wizard-loading">
				<div class="wz-spinner"></div>
				<p class="text-muted mb-0">${this.t("Loading wizard...")}</p>
			</div>
		`);
	}

	step_meta(step_num) {
		const steps = [
			{ icon: "fa-id-card", title: this.t("Identity"), subtitle: this.t("Company, client, and project title") },
			{ icon: "fa-th-large", title: this.t("Asset Type"), subtitle: this.t("Choose building type and BOQ template") },
			{ icon: "fa-sliders", title: this.t("Specifications"), subtitle: this.t("Areas, floors, and quality tier") },
			{ icon: "fa-money", title: this.t("Financials"), subtitle: this.t("Retention, advance, LD, and schedule") },
			{ icon: "fa-list-alt", title: this.t("BOQ"), subtitle: this.t("Bill of quantities preview") },
			{ icon: "fa-calendar", title: this.t("Phases & IPC"), subtitle: this.t("Delivery phases and payment certificates") },
			{ icon: "fa-calculator", title: this.t("Detail Pricing"), subtitle: this.t("Line-level costs and LD") },
			{ icon: "fa-rocket", title: this.t("Generate"), subtitle: this.t("Create contract and project documents") },
		];
		return steps[step_num - 1] || steps[0];
	}

	set_step_body(innerHtml, opts = {}) {
		const meta = this.step_meta(this.step);
		const animate = opts.animate !== false;
		this.body.html(`
			<div class="wizard-step-card${animate ? "" : " no-enter-animation"}">
				<div class="wizard-step-card-head">
					<h3><i class="fa ${meta.icon} text-muted mr-2"></i> ${meta.title}</h3>
					<p>${meta.subtitle}</p>
				</div>
				<div class="wizard-step-card-body">${innerHtml}</div>
			</div>
		`);
	}

	scroll_to_content() {
		const top = this.wrapper.offset().top - 60;
		$("html, body").animate({ scrollTop: Math.max(0, top) }, 200);
	}

	go_to_step(step_num) {
		if (step_num < 1 || step_num > 8 || step_num >= this.step || this._busy) {
			return;
		}
		this.step = step_num;
		this.render_step();
	}

	render_context_bar() {
		this.render_context_strip();
	}

	render_context_strip() {
		if (!this.context_strip) {
			return;
		}
		const s = this.setup || {};
		const lang = omnexa_construction.i18n.get_lang();
		if (this.$ctx_company_select && this.$ctx_company_select.length) {
			if (s.company) {
				this.$ctx_company_select.val(s.company);
			}
			this._fill_context_branch_options(s.company || this.$ctx_company_select.val());
			if (s.branch) {
				this.$ctx_branch_select.val(s.branch);
			}
		} else if (this.$ctx_company_readonly) {
			this.$ctx_company_readonly.text(s.company || "—");
			this.$ctx_branch_readonly.text(s.branch || "—");
		}
		this.wrapper.find(".wizard-lang-pills button").removeClass("active");
		this.wrapper.find(`.wizard-lang-pills button[data-lang="${lang}"]`).addClass("active");

		const chips = [];
		if (s.contract_title) {
			chips.push(`<span class="wizard-chip"><i class="fa fa-file-text-o"></i> ${frappe.utils.escape_html(s.contract_title)}</span>`);
		}
		if (s.building_type) {
			const meta = (this.building_types || []).find((b) => b.code === s.building_type);
			const lbl = meta ? (lang === "ar" ? meta.label_ar || meta.label_en : meta.label_en) : s.building_type;
			chips.push(`<span class="wizard-chip"><i class="fa fa-home"></i> ${frappe.utils.escape_html(lbl)}</span>`);
		}
		if (s.estimated_contract_value) {
			chips.push(
				`<span class="wizard-chip"><i class="fa fa-line-chart"></i> ${this.format_money(s.estimated_contract_value, s.contract_currency)}</span>`
			);
		}
		if (this.context_chips) {
			this.context_chips.html(chips.join(""));
			this.context_chips.toggleClass("is-empty", !chips.length);
		}
		if (this.body && this.body.length) {
			this.body.find('[data-field="company"]').val(s.company || "");
			this.body.find('[data-field="branch"]').val(s.branch || "");
		}
	}

	init_context_strip() {
		const ctx = (frappe.boot && frappe.boot.omnexa_view_context) || {};
		const can_switch = Boolean(ctx.can_switch);
		const s = this.setup || {};
		const lang = omnexa_construction.i18n.get_lang();

		let controls_html;
		if (can_switch) {
			controls_html = `
				<div class="wizard-context-field">
					<label class="wizard-context-label">${this.t("Company")}</label>
					<select class="form-control wizard-ctx-company"></select>
				</div>
				<div class="wizard-context-field">
					<label class="wizard-context-label">${this.t("Branch")}</label>
					<select class="form-control wizard-ctx-branch"></select>
				</div>
			`;
		} else {
			controls_html = `
				<div class="wizard-context-field">
					<label class="wizard-context-label">${this.t("Company")}</label>
					<span class="wizard-context-value wizard-ctx-company-readonly"></span>
				</div>
				<div class="wizard-context-field">
					<label class="wizard-context-label">${this.t("Branch")}</label>
					<span class="wizard-context-value wizard-ctx-branch-readonly"></span>
				</div>
			`;
		}

		this.context_strip.html(`
			<div class="wizard-context-controls">
				${controls_html}
				<div class="wizard-context-field wizard-context-lang">
					<label class="wizard-context-label">${this.t("Language")}</label>
					<div class="wizard-lang-pills">
						<button type="button" data-lang="ar" class="${lang === "ar" ? "active" : ""}">${this.t("Arabic")}</button>
						<button type="button" data-lang="en" class="${lang === "en" ? "active" : ""}">${this.t("English")}</button>
					</div>
				</div>
			</div>
			<div class="wizard-context-chips"></div>
		`);

		this.context_chips = this.context_strip.find(".wizard-context-chips");
		this.$ctx_company_select = this.context_strip.find(".wizard-ctx-company");
		this.$ctx_branch_select = this.context_strip.find(".wizard-ctx-branch");
		this.$ctx_company_readonly = this.context_strip.find(".wizard-ctx-company-readonly");
		this.$ctx_branch_readonly = this.context_strip.find(".wizard-ctx-branch-readonly");

		this.context_strip.find(".wizard-lang-pills button").on("click", (e) => {
			this.switch_lang($(e.currentTarget).data("lang"));
		});

		if (can_switch) {
			this._load_context_switcher_options(s, ctx);
			this.$ctx_company_select.on("change", () => {
				const company = this.$ctx_company_select.val() || "";
				this._fill_context_branch_options(company);
				this._apply_desk_context_from_strip();
			});
			this.$ctx_branch_select.on("change", () => this._apply_desk_context_from_strip());
		}
	}

	_load_context_switcher_options(setup, ctx) {
		if (!frappe.call) {
			return;
		}
		frappe.call({
			method: "omnexa_core.omnexa_core.session_context.get_view_context_options",
			callback: (r) => {
				if (!r.message) {
					return;
				}
				this._context_options = r.message;
				const data = r.message;
				const active = data.context || ctx || {};
				const branchesByCo = data.branches_by_company || {};

				this.$ctx_company_select.empty();
				(data.companies || []).forEach((co) => {
					this.$ctx_company_select.append(
						`<option value="${frappe.utils.escape_html(co)}">${frappe.utils.escape_html(co)}</option>`
					);
				});

				const company = setup.company || active.company || (data.companies || [])[0] || "";
				this.$ctx_company_select.val(company);
				this._branches_by_company = branchesByCo;
				this._fill_context_branch_options(company);
				if (active.view_all_branches) {
					this.$ctx_branch_select.val("__ALL__");
				} else {
					this.$ctx_branch_select.val(setup.branch || active.branch || "");
				}
				this.render_context_strip();
			},
		});
	}

	_fill_context_branch_options(company) {
		if (!this.$ctx_branch_select || !this.$ctx_branch_select.length) {
			return;
		}
		const branchesByCo = this._branches_by_company || {};
		this.$ctx_branch_select.empty();
		if (!company) {
			this.$ctx_branch_select.prop("disabled", true);
			return;
		}
		this.$ctx_branch_select.prop("disabled", false);
		this.$ctx_branch_select.append(`<option value="__ALL__">${this.t("All branches")}</option>`);
		(branchesByCo[company] || []).forEach((b) => {
			const label = b.branch_name || b.name;
			this.$ctx_branch_select.append(
				`<option value="${frappe.utils.escape_html(b.name)}">${frappe.utils.escape_html(label)}</option>`
			);
		});
	}

	_refresh_context_strip_labels() {
		if (!this.context_strip || !this.context_strip.length) {
			return;
		}
		const $fields = this.context_strip.find(".wizard-context-field");
		if ($fields.length >= 3) {
			$fields.eq(0).find(".wizard-context-label").text(this.t("Company"));
			$fields.eq(1).find(".wizard-context-label").text(this.t("Branch"));
			$fields.eq(2).find(".wizard-context-label").text(this.t("Language"));
		}
		this.context_strip.find('.wizard-lang-pills button[data-lang="ar"]').text(this.t("Arabic"));
		this.context_strip.find('.wizard-lang-pills button[data-lang="en"]').text(this.t("English"));
	}

	_apply_desk_context_from_strip() {
		if (!this.$ctx_company_select || !this.$ctx_company_select.length) {
			return;
		}
		const company = this.$ctx_company_select.val() || null;
		const branchVal = this.$ctx_branch_select.val();
		const view_all = !company ? 0 : branchVal === "__ALL__" ? 1 : 0;
		const branch = view_all ? null : branchVal;

		frappe.call({
			method: "omnexa_core.omnexa_core.session_context.set_desk_view_context",
			type: "POST",
			args: { company, branch, view_all_branches: view_all },
			freeze: true,
			freeze_message: this.t("Updating company and branch…"),
			callback: (res) => {
				if (res.exc || !res.message) {
					return;
				}
				frappe.boot.omnexa_view_context = res.message;
				this.setup_name = null;
				this.clear_setup_query_param();
				this._wizard_loaded = false;
				this.load();
			},
		});
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
		this._refresh_context_strip_labels();
		this.wrapper.find(".wizard-lang-pills button").removeClass("active");
		this.wrapper.find(`.wizard-lang-pills button[data-lang="${lang}"]`).addClass("active");
		if (this.hero_title) {
			this.hero_title.text(this.t("Construction Project Wizard"));
		}
		if (this.hero_sub) {
			this.hero_sub.text(this.t("Guided setup for contracts, BOQ, and IPC"));
		}
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
		this.wrapper.append(`
			<div class="wizard-hero">
				<div class="wizard-hero-text">
					<h2 class="wizard-hero-title"></h2>
					<p class="wizard-hero-sub"></p>
					<span class="hero-draft wizard-hero-draft" style="display:none"></span>
				</div>
			</div>
		`);
		this.hero_title = this.wrapper.find(".wizard-hero-title");
		this.hero_sub = this.wrapper.find(".wizard-hero-sub");
		this.hero_draft = this.wrapper.find(".wizard-hero-draft");
		this.hero_title.text(this.t("Construction Project Wizard"));
		this.hero_sub.text(this.t("Guided setup for contracts, BOQ, and IPC"));
		this.context_strip = $(`<div class="wizard-context-strip"></div>`).appendTo(this.wrapper);
		this.init_context_strip();
		this.steps_bar = $(`<div class="wizard-progress"><div class="wizard-progress-track"></div></div>`).appendTo(this.wrapper);
		this.progress_track = this.steps_bar.find(".wizard-progress-track");
		this.body = $(`<div class="wizard-body"></div>`).appendTo(this.wrapper);

		this.footer_bar = $(`
			<div class="wizard-footer-bar">
				<div class="footer-left">
					<button type="button" class="btn btn-default btn-lg wizard-btn-prev">${this.t("Previous")}</button>
				</div>
				<div class="footer-step-hint"></div>
				<div class="footer-right">
					<button type="button" class="btn btn-primary btn-lg wizard-btn-next">${this.t("Next")} →</button>
					<button type="button" class="btn btn-success btn-lg wizard-btn-generate">${this.t("Generate Project")}</button>
				</div>
			</div>
		`).appendTo(this.wrapper);

		this.$footer_hint = this.footer_bar.find(".footer-step-hint");
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
		omnexa_construction.i18n.apply_page_direction(this.wrapper);
		this.render_steps_bar();
		this.update_footer_buttons();
	}

	render_steps_bar() {
		if (!this.progress_track || !this.progress_track.length) {
			return;
		}
		const labels = [
			this.t("Identity"),
			this.t("Asset Type"),
			this.t("Specifications"),
			this.t("Financials"),
			this.t("BOQ"),
			this.t("Phases & IPC"),
			this.t("Detail Pricing"),
			this.t("Generate"),
		];
		const icons = ["fa-id-card", "fa-th-large", "fa-sliders", "fa-money", "fa-list-alt", "fa-calendar", "fa-calculator", "fa-rocket"];
		this.progress_track.empty();
		labels.forEach((label, i) => {
			const n = i + 1;
			let cls = "wizard-step-item";
			if (n === this.step) {
				cls += " is-active";
			} else if (n < this.step) {
				cls += " is-done";
			}
			const $item = $(`
				<div class="${cls}" data-step="${n}" title="${frappe.utils.escape_html(label)}">
					<div class="step-dot">${n < this.step ? '<i class="fa fa-check"></i>' : `<i class="fa ${icons[i]}"></i>`}</div>
					<span class="step-label">${frappe.utils.escape_html(label)}</span>
				</div>
			`);
			if (n < this.step) {
				$item.on("click", () => this.go_to_step(n));
			}
			this.progress_track.append($item);
		});
		if (this.$footer_hint) {
			const meta = this.step_meta(this.step);
			this.$footer_hint.text(`${this.t("Step")} ${this.step}/8 — ${meta.title}`);
		}
	}

	show_wizard_error(r, fallback) {
		frappe.msgprint({
			title: this.t("Wizard"),
			message: this.server_error_message(r, fallback),
			indicator: "red",
		});
	}

	load() {
		const seq = ++this._save_seq;
		this.set_busy(true, this.t("Loading wizard..."));
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.get_wizard_context",
			args: this.wizard_context_args(),
			freeze: false,
			callback: (r) => {
				if (seq !== this._save_seq) {
					return;
				}
				this.handle_load_response(r);
			},
			error: (r) => {
				if (seq !== this._save_seq) {
					return;
				}
				this.set_busy(false);
				if (this._wizard_loaded) {
					return;
				}
				this.render_load_error(r);
			},
		});
	}

	handle_load_response(r) {
		this.set_busy(false);
		try {
			const payload =
				r.message && typeof r.message === "object" && !Array.isArray(r.message) ? r.message : null;
			if (payload && payload.setup) {
				// Use successful payload even if Frappe flagged a non-fatal exc bit.
				this.render_context_strip();
			} else if (r.exc) {
				this.render_load_error(r);
				return;
			}
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
			if (this.setup.building_type) {
				this._selected_building_type = this.setup.building_type;
			}
			if (!this.setup_name) {
				this.render_load_error(r);
				return;
			}
			this.building_types = payload.building_types || [];
			this.load_regional_cost_options();
			this.load_site_region_codes();
			this.step = Math.min(8, Math.max(1, cint(this.setup.wizard_step) || 1));
			if (this.step >= 3 && !this.setup.building_type) {
				this.step = 2;
			}
			if (this.hero_draft) {
				this.hero_draft.text(this.setup_name).show();
			}
			this._wizard_loaded = true;
			this.render_step();
		} catch (e) {
			console.error("Construction wizard load failed", e);
			this.setup = this.setup || {};
			const detail = (e && e.message) || "";
			this.show_wizard_error(
				r,
				detail ||
					this.t("Could not load the wizard. Check company/branch context and try again.")
			);
			if (!this._wizard_loaded) {
				this.step = 1;
				try {
					this.render_step();
				} catch (e2) {
					console.error("Construction wizard fallback render failed", e2);
				}
			}
		}
	}

	render_load_error(r) {
		if (this._wizard_loaded) {
			return;
		}
		this.set_busy(false);
		this.show_wizard_error(
			r,
			this.t("Could not load the wizard. Check company/branch context and try again.")
		);
		this.setup = this.setup || {};
		this.step = 1;
		try {
			this.render_step();
		} catch (e) {
			console.error("Construction wizard error render failed", e);
		}
	}

	sanitize_step4_data(data) {
		if (!data) {
			return data;
		}
		const region = (data.site_region || "").toString().trim();
		if (region) {
			data.site_region = region.toUpperCase();
		} else {
			delete data.site_region;
		}
		const raw = (data.regional_cost_factor || "").toString().trim();
		if (!raw || /^[\d.]+$/.test(raw)) {
			delete data.regional_cost_factor;
			if (this.setup) {
				this.setup.regional_cost_factor = null;
			}
		}
		return data;
	}

	save_step(callback, opts = {}) {
		let data = this.merge_persisted_fields(this.collect_step_data());
		if (this.step === 4 || (opts.advance && this.step === 4)) {
			data = this.sanitize_step4_data(data);
		}
		const advance = Boolean(opts && opts.advance);
		const step_to_save = advance ? this.step + 1 : this.step;
		return this._call_save_step(step_to_save, data, callback, { freeze: true, advance });
	}

	_call_save_step(step_to_save, data, callback, opts = {}) {
		this._save_chain = this._save_chain
			.then(() => this._run_save_step(step_to_save, data, opts))
			.then(() => {
				callback && callback();
			})
			.catch((r) => {
				const rollback_step = opts.rollback_step;
				const on_fail = opts.on_fail;
				on_fail && on_fail();
				if (rollback_step) {
					this.step = rollback_step;
					this.render_step();
				}
				frappe.msgprint({
					title: this.t("Wizard"),
					message: this.server_error_message(
						r,
						this.t("Could not save this step. Check required fields and try again.")
					),
					indicator: "red",
				});
			});
	}

	_run_save_step(step_to_save, data, opts = {}) {
		if (step_to_save >= 4 || this.step === 4) {
			data = this.sanitize_step4_data(data || {});
		}
		const freeze = opts.freeze !== false;
		return new Promise((resolve, reject) => {
			frappe.call({
				method: "omnexa_construction.wizard.wizard_api.save_wizard_step",
				args: { setup_name: this.setup_name, step: step_to_save, data: data },
				freeze,
				callback: (r) => {
					if (r.exc) {
						reject(r);
						return;
					}
					if (r.message) {
						const saved = cint(r.message.wizard_step);
						if (saved) {
							this.setup.wizard_step = saved;
							if (saved >= this.step) {
								this.step = saved;
							}
						}
						if (r.message.modified) {
							this.setup.modified = r.message.modified;
						}
					}
					this._apply_setup_patch(data);
					if (data && data.building_type) {
						this._selected_building_type = data.building_type;
					}
					resolve(r.message);
				},
				error: (r) => reject(r),
			});
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
		const n = flt(value);
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
			if (raw === "" || flt(raw) <= 0) {
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
				return flt(raw);
			}
		}
		const stored = this.setup[field];
		if (stored != null && String(stored).trim() !== "") {
			return flt(stored);
		}
		return flt(fallback);
	}

	get_building_type() {
		const from_dom = (this.body.find('[data-field="building_type"]').val() || "").toString().trim();
		const from_setup = (this.setup && this.setup.building_type) || "";
		const from_cache = this._selected_building_type || "";
		return (from_cache || from_setup || from_dom).toString().trim();
	}

	building_type_code() {
		return this.get_building_type();
	}

	_apply_setup_patch(data) {
		if (!data || !this.setup) {
			return;
		}
		Object.keys(data).forEach((key) => {
			const val = data[key];
			if (val === 0 || val === "0") {
				this.setup[key] = val;
				return;
			}
			if (val != null && String(val).trim() !== "") {
				this.setup[key] = val;
			}
		});
	}

	is_road_type(code) {
		return ["urban_road", "highway"].includes(code);
	}

	is_pipeline_type(code) {
		return [
			"water_network",
			"sewer_network",
			"electrical_network",
			"gas_network",
			"telecom_fiber",
		].includes(code);
	}

	sync_building_type_to_setup() {
		const bt = this.get_building_type();
		if (!bt) {
			return "";
		}
		this.setup.building_type = bt;
		this._selected_building_type = bt;
		return bt;
	}

	apply_step3_defaults_to_setup() {
		const bt = this.sync_building_type_to_setup();
		if (!bt || !this.setup) {
			return;
		}
		const s = this.setup;
		const set_if_empty = (field, val, allow_zero = false) => {
			const cur = s[field];
			if (cur === 0 || cur === "0") {
				if (!allow_zero) {
					s[field] = val;
				}
				return;
			}
			if (cur == null || cur === "" || flt(cur) <= 0) {
				s[field] = val;
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
			set_if_empty("basement_levels", 0, true);
			set_if_empty("unit_count", 1);
			if (bt === "hotel") {
				set_if_empty("key_count", 120);
			}
			if (bt === "hospital") {
				set_if_empty("bed_count", 200);
			}
		}
		if (!s.quality_tier) {
			s.quality_tier = "Standard";
		}
	}

	_step3_prepare_key() {
		const bt = this.get_building_type();
		if (!this.setup_name || !bt) {
			return null;
		}
		return `${this.setup_name}:${bt}`;
	}

	_reset_step3_prepare_state() {
		this._step3_prepared_key = null;
		this._step3_prepare_pending = null;
		++this._step3_prepare_seq;
	}

	_patch_step3_fields_from_server(data) {
		if (!data || !this.body || !this.body.length) {
			return;
		}
		const numeric = new Set([
			"plot_area_m2",
			"gross_floor_area_m2",
			"number_of_floors",
			"basement_levels",
			"unit_count",
			"bed_count",
			"key_count",
			"road_length_m",
			"road_width_m",
			"pipe_network_km",
		]);
		Object.keys(data).forEach((key) => {
			const $el = this.body.find(`[data-field="${key}"]`);
			if (!$el.length) {
				return;
			}
			const incoming = data[key];
			if (incoming == null || incoming === "") {
				return;
			}
			const raw = ($el.val() || "").toString().trim();
			if ($el.is("select")) {
				if (!raw) {
					$el.val(incoming);
				}
				return;
			}
			if (key === "basement_levels") {
				if (raw === "") {
					$el.val(incoming);
				}
				return;
			}
			if (numeric.has(key)) {
				if (!raw || flt(raw) <= 0) {
					$el.val(incoming);
				}
			}
		});
	}

	prepare_step3_from_server() {
		const key = this._step3_prepare_key();
		if (!key || this._step3_prepared_key === key || this._step3_prepare_pending === key) {
			return;
		}
		this._step3_prepare_pending = key;
		const seq = ++this._step3_prepare_seq;
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.prepare_specifications_step",
			args: { setup_name: this.setup_name },
			freeze: false,
			callback: (r) => {
				this._step3_prepare_pending = null;
				if (seq !== this._step3_prepare_seq || this.step !== 3) {
					return;
				}
				if (r.exc || !r.message) {
					return;
				}
				this._step3_prepared_key = key;
				this._apply_setup_patch(r.message);
				this.sync_building_type_to_setup();
				this._patch_step3_fields_from_server(r.message);
			},
			error: () => {
				this._step3_prepare_pending = null;
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
		if (this.client_control) {
			d.client = this.client_control.get_value() || d.client || "";
		}
		if (this.regional_cost_control && this.regional_cost_control.get_value) {
			d.regional_cost_factor = this.regional_cost_control.get_value() || d.regional_cost_factor || "";
		}
		return d;
	}

	collect_assignments() {
		const rows = [];
		this.body.find(".wizard-assign-row").each(function () {
			const $row = $(this);
			rows.push({
				trade_package_code: ($row.data("trade") || "").toString(),
				assignment_type: ($row.find('[data-field="assignment_type"]').val() || "Subcontractor").toString(),
				party: ($row.find(".assign-party").val() || "").trim(),
			});
		});
		return rows;
	}

	collect_phases() {
		const rows = [];
		this.body.find(".wizard-phase-row").each(function () {
			const $row = $(this);
			const code = ($row.find('[data-field="phase_code"]').val() || "").toString().trim();
			const name = ($row.find('[data-field="phase_name"]').val() || "").toString().trim();
			if (!code && !name) {
				return;
			}
			rows.push({
				phase_code: code,
				phase_name: name,
				phase_name_ar: ($row.find('[data-field="phase_name_ar"]').val() || "").toString().trim(),
				planned_start: $row.find('[data-field="planned_start"]').val() || null,
				planned_finish: $row.find('[data-field="planned_finish"]').val() || null,
				handover_date: $row.find('[data-field="handover_date"]').val() || null,
				weight_percent: flt($row.find('[data-field="weight_percent"]').val()),
				boq_cost_prefixes: ($row.find('[data-field="boq_cost_prefixes"]').val() || "").toString().trim(),
			});
		});
		return rows;
	}

	collect_boq_line_edits() {
		const rows = [];
		this.body.find(".wizard-boq-row").each(function () {
			const $row = $(this);
			const code = ($row.data("cost-code") || "").toString();
			if (!code) {
				return;
			}
			rows.push({
				cost_code: code,
				include: $row.find('[data-field="include"]').is(":checked") ? 1 : 0,
				phase_code: ($row.find('[data-field="phase_code"]').val() || "").toString().trim(),
				execution_mode: ($row.find('[data-field="execution_mode"]').val() || "Company").toString(),
				assigned_party: ($row.find(".boq-party").val() || "").toString().trim(),
				material_cost: flt($row.find('[data-field="material_cost"]').val()),
				labor_cost: flt($row.find('[data-field="labor_cost"]').val()),
				equipment_cost: flt($row.find('[data-field="equipment_cost"]').val()),
				quantity: flt($row.find('[data-field="quantity"]').val()),
			});
		});
		return rows;
	}

	collect_boq_detail_edits() {
		const rows = [];
		this.body.find(".wizard-detail-row").each(function () {
			const $row = $(this);
			rows.push({
				boq_cost_code: ($row.data("boq-code") || "").toString(),
				spec_description: ($row.data("detail-desc") || "").toString(),
				name: ($row.data("detail-name") || "").toString(),
				quantity: flt($row.find('[data-field="quantity"]').val()),
				material_rate: flt($row.find('[data-field="material_rate"]').val()),
				labor_rate: flt($row.find('[data-field="labor_rate"]').val()),
				equipment_rate: flt($row.find('[data-field="equipment_rate"]').val()),
				unit_rate: flt($row.find('[data-field="unit_rate"]').val()),
			});
		});
		return rows;
	}

	phase_select_options(selected) {
		const phases = this.setup.phases || [];
		const sel = frappe.utils.escape_html(selected || "");
		let html = `<option value="">${this.t("— Phase —")}</option>`;
		phases.forEach((p) => {
			const code = frappe.utils.escape_html(p.phase_code || "");
			const s = code === sel ? " selected" : "";
			html += `<option value="${code}"${s}>${code}</option>`;
		});
		return html;
	}

	persist_phases(callback) {
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.save_wizard_phases",
			args: { setup_name: this.setup_name, phases: this.collect_phases() },
			freeze: true,
			callback: (r) => {
				if (r.message && r.message.phases) {
					this.setup.phases = r.message.phases;
				}
				callback && callback(r);
			},
			error: (r) => {
				this.show_wizard_error(r, this.t("Could not save phases."));
			},
		});
	}

	persist_boq_edits(callback) {
		const lines = this.collect_boq_line_edits();
		const details = this.collect_boq_detail_edits();
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.save_wizard_boq_lines",
			args: { setup_name: this.setup_name, lines },
			freeze: true,
			callback: (r) => {
				if (r.message) {
					if (r.message.estimated_contract_value != null) {
						this.setup.estimated_contract_value = r.message.estimated_contract_value;
					}
				}
				if (!details.length) {
					callback && callback(r);
					return;
				}
				frappe.call({
					method: "omnexa_construction.wizard.wizard_api.save_wizard_boq_details",
					args: { setup_name: this.setup_name, details },
					freeze: true,
					callback: (r2) => {
						if (r2.message) {
							if (r2.message.boq_details) {
								this.setup.boq_details = r2.message.boq_details;
							}
							if (r2.message.estimated_contract_value != null) {
								this.setup.estimated_contract_value = r2.message.estimated_contract_value;
							}
						}
						callback && callback(r2);
					},
					error: (r2) => this.show_wizard_error(r2, this.t("Could not save material details.")),
				});
			},
			error: (r) => this.show_wizard_error(r, this.t("Could not save BOQ lines.")),
		});
	}

	bind_subcontractor_input($input) {
		$input.on("focus", () => {
			if ($input.data("linked")) {
				return;
			}
			$input.data("linked", 1);
			frappe.prompt(
				[
					{
						fieldname: "party",
						fieldtype: "Link",
						options: "Supplier",
						label: this.t("Subcontractor"),
						default: $input.val(),
					},
				],
				(values) => {
					$input.val(values.party || "");
					const $row = $input.closest(".wizard-boq-row");
					if ($row.length && values.party) {
						$row.find('[data-field="execution_mode"]').val("Subcontractor");
					}
				},
				this.t("Select Subcontractor")
			);
		});
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
			const bt = this.get_building_type();
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
			if (!this.setup.boq_template) {
				frappe.msgprint({
					title: this.t("Wizard"),
					message: this.t("Wait for the template to load before continuing."),
					indicator: "orange",
				});
				return false;
			}
			this.setup.building_type = bt;
			this._selected_building_type = bt;
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
		try {
			const step_changed = this._last_rendered_step !== this.step;
			if (this.progress_track && this.progress_track.length) {
				this.render_steps_bar();
			}
			this.render_context_bar();
			this.update_footer_buttons();
			omnexa_construction.i18n.apply_page_direction(this.wrapper);

			if (this.step === 1) this.render_step1();
			else if (this.step === 2) this.render_step2();
			else if (this.step === 3) this.render_step3();
			else if (this.step === 4) this.render_step4_financials();
			else if (this.step === 5) this.render_step5_boq();
			else if (this.step === 6) this.render_step6_phases_ipc();
			else if (this.step === 7) this.render_step7_details();
			else if (this.step === 8) this.render_step8_generate();
			else this.render_step1();
			this._last_rendered_step = this.step;
			if (step_changed) {
				this.scroll_to_content();
			}
		} catch (e) {
			console.error("Construction wizard render failed", e);
			if (!this._wizard_loaded) {
				throw e;
			}
			this.set_step_body(
				`<div class="wz-callout is-warning"><p class="mb-0">${frappe.utils.escape_html(
					(e && e.message) || this.t("Could not display this step. Try again.")
				)}</p></div>`
			);
			frappe.msgprint({
				title: this.t("Wizard"),
				message: (e && e.message) || this.t("Could not display this step. Try again."),
				indicator: "red",
			});
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

	field_row(label, html, span2 = false) {
		return `<div class="wizard-field ${span2 ? "span-2" : ""}"><label>${label}</label>${html}</div>`;
	}

	render_step1() {
		const s = this.setup;
		this.set_step_body(`
			<div class="wz-callout">${this.t("Set company, branch, and language in the bar above, then enter client and project details.")}</div>
			<input type="hidden" data-field="company" value="${frappe.utils.escape_html(s.company || "")}">
			<input type="hidden" data-field="branch" value="${frappe.utils.escape_html(s.branch || "")}">
			<div class="wizard-form-grid">
				${this.field_row(this.t("Client"), `<div class="client-link-field"></div>`)}
				${this.field_row(this.t("Project Title"), `<input class="form-control" data-field="contract_title" value="${frappe.utils.escape_html(s.contract_title || "")}">`)}
				${this.field_row(this.t("Contract Type"), `<select class="form-control" data-field="contract_type">
					<option ${s.contract_type === "Turnkey (EPC)" ? "selected" : ""}>Turnkey (EPC)</option>
					<option ${s.contract_type === "Lump Sum" ? "selected" : ""}>Lump Sum</option>
					<option ${s.contract_type === "Unit Price" ? "selected" : ""}>Unit Price</option>
				</select>`)}
				${this.field_row(this.t("Site Location"), `<textarea class="form-control" data-field="site_location" rows="2">${frappe.utils.escape_html(s.site_location || "")}</textarea>`, true)}
			</div>
		`);
		this.init_client_control(s.client || "");
	}

	refresh_step2_selection_summary(code) {
		const lang = omnexa_construction.i18n.get_lang();
		const bt = code || this.get_building_type();
		const meta = (this.building_types || []).find((b) => b.code === bt);
		const sel_label = meta
			? lang === "ar"
				? meta.label_ar || meta.label_en
				: meta.label_en
			: bt;
		const $summary = this.body.find(".selected-type-summary");
		if (!$summary.length) {
			return;
		}
		if (!bt) {
			$summary.addClass("empty").removeClass("is-success wz-callout");
			$summary.html(this.t("Building type is required."));
			return;
		}
		$summary.removeClass("empty").addClass("wz-callout is-success");
		$summary.html(
			`<strong>${this.t("Building / Project Type")}:</strong> ${frappe.utils.escape_html(sel_label)}<br>
			<strong>${this.t("BOQ Template")}:</strong> ${frappe.utils.escape_html(this.setup.boq_template || this.t("Loading template..."))}`
		);
	}

	render_step2() {
		const s = this.setup;
		const selected = this.get_building_type() || s.building_type || "";
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

		this.set_step_body(`
			<input type="hidden" data-field="building_type" value="${frappe.utils.escape_html(selected)}">
			<div class="wz-callout">${this.t("Select a building type below")}</div>
			<div class="building-type-toolbar">
				<input type="search" class="form-control building-type-search" placeholder="${this.t("Search building types...")}" autocomplete="off">
			</div>
			<div class="building-type-grid">${cards || `<p class="text-muted">${__("No building types available.")}</p>`}</div>
			<div class="selected-type-summary ${selected ? "is-success" : "empty"}">
				${selected
					? `<strong>${this.t("Building / Project Type")}:</strong> ${frappe.utils.escape_html(sel_label)}<br>
					   <strong>${this.t("BOQ Template")}:</strong> ${frappe.utils.escape_html(s.boq_template || "—")}`
					: this.t("Building type is required.")}
			</div>
			<div class="section-title">${this.t("Standards")}</div>
			<div class="wizard-form-grid">
				${this.field_row(this.t("Segment"), `<input class="form-control" data-field="project_segment" value="${frappe.utils.escape_html(s.project_segment || "")}" readonly>`)}
				${this.field_row(this.t("Governing Standard"), `<input class="form-control" data-field="governing_standard" value="${frappe.utils.escape_html(s.governing_standard || "")}">`)}
			</div>
		`);
		const self = this;
		this.body.find(".building-type-search").on("input", function () {
			const q = ($(this).val() || "").toString().toLowerCase().trim();
			self.body.find(".building-type-card").each(function () {
				const $c = $(this);
				const text = $c.text().toLowerCase();
				$c.toggleClass("is-hidden", q.length > 0 && !text.includes(q));
			});
		});

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
			this._selected_building_type = code;
			this.setup.building_type = code;
			this._reset_step3_prepare_state();
			this.body.find('[data-field="building_type"]').val(code);
			this.body.find(".building-type-card").removeClass("selected");
			this.body.find(`.building-type-card[data-code="${frappe.utils.escape_html(code)}"]`).addClass("selected");
			this.refresh_step2_selection_summary(code);

			if (code === this.setup.building_type && this.setup.boq_template) {
				return;
			}

			this.set_busy(true, this.t("Loading template..."));
			const seq = ++this._save_seq;
			frappe.call({
				method: "omnexa_construction.wizard.wizard_api.select_building_type",
				args: { setup_name: this.setup_name, building_type: code },
				freeze: false,
				callback: (r) => {
					if (seq !== this._save_seq) {
						return;
					}
					this.set_busy(false);
					if (r.exc || !r.message) {
						this.show_wizard_error(
							r,
							this.t("No BOQ template for this building type. Choose another type.")
						);
						return;
					}
					this._apply_setup_patch(r.message);
					this.setup.building_type = code;
					this._selected_building_type = code;
					this.setup.wizard_step = cint(r.message.wizard_step) || 2;
					this.step = Math.max(this.step, 2);
					this.render_step();
					frappe.show_alert({ message: this.t("Template loaded"), indicator: "green" });
				},
				error: (r) => {
					if (seq !== this._save_seq) {
						return;
					}
					this.set_busy(false);
					this.show_wizard_error(
						r,
						this.t("No BOQ template for this building type. Choose another type.")
					);
				},
			});
		};

		this.body.find(".building-type-card").on("click", function () {
			select_type($(this).attr("data-code"));
		});
		this.body.find(".building-type-card").on("keydown", function (e) {
			if (e.key === "Enter" || e.key === " ") {
				e.preventDefault();
				select_type($(this).attr("data-code"));
			}
		});
	}

	render_step3_fields_html(bt) {
		const s = this.setup || {};
		if (this.is_road_type(bt)) {
			return [
				this.field_row(
					this.t("Road Length (m)"),
					`<input type="number" min="1" step="1" class="form-control" data-field="road_length_m" value="${this.num_or_default(s.road_length_m, 800)}">`
				),
				this.field_row(
					this.t("Road Width (m)"),
					`<input type="number" min="1" step="0.5" class="form-control" data-field="road_width_m" value="${this.num_or_default(s.road_width_m, 12)}">`
				),
			].join("");
		}
		if (this.is_pipeline_type(bt)) {
			return this.field_row(
				this.t("Pipe Network (km)"),
				`<input type="number" min="0.1" step="0.1" class="form-control" data-field="pipe_network_km" value="${this.num_or_default(s.pipe_network_km, 5)}">`
			);
		}
		let rows = [
			this.field_row(
				this.t("Plot Area (m²)"),
				`<input type="number" min="1" class="form-control" data-field="plot_area_m2" value="${this.num_or_default(s.plot_area_m2, 600)}">`
			),
			this.field_row(
				this.t("Gross Floor Area (m²)"),
				`<input type="number" min="1" class="form-control" data-field="gross_floor_area_m2" value="${this.num_or_default(s.gross_floor_area_m2, 450)}">`
			),
			this.field_row(
				this.t("Floors"),
				`<input type="number" min="1" class="form-control" data-field="number_of_floors" value="${this.num_or_default(s.number_of_floors, 2)}">`
			),
			this.field_row(
				this.t("Basements"),
				`<input type="number" min="0" class="form-control" data-field="basement_levels" value="${this.num_or_default(s.basement_levels, 0, true)}">`
			),
			this.field_row(
				this.t("Units"),
				`<input type="number" min="1" class="form-control" data-field="unit_count" value="${this.num_or_default(s.unit_count, 1)}">`
			),
		];
		if (bt === "hotel") {
			rows.push(
				this.field_row(
					this.t("Keys / Rooms"),
					`<input type="number" min="1" class="form-control" data-field="key_count" value="${this.num_or_default(s.key_count, 120)}">`
				)
			);
		}
		if (bt === "hospital") {
			rows.push(
				this.field_row(
					this.t("Bed Count"),
					`<input type="number" min="1" class="form-control" data-field="bed_count" value="${this.num_or_default(s.bed_count, 200)}">`
				)
			);
		}
		return rows.join("");
	}

	render_step3() {
		this.setup = this.setup || {};
		this.apply_step3_defaults_to_setup();
		const s = this.setup;
		const bt = this.sync_building_type_to_setup();
		const lang = omnexa_construction.i18n.get_lang();
		const meta = (this.building_types || []).find((b) => b.code === bt);
		const type_label = meta
			? lang === "ar"
				? meta.label_ar || meta.label_en
				: meta.label_en
			: bt || this.t("Building type is required.");
		const tier = s.quality_tier || "Standard";
		const building_fields = bt ? this.render_step3_fields_html(bt) : "";
		this.set_step_body(`
			<input type="hidden" data-field="building_type" value="${frappe.utils.escape_html(bt || "")}">
			<div class="wz-callout ${bt ? "is-success" : "is-warning"}">
				<strong>${this.t("Building / Project Type")}:</strong> ${frappe.utils.escape_html(type_label)}
				${bt ? "" : `<div class="mt-2"><button type="button" class="btn btn-sm btn-default wizard-goto-step2">${this.t("Back to Asset Type")}</button></div>`}
			</div>
			<div class="section-title">${this.t("Specifications")}</div>
			<div class="wizard-form-grid">
				${this.field_row(
					this.t("Quality Tier"),
					`<select class="form-control" data-field="quality_tier">
					<option value="Economy" ${tier === "Economy" ? "selected" : ""}>Economy</option>
					<option value="Standard" ${tier === "Standard" ? "selected" : ""}>Standard</option>
					<option value="Premium" ${tier === "Premium" ? "selected" : ""}>Premium</option>
					<option value="Luxury" ${tier === "Luxury" ? "selected" : ""}>Luxury</option>
				</select>`
				)}
				${building_fields || this.field_row(this.t("Specifications"), `<p class="text-muted mb-0">${this.t("Complete step 2 and select a building type before continuing.")}</p>`, true)}
			</div>
		`);
		this.body.find(".wizard-goto-step2").on("click", () => {
			this.step = 2;
			this.render_step();
		});
		if (bt) {
			this.prepare_step3_from_server();
		}
	}

	site_region_datalist_html() {
		const lang = omnexa_construction.i18n.get_lang();
		const rows = this.site_region_codes || [];
		return rows
			.map((r) => {
				const code = frappe.utils.escape_html(r.region_code || "");
				const name =
					lang === "ar"
						? r.region_name_ar || r.region_name || code
						: r.region_name || code;
				const suffix =
					r.source === "regional" && r.cost_factor != null
						? ` (×${r.cost_factor})`
						: "";
				return `<option value="${code}">${frappe.utils.escape_html(name)} — ${code}${suffix}</option>`;
			})
			.join("");
	}

	load_site_region_codes(callback) {
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.list_site_region_code_options",
			args: { company: (this.setup && this.setup.company) || null, limit: 500 },
			freeze: false,
			callback: (r) => {
				if (r.message && Array.isArray(r.message)) {
					this.site_region_codes = r.message;
					if (this.step === 4) {
						const $list = this.body.find("#wizard-region-list");
						if ($list.length) {
							$list.html(this.site_region_datalist_html());
						}
					}
				}
				callback && callback();
			},
		});
	}

	render_step4_financials() {
		const s = this.setup || {};
		const region_opts = this.site_region_datalist_html();
		const region_value = frappe.utils.escape_html((s.site_region || "").toString().toUpperCase());
		const region_placeholder = this.t("e.g. EG, US, SA or EG-CAIRO");
		this.set_step_body(`
			<div class="wz-callout">${this.t("Pick an ISO country code (EG, US, SA…) or a company region (EG-CAIRO). Leave blank for default (×1).")}</div>
			<div class="wizard-form-grid">
				${this.field_row(this.t("Retention %"), `<input type="number" class="form-control" data-field="retention_percent" value="${s.retention_percent || 5}">`)}
				${this.field_row(this.t("Advance %"), `<input type="number" class="form-control" data-field="advance_payment_percent" value="${s.advance_payment_percent || 10}">`)}
				${this.field_row(this.t("Default IPC Discount %"), `<input type="number" class="form-control" data-field="default_discount_percent" value="${s.default_discount_percent || 0}">`)}
				${this.field_row(this.t("Contract LD / day"), `<input type="number" class="form-control" data-field="liquidated_damages_per_day" value="${s.liquidated_damages_per_day || 0}">`)}
				${this.field_row(this.t("LD cap % of contract"), `<input type="number" class="form-control" data-field="liquidated_damages_cap_percent" value="${s.liquidated_damages_cap_percent || 10}">`)}
				${this.field_row(this.t("Planned Start"), `<input type="date" class="form-control" data-field="planned_start" value="${s.planned_start || ""}">`)}
				${this.field_row(this.t("Planned Completion"), `<input type="date" class="form-control" data-field="planned_completion" value="${s.planned_completion || ""}">`)}
				${this.field_row(
					this.t("Site Region Code"),
					`<input class="form-control" data-field="site_region" list="wizard-region-list" value="${region_value}" placeholder="${frappe.utils.escape_html(region_placeholder)}" autocomplete="off">
					<datalist id="wizard-region-list">${region_opts}</datalist>
					<p class="text-muted small mb-0 wizard-region-hint"></p>`,
					true
				)}
				${this.field_row(this.t("Regional Cost Factor"), `<div class="regional-cost-link-field"></div><p class="text-muted small mb-0">${this.t("Optional — pick from master list")}</p>`)}
			</div>
		`);
		this.init_regional_cost_control(s.regional_cost_factor || "");
		this.refresh_regional_hint();
		const self = this;
		this.body.find('[data-field="site_region"]').on("change blur", function () {
			const code = ($(this).val() || "").toString().trim().toUpperCase();
			$(this).val(code);
			self.resolve_regional_from_site_region(code);
		});
		if (!this.regional_cost_options || !this.regional_cost_options.length) {
			this.load_regional_cost_options();
		}
		if (!this.site_region_codes || !this.site_region_codes.length) {
			this.load_site_region_codes();
		}
	}

	load_regional_cost_options() {
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.list_regional_cost_options",
			args: { company: (this.setup && this.setup.company) || null },
			freeze: false,
			callback: (r) => {
				if (r.message && r.message.length) {
					this.regional_cost_options = r.message;
					if (this.step === 4) {
						this.render_step4_financials();
					}
				}
			},
		});
	}

	init_regional_cost_control(value) {
		const $parent = this.body.find(".regional-cost-link-field");
		if (!$parent.length) {
			return;
		}
		const company = (this.setup && this.setup.company) || "";
		const fallback = () => {
			$parent.html(
				`<input type="hidden" data-field="regional_cost_factor" value="${frappe.utils.escape_html(value || "")}">`
			);
		};
		try {
			if (!frappe.ui.form || !frappe.ui.form.make_control) {
				fallback();
				return;
			}
			this.regional_cost_control = frappe.ui.form.make_control({
				df: {
					fieldtype: "Link",
					options: "Regional Cost Factor",
					fieldname: "regional_cost_factor",
					label: this.t("Regional Cost Factor"),
					get_query: () => ({
						filters: { company, disabled: 0 },
					}),
				},
				parent: $parent[0],
				render_input: true,
				only_input: true,
			});
			if (!this.regional_cost_control || !this.regional_cost_control.set_value) {
				fallback();
				return;
			}
			this.regional_cost_control.set_value(value || "");
			if (this.regional_cost_control.$input) {
				this.regional_cost_control.$input.attr("data-field", "regional_cost_factor");
				this.regional_cost_control.$input.on("change", () => this.refresh_regional_hint());
			}
		} catch (e) {
			console.error("Regional cost link control failed", e);
			fallback();
		}
	}

	resolve_regional_from_site_region(code) {
		if (!code || !this.regional_cost_options) {
			this.refresh_regional_hint();
			return;
		}
		const row = (this.regional_cost_options || []).find(
			(r) => (r.region_code || "").toUpperCase() === code.toUpperCase()
		);
		if (row && row.name) {
			this.setup.regional_cost_factor = row.name;
			if (this.regional_cost_control && this.regional_cost_control.set_value) {
				this.regional_cost_control.set_value(row.name);
			}
		}
		this.refresh_regional_hint();
	}

	refresh_regional_hint() {
		const $hint = this.body.find(".wizard-region-hint");
		if (!$hint.length) {
			return;
		}
		const code = (this.body.find('[data-field="site_region"]').val() || "").toString().trim().toUpperCase();
		const lang = omnexa_construction.i18n.get_lang();
		const row = (this.regional_cost_options || []).find(
			(r) => (r.region_code || "").toUpperCase() === code
		);
		if (row) {
			$hint.text(`${this.t("Effective multiplier")}: ×${row.cost_factor}`);
			return;
		}
		const country = (this.site_region_codes || []).find((r) => (r.region_code || "").toUpperCase() === code);
		if (country) {
			const name =
				lang === "ar"
					? country.region_name_ar || country.region_name
					: country.region_name || code;
			$hint.text(`${name} (${code})`);
			return;
		}
		$hint.text(this.t("Leave blank for company default (×1)."));
	}

	load_boq_preview_after_step4(callback) {
		this.set_busy(true, this.t("Loading BOQ preview..."));
		frappe.call({
			method: "omnexa_construction.wizard.project_bundle.preview_boq",
			args: { setup_name: this.setup_name },
			freeze: false,
			callback: (r) => {
				this.set_busy(false);
				if (r.exc) {
					frappe.msgprint({
						title: this.t("BOQ"),
						message: this.t("Could not load BOQ preview. Check building type and specifications."),
						indicator: "red",
					});
					return;
				}
				this.reload_setup(callback, { keep_step: true });
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
	}

	render_step5_boq() {
		const tpl = frappe.utils.escape_html(this.setup.boq_template || "");
		const lines = this.setup.boq_lines || [];
		if (lines.length) {
			const total = this.format_money(this.setup.estimated_contract_value, this.setup.contract_currency);
			this.set_step_body(`
				<div class="wizard-stats">
					<div class="wizard-stat"><div class="stat-label">${this.t("BOQ Template")}</div><div class="stat-value">${tpl}</div></div>
					<div class="wizard-stat"><div class="stat-label">${this.t("Lines")}</div><div class="stat-value">${lines.length}</div></div>
					<div class="wizard-stat"><div class="stat-label">${this.t("Estimated value")}</div><div class="stat-value">${total}</div></div>
				</div>
				${this.render_boq_table(lines)}
				<p class="text-muted mt-3">${this.t("Click Next to review phases and IPC schedule.")}</p>
			`);
			return;
		}
		this.set_step_body(
			`<div class="wz-callout"><p class="mb-0">${this.t("Click Next to load the BOQ package for")} <b>${tpl}</b> — ${this.t("lines, phases, IPC, and detail pricing.")}</p></div>`
		);
	}

	render_boq_table(lines) {
		let rows = (lines || [])
			.map((r) => {
				const indent = r.parent_cost_code ? "&nbsp;&nbsp;" : "";
				const cost = this.format_money(r.planned_cost, this.setup.contract_currency);
				return `<tr><td>${indent}${frappe.utils.escape_html(r.cost_code)}</td><td>${frappe.utils.escape_html(r.item_description)}</td><td>${r.quantity || ""}</td><td>${cost}</td></tr>`;
			})
			.join("");
		return `<div class="wizard-table-wrap"><table class="table table-bordered table-sm table-hover"><thead><tr><th>${this.t("Code")}</th><th>${this.t("Description")}</th><th>${this.t("Qty")}</th><th>${this.t("Planned")}</th></tr></thead><tbody>${rows}</tbody></table></div>`;
	}

	render_editable_phases_table(phases) {
		const rows = (phases || [])
			.map(
				(p, idx) => `
			<tr class="wizard-phase-row" data-idx="${idx}">
				<td><input class="form-control form-control-sm" data-field="phase_code" value="${frappe.utils.escape_html(p.phase_code || "")}"></td>
				<td><input class="form-control form-control-sm" data-field="phase_name" value="${frappe.utils.escape_html(p.phase_name || "")}"></td>
				<td><input type="date" class="form-control form-control-sm" data-field="planned_finish" value="${p.planned_finish || ""}"></td>
				<td><input type="date" class="form-control form-control-sm" data-field="handover_date" value="${p.handover_date || ""}"></td>
				<td><input type="number" min="0" max="100" step="0.1" class="form-control form-control-sm" data-field="weight_percent" value="${p.weight_percent != null ? p.weight_percent : ""}"></td>
				<td><input class="form-control form-control-sm" data-field="boq_cost_prefixes" value="${frappe.utils.escape_html(p.boq_cost_prefixes || "")}" placeholder="01,02"></td>
				<td><button type="button" class="btn btn-xs btn-default wizard-phase-remove" title="${this.t("Remove")}"><i class="fa fa-trash"></i></button></td>
			</tr>`
			)
			.join("");
		return `<div class="wizard-table-wrap wizard-table-edit">
			<table class="table table-bordered table-sm table-hover">
				<thead><tr>
					<th>${this.t("Phase")}</th><th>${this.t("Name")}</th><th>${this.t("Finish")}</th>
					<th>${this.t("Handover")}</th><th>${this.t("Weight")}</th><th>${this.t("BOQ Prefixes")}</th><th></th>
				</tr></thead>
				<tbody id="wizard-phases-tbody">${rows}</tbody>
			</table>
			<button type="button" class="btn btn-sm btn-default mt-2 wizard-phase-add"><i class="fa fa-plus"></i> ${this.t("Add Phase")}</button>
		</div>`;
	}

	render_editable_boq_table(lines) {
		const rows = (lines || [])
			.filter((r) => !r.is_group)
			.map((r) => {
				const code = frappe.utils.escape_html(r.cost_code || "");
				const exec = (r.execution_mode || "Company").toString();
				const party = frappe.utils.escape_html(r.assigned_party || "");
				const mat = r.material_cost != null ? r.material_cost : "";
				const lab = r.labor_cost != null ? r.labor_cost : "";
				return `<tr class="wizard-boq-row" data-cost-code="${code}">
					<td><input type="checkbox" data-field="include" ${r.include ? "checked" : ""}></td>
					<td><code>${code}</code></td>
					<td class="desc-cell">${frappe.utils.escape_html(r.item_description || "")}</td>
					<td><select class="form-control form-control-sm" data-field="phase_code">${this.phase_select_options(r.phase_code)}</select></td>
					<td><select class="form-control form-control-sm" data-field="execution_mode">
						<option value="Company" ${exec === "Company" ? "selected" : ""}>${this.t("Company")}</option>
						<option value="Subcontractor" ${exec === "Subcontractor" ? "selected" : ""}>${this.t("Subcontractor")}</option>
					</select></td>
					<td><input class="form-control form-control-sm boq-party" value="${party}" placeholder="${this.t("Subcontractor")}"></td>
					<td><input type="number" step="0.01" class="form-control form-control-sm" data-field="material_cost" value="${mat}"></td>
					<td><input type="number" step="0.01" class="form-control form-control-sm" data-field="labor_cost" value="${lab}"></td>
				</tr>`;
			})
			.join("");
		return `<div class="wizard-table-wrap wizard-table-edit">
			<table class="table table-bordered table-sm table-hover">
				<thead><tr>
					<th>${this.t("Include")}</th><th>${this.t("Code")}</th><th>${this.t("Description")}</th>
					<th>${this.t("Phase")}</th><th>${this.t("Execution")}</th><th>${this.t("Subcontractor")}</th>
					<th>${this.t("Material")}</th><th>${this.t("Labor")}</th>
				</tr></thead>
				<tbody>${rows || `<tr><td colspan="8" class="text-muted">${this.t("No BOQ lines yet.")}</td></tr>`}</tbody>
			</table>
		</div>`;
	}

	render_editable_details_table(details) {
		const rows = (details || [])
			.slice(0, 120)
			.map((d) => {
				const code = frappe.utils.escape_html(d.boq_cost_code || "");
				const desc = frappe.utils.escape_html(d.spec_description || "");
				return `<tr class="wizard-detail-row" data-boq-code="${code}" data-detail-desc="${desc}" data-detail-name="${frappe.utils.escape_html(d.name || "")}">
					<td><code>${code}</code></td>
					<td class="desc-cell">${desc}</td>
					<td><input type="number" step="0.01" class="form-control form-control-sm" data-field="quantity" value="${d.quantity != null ? d.quantity : 1}"></td>
					<td><input type="number" step="0.01" class="form-control form-control-sm" data-field="material_rate" value="${d.material_rate != null ? d.material_rate : ""}"></td>
					<td><input type="number" step="0.01" class="form-control form-control-sm" data-field="labor_rate" value="${d.labor_rate != null ? d.labor_rate : ""}"></td>
					<td><input type="number" step="0.01" class="form-control form-control-sm" data-field="equipment_rate" value="${d.equipment_rate != null ? d.equipment_rate : ""}"></td>
				</tr>`;
			})
			.join("");
		const more =
			(details || []).length > 120
				? `<p class="text-muted small">${this.t("Showing first 120 detail lines. Edit the rest in Full Editor.")}</p>`
				: "";
		return `${more}<div class="wizard-table-wrap wizard-table-edit">
			<table class="table table-bordered table-sm table-hover">
				<thead><tr>
					<th>${this.t("BOQ Code")}</th><th>${this.t("Detail")}</th><th>${this.t("Qty")}</th>
					<th>${this.t("Material / unit")}</th><th>${this.t("Labor / unit")}</th><th>${this.t("Equipment / unit")}</th>
				</tr></thead>
				<tbody>${rows || `<tr><td colspan="6" class="text-muted">${this.t("No detail pricing rows.")}</td></tr>`}</tbody>
			</table>
		</div>`;
	}

	render_ipc_table(ipc_plan) {
		const rows = (ipc_plan || [])
			.map(
				(i) =>
					`<tr><td>${i.ipc_number}</td><td>${i.ipc_date || ""}</td><td>${i.cumulative_completion_percent || ""}%</td><td>${this.format_money(i.net_amount, this.setup.contract_currency)}</td><td>${i.retention_percent || ""}%</td><td>${i.discount_percent || 0}%</td></tr>`
			)
			.join("");
		return `<div class="wizard-table-wrap"><table class="table table-bordered table-sm table-hover"><thead><tr><th>#</th><th>${this.t("Date")}</th><th>${this.t("Cum. %")}</th><th>${this.t("Net")}</th><th>${this.t("Retention")}</th><th>${this.t("Discount")}</th></tr></thead><tbody>${rows}</tbody></table></div>`;
	}

	render_step6_phases_ipc() {
		const total = this.format_money(this.setup.estimated_contract_value, this.setup.contract_currency);
		const self = this;
		this.set_step_body(`
			<div class="wz-callout">${this.t("Add or edit delivery phases. Weights should total 100%. Changes are saved when you click Next.")}</div>
			<div class="wizard-stats">
				<div class="wizard-stat"><div class="stat-label">${this.t("Contract Value")}</div><div class="stat-value">${total}</div></div>
			</div>
			<div class="section-title">${this.t("Delivery Phases")}</div>
			${this.render_editable_phases_table(this.setup.phases)}
			<div class="section-title mt-4">${this.t("IPC Payment Schedule")}</div>
			${this.render_ipc_table(this.setup.ipc_plan)}
			<p class="text-muted small">${this.t("IPC rows follow phases after save.")}</p>
		`);
		this.body.find(".wizard-phase-add").on("click", () => {
			const n = (self.setup.phases || []).length + 1;
			const code = `PH-${String(n).padStart(2, "0")}`;
			self.setup.phases = self.setup.phases || [];
			self.setup.phases.push({
				phase_code: code,
				phase_name: `${self.t("Phase")} ${n}`,
				weight_percent: 0,
			});
			self.render_step6_phases_ipc();
		});
		this.body.find(".wizard-phase-remove").on("click", function () {
			const idx = cint($(this).closest(".wizard-phase-row").data("idx"));
			self.setup.phases = (self.setup.phases || []).filter((_, i) => i !== idx);
			self.render_step6_phases_ipc();
		});
	}

	render_step7_details() {
		const lines = (this.setup.boq_lines || []).filter((r) => r.include && !r.is_group);
		const details = this.setup.boq_details || [];
		const total = this.format_money(this.setup.estimated_contract_value, this.setup.contract_currency);
		this.set_step_body(`
			<div class="wz-callout">${this.t("Assign each line to your company or a subcontractor, and adjust material/labor costs.")}</div>
			<div class="wizard-stats">
				<div class="wizard-stat"><div class="stat-label">${this.t("Estimated Contract Value")}</div><div class="stat-value">${total}</div></div>
				<div class="wizard-stat"><div class="stat-label">${this.t("BOQ Lines")}</div><div class="stat-value">${lines.length}</div></div>
				<div class="wizard-stat"><div class="stat-label">${this.t("Detail Pricing")}</div><div class="stat-value">${details.length}</div></div>
			</div>
			<div class="section-title">${this.t("BOQ Lines — Phase & Assignment")}</div>
			${this.render_editable_boq_table(this.setup.boq_lines)}
			<div class="section-title mt-4">${this.t("Materials & Unit Rates (detail)")}</div>
			${this.render_editable_details_table(details)}
		`);
		this.body.find(".boq-party").each((_, el) => this.bind_subcontractor_input($(el)));
		this.body.find('[data-field="execution_mode"]').on("change", function () {
			const $row = $(this).closest(".wizard-boq-row");
			if ($(this).val() === "Company") {
				$row.find(".boq-party").val("");
			}
		});
	}

	render_assignments_table(assignments) {
		const rows = (assignments || [])
			.map((a) => {
				const trade = frappe.utils.escape_html(a.trade_package_code || "");
				const type = (a.assignment_type || "Subcontractor").toString();
				const party = frappe.utils.escape_html(a.party || "");
				return `<tr class="wizard-assign-row" data-trade="${trade}">
					<td>${trade}</td>
					<td class="desc-cell">${frappe.utils.escape_html(a.scope_notes || "")}</td>
					<td><select class="form-control form-control-sm" data-field="assignment_type">
						<option value="Company" ${type === "Company" ? "selected" : ""}>${this.t("Company")}</option>
						<option value="Subcontractor" ${type === "Subcontractor" ? "selected" : ""}>${this.t("Subcontractor")}</option>
						<option value="Supplier" ${type === "Supplier" ? "selected" : ""}>${this.t("Supplier")}</option>
					</select></td>
					<td><input class="form-control form-control-sm assign-party" value="${party}" placeholder="${this.t("Subcontractor")}"></td>
				</tr>`;
			})
			.join("");
		return `<div class="wizard-table-wrap wizard-table-edit"><table class="table table-bordered table-sm"><thead><tr>
			<th>${this.t("Trade")}</th><th>${this.t("Scope")}</th><th>${this.t("Execution")}</th><th>${this.t("Party")}</th>
		</tr></thead><tbody>${rows}</tbody></table></div>`;
	}

	render_step8_generate() {
		const total = this.format_money(this.setup.estimated_contract_value, this.setup.contract_currency);
		this.set_step_body(`
			<div class="wizard-generate-hero">
				<div class="gen-icon"><i class="fa fa-rocket"></i></div>
				<h4 class="gen-title">${this.t("Ready to generate")}</h4>
				<p class="gen-project">${frappe.utils.escape_html(this.setup.contract_title || "")}</p>
				<p class="gen-value">${total}</p>
			</div>
			<ul class="wizard-checklist">
				<li>${this.t("Project contract and BOQ items")}</li>
				<li>${this.t("Phases, IPC schedule, and detail pricing")}</li>
				<li>${this.t("Subcontracts, purchase requests, and transmittal")}</li>
			</ul>
			<div class="section-title">${this.t("Assignments")}</div>
			${this.render_assignments_table(this.setup.assignments)}
		`);
		this.body.find(".assign-party").each((_, el) => this.bind_subcontractor_input($(el)));
		this.body.find('[data-field="assignment_type"]').on("change", function () {
			const $row = $(this).closest(".wizard-assign-row");
			if ($(this).val() === "Company") {
				$row.find(".assign-party").val("");
			}
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

		// Steps 1–4: navigate immediately, persist in background (avoids freeze on financials / BOQ load)
		if (from_step <= 4) {
			if (from_step === 3) {
				this.ensure_step3_defaults();
			}
			const next_step = from_step + 1;
			let data = this.merge_persisted_fields(this.collect_step_data());
			if (from_step === 4) {
				data = this.sanitize_step4_data(data);
			}
			if (from_step === 2) {
				const bt = this.get_building_type();
				if (bt) {
					data.building_type = bt;
					this.setup.building_type = bt;
					this._selected_building_type = bt;
				}
			}
			this._apply_setup_patch(data);
			this.setup.wizard_step = next_step;
			this.step = next_step;
			this.render_step();
			if (from_step === 4) {
				this._call_save_step(
					next_step,
					data,
					() => {
						this.load_boq_preview_after_step4(() => {
							if (this.step < 5) {
								this.step = 5;
								this.setup.wizard_step = 5;
								this.render_step();
							}
						});
					},
					{ freeze: false, rollback_step: from_step }
				);
			} else {
				this._call_save_step(next_step, data, null, { freeze: false, rollback_step: from_step });
			}
			return;
		}

		if (from_step === 6) {
			this.persist_phases(() => {
				this.save_step(() => this.advance_after_save(from_step), { advance: true });
			});
			return;
		}
		if (from_step === 7) {
			this.persist_boq_edits(() => {
				this.save_step(() => this.advance_after_save(from_step), { advance: true });
			});
			return;
		}

		this.save_step(() => {
			this.advance_after_save(from_step);
		}, { advance: true });
	}

	advance_after_save(from_step) {
		if (from_step === 4) {
			return;
		}
		if (from_step === 5) {
			this.step = 6;
			this.setup.wizard_step = 6;
			this.reload_setup(() => this.render_step(), { keep_step: true });
			return;
		}
		if (from_step === 6) {
			this.step = 7;
			this.setup.wizard_step = 7;
			this.reload_setup(() => this.render_step(), { keep_step: true });
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
					this.setup.wizard_step = 8;
					this.reload_setup(() => this.render_step(), { keep_step: true });
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

	reload_setup(callback, opts = {}) {
		const keep_step = this.step;
		frappe.call({
			method: "omnexa_construction.wizard.wizard_api.get_wizard_context",
			args: this.wizard_context_args(),
			callback: (r) => {
				if (r.message && r.message.setup) {
					this.setup = r.message.setup;
					this.setup_name = this.setup.name || this.setup_name;
					this.building_types = r.message.building_types || this.building_types;
					if (!opts.keep_step) {
						const server_step = cint(this.setup.wizard_step) || 1;
						if (server_step >= keep_step) {
							this.step = server_step;
						}
					}
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
						if (r.exc) {
							this.show_wizard_error(
								r,
								this.t("Could not generate the project. Open the setup form error log for details.")
							);
							return;
						}
						if (!r.message || !r.message.project_contract) {
							this.show_wizard_error(
								r,
								this.t("Could not generate the project. Try saving the draft and reload the wizard.")
							);
							return;
						}
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
					error: (r) => {
						this.show_wizard_error(
							r,
							this.t("Could not generate the project. Check required fields and try again.")
						);
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
