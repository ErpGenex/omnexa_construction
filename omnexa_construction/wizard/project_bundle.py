from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_months, cint, flt, getdate, today

from omnexa_construction.wizard.regional_cost import resolve_regional_factor
from omnexa_construction.wizard.residential_inventory import sync_residential_inventory_from_setup
from omnexa_construction.wizard.scaling import (
	build_drivers,
	line_planned_cost,
	resolve_quantity,
	rollup_setup_boq_lines,
	split_costs,
	unit_cost_with_quality,
)
from omnexa_construction.wizard.apply_template_defaults import apply_template_defaults
from omnexa_construction.wizard.boq_helpers import expand_default_boq_details
from omnexa_construction.wizard.catalog_import import import_material_catalog, resolve_item_code, ensure_catalog_item
from omnexa_construction.wizard.document_pack import export_project_document_pack
from omnexa_construction.wizard.material_bom import apply_material_bom_to_boq_items
from omnexa_construction.wizard.pricing import detail_amount, line_ld_cap_amount, money, recalculate_setup_pricing
from omnexa_construction.wizard.procurement_rfq import create_rfqs_for_setup
from omnexa_construction.wizard.template_packs import BUILDING_TYPE_META

# Trades where a separate Supplier row improves material PR / IPC traceability
MATERIAL_SUPPLY_TRADES = frozenset(
	{"TRD-CONC", "TRD-FACADE", "TRD-MEP-P", "TRD-MEP-H", "TRD-MEP-E", "TRD-FIN"}
)


def _trade_assignment_meta(trade_code: str) -> dict:
	row = frappe.db.get_value(
		"Construction Trade Package",
		trade_code,
		["trade_name", "boq_section_prefixes", "default_retention_percent"],
		as_dict=True,
	)
	return row or {}


def _boq_section_prefixes_for_trade(setup, trade_code: str, default_prefixes: str | None) -> str:
	prefixes: set[str] = set()
	for part in (default_prefixes or "").split(","):
		part = part.strip()
		if part:
			prefixes.add(part)
	for row in setup.boq_lines or []:
		if not row.include or row.is_group or row.trade_package_code != trade_code:
			continue
		code = str(row.cost_code or "").strip()
		if code:
			prefixes.add(code.split(".")[0])
	return ",".join(sorted(prefixes)) if prefixes else trade_code


def _bundle_has_submitted_documents(contract_name: str) -> bool:
	if frappe.db.exists("DocType", "IPC Certificate"):
		if frappe.db.exists("IPC Certificate", {"project_contract": contract_name, "docstatus": 1}):
			return True
	if frappe.db.exists("DocType", "Subcontract Payment Certificate"):
		if frappe.db.exists(
			"Subcontract Payment Certificate", {"project_contract": contract_name, "docstatus": 1}
		):
			return True
	return False


def _cleanup_wizard_bundle(contract_name: str) -> None:
	"""Remove draft wizard-generated documents before regenerate."""
	if _bundle_has_submitted_documents(contract_name):
		frappe.throw(
			_("Cannot regenerate: submitted certificates exist on contract {0}.").format(contract_name),
			title=_("Wizard"),
		)
	child_doctypes = [
		("IPC Certificate", "project_contract"),
		("Subcontract Work Order", "project_contract"),
		("Purchase Request", "project_contract"),
		("Construction RFQ", "project_contract"),
		("Construction Document Transmittal", "project_contract"),
	]
	for doctype, field in child_doctypes:
		if not frappe.db.exists("DocType", doctype):
			continue
		for name in frappe.get_all(doctype, filters={field: contract_name}, pluck="name"):
			frappe.delete_doc(doctype, name, force=1, ignore_permissions=True)
	boq_items = frappe.get_all("BOQ Item", filters={"project_contract": contract_name}, pluck="name")
	for name in sorted(boq_items, reverse=True):
		frappe.delete_doc("BOQ Item", name, force=1, ignore_permissions=True)
	frappe.delete_doc("Project Contract", contract_name, force=1, ignore_permissions=True)


