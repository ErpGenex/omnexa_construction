# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Optional workflow binding when omnexa_engineering_consulting is installed."""

from __future__ import annotations

import frappe


def validate_construction_workflow_binding(doc, method=None) -> None:
	if getattr(doc.flags, "ignore_contract_workflow_binding", False):
		return
	if getattr(frappe.flags, "in_migrate", False):
		return
	if not frappe.db.exists("DocType", "Engineering Consulting Settings"):
		return
	if not frappe.db.get_single_value(
		"Engineering Consulting Settings",
		"strict_enforce_contract_workflow_binding",
	):
		return

	project_contract = getattr(doc, "project_contract", None)
	if not project_contract:
		return

	original_project = getattr(doc, "project", None)
	doc.project = project_contract
	try:
		from omnexa_engineering_consulting.contract_workflow_hooks import (
			validate_bound_workflow_matches_site,
		)

		validate_bound_workflow_matches_site(doc, method)
	finally:
		doc.project = original_project
