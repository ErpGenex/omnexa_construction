# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	prepare_filters,
)


def execute(filters=None):
	filters = prepare_filters(filters)
	filters_dict = get_all_filters(
		filters,
		"BOQ Item",
		date_field="creation",
		company=True,
		branch=True,
		extra_links={"project_contract": "project_contract"},
	)
	data = frappe.get_all(
		"BOQ Item",
		fields=["name", "project_contract", "section_name", "item_description", "planned_cost", "actual_cost"],
		filters=filters_dict,
		limit_page_length=5000,
	)
	for row in data:
		planned = flt(row.planned_cost)
		actual = flt(row.actual_cost)
		overrun = actual - planned
		row.overrun = overrun
		row.overrun_percent = (overrun / planned * 100.0) if planned else 0.0
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Project Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 160},
		{"label": _("BOQ Item"), "fieldname": "name", "fieldtype": "Link", "options": "BOQ Item", "width": 130},
		{"label": _("Section"), "fieldname": "section_name", "fieldtype": "Data", "width": 120},
		{"label": _("Item"), "fieldname": "item_description", "fieldtype": "Data", "width": 200},
		{"label": _("Planned Cost"), "fieldname": "planned_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "width": 120},
		{"label": _("Overrun"), "fieldname": "overrun", "fieldtype": "Currency", "width": 110},
		{"label": _("% Over planned"), "fieldname": "overrun_percent", "fieldtype": "Percent", "width": 110},
	]
