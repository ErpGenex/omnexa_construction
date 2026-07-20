# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Lite IFC viewer context — model metadata, file URL, linked BIM issues (Phase 12.3)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import get_url


@frappe.whitelist()
def get_ifc_viewer_context(project_contract: str, bim_model: str | None = None) -> dict:
	if not project_contract:
		frappe.throw(_("Project Contract is required."), title=_("IFC Viewer"))
	if not frappe.has_permission("Construction BIM Model Register", "read"):
		frappe.throw(_("Not permitted to view BIM models."), frappe.PermissionError)

	model_filters = {"project_contract": project_contract, "docstatus": ["<", 2]}
	if bim_model:
		model_filters["name"] = bim_model

	models = frappe.get_all(
		"Construction BIM Model Register",
		filters=model_filters,
		fields=[
			"name",
			"model_name",
			"model_format",
			"discipline",
			"revision",
			"file_attachment",
			"status",
		],
		order_by="modified desc",
	)

	selected = bim_model or (models[0].name if models else None)
	issues = []
	if selected:
		issues = frappe.get_all(
			"Construction BIM Issue",
			filters={"bim_model": selected, "docstatus": ["<", 2]},
			fields=[
				"name",
				"title",
				"status",
				"issue_date",
				"location",
				"assigned_to",
				"description",
			],
			order_by="modified desc",
			limit=200,
		)

	for row in models:
		row["file_url"] = _file_url(row.pop("file_attachment", None))
		row["is_ifc"] = (row.get("model_format") or "").upper() == "IFC"
		row["selected"] = row.name == selected

	return {
		"project_contract": project_contract,
		"selected_model": selected,
		"models": models,
		"issues": issues,
		"viewer_note": _(
			"Lite viewer: metadata and issues list. Open 3D view loads IFC in-browser when a valid IFC file is attached."
		)}


@frappe.whitelist()
def create_bim_issue_from_viewer(
	project_contract: str,
	bim_model: str,
	title: str,
	description: str | None = None,
	location: str | None = None,
) -> dict:
	if not frappe.has_permission("Construction BIM Issue", "create"):
		frappe.throw(_("Not permitted to create BIM issues."), frappe.PermissionError)
	if not frappe.db.exists("Construction BIM Model Register", bim_model):
		frappe.throw(_("BIM model not found."), title=_("BIM Issue"))
	contract_on_model = frappe.db.get_value("Construction BIM Model Register", bim_model, "project_contract")
	if contract_on_model != project_contract:
		frappe.throw(_("BIM model does not belong to this contract."), title=_("BIM Issue"))

	company, branch = frappe.db.get_value(
		"Project Contract", project_contract, ["company", "branch"]
	)
	doc = frappe.get_doc(
		{
			"doctype": "Construction BIM Issue",
			"project_contract": project_contract,
			"bim_model": bim_model,
			"title": title,
			"description": description,
			"location": location,
			"company": company,
			"branch": branch
	}
	)
	doc.insert()
	return {"name": doc.name, "ok": True
	}


def _file_url(file_path: str | None) -> str | None:
	if not file_path:
		return None
	return get_url(file_path)
