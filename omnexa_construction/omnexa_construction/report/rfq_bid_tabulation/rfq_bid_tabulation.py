# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt, getdate, today
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	conditions = ["r.company = %(company)s", "r.docstatus < 2"]
	if filters.get("branch"):
		conditions.append("r.branch = %(branch)s")
	if filters.get("project_contract"):
		conditions.append("r.project_contract = %(project_contract)s")
	if filters.get("rfq"):
		conditions.append("r.name = %(rfq)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("r.branch in %(allowed_branches)s")

	rfqs = frappe.db.sql(
		f"""
		SELECT r.name, r.project_contract, r.status, r.estimated_total, r.lowest_quote, r.recommended_supplier
		FROM `tabConstruction RFQ` r
		WHERE {' AND '.join(conditions)}
		ORDER BY r.modified DESC
		LIMIT 200
		""",
		filters,
		as_dict=True,
	)

	data = []
	for rfq in rfqs:
		quotes = frappe.get_all(
			"Construction RFQ Supplier Quote",
			filters={"parent": rfq.name
	},
			fields=["supplier", "quoted_amount", "lead_time_days", "total_score", "is_recommended"],
			order_by="quoted_amount asc",
		)
		for q in quotes:
			data.append(
				{
					"rfq": rfq.name,
					"project_contract": rfq.project_contract,
					"rfq_status": rfq.status,
					"estimated_total": flt(rfq.estimated_total),
					"supplier": q.supplier,
					"quoted_amount": flt(q.quoted_amount),
					"lead_time_days": q.lead_time_days,
					"total_score": flt(q.total_score),
					"is_recommended": q.is_recommended,
					"variance_to_estimate": flt(q.quoted_amount) - flt(rfq.estimated_total),
					"is_lowest": 1 if quotes and q.quoted_amount == quotes[0].quoted_amount else 0
	}
			)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("RFQ"), "fieldname": "rfq", "fieldtype": "Link", "options": "Construction RFQ", "width": 120
	},
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 130
	},
		{"label": _("RFQ Status"), "fieldname": "rfq_status", "fieldtype": "Data", "width": 90
	},
		{"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 120
	},
		{"label": _("Quoted Amount"), "fieldname": "quoted_amount", "fieldtype": "Currency", "width": 110
	},
		{"label": _("Estimate"), "fieldname": "estimated_total", "fieldtype": "Currency", "width": 100
	},
		{"label": _("Variance"), "fieldname": "variance_to_estimate", "fieldtype": "Currency", "width": 100
	},
		{"label": _("Lead Time"), "fieldname": "lead_time_days", "fieldtype": "Int", "width": 80
	},
		{"label": _("Score"), "fieldname": "total_score", "fieldtype": "Percent", "width": 70
	},
		{"label": _("Lowest"), "fieldname": "is_lowest", "fieldtype": "Check", "width": 60
	},
		{"label": _("Recommended"), "fieldname": "is_recommended", "fieldtype": "Check", "width": 90
	},
	]
