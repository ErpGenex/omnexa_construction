# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import json

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"

NEW_DOCTYPES = (
	"Construction DAB Referral",
	"Construction Settlement",
	"Subcontract Retention Release",
)

WORKFLOW_DOCTYPES = (
	"Construction Early Warning",
	"Construction Compensation Event",
	"Construction Dispute Case",
)

EXEC_CARDS = [
	("Open RFIs", "Construction RFI", [["status", "in", ["Open", "Overdue"]]]),
	("FIDIC overdue notices", "Construction FIDIC Notice", [["status", "=", "Overdue"]]),
	("Open disputes", "Construction Dispute Case", [["status", "in", ["Open", "DAB Referral"]]]),
	("NEC4 early warnings", "Construction Early Warning", [["status", "in", ["Open", "Escalated"]]]),
]


def execute():
	create_custom_fields(
		{
			"Project Contract": [
				{
					"fieldname": "nec_programme_status",
					"label": "NEC Programme Status",
					"fieldtype": "Select",
					"options": "\nSubmitted\nAccepted\nRejected",
					"insert_after": "governing_standard",
					"depends_on": "eval:doc.governing_standard=='NEC4 ECC'",
					"module": MODULE,
				},
			],
			"Site Daily Report": [
				{
					"fieldname": "stock_entry",
					"label": "Stock Entry",
					"fieldtype": "Link",
					"options": "Stock Entry",
					"read_only": 1,
					"insert_after": "material_consumed_cost",
					"module": MODULE,
				},
			],
		},
		update=True,
	)

	for dt in WORKFLOW_DOCTYPES:
		if not frappe.db.exists("DocType", dt):
			continue
		if frappe.get_meta(dt).has_field("workflow_state"):
			continue
		create_custom_fields(
			{
				dt: [
					{
						"fieldname": "workflow_state",
						"label": "Workflow State",
						"fieldtype": "Link",
						"options": "Workflow State",
						"hidden": 1,
						"insert_after": "status",
						"module": MODULE,
					},
				],
			},
			update=True,
		)

	for name in NEW_DOCTYPES:
		frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))

	frappe.reload_doc("omnexa_construction", "report", "material_consumption_vs_boq")
	if frappe.db.exists("Page", "construction-executive-dashboard"):
		frappe.reload_doc("omnexa_construction", "page", "construction_executive_dashboard")

	try:
		from omnexa_construction.construction_workflows import sync_nec4_and_dispute_workflows

		sync_nec4_and_dispute_workflows()
	except Exception:
		frappe.log_error(title="NEC4 workflow sync failed")
		raise

	_ensure_exec_number_cards()
	_link_executive_dashboard()
	frappe.clear_cache()


def _ensure_exec_number_cards():
	if not frappe.db.exists("DocType", "Number Card"):
		return
	for label, doctype, filters in EXEC_CARDS:
		if not frappe.db.exists("DocType", doctype):
			continue
		filters_json = json.dumps(filters, separators=(",", ":"))
		existing = frappe.db.get_value(
			"Number Card",
			{"label": label, "document_type": doctype, "function": "Count"},
			"name",
		)
		if existing:
			frappe.db.set_value("Number Card", existing, "filters_json", filters_json, update_modified=False)
			continue
		frappe.get_doc(
			{
				"doctype": "Number Card",
				"label": label,
				"type": "Document Type",
				"document_type": doctype,
				"function": "Count",
				"filters_json": filters_json,
				"module": MODULE,
				"is_public": 1,
				"show_full_number": 1,
			}
		).insert(ignore_permissions=True)


def _link_executive_dashboard():
	if not frappe.db.exists("Workspace", "Construction"):
		return
	ws = frappe.get_doc("Workspace", "Construction")
	labels = {s.label for s in (ws.shortcuts or [])}
	if "Executive Dashboard" not in labels and frappe.db.exists("Page", "construction-executive-dashboard"):
		ws.append(
			"shortcuts",
			{
				"type": "Page",
				"link_to": "construction-executive-dashboard",
				"label": "Executive Dashboard",
				"color": "Blue",
			},
		)
	for label, doctype, _ in EXEC_CARDS:
		if label in labels or not frappe.db.exists("DocType", doctype):
			continue
		ws.append("number_cards", {"label": label, "number_card_name": label})
	ws.save(ignore_permissions=True)
