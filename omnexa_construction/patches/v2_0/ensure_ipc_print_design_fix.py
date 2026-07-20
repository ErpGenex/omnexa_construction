# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe

from omnexa_construction.construction_forms.print_style import sync_all_a4_print_formats


def execute():
	stats = sync_all_a4_print_formats()
	frappe.clear_cache(doctype="IPC Certificate")
	frappe.clear_cache(doctype="Print Format")
	return stats