def expand_template_to_lines(setup) -> list[dict]:
	"""Build BOQ preview lines from linked Construction BOQ Template."""
	if not setup.boq_template:
		frappe.throw(_("Select a BOQ Template first."), title=_("Wizard"))
	template = frappe.get_doc("Construction BOQ Template", setup.boq_template)
	drivers = build_drivers(setup)
	regional_factor = resolve_regional_factor(setup)
	quality = setup.quality_tier or template.quality_tier or "Standard"
	lines: list[dict] = []
	for row in template.lines:
		qty = resolve_quantity(row, drivers, regional_factor=regional_factor)
		uc = unit_cost_with_quality(row.unit_cost_base, quality)
		planned = line_planned_cost(qty, uc)
		labor, material, equipment = split_costs(
			planned, row.labor_ratio, row.material_ratio, row.equipment_ratio
		)
		lines.append(
			{
				"include": 1,
				"section_name": row.section_name,
				"cost_code": row.cost_code,
				"item_description": row.item_description,
				"parent_cost_code": row.parent_cost_code or "",
				"is_group": row.is_group,
				"quantity": qty,
				"unit_of_measure": row.unit_of_measure,
				"unit_cost": uc,
				"planned_cost": planned if not row.is_group else 0,
				"trade_package_code": row.trade_package_code or "",
				"labor_cost": labor,
				"material_cost": material,
				"equipment_cost": equipment,
			}
		)
	return rollup_setup_boq_lines(lines)


@frappe.whitelist()
def preview_boq(setup_name: str, save: int | str = 1) -> dict:
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	if setup.building_type and not setup.boq_template:
		meta = BUILDING_TYPE_META.get(setup.building_type, {})
		code = meta.get("template_code")
		if code and frappe.db.exists("Construction BOQ Template", code):
			setup.boq_template = code
			setup.project_segment = setup.project_segment or meta.get("segment")
	if not setup.boq_template:
		frappe.throw(_("BOQ Template is required. Choose a building type with a template."), title=_("Wizard"))
	lines = expand_template_to_lines(setup)
	total = sum(flt(r["planned_cost"]) for r in lines if r.get("include") and not r.get("is_group"))
	if cint(save):
		setup.set("boq_lines", [])
		for row in lines:
			setup.append("boq_lines", row)
		apply_template_defaults(setup, force_phases=not setup.phases, force_details=not setup.boq_details)
		result = {"estimated_contract_value": setup.estimated_contract_value}
		total = result["estimated_contract_value"]
		from omnexa_construction.wizard.persist import save_wizard_setup

		save_wizard_setup(setup)
	return {"lines": lines, "estimated_contract_value": total, "line_count": len(lines)}


@frappe.whitelist()
def suggest_assignments(setup_name: str, save: int | str = 1) -> dict:
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	trades: dict[str, float] = {}
	for row in setup.boq_lines or []:
		if not row.include or row.is_group or not row.trade_package_code:
			continue
		trades[row.trade_package_code] = trades.get(row.trade_package_code, 0) + flt(row.planned_cost)
	suggestions = []
	for code, value in sorted(trades.items(), key=lambda x: -x[1]):
		meta = _trade_assignment_meta(code)
		trade_name = meta.get("trade_name") or code
		prefixes = _boq_section_prefixes_for_trade(setup, code, meta.get("boq_section_prefixes"))
		retention = meta.get("default_retention_percent") or 5
		suggestions.append(
			{
				"assignment_type": "Subcontractor",
				"trade_package_code": code,
				"boq_section_codes": prefixes,
				"retention_percent": retention,
				"scope_notes": _("Subcontract package — {0} (est. {1})").format(trade_name, value),
			}
		)
		if code in MATERIAL_SUPPLY_TRADES:
			suggestions.append(
				{
					"assignment_type": "Supplier",
					"trade_package_code": code,
					"boq_section_codes": prefixes,
					"retention_percent": 0,
					"scope_notes": _("Materials supply — {0} (sections {1})").format(trade_name, prefixes),
				}
			)
	if cint(save):
		setup.set("assignments", [])
		for row in suggestions:
			setup.append("assignments", row)
		from omnexa_construction.wizard.persist import save_wizard_setup

		save_wizard_setup(setup)
	return {"assignments": suggestions}


