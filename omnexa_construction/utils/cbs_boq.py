from __future__ import annotations

import frappe
from frappe.utils import flt

from omnexa_construction.omnexa_construction.doctype.construction_cbs_element.construction_cbs_element import (
	suggest_cbs_for_cost_code,
)


def apply_cbs_to_boq_line(doc) -> None:
	if doc.get("cbs_element") or not doc.get("cost_code"):
		return
	suggested = suggest_cbs_for_cost_code(doc.cost_code)
	if suggested:
		doc.cbs_element = suggested


@frappe.whitelist()
def cbs_boq_summary(project_contract: str) -> list[dict]:
	"""Aggregate BOQ planned/actual by CBS element for a contract."""
	if not project_contract:
		return []

	lines = frappe.get_all(
		"BOQ Item",
		filters={"project_contract": project_contract, "docstatus": ["!=", 2], "is_group": 0
	},
		fields=["cbs_element", "planned_cost", "actual_cost", "cost_code"],
		limit_page_length=10000,
	)
	totals: dict[str, dict] = {}
	for row in lines:
		cbs = row.get("cbs_element") or suggest_cbs_for_cost_code(row.get("cost_code")) or "Unmapped"
		bucket = totals.setdefault(
			cbs,
			{"cbs_element": cbs, "planned_cost": 0.0, "actual_cost": 0.0, "line_count": 0
	},
		)
		bucket["planned_cost"] += flt(row.get("planned_cost"))
		bucket["actual_cost"] += flt(row.get("actual_cost"))
		bucket["line_count"] += 1

	out = list(totals.values())
	out.sort(key=lambda r: str(r["cbs_element"]))
	return out
