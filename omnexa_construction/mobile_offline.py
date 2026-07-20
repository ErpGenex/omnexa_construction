# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Offline queue sync for Site Mobile Hub."""

from __future__ import annotations

import json

import frappe
from frappe import _


@frappe.whitelist()
def sync_offline_queue(queue_json: str) -> dict:
	items = json.loads(queue_json or "[]")
	synced = 0
	errors: list[dict] = []
	for item in items:
		doctype = item.get("doctype")
		if not doctype or not frappe.db.exists("DocType", doctype):
			errors.append({"item": item, "error": _("Unknown DocType")})
			continue
		draft = item.get("draft") or {}
		if not draft:
			synced += 1
			continue
		try:
			doc = frappe.new_doc(doctype)
			doc.update(draft)
			doc.flags.from_offline_queue = True
			doc.insert(ignore_permissions=True)
			synced += 1
		except Exception as exc:
			errors.append({"item": item, "error": str(exc)})
	return {
		"synced": synced,
		"remaining": max(0, len(items) - synced - len(errors)),
		"errors": errors,
		"failed": len(errors),
	}