@frappe.whitelist()
def save_wizard_assignments(setup_name: str, assignments: str | list | None = None) -> dict:
	"""Persist trade assignments (company / subcontractor) from wizard step 8."""
	from omnexa_construction.wizard.setup_tables import save_wizard_assignments_full

	return save_wizard_assignments_full(setup_name, assignments, sync_boq_lines=1)


@frappe.whitelist()
def create_project_bundle(setup_name: str, force: int | str = 0) -> dict:
	frappe.flags.in_wizard = True
	try:
		return _create_project_bundle(setup_name, force=cint(force))
	except Exception:
		setup = frappe.get_doc("Construction Project Setup", setup_name)
		setup.status = "Failed"
		setup.error_log = frappe.get_traceback(with_context=True)
		from omnexa_construction.wizard.persist import save_wizard_setup

		save_wizard_setup(setup)
		raise
	finally:
		frappe.flags.in_wizard = False


def _create_project_bundle(setup_name: str, force: int = 0) -> dict:
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	if setup.status == "Completed" and not force:
		frappe.throw(_("Setup already completed. Open the Project Contract or use force=1 to regenerate."), title=_("Wizard"))
	if setup.project_contract:
		if not force:
			frappe.throw(
				_("Project Contract {0} already exists. Use force=1 to regenerate.").format(setup.project_contract),
				title=_("Wizard"),
			)
		_cleanup_wizard_bundle(setup.project_contract)
		setup.project_contract = None
		setup.status = "Draft"
		from omnexa_construction.wizard.persist import save_wizard_setup

		save_wizard_setup(setup)
		setup.reload()
	setup.governing_standard = _normalized_governing_standard(setup)
	_validate_setup(setup)
	if not setup.boq_lines:
		preview_boq(setup_name, save=1)
		setup.reload()
	if not setup.assignments:
		suggest_assignments(setup_name, save=1)
		setup.reload()
	apply_template_defaults(setup)
	from omnexa_construction.wizard.persist import save_wizard_setup

	save_wizard_setup(setup)
	setup.reload()

	save_point = f"wizard_bundle_{frappe.generate_hash(length=10)}"
	frappe.db.savepoint(save_point)
	try:
		result = _execute_project_bundle(setup)
	except Exception:
		frappe.db.rollback(save_point=save_point)
		raise
	frappe.db.release_savepoint(save_point)
	return result


def _insert_boq_items_from_setup(setup, contract_name: str) -> tuple[list[str], dict[str, str], float]:
	"""Create BOQ Item rows on an existing Project Contract from setup lines."""
	boq_items: list[str] = []
	code_to_boq: dict[str, str] = {}
	ordered = _sort_boq_lines(list(setup.boq_lines))
	boq_meta = frappe.get_meta("BOQ Item")
	for row in ordered:
		if not row.include:
			continue
		parent = code_to_boq.get(row.parent_cost_code) if row.parent_cost_code else None
		planned = flt(row.planned_cost)
		payload = {
			"doctype": "BOQ Item",
			"project_contract": contract_name,
			"parent_boq_item": parent,
			"is_group": row.is_group,
			"section_name": row.section_name or row.cost_code,
			"cost_code": row.cost_code,
			"item_description": row.item_description,
			"quantity": 0 if row.is_group else flt(row.quantity),
			"unit_of_measure": row.unit_of_measure,
			"unit_cost": 0 if row.is_group else flt(row.unit_cost),
			"labor_cost": flt(row.labor_cost),
			"material_cost": flt(row.material_cost),
			"equipment_cost": flt(row.equipment_cost),
			"company": setup.company,
			"branch": setup.branch,
		}
		if boq_meta.has_field("planned_start_date") and row.planned_start:
			payload["planned_start_date"] = row.planned_start
		if boq_meta.has_field("planned_completion_date") and row.planned_finish:
			payload["planned_completion_date"] = row.planned_finish
		if boq_meta.has_field("construction_phase") and row.phase_code:
			payload["construction_phase"] = row.phase_code
		if boq_meta.has_field("liquidated_damages_per_day"):
			payload["liquidated_damages_per_day"] = flt(row.ld_per_day)
		if boq_meta.has_field("liquidated_damages_cap_amount") and not row.is_group:
			payload["liquidated_damages_cap_amount"] = line_ld_cap_amount(row, planned)
		if boq_meta.has_field("boq_item_details") and not row.is_group:
			payload["boq_item_details"] = _boq_details_for_line(setup, row.cost_code)
		boq = frappe.get_doc(payload)
		boq.insert(ignore_permissions=True)
		code_to_boq[row.cost_code] = boq.name
		boq_items.append(boq.name)
	contract_value = sum(flt(r.planned_cost) for r in setup.boq_lines if r.include and not r.is_group)
	return boq_items, code_to_boq, contract_value


