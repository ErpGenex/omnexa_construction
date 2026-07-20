from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import today

from omnexa_construction.wizard.boq_helpers import expand_default_boq_details, suggest_phases_and_ipc
from omnexa_construction.wizard.pricing import recalculate_setup_pricing
from omnexa_construction.wizard.apply_template_defaults import apply_template_defaults
from omnexa_construction.wizard.template_packs import BOQ_TEMPLATES, BUILDING_TYPE_META, TEMPLATE_PACKS


def _sanitize_company_branch(
	company: str | None,
	branch: str | None,
) -> tuple[str | None, str | None]:
	"""Drop invalid Link values sent from desk (labels, stale boot cache, etc.)."""
	company = (company or "").strip() or None
	branch = (branch or "").strip() or None
	if branch in ("__ALL__", "ALL", "all"):
		branch = None
	if company and not frappe.db.exists("Company", company):
		branch_guess = frappe.db.get_value("Branch", {"branch_name": company
	}, "name")
		if branch_guess:
			branch = branch or branch_guess
		company = None
	if branch and not frappe.db.exists("Branch", branch):
		branch = None
	if branch and company and frappe.db.get_value("Branch", branch, "company") != company:
		branch = None
	return company, branch


def _resolve_company_branch(
	company: str | None = None,
	branch: str | None = None,
	*,
	required: bool = True,
) -> tuple[str | None, str | None]:
	"""Resolve company/branch using ErpGenEx desk context and branch access fallbacks."""
	from omnexa_core.omnexa_core.branch_access import get_default_branch, get_default_company
	from omnexa_core.omnexa_core.session_context import get_view_context

	company, branch = _sanitize_company_branch(company, branch)

	if not company:
		ctx = get_view_context()
		company = _sanitize_company_branch(ctx.get("company"), None)[0] or get_default_company()

	if not company and required:
		frappe.throw(
			_(
				"Company is required. Set a default Company in User Preferences or select one from the desk company/branch switcher."
			),
			title=_("Wizard"),
		)

	if company and not branch:
		ctx = get_view_context()
		ctx_company, ctx_branch = _sanitize_company_branch(ctx.get("company"), ctx.get("branch"))
		if ctx_company == company and ctx_branch and not ctx.get("view_all_branches"):
			branch = ctx_branch
		if not branch:
			branch = get_default_branch(company)
		if not branch:
			branch = frappe.db.get_value(
				"Branch",
				{"company": company
	},
				"name",
				order_by="is_head_office desc, creation asc",
			)

	if company and required and not branch:
		frappe.throw(
			_("No branch is configured for company {0}. Create a Branch or assign User Branch Access.").format(
				company
			),
			title=_("Wizard"),
		)

	return company, branch


def _boq_template_available(template_code: str | None) -> bool:
	"""True when a BOQ template exists in DB or can be loaded from seed packs."""
	if not template_code:
		return False
	if frappe.db.exists("Construction BOQ Template", template_code):
		return True
	return template_code in TEMPLATE_PACKS


def _ensure_boq_template_in_db(template_code: str | None) -> bool:
	"""Create or refresh a Construction BOQ Template from seed packs when missing."""
	if not template_code:
		return False
	if frappe.db.exists("Construction BOQ Template", template_code):
		return True
	for tpl in BOQ_TEMPLATES:
		if tpl.get("template_code") == template_code:
			_upsert_boq_template(tpl, replace_lines=True)
			return True
	return False


@frappe.whitelist()
def get_building_types() -> list[dict]:
	"""All building / project types with BOQ template availability."""
	from omnexa_construction.wizard.building_type_registry import list_building_types_for_api

	out = list_building_types_for_api()
	for row in out:
		row["has_template"] = _boq_template_available(row.get("template_code"))
	return out


@frappe.whitelist()
def create_setup(company: str | None = None, branch: str | None = None) -> dict:
	"""Create a draft Construction Project Setup with company/branch defaults."""
	company, branch = _resolve_company_branch(company, branch)
	currency = frappe.db.get_value("Company", company, "default_currency") or "EGP"
	doc = frappe.get_doc(
		{
			"doctype": "Construction Project Setup",
			"company": company,
			"branch": branch,
			"contract_currency": currency,
			"contract_type": "Turnkey (EPC)",
			"delivery_model": "EPC Turnkey",
			"quality_tier": "Standard",
			"wizard_step": 1,
			"status": "Draft",
			"number_of_floors": 1,
			"basement_levels": 0
	}
	)
	doc.flags.wizard_save = True
	doc.insert(ignore_permissions=True)
	return {"name": doc.name, "company": company, "branch": branch
	}


