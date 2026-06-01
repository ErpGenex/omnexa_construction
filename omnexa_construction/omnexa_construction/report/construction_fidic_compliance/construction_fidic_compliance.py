# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	conditions = ["n.company = %(company)s", "n.docstatus < 2"]
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

	meta = frappe.get_meta("Construction FIDIC Notice")
	fields = [
		"n.name",
		"n.project_contract",
		"n.notice_type",
		"n.notice_date",
		"n.response_due_date",
		"n.status",
	]
	if meta.has_field("notice_due_date"):
		fields.append("n.notice_due_date")
	if meta.has_field("is_time_barred"):
		fields.append("n.is_time_barred")

	data = frappe.db.sql(
		f"""
		SELECT {', '.join(fields)}
		FROM `tabConstruction FIDIC Notice` n
		WHERE {' AND '.join(conditions)}
		ORDER BY n.notice_date DESC
		LIMIT 500
		""",
		filters,
		as_dict=True,
	)
	return _columns(meta), data


def _columns(meta=None):
	cols = [
		{"label": _("Notice"), "fieldname": "name", "fieldtype": "Link", "options": "Construction FIDIC Notice", "width": 140},
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 160},
		{"label": _("Type"), "fieldname": "notice_type", "fieldtype": "Data", "width": 120},
		{"label": _("Notice Date"), "fieldname": "notice_date", "fieldtype": "Date", "width": 100},
		{"label": _("Due Date"), "fieldname": "response_due_date", "fieldtype": "Date", "width": 100},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
	]
	if meta and meta.has_field("is_time_barred"):
		cols.append({"label": _("Time Barred"), "fieldname": "is_time_barred", "fieldtype": "Check", "width": 80})
	return cols
