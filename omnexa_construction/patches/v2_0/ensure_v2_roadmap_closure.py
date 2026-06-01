# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

from pathlib import Path

import frappe

MODULE = "Omnexa Construction"

REPORTS = ("construction_evm_dashboard",)

EN_PRINTS = (
	("Construction Material Approval — EN", "Construction Material Approval Request", "material_approval_en.html", "en"),
	("Construction Work Approval — EN", "Construction Work Approval Request", "work_approval_en.html", "en"),
	("Construction CAPA — EN", "Construction CAPA", "capa_en.html", "en"),
	("Subcontract Payment Certificate — EN", "Subcontract Payment Certificate", "subcontract_payment_en.html", "en"),
)


def execute():
	for report in REPORTS:
		frappe.reload_doc("omnexa_construction", "report", report)

	base = Path(__file__).resolve().parents[2] / "construction_forms" / "print_templates"
	for name, doctype, filename, lang in EN_PRINTS:
		if not frappe.db.exists("DocType", doctype):
			continue
		path = base / filename
		if not path.exists():
			continue
		html = path.read_text(encoding="utf-8")
		if frappe.db.exists("Print Format", name):
			frappe.db.set_value(
				"Print Format",
				name,
				{"html": html, "custom_format": 1, "print_format_type": "Jinja", "disabled": 0, "default_print_language": lang},
				update_modified=True,
			)
		else:
			frappe.get_doc(
				{
					"doctype": "Print Format",
					"name": name,
					"doc_type": doctype,
					"module": MODULE,
					"custom_format": 1,
					"print_format_type": "Jinja",
					"standard": "Yes",
					"disabled": 0,
					"default_print_language": lang,
					"html": html,
				}
			).insert(ignore_permissions=True)

	_add_evm_dashboard_shortcut()
	frappe.clear_cache()


def _add_evm_dashboard_shortcut():
	ws_name = "Construction"
	if not frappe.db.exists("Workspace", ws_name):
		return
	ws = frappe.get_doc("Workspace", ws_name)
	existing = {s.link_to for s in (ws.shortcuts or []) if s.link_to}
	if "Construction EVM Dashboard" in existing:
		return
	ws.append(
		"shortcuts",
		{"type": "Report", "link_to": "Construction EVM Dashboard", "label": "EVM Dashboard", "color": "Blue"},
	)
	ws.save(ignore_permissions=True)
