# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe


def execute():
	ws = frappe.get_doc("Workspace", "Construction")
	shortcuts = {s.link_to for s in (ws.shortcuts or []) if s.link_to}
	add = [
		("Construction Work Approval Request", "Work Approval"),
		("Construction Material Approval Request", "Material Approval"),
		("Contractor Account Statement", "Contractor Statement"),
		("Construction Fines Statement", "Fines Statement"),
		("Construction Work Delay Notice", "Work Delay Notice"),
	]
	for link_to, label in add:
		if link_to in shortcuts or not frappe.db.exists("DocType", link_to):
			continue
		ws.append("shortcuts", {"type": "DocType", "link_to": link_to, "label": label, "color": "Blue"})
	ws.save(ignore_permissions=True)
