# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

from pathlib import Path

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from omnexa_construction.construction_forms.print_style import ensure_print_format

MODULE = "Omnexa Construction"

NEW_DOCTYPES = (
	"Construction MIDP Line",
	"Construction MIDP",
	"Construction BIM Model Register",
	"Construction BIM Issue",
	"Construction Early Warning",
	"Construction Compensation Event",
	"Construction Dispute Event",
	"Construction Dispute Case",
)

PRINTS = (
	("Construction RFI — AR", "Construction RFI", "rfi_ar.html", "ar"),
	("Construction Permit to Work — AR", "Construction Permit to Work", "ptw_ar.html", "ar"),
	("Construction NCR — AR", "Construction NCR", "ncr_ar.html", "ar"),
	("Construction CAPA — AR", "Construction CAPA", "capa_ar.html", "ar"),
	("Subcontract Payment Certificate — AR", "Subcontract Payment Certificate", "subcontract_payment_ar.html", "ar"),
)

WORKSPACE_SHORTCUTS = (
	("Construction Hazard Register", "Hazard Register"),
	("Construction Environmental Aspect", "Environmental"),
	("Construction Waste Log", "Waste Log"),
	("Construction Internal Audit", "Internal Audit"),
	("Construction Toolbox Talk", "Toolbox Talk"),
	("Construction MIDP", "MIDP"),
	("Construction BIM Model Register", "BIM Models"),
	("Construction BIM Issue", "BIM Issues"),
	("Construction Early Warning", "Early Warnings"),
	("Construction Compensation Event", "Compensation Events"),
	("Construction Dispute Case", "Disputes"),
	("Construction RFI", "RFI"),
)


def _template_dir() -> Path:
	return Path(__file__).resolve().parents[2] / "construction_forms" / "print_templates"


def execute():
	create_custom_fields(
		{
			"Construction RFQ": [
				{
					"fieldname": "purchase_order",
					"label": "Purchase Order",
					"fieldtype": "Link",
					"options": "Purchase Order",
					"read_only": 1,
					"insert_after": "awarded_supplier",
					"module": MODULE
	},
			],
			"IPC Certificate": [
				{
					"fieldname": "exchange_rate",
					"label": "Exchange Rate",
					"fieldtype": "Float",
					"default": "1",
					"insert_after": "net_after_tax",
					"module": MODULE
	},
			],
			"Construction Material Approval Request": [
				{
					"fieldname": "material_request",
					"label": "Material Request",
					"fieldtype": "Link",
					"options": "Material Request",
					"read_only": 1,
					"insert_after": "status",
					"module": MODULE
	},
			],
			"Construction Material Approval Line": [
				{
					"fieldname": "item_code",
					"label": "Item",
					"fieldtype": "Link",
					"options": "Item",
					"insert_after": "material_name",
					"module": MODULE
	},
			]},
		update=True,
	)

	for name in NEW_DOCTYPES:
		frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))

	base = _template_dir()
	for name, doctype, filename, lang in PRINTS:
		if not frappe.db.exists("DocType", doctype):
			continue
		path = base / filename
		if not path.exists():
			continue
		ensure_print_format(name, doctype, path.read_text(encoding="utf-8"), lang=lang)

	if frappe.db.exists("Workspace", "Construction"):
		ws = frappe.get_doc("Workspace", "Construction")
		existing = {s.link_to for s in (ws.shortcuts or []) if s.link_to}
		for link_to, label in WORKSPACE_SHORTCUTS:
			if link_to in existing or not frappe.db.exists("DocType", link_to):
				continue
			ws.append(
				"shortcuts",
				{"type": "DocType", "link_to": link_to, "label": label, "color": "Green"
	},
			)
		ws.save(ignore_permissions=True)

	frappe.clear_cache()
