# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Sync global BOQ catalog (34 project types) and wizard Select options."""


def execute():
	import frappe

	from omnexa_construction.wizard.building_type_registry import building_type_select_options
	from omnexa_construction.wizard.wizard_api import import_seed_templates

	options = building_type_select_options()
	for dt in ("Construction Project Setup", "Construction BOQ Template"):
		frappe.make_property_setter(
			{
				"doctype": dt,
				"doctype_or_field": "DocField",
				"fieldname": "building_type",
				"property": "options",
				"property_type": "Text",
				"value": options,
			},
			ignore_validate=True,
		)

	import_seed_templates(sync_all=True)
