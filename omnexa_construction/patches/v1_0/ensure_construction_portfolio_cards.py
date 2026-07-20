# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import json

import frappe

from omnexa_construction.utils.number_card_filters import normalize_number_card_filters


PORTFOLIO_CARDS = [
	("Active contracts", "Project Contract", [["status", "=", "Active"]]),
	("Suspended contracts", "Project Contract", [["status", "=", "Suspended"]]),
	("Closed contracts", "Project Contract", [["status", "=", "Closed"]]),
]


def execute():
	if not frappe.db.exists("DocType", "Number Card"):
		return
	for label, doctype, filters in PORTFOLIO_CARDS:
		_upsert_number_card(label, doctype, filters)
	_sync_construction_workspace_cards()
	frappe.db.commit()


def _upsert_number_card(label: str, document_type: str, filters: list) -> str | None:
	filters_json = json.dumps(
		normalize_number_card_filters(document_type, filters),
		separators=(",", ":"),
	)
	existing = frappe.db.get_value(
		"Number Card",
		{"label": label, "document_type": document_type, "function": "Count"
	},
		"name",
	)
	if existing:
		frappe.db.set_value("Number Card", existing, "filters_json", filters_json, update_modified=False)
		return existing
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
	return doc.name


def _sync_construction_workspace_cards():
	if not frappe.db.exists("Workspace", "Construction"):
		return
	ws = frappe.get_doc("Workspace", "Construction")
	labels = {row.label for row in (ws.number_cards or [])}
	for label, _, _ in PORTFOLIO_CARDS:
		if label in labels:
			continue
		ws.append("number_cards", {"label": label, "number_card_name": label
	})
		labels.add(label)

	content = json.loads(ws.content or "[]")
	existing_ids = {row.get("id") for row in content if isinstance(row, dict)}
	insert_at = 2
	for idx, (label, _, _) in enumerate(PORTFOLIO_CARDS):
		block_id = f"construction-portfolio-{idx}"
		if block_id in existing_ids:
			continue
		content.insert(
			insert_at + idx,
			{
				"id": block_id,
				"type": "number_card",
				"data": {"number_card_name": label, "col": 4}
	},
		)
	if not any(row.get("id") == "construction-portfolio-h" for row in content if isinstance(row, dict)):
		content.insert(
			2,
			{
				"id": "construction-portfolio-h",
				"type": "header",
				"data": {"text": "<b>Portfolio · Contract status</b>", "col": 12}
	},
		)
	ws.content = json.dumps(content, separators=(",", ":"))
	ws.save(ignore_permissions=True)