def _setup_dict_for_wizard(setup) -> dict:
	"""JSON-safe setup payload; child tables included from BOQ step onward."""
	row = setup.as_dict(convert_dates_to_str=True)
	rcf = row.get("regional_cost_factor")
	if rcf and not frappe.db.exists("Regional Cost Factor", rcf):
		row["regional_cost_factor"] = None
	step = cint(setup.wizard_step) or 1
	if step < 5:
		for table in ("boq_lines", "phases", "ipc_plan"):
			row.pop(table, None)
	if step < 7:
		row.pop("boq_details", None)
	if step < 8 and not (setup.assignments or []):
		row.pop("assignments", None)
	return row


def _find_open_setup(company: str, branch: str | None = None) -> str | None:
	"""Reuse the user's latest in-progress wizard draft when possible."""
	filters = {
		"owner": frappe.session.user,
		"company": company,
		"status": "Draft",
		"docstatus": 0,
		"project_contract": ("is", "not set")}
	if branch:
		filters["branch"] = branch
	return frappe.db.get_value(
		"Construction Project Setup",
		filters,
		"name",
		order_by="modified desc",
	)


def _ensure_setup_company_branch(setup) -> None:
	"""Back-fill company/branch on older wizard drafts."""
	if setup.get("company") and setup.get("branch"):
		return
	company, branch = _resolve_company_branch(setup.get("company"), setup.get("branch"))
	if company and setup.get("company") != company:
		setup.company = company
	if branch and setup.get("branch") != branch:
		setup.branch = branch
	if setup.has_value_changed("company") or setup.has_value_changed("branch"):
		from omnexa_construction.wizard.persist import save_wizard_setup

		save_wizard_setup(setup)


def _load_setup_doc(setup_name: str | None, company: str | None, branch: str | None):
	if setup_name and frappe.db.exists("Construction Project Setup", setup_name):
		try:
			setup = frappe.get_doc("Construction Project Setup", setup_name)
			_ensure_setup_company_branch(setup)
			return setup
		except Exception:
			frappe.log_error(
				title="Construction Wizard — setup load failed",
				message=frappe.get_traceback(),
			)

	company, branch = _resolve_company_branch(company, branch)
	open_name = _find_open_setup(company, branch)
	if open_name:
		setup = frappe.get_doc("Construction Project Setup", open_name)
		_ensure_setup_company_branch(setup)
		return setup

	created = create_setup(company=company, branch=branch)
	return frappe.get_doc("Construction Project Setup", created["name"])


@frappe.whitelist()
def get_wizard_context(
	setup_name: str | None = None,
	company: str | None = None,
	branch: str | None = None,
) -> dict:
	"""Load or create a wizard draft; company/branch are resolved server-side when omitted."""
	company, branch = _sanitize_company_branch(company, branch)
	try:
		setup = _load_setup_doc(setup_name, company, branch)
		_ensure_setup_company_branch(setup)
		return {
			"setup": _setup_dict_for_wizard(setup),
			"building_types": get_building_types()
	}
	except frappe.ValidationError:
		raise
	except Exception as exc:
		frappe.log_error(title="Construction Wizard — get_wizard_context", message=frappe.get_traceback())
		frappe.throw(
			_("Could not load the wizard: {0}").format(str(exc) or _("Unknown error")),
			title=_("Wizard"),
		)


@frappe.whitelist()
def select_building_type(setup_name: str, building_type: str) -> dict:
	"""Save building type and apply BOQ template pack in one request."""
	if not setup_name or not frappe.db.exists("Construction Project Setup", setup_name):
		frappe.throw(_("Wizard draft not found. Reload the page."), title=_("Wizard"))
	if not building_type:
		frappe.throw(_("Building type is required."), title=_("Wizard"))
	save_wizard_step(setup_name, 2, {"building_type": building_type
	})
	result = load_building_type_template(setup_name)
	result["wizard_step"] = 2
	return result


