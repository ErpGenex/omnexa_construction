# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	if not frappe.db.exists("DocType", "Purchase Request"):
		return
	fields = {
		"Purchase Request": [
			{
				"fieldname": "project_contract",
				"label": "Project Contract",
				"fieldtype": "Link",
				"options": "Project Contract",
				"insert_after": "branch",
				"module": "Omnexa Construction",
			}
		],
		"Purchase Request Item": [
			{
				"fieldname": "boq_item",
				"label": "BOQ Item",
				"fieldtype": "Link",
				"options": "BOQ Item",
				"insert_after": "classification_code",
				"in_list_view": 1,
				"module": "Omnexa Construction",
			},
			{
				"fieldname": "cost_code",
				"label": "BOQ Cost Code",
				"fieldtype": "Data",
				"insert_after": "boq_item",
				"read_only": 1,
				"in_list_view": 1,
				"module": "Omnexa Construction",
			},
		],
		"Purchase Order": [
			{
				"fieldname": "project_contract",
				"label": "Project Contract",
				"fieldtype": "Link",
				"options": "Project Contract",
				"insert_after": "branch",
				"module": "Omnexa Construction",
			}
		],
		"Purchase Order Item": [
			{
				"fieldname": "boq_item",
				"label": "BOQ Item",
				"fieldtype": "Link",
				"options": "BOQ Item",
				"insert_after": "external_reference",
				"in_list_view": 1,
				"module": "Omnexa Construction",
			},
			{
				"fieldname": "cost_code",
				"label": "BOQ Cost Code",
				"fieldtype": "Data",
				"insert_after": "boq_item",
				"read_only": 1,
				"in_list_view": 1,
				"module": "Omnexa Construction",
			},
		],
	}
	create_custom_fields(fields, update=True)
	frappe.clear_cache(doctype="Purchase Request")
	frappe.clear_cache(doctype="Purchase Order")
