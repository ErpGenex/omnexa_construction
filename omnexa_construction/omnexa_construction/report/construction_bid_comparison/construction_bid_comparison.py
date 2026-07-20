# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_construction.bid_analysis import compare_bids_in_package


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))
	if not filters.get("bid_package"):
		frappe.throw(_("Bid Package is required."), title=_("Filters"))

	rows = compare_bids_in_package(filters.bid_package, company=filters.company)
	return _columns(), rows


def _columns():
	return [
		{"label": _("Bid"), "fieldname": "name", "fieldtype": "Link", "options": "Construction Bid Estimate", "width": 130
	},
		{"label": _("Title"), "fieldname": "estimate_title", "fieldtype": "Data", "width": 180
	},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 120
	},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90
	},
		{"label": _("Contract Value"), "fieldname": "estimated_contract_value", "fieldtype": "Currency", "width": 120
	},
		{"label": _("Cost"), "fieldname": "estimated_cost", "fieldtype": "Currency", "width": 110
	},
		{"label": _("Margin %"), "fieldname": "margin_percent", "fieldtype": "Percent", "width": 90
	},
		{"label": _("Variance to Lowest"), "fieldname": "variance_to_lowest", "fieldtype": "Currency", "width": 120
	},
		{"label": _("Lowest"), "fieldname": "is_lowest", "fieldtype": "Check", "width": 70
	},
	]
