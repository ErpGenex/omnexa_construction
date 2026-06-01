# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	if not frappe.get_meta("BOQ Item").has_field("material_bom"):
		return _columns(), []

	conditions = ["b.company = %(company)s", "b.is_group = 0", "b.docstatus < 2"]
	if filters.get("branch"):
		conditions.append("b.branch = %(branch)s")
	if filters.get("project_contract"):
		conditions.append("b.project_contract = %(project_contract)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("b.branch in %(allowed_branches)s")

	rows = frappe.db.sql(
		f"""
		SELECT
			b.name AS boq_item,
			b.project_contract,
			b.item_description,
			b.actual_cost,
			m.item_code,
			m.quantity AS planned_qty,
			m.uom,
			m.amount AS planned_amount
		FROM `tabBOQ Item` b
		INNER JOIN `tabBOQ Item Material` m ON m.parent = b.name
		WHERE {' AND '.join(conditions)}
		ORDER BY b.project_contract, b.name, m.idx
		LIMIT 5000
		""",
		filters,
		as_dict=True,
	)

	data = []
	for row in rows:
		planned = flt(row.planned_amount)
		actual = flt(row.actual_cost)
		variance = actual - planned
		data.append(
			{
				**row,
				"planned_qty": flt(row.planned_qty),
				"planned_amount": planned,
				"actual_cost": actual,
				"variance": variance,
				"over_consumed": 1 if variance > 0 and planned > 0 else 0,
			}
		)
	return _columns(), data


def _columns():
	return [
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 130},
		{"label": _("BOQ Item"), "fieldname": "boq_item", "fieldtype": "Link", "options": "BOQ Item", "width": 110},
		{"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
		{"label": _("Planned Qty"), "fieldname": "planned_qty", "fieldtype": "Float", "width": 90},
		{"label": _("UOM"), "fieldname": "uom", "fieldtype": "Link", "options": "UOM", "width": 70},
		{"label": _("Planned Amount"), "fieldname": "planned_amount", "fieldtype": "Currency", "width": 110},
		{"label": _("BOQ Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "width": 110},
		{"label": _("Variance"), "fieldname": "variance", "fieldtype": "Currency", "width": 100},
		{"label": _("Over"), "fieldname": "over_consumed", "fieldtype": "Check", "width": 60},
	]
