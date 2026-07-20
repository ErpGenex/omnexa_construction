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

	conditions = ["s.company = %(company)s", "s.docstatus < 2"]
	if filters.get("branch"):
		conditions.append("s.branch = %(branch)s")
	if filters.get("project_contract"):
		conditions.append("s.project_contract = %(project_contract)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("s.branch in %(allowed_branches)s")

	as_of = getdate(filters.get("as_of_date") or today())
	rows = frappe.db.sql(
		f"""
		SELECT
			s.project_contract,
			s.status,
			COUNT(*) AS snag_count,
			MIN(s.snag_date) AS oldest_snag_date
		FROM `tabConstruction Snagging Item` s
		WHERE {' AND '.join(conditions)}
		GROUP BY s.project_contract, s.status
		ORDER BY s.project_contract, s.status
		""",
		filters,
		as_dict=True,
	)
	for row in rows:
		row.snag_count = int(row.snag_count or 0)
		if row.oldest_snag_date and row.status != "Closed":
			row.max_age_days = date_diff(as_of, getdate(row.oldest_snag_date))
		else:
			row.max_age_days = 0
	columns = _columns()
	chart = auto_chart_for_columns(rows, columns)
	return columns, rows, None, chart


def _columns():
	return [
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 140},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Count"), "fieldname": "snag_count", "fieldtype": "Int", "width": 80},
		{"label": _("Oldest Snag"), "fieldname": "oldest_snag_date", "fieldtype": "Date", "width": 110},
		{"label": _("Max Age (days)"), "fieldname": "max_age_days", "fieldtype": "Int", "width": 100},
	]
