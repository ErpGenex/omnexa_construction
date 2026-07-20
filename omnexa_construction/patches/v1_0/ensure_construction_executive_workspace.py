# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Merge Construction Executive workspace into Construction; remove duplicate workspace."""

from __future__ import annotations

import json

import frappe


def execute():
	if not frappe.db.exists("DocType", "Workspace"):
		return
	_ensure_kpi_cards()
	_merge_executive_into_construction()
	_remove_executive_workspace()
	frappe.db.commit()


def _merge_executive_into_construction():
	if not frappe.db.exists("Workspace", "Construction"):
		return

	ws = frappe.get_doc("Workspace", "Construction")
	_add_shortcut(ws, "Earned value (EVM)", "Report", "Construction Earned Value", "Project Contract", "Blue")
	_add_shortcut(ws, "Executive summary", "Report", "Construction Executive Summary", "Project Contract", "Green")
	_add_shortcut(ws, "Contract control", "Report", "Construction Contract Control", "Project Contract", "Orange")
	_add_number_card(ws, "Open NCRs")
	_add_number_card(ws, "Open HSE incidents")
	_merge_content_blocks(ws)
	ws.save(ignore_permissions=True)


def _add_shortcut(ws, label: str, link_type: str, link_to: str, report_ref: str | None, color: str):
	for row in ws.shortcuts or []:
		if row.label == label or (row.link_to == link_to and row.type == link_type):
			return
	ws.append(
		"shortcuts",
		{
			"label": label,
			"type": link_type,
			"link_to": link_to,
			"report_ref_doctype": report_ref,
			"color": color
	},
	)


def _add_number_card(ws, number_card_name: str):
	for row in ws.number_cards or []:
		if row.number_card_name == number_card_name or row.label == number_card_name:
			return
	ws.append("number_cards", {"label": number_card_name, "number_card_name": number_card_name
	})


def _shortcut_label(ws, link_to: str, fallback: str) -> str:
	for row in ws.shortcuts or []:
		if row.link_to == link_to and row.type == "Report":
			return row.label or fallback
	return fallback


def _merge_content_blocks(ws):
	try:
		content = json.loads(ws.content or "[]")
	except Exception:
		content = []
	ids = {block.get("id") for block in content if block.get("id")}
	report_shortcuts = [
		("construction-sc-evm", "Construction Earned Value", "Earned value (EVM)"),
		("construction-sc-exec", "Construction Executive Summary", "Executive summary"),
		("construction-sc-ctrl", "Construction Contract Control", "Contract control"),
	]
	extra = [
		{"id": "construction-nc-open-ncr", "type": "number_card", "data": {"number_card_name": "Open NCRs", "col": 4}
	},
		{"id": "construction-nc-open-hse", "type": "number_card", "data": {"number_card_name": "Open HSE incidents", "col": 4}
	},
	]
	for block_id, link_to, fallback in report_shortcuts:
		extra.append(
			{
				"id": block_id,
				"type": "shortcut",
				"data": {"shortcut_name": _shortcut_label(ws, link_to, fallback), "col": 3}
	}
		)
	insert_at = 0
	for i, block in enumerate(content):
		if block.get("id") == "construction-ops":
			insert_at = i
			break
	for block in extra:
		if block["id"] in ids:
			for existing in content:
				if existing.get("id") == block["id"] and existing.get("type") == "shortcut":
					existing.setdefault("data", {})["shortcut_name"] = block["data"]["shortcut_name"]
			continue
		content.insert(insert_at, block)
		insert_at += 1
		ids.add(block["id"])
	ws.content = json.dumps(content, separators=(",", ":"))


def _remove_executive_workspace():
	if frappe.db.exists("Workspace", "Construction Executive"):
		frappe.delete_doc("Workspace", "Construction Executive", force=1, ignore_permissions=True)


def _ensure_kpi_cards():
	if not frappe.db.exists("DocType", "Number Card"):
		return
	_upsert_number_card("Open NCRs", "Construction NCR", [["status", "in", ["Open", "Under Review"]]])
	_upsert_number_card(
		"Open HSE incidents",
		"Construction HSE Incident",
		[["status", "in", ["Reported", "Investigating"]]],
	)


def _upsert_number_card(label: str, document_type: str, filters: list) -> None:
	filters_json = json.dumps(filters, separators=(",", ":"))
	existing = frappe.db.get_value(
		"Number Card",
		{"label": label, "document_type": document_type, "function": "Count"
	},
		"name",
	)
	if existing:
		frappe.db.set_value("Number Card", existing, "filters_json", filters_json, update_modified=False)
		return
	doc = frappe.get_doc(
		{
			"doctype": "Number Card",
			"label": label,
			"type": "Document Type",
			"document_type": document_type,
			"function": "Count",
			"filters_json": filters_json,
			"module": "Omnexa Construction",
			"is_public": 1,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly",
			"show_full_number": 1
	}
	)
	doc.insert(ignore_permissions=True)
