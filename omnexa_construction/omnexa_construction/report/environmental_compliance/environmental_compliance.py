# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _
from frappe.utils import date_diff, getdate, today
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	as_of = getdate(filters.get("as_of_date") or today())
	data = []
	data.extend(_aspect_rows(filters, as_of))
	data.extend(_waste_rows(filters, as_of))
	return _columns(), data


def _aspect_rows(filters, as_of):
	if not frappe.db.exists("DocType", "Construction Environmental Aspect"):
		return []
	conditions = ["a.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("a.branch = %(branch)s")
	if filters.get("project_contract"):
		conditions.append("a.project_contract = %(project_contract)s")
	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return []
		filters.allowed_branches = tuple(allowed)
		conditions.append("a.branch in %(allowed_branches)s")

	rows = frappe.db.sql(
		f"""
		SELECT a.name AS record, a.project_contract, a.activity AS aspect, a.aspect_type AS impact_level,
			a.status, a.aspect_date AS review_date
		FROM `tabConstruction Environmental Aspect` a
		WHERE {' AND '.join(conditions)}
		ORDER BY a.project_contract
		LIMIT 2000
		""",
		filters,
		as_dict=True,
	)
	out = []
	for row in rows:
		out.append(
			{
				**row,
				"record_type": "Environmental Aspect",
				"overdue_review": 0,
			}
		)
	return out


def _waste_rows(filters, as_of):
	if not frappe.db.exists("DocType", "Construction Waste Log"):
		return []
	conditions = ["w.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("w.branch = %(branch)s")
	if filters.get("project_contract"):
		conditions.append("w.project_contract = %(project_contract)s")
	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return []
		filters.allowed_branches = tuple(allowed)
		conditions.append("w.branch in %(allowed_branches)s")

	rows = frappe.db.sql(
		f"""
		SELECT w.name AS record, w.project_contract, w.waste_type AS aspect, w.quantity, w.log_date AS review_date, w.disposal_method AS status
		FROM `tabConstruction Waste Log` w
		WHERE {' AND '.join(conditions)}
		ORDER BY w.log_date DESC
		LIMIT 2000
		""",
		filters,
		as_dict=True,
	)
	return [{**r, "record_type": "Waste Log", "impact_level": "", "overdue_review": 0} for r in rows]


def _columns():
	return [
		{"label": _("Type"), "fieldname": "record_type", "fieldtype": "Data", "width": 140},
		{"label": _("Record"), "fieldname": "record", "fieldtype": "Data", "width": 120},
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 130},
		{"label": _("Aspect / Waste"), "fieldname": "aspect", "fieldtype": "Data", "width": 140},
		{"label": _("Impact"), "fieldname": "impact_level", "fieldtype": "Data", "width": 90},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Review / Log Date"), "fieldname": "review_date", "fieldtype": "Date", "width": 110},
		{"label": _("Overdue"), "fieldname": "overdue_review", "fieldtype": "Check", "width": 70},
	]
