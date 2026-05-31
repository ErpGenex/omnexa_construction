# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe


CHILD_DOCTYPES = (
	"Construction Work Approval Line",
	"Construction Material Approval Line",
	"Construction Fines Statement Line",
	"Contractor Account Statement Line",
)


def execute():
	for name in CHILD_DOCTYPES:
		frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))
