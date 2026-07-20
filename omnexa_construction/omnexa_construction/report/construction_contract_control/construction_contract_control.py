# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt

from omnexa_construction.contract_financials import (
	approved_change_order_impact,
	billable_contract_value,
	certified_ipc_net_total,
)
from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	prepare_filters,
)


def execute(filters=None):
	filters = prepare_filters(filters)
	filters_dict = get_all_filters(
		filters, "Project Contract", date_field="creation", company=True, branch=True, extra_links={}
	)
	data = frappe.get_all(
		"Project Contract",
		fields=["name", "contract_value"],
		filters=filters_dict,
		limit_page_length=5000,
	)
	for row in data:
		co = approved_change_order_impact(row.name)
		revised = billable_contract_value(row.name)
		ipc_net = certified_ipc_net_total(row.name)
		row.change_orders = co
		row.revised_value = revised
		row.ipc_net = ipc_net
		row.remaining = flt(revised) - flt(ipc_net)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Project Contract"), "fieldname": "name", "fieldtype": "Link", "options": "Project Contract", "width": 180
	},
		{"label": _("Contract Value"), "fieldname": "contract_value", "fieldtype": "Currency", "width": 140
	},
		{"label": _("Approved Change Orders"), "fieldname": "change_orders", "fieldtype": "Currency", "width": 170
	},
		{"label": _("Revised Value"), "fieldname": "revised_value", "fieldtype": "Currency", "width": 140
	},
		{"label": _("IPC Net Billed"), "fieldname": "ipc_net", "fieldtype": "Currency", "width": 140
	},
		{"label": _("Remaining"), "fieldname": "remaining", "fieldtype": "Currency", "width": 130
	},
	]
