# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import get_datetime, now_datetime
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	conditions = ["p.company = %(company)s", "p.docstatus < 2"]
	if filters.get("branch"):
		conditions.append("p.branch = %(branch)s")
	if filters.get("project_contract"):
		conditions.append("p.project_contract = %(project_contract)s")
	if filters.get("status"):
		conditions.append("p.status = %(status)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("p.branch in %(allowed_branches)s")

	now = now_datetime()
	data = frappe.db.sql(
		f"""
		SELECT
			p.name,
			p.project_contract,
			p.permit_date,
			p.work_location,
			p.valid_from,
			p.valid_to,
			p.status,
			p.issued_by,
			p.approved_by
		FROM `tabConstruction Permit to Work` p
		WHERE {' AND '.join(conditions)}
		ORDER BY p.valid_from DESC
		LIMIT 5000
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		valid_to = get_datetime(row.valid_to) if row.valid_to else None
		row.is_expired = 1 if valid_to and valid_to < now and row.status == "Active" else 0
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("PTW"), "fieldname": "name", "fieldtype": "Link", "options": "Construction Permit to Work", "width": 110},
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 130},
		{"label": _("Location"), "fieldname": "work_location", "fieldtype": "Data", "width": 120},
		{"label": _("Valid From"), "fieldname": "valid_from", "fieldtype": "Datetime", "width": 140},
		{"label": _("Valid To"), "fieldname": "valid_to", "fieldtype": "Datetime", "width": 140},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
		{"label": _("Expired"), "fieldname": "is_expired", "fieldtype": "Check", "width": 70},
		{"label": _("Issued By"), "fieldname": "issued_by", "fieldtype": "Link", "options": "User", "width": 110},
	]
