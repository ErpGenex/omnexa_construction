from __future__ import annotations

import frappe


def _branch_display_name(branch_link: str | None) -> str:
	"""Resolve Branch link to human-readable name (Branch uses branch_name, not branch)."""
	if not branch_link:
		return ""
	if not frappe.db.exists("Branch", branch_link):
		return branch_link
	return frappe.db.get_value("Branch", branch_link, "branch_name") or branch_link


def get_setup_print_context(doc) -> dict:
	"""Shared header/meta for Construction Project Setup A4 prints."""
	company_name = frappe.db.get_value("Company", doc.company, "company_name") if doc.company else ""
	branch_name = _branch_display_name(doc.branch)
	client_name = ""
	if doc.client:
		client_name = frappe.db.get_value("Customer", doc.client, "customer_name") or doc.client
	currency = doc.contract_currency or frappe.db.get_value("Company", doc.company, "default_currency") or "EGP"
	regional_cost_factor_label = ""
	rcf = getattr(doc, "regional_cost_factor", None)
	if rcf and frappe.db.exists("Regional Cost Factor", rcf):
		regional_cost_factor_label = (
			frappe.db.get_value("Regional Cost Factor", rcf, "region_name")
			or frappe.db.get_value("Regional Cost Factor", rcf, "region_code")
			or rcf
		)
	elif rcf:
		regional_cost_factor_label = rcf
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
		"regional_cost_factor_label": regional_cost_factor_label,
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
	setup_name = getattr(doc, "wizard_setup", None)
	setup_revision = getattr(doc, "approved_setup_revision", None)
	boq_rows = frappe.get_all(
		"BOQ Item",
		filters={"project_contract": doc.name},
		fields=[
			"cost_code",
			"item_description",
			"quantity",
			"unit_of_measure",
			"unit_cost",
			"planned_cost",
			"is_group",
		],
		order_by="cost_code asc",
		limit=500,
	)
	terms = []
	if doc.get("contract_terms"):
		terms = sorted(doc.contract_terms, key=lambda r: int(r.sort_order or 0))
	elif setup_name and frappe.db.exists("Construction Project Setup", setup_name):
		setup = frappe.get_doc("Construction Project Setup", setup_name)
		terms = sorted(setup.get("contract_terms") or [], key=lambda r: int(r.sort_order or 0))
		setup_revision = setup_revision or setup.setup_revision
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
		"wizard_setup": setup_name or "",
		"setup_revision": setup_revision or 1,
		"approved_setup_attachment": getattr(doc, "approved_setup_attachment", None) or "",
		"payment_terms": doc.payment_terms or "",
		"boq_rows": boq_rows,
		"contract_terms": terms,
		"print_date": frappe.utils.today(),
	}


@frappe.whitelist()
def build_contract_print_context(contract_name: str) -> dict:
	doc = frappe.get_doc("Project Contract", contract_name)
	return get_contract_print_context(doc)
