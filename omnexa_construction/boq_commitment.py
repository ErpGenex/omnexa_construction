# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Roll up purchase commitments to BOQ items."""

from __future__ import annotations

import frappe
from frappe.utils import flt


def committed_amount_for_boq(boq_item: str) -> float:
	if not boq_item or not frappe.db.exists("DocType", "Purchase Order Item"):
		return 0.0
	meta = frappe.get_meta("Purchase Order Item")
	if not meta.has_field("boq_item"):
		return 0.0
	amount_field = "amount" if meta.has_field("amount") else "base_amount"
	row = frappe.db.sql(
		f"""
		SELECT COALESCE(SUM(poi.`{amount_field}`), 0)
		FROM `tabPurchase Order Item` poi
		INNER JOIN `tabPurchase Order` po ON po.name = poi.parent
		WHERE poi.boq_item = %s
			AND po.docstatus = 1
			AND poi.docstatus < 2
		""",
		(boq_item,),
	)
	return flt(row[0][0] if row else 0)


def refresh_boq_commitment(boq_item: str) -> None:
	if not boq_item:
		return
	meta = frappe.get_meta("BOQ Item")
	if not meta.has_field("committed_cost"):
		return
	committed = committed_amount_for_boq(boq_item)
	frappe.db.set_value("BOQ Item", boq_item, "committed_cost", committed, update_modified=False)
	if meta.has_field("po_committed"):
		frappe.db.set_value("BOQ Item", boq_item, "po_committed", committed, update_modified=False)


def refresh_contract_boq_commitments(project_contract: str) -> None:
	if not project_contract:
		return
	for name in frappe.get_all(
		"BOQ Item",
		filters={"project_contract": project_contract, "is_group": 0, "docstatus": ["<", 2]},
		pluck="name",
	):
		refresh_boq_commitment(name)


def on_purchase_order_update(doc, method=None) -> None:
	seen = set()
	for row in doc.get("items") or []:
		boq = getattr(row, "boq_item", None)
		if boq and boq not in seen:
			seen.add(boq)
			refresh_boq_commitment(boq)
	if doc.get("project_contract"):
		frappe.enqueue(
			"omnexa_construction.boq_commitment.refresh_contract_boq_commitments",
			project_contract=doc.project_contract,
			queue="short",
		)
