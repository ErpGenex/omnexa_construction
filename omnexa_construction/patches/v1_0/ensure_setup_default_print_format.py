# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe

from omnexa_construction.construction_forms.print_style import sync_all_a4_print_formats

DEFAULT_FORMAT = "Construction Setup — Summary"
DOCTYPE = "Construction Project Setup"


def execute():
	if not frappe.db.exists("DocType", DOCTYPE):
		return
	sync_all_a4_print_formats()
	if frappe.db.exists("Print Format", DEFAULT_FORMAT):
		frappe.db.set_value("DocType", DOCTYPE, "default_print_format", DEFAULT_FORMAT, update_modified=False)
	frappe.clear_cache(doctype="DocType")
