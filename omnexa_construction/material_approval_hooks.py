# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Material Approval → Purchase Material Request when approved."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt


def maybe_create_material_request(doc, method=None) -> None:
	if doc.status != "Approved":
		return
	if doc.get("material_request"):
		return
	if not frappe.db.exists("DocType", "Material Request"):
		return
	if not doc.materials:
		return

	mr = frappe.new_doc("Material Request")
	mr.material_request_type = "Purchase"
	mr.company = doc.company
	if mr.meta.has_field("branch"):
		mr.branch = doc.branch
	mr.transaction_date = doc.request_date
	if mr.meta.has_field("project_contract"):
		mr.project_contract = doc.project_contract
	mr.schedule_date = doc.request_date

	for row in doc.materials:
		item_code = _resolve_item_code(row)
		if not item_code:
			continue
		line = {
			"item_code": item_code,
			"qty": flt(row.suggested_quantity) or 1,
			"uom": row.uom or frappe.db.get_value("Item", item_code, "stock_uom"),
			"description": row.material_name,
		}
		if frappe.get_meta("Material Request Item").has_field("project_contract"):
			line["project_contract"] = doc.project_contract
		mr.append("items", line)

	if not mr.items:
		return

	mr.insert(ignore_permissions=True)
	updates = {"material_request": mr.name}
	if doc.meta.has_field("status"):
		pass
	frappe.db.set_value(doc.doctype, doc.name, updates, update_modified=True)
	frappe.msgprint(
		_("Material Request {0} created from approval.").format(mr.name),
		indicator="green",
		title=_("Procurement"),
	)


def _resolve_item_code(row) -> str | None:
	if row.get("item_code"):
		return row.item_code
	name = (row.material_name or "").strip()
	if not name:
		return None
	item = frappe.db.get_value("Item", {"item_name": name, "disabled": 0}, "name")
	if item:
		return item
	return frappe.db.get_value("Item", {"item_code": name, "disabled": 0}, "name")
