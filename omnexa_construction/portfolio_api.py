# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Construction portfolio KPIs for dashboards."""

from __future__ import annotations

import frappe
from frappe.utils import flt

from omnexa_construction.evm_metrics import evm_snapshot


@frappe.whitelist()
def get_portfolio_dashboard(company: str, branch: str | None = None) -> dict:
	filters = {"company": company, "docstatus": ["<", 2]}
	if branch:
		filters["branch"] = branch

	contracts = frappe.get_all("Project Contract", filters=filters, pluck="name")
	open_ipc = frappe.db.count(
		"IPC Certificate",
		{"company": company, "status": ["in", ["Draft", "Certified"]], "docstatus": ["<", 2]},
	)
	open_ncr = 0
	if frappe.db.exists("DocType", "Construction NCR"):
		open_ncr = frappe.db.count(
			"Construction NCR",
			{"company": company, "status": ["!=", "Closed"], "docstatus": ["<", 2]},
		)
	open_rfi = 0
	if frappe.db.exists("DocType", "Construction RFI"):
		open_rfi = frappe.db.count(
			"Construction RFI",
			{"company": company, "status": ["in", ["Open", "Overdue"]], "docstatus": ["<", 2]},
		)
	fidic_overdue = 0
	if frappe.db.exists("DocType", "Construction FIDIC Notice"):
		fidic_overdue = frappe.db.count(
			"Construction FIDIC Notice",
			{"company": company, "status": "Overdue", "docstatus": ["<", 2]},
		)
	open_disputes = 0
	if frappe.db.exists("DocType", "Construction Dispute Case"):
		dispute_filters = {"company": company, "status": ["in", ["Open", "DAB Referral"]], "docstatus": ["<", 2]}
		if branch:
			dispute_filters["branch"] = branch
		open_disputes = frappe.db.count("Construction Dispute Case", dispute_filters)
	open_early_warnings = 0
	if frappe.db.exists("DocType", "Construction Early Warning"):
		ew_filters = {"company": company, "status": ["in", ["Open", "Escalated"]], "docstatus": ["<", 2]}
		if branch:
			ew_filters["branch"] = branch
		open_early_warnings = frappe.db.count("Construction Early Warning", ew_filters)

	total_bac = 0.0
	total_ev = 0.0
	weighted_spi = 0.0
	weight = 0.0
	delayed_contracts = 0
	at_risk_contracts = 0
	on_track_contracts = 0
	total_sv_days = 0.0
	contract_rows = []
	for name in contracts[:50]:
		snap = evm_snapshot(name)
		bac = flt(snap.get("bac"))
		total_bac += bac
		total_ev += flt(snap.get("ev"))
		if bac:
			weighted_spi += flt(snap.get("spi")) * bac
			weight += bac
		sv_days = flt(snap.get("schedule_variance_days"))
		total_sv_days += sv_days
		health = snap.get("schedule_health_status") or "On Track"
		if health == "Delayed":
			delayed_contracts += 1
		elif health == "At Risk":
			at_risk_contracts += 1
		else:
			on_track_contracts += 1
		contract_rows.append(
			{
				"project_contract": name,
				"contract_title": snap.get("contract_title"),
				"bac": bac,
				"ev": flt(snap.get("ev")),
				"cpi": flt(snap.get("cpi")),
				"spi": flt(snap.get("spi")),
				"schedule_variance_days": sv_days,
				"schedule_health_status": health,
				"status": snap.get("status"),
			}
		)

	# Prioritize delayed contracts in executive dashboard table.
	health_rank = {"Delayed": 0, "At Risk": 1, "On Track": 2}
	contract_rows.sort(
		key=lambda row: (
			health_rank.get(row.get("schedule_health_status") or "On Track", 2),
			-(flt(row.get("schedule_variance_days"))),
		)
	)

	return {
		"contract_count": len(contracts),
		"total_bac": total_bac,
		"total_ev": total_ev,
		"portfolio_spi": (weighted_spi / weight) if weight else 0,
		"avg_schedule_variance_days": (total_sv_days / len(contract_rows)) if contract_rows else 0.0,
		"delayed_contracts": delayed_contracts,
		"at_risk_contracts": at_risk_contracts,
		"on_track_contracts": on_track_contracts,
		"open_ipc": open_ipc,
		"open_ncr": open_ncr,
		"open_rfi": open_rfi,
		"fidic_overdue": fidic_overdue,
		"open_disputes": open_disputes,
		"open_early_warnings": open_early_warnings,
		"contracts": contract_rows,
	}