@frappe.whitelist()
def save_wizard_step(setup_name: str, step: int, data: str | dict | None = None) -> dict:
	"""Persist wizard step fields onto Construction Project Setup."""
	import json

	setup = frappe.get_doc("Construction Project Setup", setup_name)
	payload = json.loads(data) if isinstance(data, str) else (data or {})
	allowed = {
		"company",
		"branch",
		"client",
		"contract_title",
		"contract_type",
		"contract_currency",
		"delivery_model",
		"planned_start",
		"planned_completion",
		"site_location",
		"project_segment",
		"building_type",
		"boq_template",
		"governing_standard",
		"quality_tier",
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
		"retention_percent",
		"advance_payment_percent",
		"advance_payment_amount",
		"default_discount_percent",
		"liquidated_damages_per_day",
		"liquidated_damages_cap_percent",
		"regional_cost_factor",
		"site_region",
	}
	float_fields = {
		"plot_area_m2",
		"gross_floor_area_m2",
		"road_length_m",
		"road_width_m",
		"pipe_network_km",
		"liquidated_damages_per_day",
	}
	int_fields = {
		"number_of_floors",
		"basement_levels",
		"unit_count",
		"bed_count",
		"key_count",
	}
	regional_payload = {
		k: payload.get(k)
		for k in ("regional_cost_factor", "site_region")
		if k in payload
	}
	for key, value in payload.items():
		if key not in allowed:
			continue
		if key in ("regional_cost_factor", "site_region"):
			continue
		if value in ("", None):
			continue
		if key in int_fields:
			setup.set(key, cint(value))
		elif key in float_fields:
			setup.set(key, flt(value))
		else:
			setup.set(key, value)
	if regional_payload:
		from omnexa_construction.wizard.regional_fields import apply_regional_fields

		apply_regional_fields(setup, regional_payload)
	setup.wizard_step = int(step)
	if setup.building_type and not setup.boq_template:
		meta = BUILDING_TYPE_META.get(setup.building_type, {})
		code = meta.get("template_code")
		if code and _ensure_boq_template_in_db(code):
			setup.boq_template = code
		if meta.get("segment"):
			setup.project_segment = setup.project_segment or meta.get("segment")
	if not setup.governing_standard and setup.boq_template:
		setup.governing_standard = frappe.db.get_value(
			"Construction BOQ Template", setup.boq_template, "default_governing_standard"
		)
	from omnexa_construction.wizard.governing_standards import normalize_governing_standard

	if setup.governing_standard:
		setup.governing_standard = normalize_governing_standard(
			setup.governing_standard,
			contract_type=setup.contract_type,
		)
	if int(step) >= 3:
		from omnexa_construction.wizard.spec_defaults import apply_wizard_spec_defaults

		apply_wizard_spec_defaults(setup)
	from omnexa_construction.wizard.persist import save_wizard_setup

	save_wizard_setup(setup)
	return {
		"name": setup.name,
		"wizard_step": setup.wizard_step,
		"status": setup.status,
		"modified": setup.modified
	}


@frappe.whitelist()
def recalculate_pricing(setup_name: str) -> dict:
	from omnexa_construction.wizard.setup_approval import ensure_setup_editable

	setup = ensure_setup_editable(setup_name)
	result = recalculate_setup_pricing(setup)
	from omnexa_construction.wizard.persist import save_wizard_setup

	save_wizard_setup(setup)
	return result


@frappe.whitelist()
def expand_boq_details(setup_name: str, replace: int | str = 0) -> dict:
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	if cint(replace):
		setup.set("boq_details", [])
	from omnexa_construction.wizard.template_packs import get_template_pack

	if get_template_pack(setup.boq_template, setup.building_type):
		result = apply_template_defaults(setup, force_phases=False, force_details=True)
	else:
		added = expand_default_boq_details(setup)
		result = {**recalculate_setup_pricing(setup), "added": added
	}
	from omnexa_construction.wizard.persist import save_wizard_setup

	save_wizard_setup(setup)
	return result


@frappe.whitelist()
def suggest_phases_ipc(setup_name: str, save: int | str = 1) -> dict:
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	result = apply_template_defaults(setup, force_phases=True, force_details=not setup.boq_details)
	if cint(save):
		from omnexa_construction.wizard.persist import save_wizard_setup

		save_wizard_setup(setup)
	return result


@frappe.whitelist()
def apply_full_template(setup_name: str) -> dict:
	"""Re-apply BOQ phases, details, and IPC from template (keeps manual BOQ line edits)."""
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	result = apply_template_defaults(setup, force_phases=True, force_details=True)
	from omnexa_construction.wizard.persist import save_wizard_setup

	save_wizard_setup(setup)
	return result


