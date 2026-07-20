# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe.utils import flt
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns

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
		fields=['project_contract', 'section_name', 'cost_code', 'item_description', 'planned_cost', 'actual_cost', 'completion_percent'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	for row in data:
		row.cost_variance = flt(row.actual_cost) - flt(row.planned_cost)

	return [
		{"label": _("Project Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 150
	},
				{"label": _("Section"), "fieldname": "section_name", "fieldtype": "Data", "width": 140
	},
		{"label": _("Cost code"), "fieldname": "cost_code", "fieldtype": "Data", "width": 100
	},
		{"label": _("Item"), "fieldname": "item_description", "fieldtype": "Data", "width": 220
	},
		{"label": _("Planned Cost"), "fieldname": "planned_cost", "fieldtype": "Currency", "width": 130
	},
		{"label": _("Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "width": 130
	},
		{"label": _("Variance"), "fieldname": "cost_variance", "fieldtype": "Currency", "width": 120
	},
		{"label": _("Completion %"), "fieldname": "completion_percent", "fieldtype": "Percent", "width": 120
	},
	], data
