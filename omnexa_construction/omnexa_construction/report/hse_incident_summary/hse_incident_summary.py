# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	conditions = ["h.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("h.branch = %(branch)s")
	if filters.get("project_contract"):
		conditions.append("h.project_contract = %(project_contract)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("h.branch in %(allowed_branches)s")

	rows = frappe.db.sql(
		f"""
		SELECT
			h.project_contract,
			h.incident_type,
			h.severity,
			h.status,
			COUNT(*) AS incident_count
		FROM `tabConstruction HSE Incident` h
		WHERE {' AND '.join(conditions)}
		GROUP BY h.project_contract, h.incident_type, h.severity, h.status
		ORDER BY h.project_contract, h.incident_type
		""",
		filters,
		as_dict=True,
	)
	for row in rows:
		row.incident_count = int(row.incident_count or 0)
	columns = _columns()
	chart = auto_chart_for_columns(rows, columns)
	return columns, rows, None, chart


def _columns():
	return [
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 140
	},
		{"label": _("Type"), "fieldname": "incident_type", "fieldtype": "Data", "width": 120
	},
		{"label": _("Severity"), "fieldname": "severity", "fieldtype": "Data", "width": 90
	},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100
	},
		{"label": _("Count"), "fieldname": "incident_count", "fieldtype": "Int", "width": 80
	},
	]
