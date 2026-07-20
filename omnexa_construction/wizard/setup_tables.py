from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import flt

from omnexa_construction.wizard.persist import save_wizard_setup
from omnexa_construction.wizard.pricing import recalculate_setup_pricing


def _load_setup(setup_name: str):
	if not setup_name or not frappe.db.exists("Construction Project Setup", setup_name):
		frappe.throw(_("Wizard draft not found."), title=_("Wizard"))
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	from omnexa_construction.wizard.setup_approval import is_setup_locked

	if is_setup_locked(setup):
		frappe.throw(_("Cannot edit an approved setup. Reopen for revision first."), title=_("Wizard"))
	return setup


def save_wizard_phases(setup_name: str, phases: str | list | None = None) -> dict:
	setup = _load_setup(setup_name)
	rows = json.loads(phases) if isinstance(phases, str) else (phases or [])
	setup.set("phases", [])
	for row in rows:
		code = (row.get("phase_code") or "").strip()
		name = (row.get("phase_name") or "").strip()
		if not code or not name:
			continue
		setup.append(
			"phases",
			{
				"phase_code": code,
				"phase_name": name,
				"phase_name_ar": (row.get("phase_name_ar") or "").strip() or None,
				"planned_start": row.get("planned_start") or None,
				"planned_finish": row.get("planned_finish") or None,
				"handover_date": row.get("handover_date") or None,
				"weight_percent": flt(row.get("weight_percent")),
				"boq_cost_prefixes": (row.get("boq_cost_prefixes") or "").strip() or None,
				"remarks": (row.get("remarks") or "").strip() or None
	},
		)
	save_wizard_setup(setup)
	return {"phases": [p.as_dict() for p in setup.phases]
	}


def save_wizard_boq_lines(setup_name: str, lines: str | list | None = None) -> dict:
	setup = _load_setup(setup_name)
	patches = json.loads(lines) if isinstance(lines, str) else (lines or [])
	by_code = {(r.cost_code or "").strip(): r for r in (setup.boq_lines or []) if r.cost_code}
	for patch in patches:
		code = (patch.get("cost_code") or "").strip()
		row = by_code.get(code)
		if not row or row.is_group:
			continue
		if "include" in patch:
			row.include = 1 if frappe.utils.cint(patch.get("include")) else 0
		if "phase_code" in patch:
			row.phase_code = (patch.get("phase_code") or "").strip() or None
		if "execution_mode" in patch:
			mode = (patch.get("execution_mode") or "Company").strip()
			row.execution_mode = mode if mode in ("Company", "Subcontractor") else "Company"
		if "assigned_party" in patch:
			party = (patch.get("assigned_party") or "").strip() or None
			row.assigned_party = party
			if party:
				row.execution_mode = "Subcontractor"
		if "material_cost" in patch:
			row.material_cost = flt(patch.get("material_cost"))
		if "labor_cost" in patch:
			row.labor_cost = flt(patch.get("labor_cost"))
		if "equipment_cost" in patch:
			row.equipment_cost = flt(patch.get("equipment_cost"))
		if "quantity" in patch:
			row.quantity = flt(patch.get("quantity"))
	recalculate_setup_pricing(setup)
	save_wizard_setup(setup)
	return {
		"boq_lines": [r.as_dict() for r in setup.boq_lines if r.include and not r.is_group],
		"estimated_contract_value": setup.estimated_contract_value
	}


def save_wizard_boq_details(setup_name: str, details: str | list | None = None) -> dict:
	setup = _load_setup(setup_name)
	patches = json.loads(details) if isinstance(details, str) else (details or [])
	by_key = {}
	for d in setup.boq_details or []:
		key = (d.boq_cost_code or "").strip(), (d.spec_description or "").strip()
		by_key[key] = d
	for patch in patches:
		code = (patch.get("boq_cost_code") or "").strip()
		desc = (patch.get("spec_description") or patch.get("detail_key") or "").strip()
		row = by_key.get((code, desc))
		if not row and patch.get("name"):
			row = next((d for d in setup.boq_details if d.name == patch.get("name")), None)
		if not row:
			continue
		for field in (
			"quantity",
			"unit_rate",
			"labor_rate",
			"material_rate",
			"equipment_rate",
			"spec_description",
			"spec_description_ar",
			"unit_of_measure",
			"remarks",
		):
			if field in patch:
				row.set(field, patch[field])
		if any(f in patch for f in ("quantity", "unit_rate", "labor_rate", "material_rate", "equipment_rate")):
			row.amount = flt(row.quantity) * (
				flt(row.unit_rate)
				or flt(row.labor_rate) + flt(row.material_rate) + flt(row.equipment_rate)
			)
	recalculate_setup_pricing(setup)
	save_wizard_setup(setup)
	return {
		"boq_details": [d.as_dict() for d in setup.boq_details],
		"estimated_contract_value": setup.estimated_contract_value
	}


def save_wizard_assignments_full(
	setup_name: str, assignments: str | list | None = None, sync_boq_lines: int | str = 1
) -> dict:
	setup = _load_setup(setup_name)
	rows = json.loads(assignments) if isinstance(assignments, str) else (assignments or [])
	by_trade = {r.get("trade_package_code"): r for r in rows if r.get("trade_package_code")}

	for assign in setup.assignments or []:
		patch = by_trade.get(assign.trade_package_code)
		if not patch:
			continue
		assign.assignment_type = patch.get("assignment_type") or assign.assignment_type or "Subcontractor"
		if assign.assignment_type == "Company":
			assign.party = None
		else:
			assign.party = (patch.get("party") or "").strip() or None

	if frappe.utils.cint(sync_boq_lines):
		for row in setup.boq_lines or []:
			if row.is_group or not row.trade_package_code:
				continue
			patch = by_trade.get(row.trade_package_code)
			if not patch:
				continue
			if patch.get("assignment_type") == "Company":
				row.execution_mode = "Company"
				row.assigned_party = None
			elif patch.get("party"):
				row.execution_mode = "Subcontractor"
				row.assigned_party = patch.get("party")

	save_wizard_setup(setup)
	return {"assignments": [a.as_dict() for a in setup.assignments or []]
	}
