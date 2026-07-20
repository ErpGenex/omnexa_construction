# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe


def execute():
	if frappe.db.exists("DocType", "Construction Permit to Work"):
		return
	frappe.reload_doc("omnexa_construction", "doctype", "construction_permit_to_work")
	frappe.db.commit()
