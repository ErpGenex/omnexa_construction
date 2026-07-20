# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe


SHORTCUTS = (
	("Regional Cost Factor", "Regional Cost"),
	("Construction Plot Unit", "Plot Inventory"),
	("Construction Residential Unit", "Unit Inventory"),
	("Construction QS Measurement Sheet", "QS Measurement"),
	("Construction FIDIC Notice", "FIDIC Notices"),
	("Construction Final Account Statement", "Final Account"),
	("Construction DLP Record", "DLP Tracking"),
	("Construction Inspection Test Plan", "ITP"),
	("BOQ Cost Overrun", "QS — Cost Overrun"),
	("Construction Earned Value", "PM — Earned Value"),
)


def execute():
	ws = frappe.get_doc("Workspace", "Construction")
	existing = {s.link_to for s in (ws.shortcuts or []) if s.link_to}
	for link_to, label in SHORTCUTS:
		if link_to in existing:
			continue
		if frappe.db.exists("Report", link_to):
			ws.append(
				"shortcuts",
				{"type": "Report", "link_to": link_to, "label": label, "color": "Grey"},
			)
		elif frappe.db.exists("DocType", link_to):
			ws.append(
				"shortcuts",
				{"type": "DocType", "link_to": link_to, "label": label, "color": "Blue"},
			)
		existing.add(link_to)
	ws.save(ignore_permissions=True)
