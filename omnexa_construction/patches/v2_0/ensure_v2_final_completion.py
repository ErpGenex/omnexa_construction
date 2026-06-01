# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

from pathlib import Path

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"

NEW_DOCTYPES = (
	"Construction Change Order BOQ Line",
	"Construction Document Transmittal Recipient",
	"Construction Management Review",
	"Construction Safety KPI",
	"Construction Environmental Monitoring",
)

REPORTS = ("currency_revaluation_exposure",)

EN_PRINTS = (
	("Construction RFI — EN", "Construction RFI", "rfi_en.html", "en"),
	("Construction Permit to Work — EN", "Construction Permit to Work", "ptw_en.html", "en"),
	("Construction NCR — EN", "Construction NCR", "ncr_en.html", "en"),
)


def execute():
	for name in NEW_DOCTYPES:
		frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))

	create_custom_fields(
		{
			"Construction Change Order": [
				{
					"fieldname": "boq_lines",
					"label": "BOQ Lines",
					"fieldtype": "Table",
					"options": "Construction Change Order BOQ Line",
					"insert_after": "cost_impact",
					"module": MODULE,
				},
				{
					"fieldname": "boq_applied",
					"label": "BOQ Applied",
					"fieldtype": "Check",
					"read_only": 1,
					"default": "0",
					"insert_after": "boq_lines",
					"module": MODULE,
				},
			],
			"Construction Document Transmittal": [
				{
					"fieldname": "recipients",
					"label": "Recipients Matrix",
					"fieldtype": "Table",
					"options": "Construction Document Transmittal Recipient",
					"insert_after": "recipient_notes",
					"module": MODULE,
				},
			],
			"Construction CDE Document": [
				{
					"fieldname": "midp_reference",
					"label": "MIDP Reference",
					"fieldtype": "Link",
					"options": "Construction MIDP",
					"insert_after": "information_container",
					"module": MODULE,
				},
			],
			"Project Contract": [
				{
					"fieldname": "pm_risk_register",
					"label": "PM Risk Register",
					"fieldtype": "Data",
					"description": "External risk register reference (PM module)",
					"insert_after": "nec_programme_status",
					"module": MODULE,
				},
			],
			"Subcontract Work Order": [
				{
					"fieldname": "back_to_back_ld",
					"label": "Back-to-Back LD",
					"fieldtype": "Check",
					"default": "0",
					"insert_after": "scope_of_work",
					"module": MODULE,
				},
			],
		},
		update=True,
	)

	if frappe.db.exists("DocType", "Construction Integration Settings"):
		frappe.reload_doc("omnexa_construction", "doctype", "construction_integration_settings")
		create_custom_fields(
			{
				"Construction Integration Settings": [
					{
						"fieldname": "procore_project_id",
						"label": "Procore Project ID",
						"fieldtype": "Data",
						"insert_after": "webhook_secret",
						"module": MODULE,
					},
					{
						"fieldname": "aconex_project_id",
						"label": "Aconex Project ID",
						"fieldtype": "Data",
						"insert_after": "procore_project_id",
						"module": MODULE,
					},
				],
			},
			update=True,
		)

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

	try:
		from omnexa_construction.construction_workflows import sync_qhse_and_document_workflows

		sync_qhse_and_document_workflows()
	except Exception:
		frappe.log_error(title="Final workflow sync failed")
		raise

	_ensure_qhse_workspace()
	from omnexa_construction.patches.v2_0.sync_construction_ar_translations import execute as sync_i18n

	sync_i18n()
	frappe.clear_cache()


def _ensure_qhse_workspace():
	name = "Construction QHSE"
	if not frappe.db.exists("Workspace", name):
		ws = frappe.get_doc(
			{
				"doctype": "Workspace",
				"name": name,
				"label": name,
				"title": name,
				"module": MODULE,
				"public": 1,
				"content": "[]",
			}
		)
		ws.insert(ignore_permissions=True)
	else:
		ws = frappe.get_doc("Workspace", name)

	existing = {s.link_to for s in (ws.shortcuts or []) if s.link_to}
	shortcuts = [
		("DocType", "Construction NCR", "NCR"),
		("DocType", "Construction CAPA", "CAPA"),
		("DocType", "Construction HSE Incident", "HSE Incidents"),
		("DocType", "Construction Permit to Work", "PTW"),
		("DocType", "Construction Hazard Register", "Hazards"),
		("DocType", "Construction Toolbox Talk", "Toolbox Talks"),
		("DocType", "Construction Environmental Aspect", "Environmental"),
		("DocType", "Construction Waste Log", "Waste Log"),
		("DocType", "Construction Environmental Monitoring", "Monitoring"),
		("DocType", "Construction Safety KPI", "Safety KPIs"),
		("DocType", "Construction Internal Audit", "Audits"),
		("DocType", "Construction Management Review", "Mgmt Review"),
		("Report", "HSE Incident Summary", "HSE Summary"),
		("Report", "NCR Aging", "NCR Aging"),
		("Report", "PTW Register", "PTW Register"),
		("Report", "Environmental Compliance", "ENV Compliance"),
	]
	for typ, link_to, label in shortcuts:
		if link_to in existing:
			continue
		if typ == "DocType" and not frappe.db.exists("DocType", link_to):
			continue
		ws.append("shortcuts", {"type": typ, "link_to": link_to, "label": label, "color": "Green"})
		existing.add(link_to)
	ws.save(ignore_permissions=True)
