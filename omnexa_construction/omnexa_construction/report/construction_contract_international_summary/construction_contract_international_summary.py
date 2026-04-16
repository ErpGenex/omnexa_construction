# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.utils import flt

from omnexa_construction.contract_financials import (
	billable_contract_value,
	retention_held_from_certified_ipc,
)


def execute(filters=None):
	filters = filters or {}
	project = filters.get("project_contract")

	columns = [
		{"label": _("Contract"), "fieldname": "name", "fieldtype": "Link", "options": "Project Contract", "width": 140},
		{"label": _("Title"), "fieldname": "contract_title", "fieldtype": "Data", "width": 160},
		{"label": _("Governing form"), "fieldname": "governing_standard", "fieldtype": "Data", "width": 200},
		{"label": _("Segment"), "fieldname": "project_segment", "fieldtype": "Data", "width": 120},
		{"label": _("Currency"), "fieldname": "contract_currency", "fieldtype": "Link", "options": "Currency", "width": 80},
		{"label": _("Contract value"), "fieldname": "contract_value", "fieldtype": "Currency", "width": 120},
		{"label": _("Revised value"), "fieldname": "revised_contract_value", "fieldtype": "Currency", "width": 120},
		{"label": _("Retention held"), "fieldname": "retention_held_to_date", "fieldtype": "Currency", "width": 110},
		{"label": _("IPC net (cert.)"), "fieldname": "ipc_net_certified", "fieldtype": "Currency", "width": 120},
		{"label": _("EOT approved"), "fieldname": "eot_approved_count", "fieldtype": "Int", "width": 90},
		{"label": _("Claims active"), "fieldname": "claims_active_count", "fieldtype": "Int", "width": 90},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
	]

	flt = {"docstatus": ["<", 2]}
	if project:
		flt["name"] = project

	rows = frappe.get_all(
		"Project Contract",
		filters=flt,
		fields=[
			"name",
			"contract_title",
			"governing_standard",
			"project_segment",
			"contract_currency",
			"contract_value",
			"revised_contract_value",
			"retention_held_to_date",
			"status",
		],
		order_by="name asc",
		limit_page_length=500,
	)

	for r in rows:
		r["revised_contract_value"] = billable_contract_value(r["name"])
		r["retention_held_to_date"] = retention_held_from_certified_ipc(r["name"])
		r["ipc_net_certified"] = _sum_ipc_net(r["name"])
		r["eot_approved_count"] = frappe.db.count(
			"Construction Extension of Time",
			{"project_contract": r["name"], "status": "Approved", "docstatus": ["<", 2]},
		)
		r["claims_active_count"] = frappe.db.count(
			"Construction Claim",
			{
				"project_contract": r["name"],
				"status": ["in", ["Submitted", "Under Review"]],
				"docstatus": ["<", 2],
			},
		)

	return columns, rows


def _sum_ipc_net(project_contract: str) -> float:
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(net_amount), 0)
		FROM `tabIPC Certificate`
		WHERE project_contract = %s
			AND status IN ('Certified', 'Posted')
			AND docstatus < 2
		""",
		(project_contract,),
	)
	return flt(row[0][0] if row else 0)
