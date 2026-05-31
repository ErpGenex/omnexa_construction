from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import today

from omnexa_construction.wizard.boq_helpers import expand_default_boq_details, suggest_phases_and_ipc
from omnexa_construction.wizard.pricing import recalculate_setup_pricing
from omnexa_construction.wizard.apply_template_defaults import apply_template_defaults
from omnexa_construction.wizard.template_packs import BUILDING_TYPE_META, BOQ_TEMPLATES


@frappe.whitelist()
def get_building_types() -> list[dict]:
	"""Building types available in Phase 4 MVP wizard."""
	out = []
	for code, meta in BUILDING_TYPE_META.items():
		out.append(
			{
				"code": code,
				"label_en": meta.get("label_en", code),
				"label_ar": meta.get("label_ar", code),
				"segment": meta.get("segment"),
				"template_code": meta.get("template_code"),
				"has_template": bool(
					meta.get("template_code")
					and frappe.db.exists("Construction BOQ Template", meta.get("template_code"))
				),
			}
		)
	return out


@frappe.whitelist()
def create_setup(company: str | None = None, branch: str | None = None) -> dict:
	"""Create a draft Construction Project Setup with company/branch defaults."""
	if not company:
		company = frappe.defaults.get_user_default("Company")
	if not company:
		frappe.throw(_("Company is required."), title=_("Wizard"))
	if not branch:
		branch = frappe.db.get_value("Branch", {"company": company}, "name", order_by="creation asc")
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
			"basement_levels": 0,
		}
	)
	doc.insert(ignore_permissions=True)
	return {"name": doc.name, "company": company, "branch": branch}


@frappe.whitelist()
def get_wizard_context(setup_name: str | None = None) -> dict:
	if setup_name and frappe.db.exists("Construction Project Setup", setup_name):
		setup = frappe.get_doc("Construction Project Setup", setup_name)
	else:
		created = create_setup()
		setup = frappe.get_doc("Construction Project Setup", created["name"])
	return {
		"setup": setup.as_dict(),
		"building_types": get_building_types(),
		"templates": frappe.get_all(
			"Construction BOQ Template",
			filters={"is_active": 1},
			fields=["name", "template_name", "template_name_ar", "building_type", "project_segment"],
		),
	}


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
	for key, value in payload.items():
		if key in allowed:
			setup.set(key, value)
	setup.wizard_step = int(step)
	if setup.building_type and not setup.boq_template:
		meta = BUILDING_TYPE_META.get(setup.building_type, {})
		code = meta.get("template_code")
		if code and frappe.db.exists("Construction BOQ Template", code):
			setup.boq_template = code
		if meta.get("segment"):
			setup.project_segment = setup.project_segment or meta.get("segment")
	if not setup.governing_standard and setup.boq_template:
		setup.governing_standard = frappe.db.get_value(
			"Construction BOQ Template", setup.boq_template, "default_governing_standard"
		)
	setup.flags.ignore_permissions = True
	setup.save()
	return {"name": setup.name, "wizard_step": setup.wizard_step, "status": setup.status}


@frappe.whitelist()
def recalculate_pricing(setup_name: str) -> dict:
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	if setup.status == "Completed":
		frappe.throw(_("Cannot recalculate a completed setup. Reopen as copy."), title=_("Wizard"))
	result = recalculate_setup_pricing(setup)
	setup.flags.ignore_permissions = True
	setup.save()
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
		result = {**recalculate_setup_pricing(setup), "added": added}
	setup.flags.ignore_permissions = True
	setup.save()
	return result


@frappe.whitelist()
def suggest_phases_ipc(setup_name: str, save: int | str = 1) -> dict:
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	result = apply_template_defaults(setup, force_phases=True, force_details=not setup.boq_details)
	if cint(save):
		setup.flags.ignore_permissions = True
		setup.save()
	return result


@frappe.whitelist()
def apply_full_template(setup_name: str) -> dict:
	"""Re-apply BOQ phases, details, and IPC from template (keeps manual BOQ line edits)."""
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	result = apply_template_defaults(setup, force_phases=True, force_details=True)
	setup.flags.ignore_permissions = True
	setup.save()
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
	return {"trade_packages": trades, "templates_created": created, "templates_updated": updated}


@frappe.whitelist()
def load_building_type_template(setup_name: str) -> dict:
	"""Set BOQ template, segment, dates, and governing standard from building type pack."""
	from frappe.utils import add_months, getdate

	from omnexa_construction.wizard.template_packs import get_template_pack

	setup = frappe.get_doc("Construction Project Setup", setup_name)
	meta = BUILDING_TYPE_META.get(setup.building_type or "", {})
	if meta.get("template_code"):
		setup.boq_template = meta["template_code"]
	if meta.get("segment"):
		setup.project_segment = meta["segment"]
	pack = get_template_pack(setup.boq_template, setup.building_type)
	if pack:
		setup.governing_standard = pack.get("default_governing_standard") or setup.governing_standard
		if pack.get("quality_tier") and not setup.quality_tier:
			setup.quality_tier = pack["quality_tier"]
		if not setup.planned_start:
			setup.planned_start = getdate()
		if not setup.planned_completion:
			setup.planned_completion = add_months(
				getdate(setup.planned_start), pack.get("duration_months", 18)
			)
	setup.flags.ignore_permissions = True
	setup.save()
	return {
		"boq_template": setup.boq_template,
		"project_segment": setup.project_segment,
		"governing_standard": setup.governing_standard,
		"duration_months": (pack or {}).get("duration_months"),
	}


@frappe.whitelist()
def ensure_material_catalog(company: str | None = None) -> dict:
	if not company:
		company = frappe.defaults.get_user_default("Company")
	if not company:
		frappe.throw(_("Company is required."), title=_("Catalog"))
	from omnexa_construction.wizard.catalog_import import import_material_catalog

	return import_material_catalog(company)


@frappe.whitelist()
def create_rfq_from_pr(purchase_request: str) -> dict:
	from omnexa_construction.wizard.procurement_rfq import create_rfq_from_purchase_request

	name = create_rfq_from_purchase_request(purchase_request)
	return {"rfq": name}


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