def sync_boq_items_from_setup(setup, contract_name: str) -> dict:
	"""Replace contract BOQ from setup (caller must ensure no submitted IPCs)."""
	if _bundle_has_submitted_documents(contract_name):
		frappe.throw(
			_("Cannot resync BOQ: submitted certificates exist on {0}.").format(contract_name),
			title=_("Sync"),
		)
	for name in sorted(
		frappe.get_all("BOQ Item", filters={"project_contract": contract_name}, pluck="name"),
		reverse=True,
	):
		frappe.delete_doc("BOQ Item", name, force=1, ignore_permissions=True)
	boq_items, code_to_boq, contract_value = _insert_boq_items_from_setup(setup, contract_name)
	bom_count = apply_material_bom_to_boq_items(setup, code_to_boq)
	frappe.db.set_value(
		"Project Contract",
		contract_name,
		{"contract_value": contract_value, "revised_contract_value": contract_value},
		update_modified=True,
	)
	return {"boq_items": len(boq_items), "material_bom_lines": bom_count, "contract_value": contract_value}


def _execute_project_bundle(setup) -> dict:
	import_material_catalog(setup.company)

	boq_items: list[str] = []
	scw_names: list[str] = []
	pr_names: list[str] = []
	rfq_names: list[str] = []
	ipc_names: list[str] = []

	contract = _create_project_contract(setup)
	boq_items, code_to_boq, contract_value = _insert_boq_items_from_setup(setup, contract.name)
	bom_count = apply_material_bom_to_boq_items(setup, code_to_boq)

	frappe.db.set_value(
		"Project Contract",
		contract.name,
		{"contract_value": contract_value, "revised_contract_value": contract_value},
		update_modified=True,
	)

	trade_boq: dict[str, list[str]] = {}
	party_boq: dict[str, list[str]] = {}
	for row in setup.boq_lines:
		if not row.include or row.is_group:
			continue
		name = code_to_boq.get(row.cost_code)
		if not name:
			continue
		exec_mode = (getattr(row, "execution_mode", None) or "Company").strip()
		party = (getattr(row, "assigned_party", None) or "").strip()
		if exec_mode == "Subcontractor" and party:
			party_boq.setdefault(party, []).append(name)
		elif row.trade_package_code:
			trade_boq.setdefault(row.trade_package_code, []).append(name)

	created_parties: set[str] = set()
	for party, linked in party_boq.items():
		scope_value = sum(flt(frappe.db.get_value("BOQ Item", b, "planned_cost")) for b in linked)
		scw = frappe.get_doc(
			{
				"doctype": "Subcontract Work Order",
				"project_contract": contract.name,
				"subcontractor": party,
				"scope_of_work": _("BOQ lines assigned to {0} — {1}").format(party, setup.contract_title),
				"contract_value": scope_value,
				"status": "Active",
				"company": setup.company,
				"branch": setup.branch,
			}
		)
		scw.insert(ignore_permissions=True)
		scw_names.append(scw.name)
		created_parties.add(party)

	for assign in setup.assignments or []:
		if assign.assignment_type == "Company" or not assign.party:
			continue
		if assign.party in created_parties:
			continue
		trade = assign.trade_package_code
		linked = trade_boq.get(trade, [])
		if not linked:
			continue
		scope_value = sum(flt(frappe.db.get_value("BOQ Item", b, "planned_cost")) for b in linked)
		trade_label = frappe.db.get_value("Construction Trade Package", trade, "trade_name") or trade
		scw = frappe.get_doc(
			{
				"doctype": "Subcontract Work Order",
				"project_contract": contract.name,
				"subcontractor": assign.party,
				"scope_of_work": assign.scope_notes
				or _("Trade package {0} — {1}").format(trade_label, setup.contract_title),
				"contract_value": scope_value,
				"status": "Active",
				"company": setup.company,
				"branch": setup.branch,
			}
		)
		scw.insert(ignore_permissions=True)
		scw_names.append(scw.name)
		created_parties.add(assign.party)

	if frappe.db.exists("DocType", "Purchase Request"):
		pr_names.extend(_create_purchase_requests(setup, contract.name, code_to_boq))

	if frappe.db.exists("DocType", "Construction RFQ") and pr_names:
		rfq_names = create_rfqs_for_setup(setup, pr_names, project_contract=contract.name)

	transmittal = _create_kickoff_transmittal(setup, contract.name)
	ipc_names = _create_ipc_schedule_drafts(setup, contract.name)
	pack = export_project_document_pack(setup.name)
	inventory = sync_residential_inventory_from_setup(setup, contract.name)

	final = frappe.get_doc("Construction Project Setup", setup.name)
	final.project_contract = contract.name
	final.document_transmittal = transmittal
	final.generated_boq_count = len(boq_items)
	final.generated_scw_count = len(scw_names)
	final.generated_pr_count = len(pr_names)
	final.generated_rfq_count = len(rfq_names)
	final.generated_ipc_count = len(ipc_names)
	if pack.get("file_url"):
		final.document_pack_file = pack["file_url"]
	final.approval_status = final.approval_status or "Open"
	final.status = "Completed"
	final.wizard_step = 8
	final.flags.ignore_permissions = True
	final.flags.wizard_save = True
	final.flags.ignore_version_check = True
	final.save()

	return {
		"project_contract": contract.name,
		"boq_items": boq_items,
		"material_bom_lines": bom_count,
		"scw": scw_names,
		"pr": pr_names,
		"rfq": rfq_names,
		"transmittal": transmittal,
		"ipc": ipc_names,
		"document_pack": pack,
		"residential_inventory": inventory,
		"contract_value": contract_value,
	}


