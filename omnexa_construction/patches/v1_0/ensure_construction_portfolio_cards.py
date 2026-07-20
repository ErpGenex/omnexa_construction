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

# Additional Number Cards required by Workspace
ADDITIONAL_CARDS = [
	("Project Contract", "Project Contract", []),
	("BOQ Item", "BOQ Item", []),
	("Site Daily Report", "Site Daily Report", []),
	("Subcontract Work Order", "Subcontract Work Order", []),
	("Extension of Time (EOT)", "Construction Extension of Time", []),
	("Construction Claim", "Construction Claim", []),
	("IPC Certificate", "IPC Certificate", []),
	("Open NCRs", "Construction NCR", [["status", "in", ["Open", "Under Review"]]]),
	("Open HSE incidents", "Construction HSE Incident", [["status", "in", ["Open", "Reported", "Under Investigation"]]]),
]


def execute():
	if not frappe.db.exists("DocType", "Number Card"):
		return
	for label, doctype, filters in PORTFOLIO_CARDS:
		if frappe.db.exists("DocType", doctype):
			_upsert_number_card(label, doctype, filters)
	for label, doctype, filters in ADDITIONAL_CARDS:
		if frappe.db.exists("DocType", doctype):
			_upsert_number_card(label, doctype, filters)
	# Prune non-existent charts BEFORE syncing workspace to prevent LinkValidationError
	_prune_nonexistent_charts()
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


def _prune_nonexistent_charts():
	"""Remove Dashboard Chart references from Workspace if the charts don't exist."""
	if not frappe.db.exists("Workspace", "Construction"):
		return
	ws = frappe.get_doc("Workspace", "Construction")
	valid_charts = []
	for row in ws.charts or []:
		chart_name = row.get("chart_name") or row.get("label")
		if chart_name and frappe.db.exists("Dashboard Chart", chart_name):
			valid_charts.append({"chart_name": chart_name, "label": row.get("label") or chart_name})
	ws.charts = []
	for row in valid_charts:
		ws.append("charts", row)
	ws.save(ignore_permissions=True)
