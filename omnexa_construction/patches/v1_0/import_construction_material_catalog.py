# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe

from omnexa_construction.wizard.catalog_import import import_material_catalog


def execute():
	for company in frappe.get_all("Company", pluck="name"):
		import_material_catalog(company)
