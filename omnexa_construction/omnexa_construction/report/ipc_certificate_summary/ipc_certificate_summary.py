# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	conditions = [
		"ipc.company = %(company)s",
		"ipc.status IN ('Certified', 'Posted')",
	]
	if filters.get("branch"):
		conditions.append("ipc.branch = %(branch)s")
	if filters.get("project_contract"):
		conditions.append("ipc.project_contract = %(project_contract)s")
	if filters.get("from_date"):
		conditions.append("ipc.ipc_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("ipc.ipc_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("ipc.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			ipc.project_contract,
			ipc.branch,
			DATE_FORMAT(ipc.ipc_date, '%%Y-%%m') AS period,
			COUNT(*) AS certificate_count,
			COALESCE(SUM(ipc.gross_amount), 0) AS total_gross,
			COALESCE(SUM(ipc.net_amount), 0) AS total_net
		FROM `tabIPC Certificate` ipc
		WHERE {' AND '.join(conditions)}
		GROUP BY ipc.project_contract, ipc.branch, DATE_FORMAT(ipc.ipc_date, '%%Y-%%m')
		ORDER BY period DESC, ipc.project_contract
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		row["total_gross"] = flt(row.total_gross)
		row["total_net"] = flt(row.total_net)

	return _columns(), data


def _columns():
	return [
		{"label": _("Project Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 160},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Period (YYYY-MM)"), "fieldname": "period", "fieldtype": "Data", "width": 110},
		{"label": _("Certificates"), "fieldname": "certificate_count", "fieldtype": "Int", "width": 100},
		{"label": _("Period gross"), "fieldname": "total_gross", "fieldtype": "Currency", "width": 130},
		{"label": _("Period net"), "fieldname": "total_net", "fieldtype": "Currency", "width": 130},
	]
