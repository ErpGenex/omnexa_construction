# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

from pathlib import Path

import frappe

from omnexa_construction.construction_forms.print_style import ensure_print_format

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
		ensure_print_format(name, doctype, path.read_text(encoding="utf-8"), lang=lang)

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
		{"type": "Report", "link_to": "Construction EVM Dashboard", "label": "EVM Dashboard", "color": "Blue"
	},
	)
	ws.save(ignore_permissions=True)
