# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""ISO 45001 HSE KPI dashboard."""

from __future__ import annotations

import frappe
from frappe.utils import flt, today


@frappe.whitelist()
def get_hse_kpi_dashboard(company: str, branch: str | None = None) -> dict:
	filters = {"company": company, "docstatus": ["<", 2]}
	if branch:
		filters["branch"] = branch

	open_ncr = frappe.db.count("Construction NCR", {**filters, "status": ["!=", "Closed"]})
	ncr_sla_breach = 0
	if frappe.db.exists("DocType", "Construction NCR") and frappe.get_meta("Construction NCR").has_field("is_sla_breached"):
		ncr_sla_breach = frappe.db.count("Construction NCR", {**filters, "is_sla_breached": 1
	})

	hse_incidents = 0
	if frappe.db.exists("DocType", "Construction HSE Incident"):
		hse_incidents = frappe.db.count("Construction HSE Incident", filters)

	ptw_open = 0
	if frappe.db.exists("DocType", "Construction Permit to Work"):
		ptw_open = frappe.db.count(
			"Construction Permit to Work",
			{**filters, "status": ["in", ["Open", "Active"]]},
		)

	osha_checks = 0
	if frappe.db.exists("DocType", "Construction OSHA Site Checklist"):
		osha_checks = frappe.db.count("Construction OSHA Site Checklist", filters)

	risk_rows = []
	if frappe.db.exists("DocType", "Construction Project Risk"):
		risk_rows = frappe.get_all(
			"Construction Project Risk",
			filters={**filters, "status": ["!=", "Closed"]},
			fields=["name", "risk_title", "risk_score", "project_contract"],
			limit=15,
			order_by="risk_score desc",
		)

	safety_kpis = []
	if frappe.db.exists("DocType", "Construction Safety KPI"):
		smeta = frappe.get_meta("Construction Safety KPI")
		sfields = ["name"]
		for f in ("kpi_name", "target_value", "actual_value", "period", "title"):
			if smeta.has_field(f):
				sfields.append(f)
		safety_kpis = frappe.get_all(
			"Construction Safety KPI",
			filters={"company": company} if smeta.has_field("company") else {
	},
			fields=sfields,
			limit=20,
		)

	ltifr = _calc_ltifr(company, branch)
	score = min(100, 100 - open_ncr * 2 - ncr_sla_breach * 5 - hse_incidents * 3 + osha_checks)

	return {
		"as_of": today(),
		"open_ncr": open_ncr,
		"ncr_sla_breached": ncr_sla_breach,
		"hse_incidents_ytd": hse_incidents,
		"open_ptw": ptw_open,
		"osha_checklists": osha_checks,
		"ltifr_estimate": ltifr,
		"iso_45001_score": score,
		"top_risks": risk_rows,
		"safety_kpis": safety_kpis
	}


def _calc_ltifr(company: str, branch: str | None) -> float:
	if not frappe.db.exists("DocType", "Construction HSE Incident"):
		return 0.0
	filters = {"company": company
	}
	if branch:
		filters["branch"] = branch
	lost_time = frappe.db.count("Construction HSE Incident", {**filters, "severity": ["in", ["Major", "Critical"]]})
	return flt(lost_time) * 200000 / 1000000.0
