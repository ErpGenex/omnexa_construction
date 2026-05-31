# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe

from omnexa_construction.construction_forms.print_style import sync_all_a4_print_formats


def execute():
	stats = sync_all_a4_print_formats()
	frappe.db.commit()
	frappe.logger("omnexa_construction").info("A4 print formats synced: %s", stats)
