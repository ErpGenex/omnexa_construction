# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

from pathlib import Path

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from omnexa_construction.construction_forms.print_style import ensure_print_format

MODULE = "Omnexa Construction"

NEW_DOCTYPES = (
	"Subcontract Compliance Line",
	"Construction Integration Settings",
)

REPORTS = (
	"construction_commercial_pipeline",
	"construction_snagging_summary",
	"hse_incident_summary",
	"environmental_compliance",
)

PRINTS = (("IPC Certificate — EN", "IPC Certificate", "ipc_certificate_en.html", "en"),)


def execute():
	for name in NEW_DOCTYPES:
		if frappe.db.exists("DocType", name):
			frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))

	create_custom_fields(
		{
			"Subcontract Work Order": [
				{
					"fieldname": "compliance_documents",
					"label": "Compliance Documents",
					"fieldtype": "Table",
					"options": "Subcontract Compliance Line",
					"insert_after": "scope_of_work",
					"module": MODULE,
				},
			],
			"Subcontract Payment Certificate": [
				{
					"fieldname": "lien_waiver_attachment",
					"label": "Lien Waiver",
					"fieldtype": "Attach",
					"insert_after": "payment_reference",
					"module": MODULE,
				},
			],
			"Project Contract": [
				{
					"fieldname": "require_lien_waiver",
					"label": "Require Lien Waiver on Subcontract Payment",
					"fieldtype": "Check",
					"default": "0",
					"insert_after": "default_wht_percent",
					"module": MODULE,
				},
			],
		},
		update=True,
	)

	for report in REPORTS:
		frappe.reload_doc("omnexa_construction", "report", report)

	base = Path(__file__).resolve().parents[2] / "construction_forms" / "print_templates"
	for name, doctype, filename, lang in PRINTS:
		if not frappe.db.exists("DocType", doctype):
			continue
		path = base / filename
		if not path.exists():
			continue
		ensure_print_format(name, doctype, path.read_text(encoding="utf-8"), lang=lang)

	if frappe.db.exists("Page", "construction-site-mobile"):
		frappe.reload_doc("omnexa_construction", "page", "construction_site_mobile")

	_link_workspace()
	frappe.clear_cache()


def _link_workspace():
	if not frappe.db.exists("Workspace", "Construction"):
		return
	ws = frappe.get_doc("Workspace", "Construction")
	existing = {s.link_to for s in (ws.shortcuts or []) if s.link_to}
	add = [
		("Page", "construction-site-mobile", "Site Mobile Hub"),
		("Report", "Construction Commercial Pipeline", "Commercial Pipeline"),
		("Report", "Construction Snagging Summary", "Snagging Summary"),
		("Report", "HSE Incident Summary", "HSE Summary"),
		("Report", "Environmental Compliance", "Environmental"),
		("DocType", "Construction Integration Settings", "Integrations"),
	]
	for typ, link_to, label in add:
		if link_to in existing:
			continue
		if typ == "DocType" and not frappe.db.exists("DocType", link_to):
			continue
		ws.append("shortcuts", {"type": typ, "link_to": link_to, "label": label, "color": "Grey"})
		existing.add(link_to)
	ws.save(ignore_permissions=True)
