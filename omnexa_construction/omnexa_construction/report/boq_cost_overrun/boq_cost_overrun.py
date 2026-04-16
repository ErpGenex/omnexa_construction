# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	project = filters.get("project_contract")

	columns = [
		{"label": _("Project Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 160},
		{"label": _("BOQ Item"), "fieldname": "name", "fieldtype": "Link", "options": "BOQ Item", "width": 130},
		{"label": _("Section"), "fieldname": "section_name", "fieldtype": "Data", "width": 120},
		{"label": _("Item"), "fieldname": "item_description", "fieldtype": "Data", "width": 200},
		{"label": _("Planned Cost"), "fieldname": "planned_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Overrun"), "fieldname": "overrun", "fieldtype": "Currency", "width": 110},
		{"label": _("% Over planned"), "fieldname": "overrun_percent", "fieldtype": "Percent", "width": 110},
	]

	flt_filters = {"is_group": 0, "docstatus": ["<", 2]}
	if project:
		flt_filters["project_contract"] = project

	rows = frappe.get_all(
		"BOQ Item",
		filters=flt_filters,
		fields=[
			"name",
			"project_contract",
			"section_name",
			"item_description",
			"planned_cost",
			"actual_cost",
		],
		order_by="project_contract asc, section_name asc",
		limit_page_length=2000,
	)

	out = []
	for r in rows:
		planned = flt(r.get("planned_cost"))
		actual = flt(r.get("actual_cost"))
		if planned <= 0 or actual <= planned:
			continue
		over = actual - planned
		r["overrun"] = over
		r["overrun_percent"] = (over / planned * 100.0) if planned else 0.0
		out.append(r)

	return columns, out
