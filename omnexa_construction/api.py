from __future__ import annotations

import frappe


@frappe.whitelist()
def preview_sector_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	"""SAP Wave C — sector KPI preview (omnexa_core bridge)."""
	from omnexa_core.omnexa_core.vertical_api import preview_sector_kpi as _core_preview

	return _core_preview("construction", scenario=scenario, params=params)


@frappe.whitelist()
def seed_construction_demo_from_company(
	company: str,
	branch: str | None = None,
	force: int | str | None = 0,
) -> dict:
	"""Seed five-project construction portfolio demo for training and UAT."""
	from omnexa_construction.utils.demo_seed import seed_construction_portfolio_demo

	return seed_construction_portfolio_demo(company, branch=branch, force=force)
