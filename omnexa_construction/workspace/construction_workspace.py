# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Keep Construction Project Wizard + Setup visible on Construction workspace."""

from __future__ import annotations

import json

import frappe

WIZARD_LABEL = "New Project (Wizard)"
WIZARD_PAGE = "construction-project-wizard"
WIZARD_CONTENT_ID = "construction-sc-wizard"

SETUP_DOCTYPE = "Construction Project Setup"
SETUP_LABEL = "Construction Project Setup"
SETUP_CONTENT_ID = "construction-sc-project-setup"


def _row_val(row, field: str, default=None):
	if isinstance(row, dict):
		return row.get(field, default)
	return getattr(row, field, default)


def _reindex_child_rows(rows) -> None:
	"""Frappe persists child-table order via row.idx, not Python list order."""
	for i, row in enumerate(rows or []):
		idx = i + 1
		if isinstance(row, dict):
			row["idx"] = idx
		else:
			row.idx = idx


def sync_construction_wizard_and_setup(*, save: bool = True) -> bool:
	"""Backward-compatible entry — syncs full Construction workspace menu."""
	stats = sync_construction_workspace_menu(save=save)
	return bool(stats.get("links") or stats.get("shortcuts") or stats.get("sections"))


def _sidebar_insert_index(ws, before_card: str) -> int:
	for i, row in enumerate(ws.links or []):
		if _row_val(row, "type") == "Card Break" and (_row_val(row, "label") or "") == before_card:
			return i
	return 0


def _reposition_sidebar_link(ws, link_to: str, link_type: str, insert_at: int) -> bool:
	found_idx = None
	for i, row in enumerate(ws.links or []):
		if (_row_val(row, "link_to") or "") == link_to and _row_val(row, "link_type") == link_type:
			found_idx = i
			break
	if found_idx is None:
		return False
	if found_idx == insert_at:
		row = ws.links[found_idx]
		if _row_val(row, "hidden"):
			if isinstance(row, dict):
				row["hidden"] = 0
			else:
				row.hidden = 0
			return True
		return False
	row = ws.links.pop(found_idx)
	ws.links.insert(min(insert_at, len(ws.links)), row)
	return True


def _reposition_shortcut(ws, link_to: str, link_type: str, position: int) -> bool:
	found_idx = None
	for i, row in enumerate(ws.shortcuts or []):
		if (_row_val(row, "link_to") or "") == link_to and _row_val(row, "type") == link_type:
			found_idx = i
			break
	if found_idx is None:
		return False
	if found_idx == position:
		return False
	row = ws.shortcuts.pop(found_idx)
	ws.shortcuts.insert(min(position, len(ws.shortcuts)), row)
	return True


