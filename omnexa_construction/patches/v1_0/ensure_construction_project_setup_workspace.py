# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Expose Construction Project Setup in Construction workspace (sidebar + dashboard)."""

from __future__ import annotations

import json

import frappe

SETUP_DOCTYPE = "Construction Project Setup"
SETUP_LABEL = "Construction Project Setup"
SETUP_ICON = "edit"
CONTENT_ID = "construction-sc-project-setup"
WIZARD_CONTENT_ID = "construction-sc-wizard"


def execute():
	if not frappe.db.exists("DocType", SETUP_DOCTYPE):
		return
	if not frappe.db.exists("Workspace", "Construction"):
		return

	for attempt in range(5):
		ws = frappe.get_doc("Workspace", "Construction")
		changed = _apply(ws)
		if not changed:
			break
		try:
			ws.save(ignore_permissions=True, ignore_version=True)
			break
		except frappe.TimestampMismatchError:
			frappe.db.rollback()
			if attempt == 4:
				raise

	frappe.clear_cache(doctype="Workspace")


def _apply(ws) -> bool:
	changed = False
	changed |= _ensure_sidebar_link(ws)
	changed |= _ensure_shortcut_row(ws)
	content = json.loads(ws.content or "[]")
	if _ensure_content_shortcut(content, ws):
		ws.content = json.dumps(content, separators=(",", ":"))
		changed = True
	return changed


def _row_val(row, field: str, default=None):
	if isinstance(row, dict):
		return row.get(field, default)
	return getattr(row, field, default)


def _ensure_sidebar_link(ws) -> bool:
	for row in ws.links or []:
		if (_row_val(row, "link_to") or "") == SETUP_DOCTYPE and _row_val(row, "link_type") == "DocType":
			if _row_val(row, "hidden"):
				if isinstance(row, dict):
					row["hidden"] = 0
				else:
					row.hidden = 0
				return True
			return False

	insert_at = 0
	for i, row in enumerate(ws.links or []):
		if _row_val(row, "type") == "Card Break" and (_row_val(row, "label") or "") == "Contracts & BOQ":
			insert_at = i
			break
		if (_row_val(row, "link_to") or "") == "construction-project-wizard":
			insert_at = i + 1

	row = ws.append(
		"links",
		{
			"type": "Link",
			"label": SETUP_LABEL,
			"link_to": SETUP_DOCTYPE,
			"link_type": "DocType",
			"icon": SETUP_ICON,
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
	)
	if insert_at < len(ws.links) - 1:
		ws.links.pop()
		ws.links.insert(insert_at, row)
	return True


def _ensure_shortcut_row(ws) -> bool:
	for row in ws.shortcuts or []:
		if (_row_val(row, "link_to") or "") == SETUP_DOCTYPE and _row_val(row, "type") == "DocType":
			return False

	insert_at = 0
	for i, row in enumerate(ws.shortcuts or []):
		if (_row_val(row, "link_to") or "") == "construction-project-wizard":
			insert_at = i + 1
			break

	row = ws.append(
		"shortcuts",
		{
			"label": SETUP_LABEL,
			"type": "DocType",
			"link_to": SETUP_DOCTYPE,
			"doc_view": "List",
			"color": "Green",
		},
	)
	if insert_at < len(ws.shortcuts) - 1:
		ws.shortcuts.pop()
		ws.shortcuts.insert(insert_at, row)
	return True


def _ensure_content_shortcut(content: list, ws) -> bool:
	if any(isinstance(row, dict) and row.get("id") == CONTENT_ID for row in content):
		return False
	label = SETUP_LABEL
	for row in ws.shortcuts or []:
		if (_row_val(row, "link_to") or "") == SETUP_DOCTYPE:
			label = _row_val(row, "label") or label
			break

	insert_at = len(content)
	for i, row in enumerate(content):
		if isinstance(row, dict) and row.get("id") == WIZARD_CONTENT_ID:
			insert_at = i + 1
			break

	content.insert(
		insert_at,
		{
			"id": CONTENT_ID,
			"type": "shortcut",
			"data": {"shortcut_name": label, "col": 3},
		},
	)
	return True
