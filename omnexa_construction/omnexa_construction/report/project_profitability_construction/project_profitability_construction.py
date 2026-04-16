import frappe
from frappe import _
from frappe.utils import flt

from omnexa_construction.contract_financials import billable_contract_value


def execute(filters=None):
	contracts = frappe.get_all(
		"Project Contract",
		fields=["name", "contract_value", "company", "branch"],
		limit_page_length=1000,
	)
	for c in contracts:
		actual_cost = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(actual_cost), 0)
			FROM `tabBOQ Item`
			WHERE project_contract = %s
			""",
			(c.name,),
		)[0][0]
		c.actual_cost = flt(actual_cost)
		revised = billable_contract_value(c.name)
		c.revised_contract_value = revised
		c.profit = flt(revised) - flt(c.actual_cost)
		c.profit_percent = (flt(c.profit) / flt(revised) * 100.0) if flt(revised) else 0
	return _columns(), contracts


def _columns():
	return [
		{"label": _("Contract"), "fieldname": "name", "fieldtype": "Link", "options": "Project Contract", "width": 140},
		{"label": _("Contract Value"), "fieldname": "contract_value", "fieldtype": "Currency", "width": 130},
		{"label": _("Revised Value"), "fieldname": "revised_contract_value", "fieldtype": "Currency", "width": 130},
		{"label": _("Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Profit"), "fieldname": "profit", "fieldtype": "Currency", "width": 120},
		{"label": _("Profit %"), "fieldname": "profit_percent", "fieldtype": "Percent", "width": 110},
	]

