# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"

SPECIALIST_ROLES = (
	"Construction QS",
	"Construction Commercial Manager",
	"Construction HSE Officer",
	"Construction QA Manager",
	"Construction Document Controller",
)

NEW_DOCTYPES = (
	"Construction RFI",
	"Construction Snagging Item",
	"Construction Retention Release",
	"Construction CAPA",
	"Construction Permit to Work",
)

COMMERCIAL_SUBMITTABLE = (
	"IPC Certificate",
	"Construction Change Order",
	"Construction Extension of Time",
	"Construction Claim",
	"Construction FIDIC Notice",
	"Construction Final Account Statement",
	"Construction Fines Statement",
	"Construction Work Delay Notice",
)


def _ensure_roles():
	for role in SPECIALIST_ROLES:
		if frappe.db.exists("Role", role):
			continue
		frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1
	}).insert(ignore_permissions=True)


def _ensure_custom_fields():
	create_custom_fields(
		{
			"IPC Certificate": [
				{
					"fieldname": "ld_calculation_notes",
					"label": "LD Calculation Notes",
					"fieldtype": "Small Text",
					"read_only": 1,
					"insert_after": "other_deductions",
					"module": MODULE
	},
				{
					"fieldname": "engineer_certified_by",
					"label": "Engineer Certified By",
					"fieldtype": "Data",
					"insert_after": "employer_certificate_ref",
					"module": MODULE
	},
				{
					"fieldname": "engineer_cert_date",
					"label": "Engineer Cert. Date",
					"fieldtype": "Date",
					"insert_after": "engineer_certified_by",
					"module": MODULE
	},
				{
					"fieldname": "vat_percent",
					"label": "VAT %",
					"fieldtype": "Percent",
					"insert_after": "net_amount",
					"module": MODULE
	},
				{
					"fieldname": "vat_amount",
					"label": "VAT Amount",
					"fieldtype": "Currency",
					"read_only": 1,
					"insert_after": "vat_percent",
					"module": MODULE
	},
				{
					"fieldname": "wht_percent",
					"label": "WHT %",
					"fieldtype": "Percent",
					"insert_after": "vat_amount",
					"module": MODULE
	},
				{
					"fieldname": "wht_amount",
					"label": "WHT Amount",
					"fieldtype": "Currency",
					"read_only": 1,
					"insert_after": "wht_percent",
					"module": MODULE
	},
				{
					"fieldname": "net_after_tax",
					"label": "Net After Tax",
					"fieldtype": "Currency",
					"read_only": 1,
					"insert_after": "wht_amount",
					"module": MODULE
	},
			],
			"Construction FIDIC Notice": [
				{
					"fieldname": "section_links",
					"label": "Linked Records",
					"fieldtype": "Section Break",
					"insert_after": "description",
					"module": MODULE
	},
				{
					"fieldname": "linked_claim",
					"label": "Linked Claim",
					"fieldtype": "Link",
					"options": "Construction Claim",
					"insert_after": "section_links",
					"module": MODULE
	},
				{
					"fieldname": "linked_eot",
					"label": "Linked EOT",
					"fieldtype": "Link",
					"options": "Construction Extension of Time",
					"insert_after": "linked_claim",
					"module": MODULE
	},
				{
					"fieldname": "linked_change_order",
					"label": "Linked Change Order",
					"fieldtype": "Link",
					"options": "Construction Change Order",
					"insert_after": "linked_eot",
					"module": MODULE
	},
				{
					"fieldname": "notice_due_date",
					"label": "Notice Due Date (Time-bar)",
					"fieldtype": "Date",
					"read_only": 1,
					"insert_after": "response_due_date",
					"module": MODULE
	},
				{
					"fieldname": "is_time_barred",
					"label": "Time Barred",
					"fieldtype": "Check",
					"read_only": 1,
					"insert_after": "notice_due_date",
					"module": MODULE
	},
			],
			"Construction Change Order": [
				{
					"fieldname": "change_order_type",
					"label": "Change Order Type",
					"fieldtype": "Select",
					"options": "Instruction\nProposal\nDaywork",
					"default": "Proposal",
					"insert_after": "title",
					"module": MODULE
	},
			],
			"Project Contract": [
				{
					"fieldname": "default_vat_percent",
					"label": "Default VAT %",
					"fieldtype": "Percent",
					"insert_after": "retention_percent",
					"module": MODULE
	},
				{
					"fieldname": "default_wht_percent",
					"label": "Default WHT %",
					"fieldtype": "Percent",
					"insert_after": "default_vat_percent",
					"module": MODULE
	},
			]},
		update=True,
	)


def _reload_doctypes():
	for name in NEW_DOCTYPES + COMMERCIAL_SUBMITTABLE:
		if frappe.db.exists("DocType", name):
			frappe.reload_doc("omnexa_construction", "doctype", frappe.scrub(name))
	report = "construction_fidic_compliance"
	if frappe.db.exists("Report", "Construction FIDIC Compliance"):
		frappe.reload_doc("omnexa_construction", "report", report)


def execute():
	_ensure_roles()
	_ensure_custom_fields()
	_reload_doctypes()

	workflows = []
	try:
		from omnexa_construction.construction_workflows import sync_all_commercial_workflows

		workflows = sync_all_commercial_workflows()
	except Exception:
		frappe.log_error(title="Construction workflows sync failed")
		raise

	frappe.db.commit()
	frappe.logger("omnexa_construction").info(
		"v2 roadmap foundation: roles=%s workflows=%s", SPECIALIST_ROLES, workflows
	)
