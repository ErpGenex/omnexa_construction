# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe


def execute():
	ws = frappe.get_doc("Workspace", "Construction")
	existing = {s.link_to for s in (ws.shortcuts or []) if s.link_to}
	add = [
		("Construction CDE Document", "CDE Documents"),
		("Construction Equipment Usage", "Equipment Usage"),
	]
	for link_to, label in add:
		if link_to in existing or not frappe.db.exists("DocType", link_to):
			continue
		ws.append("shortcuts", {"type": "DocType", "link_to": link_to, "label": label, "color": "Green"})
	ws.save(ignore_permissions=True)
