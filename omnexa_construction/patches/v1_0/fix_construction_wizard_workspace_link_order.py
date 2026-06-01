# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe

from omnexa_construction.workspace.construction_workspace import sync_construction_wizard_and_setup


def execute():
	"""Re-apply wizard/setup placement; earlier sync did not update child row idx."""
	if sync_construction_wizard_and_setup(save=True):
		frappe.db.commit()
