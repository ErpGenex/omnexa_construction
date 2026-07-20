# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"

DOCTYPES = (
	"Regional Cost Factor",
	"Construction Plot Unit",
	"Construction Residential Unit",
	"Construction QS Measurement Sheet",
	"Construction QS Measurement Line",
	"Construction FIDIC Notice",
	"Construction Final Account Statement",
	"Construction Final Account Line",
	"Construction DLP Record",
	"Construction Inspection Test Plan",
	"Construction Inspection Test Plan Line",
)


def execute():
	create_custom_fields(
		{
			"Construction Project Setup": [
				{
					"fieldname": "regional_cost_factor",
					"label": "Regional Cost Factor",
					"fieldtype": "Link",
					"options": "Regional Cost Factor",
					"insert_after": "quality_tier",
					"module": MODULE
	},
				{
					"fieldname": "site_region",
					"label": "Site Region Code",
					"fieldtype": "Data",
					"insert_after": "regional_cost_factor",
					"module": MODULE
	},
			],
			"Project Contract": [
				{
					"fieldname": "section_residential",
					"label": "Residential Inventory",
					"fieldtype": "Section Break",
					"insert_after": "wizard_setup",
					"collapsible": 1,
					"module": MODULE
	},
				{
					"fieldname": "unit_count_planned",
					"label": "Planned Units",
					"fieldtype": "Int",
					"insert_after": "section_residential",
					"read_only": 1,
					"module": MODULE
	},
			]},
		update=True,
	)
	for name in DOCTYPES:
		frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))
