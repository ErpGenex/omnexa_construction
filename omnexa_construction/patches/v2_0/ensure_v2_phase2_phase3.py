# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"

NEW_DOCTYPES = (
	"Construction Schedule Baseline",
	"Construction Hazard Register Line",
	"Construction Hazard Register",
	"Construction Environmental Aspect",
	"Construction Waste Log",
	"Construction Quality Audit Finding",
	"Construction Internal Audit",
	"Construction Toolbox Talk",
)

REPORTS = ("boq_commitment_vs_actual", "construction_fidic_compliance")


def execute():
	create_custom_fields(
		{
			"BOQ Item": [
				{
					"fieldname": "committed_cost",
					"label": "Committed Cost (PO)",
					"fieldtype": "Currency",
					"read_only": 1,
					"insert_after": "actual_cost",
					"module": MODULE,
				},
				{
					"fieldname": "po_committed",
					"label": "PO Committed",
					"fieldtype": "Currency",
					"read_only": 1,
					"insert_after": "committed_cost",
					"module": MODULE,
				},
			],
			"Construction CDE Document": [
				{
					"fieldname": "naming_convention",
					"label": "Naming Convention",
					"fieldtype": "Data",
					"insert_after": "document_number",
					"module": MODULE,
				},
				{
					"fieldname": "suitability_code",
					"label": "Suitability Code",
					"fieldtype": "Select",
					"options": "S0\nS1\nS2\nS3\nS4",
					"insert_after": "revision",
					"module": MODULE,
				},
				{
					"fieldname": "information_container",
					"label": "Information Container",
					"fieldtype": "Data",
					"insert_after": "suitability_code",
					"module": MODULE,
				},
			],
		},
		update=True,
	)

	for name in NEW_DOCTYPES:
		frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))
	for report in REPORTS:
		frappe.reload_doc("omnexa_construction", "report", report)

	# Reload PTW if missing from prior orphaned delete
	if not frappe.db.exists("DocType", "Construction Permit to Work"):
		frappe.reload_doc("omnexa_construction", "doctype", "construction_permit_to_work")

	frappe.clear_cache()
	frappe.db.commit()
