# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""AACE-style earned value helpers for construction project contracts."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, date_diff, flt, getdate, today

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


def earned_value_from_qs(project_contract: str | None) -> float:
	"""EV from latest submitted QS measurements (measured qty × unit cost)."""
	if not project_contract or not frappe.db.exists("DocType", "Construction QS Measurement Sheet"):
		return 0.0
	total = 0.0
	sheets = frappe.get_all(
		"Construction QS Measurement Sheet",
		filters={"project_contract": project_contract, "docstatus": 1},
		pluck="name",
	)
	for sheet in sheets:
		for row in frappe.get_all(
			"Construction QS Measurement Line",
			filters={"parent": sheet},
			fields=["boq_item", "measured_qty"],
		):
			if not row.boq_item:
				continue
			uc = flt(frappe.db.get_value("BOQ Item", row.boq_item, "unit_cost"))
			total += flt(row.measured_qty) * uc
	return total


def schedule_percent_from_wbs(project_contract: str | None, as_of_date=None) -> float | None:
	"""Weighted WBS progress for BOQ lines linked to PM WBS Task."""
	if not project_contract or not frappe.db.exists("DocType", "PM WBS Task"):
		return None
	rows = frappe.db.get_all(
		"BOQ Item",
		filters={
			"project_contract": project_contract,
			"is_group": 0,
			"pm_wbs_task": ["is", "set"],
			"docstatus": ["<", 2],
		},
		fields=["planned_cost", "pm_wbs_task"],
	)
	if not rows:
		return None
	acc = 0.0
	total_w = 0.0
	for row in rows:
		w = flt(row.planned_cost) or 1.0
		pct = flt(frappe.db.get_value("PM WBS Task", row.pm_wbs_task, "progress_percent"))
		if pct <= 0:
			pct = _wbs_time_percent(row.pm_wbs_task, as_of_date)
		acc += w * pct
		total_w += w
	if not total_w:
		return None
	return max(0.0, min(100.0, acc / total_w))


def _wbs_time_percent(pm_wbs_task: str, as_of_date=None) -> float:
	task = frappe.db.get_value(
		"PM WBS Task",
		pm_wbs_task,
		["planned_start", "planned_end", "progress_percent"],
		as_dict=True,
	)
	if not task:
		return 0.0
	end = task.get("planned_end")
	return schedule_percent_planned(task.get("planned_start"), end, as_of_date) or flt(task.progress_percent)


def expected_finish_date_from_progress(planned_start, planned_completion, progress_percent: float, as_of_date=None):
	"""Forecast completion date from current progress against baseline duration."""
	start = getdate(planned_start) if planned_start else None
	end = getdate(planned_completion) if planned_completion else None
	if not start or not end or end <= start:
		return None
	progress = flt(progress_percent)
	if progress <= 0:
		return end
	if progress >= 100:
		return getdate(as_of_date or today())
	as_of = getdate(as_of_date or today())
	elapsed = max(1, date_diff(as_of, start))
	forecast_total = round(elapsed / max(progress / 100.0, 0.001))
	forecast_total = max(1, forecast_total)
	return add_days(start, forecast_total)


def schedule_health_status(spi: float, schedule_variance_days: float) -> str:
	"""Classify schedule health for early warning dashboards."""
	spi_v = flt(spi)
	sv_days = flt(schedule_variance_days)
	thresholds = _schedule_health_thresholds()
	if sv_days > thresholds["delayed_sv_days"] or spi_v < thresholds["delayed_spi"]:
		return "Delayed"
	if sv_days > thresholds["at_risk_sv_days"] or spi_v < thresholds["at_risk_spi"]:
		return "At Risk"
	return "On Track"


