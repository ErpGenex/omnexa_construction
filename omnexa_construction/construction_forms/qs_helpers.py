from __future__ import annotations

import frappe
from frappe.utils import flt


@frappe.whitelist()
def load_boq_measurement_lines(project_contract: str) -> list[dict]:
	rows = frappe.get_all(
		"BOQ Item",
		filters={"project_contract": project_contract, "is_group": 0, "docstatus": ["<", 2]},
		fields=["name", "cost_code", "item_description", "unit_of_measure", "quantity"],
		order_by="cost_code asc",
		limit_page_length=500,
	)
	return [
		{
			"boq_item": r.name,
			"cost_code": r.cost_code,
			"description": r.item_description,
			"unit_of_measure": r.unit_of_measure,
			"previous_qty": flt(r.quantity),
			"measured_qty": flt(r.quantity),
		}
		for r in rows
	]
