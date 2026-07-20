# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe


def execute():
	if not frappe.db.exists("Page", "construction-project-wizard"):
		return
	frappe.reload_doc("omnexa_construction", "page", "construction_project_wizard")
	page = frappe.get_doc("Page", "construction-project-wizard")
	existing = {row.role for row in (page.roles or [])}
	for role in ("System Manager", "Project Manager", "Desk User"):
		if role not in existing:
			page.append("roles", {"role": role
	})
	page.save(ignore_permissions=True)
	frappe.clear_cache(doctype="Page")
