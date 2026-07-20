# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Roll up Subcontract Payment Certificate totals onto Subcontract Work Order."""

from __future__ import annotations

import frappe
from frappe.utils import flt


def subcontract_certified_total(subcontract_work_order: str | None) -> float:
	if not subcontract_work_order:
		return 0.0
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(certified_amount), 0)
		FROM `tabSubcontract Payment Certificate`
		WHERE subcontract_work_order = %s
			AND docstatus = 1
		""",
		(subcontract_work_order,),
	)
	return flt(row[0][0] if row else 0)


def subcontract_paid_total(subcontract_work_order: str | None) -> float:
	if not subcontract_work_order:
		return 0.0
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(net_payable), 0)
		FROM `tabSubcontract Payment Certificate`
		WHERE subcontract_work_order = %s
			AND docstatus = 1
			AND status IN ('Paid', 'Retention Released')
		""",
		(subcontract_work_order,),
	)
	return flt(row[0][0] if row else 0)


def refresh_subcontract_work_order_amounts(subcontract_work_order: str | None) -> None:
	if not subcontract_work_order or not frappe.db.exists("Subcontract Work Order", subcontract_work_order):
		return
	certified = subcontract_certified_total(subcontract_work_order)
	paid = subcontract_paid_total(subcontract_work_order)
	contract_value = flt(frappe.db.get_value("Subcontract Work Order", subcontract_work_order, "contract_value"))
	progress = min(100.0, certified / contract_value * 100.0) if contract_value else 0.0
	frappe.db.set_value(
		"Subcontract Work Order",
		subcontract_work_order,
		{
			"amount_certified": certified,
			"amount_paid": paid,
			"progress_percent": round(progress, 2)},
		update_modified=False,
	)
