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
	filters_dict = get_all_filters(filters, "BOQ Item", date_field="creation", company=True, branch=True, extra_links={'project_contract': 'project_contract'})
	data = frappe.get_all(
		"BOQ Item",
		fields=['name', 'project_contract', 'section_name', 'item_description', 'planned_cost', 'actual_cost'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [
		{"label": _("Project Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 160},
		{"label": _("BOQ Item"), "fieldname": "name", "fieldtype": "Link", "options": "BOQ Item", "width": 130},
		{"label": _("Section"), "fieldname": "section_name", "fieldtype": "Data", "width": 120},
		{"label": _("Item"), "fieldname": "item_description", "fieldtype": "Data", "width": 200},
		{"label": _("Planned Cost"), "fieldname": "planned_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Overrun"), "fieldname": "overrun", "fieldtype": "Currency", "width": 110},
		{"label": _("% Over planned"), "fieldname": "overrun_percent", "fieldtype": "Percent", "width": 110},
	], data
