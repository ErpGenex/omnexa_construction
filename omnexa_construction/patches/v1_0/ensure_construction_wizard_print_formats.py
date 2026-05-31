# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

from pathlib import Path

import frappe

DOCTYPE = "Construction Project Setup"
MODULE = "Omnexa Construction"

PRINT_FORMATS = (
	("Construction Setup — BOQ Schedule", "setup_boq_schedule.html"),
	("Construction Setup — IPC Schedule", "setup_ipc_schedule.html"),
	("Construction Setup — Phase Delivery", "setup_phase_delivery.html"),
)


def _template_dir() -> Path:
	return Path(__file__).resolve().parents[2] / "wizard" / "print_templates"


def _ensure_print_format(name: str, html: str) -> None:
	if frappe.db.exists("Print Format", name):
		frappe.db.set_value(
			"Print Format",
			name,
			{
				"html": html,
				"custom_format": 1,
				"print_format_type": "Jinja",
				"disabled": 0,
				"standard": "Yes",
			},
			update_modified=True,
		)
		return
	doc = frappe.get_doc(
		{
			"doctype": "Print Format",
			"name": name,
			"doc_type": DOCTYPE,
			"module": MODULE,
			"custom_format": 1,
			"print_format_type": "Jinja",
			"standard": "Yes",
			"disabled": 0,
			"html": html,
		}
	)
	doc.insert(ignore_permissions=True)


def execute():
	if not frappe.db.exists("DocType", DOCTYPE):
		return
	base = _template_dir()
	for name, filename in PRINT_FORMATS:
		html = (base / filename).read_text(encoding="utf-8")
		_ensure_print_format(name, html)
