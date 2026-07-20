# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""EU GDPR — CDE access log report data."""

from __future__ import annotations

import frappe


@frappe.whitelist()
def get_gdpr_access_report(project_contract: str | None = None) -> list[dict]:
	if not frappe.db.exists("DocType", "Construction CDE Access Log"):
		return []
	filters = {}
	if project_contract:
		filters["project_contract"] = project_contract
	return frappe.get_all(
		"Construction CDE Access Log",
		filters=filters,
		fields=["name", "cde_document", "user", "action", "creation", "project_contract"],
		order_by="creation desc",
		limit=500,
	)
