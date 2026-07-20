from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, add_months, flt, getdate

from omnexa_construction.wizard.pricing import money
from omnexa_construction.wizard.template_packs import get_template_pack


PHASE_BLUEPRINT = [
	("P1", "Substructure & Earthworks", "الأعمال الترابية والأساسات", "01,02", 25),
	("P2", "Structure & Envelope", "الهيكل والواجهات", "03,05", 35),
	("P3", "MEP Systems", "الأنظمة الكهربائية والميكانيكية", "09,10,11", 25),
	("P4", "Finishes & Handover", "التشطيبات والتسليم", "07,13,15", 15),
]


def expand_default_boq_details(setup) -> int:
	"""Create Labor / Material / Equipment detail rows for each leaf BOQ line without details."""
	existing = {(d.boq_cost_code or "").strip() for d in (setup.boq_details or [])}
	added = 0
	for row in setup.boq_lines or []:
		if not row.include or row.is_group:
			continue
		code = (row.cost_code or "").strip()
		if not code or code in existing:
			continue
		qty = flt(row.quantity) or 1.0
		planned = flt(row.planned_cost)
		if not planned:
			continue
		labor = flt(row.labor_cost) or planned * 0.4
		material = flt(row.material_cost) or planned * 0.5
		equipment = flt(row.equipment_cost) or planned * 0.1
		ld_day = flt(row.ld_per_day) or flt(setup.liquidated_damages_per_day) * 0.15
		for label, amount, rate_field in (
			("Labor", labor, "labor_rate"),
			("Materials", material, "material_rate"),
			("Equipment", equipment, "equipment_rate"),
		):
			if amount <= 0:
				continue
			setup.append(
				"boq_details",
				{
					"boq_cost_code": code,
					"spec_description": f"{row.item_description} — {label
	}",
					"quantity": qty,
					"unit_of_measure": row.unit_of_measure,
					rate_field: money(amount / qty),
					"ld_per_day": ld_day / 3.0 if ld_day else 0,
					"ld_cap_days": row.ld_cap_days or 30,
					"planned_finish": row.planned_finish
	},
			)
			added += 1
		existing.add(code)
	return added


def apply_phase_dates_to_boq(setup) -> None:
	phase_by_code = {p.phase_code: p for p in (setup.phases or []) if p.phase_code}
	for row in setup.boq_lines or []:
		if not row.include or row.is_group:
			continue
		phase = row.phase_code
		if not phase:
			for pcode, p in phase_by_code.items():
				prefixes = [x.strip() for x in (p.boq_cost_prefixes or "").split(",") if x.strip()]
				if any((row.cost_code or "").startswith(pr) for pr in prefixes):
					phase = pcode
					row.phase_code = pcode
					break
		p = phase_by_code.get(phase)
		if not p:
			continue
		if not row.planned_start:
			row.planned_start = p.planned_start
		if not row.planned_finish:
			row.planned_finish = p.planned_finish


def suggest_phases_and_ipc(setup) -> dict:
	"""Generate delivery phases and IPC payment schedule from BOQ + contract dates."""
	from omnexa_construction.wizard.apply_template_defaults import apply_template_defaults

	pack = get_template_pack(setup.boq_template, setup.building_type)
	if pack and pack.get("phases"):
		return apply_template_defaults(setup, force_phases=True, force_details=False)

	start = getdate(setup.planned_start) if setup.planned_start else getdate()
	end = getdate(setup.planned_completion) if setup.planned_completion else add_months(start, 18)
	duration_days = max((end - start).days, 90)
	retention = flt(setup.retention_percent) or 5.0
	discount = flt(setup.default_discount_percent)
	contract_value = flt(setup.estimated_contract_value)

	setup.set("phases", [])
	months_per_phase = duration_days / 30.0 / len(PHASE_BLUEPRINT)
	for i, (code, name_en, name_ar, prefixes, weight) in enumerate(PHASE_BLUEPRINT):
		p_start = add_days(start, int(i * months_per_phase * 30))
		p_finish = add_days(start, int((i + 1) * months_per_phase * 30))
		handover = p_finish
		setup.append(
			"phases",
			{
				"phase_code": code,
				"phase_name": name_en,
				"phase_name_ar": name_ar,
				"planned_start": p_start,
				"planned_finish": p_finish,
				"handover_date": handover,
				"weight_percent": weight,
				"boq_cost_prefixes": prefixes
	},
		)

	apply_phase_dates_to_boq(setup)

	setup.set("ipc_plan", [])
	cumulative = 0.0
	advance_total = flt(setup.advance_payment_amount)
	if not advance_total and setup.advance_payment_percent and contract_value:
		advance_total = money(contract_value * flt(setup.advance_payment_percent) / 100.0)
		setup.advance_payment_amount = advance_total

	for i, (code, _en, _ar, _pfx, weight) in enumerate(PHASE_BLUEPRINT, start=1):
		phase = next((p for p in setup.phases if p.phase_code == code), None)
		cumulative += flt(weight)
		period_from = phase.planned_start if phase else start
		period_to = phase.handover_date if phase else end
		ipc_date = phase.handover_date if phase else end
		adv_rec = 0.0
		if i == len(PHASE_BLUEPRINT) and advance_total:
			adv_rec = advance_total
		setup.append(
			"ipc_plan",
			{
				"ipc_number": i,
				"phase_code": code,
				"ipc_date": ipc_date,
				"period_from": period_from,
				"period_to": period_to,
				"cumulative_completion_percent": cumulative,
				"retention_percent": retention,
				"discount_percent": discount,
				"advance_recovery": adv_rec,
				"remarks": _("IPC at handover of phase {0}").format(code)
	},
		)

	return {"phases": len(setup.phases), "ipc_rows": len(setup.ipc_plan)
	}
