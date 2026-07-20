# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Enhanced site mobile — GPS, photos, signature payloads."""

from __future__ import annotations

import base64
import json

import frappe
from frappe import _


@frappe.whitelist()
def capture_site_payload(
	doctype: str,
	draft_json: str,
	gps_lat: float | None = None,
	gps_lng: float | None = None,
	photo_base64: str | None = None,
	signature_base64: str | None = None,
) -> dict:
	"""Enrich offline draft with geo + attachments before queue sync."""
	draft = json.loads(draft_json or "{}")
	if gps_lat is not None and gps_lng is not None:
		draft["gps_latitude"] = gps_lat
		draft["gps_longitude"] = gps_lng
	meta = frappe.get_meta(doctype)
	if gps_lat is not None and meta.has_field("gps_location"):
		draft["gps_location"] = f"{gps_lat},{gps_lng}"

	attachments = []
	if photo_base64:
		attachments.append(_save_data_url(photo_base64, prefix="site_photo"))
	if signature_base64:
		attachments.append(_save_data_url(signature_base64, prefix="site_signature"))

	return {"draft": draft, "attachments": attachments}


@frappe.whitelist()
def sync_offline_queue_enhanced(queue_json: str) -> dict:
	from omnexa_construction.mobile_offline import sync_offline_queue

	items = json.loads(queue_json or "[]")
	for item in items:
		for att in item.get("attachments") or []:
			if att.get("file_url") and item.get("draft"):
				item["draft"]["remarks"] = (item["draft"].get("remarks") or "") + f"\n[Attachment: {att['file_url']}]"
	return sync_offline_queue(json.dumps(items))


def _save_data_url(data_url: str, prefix: str) -> dict:
	if "," in data_url:
		data_url = data_url.split(",", 1)[1]
	content = base64.b64decode(data_url)
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": f"{prefix}_{frappe.generate_hash(length=8)}.png",
			"content": content,
			"is_private": 1,
		}
	)
	file_doc.insert(ignore_permissions=True)
	return {"file_url": file_doc.file_url}
