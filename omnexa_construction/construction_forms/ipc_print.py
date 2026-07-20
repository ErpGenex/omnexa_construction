from __future__ import annotations

import frappe
from frappe.utils import flt


def currency_display_label(currency: str | None) -> str:
	"""Short Arabic-friendly currency label for print headers."""
	if not currency:
		return "EGP"
	labels = {
		"EGP": "ج.م",
		"SAR": "ر.س",
		"AED": "د.إ",
		"USD": "USD",
		"EUR": "EUR",
		"GBP": "GBP"
	}
	if currency in labels:
		return labels[currency]
	return frappe.db.get_value("Currency", currency, "symbol", cache=True) or currency


def format_ipc_amount(amount) -> str:
	"""Numeric amount only — currency is shown in column headers."""
	return frappe.utils.fmt_money(amount, currency=None)


def get_ipc_print_context(doc) -> dict:
	"""Build BOQ rows and totals for Arabic IPC print format."""
	currency = frappe.db.get_value("Project Contract", doc.project_contract, "contract_currency") or "EGP"
	company_name = frappe.db.get_value("Company", doc.company, "company_name") or doc.company
	contract = frappe.get_doc("Project Contract", doc.project_contract)
	client_name = ""
	if contract.client:
		client_name = frappe.db.get_value("Customer", contract.client, "customer_name") or contract.client

	contractor_name = company_name
	if frappe.db.exists("DocType", "Subcontract Work Order"):
		sub = frappe.db.get_value(
			"Subcontract Work Order",
			{"project_contract": doc.project_contract, "docstatus": ["<", 2]},
			"subcontractor",
			order_by="creation asc",
		)
		if sub:
			contractor_name = frappe.db.get_value("Supplier", sub, "supplier_name") or sub

	period_map = {row.boq_item: flt(row.period_value) for row in (doc.boq_lines or []) if row.boq_item}
	boq_items = frappe.get_all(
		"BOQ Item",
		filters={"project_contract": doc.project_contract, "is_group": 0, "docstatus": ["!=", 2]},
		fields=["name", "item_description", "planned_cost", "completion_percent", "cost_code"],
		order_by="cost_code asc, name asc",
	)

	rows = []
	total_contract = total_prior = total_current = total_cumulative = 0.0
	for i, item in enumerate(boq_items, start=1):
		contract_val = flt(item.planned_cost)
		pct = flt(item.completion_percent)
		cumulative = contract_val * pct / 100.0
		current = period_map.get(item.name, 0.0)
		if not current and doc.boq_lines:
			current = 0.0
		elif not doc.boq_lines and contract_val:
			current = contract_val * (flt(doc.boq_completion_percent) / 100.0) / max(len(boq_items), 1)
		prior = max(cumulative - current, 0.0)
		exec_pct = (cumulative / contract_val * 100.0) if contract_val else 0.0
		rows.append(
			{
				"idx": i,
				"description": item.item_description,
				"contract_value": contract_val,
				"prior_cumulative": prior,
				"current_ipc": current,
				"cumulative_to_date": cumulative,
				"completion_percent": exec_pct
	}
		)
		total_contract += contract_val
		total_prior += prior
		total_current += current
		total_cumulative += cumulative

	penalty = flt(doc.get("penalty_deduction"))
	discount = flt(doc.get("discount_amount"))
	other_ded = flt(doc.get("other_deductions"))
	net_due = flt(doc.net_amount)
	cumulative_billed = flt(doc.cumulative_value_billed) or total_cumulative
	completion_pct = flt(doc.boq_completion_percent)
	if not completion_pct and total_contract:
		completion_pct = total_cumulative / total_contract * 100.0

	cert_number = doc.employer_certificate_ref or doc.certificate_reference or doc.name

	return {
		"currency": currency,
		"currency_label": currency_display_label(currency),
		"company_name": company_name,
		"client_name": client_name,
		"contract_title": contract.contract_title,
		"contract_number": contract.name,
		"contractor_name": contractor_name,
		"site_location": contract.site_location or "",
		"boq_rows": rows,
		"totals": {
			"contract_value": total_contract or flt(doc.billable_contract_value),
			"prior_cumulative": total_prior or flt(doc.prior_cumulative_billed),
			"current_ipc": total_current or flt(doc.gross_amount),
			"cumulative_to_date": total_cumulative or cumulative_billed,
			"completion_percent": round(completion_pct, 2)},
		"summary": {
			"cumulative_billed": cumulative_billed,
			"completion_percent": round(completion_pct, 2),
			"current_ipc_gross": flt(doc.gross_amount),
			"retention": flt(doc.retention_deduction),
			"advance_recovery": flt(doc.advance_recovery),
			"penalty": penalty,
			"discount": discount,
			"other": other_ded,
			"net_due": net_due
	},
		"certificate_number": cert_number,
		"ipc_date": doc.ipc_date,
		"period_from": doc.period_from,
		"period_to": doc.period_to
	}


@frappe.whitelist()
def build_ipc_print_context(ipc_name: str) -> dict:
	doc = frappe.get_doc("IPC Certificate", ipc_name)
	return get_ipc_print_context(doc)
