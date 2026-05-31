from __future__ import annotations

"""Precise BOQ / IPC pricing for Construction Project Wizard."""

from frappe.utils import flt, rounded

from omnexa_construction.ipc_billing import compute_ipc_amounts as _base_ipc_amounts

MONEY_PRECISION = 2


def money(value) -> float:
	return flt(rounded(flt(value), MONEY_PRECISION))


def detail_unit_rate(detail) -> float:
	explicit = flt(detail.unit_rate)
	if explicit:
		return money(explicit)
	return money(flt(detail.labor_rate) + flt(detail.material_rate) + flt(detail.equipment_rate))


def detail_amount(detail) -> float:
	return money(flt(detail.quantity) * detail_unit_rate(detail))


def detail_ld_cap_amount(detail) -> float:
	per_day = flt(detail.ld_per_day)
	cap_days = flt(detail.ld_cap_days)
	cap_amount = flt(detail.ld_cap_amount)
	if cap_amount:
		return money(cap_amount)
	if per_day and cap_days:
		return money(per_day * cap_days)
	return 0.0


def line_ld_cap_amount(line, planned_cost: float) -> float:
	per_day = flt(line.ld_per_day)
	cap_days = flt(line.ld_cap_days)
	cap_pct = flt(line.ld_cap_percent)
	candidates = []
	if per_day and cap_days:
		candidates.append(per_day * cap_days)
	if cap_pct and planned_cost:
		candidates.append(planned_cost * cap_pct / 100.0)
	return money(min(candidates)) if candidates else 0.0


def rollup_boq_line_from_details(setup, cost_code: str) -> dict | None:
	details = [d for d in (setup.boq_details or []) if (d.boq_cost_code or "").strip() == cost_code]
	if not details:
		return None
	total = money(sum(detail_amount(d) for d in details))
	return {
		"planned_cost": total,
		"labor_cost": money(sum(flt(d.quantity) * flt(d.labor_rate) for d in details)),
		"material_cost": money(sum(flt(d.quantity) * flt(d.material_rate) for d in details)),
		"equipment_cost": money(sum(flt(d.quantity) * flt(d.equipment_rate) for d in details)),
	}


def compute_ipc_amounts_with_discount(
	*,
	billable_contract_value: float,
	cumulative_completion_percent: float,
	prior_certified_completion_percent: float,
	retention_percent: float,
	advance_recovery: float,
	discount_percent: float = 0,
) -> dict[str, float]:
	out = _base_ipc_amounts(
		billable_contract_value=billable_contract_value,
		cumulative_completion_percent=cumulative_completion_percent,
		prior_certified_completion_percent=prior_certified_completion_percent,
		retention_percent=retention_percent,
		advance_recovery=advance_recovery,
	)
	period_gross = money(out["gross_amount"])
	discount_amount = money(period_gross * flt(discount_percent) / 100.0)
	out["discount_amount"] = discount_amount
	out["net_amount"] = money(flt(out["net_amount"]) - discount_amount)
	return out


def recalculate_ipc_plan(setup, contract_value: float, default_retention: float) -> list[dict]:
	rows = sorted(setup.ipc_plan or [], key=lambda r: (int(r.ipc_number or 0), str(r.ipc_date or "")))
	prior_pct = 0.0
	summary = []
	for row in rows:
		cur_pct = flt(row.cumulative_completion_percent)
		ret_pct = flt(row.retention_percent) if row.retention_percent is not None else default_retention
		out = compute_ipc_amounts_with_discount(
			billable_contract_value=contract_value,
			cumulative_completion_percent=cur_pct,
			prior_certified_completion_percent=prior_pct,
			retention_percent=ret_pct,
			advance_recovery=flt(row.advance_recovery),
			discount_percent=flt(row.discount_percent),
		)
		row.period_gross = out["gross_amount"]
		row.retention_amount = out["retention_deduction"]
		row.discount_amount = out.get("discount_amount", 0)
		row.net_amount = out["net_amount"]
		prior_pct = cur_pct
		summary.append({"ipc_number": row.ipc_number, "period_gross": row.period_gross, "net_amount": row.net_amount})
	return summary


def recalculate_setup_pricing(setup) -> dict:
	for detail in setup.boq_details or []:
		detail.amount = detail_amount(detail)

	for row in setup.boq_lines or []:
		if not row.include or row.is_group:
			continue
		rollup = rollup_boq_line_from_details(setup, row.cost_code)
		if rollup:
			row.planned_cost = rollup["planned_cost"]
			row.labor_cost = rollup["labor_cost"]
			row.material_cost = rollup["material_cost"]
			row.equipment_cost = rollup["equipment_cost"]
			qty = flt(row.quantity) or 1.0
			row.unit_cost = money(row.planned_cost / qty)
		else:
			qty = flt(row.quantity)
			uc = flt(row.unit_cost)
			row.planned_cost = money(qty * uc)
			if not flt(row.labor_cost) and not flt(row.material_cost) and not flt(row.equipment_cost):
				row.labor_cost = money(row.planned_cost * 0.4)
				row.material_cost = money(row.planned_cost * 0.5)
				row.equipment_cost = money(row.planned_cost * 0.1)

	changed = True
	while changed:
		changed = False
		for row in setup.boq_lines or []:
			if not row.include or not row.is_group:
				continue
			children = [c for c in setup.boq_lines if c.include and (c.parent_cost_code or "") == row.cost_code]
			if not children:
				continue
			new_total = money(sum(flt(c.planned_cost) for c in children))
			if money(row.planned_cost) != new_total:
				row.planned_cost = new_total
				row.labor_cost = money(sum(flt(c.labor_cost) for c in children))
				row.material_cost = money(sum(flt(c.material_cost) for c in children))
				row.equipment_cost = money(sum(flt(c.equipment_cost) for c in children))
				changed = True

	contract_value = money(
		sum(flt(r.planned_cost) for r in (setup.boq_lines or []) if r.include and not r.is_group)
	)
	setup.estimated_contract_value = contract_value
	retention_default = flt(setup.retention_percent) or 5.0
	ipc_summary = recalculate_ipc_plan(setup, contract_value, retention_default)
	return {
		"estimated_contract_value": contract_value,
		"boq_line_count": len([r for r in (setup.boq_lines or []) if r.include and not r.is_group]),
		"detail_count": len(setup.boq_details or []),
		"ipc_plan": ipc_summary,
	}
