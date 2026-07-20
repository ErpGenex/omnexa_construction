# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Construction RFQ award → Purchase Order."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, getdate


@frappe.whitelist()
def create_purchase_order_from_rfq(rfq_name: str, supplier: str | None = None) -> str:
	if not frappe.db.exists("DocType", "Purchase Order"):
		frappe.throw(_("Purchase Order is not available."), title=_("Procurement"))

	rfq = frappe.get_doc("Construction RFQ", rfq_name)
	supplier = supplier or rfq.awarded_supplier or rfq.recommended_supplier
	if not supplier:
		frappe.throw(_("Select or award a supplier first."), title=_("Procurement"))

	quote = _winning_quote(rfq, supplier)
	po = frappe.new_doc("Purchase Order")
	po.supplier = supplier
	po.company = rfq.company
	if po.meta.has_field("branch"):
		po.branch = rfq.branch
	if po.meta.has_field("project_contract"):
		po.project_contract = rfq.project_contract
	po.transaction_date = getdate()
	if rfq.required_by and po.meta.has_field("schedule_date"):
		po.schedule_date = rfq.required_by

	for row in rfq.items or []:
		rate = flt(row.estimated_rate)
		if quote and rfq.estimated_total:
			share = flt(row.amount) / flt(rfq.estimated_total) if rfq.estimated_total else 0
			rate = (flt(quote.quoted_amount) * share / flt(row.quantity)) if row.quantity else rate
		item_row = {
			"item_code": row.item_code,
			"qty": flt(row.quantity),
			"rate": rate,
			"uom": row.uom,
		}
		if frappe.get_meta("Purchase Order Item").has_field("boq_item"):
			item_row["boq_item"] = row.boq_item
		if frappe.get_meta("Purchase Order Item").has_field("cost_code"):
			item_row["cost_code"] = row.cost_code
		po.append("items", item_row)

	if not po.items:
		frappe.throw(_("RFQ has no lines to order."), title=_("Procurement"))

	po.insert(ignore_permissions=True)
	updates = {"status": "Awarded", "awarded_supplier": supplier}
	if rfq.meta.has_field("purchase_order"):
		updates["purchase_order"] = po.name
	frappe.db.set_value("Construction RFQ", rfq.name, updates, update_modified=True)
	frappe.msgprint(_("Purchase Order {0} created.").format(po.name), indicator="green")
	return po.name


def _winning_quote(rfq, supplier: str):
	for row in rfq.supplier_quotes or []:
		if row.supplier == supplier:
			return row
	return None
