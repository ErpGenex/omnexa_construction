# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Purchase Request / Order validation and BOQ cost-code hydration."""

from __future__ import annotations

import frappe
from frappe import _


def validate_purchase_request_boq_links(doc, method=None) -> None:
	_hydrate_header_and_lines(doc, "Purchase Request Item")


def validate_purchase_order_boq_links(doc, method=None) -> None:
	_hydrate_header_and_lines(doc, "Purchase Order Item")


def _hydrate_header_and_lines(doc, child_table: str) -> None:
	if not doc.get("items"):
		return
	child_meta = frappe.get_meta(child_table)
	for row in doc.items:
		if not getattr(row, "boq_item", None):
			continue
		boq = frappe.db.get_value(
			"BOQ Item",
			row.boq_item,
			["project_contract", "cost_code", "item_description"],
			as_dict=True,
		)
		if not boq:
			frappe.throw(_("BOQ Item {0} was not found.").format(row.boq_item), title=_("Procurement"))
		if doc.meta.has_field("project_contract"):
			if doc.project_contract and doc.project_contract != boq.project_contract:
				frappe.throw(
					_("Line BOQ Item must belong to the same Project Contract as the document header."),
					title=_("Procurement"),
				)
			doc.project_contract = doc.project_contract or boq.project_contract
		if child_meta.has_field("cost_code"):
			row.cost_code = row.cost_code or boq.cost_code
		if child_table == "Purchase Request Item" and child_meta.has_field("purpose") and not row.purpose:
			row.purpose = boq.item_description
