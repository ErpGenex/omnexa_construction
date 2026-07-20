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

	conditions = ["i.company = %(company)s", "i.docstatus < 2"]
	if filters.get("branch"):
		conditions.append("i.branch = %(branch)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("i.branch in %(allowed_branches)s")

	if not frappe.get_meta("IPC Certificate").has_field("exchange_rate"):
		return _columns(), []

	rows = frappe.db.sql(
		f"""
		SELECT
			i.name,
			i.project_contract,
			i.ipc_date,
			i.net_amount,
			c.contract_currency AS currency,
			COALESCE(i.exchange_rate, 1) AS exchange_rate,
			i.net_amount * COALESCE(i.exchange_rate, 1) AS base_amount
		FROM `tabIPC Certificate` i
		INNER JOIN `tabProject Contract` c ON c.name = i.project_contract
		INNER JOIN `tabCompany` co ON co.name = i.company
		WHERE {' AND '.join(conditions)}
			AND c.contract_currency IS NOT NULL
			AND c.contract_currency != co.default_currency
		ORDER BY i.ipc_date DESC
		LIMIT 2000
		""",
		filters,
		as_dict=True,
	)
	for row in rows:
		row.net_amount = flt(row.net_amount)
		row.exchange_rate = flt(row.exchange_rate)
		row.base_amount = flt(row.base_amount)
	columns = _columns()
	chart = auto_chart_for_columns(rows, columns)
	return columns, rows, None, chart


def _columns():
	return [
		{"label": _("IPC"), "fieldname": "name", "fieldtype": "Link", "options": "IPC Certificate", "width": 120
	},
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 130
	},
		{"label": _("Date"), "fieldname": "ipc_date", "fieldtype": "Date", "width": 100
	},
		{"label": _("Currency"), "fieldname": "currency", "fieldtype": "Data", "width": 70
	},
		{"label": _("Net (FCY)"), "fieldname": "net_amount", "fieldtype": "Currency", "width": 110
	},
		{"label": _("Rate"), "fieldname": "exchange_rate", "fieldtype": "Float", "width": 80
	},
		{"label": _("Base Amount"), "fieldname": "base_amount", "fieldtype": "Currency", "width": 110
	},
	]
