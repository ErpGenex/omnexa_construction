# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

from pathlib import Path

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"

PRINTS = (
	("Construction Work Approval — AR", "Construction Work Approval Request", "work_approval_ar.html", "ar"),
	("Construction Material Approval — AR", "Construction Material Approval Request", "material_approval_ar.html", "ar"),
	("Contractor Account Statement — AR", "Contractor Account Statement", "contractor_account_ar.html", "ar"),
	("Construction Fines Statement — AR", "Construction Fines Statement", "fines_statement_ar.html", "ar"),
	("Construction Work Delay — AR", "Construction Work Delay Notice", "work_delay_ar.html", "ar"),
	("IPC Certificate — AR (مستخلص مقاولات)", "IPC Certificate", "ipc_certificate_ar.html", "ar"),
)


def _template_dir() -> Path:
	return Path(__file__).resolve().parents[2] / "construction_forms" / "print_templates"


def _ensure_print(name: str, doctype: str, html: str, lang: str = "ar") -> None:
	if frappe.db.exists("Print Format", name):
		frappe.db.set_value(
			"Print Format",
			name,
			{"html": html, "custom_format": 1, "print_format_type": "Jinja", "disabled": 0, "standard": "Yes", "default_print_language": lang},
			update_modified=True,
		)
		return
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


def execute():
	create_custom_fields(
		{
			"IPC Certificate": [
				{"fieldname": "penalty_deduction", "label": "Penalty Deduction", "fieldtype": "Currency", "insert_after": "advance_recovery", "module": MODULE},
				{"fieldname": "other_deductions", "label": "Other Deductions", "fieldtype": "Currency", "insert_after": "penalty_deduction", "module": MODULE},
			]
		},
		update=True,
	)
	base = _template_dir()
	for name, doctype, filename, lang in PRINTS:
		if not frappe.db.exists("DocType", doctype):
			continue
		html = (base / filename).read_text(encoding="utf-8")
		if filename == "contractor_account_ar.html" and "set currency" not in html:
			html = html.replace(
				"{% for row in doc.lines %}",
				"{% set currency = frappe.db.get_value('Project Contract', doc.project_contract, 'contract_currency') or 'EGP' %}\n    {% for row in doc.lines %}",
			)
		_ensure_print(name, doctype, html, lang)
	frappe.clear_cache(doctype="IPC Certificate")
