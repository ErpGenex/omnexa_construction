# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

from pathlib import Path

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from omnexa_construction.construction_forms.print_style import ensure_print_format

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


def execute():
	create_custom_fields(
		{
			"IPC Certificate": [
				{"fieldname": "penalty_deduction", "label": "Penalty Deduction", "fieldtype": "Currency", "insert_after": "advance_recovery", "module": MODULE
	},
				{"fieldname": "other_deductions", "label": "Other Deductions", "fieldtype": "Currency", "insert_after": "penalty_deduction", "module": MODULE
	},
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
		ensure_print_format(name, doctype, html, lang=lang)
	frappe.clear_cache(doctype="IPC Certificate")
