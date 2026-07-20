# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe

from omnexa_construction.workspace.construction_workspace import sync_construction_workspace_menu


def execute():
	"""Drop Construction QHSE workspace; all items live on Construction sidebar."""
	stats = sync_construction_workspace_menu(save=True)
	frappe.logger("omnexa_construction").info(
		"Construction workspace merged QHSE: %s", stats
	)
