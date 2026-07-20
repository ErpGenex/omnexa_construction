# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"


def execute():
	_add_world_class_certification_fields()
	frappe.reload_doc("omnexa_construction", "page", "construction_site_mobile")
	from omnexa_construction.world_class_certification import apply_site_certification_defaults

	apply_site_certification_defaults()
	frappe.clear_cache()


def _add_world_class_certification_fields():
	create_custom_fields(
		{
			"Construction Integration Settings": [
				{
					"fieldname": "world_class_section",
					"fieldtype": "Section Break",
					"label": "World Class Certification",
					"insert_after": "oracle_unifier_project_number",
					"module": MODULE,
				},
				{
					"fieldname": "world_class_compliance_score",
					"fieldtype": "Int",
					"label": "Compliance Score",
					"read_only": 1,
					"default": "100",
					"insert_after": "world_class_section",
					"module": MODULE,
				},
				{
					"fieldname": "world_class_certified_on",
					"fieldtype": "Date",
					"label": "Certified On",
					"read_only": 1,
					"insert_after": "world_class_compliance_score",
					"module": MODULE,
				},
				{
					"fieldname": "world_class_external_auditor_signed",
					"fieldtype": "Check",
					"label": "Auditor Sign-off",
					"default": "0",
					"insert_after": "world_class_certified_on",
					"module": MODULE,
				},
				{
					"fieldname": "world_class_external_auditor",
					"fieldtype": "Data",
					"label": "Auditor Name",
					"insert_after": "world_class_external_auditor_signed",
					"module": MODULE,
				},
				{
					"fieldname": "world_class_external_auditor_firm",
					"fieldtype": "Data",
					"label": "Auditor Firm",
					"insert_after": "world_class_external_auditor",
					"module": MODULE,
				},
				{
					"fieldname": "world_class_mobile_pwa_certified",
					"fieldtype": "Check",
					"label": "Site Mobile PWA Certified",
					"default": "1",
					"description": "ErpGenEx Construction Site Mobile Hub — installable PWA with offline queue.",
					"insert_after": "world_class_external_auditor_firm",
					"module": MODULE,
				},
				{
					"fieldname": "world_class_certificate_notes",
					"fieldtype": "Small Text",
					"label": "Certificate Notes",
					"insert_after": "world_class_mobile_pwa_certified",
					"module": MODULE,
				},
			],
		},
		update=True,
	)
