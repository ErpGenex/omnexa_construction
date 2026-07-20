# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	fields = {
		"BOQ Item": [
			{
				"fieldname": "material_bom",
				"label": "Material BOM",
				"fieldtype": "Table",
				"options": "BOQ Item Material",
				"insert_after": "boq_item_details",
				"module": "Omnexa Construction"
	},
		],
		"Construction Project Setup": [
			{
				"fieldname": "generated_rfq_count",
				"label": "RFQs Created",
				"fieldtype": "Int",
				"insert_after": "generated_pr_count",
				"read_only": 1,
				"module": "Omnexa Construction"
	},
			{
				"fieldname": "document_pack_file",
				"label": "Document Pack (ZIP)",
				"fieldtype": "Attach",
				"insert_after": "generated_rfq_count",
				"read_only": 1,
				"module": "Omnexa Construction"
	},
		]}
	create_custom_fields(fields, update=True)
	frappe.clear_cache(doctype="BOQ Item")
	frappe.clear_cache(doctype="Construction Project Setup")
