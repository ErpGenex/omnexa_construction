# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""BOQ material BOM → stock consumption helpers."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def create_material_issue_from_boq(boq_item: str, qty: float | None = None) -> str:
	"""Create draft Stock Entry (Material Issue) from BOQ Item Material lines."""
	if not frappe.db.exists("DocType", "Stock Entry"):
		frappe.throw(_("Stock module is not installed."), title=_("Inventory"))
	boq = frappe.get_doc("BOQ Item", boq_item)
	if boq.is_group:
		frappe.throw(_("Cannot issue stock against a group BOQ line."), title=_("Inventory"))
	materials = boq.get("material_bom") or []
	if not materials:
		frappe.throw(_("No materials on this BOQ item."), title=_("Inventory"))

	se = frappe.new_doc("Stock Entry")
	se.stock_entry_type = "Material Issue"
	se.company = boq.company
	if se.meta.has_field("project_contract"):
		se.project_contract = boq.project_contract
	for row in materials:
		issue_qty = flt(qty) if qty else flt(row.quantity)
		if issue_qty <= 0:
			continue
		se.append(
			"items",
			{
				"item_code": row.item_code,
				"qty": issue_qty,
				"uom": row.uom,
				"s_warehouse": _default_issue_warehouse(boq.company)
	},
		)
	if not se.items:
		frappe.throw(_("No issue quantity to process."), title=_("Inventory"))
	se.insert(ignore_permissions=True)
	return se.name


def _default_issue_warehouse(company: str) -> str | None:
	for wh in frappe.get_all("Warehouse", filters={"company": company, "is_group": 0
	}, pluck="name", limit=1):
		return wh
	return None
