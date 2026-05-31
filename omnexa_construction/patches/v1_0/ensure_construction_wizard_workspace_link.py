# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe


def execute():
	if not frappe.db.exists("Workspace", "Construction"):
		return
	ws = frappe.get_doc("Workspace", "Construction")
	for row in ws.shortcuts or []:
		if row.link_to == "construction-project-wizard":
			return
	ws.append(
		"shortcuts",
		{
			"label": "New Project (Wizard)",
			"type": "Page",
			"link_to": "construction-project-wizard",
			"color": "Green",
		},
	)
	ws.save(ignore_permissions=True)
