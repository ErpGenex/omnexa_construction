# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""GCC — ZATCA readiness check on IPC submit."""

from __future__ import annotations

import frappe
from frappe import _


def validate_ipc_zatca_readiness(doc, method=None) -> None:
	if doc.doctype != "IPC Certificate":
		return
	branch = frappe.db.get_value("Project Contract", doc.project_contract, "branch")
	if not branch:
		return
	meta = frappe.get_meta("Branch")
	if not meta.has_field("enable_zatca_e_invoicing"):
		return
	if not frappe.db.get_value("Branch", branch, "enable_zatca_e_invoicing"):
		return
	if doc.docstatus == 1 and not doc.get("sales_invoice"):
		frappe.msgprint(
			_("ZATCA is enabled on branch — link or generate e-invoice for this IPC when posting."),
			indicator="orange",
			title=_("GCC / ZATCA"),
		)
