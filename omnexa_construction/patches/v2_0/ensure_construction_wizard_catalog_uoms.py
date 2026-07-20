# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe

from omnexa_construction.wizard.catalog_import import ensure_construction_uoms, import_material_catalog


def execute():
	ensure_construction_uoms()
	for company in frappe.get_all("Company", pluck="name"):
		import_material_catalog(company, limit=80)