@frappe.whitelist()
def list_saved_setups(company: str | None = None, branch: str | None = None) -> list[dict]:
	filters: dict = {"status": ["in", ["Draft", "In Progress", "Ready"]]}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	return frappe.get_all(
		"Construction Project Setup",
		filters=filters,
		fields=[
			"name",
			"contract_title",
			"building_type",
			"wizard_step",
			"status",
			"estimated_contract_value",
			"modified",
		],
		order_by="modified desc",
		limit=50,
	)


def cint(value):
	from frappe.utils import cint as _cint

	return _cint(value)


def flt(value):
	from frappe.utils import flt as _flt

	return _flt(value)


def _upsert_boq_template(tpl: dict, *, replace_lines: bool = True) -> str:
	"""Insert or update a Construction BOQ Template from seed data."""
	code = tpl["template_code"]
	data = {k: v for k, v in tpl.items() if k != "lines"}
	lines = tpl.get("lines") or []
	if frappe.db.exists("Construction BOQ Template", code):
		doc = frappe.get_doc("Construction BOQ Template", code)
		for key, value in data.items():
			if key != "template_code" and hasattr(doc, key):
				setattr(doc, key, value)
		if replace_lines:
			doc.set("lines", [])
			for line in lines:
				doc.append("lines", line)
		doc.flags.ignore_permissions = True
		doc.save()
		return "updated"
	data = dict(tpl)
	lines = data.pop("lines")
	doc = frappe.get_doc({"doctype": "Construction BOQ Template", **data})
	for line in lines:
		doc.append("lines", line)
	doc.insert(ignore_permissions=True)
	return "created"


def import_seed_templates(*, sync_all: bool = False) -> dict:
	"""Idempotent import of trade packages and BOQ templates (patch / install)."""
	from omnexa_construction.wizard.template_loader import TRADE_PACKAGES

	trades = 0
	created = 0
	updated = 0
	for row in TRADE_PACKAGES:
		if frappe.db.exists("Construction Trade Package", row["trade_code"]):
			continue
		doc = frappe.get_doc({"doctype": "Construction Trade Package", **row})
		doc.insert(ignore_permissions=True)
		trades += 1
	for tpl in BOQ_TEMPLATES:
		code = tpl["template_code"]
		exists = frappe.db.exists("Construction BOQ Template", code)
		if not exists or sync_all:
			action = _upsert_boq_template(tpl, replace_lines=True)
			if action == "created":
				created += 1
			elif action == "updated":
				updated += 1
	return {"trade_packages": trades, "templates_created": created, "templates_updated": updated
	}


@frappe.whitelist()
def load_building_type_template(setup_name: str) -> dict:
	"""Set BOQ template, segment, dates, and governing standard from building type pack."""
	from frappe.utils import add_months, getdate

	from omnexa_construction.wizard.template_packs import get_template_pack

	setup = frappe.get_doc("Construction Project Setup", setup_name)
	meta = BUILDING_TYPE_META.get(setup.building_type or "", {})
	template_code = meta.get("template_code")
	if template_code:
		_ensure_boq_template_in_db(template_code)
		setup.boq_template = template_code
	if meta.get("segment"):
		setup.project_segment = meta["segment"]
	pack = get_template_pack(setup.boq_template, setup.building_type)
	if pack:
		from omnexa_construction.wizard.governing_standards import normalize_governing_standard

		raw_gov = pack.get("default_governing_standard") or setup.governing_standard
		setup.governing_standard = normalize_governing_standard(
			raw_gov,
			contract_type=setup.contract_type or pack.get("default_contract_type"),
		)
		if pack.get("quality_tier") and not setup.quality_tier:
			setup.quality_tier = pack["quality_tier"]
		if not setup.planned_start:
			setup.planned_start = getdate()
		if not setup.planned_completion:
			setup.planned_completion = add_months(
				getdate(setup.planned_start), pack.get("duration_months", 18)
			)
	from omnexa_construction.wizard.spec_defaults import apply_wizard_spec_defaults

	apply_wizard_spec_defaults(setup)
	from omnexa_construction.wizard.persist import save_wizard_setup

	save_wizard_setup(setup)
	result = {
		"building_type": setup.building_type,
		"boq_template": setup.boq_template,
		"project_segment": setup.project_segment,
		"governing_standard": setup.governing_standard,
		"quality_tier": setup.quality_tier,
		"duration_months": (pack or {
	}).get("duration_months"),
		"plot_area_m2": setup.plot_area_m2,
		"gross_floor_area_m2": setup.gross_floor_area_m2,
		"number_of_floors": setup.number_of_floors,
		"basement_levels": setup.basement_levels,
		"unit_count": setup.unit_count,
		"bed_count": setup.bed_count,
		"key_count": setup.key_count,
		"road_length_m": setup.road_length_m,
		"road_width_m": setup.road_width_m,
		"pipe_network_km": setup.pipe_network_km
	}
	return result


