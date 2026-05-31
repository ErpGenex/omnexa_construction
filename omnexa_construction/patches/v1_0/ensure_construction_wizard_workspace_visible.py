# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Ensure Construction Project Wizard appears in Construction workspace sidebar + dashboard."""

from __future__ import annotations

import json

import frappe

WIZARD_LABEL = "New Project (Wizard)"
WIZARD_PAGE = "construction-project-wizard"
WIZARD_CONTENT_ID = "construction-sc-wizard"


def execute():
	if not frappe.db.exists("Page", WIZARD_PAGE):
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
	if _ensure_content_shortcut(content):
		ws.content = json.dumps(content, separators=(",", ":"))
		changed = True

	return changed


def _ensure_sidebar_link(ws) -> bool:
	for row in ws.links or []:
		if (row.link_to or "") == WIZARD_PAGE:
			if row.hidden:
				row.hidden = 0
				return True
			return False
	ws.append(
		"links",
		{
			"type": "Link",
			"label": WIZARD_LABEL,
			"link_to": WIZARD_PAGE,
			"link_type": "Page",
			"icon": "add",
			"hidden": 0,
		},
	)
	return True


def _ensure_shortcut_row(ws) -> bool:
	for row in ws.shortcuts or []:
		if (row.link_to or "") == WIZARD_PAGE:
			return False
	ws.append(
		"shortcuts",
		{
			"label": WIZARD_LABEL,
			"type": "Page",
			"link_to": WIZARD_PAGE,
			"color": "Green",
		},
	)
	return True


def _ensure_content_shortcut(content: list) -> bool:
	if any(isinstance(row, dict) and row.get("id") == WIZARD_CONTENT_ID for row in content):
		return False
	if any(
		isinstance(row, dict)
		and row.get("type") == "shortcut"
		and (row.get("data") or {}).get("shortcut_name") == WIZARD_LABEL
		for row in content
	):
		return False

	insert_at = _content_insert_index(content)
	content.insert(
		insert_at,
		{
			"id": WIZARD_CONTENT_ID,
			"type": "shortcut",
			"data": {"shortcut_name": WIZARD_LABEL, "col": 3},
		},
	)
	return True


def _content_insert_index(content: list) -> int:
	for i, row in enumerate(content):
		if not isinstance(row, dict):
			continue
		if row.get("type") != "header":
			continue
		text = (row.get("data") or {}).get("text") or ""
		if any(token in text for token in ("Operations", "Quick Actions", "Construction")):
			return i + 1
	for i, row in enumerate(content):
		if isinstance(row, dict) and row.get("type") == "shortcut":
			return i
	return len(content)
