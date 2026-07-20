# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None and not allowed:
		return _columns(), []

	data = []
	data.extend(_ipc_rows(filters, allowed))
	data.extend(_change_order_rows(filters, allowed))
	data.extend(_claim_rows(filters, allowed))
	data.extend(_eot_rows(filters, allowed))
	data.extend(_subcontract_cert_rows(filters, allowed))
	data.sort(key=lambda r: (r.get("project_contract") or "", r.get("document_type") or ""))
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart
def _scope(filters, allowed):
	conditions = ["company = %(company)s"]
	if filters.get("branch"):
		conditions.append("branch = %(branch)s")
	if filters.get("project_contract"):
		conditions.append("project_contract = %(project_contract)s")
	if allowed is not None:
		filters.allowed_branches = tuple(allowed)
		conditions.append("branch in %(allowed_branches)s")
	return conditions


def _ipc_rows(filters, allowed):
	if not frappe.db.exists("DocType", "IPC Certificate"):
		return []
	conditions = _scope(filters, allowed) + ["docstatus < 2"]
	rows = frappe.db.sql(
		f"""
		SELECT name AS document, project_contract, status, net_amount AS amount, ipc_date AS doc_date
		FROM `tabIPC Certificate`
		WHERE {' AND '.join(conditions)}
		ORDER BY modified DESC LIMIT 500
		""",
		filters,
		as_dict=True,
	)
	return [{**r, "document_type": "IPC Certificate", "amount": flt(r.amount)} for r in rows]


def _change_order_rows(filters, allowed):
	if not frappe.db.exists("DocType", "Construction Change Order"):
		return []
	conditions = _scope(filters, allowed) + ["docstatus < 2"]
	rows = frappe.db.sql(
		f"""
		SELECT name AS document, project_contract, status, cost_impact AS amount, order_date AS doc_date
		FROM `tabConstruction Change Order`
		WHERE {' AND '.join(conditions)}
		ORDER BY modified DESC LIMIT 300
		""",
		filters,
		as_dict=True,
	)
	return [{**r, "document_type": "Construction Change Order", "amount": flt(r.amount)} for r in rows]


def _claim_rows(filters, allowed):
	if not frappe.db.exists("DocType", "Construction Claim"):
		return []
	conditions = _scope(filters, allowed) + ["docstatus < 2"]
	rows = frappe.db.sql(
		f"""
		SELECT name AS document, project_contract, status, claimed_amount AS amount, claim_date AS doc_date
		FROM `tabConstruction Claim`
		WHERE {' AND '.join(conditions)}
		ORDER BY modified DESC LIMIT 300
		""",
		filters,
		as_dict=True,
	)
	return [{**r, "document_type": "Construction Claim", "amount": flt(r.amount)} for r in rows]


def _eot_rows(filters, allowed):
	if not frappe.db.exists("DocType", "Construction Extension of Time"):
		return []
	conditions = _scope(filters, allowed) + ["docstatus < 2"]
	rows = frappe.db.sql(
		f"""
		SELECT name AS document, project_contract, status, 0 AS amount, application_date AS doc_date
		FROM `tabConstruction Extension of Time`
		WHERE {' AND '.join(conditions)}
		ORDER BY modified DESC LIMIT 300
		""",
		filters,
		as_dict=True,
	)
	return [{**r, "document_type": "Construction Extension of Time", "amount": 0} for r in rows]


def _subcontract_cert_rows(filters, allowed):
	if not frappe.db.exists("DocType", "Subcontract Payment Certificate"):
		return []
	conditions = _scope(filters, allowed) + ["docstatus < 2"]
	rows = frappe.db.sql(
		f"""
		SELECT name AS document, project_contract, status, net_payable AS amount, certificate_date AS doc_date
		FROM `tabSubcontract Payment Certificate`
		WHERE {' AND '.join(conditions)}
		ORDER BY modified DESC LIMIT 300
		""",
		filters,
		as_dict=True,
	)
	return [{**r, "document_type": "Subcontract Payment Certificate", "amount": flt(r.amount)} for r in rows]


def _columns():
	return [
		{"label": _("DocType"), "fieldname": "document_type", "fieldtype": "Link", "options": "DocType", "width": 180},
		{"label": _("Document"), "fieldname": "document", "fieldtype": "Dynamic Link", "options": "document_type", "width": 140},
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 110},
		{"label": _("Date"), "fieldname": "doc_date", "fieldtype": "Date", "width": 100},
	]