@frappe.whitelist()
def list_regional_cost_options(company: str | None = None) -> list[dict]:
	"""Region codes and cost factors for the wizard financials step."""
	company, _branch = _resolve_company_branch(company, None)
	if not company:
		return []
	rows = frappe.get_all(
		"Regional Cost Factor",
		filters={"company": company, "disabled": 0
	},
		fields=["name", "region_code", "region_name", "cost_factor", "is_default"],
		order_by="is_default desc, region_code asc",
	)
	return rows


@frappe.whitelist()
def save_wizard_phases(setup_name: str, phases: str | list | None = None) -> dict:
	from omnexa_construction.wizard.setup_tables import save_wizard_phases as _save

	return _save(setup_name, phases)


@frappe.whitelist()
def save_wizard_boq_lines(setup_name: str, lines: str | list | None = None) -> dict:
	from omnexa_construction.wizard.setup_tables import save_wizard_boq_lines as _save

	return _save(setup_name, lines)


@frappe.whitelist()
def save_wizard_boq_details(setup_name: str, details: str | list | None = None) -> dict:
	from omnexa_construction.wizard.setup_tables import save_wizard_boq_details as _save

	return _save(setup_name, details)


@frappe.whitelist()
def list_site_region_code_options(
	company: str | None = None,
	search: str | None = None,
	limit: int = 500,
) -> list[dict]:
	"""ISO country codes (all countries) plus company Regional Cost Factor region codes."""
	from omnexa_construction.wizard.site_region_codes import get_site_region_options

	company, _branch = _resolve_company_branch(company, None)
	return get_site_region_options(company=company, search=search, limit=cint(limit) or 500)


@frappe.whitelist()
def prepare_specifications_step(setup_name: str) -> dict:
	"""Ensure specification drivers exist before BOQ scaling (wizard step 3)."""
	if not setup_name or not frappe.db.exists("Construction Project Setup", setup_name):
		frappe.throw(_("Wizard draft not found. Reload the page."), title=_("Wizard"))
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	if not setup.building_type:
		frappe.throw(_("Building type is required."), title=_("Wizard"))
	from omnexa_construction.wizard.spec_defaults import apply_wizard_spec_defaults

	apply_wizard_spec_defaults(setup)
	return {
		"building_type": setup.building_type,
		"quality_tier": setup.quality_tier,
		"plot_area_m2": setup.plot_area_m2,
		"gross_floor_area_m2": setup.gross_floor_area_m2,
		"number_of_floors": setup.number_of_floors,
		"basement_levels": setup.basement_levels,
		"unit_count": setup.unit_count,
		"bed_count": setup.bed_count,
		"key_count": setup.key_count,
		"road_length_m": setup.road_length_m,
		"road_width_m": setup.road_width_m,
		"pipe_network_km": setup.pipe_network_km
	}


@frappe.whitelist()
def ensure_material_catalog(company: str | None = None) -> dict:
	company, _branch = _resolve_company_branch(company, None, required=True)
	from omnexa_construction.wizard.catalog_import import import_material_catalog

	return import_material_catalog(company)


@frappe.whitelist()
def create_rfq_from_pr(purchase_request: str) -> dict:
	from omnexa_construction.wizard.procurement_rfq import create_rfq_from_purchase_request

	name = create_rfq_from_purchase_request(purchase_request)
	return {"rfq": name
	}


@frappe.whitelist()
def evaluate_construction_rfq(rfq_name: str) -> dict:
	from omnexa_construction.wizard.procurement_rfq import evaluate_rfq

	out = evaluate_rfq(rfq_name)
	frappe.db.set_value("Construction RFQ", rfq_name, "status", "Evaluated")
	return out


@frappe.whitelist()
def export_setup_document_pack(setup_name: str) -> dict:
	from omnexa_construction.wizard.document_pack import export_project_document_pack

	return export_project_document_pack(setup_name)
