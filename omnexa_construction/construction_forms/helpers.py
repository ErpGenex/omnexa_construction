from __future__ import annotations

import frappe


def hydrate_contract_party_fields(doc) -> None:
	if not doc.project_contract:
		return
	contract = frappe.get_doc("Project Contract", doc.project_contract)
	doc.company = doc.company or contract.company
	doc.branch = doc.branch or contract.branch
	if not doc.project_name:
		doc.project_name = contract.contract_title
	if not doc.project_number:
		doc.project_number = contract.name
	if not doc.contract_number:
		doc.contract_number = contract.name
	if not doc.site_location:
		doc.site_location = contract.site_location
	if not doc.contractor_name and doc.company:
		doc.contractor_name = frappe.db.get_value("Company", doc.company, "company_name")
