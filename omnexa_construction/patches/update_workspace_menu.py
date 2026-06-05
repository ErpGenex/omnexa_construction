# Patch to update workspace menu with new pages

import frappe
from omnexa_construction.workspace.construction_workspace import sync_construction_workspace_menu


def execute():
	"""Update workspace menu with new pages"""
	try:
		stats = sync_construction_workspace_menu(save=True)
		frappe.logger("omnexa_construction").info("Workspace menu updated: %s", stats)
	except Exception as e:
		frappe.logger("omnexa_construction").error("Failed to update workspace menu: %s", str(e))
