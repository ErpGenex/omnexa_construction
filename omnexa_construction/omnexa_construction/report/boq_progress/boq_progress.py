import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	data = frappe.get_all(
		"BOQ Item",
		fields=[
			"project_contract",
			"section_name",
			"cost_code",
			"item_description",
			"planned_cost",
			"actual_cost",
			"completion_percent",
		],
		limit_page_length=1000,
	)
	for row in data:
		row.cost_variance = flt(row.actual_cost) - flt(row.planned_cost)
	return _columns(), data


def _columns():
	return [
		{"label": _("Project Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 150},
				{"label": _("Section"), "fieldname": "section_name", "fieldtype": "Data", "width": 140},
		{"label": _("Cost code"), "fieldname": "cost_code", "fieldtype": "Data", "width": 100},
		{"label": _("Item"), "fieldname": "item_description", "fieldtype": "Data", "width": 220},
		{"label": _("Planned Cost"), "fieldname": "planned_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Actual Cost"), "fieldname": "actual_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Variance"), "fieldname": "cost_variance", "fieldtype": "Currency", "width": 120},
		{"label": _("Completion %"), "fieldname": "completion_percent", "fieldtype": "Percent", "width": 120},
	]

