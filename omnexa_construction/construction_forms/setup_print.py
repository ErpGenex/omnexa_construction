from __future__ import annotations

import frappe


def get_setup_print_context(doc) -> dict:
	"""Shared header/meta for Construction Project Setup A4 prints."""
	company_name = frappe.db.get_value("Company", doc.company, "company_name") if doc.company else ""
	branch_name = frappe.db.get_value("Branch", doc.branch, "branch") if doc.branch else ""
	client_name = ""
	if doc.client:
		client_name = frappe.db.get_value("Customer", doc.client, "customer_name") or doc.client
	currency = doc.contract_currency or frappe.db.get_value("Company", doc.company, "default_currency") or "EGP"
	return {
		"company_name": company_name or doc.company or "",
		"branch_name": branch_name or doc.branch or "",
		"client_name": client_name,
		"contract_title": doc.contract_title or doc.name,
		"building_type": doc.building_type or "",
		"boq_template": doc.boq_template or "",
		"governing_standard": doc.governing_standard or "",
		"currency": currency,
		"estimated_contract_value": doc.estimated_contract_value,
		"planned_start": doc.planned_start,
		"planned_completion": doc.planned_completion,
		"retention_percent": doc.retention_percent,
		"advance_payment_percent": doc.advance_payment_percent,
		"print_date": frappe.utils.today(),
	}


@frappe.whitelist()
def build_setup_print_context(setup_name: str) -> dict:
	doc = frappe.get_doc("Construction Project Setup", setup_name)
	return get_setup_print_context(doc)


def get_contract_print_context(doc) -> dict:
	company_name = frappe.db.get_value("Company", doc.company, "company_name") if doc.company else ""
	client_name = ""
	if doc.client:
		client_name = frappe.db.get_value("Customer", doc.client, "customer_name") or doc.client
	return {
		"company_name": company_name or doc.company or "",
		"client_name": client_name,
		"contract_title": doc.contract_title or doc.name,
		"contract_number": doc.name,
		"building_type": doc.building_type or "",
		"contract_value": doc.contract_value,
		"currency": doc.contract_currency or "EGP",
		"planned_start": doc.planned_start,
		"planned_completion": doc.planned_completion,
		"governing_standard": doc.governing_standard or "",
		"site_location": doc.site_location or "",
		"print_date": frappe.utils.today(),
	}


@frappe.whitelist()
def build_contract_print_context(contract_name: str) -> dict:
	doc = frappe.get_doc("Project Contract", contract_name)
	return get_contract_print_context(doc)
