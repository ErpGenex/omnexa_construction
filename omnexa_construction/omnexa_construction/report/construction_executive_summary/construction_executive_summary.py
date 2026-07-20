# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt

from omnexa_construction.contract_financials import certified_ipc_net_total
from omnexa_construction.evm_metrics import evm_snapshot
from omnexa_core.omnexa_core.report_print.report_query_filters import get_all_filters, prepare_filters


def execute(filters=None):
	filters = prepare_filters(filters)
	base = get_all_filters(filters, "Project Contract", company=True, branch=True)
	contracts = frappe.get_all("Project Contract", filters=base, pluck="name", limit_page_length=5000)
	if not contracts:
		return _columns(), []

	active = frappe.db.count("Project Contract", {**base, "status": "Active"
	})
	claim_filters = {"docstatus": ["<", 2], "status": ["in", ["Submitted", "Under Review"]]}
	if filters.get("company"):
		claim_filters["company"] = filters.company
	if filters.get("branch"):
		claim_filters["branch"] = filters.branch
	claims = frappe.db.count("Construction Claim", claim_filters)

	overrun_lines = frappe.db.sql(
		"""
		SELECT COUNT(*)
		FROM `tabBOQ Item`
		WHERE docstatus < 2
			AND is_group = 0
			AND planned_cost > 0
			AND actual_cost > planned_cost
			{company_branch}
		""".format(company_branch=_boq_scope_sql(filters)),
		_boq_scope_params(filters),
	)[0][0]

	cpi_values = []
	for name in contracts:
		snap = evm_snapshot(name, filters.get("as_of_date"))
		if snap.get("cpi"):
			cpi_values.append(flt(snap["cpi"]))
	avg_cpi = sum(cpi_values) / len(cpi_values) if cpi_values else 0
	ipc_billed = sum(certified_ipc_net_total(name) for name in contracts)

	data = [
		{
			"kpi": _("Active contracts"),
			"value": active,
			"unit": _("count")
	},
		{
			"kpi": _("Open claims"),
			"value": claims,
			"unit": _("count")
	},
		{
			"kpi": _("BOQ overrun lines"),
			"value": overrun_lines,
			"unit": _("count")
	},
		{
			"kpi": _("Portfolio avg CPI"),
			"value": round(avg_cpi, 2),
			"unit": _("index")
	},
		{
			"kpi": _("IPC net billed (certified)"),
			"value": ipc_billed,
			"unit": _("currency")
	},
	]
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart
def _boq_scope_sql(filters) -> str:
	clauses = []
	if filters.get("company"):
		clauses.append("AND company = %(company)s")
	if filters.get("branch"):
		clauses.append("AND branch = %(branch)s")
	return " ".join(clauses)


def _boq_scope_params(filters) -> dict:
	out = {}
	if filters.get("company"):
		out["company"] = filters.company
	if filters.get("branch"):
		out["branch"] = filters.branch
	return out


def _columns():
	return [
		{"label": _("KPI"), "fieldname": "kpi", "fieldtype": "Data", "width": 220
	},
		{"label": _("Value"), "fieldname": "value", "fieldtype": "Float", "width": 140
	},
		{"label": _("Unit"), "fieldname": "unit", "fieldtype": "Data", "width": 100
	},
	]
