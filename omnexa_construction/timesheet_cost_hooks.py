from __future__ import annotations

import frappe
from frappe.utils import flt

from omnexa_construction.cost_rollup import refresh_linked_boq_actual_cost


def timesheet_entry_before_save(doc, method=None) -> None:
	if not getattr(doc, "boq_item", None):
		return
	hours = flt(doc.hours)
	if not hours:
		return
	rate = flt(getattr(doc, "cost_rate", None)) or flt(getattr(doc, "billing_rate", None))
	if hasattr(doc, "cost_amount"):
		doc.cost_amount = hours * rate


def timesheet_entry_rollup(doc, method=None) -> None:
	if not getattr(doc, "boq_item", None):
		return
	refresh_linked_boq_actual_cost(doc)