def _schedule_health_thresholds() -> dict:
	"""Read classification thresholds from Integration Settings with defaults."""
	defaults = {
		"delayed_spi": 0.90,
		"delayed_sv_days": 14,
		"at_risk_spi": 1.00,
		"at_risk_sv_days": 0,
	}
	if not frappe.db.exists("DocType", "Construction Integration Settings"):
		return defaults
	try:
		delayed_spi = flt(
			frappe.db.get_single_value(
				"Construction Integration Settings",
				"schedule_delayed_spi_threshold",
			)
		)
		delayed_sv_days = flt(
			frappe.db.get_single_value(
				"Construction Integration Settings",
				"schedule_delayed_sv_days_threshold",
			)
		)
		at_risk_spi = flt(
			frappe.db.get_single_value(
				"Construction Integration Settings",
				"schedule_at_risk_spi_threshold",
			)
		)
		at_risk_sv_days = flt(
			frappe.db.get_single_value(
				"Construction Integration Settings",
				"schedule_at_risk_sv_days_threshold",
			)
		)
	except Exception:
		return defaults
	return {
		"delayed_spi": delayed_spi or defaults["delayed_spi"],
		"delayed_sv_days": delayed_sv_days or defaults["delayed_sv_days"],
		"at_risk_spi": at_risk_spi or defaults["at_risk_spi"],
		"at_risk_sv_days": at_risk_sv_days or defaults["at_risk_sv_days"],
	}


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
		["contract_title", "planned_start", "planned_completion", "status", "primary_wbs_task"],
		as_dict=True,
	) or {}
	bac = billable_contract_value(project_contract)
	schedule_pct = schedule_percent_from_wbs(project_contract, as_of_date)
	schedule_source = "WBS"
	if schedule_pct is None:
		schedule_pct = schedule_percent_planned(
			contract.get("planned_start"),
			contract.get("planned_completion"),
			as_of_date,
		)
		schedule_source = "Contract Dates"
	pv = planned_value(bac, schedule_pct)
	ev_boq = earned_value_from_boq(project_contract)
	ev_qs = earned_value_from_qs(project_contract)
	ev = ev_qs if ev_qs > 0 else ev_boq
	ac = actual_cost_from_boq(project_contract)
	cpi = (ev / ac) if ac else 0.0
	spi = (ev / pv) if pv else 0.0
	cv = ev - ac
	sv = ev - pv
	eac = (bac / cpi) if cpi else bac
	etc = eac - ac
	vac = bac - eac
	tcpi = (bac - ev) / (bac - ac) if (bac - ac) else 0.0
	committed = _total_boq_committed(project_contract)
	planned_start = contract.get("planned_start")
	planned_completion = contract.get("planned_completion")
	as_of = getdate(as_of_date or today())
	forecast_finish = expected_finish_date_from_progress(
		planned_start,
		planned_completion,
		schedule_pct,
		as_of,
	)
	schedule_variance_days = 0
	if forecast_finish and planned_completion:
		schedule_variance_days = date_diff(forecast_finish, getdate(planned_completion))
	schedule_health = schedule_health_status(spi, schedule_variance_days)

	return {
		"project_contract": project_contract,
		"contract_title": contract.get("contract_title") or project_contract,
		"status": contract.get("status"),
		"bac": bac,
		"pv": pv,
		"ev": ev,
		"ev_boq": ev_boq,
		"ev_qs": ev_qs,
		"ac": ac,
		"committed_cost": committed,
		"cpi": cpi,
		"spi": spi,
		"cv": cv,
		"sv": sv,
		"eac": eac,
		"etc": etc,
		"vac": vac,
		"tcpi": tcpi,
		"schedule_percent": schedule_pct,
		"schedule_source": schedule_source,
		"as_of_date": as_of,
		"planned_start": planned_start,
		"planned_completion": planned_completion,
		"forecast_finish_date": forecast_finish,
		"schedule_variance_days": schedule_variance_days,
		"schedule_health_status": schedule_health,
	}


def _total_boq_committed(project_contract: str) -> float:
	if not frappe.get_meta("BOQ Item").has_field("committed_cost"):
		return 0.0
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(committed_cost), 0)
		FROM `tabBOQ Item`
		WHERE project_contract = %s AND is_group = 0 AND docstatus < 2
		""",
		(project_contract,),
	)
	return flt(row[0][0] if row else 0)