def _ensure_sidebar_link(
	ws,
	*,
	label: str,
	link_to: str,
	link_type: str,
	icon: str,
	insert_at: int = 0,
) -> bool:
	for row in ws.links or []:
		if (_row_val(row, "link_to") or "") == link_to and _row_val(row, "link_type") == link_type:
			if _row_val(row, "hidden"):
				if isinstance(row, dict):
					row["hidden"] = 0
				else:
					row.hidden = 0
				return True
			return False

	row = ws.append(
		"links",
		{
			"type": "Link",
			"label": label,
			"link_to": link_to,
			"link_type": link_type,
			"icon": icon,
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
	)
	if insert_at < len(ws.links) - 1:
		ws.links.pop()
		ws.links.insert(min(insert_at, len(ws.links)), row)
	return True


def _ensure_shortcut(
	ws,
	*,
	label: str,
	link_to: str,
	link_type: str,
	color: str,
	position: int = 0,
	doc_view: str | None = None,
) -> bool:
	for row in ws.shortcuts or []:
		if (_row_val(row, "link_to") or "") == link_to and _row_val(row, "type") == link_type:
			return False

	values = {
		"label": label,
		"type": link_type,
		"link_to": link_to,
		"color": color,
	}
	if doc_view:
		values["doc_view"] = doc_view

	row = ws.append("shortcuts", values)
	insert_at = min(position, max(0, len(ws.shortcuts) - 1))
	if insert_at < len(ws.shortcuts) - 1:
		ws.shortcuts.pop()
		ws.shortcuts.insert(insert_at, row)
	return True


def _ensure_content_shortcut(
	content: list,
	block_id: str,
	shortcut_name: str,
	*,
	after_header: bool = False,
	after_id: str | None = None,
) -> bool:
	if any(isinstance(row, dict) and row.get("id") == block_id for row in content):
		return False

	insert_at = len(content)
	if after_id:
		for i, row in enumerate(content):
			if isinstance(row, dict) and row.get("id") == after_id:
				insert_at = i + 1
				break
	elif after_header:
		for i, row in enumerate(content):
			if not isinstance(row, dict):
				continue
			if row.get("type") == "header":
				text = (row.get("data") or {}).get("text") or ""
				if any(token in text for token in ("Quick Actions", "Operations", "Construction")):
					insert_at = i + 1
					break

	content.insert(
		insert_at,
		{
			"id": block_id,
			"type": "shortcut",
			"data": {"shortcut_name": shortcut_name, "col": 3},
		},
	)
	return True


# ---------------------------------------------------------------------------
# Full Construction workspace sidebar (logical project lifecycle order)
# ---------------------------------------------------------------------------

# (link_type, link_to, label, icon, is_query_report)
WorkspaceItem = tuple[str, str, str, str, bool]

WORKSPACE_SECTIONS: list[tuple[str, list[WorkspaceItem]]] = [
	(
		"1. البداية والإعداد",
		[
			("Page", "construction-project-wizard", "New Project (Wizard)", "add", False),
			("DocType", "Construction Project Setup", "Construction Project Setup", "edit", False),
			("Page", "construction-executive-dashboard", "Executive Dashboard", "layout", False),
			("Page", "construction-site-mobile", "Site Mobile Hub", "smartphone", False),
			("DocType", "Construction Integration Settings", "Integration Settings", "link", False),
		],
	),
	(
		"2. العقود والكميات",
		[
			("DocType", "Customer", "Customer (project owners)", "users", False),
			("DocType", "Project Contract", "Project Contract", "file-text", False),
			("DocType", "BOQ Item", "BOQ Item", "list", False),
			("DocType", "Construction BOQ Template", "BOQ Template", "copy", False),
			("DocType", "Construction Trade Package", "Trade Package", "briefcase", False),
			("DocType", "Regional Cost Factor", "Regional Cost Factor", "globe", False),
		],
	),
	(
		"3. الجدول الزمني",
		[
			("DocType", "Construction Schedule Baseline", "Schedule Baseline", "calendar", False),
			("DocType", "PM WBS Task", "PM WBS Task", "tree", False),
			("DocType", "Construction MIDP", "MIDP", "book", False),
		],
	),
	(
		"4. الموقع والتنفيذ",
		[
			("DocType", "Site Daily Report", "Site Daily Report", "clipboard", False),
			("DocType", "Construction Equipment Usage", "Equipment Usage", "tool", False),
			("DocType", "Construction Snagging Item", "Snagging", "check-circle", False),
			("DocType", "Construction Inspection Request", "Inspection Request", "search", False),
			("DocType", "Construction QS Measurement Sheet", "QS Measurement", "edit", False),
		],
	),
	(
		"5. مقاولي الباطن",
		[
			("DocType", "Subcontract Work Order", "Subcontract Work Order", "users", False),
			("DocType", "Subcontract Payment Certificate", "Subcontract Payment", "credit-card", False),
			("DocType", "Subcontract Retention Release", "Subcontract Retention Release", "unlock", False),
			("DocType", "Construction Supplier Prequalification", "Supplier Prequalification", "award", False),
		],
	),
	(
		"6. التغييرات والمطالبات (FIDIC)",
		[
			("DocType", "Construction Change Order", "Change Order", "shuffle", False),
			("DocType", "Construction Extension of Time", "Extension of Time (EOT)", "clock", False),
			("DocType", "Construction Claim", "Construction Claim", "file-warning", False),
			("DocType", "Construction FIDIC Notice", "FIDIC Notice", "bell", False),
			("DocType", "Construction Work Delay Notice", "Work Delay Notice", "alert-circle", False),
			("DocType", "Construction Final Account Statement", "Final Account", "file-text", False),
			("DocType", "Construction Retention Release", "Retention Release", "unlock", False),
		],
	),
	(
		"7. NEC4 والنزاعات",
		[
			("DocType", "Construction Early Warning", "Early Warning (NEC4)", "alert-triangle", False),
			("DocType", "Construction Compensation Event", "Compensation Event", "zap", False),
			("DocType", "Construction Dispute Case", "Dispute Case", "flag", False),
			("DocType", "Construction DAB Referral", "DAB Referral", "share-2", False),
			("DocType", "Construction Settlement", "Settlement", "check", False),
		],
	),
	(
		"8. الفوترة والدفع",
		[
			("DocType", "IPC Certificate", "IPC Certificate", "credit-card", False),
			("DocType", "Project WIP Snapshot", "Project WIP Snapshot", "activity", False),
		],
	),
	(
		"9. المشتريات",
		[
			("DocType", "Construction RFQ", "Construction RFQ", "file-search", False),
			("DocType", "Purchase Request", "Purchase Request", "shopping-bag", False),
			("DocType", "Purchase Order", "Purchase Order", "shopping-cart", False),
			("DocType", "Supplier", "Supplier", "truck", False),
		],
	),
	(
		"10. الاعتمادات والنماذج",
		[
			("DocType", "Construction RFI", "RFI", "help-circle", False),
			("DocType", "Construction Material Approval Request", "Material Approval", "package", False),
			("DocType", "Construction Work Approval Request", "Work Approval", "check-square", False),
			("DocType", "Construction Fines Statement", "Fines Statement", "slash", False),
			("DocType", "Contractor Account Statement", "Contractor Statement", "file-minus", False),
			("DocType", "Construction Document Transmittal", "Document Transmittal", "folder", False),
		],
	),
	(
		"11. الجودة والسلامة (QHSE)",
		[
			("DocType", "Construction NCR", "NCR", "alert-triangle", False),
			("DocType", "Construction CAPA", "CAPA", "shield", False),
			("DocType", "Construction HSE Incident", "HSE Incident", "heart", False),
			("DocType", "Construction Permit to Work", "Permit to Work", "lock", False),
			("DocType", "Construction Hazard Register", "Hazard Register", "alert-octagon", False),
			("DocType", "Construction Toolbox Talk", "Toolbox Talk", "message-circle", False),
			("DocType", "Construction Internal Audit", "Internal Audit", "search", False),
			("DocType", "Construction Management Review", "Management Review", "users", False),
			("DocType", "Construction Safety KPI", "Safety KPI", "trending-up", False),
			("Report", "NCR Aging", "NCR Aging", "alert-triangle", True),
			("Report", "PTW Register", "PTW Register", "lock", True),
			("Report", "HSE Incident Summary", "HSE Summary", "heart", True),
		],
	),
	(
		"12. البيئة",
		[
			("DocType", "Construction Environmental Aspect", "Environmental Aspect", "sun", False),
			("DocType", "Construction Waste Log", "Waste Log", "trash-2", False),
			("DocType", "Construction Environmental Monitoring", "Environmental Monitoring", "thermometer", False),
			("Report", "Environmental Compliance", "Environmental Compliance", "sun", True),
		],
	),
	(
		"13. الوثائق والـ CDE / BIM",
		[
			("DocType", "Construction CDE Document", "CDE Document", "file", False),
			("DocType", "Construction BIM Model Register", "BIM Model Register", "box", False),
			("DocType", "Construction BIM Issue", "BIM Issue", "git-branch", False),
			("DocType", "Construction Inspection Test Plan", "ITP", "list", False),
			("DocType", "Engineering Stage", "Engineering Stage", "map", False),
			("DocType", "Engineering Submittal", "Engineering Submittal", "file-text", False),
		],
	),
	(
		"14. التسليم والضمان",
		[
			("DocType", "Construction DLP Record", "DLP Record", "clock", False),
			("DocType", "Construction Residential Unit", "Residential Unit", "home", False),
			("DocType", "Construction Plot Unit", "Plot Unit", "map-pin", False),
		],
	),
	(
		"15. التقارير والتحليلات",
		[
			("Report", "Construction Executive Summary", "Executive Summary", "bar-chart-2", True),
			("Report", "Construction EVM Dashboard", "EVM Dashboard", "activity", True),
			("Report", "Construction Earned Value", "Earned Value (EVM)", "layers", True),
			("Report", "Construction Contract Control", "Contract Control", "sliders", True),
			("Report", "Construction FIDIC Compliance", "FIDIC Compliance", "check-circle", True),
			("Report", "Construction Commercial Pipeline", "Commercial Pipeline", "git-merge", True),
			("Report", "BOQ Progress", "BOQ Progress", "bar-chart", True),
			("Report", "BOQ Commitment vs Actual", "BOQ Commitment vs Actual", "pie-chart", True),
			("Report", "BOQ Cost Overrun", "BOQ Cost Overrun", "alert-circle", True),
			("Report", "Material Consumption vs BOQ", "Material vs BOQ", "package", True),
			("Report", "IPC Certificate Summary", "IPC Summary", "file-text", True),
			("Report", "Project Profitability (Construction)", "Project Profitability", "trending-up", True),
			("Report", "Construction Contract International Summary", "International Summary", "globe", True),
			("Report", "Currency Revaluation Exposure", "Currency Exposure", "dollar-sign", True),
			("Report", "RFQ Bid Tabulation", "RFQ Bid Tabulation", "columns", True),
			("Report", "Construction Snagging Summary", "Snagging Summary", "check-circle", True),
		],
	),
]

DASHBOARD_SHORTCUTS: list[tuple[str, str, str, str, str | None]] = [
	# (type, link_to, label, color, doc_view)
	("Page", WIZARD_PAGE, WIZARD_LABEL, "Green", None),
	("DocType", SETUP_DOCTYPE, SETUP_LABEL, "Green", "List"),
	("DocType", "Project Contract", "Project Contract", "Cyan", "List"),
	("DocType", "BOQ Item", "BOQ Item", "Blue", "List"),
	("DocType", "Site Daily Report", "Site Daily Report", "Orange", "List"),
	("DocType", "IPC Certificate", "IPC Certificate", "Cyan", "List"),
	("DocType", "Construction Change Order", "Change Order", "Red", "List"),
	("Page", "construction-executive-dashboard", "Executive Dashboard", "Purple", None),
	("Report", "Construction EVM Dashboard", "EVM Dashboard", "Grey", None),
	("Report", "Construction Executive Summary", "Executive Summary", "Grey", None),
	("Report", "BOQ Progress", "BOQ Progress", "Red", None),
	("DocType", "Construction RFI", "RFI", "Blue", "List"),
	("DocType", "Construction NCR", "NCR", "Orange", "List"),
	("DocType", "Construction Work Approval Request", "Work Approval", "Blue", "List"),
	("DocType", "Construction Fines Statement", "Fines Statement", "Red", "List"),
	("DocType", "Contractor Account Statement", "Contractor Statement", "Blue", "List"),
]


def _link_target_exists(link_type: str, link_to: str) -> bool:
	if link_type == "DocType":
		return bool(frappe.db.exists("DocType", link_to))
	if link_type == "Report":
		return bool(frappe.db.exists("Report", link_to))
	if link_type == "Page":
		return bool(frappe.db.exists("Page", link_to))
	return False


def _card_break(label: str) -> dict:
	return {
		"type": "Card Break",
		"label": label,
		"hidden": 0,
		"is_query_report": 0,
		"link_count": 0,
		"onboard": 0,
	}


def _sidebar_link(
	link_type: str,
	link_to: str,
	label: str,
	icon: str,
	*,
	is_query_report: bool = False,
) -> dict:
	row = {
		"type": "Link",
		"label": label,
		"link_to": link_to,
		"link_type": link_type,
		"icon": icon,
		"hidden": 0,
		"is_query_report": 1 if is_query_report else 0,
		"link_count": 0,
		"onboard": 0,
	}
	if is_query_report and link_type == "Report":
		ref = frappe.db.get_value("Report", link_to, "ref_doctype")
		if ref:
			row["report_ref_doctype"] = ref
	return row


def _link_key(row) -> tuple[str, str] | None:
	if _row_val(row, "type") != "Link":
		return None
	link_to = _row_val(row, "link_to")
	link_type = _row_val(row, "link_type")
	if not link_to or not link_type:
		return None
	return (link_type, link_to)


QHSE_WORKSPACE_NAME = "Construction QHSE"


def remove_construction_qhse_workspace() -> bool:
	"""Remove standalone QHSE workspace; its links live under Construction."""
	if not frappe.db.exists("Workspace", QHSE_WORKSPACE_NAME):
		return False
	frappe.delete_doc("Workspace", QHSE_WORKSPACE_NAME, force=True, ignore_permissions=True)
	frappe.clear_cache(doctype="Workspace")
	return True


def sync_construction_workspace_menu(*, save: bool = True) -> dict:
	"""Rebuild Construction workspace sidebar links in logical order (idempotent).

	Preserves custom links not in the catalog under «Other / أخرى».
	"""
	stats = {"sections": 0, "links": 0, "preserved": 0, "shortcuts": 0}
	if not frappe.db.exists("Workspace", "Construction"):
		return stats

	ws = frappe.get_doc("Workspace", "Construction")
	desired_keys: set[tuple[str, str]] = set()
	new_links: list[dict] = []

	for section_label, items in WORKSPACE_SECTIONS:
		section_rows: list[dict] = []
		for link_type, link_to, label, icon, is_report in items:
			if not _link_target_exists(link_type, link_to):
				continue
			key = (link_type, link_to)
			if key in desired_keys:
				continue
			desired_keys.add(key)
			section_rows.append(_sidebar_link(link_type, link_to, label, icon, is_query_report=is_report))
		if not section_rows:
			continue
		new_links.append(_card_break(section_label))
		new_links.extend(section_rows)
		stats["sections"] += 1
		stats["links"] += len(section_rows)

	# Preserve unknown / custom sidebar links (do not break user additions)
	extras: list[dict] = []
	for row in ws.links or []:
		key = _link_key(row)
		if not key or key in desired_keys:
			continue
		extras.append(
			_sidebar_link(
				key[0],
				key[1],
				_row_val(row, "label") or key[1],
				_row_val(row, "icon") or "link",
				is_query_report=bool(_row_val(row, "is_query_report")),
			)
		)
		stats["preserved"] += 1

	if extras:
		new_links.append(_card_break("Other / أخرى"))
		new_links.extend(extras)

	ws.links = []
	for row in new_links:
		ws.append("links", row)
	_reindex_child_rows(ws.links)

	# Dashboard shortcuts — merge without duplicating
	existing_sc = {(s.type, s.link_to) for s in (ws.shortcuts or []) if s.link_to}
	pos = 0
	for link_type, link_to, label, color, doc_view in DASHBOARD_SHORTCUTS:
		if not _link_target_exists(link_type, link_to):
			continue
		key = (link_type, link_to)
		if key not in existing_sc:
			_ensure_shortcut(
				ws,
				label=label,
				link_to=link_to,
				link_type=link_type,
				color=color,
				position=pos,
				doc_view=doc_view,
			)
			existing_sc.add(key)
			stats["shortcuts"] += 1
		else:
			_reposition_shortcut(ws, link_to, link_type, pos)
		pos += 1
	_reindex_child_rows(ws.shortcuts)

	# Wizard blocks on workspace home content
	content = json.loads(ws.content or "[]")
	content_changed = False
	if _ensure_content_shortcut(content, WIZARD_CONTENT_ID, WIZARD_LABEL, after_header=True):
		content_changed = True
	if _ensure_content_shortcut(content, SETUP_CONTENT_ID, SETUP_LABEL, after_id=WIZARD_CONTENT_ID):
		content_changed = True
	if content_changed:
		ws.content = json.dumps(content, separators=(",", ":"))

	remove_construction_qhse_workspace()

	if save:
		ws.save(ignore_permissions=True, ignore_version=True)
		frappe.clear_cache(doctype="Workspace")
	return stats

