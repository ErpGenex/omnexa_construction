# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe

from omnexa_construction.wizard.building_type_registry import sync_building_type_select_options
from omnexa_construction.wizard.wizard_api import import_seed_templates


def execute():
	# Sync building type Select options before importing templates to prevent ValidationError
	# when templates reference building types not yet in DocType JSON options
	sync_building_type_select_options()
	import_seed_templates()
	frappe.clear_cache(doctype="Construction BOQ Template")
	frappe.clear_cache(doctype="Construction Trade Package")
