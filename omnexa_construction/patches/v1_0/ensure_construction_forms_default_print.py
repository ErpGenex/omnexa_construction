# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe

DEFAULT_PRINTS = (
	("Construction Material Approval Request", "Construction Material Approval — AR"),
	("Construction Work Approval Request", "Construction Work Approval — AR"),
	("Contractor Account Statement", "Contractor Account Statement — AR"),
	("Construction Fines Statement", "Construction Fines Statement — AR"),
	("Construction Work Delay Notice", "Construction Work Delay — AR"),
	("IPC Certificate", "IPC Certificate — AR (مستخلص مقاولات)"),
)


def execute():
	for doctype, print_format in DEFAULT_PRINTS:
		if not frappe.db.exists("DocType", doctype):
			continue
		if not frappe.db.exists("Print Format", print_format):
			continue
		frappe.db.set_value("DocType", doctype, "default_print_format", print_format, update_modified=False)
	frappe.db.commit()