def _boq_details_for_line(setup, cost_code: str) -> list[dict]:
	rows = []
	for d in setup.boq_details or []:
		if (d.boq_cost_code or "").strip() != cost_code:
			continue
		rows.append(
			{
				"spec_description": d.spec_description,
				"quantity": flt(d.quantity),
				"unit_of_measure": d.unit_of_measure,
				"unit_rate": flt(d.unit_rate) or detail_amount(d) / max(flt(d.quantity), 1),
				"labor_amount": money(flt(d.quantity) * flt(d.labor_rate)),
				"material_amount": money(flt(d.quantity) * flt(d.material_rate)),
				"equipment_amount": money(flt(d.quantity) * flt(d.equipment_rate)),
				"amount": detail_amount(d),
				"ld_per_day": flt(d.ld_per_day),
				"ld_cap_days": d.ld_cap_days,
				"ld_cap_amount": flt(d.ld_cap_amount),
				"planned_finish": d.planned_finish,
			}
		)
	return rows


def _create_ipc_schedule_drafts(setup, contract_name: str) -> list[str]:
	if not frappe.db.exists("DocType", "IPC Certificate"):
		return []
	names = []
	contract_value = flt(setup.estimated_contract_value)
	prior_pct = 0.0
	for plan in sorted(setup.ipc_plan or [], key=lambda r: int(r.ipc_number or 0)):
		cur_pct = flt(plan.cumulative_completion_percent)
		ipc = frappe.get_doc(
			{
				"doctype": "IPC Certificate",
				"project_contract": contract_name,
				"ipc_date": plan.ipc_date or today(),
				"period_from": plan.period_from,
				"period_to": plan.period_to,
				"boq_completion_percent": cur_pct,
				"billable_contract_value": contract_value,
				"advance_recovery": flt(plan.advance_recovery),
				"status": "Draft",
				"company": setup.company,
				"branch": setup.branch,
				"certificate_reference": _("WIZ-IPC-{0}-{1}").format(setup.name, plan.ipc_number),
			}
		)
		if ipc.meta.has_field("discount_percent"):
			ipc.discount_percent = flt(plan.discount_percent)
		ipc.insert(ignore_permissions=True)
		names.append(ipc.name)
		prior_pct = cur_pct
	return names


