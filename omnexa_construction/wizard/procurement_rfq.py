from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, today


def create_rfq_from_purchase_request(
	pr_name: str,
	*,
	supplier_names: list[str] | None = None,
	auto_quotes: int = 1,
	project_contract: str | None = None,
) -> str:
	"""Create Construction RFQ from Purchase Request lines."""
	if not frappe.db.exists("DocType", "Construction RFQ"):
		frappe.throw(_("Construction RFQ is not installed."), title=_("Procurement"))
	pr = frappe.get_doc("Purchase Request", pr_name)
	items = []
	for row in pr.items or []:
		rate = flt(row.get("rate")) or _item_rate(row.item_code)
		items.append(
			{
				"item_code": row.item_code,
				"quantity": flt(row.qty),
				"uom": row.get("uom") or frappe.db.get_value("Item", row.item_code, "stock_uom"),
				"boq_item": row.get("boq_item"),
				"cost_code": row.get("cost_code"),
				"estimated_rate": rate
	}
		)
	if not items:
		frappe.throw(_("Purchase Request has no items."), title=_("Procurement"))
	contract = project_contract or pr.get("project_contract")
	if not contract and frappe.db.has_column("Purchase Request", "project_contract"):
		contract = frappe.db.get_value("Purchase Request", pr.name, "project_contract")
	rfq = frappe.get_doc(
		{
			"doctype": "Construction RFQ",
			"company": pr.company,
			"branch": pr.branch,
			"project_contract": contract,
			"purchase_request": pr.name,
			"rfq_date": today(),
			"required_by": pr.required_by,
			"status": "Draft",
			"items": items
	}
	)
	if auto_quotes:
		for supplier in _pick_suppliers(pr.company, supplier_names, limit=3):
			rfq.append(
				"supplier_quotes",
				{
					"supplier": supplier,
					"quoted_amount": _estimate_quote_total(items, supplier),
					"lead_time_days": 14 + len(rfq.supplier_quotes) * 3,
					"compliance_score": 85 - len(rfq.supplier_quotes) * 5,
					"remarks": _("Auto-estimate from catalog rates — replace with vendor quote.")
	},
			)
	rfq.insert(ignore_permissions=True)
	return rfq.name


def create_rfqs_for_setup(setup, pr_names: list[str], project_contract: str | None = None) -> list[str]:
	names = []
	contract = project_contract or getattr(setup, "project_contract", None)
	for pr in pr_names:
		if frappe.db.exists("Construction RFQ", {"purchase_request": pr
	}):
			names.append(frappe.db.get_value("Construction RFQ", {"purchase_request": pr
	}, "name"))
			continue
		names.append(create_rfq_from_purchase_request(pr, project_contract=contract))
	return names


def evaluate_rfq(rfq_name: str) -> dict:
	rfq = frappe.get_doc("Construction RFQ", rfq_name)
	rfq.flags.ignore_permissions = True
	rfq.save()
	return {
		"recommended_supplier": rfq.recommended_supplier,
		"lowest_quote": rfq.lowest_quote,
		"quotes": [
			{
				"supplier": q.supplier,
				"quoted_amount": q.quoted_amount,
				"total_score": q.total_score,
				"is_recommended": q.is_recommended
	}
			for q in rfq.supplier_quotes or []
		]}


def _pick_suppliers(company: str, names: list[str] | None, limit: int = 3) -> list[str]:
	if names:
		return [n for n in names if frappe.db.exists("Supplier", n)][:limit]
	return frappe.get_all(
		"Supplier",
		filters={"company": company
	},
		pluck="name",
		limit=limit,
		order_by="modified desc",
	)


def _item_rate(item_code: str) -> float:
	meta = frappe.get_meta("Item")
	for field in ("standard_rate", "valuation_rate", "last_purchase_rate"):
		if meta.has_field(field):
			val = frappe.db.get_value("Item", item_code, field)
			if flt(val):
				return flt(val)
	return 0.0


def _estimate_quote_total(items: list[dict], supplier: str) -> float:
	total = 0.0
	factor = 0.97 + (hash(supplier) % 7) * 0.01
	for row in items:
		rate = flt(row.get("estimated_rate")) or _item_rate(row["item_code"])
		total += flt(row.get("quantity")) * rate * factor
	return total
