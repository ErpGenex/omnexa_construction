# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe


def execute():
	for name in ("BOQ Item Material", "Construction RFQ Item", "Construction RFQ Supplier Quote"):
		frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))