def _normalized_governing_standard(setup) -> str:
	from omnexa_construction.wizard.governing_standards import normalize_governing_standard

	return normalize_governing_standard(
		setup.governing_standard,
		contract_type=setup.contract_type,
	)


def _validate_setup(setup) -> None:
	required = ["company", "branch", "client", "contract_title", "contract_type", "contract_currency"]
	for field in required:
		if not setup.get(field):
			frappe.throw(_("Missing required field: {0}").format(field), title=_("Wizard"))
	if not setup.building_type:
		frappe.throw(_("Building / project type is required."), title=_("Wizard"))


def _create_project_contract(setup):
	start = getdate(setup.planned_start or today())
	end = getdate(setup.planned_completion or add_months(start, 18))
	doc = frappe.get_doc(
		{
			"doctype": "Project Contract",
			"contract_title": setup.contract_title,
			"contract_type": setup.contract_type,
			"client": setup.client,
			"contract_currency": setup.contract_currency,
			"delivery_model": setup.delivery_model,
			"governing_standard": _normalized_governing_standard(setup),
			"project_segment": setup.project_segment,
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
			"pipe_network_km": setup.pipe_network_km,
			"wizard_setup": setup.name,
			"planned_start": start,
			"planned_completion": end,
			"site_location": setup.site_location,
			"contract_value": flt(setup.estimated_contract_value),
			"revised_contract_value": flt(setup.estimated_contract_value),
			"retention_percent": flt(setup.retention_percent) or 5,
			"advance_payment": flt(setup.advance_payment_amount),
			"liquidated_damages_per_day": flt(setup.liquidated_damages_per_day),
			"liquidated_damages_cap_percent": flt(setup.liquidated_damages_cap_percent),
			"status": "Active",
			"company": setup.company,
			"branch": setup.branch,
		}
	)
	doc.insert(ignore_permissions=True)
	if doc.meta.is_submittable:
		doc.submit()
	return doc


def _sort_boq_lines(rows):
	"""Parents before children."""
	rows = list(rows)
	ordered: list = []
	seen: set[str] = set()

	def visit(code: str | None):
		for row in rows:
			if row.cost_code in seen:
				continue
			parent = row.parent_cost_code or ""
			if (code is None and not parent) or parent == code:
				seen.add(row.cost_code)
				ordered.append(row)
				visit(row.cost_code)

	for _ in range(len(rows) + 1):
		before = len(ordered)
		visit(None)
		if len(ordered) == before:
			break
	for row in rows:
		if row.cost_code not in seen:
			ordered.append(row)
	return ordered


