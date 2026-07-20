# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"

NEW_DOCTYPES = (
	"Construction Supplier Prequalification",
	"Site Daily Report Photo",
)

REPORTS = ("rfq_bid_tabulation", "ncr_aging", "ptw_register")

WORKFLOW_DOCTYPES = (
	"Construction RFI",
	"Construction NCR",
	"Construction CAPA",
	"Construction Permit to Work",
	"Construction Supplier Prequalification",
)


def execute():
	create_custom_fields(
		{
			"Construction Document Transmittal Item": [
				{
					"fieldname": "cde_document",
					"label": "CDE Document",
					"fieldtype": "Link",
					"options": "Construction CDE Document",
					"insert_after": "document_no",
					"module": MODULE
	},
			],
			"Site Daily Report": [
				{
					"fieldname": "site_latitude",
					"label": "Latitude",
					"fieldtype": "Float",
					"insert_after": "weather",
					"module": MODULE
	},
				{
					"fieldname": "site_longitude",
					"label": "Longitude",
					"fieldtype": "Float",
					"insert_after": "site_latitude",
					"module": MODULE
	},
				{
					"fieldname": "site_photos",
					"label": "Site Photos",
					"fieldtype": "Table",
					"options": "Site Daily Report Photo",
					"insert_after": "safety_notes",
					"module": MODULE
	},
			]},
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
						"module": MODULE
	},
				]},
			update=True,
		)

	for name in NEW_DOCTYPES:
		frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))
	for report in REPORTS:
		frappe.reload_doc("omnexa_construction", "report", report)

	try:
		from omnexa_construction.construction_workflows import sync_qhse_and_document_workflows

		sync_qhse_and_document_workflows()
	except Exception:
		frappe.log_error(title="QHSE workflow sync failed")
		raise

	_link_workspace()
	frappe.clear_cache()


def _link_workspace():
	if not frappe.db.exists("Workspace", "Construction"):
		return
	ws = frappe.get_doc("Workspace", "Construction")
	existing = {s.link_to for s in (ws.shortcuts or []) if s.link_to}
	for link_to, label in (("Construction Supplier Prequalification", "Supplier Prequalification"),):
		if link_to in existing or not frappe.db.exists("DocType", link_to):
			continue
		ws.append("shortcuts", {"type": "DocType", "link_to": link_to, "label": label, "color": "Green"
	})
		existing.add(link_to)
	for link_to, label in (
		("RFQ Bid Tabulation", "RFQ Bid Tabulation"),
		("NCR Aging", "NCR Aging"),
		("PTW Register", "PTW Register"),
	):
		if link_to in existing:
			continue
		ws.append("shortcuts", {"type": "Report", "link_to": link_to, "label": label, "color": "Grey"
	})
		existing.add(link_to)
	ws.save(ignore_permissions=True)
