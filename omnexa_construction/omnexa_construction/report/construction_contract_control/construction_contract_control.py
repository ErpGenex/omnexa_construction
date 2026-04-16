import frappe
from frappe.utils import flt


def execute(filters=None):
	columns = [
		{"label": "Project Contract", "fieldname": "name", "fieldtype": "Link", "options": "Project Contract", "width": 180},
		{"label": "Contract Value", "fieldname": "contract_value", "fieldtype": "Currency", "width": 140},
		{"label": "Approved Change Orders", "fieldname": "change_orders", "fieldtype": "Currency", "width": 170},
		{"label": "Revised Value", "fieldname": "revised_value", "fieldtype": "Currency", "width": 140},
		{"label": "IPC Net Billed", "fieldname": "ipc_net", "fieldtype": "Currency", "width": 140},
		{"label": "Remaining", "fieldname": "remaining", "fieldtype": "Currency", "width": 130},
	]

	contracts = frappe.get_all(
		"Project Contract",
		fields=["name", "contract_value"],
		filters={"docstatus": ["<", 2]},
		limit_page_length=500,
	)

	data = []
	for c in contracts:
		change_orders = _sum_value(
			"Construction Change Order",
			"cost_impact",
			{"project_contract": c.name, "status": ["in", ["Approved", "Implemented"]], "docstatus": ["<", 2]},
		)
		ipc_net = _sum_value(
			"IPC Certificate",
			"net_amount",
			{
				"project_contract": c.name,
				"docstatus": ["<", 2],
				"status": ["in", ["Certified", "Posted"]],
			},
		)
		revised_value = flt(c.contract_value) + flt(change_orders)
		remaining = flt(revised_value) - flt(ipc_net)
		data.append(
			{
				"name": c.name,
				"contract_value": flt(c.contract_value),
				"change_orders": flt(change_orders),
				"revised_value": flt(revised_value),
				"ipc_net": flt(ipc_net),
				"remaining": flt(remaining),
			}
		)
	return columns, data


def _sum_value(doctype: str, fieldname: str, filters: dict):
	row = frappe.get_all(doctype, filters=filters, fields=[f"sum({fieldname}) as total"], limit_page_length=1)
	return flt((row[0].get("total") if row else 0) or 0)

