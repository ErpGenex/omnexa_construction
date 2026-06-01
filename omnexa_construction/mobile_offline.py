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
	for item in items:
		doctype = item.get("doctype")
		if not doctype or not frappe.db.exists("DocType", doctype):
			continue
		draft = item.get("draft") or {}
		if not draft:
			synced += 1
			continue
		doc = frappe.new_doc(doctype)
		doc.update(draft)
		doc.insert(ignore_permissions=True)
		synced += 1
	return {"synced": synced, "remaining": max(0, len(items) - synced)}
