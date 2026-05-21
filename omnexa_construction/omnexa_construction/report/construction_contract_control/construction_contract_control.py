# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	filters = prepare_filters(filters)
	filters_dict = get_all_filters(filters, "Project Contract", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Project Contract",
		fields=['name', 'contract_value'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [
		{"label": "Project Contract", "fieldname": "name", "fieldtype": "Link", "options": "Project Contract", "width": 180},
		{"label": "Contract Value", "fieldname": "contract_value", "fieldtype": "Currency", "width": 140},
		{"label": "Approved Change Orders", "fieldname": "change_orders", "fieldtype": "Currency", "width": 170},
		{"label": "Revised Value", "fieldname": "revised_value", "fieldtype": "Currency", "width": 140},
		{"label": "IPC Net Billed", "fieldname": "ipc_net", "fieldtype": "Currency", "width": 140},
		{"label": "Remaining", "fieldname": "remaining", "fieldtype": "Currency", "width": 130},
	], data
