# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	fields = {
		"BOQ Item": [
			{
				"fieldname": "planned_start_date",
				"label": "Planned Start",
				"fieldtype": "Date",
				"insert_after": "completion_percent",
				"module": "Omnexa Construction",
			},
			{
				"fieldname": "planned_completion_date",
				"label": "Planned Completion",
				"fieldtype": "Date",
				"insert_after": "planned_start_date",
				"module": "Omnexa Construction",
			},
			{
				"fieldname": "construction_phase",
				"label": "Construction Phase",
				"fieldtype": "Data",
				"insert_after": "planned_completion_date",
				"module": "Omnexa Construction",
			},
			{
				"fieldname": "liquidated_damages_per_day",
				"label": "LD per day",
				"fieldtype": "Currency",
				"insert_after": "construction_phase",
				"module": "Omnexa Construction",
			},
			{
				"fieldname": "liquidated_damages_cap_amount",
				"label": "LD cap amount",
				"fieldtype": "Currency",
				"insert_after": "liquidated_damages_per_day",
				"module": "Omnexa Construction",
			},
			{
				"fieldname": "boq_item_details",
				"label": "BOQ Item Details",
				"fieldtype": "Table",
				"options": "BOQ Item Detail",
				"insert_after": "liquidated_damages_cap_amount",
				"module": "Omnexa Construction",
			},
		],
		"IPC Certificate": [
			{
				"fieldname": "discount_percent",
				"label": "Discount %",
				"fieldtype": "Percent",
				"default": "0",
				"insert_after": "advance_recovery",
				"module": "Omnexa Construction",
			},
			{
				"fieldname": "discount_amount",
				"label": "Discount Amount",
				"fieldtype": "Currency",
				"read_only": 1,
				"insert_after": "discount_percent",
				"module": "Omnexa Construction",
			},
		],
	}
	create_custom_fields(fields, update=True)
	frappe.clear_cache(doctype="BOQ Item")
	frappe.clear_cache(doctype="IPC Certificate")
