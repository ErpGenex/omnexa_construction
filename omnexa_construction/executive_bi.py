# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Executive BI payload — portfolio + forecasts + compliance (Phase 14.5)."""

from __future__ import annotations

import frappe

from omnexa_construction.evm_ml_forecast import forecast_overrun
from omnexa_construction.portfolio_api import get_portfolio_dashboard


@frappe.whitelist()
def get_executive_bi_dashboard(company: str, branch: str | None = None) -> dict:
	base = get_portfolio_dashboard(company, branch=branch)
	contracts = frappe.get_all(
		"Project Contract",
		filters={"company": company, "docstatus": ["<", 2]},
		pluck="name",
		limit=20,
	)
	forecasts = []
	high_risk = 0
	for name in contracts:
		fc = forecast_overrun(name)
		forecasts.append(fc)
		if fc.get("cost_overrun_risk") == "high" or fc.get("schedule_overrun_risk") == "high":
			high_risk += 1

	fidic_open = 0
	if frappe.db.exists("DocType", "Construction FIDIC Notice"):
		fidic_open = frappe.db.count(
			"Construction FIDIC Notice",
			{"company": company, "status": ["in", ["Open", "Overdue"]], "docstatus": ["<", 2]},
		)

	return {
		**base,
		"bi_version": "1.0",
		"forecast_sample": forecasts[:10],
		"high_risk_contracts": high_risk,
		"open_fidic_notices": fidic_open,
		"insights_url": "/app/construction-executive-dashboard"
	}
