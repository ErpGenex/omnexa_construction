# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Apply Change Order BOQ lines to BOQ items when status is Implemented."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt


def apply_change_order_to_boq(doc, method=None) -> None:
	if doc.status != "Implemented" or doc.docstatus != 1:
		return
	lines = doc.get("boq_lines") or []
	if not lines:
		return
	if doc.meta.has_field("boq_applied") and doc.get("boq_applied"):
		return
	if not doc.meta.has_field("boq_applied") and frappe.db.get_value(doc.doctype, doc.name, "boq_applied"):
		return

	for row in lines:
		if not row.boq_item:
			continue
		boq = frappe.get_doc("BOQ Item", row.boq_item)
		if boq.project_contract != doc.project_contract:
			frappe.throw(
				_("BOQ line {0} does not belong to contract {1}.").format(row.boq_item, doc.project_contract),
				title=_("Change Order"),
			)
		boq.planned_quantity = flt(boq.planned_quantity) + flt(row.quantity)
		if row.rate:
			boq.planned_rate = flt(row.rate)
		if boq.meta.has_field("planned_cost"):
			boq.planned_cost = flt(boq.planned_quantity) * flt(boq.planned_rate or row.rate)
		boq.save(ignore_permissions=True)

	frappe.msgprint(_("BOQ items updated from change order lines."), indicator="green")
	if doc.meta.has_field("boq_applied"):
		frappe.db.set_value(doc.doctype, doc.name, "boq_applied", 1, update_modified=False)


def compute_boq_line_amounts(doc, method=None) -> None:
	for row in doc.get("boq_lines") or []:
		row.amount = flt(row.quantity) * flt(row.rate)
