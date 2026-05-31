from __future__ import annotations

import frappe
from frappe.utils import flt


def resolve_regional_factor(setup=None, company: str | None = None, branch: str | None = None) -> float:
	"""Regional multiplier for parametric BOQ (default 1.0)."""
	if setup:
		link = getattr(setup, "regional_cost_factor", None)
		if link and frappe.db.exists("Regional Cost Factor", link):
			return flt(frappe.db.get_value("Regional Cost Factor", link, "cost_factor")) or 1.0
		company = company or getattr(setup, "company", None)
		branch = branch or getattr(setup, "branch", None)
		region_code = (getattr(setup, "site_region", None) or "").strip()
		if region_code:
			factor = _lookup_factor(company, branch, region_code)
			if factor:
				return factor
	if company:
		default = frappe.db.get_value(
			"Regional Cost Factor",
			{"company": company, "is_default": 1, "disabled": 0},
			"cost_factor",
		)
		if default:
			return flt(default) or 1.0
	return 1.0


def _lookup_factor(company: str | None, branch: str | None, region_code: str) -> float:
	filters = {"region_code": region_code, "disabled": 0}
	if company:
		filters["company"] = company
	row = frappe.db.get_value(
		"Regional Cost Factor",
		filters,
		["name", "cost_factor", "branch"],
		as_dict=True,
	)
	if not row:
		return 0.0
	if branch and row.branch and row.branch != branch:
		alt = frappe.db.get_value(
			"Regional Cost Factor",
			{**filters, "branch": branch},
			"cost_factor",
		)
		return flt(alt) if alt else flt(row.cost_factor) or 1.0
	return flt(row.cost_factor) or 1.0