def _create_purchase_requests(setup, contract_name: str, code_to_boq: dict[str, str]) -> list[str]:
	pr_names: list[str] = []
	supplier_lines: dict[str, list] = {}
	for assign in setup.assignments or []:
		if assign.assignment_type != "Supplier" or not assign.party:
			continue
		supplier_lines.setdefault(assign.party, [])

	# Build PR per supplier assignment with material-heavy BOQ lines
	for assign in setup.assignments or []:
		if assign.assignment_type != "Supplier" or not assign.party:
			continue
		prefixes = [p.strip() for p in (assign.boq_section_codes or "").split(",") if p.strip()]
		items = []
		for row in setup.boq_lines:
			if not row.include or row.is_group:
				continue
			if prefixes and not any(row.cost_code.startswith(p) for p in prefixes):
				continue
			boq_name = code_to_boq.get(row.cost_code)
			if not boq_name:
				continue
			item_code = resolve_item_code(
				row.trade_package_code,
				spec_hint=row.item_description or "",
				uom=row.unit_of_measure,
				company=setup.company,
			) or _default_item_for_trade(row.trade_package_code, setup.company)
			if not item_code:
				continue
			bom_qty = max(flt(row.quantity) * 0.2, 1)
			items.append(
				{
					"item_code": item_code,
					"qty": bom_qty,
					"purpose": row.item_description,
					"boq_item": boq_name,
					"cost_code": row.cost_code,
				}
			)
		if not items:
			continue
		pr = frappe.get_doc(
			{
				"doctype": "Purchase Request",
				"company": setup.company,
				"branch": setup.branch,
				"project_contract": contract_name,
				"required_by": setup.planned_start or today(),
				"requester": frappe.session.user,
				"reference": _("Wizard PR — {0}").format(setup.name),
				"remarks": assign.scope_notes or _("Materials for {0}").format(setup.contract_title),
				"items": items,
			}
		)
		pr.insert(ignore_permissions=True)
		pr_names.append(pr.name)

	if not pr_names:
		items = []
		for row in setup.boq_lines:
			if not row.include or row.is_group or flt(row.material_cost) <= 0:
				continue
			boq_name = code_to_boq.get(row.cost_code)
			item_code = resolve_item_code(
				row.trade_package_code,
				spec_hint=row.item_description or "",
				company=setup.company,
			)
			if not item_code or not boq_name:
				continue
			items.append(
				{
					"item_code": item_code,
					"qty": max(flt(row.quantity) * 0.15, 1),
					"purpose": row.item_description,
					"boq_item": boq_name,
					"cost_code": row.cost_code,
				}
			)
			if len(items) >= 12:
				break
		if items:
			pr = frappe.get_doc(
				{
					"doctype": "Purchase Request",
					"company": setup.company,
					"branch": setup.branch,
					"project_contract": contract_name,
					"required_by": setup.planned_start or today(),
					"requester": frappe.session.user,
					"reference": _("Wizard PR Materials — {0}").format(setup.name),
					"remarks": _("Auto material package from BOQ"),
					"items": items,
				}
			)
			pr.insert(ignore_permissions=True)
			pr_names.append(pr.name)
	return pr_names


def _default_item_for_trade(trade_code: str | None, company: str) -> str | None:
	candidates = {
		"TRD-EARTH": "MAT-SAND-FINE",
		"TRD-SUB": "MAT-RMX-C30",
		"TRD-CONC": "MAT-RMX-C30",
		"TRD-ROAD": "MAT-ASPHALT",
		"TRD-PIPE": "MAT-PVC-110",
		"TRD-MEP-P": "MAT-PVC-110",
		"TRD-MEP-E": "MAT-CABLE-16",
		"TRD-FIN": "MAT-TILE-60",
	}
	suffix = candidates.get(trade_code or "", "MAT-RMX-C30")
	import_material_catalog(company, limit=50)
	code = ensure_catalog_item(suffix, company)
	if code:
		return code
	return resolve_item_code(trade_code, company=company)


def _create_kickoff_transmittal(setup, contract_name: str) -> str | None:
	if not frappe.db.exists("DocType", "Construction Document Transmittal"):
		return None
	doc = frappe.get_doc(
		{
			"doctype": "Construction Document Transmittal",
			"project_contract": contract_name,
			"transmittal_date": today(),
			"reference_no": _("WIZ-{0}").format(setup.name),
			"issued_by": frappe.session.user,
			"recipient_notes": _("Project kickoff document pack from Construction Project Wizard."),
			"status": "Issued",
			"company": setup.company,
			"branch": setup.branch,
			"items": [
				{
					"document_title": _("Project Contract Summary"),
					"document_no": contract_name,
					"revision_no": "A",
					"issue_purpose": "For Record",
					"remarks": setup.contract_title,
				},
				{
					"document_title": _("BOQ Schedule"),
					"document_no": setup.boq_template,
					"revision_no": "A",
					"issue_purpose": "For Construction",
					"remarks": _("Generated from template {0}").format(setup.boq_template),
				},
				{
					"document_title": _("Subcontract Scope Sheets"),
					"revision_no": "A",
					"issue_purpose": "For Tender",
				},
			],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name