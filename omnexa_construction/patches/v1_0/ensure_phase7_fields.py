# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"

DOCTYPES = (
	"Construction Equipment Usage",
	"Construction CDE Document",
)


def execute():
	create_custom_fields(
		{
			"Timesheet Entry": [
				{
					"fieldname": "project_contract",
					"label": "Project Contract",
					"fieldtype": "Link",
					"options": "Project Contract",
					"insert_after": "project_template",
					"module": MODULE
	},
				{
					"fieldname": "boq_item",
					"label": "BOQ Item",
					"fieldtype": "Link",
					"options": "BOQ Item",
					"insert_after": "project_contract",
					"module": MODULE
	},
				{
					"fieldname": "cost_rate",
					"label": "Cost Rate / Hour",
					"fieldtype": "Currency",
					"insert_after": "billing_rate",
					"module": MODULE
	},
				{
					"fieldname": "cost_amount",
					"label": "Cost Amount",
					"fieldtype": "Currency",
					"read_only": 1,
					"insert_after": "cost_rate",
					"module": MODULE
	},
			],
			"Site Daily Report": [
				{
					"fieldname": "section_mobile",
					"label": "Mobile / Geo",
					"fieldtype": "Section Break",
					"insert_after": "safety_notes",
					"collapsible": 1,
					"module": MODULE
	},
				{
					"fieldname": "latitude",
					"label": "Latitude",
					"fieldtype": "Float",
					"insert_after": "section_mobile",
					"precision": "6",
					"module": MODULE
	},
				{
					"fieldname": "longitude",
					"label": "Longitude",
					"fieldtype": "Float",
					"insert_after": "latitude",
					"precision": "6",
					"module": MODULE
	},
				{
					"fieldname": "site_photo",
					"label": "Site Photo",
					"fieldtype": "Attach Image",
					"insert_after": "longitude",
					"module": MODULE
	},
			],
			"Construction Work Delay Notice": [
				{
					"fieldname": "estimated_ld_amount",
					"label": "Estimated LD Amount",
					"fieldtype": "Currency",
					"read_only": 1,
					"insert_after": "delay_days",
					"module": MODULE
	},
				{
					"fieldname": "ld_per_day",
					"label": "LD / Day (Contract)",
					"fieldtype": "Currency",
					"read_only": 1,
					"fetch_from": "project_contract.liquidated_damages_per_day",
					"insert_after": "estimated_ld_amount",
					"module": MODULE
	},
			],
			"Project WIP Snapshot": [
				{
					"fieldname": "source",
					"label": "Source",
					"fieldtype": "Select",
					"options": "Manual\nBOQ/IPC\nGL Bridge",
					"default": "Manual",
					"insert_after": "snapshot_reference",
					"module": MODULE
	},
			]},
		update=True,
	)
	for name in DOCTYPES:
		frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))
