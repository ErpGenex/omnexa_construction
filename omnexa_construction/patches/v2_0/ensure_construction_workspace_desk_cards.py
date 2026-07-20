# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe

from omnexa_construction.workspace.construction_workspace import sync_construction_workspace_menu


def execute():
	try:
		stats = sync_construction_workspace_menu(save=True)
		frappe.logger("omnexa_construction").info("Construction workspace desk cards: %s", stats)
	except Exception as e:
		frappe.logger("omnexa_construction").error("Failed to sync workspace: %s", str(e))
		# Don't fail the patch - workspace sync can be done manually
