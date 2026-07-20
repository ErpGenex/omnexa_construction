# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe

from omnexa_construction.wizard.wizard_api import import_seed_templates


def execute():
	import_seed_templates()
	frappe.clear_cache(doctype="Construction BOQ Template")
	frappe.clear_cache(doctype="Construction Trade Package")
