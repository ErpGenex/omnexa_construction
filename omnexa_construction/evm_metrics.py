# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""AACE-style earned value helpers for construction project contracts."""

from __future__ import annotations

import frappe
from frappe.utils import flt, getdate, today

from omnexa_construction.contract_financials import billable_contract_value


def planned_value(bac: float, schedule_percent: float) -> float:
	return flt(bac) * flt(schedule_percent) / 100.0


def schedule_percent_planned(
	planned_start,
	planned_completion,
	as_of_date=None,
) -> float:
	start = getdate(planned_start) if planned_start else None
	end = getdate(planned_completion) if planned_completion else None
	if not start or not end or end <= start:
		return 0.0
	as_of = getdate(as_of_date or today())
	if as_of <= start:
		return 0.0
	if as_of >= end:
		return 100.0
	total_days = (end - start).days
	if not total_days:
		return 0.0
	return max(0.0, min(100.0, (as_of - start).days / total_days * 100.0))


def earned_value_from_boq(project_contract: str | None) -> float:
	if not project_contract:
		return 0.0
	rows = frappe.db.get_all(
		"BOQ Item",
		filters={
			"project_contract": project_contract,
			"is_group": 0,
			"docstatus": ["<", 2],
		},
		fields=["planned_cost", "completion_percent"],
	)
	return sum(flt(row.get("planned_cost")) * flt(row.get("completion_percent")) / 100.0 for row in rows)


def actual_cost_from_boq(project_contract: str | None) -> float:
	if not project_contract:
		return 0.0
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(actual_cost), 0)
		FROM `tabBOQ Item`
		WHERE project_contract = %s
			AND is_group = 0
			AND docstatus < 2
		""",
		(project_contract,),
	)
	return flt(row[0][0] if row else 0)


def evm_snapshot(project_contract: str, as_of_date=None) -> dict:
	contract = frappe.db.get_value(
		"Project Contract",
		project_contract,
		["contract_title", "planned_start", "planned_completion", "status"],
		as_dict=True,
	) or {}
	bac = billable_contract_value(project_contract)
	schedule_pct = schedule_percent_planned(
		contract.get("planned_start"),
		contract.get("planned_completion"),
		as_of_date,
	)
	pv = planned_value(bac, schedule_pct)
	ev = earned_value_from_boq(project_contract)
	ac = actual_cost_from_boq(project_contract)
	cpi = (ev / ac) if ac else 0.0
	spi = (ev / pv) if pv else 0.0
	cv = ev - ac
	sv = ev - pv
	eac = (bac / cpi) if cpi else bac
	etc = eac - ac
	return {
		"project_contract": project_contract,
		"contract_title": contract.get("contract_title") or project_contract,
		"status": contract.get("status"),
		"bac": bac,
		"pv": pv,
		"ev": ev,
		"ac": ac,
		"cpi": cpi,
		"spi": spi,
		"cv": cv,
		"sv": sv,
		"eac": eac,
		"etc": etc,
		"schedule_percent": schedule_pct,
	}
