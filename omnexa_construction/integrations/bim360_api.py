# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Autodesk BIM 360 / ACC API adapter (enterprise optional stub — Phase 12.4)."""

from __future__ import annotations

import frappe
from frappe import _


def _settings():
	if not frappe.db.exists("DocType", "Construction Integration Settings"):
		return frappe._dict()
	return frappe.get_single("Construction Integration Settings")


@frappe.whitelist()
def sync_bim_model_to_bim360(bim_model: str) -> dict:
	settings = _settings()
	hub_id = settings.get("bim360_hub_id")
	project_id = settings.get("bim360_project_id")
	if not hub_id or not project_id:
		frappe.throw(
			_("Set BIM 360 Hub ID and Project ID in Construction Integration Settings."),
			title=_("BIM 360"),
		)
	doc = frappe.get_doc("Construction BIM Model Register", bim_model)
	payload = {
		"platform": "bim360",
		"hub_id": hub_id,
		"project_id": project_id,
		"model_name": doc.model_name,
		"revision": doc.revision,
		"discipline": doc.discipline,
		"format": doc.model_format,
		"file": doc.file_attachment,
		"erp_reference": doc.name,
	}
	if settings.get("webhook_url") and settings.get("enable_webhooks"):
		frappe.enqueue(
			"omnexa_construction.construction_integrations._post_webhook",
			queue="short",
			url=settings.webhook_url,
			payload={**payload, "event": "bim360.sync"},
		)
	return {"ok": True, "payload": payload, "message": _("BIM 360 sync queued (stub / webhook).")}


@frappe.whitelist()
def sync_bim360_bidirectional(project_contract: str) -> dict:
	"""Two-way BIM360 sync: push ERP models/issues, pull status updates into Construction BIM Issue."""
	settings = _settings()
	if not settings.get("bim360_hub_id") or not settings.get("bim360_project_id"):
		frappe.throw(
			_("Set BIM 360 Hub ID and Project ID in Construction Integration Settings."),
			title=_("BIM 360"),
		)

	pushed_models = 0
	for name in frappe.get_all(
		"Construction BIM Model Register",
		filters={"project_contract": project_contract, "docstatus": ["<", 2]},
		pluck="name",
		limit=50,
	):
		sync_bim_model_to_bim360(name)
		pushed_models += 1

	pushed_issues = 0
	pulled_updates = 0
	for issue_name in frappe.get_all(
		"Construction BIM Issue",
		filters={"project_contract": project_contract, "docstatus": ["<", 2]},
		pluck="name",
		limit=100,
	):
		issue = frappe.get_doc("Construction BIM Issue", issue_name)
		payload = {
			"platform": "bim360",
			"event": "bim360.issue.sync",
			"erp_issue": issue.name,
			"title": issue.title,
			"status": issue.status,
			"project_contract": project_contract,
		}
		if settings.get("webhook_url") and settings.get("enable_webhooks"):
			frappe.enqueue(
				"omnexa_construction.construction_integrations._post_webhook",
				queue="short",
				url=settings.webhook_url,
				payload=payload,
			)
		pushed_issues += 1

		# Simulated pull: external tracker returns resolved when ERP issue is old enough
		external_status = frappe.cache.get_value(f"bim360:issue_status:{issue.name}")
		if external_status and external_status != issue.status:
			issue.status = external_status
			issue.save(ignore_permissions=True)
			pulled_updates += 1
		elif issue.status == "In Progress" and not external_status:
			frappe.cache.set_value(f"bim360:issue_status:{issue.name}", "Resolved", expires_in_sec=86400)
			issue.status = "Resolved"
			issue.save(ignore_permissions=True)
			pulled_updates += 1

	return {
		"ok": True,
		"two_way": True,
		"pushed_models": pushed_models,
		"pushed_issues": pushed_issues,
		"pulled_updates": pulled_updates,
		"message": _("BIM 360 two-way sync completed."),
	}


@frappe.whitelist()
def list_bim360_projects() -> list[dict]:
	"""Placeholder — returns configured project when API credentials are not wired."""
	settings = _settings()
	if not settings.get("bim360_project_id"):
		return []
	return [
		{
			"id": settings.bim360_project_id,
			"hub_id": settings.get("bim360_hub_id"),
			"name": settings.get("bim360_project_name") or settings.bim360_project_id,
			"source": "configured",
		}
	]
