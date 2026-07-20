# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""World Class Phases 12–15: IFC viewer, BIM360, regional packages, BI, mock audit."""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"


def execute():
	_reload_doctypes_and_pages()
	_ensure_integration_bim360_fields()
	_sync_workspace()
	frappe.clear_cache()


def _reload_doctypes_and_pages():
	for dt in (
		"construction_cde_access_log",
		"construction_osha_site_checklist",
	):
		frappe.reload_doc("omnexa_construction", "doctype", dt)

	for page in ("construction_ifc_viewer", "construction_bi_executive"):
		frappe.reload_doc("omnexa_construction", "page", page)

	for report in ("construction_world_class_mock_audit",):
		frappe.reload_doc("omnexa_construction", "report", report)


def _ensure_integration_bim360_fields():
	if not frappe.db.exists("DocType", "Construction Integration Settings"):
		return
	frappe.reload_doc("omnexa_construction", "doctype", "construction_integration_settings")
	create_custom_fields(
		{
			"Construction Integration Settings": [
				{
					"fieldname": "bim360_section",
					"fieldtype": "Section Break",
					"label": "Autodesk BIM 360 / ACC",
					"insert_after": "aconex_project_id",
					"module": MODULE
	},
				{
					"fieldname": "bim360_hub_id",
					"fieldtype": "Data",
					"label": "BIM 360 Hub ID",
					"insert_after": "bim360_section",
					"module": MODULE
	},
				{
					"fieldname": "bim360_project_id",
					"fieldtype": "Data",
					"label": "BIM 360 Project ID",
					"insert_after": "bim360_hub_id",
					"module": MODULE
	},
				{
					"fieldname": "bim360_project_name",
					"fieldtype": "Data",
					"label": "BIM 360 Project Name",
					"insert_after": "bim360_project_id",
					"module": MODULE
	},
			]},
		update=True,
	)


def _sync_workspace():
	try:
		from omnexa_construction.workspace.construction_workspace import sync_construction_workspace_menu

		sync_construction_workspace_menu()
	except Exception:
		frappe.log_error(title="World Class workspace sync failed")
