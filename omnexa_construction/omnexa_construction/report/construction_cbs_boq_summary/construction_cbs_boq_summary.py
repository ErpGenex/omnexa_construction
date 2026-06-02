# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_construction.utils.cbs_boq import cbs_boq_summary


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("project_contract"):
		frappe.throw(_("Project Contract is required."), title=_("Filters"))

	from frappe.utils import flt

	rows = cbs_boq_summary(filters.project_contract)
	for row in rows:
		row["variance"] = flt(row.get("actual_cost")) - flt(row.get("planned_cost"))
	return _columns(), rows


def _columns():
	return [
		{"label": _("CBS Element"), "fieldname": "cbs_element", "fieldtype": "Data", "width": 160},
		{"label": _("BOQ Lines"), "fieldname": "line_count", "fieldtype": "Int", "width": 90},
		{"label": _("Planned Cost"), "fieldname": "planned_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "width": 120},
		{
			"label": _("Variance"),
			"fieldname": "variance",
			"fieldtype": "Currency",
			"width": 110,
		},
	]
