# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Outbound webhook dispatch for construction document events."""

from __future__ import annotations

import json

import frappe
from frappe import _


def dispatch_construction_event(doc, event: str) -> None:
	if frappe.flags.in_import or frappe.flags.in_migrate:
		return
	url = _webhook_url()
	if not url:
		return
	payload = {
		"event": event,
		"doctype": doc.doctype,
		"name": doc.name,
		"project_contract": getattr(doc, "project_contract", None),
		"company": getattr(doc, "company", None),
		"status": getattr(doc, "status", None),
	}
	try:
		frappe.enqueue(
			"omnexa_construction.construction_integrations._post_webhook",
			queue="short",
			url=url,
			payload=payload,
			now=frappe.flags.in_test,
		)
	except Exception:
		frappe.log_error(title="Construction webhook enqueue failed")


def dispatch_ipc_certified(doc, method=None) -> None:
	dispatch_construction_event(doc, "ipc.certified")


def dispatch_rfi_submitted(doc, method=None) -> None:
	dispatch_construction_event(doc, "rfi.submitted")


def dispatch_transmittal_issued(doc, method=None) -> None:
	if doc.status == "Issued":
		dispatch_construction_event(doc, "transmittal.issued")


def _webhook_url() -> str | None:
	if not frappe.db.exists("DocType", "Construction Integration Settings"):
		return None
	if not frappe.db.get_single_value("Construction Integration Settings", "enable_webhooks"):
		return None
	return frappe.db.get_single_value("Construction Integration Settings", "webhook_url")


def _post_webhook(url: str, payload: dict) -> None:
	import requests

	headers = {"Content-Type": "application/json"}
	secret = None
	if frappe.db.exists("DocType", "Construction Integration Settings"):
		secret = frappe.db.get_single_value("Construction Integration Settings", "webhook_secret")
	if secret:
		headers["X-Construction-Signature"] = secret
	response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=15)
	response.raise_for_status()
