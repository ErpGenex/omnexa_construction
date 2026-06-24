# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

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

	has_committed = frappe.get_meta("BOQ Item").has_field("committed_cost")
	committed_sel = "b.committed_cost" if has_committed else "0"

	data = frappe.db.sql(
		f"""
		SELECT
			b.name AS boq_item,
			b.project_contract,
			b.section_name,
			b.item_description,
			b.planned_cost,
			{committed_sel} AS committed_cost,
			b.actual_cost,
			(b.planned_cost - b.actual_cost - {committed_sel}) AS remaining_budget
		FROM `tabBOQ Item` b
		WHERE {' AND '.join(conditions)}
		ORDER BY b.project_contract, b.section_name
		LIMIT 5000
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		row.planned_cost = flt(row.planned_cost)
		row.committed_cost = flt(row.committed_cost)
		row.actual_cost = flt(row.actual_cost)
		row.remaining_budget = flt(row.remaining_budget)
	return _columns(has_committed), data


def _columns(has_committed=True):
	cols = [
		{"label": _("BOQ Item"), "fieldname": "boq_item", "fieldtype": "Link", "options": "BOQ Item", "width": 120},
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 130},
		{"label": _("Section"), "fieldname": "section_name", "fieldtype": "Data", "width": 100},
		{"label": _("Description"), "fieldname": "item_description", "fieldtype": "Data", "width": 180},
		{"label": _("Planned"), "fieldname": "planned_cost", "fieldtype": "Currency", "width": 110},
	]
	if has_committed:
		cols.append({"label": _("Committed (PO)"), "fieldname": "committed_cost", "fieldtype": "Currency", "width": 110})
	cols.extend(
		[
			{"label": _("Actual"), "fieldname": "actual_cost", "fieldtype": "Currency", "width": 110},
			{"label": _("Remaining"), "fieldname": "remaining_budget", "fieldtype": "Currency", "width": 110},
		]
	)
	return cols
