# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Multi-entity / multi-currency project portfolio aggregation (Phase 13.4)."""

from __future__ import annotations

import json

import frappe
from frappe.utils import flt

from omnexa_construction.evm_metrics import evm_snapshot


@frappe.whitelist()
def get_multi_entity_portfolio(companies_json: str | None = None) -> dict:
	companies = json.loads(companies_json or "[]")
	if not companies:
		companies = frappe.get_all("Company", pluck="name", limit=20)

	entities = []
	total_bac = 0.0
	total_ev = 0.0
	contract_count = 0

	for company in companies:
		contracts = frappe.get_all(
			"Project Contract",
			filters={"company": company, "docstatus": ["<", 2]},
			pluck="name",
			limit=100,
		)
		company_bac = 0.0
		company_ev = 0.0
		currencies = set()
		for name in contracts:
			snap = evm_snapshot(name)
			bac = flt(snap.get("bac"))
			company_bac += bac
			company_ev += flt(snap.get("ev"))
			cur = frappe.db.get_value("Project Contract", name, "currency")
			if cur:
				currencies.add(cur)

		contract_count += len(contracts)
		total_bac += company_bac
		total_ev += company_ev
		entities.append(
			{
				"company": company,
				"contract_count": len(contracts),
				"bac": company_bac,
				"ev": company_ev,
				"currencies": sorted(currencies),
			}
		)

	return {
		"entities": entities,
		"contract_count": contract_count,
		"total_bac": total_bac,
		"total_ev": total_ev,
		"portfolio_spi": round(total_ev / total_bac, 4) if total_bac else 0,
	}
