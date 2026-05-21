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
		fields=['name', 'contract_title', 'governing_standard', 'project_segment', 'contract_currency', 'contract_value', 'revised_contract_value', 'retention_held_to_date', 'status'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [
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
	], data
