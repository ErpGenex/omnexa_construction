# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import date_diff, getdate, today
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	conditions = ["n.company = %(company)s", "n.status != 'Closed'"]
	if filters.get("branch"):
		conditions.append("n.branch = %(branch)s")
	if filters.get("project_contract"):
		conditions.append("n.project_contract = %(project_contract)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("n.branch in %(allowed_branches)s")

	rows = frappe.db.sql(
		f"""
		SELECT n.name, n.project_contract, n.ncr_date, n.severity, n.status, n.boq_item
		FROM `tabConstruction NCR` n
		WHERE {' AND '.join(conditions)}
		ORDER BY n.ncr_date asc
		LIMIT 5000
		""",
		filters,
		as_dict=True,
	)

	as_of = getdate(filters.get("as_of_date") or today())
	data = []
	for row in rows:
		age = date_diff(as_of, getdate(row.ncr_date))
		data.append({**row, "age_days": age, "overdue": 1 if age > 30 and row.status != "Closed" else 0})
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("NCR"), "fieldname": "name", "fieldtype": "Link", "options": "Construction NCR", "width": 110},
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 130},
		{"label": _("Date"), "fieldname": "ncr_date", "fieldtype": "Date", "width": 100},
		{"label": _("Age (days)"), "fieldname": "age_days", "fieldtype": "Int", "width": 90},
		{"label": _("Severity"), "fieldname": "severity", "fieldtype": "Data", "width": 80},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("BOQ Item"), "fieldname": "boq_item", "fieldtype": "Link", "options": "BOQ Item", "width": 110},
		{"label": _("Overdue (>30d)"), "fieldname": "overdue", "fieldtype": "Check", "width": 90},
	]
