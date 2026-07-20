# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns

from omnexa_construction.evm_metrics import evm_snapshot
from omnexa_core.omnexa_core.report_print.report_query_filters import get_all_filters, prepare_filters


def execute(filters=None):
	filters = prepare_filters(filters)
	as_of = filters.get("as_of_date")
	contracts = frappe.get_all(
		"Project Contract",
		filters=get_all_filters(filters, "Project Contract", company=True, branch=True),
		fields=["name"],
		limit_page_length=5000,
	)
	data = [evm_snapshot(row.name, as_of) for row in contracts]
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 140
	},
		{"label": _("Title"), "fieldname": "contract_title", "fieldtype": "Data", "width": 160
	},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90
	},
		{"label": _("BAC"), "fieldname": "bac", "fieldtype": "Currency", "width": 120
	},
		{"label": _("PV"), "fieldname": "pv", "fieldtype": "Currency", "width": 110
	},
		{"label": _("EV"), "fieldname": "ev", "fieldtype": "Currency", "width": 110
	},
		{"label": _("AC"), "fieldname": "ac", "fieldtype": "Currency", "width": 110
	},
		{"label": _("CPI"), "fieldname": "cpi", "fieldtype": "Float", "precision": 2, "width": 80
	},
		{"label": _("SPI"), "fieldname": "spi", "fieldtype": "Float", "precision": 2, "width": 80
	},
		{"label": _("CV"), "fieldname": "cv", "fieldtype": "Currency", "width": 110
	},
		{"label": _("SV"), "fieldname": "sv", "fieldtype": "Currency", "width": 110
	},
		{"label": _("EAC"), "fieldname": "eac", "fieldtype": "Currency", "width": 110
	},
		{"label": _("ETC"), "fieldname": "etc", "fieldtype": "Currency", "width": 110
	},
		{"label": _("VAC"), "fieldname": "vac", "fieldtype": "Currency", "width": 100
	},
		{"label": _("TCPI"), "fieldname": "tcpi", "fieldtype": "Float", "precision": 2, "width": 70
	},
		{"label": _("Committed"), "fieldname": "committed_cost", "fieldtype": "Currency", "width": 100
	},
		{"label": _("% Planned"), "fieldname": "schedule_percent", "fieldtype": "Percent", "width": 90
	},
		{"label": _("Planned Completion"), "fieldname": "planned_completion", "fieldtype": "Date", "width": 115
	},
		{"label": _("Forecast Finish"), "fieldname": "forecast_finish_date", "fieldtype": "Date", "width": 110
	},
		{"label": _("Schedule Variance Days"), "fieldname": "schedule_variance_days", "fieldtype": "Int", "width": 95
	},
		{"label": _("Schedule Health"), "fieldname": "schedule_health_status", "fieldtype": "Data", "width": 105
	},
		{"label": _("Schedule Source"), "fieldname": "schedule_source", "fieldtype": "Data", "width": 100
	},
	]
