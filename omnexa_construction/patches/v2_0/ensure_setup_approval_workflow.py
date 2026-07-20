# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Approval workflow fields, contract terms child tables, and print formats."""


def execute():
	import frappe

	from omnexa_construction.construction_forms.print_style import sync_all_a4_print_formats

	frappe.reload_doc("Omnexa Construction", "doctype", "construction_project_setup_contract_term")
	frappe.reload_doc("Omnexa Construction", "doctype", "project_contract_term")
	frappe.reload_doc("Omnexa Construction", "doctype", "construction_project_setup")
	frappe.reload_doc("Omnexa Construction", "doctype", "project_contract")

	if frappe.db.has_column("Construction Project Setup", "approval_status"):
		frappe.db.sql(
			"""
			UPDATE `tabConstruction Project Setup`
			SET approval_status = IFNULL(NULLIF(approval_status, ''), 'Open'),
			    setup_revision = IFNULL(setup_revision, 1)
			"""
		)

	sync_all_a4_print_formats()
