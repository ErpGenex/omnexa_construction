from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_months, flt, getdate

from omnexa_construction.wizard.pricing import detail_amount, money, recalculate_setup_pricing
from omnexa_construction.wizard.template_packs import get_template_pack


def apply_template_defaults(setup, *, force_phases: bool = False, force_details: bool = False) -> dict:
	"""Apply phases, BOQ detail pricing, line LD/dates from template pack."""
	pack = get_template_pack(setup.boq_template, setup.building_type)
	if not pack:
		return {"applied": False}

	if not setup.planned_completion and setup.planned_start:
		setup.planned_completion = add_months(getdate(setup.planned_start), pack.get("duration_months", 18))
	elif not setup.planned_completion:
		setup.planned_completion = add_months(getdate(), pack.get("duration_months", 18))

	if not setup.planned_start:
		setup.planned_start = getdate()

	if not setup.retention_percent:
		setup.retention_percent = 5
	if not setup.advance_payment_percent:
		setup.advance_payment_percent = 10

	if force_phases or not setup.phases:
		_apply_phases(setup, pack)

	_apply_phase_dates_to_lines(setup)

	if force_details or not setup.boq_details:
		_apply_details(setup, pack)

	_apply_line_ld_defaults(setup, pack)

	return recalculate_setup_pricing(setup)


def _apply_phases(setup, pack: dict) -> None:
	setup.set("phases", [])
	start = getdate(setup.planned_start)
	for row in pack.get("phases", []):
		code, name_en, name_ar, prefixes, weight, m_start, m_dur = row
		p_start = add_months(start, m_start)
		p_finish = add_months(start, m_start + m_dur)
		setup.append(
			"phases",
			{
				"phase_code": code,
				"phase_name": name_en,
				"phase_name_ar": name_ar,
				"planned_start": p_start,
				"planned_finish": p_finish,
				"handover_date": p_finish,
				"weight_percent": weight,
				"boq_cost_prefixes": prefixes,
			},
		)

	setup.set("ipc_plan", [])
	retention = flt(setup.retention_percent) or 5
	discount = flt(setup.default_discount_percent)
	cumulative = 0.0
	contract_value = flt(setup.estimated_contract_value)
	advance_total = flt(setup.advance_payment_amount)
	if not advance_total and setup.advance_payment_percent and contract_value:
		advance_total = money(contract_value * flt(setup.advance_payment_percent) / 100.0)
		setup.advance_payment_amount = advance_total

	for i, phase in enumerate(setup.phases or [], start=1):
		cumulative += flt(phase.weight_percent)
		adv_rec = advance_total if i == len(setup.phases) else 0
		setup.append(
			"ipc_plan",
			{
				"ipc_number": i,
				"phase_code": phase.phase_code,
				"ipc_date": phase.handover_date,
				"period_from": phase.planned_start,
				"period_to": phase.handover_date,
				"cumulative_completion_percent": cumulative,
				"retention_percent": retention,
				"discount_percent": discount,
				"advance_recovery": adv_rec,
				"remarks": _("IPC at {0} handover").format(phase.phase_name),
			},
		)


def _apply_phase_dates_to_lines(setup) -> None:
	phase_by_code = {p.phase_code: p for p in (setup.phases or []) if p.phase_code}
	for row in setup.boq_lines or []:
		if not row.include or row.is_group:
			continue
		phase_code = row.phase_code
		if not phase_code:
			for pcode, p in phase_by_code.items():
				prefixes = [x.strip() for x in (p.boq_cost_prefixes or "").split(",") if x.strip()]
				if any((row.cost_code or "").startswith(pr) for pr in prefixes):
					phase_code = pcode
					row.phase_code = pcode
					break
		p = phase_by_code.get(phase_code)
		if not p:
			continue
		row.planned_start = row.planned_start or p.planned_start
		row.planned_finish = row.planned_finish or p.planned_finish


def _apply_details(setup, pack: dict) -> None:
	setup.set("boq_details", [])
	rules = pack.get("detail_rules") or []
	contract_ld_day = flt(setup.liquidated_damages_per_day)
	for row in setup.boq_lines or []:
		if not row.include or row.is_group:
			continue
		code = (row.cost_code or "").strip()
		planned = flt(row.planned_cost)
		if not planned:
			continue
		qty = flt(row.quantity) or 1.0
		matched_rules = [r for r in rules if code.endswith(r.get("suffix", ""))]
		specs = matched_rules[0]["specs"] if matched_rules else [
			("Labor", 0.40, 0.45, 0.15),
			("Materials", 0.10, 0.80, 0.10),
		]
		for spec_name, labor_pct, mat_pct, equip_pct in specs:
			amount = planned * (labor_pct + mat_pct + equip_pct)
			if amount <= 0:
				continue
			setup.append(
				"boq_details",
				{
					"boq_cost_code": code,
					"spec_description": f"{row.item_description} — {spec_name}",
					"quantity": qty,
					"unit_of_measure": row.unit_of_measure or "Nos",
					"labor_rate": money(amount * labor_pct / qty),
					"material_rate": money(amount * mat_pct / qty),
					"equipment_rate": money(amount * equip_pct / qty),
					"ld_per_day": money(contract_ld_day * 0.12 / max(len(specs), 1)),
					"ld_cap_days": row.ld_cap_days or 30,
					"planned_finish": row.planned_finish,
				},
			)
		for d in setup.boq_details:
			if d.boq_cost_code == code:
				d.amount = detail_amount(d)


def _apply_line_ld_defaults(setup, pack: dict) -> None:
	ld_day = flt(setup.liquidated_damages_per_day)
	ld_cap_pct = flt(setup.liquidated_damages_cap_percent) or 10
	for row in setup.boq_lines or []:
		if not row.include or row.is_group:
			continue
		if not row.ld_per_day and ld_day:
			row.ld_per_day = money(ld_day * 0.15)
		if not row.ld_cap_percent:
			row.ld_cap_percent = ld_cap_pct
		if not row.ld_cap_days:
			row.ld_cap_days = 30
