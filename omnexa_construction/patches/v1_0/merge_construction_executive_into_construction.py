# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""One-time: merge Construction Executive workspace into Construction and delete it."""

from __future__ import annotations

import frappe

from omnexa_construction.patches.v1_0.ensure_construction_executive_workspace import (
	_ensure_kpi_cards,
	_merge_executive_into_construction,
	_remove_executive_workspace,
)


def execute():
	if not frappe.db.exists("DocType", "Workspace"):
		return
	_ensure_kpi_cards()
	_merge_executive_into_construction()
	_remove_executive_workspace()
	frappe.db.commit()
