# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Close World Class competitive gaps (§3.3)."""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "Omnexa Construction"


def execute():
	_add_custom_fields()
	_reload_assets()
	_sync_workspace()
	frappe.clear_cache()


def _add_custom_fields():
	create_custom_fields(
		{
			"Construction Schedule Baseline Task": [
				{
					"fieldname": "predecessor_task",
					"fieldtype": "Data",
					"label": "Predecessor Task",
					"insert_after": "is_milestone",
					"module": MODULE
	},
			],
			"Construction NCR": [
				{
					"fieldname": "target_close_date",
					"fieldtype": "Date",
					"label": "Target Close Date (SLA)",
					"insert_after": "ncr_date",
					"module": MODULE
	},
				{
					"fieldname": "is_sla_breached",
					"fieldtype": "Check",
					"label": "SLA Breached",
					"read_only": 1,
					"insert_after": "status",
					"module": MODULE
	},
			],
			"Construction Integration Settings": [
				{
					"fieldname": "bim360_client_id",
					"fieldtype": "Data",
					"label": "BIM 360 Client ID",
					"insert_after": "bim360_project_name",
					"module": MODULE
	},
				{
					"fieldname": "bim360_client_secret",
					"fieldtype": "Password",
					"label": "BIM 360 Client Secret",
					"insert_after": "bim360_client_id",
					"module": MODULE
	},
				{
					"fieldname": "bim360_access_token",
					"fieldtype": "Password",
					"label": "BIM 360 Access Token",
					"read_only": 1,
					"insert_after": "bim360_client_secret",
					"module": MODULE
	},
				{
					"fieldname": "bim360_token_updated",
					"fieldtype": "Datetime",
					"label": "BIM 360 Token Updated",
					"read_only": 1,
					"insert_after": "bim360_access_token",
					"module": MODULE
	},
				{
					"fieldname": "sap_ps_company_code",
					"fieldtype": "Data",
					"label": "SAP PS Company Code",
					"insert_after": "bim360_token_updated",
					"module": MODULE
	},
				{
					"fieldname": "oracle_unifier_project_number",
					"fieldtype": "Data",
					"label": "Oracle Unifier Project Number",
					"insert_after": "sap_ps_company_code",
					"module": MODULE
	},
			]},
		update=True,
	)

	for dt in ("construction_user_nps",):
		frappe.reload_doc("omnexa_construction", "doctype", dt)

	for page in (
		"construction_hse_dashboard",
		"construction_schedule_gantt",
		"construction_ifc_viewer",
	):
		frappe.reload_doc("omnexa_construction", "page", page)


def _reload_assets():
	pass


def _sync_workspace():
	try:
		from omnexa_construction.workspace.construction_workspace import sync_construction_workspace_menu

		sync_construction_workspace_menu()
	except Exception:
		frappe.log_error(title="Gaps closure workspace sync failed")
