# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Optional draft Sales Invoice from IPC when feature flag is enabled."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate

from omnexa_core.omnexa_core.feature_flags import get_feature_flags, is_feature_enabled


def maybe_create_draft_sales_invoice(doc, method=None) -> None:
	if not is_feature_enabled("construction_ipc_draft_sales_invoice", default=False):
		return
	if doc.status != "Posted" or doc.sales_invoice or flt(doc.net_amount) <= 0:
		return
	if frappe.db.exists("Sales Invoice", {"remarks": ["like", f"%IPC:{doc.name}%"]}):
		return
	si_name = create_draft_sales_invoice(doc.name)
	if si_name:
		doc.db_set("sales_invoice", si_name, update_modified=False)


@frappe.whitelist()
def create_draft_sales_invoice(ipc_name: str) -> str | None:
	if not is_feature_enabled("construction_ipc_draft_sales_invoice", default=False):
		frappe.throw(
			_("Enable feature flag construction_ipc_draft_sales_invoice to create Sales Invoices from IPC."),
			title=_("IPC billing"),
		)
	if not frappe.db.exists("DocType", "Sales Invoice"):
		frappe.throw(_("Sales Invoice is not available on this site."), title=_("IPC billing"))

	ipc = frappe.get_doc("IPC Certificate", ipc_name)
	if ipc.sales_invoice:
		return ipc.sales_invoice
	if flt(ipc.net_amount) <= 0:
		frappe.throw(_("IPC net amount must be greater than zero."), title=_("IPC billing"))

	contract = frappe.db.get_value(
		"Project Contract",
		ipc.project_contract,
		["client", "contract_currency", "contract_title"],
		as_dict=True,
	)
	if not contract or not contract.client:
		frappe.throw(_("Project Contract client is required for billing."), title=_("IPC billing"))

	item = _resolve_ipc_billing_item(ipc.company)
	income_account = _resolve_income_account(item, ipc.company)
	currency = contract.contract_currency or frappe.db.get_value("Company", ipc.company, "default_currency")

	si = frappe.new_doc("Sales Invoice")
	si.company = ipc.company
	si.branch = ipc.branch
	si.customer = contract.client
	si.posting_date = ipc.ipc_date or getdate()
	si.due_date = add_days(si.posting_date, 30)
	si.currency = currency
	si.conversion_rate = 1
	si.remarks = f"IPC:{ipc.name} · {contract.contract_title or ipc.project_contract}"
	si.append(
		"items",
		{
			"item": item,
			"item_code": frappe.db.get_value("Item", item, "item_code"),
			"description": _("IPC {0} net billing").format(ipc.name),
			"qty": 1,
			"rate": flt(ipc.net_amount),
			"income_account": income_account,
		},
	)
	si.insert(ignore_permissions=True)
	ipc.db_set("sales_invoice", si.name, update_modified=False)
	frappe.msgprint(
		_("Draft Sales Invoice {0} created from IPC.").format(frappe.bold(si.name)),
		indicator="green",
		title=_("IPC billing"),
	)
	return si.name


def _resolve_ipc_billing_item(company: str) -> str:
	flags = get_feature_flags()
	configured = flags.get("construction_ipc_billing_item")
	if configured and frappe.db.exists("Item", configured):
		return configured

	item = frappe.db.get_value(
		"Item",
		{"company": company, "disabled": 0, "is_stock_item": 0},
		"name",
		order_by="creation asc",
	)
	if item:
		return item
	frappe.throw(
		_(
			"Set omnexa_feature_flags.construction_ipc_billing_item or create a non-stock Item for company {0}."
		).format(company),
		title=_("IPC billing"),
	)


def _resolve_income_account(item: str, company: str) -> str:
	account = frappe.db.get_value("Item", item, "income_account")
	if account:
		return account
	company_income = frappe.db.get_value("Company", company, "default_income_account")
	if company_income:
		return company_income
	frappe.throw(_("Income account is required for IPC billing item."), title=_("IPC billing"))
