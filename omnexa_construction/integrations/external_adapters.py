# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""External platform adapters (Procore / Aconex) — export stubs."""

from __future__ import annotations

import frappe
from frappe import _


def _settings():
	if not frappe.db.exists("DocType", "Construction Integration Settings"):
		return frappe._dict()
	return frappe.get_single("Construction Integration Settings")


@frappe.whitelist()
def export_to_procore(doctype: str, name: str) -> dict:
	settings = _settings()
	if not settings.get("procore_project_id"):
		frappe.throw(_("Set Procore Project ID in Construction Integration Settings."), title=_("Procore"))
	doc = frappe.get_doc(doctype, name)
	payload = {
		"platform": "procore",
		"procore_project_id": settings.procore_project_id,
		"doctype": doctype,
		"name": name,
		"project_contract": getattr(doc, "project_contract", None),
		"subject": getattr(doc, "subject", None) or getattr(doc, "title", None),
		"status": getattr(doc, "status", None),
	}
	if settings.get("webhook_url") and settings.get("enable_webhooks"):
		from omnexa_construction.construction_integrations import _post_webhook

		frappe.enqueue(
			"omnexa_construction.construction_integrations._post_webhook",
			queue="short",
			url=settings.webhook_url,
			payload={**payload, "event": "procore.export"},
		)
	return {"ok": True, "payload": payload}


@frappe.whitelist()
def export_to_aconex(doctype: str, name: str) -> dict:
	settings = _settings()
	if not settings.get("aconex_project_id"):
		frappe.throw(_("Set Aconex Project ID in Construction Integration Settings."), title=_("Aconex"))
	doc = frappe.get_doc(doctype, name)
	payload = {
		"platform": "aconex",
		"aconex_project_id": settings.aconex_project_id,
		"doctype": doctype,
		"name": name,
		"project_contract": getattr(doc, "project_contract", None),
		"reference": getattr(doc, "reference_no", None) or name,
	}
	if settings.get("webhook_url") and settings.get("enable_webhooks"):
		from omnexa_construction.construction_integrations import _post_webhook

		frappe.enqueue(
			"omnexa_construction.construction_integrations._post_webhook",
			queue="short",
			url=settings.webhook_url,
			payload={**payload, "event": "aconex.export"},
		)
	return {"ok": True, "payload": payload}
