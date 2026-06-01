# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Site Daily Report → draft Material Issue when BOQ is linked."""

from __future__ import annotations

import frappe
from frappe import _


def maybe_create_material_issue_on_submit(doc, method=None) -> None:
	if doc.docstatus != 1 or not doc.get("boq_item"):
		return
	if doc.get("stock_entry"):
		return
	if not frappe.db.exists("DocType", "Stock Entry"):
		return
	if not frappe.get_meta("BOQ Item").has_field("material_bom"):
		return

	try:
		from omnexa_construction.inventory_hooks import create_material_issue_from_boq

		se_name = create_material_issue_from_boq(doc.boq_item)
	except frappe.ValidationError:
		return

	if doc.meta.has_field("stock_entry"):
		frappe.db.set_value(doc.doctype, doc.name, "stock_entry", se_name, update_modified=True)
	frappe.msgprint(
		_("Draft Stock Entry {0} created from BOQ materials.").format(se_name),
		indicator="blue",
		title=_("Inventory"),
	)
