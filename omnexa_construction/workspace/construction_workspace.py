# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Keep Construction Project Wizard + Setup visible on Construction workspace."""

from __future__ import annotations

import json
from pathlib import Path
import frappe
from frappe import _

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
			"onboard": 0
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
		"color": color
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
				text = (row.get("data") or {
	}).get("text") or ""
				if any(token in text for token in ("Quick Actions", "Operations", "Construction")):
					insert_at = i + 1
					break

	content.insert(
		insert_at,
		{
			"id": block_id,
			"type": "shortcut",
			"data": {"shortcut_name": shortcut_name, "col": 3}
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
		"1. Start & Setup",
		[
			("Page", "construction-project-wizard", "New Project (Wizard)", "add", False),
			("DocType", "Construction Project Setup", "Construction Project Setup", "edit", False),
			("Page", "construction-executive-dashboard", "Executive Dashboard", "layout", False),
			("Page", "portfolio_dashboard", "Portfolio Dashboard", "grid", False),
			("Page", "construction-site-mobile", "Site Mobile Hub", "smartphone", False),
			("DocType", "Construction Integration Settings", "Integration Settings", "link", False),
			("Page", "primavera_sync_dashboard", "Primavera P6 Sync Dashboard", "refresh-cw", False),
		],
	),
	(
		"2. Contracts & BOQ",
		[
			("DocType", "Customer", "Customer (project owners)", "users", False),
			("DocType", "Construction Bid Estimate", "Bid Estimate", "target", False),
			("DocType", "Construction CBS Element", "CBS Element", "git-branch", False),
			("DocType", "Project Contract", "Project Contract", "file-text", False),
			("DocType", "BOQ Item", "BOQ Item", "list", False),
			("DocType", "Construction BOQ Template", "BOQ Template", "copy", False),
			("DocType", "Construction Trade Package", "Trade Package", "briefcase", False),
			("DocType", "Regional Cost Factor", "Regional Cost Factor", "globe", False),
		],
	),
	(
		"3. Schedule",
		[
			("DocType", "Construction Schedule Baseline", "Schedule Baseline", "calendar", False),
			("Page", "construction-schedule-gantt", "Schedule Gantt", "bar-chart", False),
			("Page", "primavera-project-import", "Import from Primavera XER", "upload", False),
			("DocType", "PM WBS Task", "PM WBS Task", "tree", False),
			("DocType", "Construction MIDP", "MIDP", "book", False),
		],
	),
	(
		"10. BIM & CDE",
		[
			("Page", "bim_ifc_viewer", "BIM IFC Viewer", "box", False),
			("DocType", "Construction BIM Model Register", "BIM Model Register", "database", False),
			("DocType", "Construction BIM Issue", "BIM Issue", "alert-circle", False),
			("DocType", "Construction CDE Document", "CDE Document", "file", False),
			("DocType", "Construction Document Transmittal", "Document Transmittal", "share", False),
			("DocType", "Uniclass 2015 Classification", "Uniclass 2015", "list", False),
		],
	),
	(
		"4. Site & Execution",
		[
			("DocType", "Site Daily Report", "Site Daily Report", "clipboard", False),
			("DocType", "Timesheet Entry", "Timesheet Entry", "clock", False),
			("DocType", "Construction Project Risk", "Project Risk Register", "alert-triangle", False),
			("DocType", "Construction Equipment Usage", "Equipment Usage", "tool", False),
			("DocType", "Construction Snagging Item", "Snagging", "check-circle", False),
			("DocType", "Construction Inspection Request", "Inspection Request", "search", False),
			("DocType", "Construction QS Measurement Sheet", "QS Measurement", "edit", False),
		],
	),
	(
		"5. Subcontractors",
		[
			("DocType", "Subcontract Work Order", "Subcontract Work Order", "users", False),
			("DocType", "Subcontract Payment Certificate", "Subcontract Payment", "credit-card", False),
			("DocType", "Subcontract Retention Release", "Subcontract Retention Release", "unlock", False),
			("DocType", "Construction Supplier Prequalification", "Supplier Prequalification", "award", False),
		],
	),
	(
		"6. Changes & Claims (FIDIC)",
		[
			("DocType", "Construction FIDIC Clause Reference", "FIDIC Clause Reference", "book-open", False),
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
		"7. NEC4 & Disputes",
		[
			("DocType", "Construction Early Warning", "Early Warning (NEC4)", "alert-triangle", False),
			("DocType", "Construction Compensation Event", "Compensation Event", "zap", False),
			("DocType", "Construction Dispute Case", "Dispute Case", "flag", False),
			("DocType", "Construction DAB Referral", "DAB Referral", "share-2", False),
			("DocType", "Construction Settlement", "Settlement", "check", False),
		],
	),
	(
		"8. Billing & Payment",
		[
			("DocType", "IPC Certificate", "IPC Certificate", "credit-card", False),
			("DocType", "Subcontract Payment Certificate", "Subcontract Payment", "credit-card", False),
			("DocType", "Subcontract Retention Release", "Subcontract Retention Release", "unlock", False),
			("DocType", "Construction Retention Release", "Retention Release", "unlock", False),
			("DocType", "Construction Final Account Statement", "Final Account", "file-text", False),
			("DocType", "Contractor Account Statement", "Contractor Statement", "file-minus", False),
			("DocType", "Construction Fines Statement", "Fines Statement", "slash", False),
			("DocType", "Project WIP Snapshot", "Project WIP Snapshot", "activity", False),
		],
	),
	(
		"9. Procurement",
		[
			("DocType", "Construction RFQ", "Construction RFQ", "file-search", False),
			("DocType", "Purchase Request", "Purchase Request", "shopping-bag", False),
			("DocType", "Purchase Order", "Purchase Order", "shopping-cart", False),
			("DocType", "Supplier", "Supplier", "truck", False),
		],
	),
	(
		"10. Approvals & Forms",
		[
			("DocType", "Construction RFI", "RFI", "help-circle", False),
			("DocType", "Construction Material Approval Request", "Material Approval", "package", False),
			("DocType", "Construction Work Approval Request", "Work Approval", "check-square", False),
			("DocType", "Construction Document Transmittal", "Document Transmittal", "folder", False),
		],
	),
	(
		"11. Quality & Safety (QHSE)",
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
			("Page", "construction-hse-dashboard", "HSE KPI Dashboard", "activity", False),
			("Report", "HSE Incident Summary", "HSE Summary", "heart", True),
			("DocType", "Construction OSHA Site Checklist", "OSHA Site Checklist", "clipboard", False),
			("DocType", "Construction User NPS", "User NPS Survey", "smile", False),
		],
	),
	(
		"12. Environment",
		[
			("DocType", "Construction Environmental Aspect", "Environmental Aspect", "sun", False),
			("DocType", "Construction Waste Log", "Waste Log", "trash-2", False),
			("DocType", "Construction Environmental Monitoring", "Environmental Monitoring", "thermometer", False),
			("Report", "Environmental Compliance", "Environmental Compliance", "sun", True),
		],
	),
	(
		"13. Documents & CDE / BIM",
		[
			("Page", "construction-ifc-viewer", "IFC Viewer (Lite)", "box", False),
			("DocType", "Construction CDE Document", "CDE Document", "file", False),
			("DocType", "Construction BIM Model Register", "BIM Model Register", "box", False),
			("DocType", "Construction BIM Issue", "BIM Issue", "git-branch", False),
			("DocType", "Construction CDE Access Log", "CDE Access Log", "shield", False),
			("DocType", "Construction Inspection Test Plan", "ITP", "list", False),
			("DocType", "Engineering Stage", "Engineering Stage", "map", False),
			("DocType", "Engineering Submittal", "Engineering Submittal", "file-text", False),
		],
	),
	(
		"14. Handover & Warranty",
		[
			("DocType", "Construction DLP Record", "DLP Record", "clock", False),
			("DocType", "Construction Residential Unit", "Residential Unit", "home", False),
			("DocType", "Construction Plot Unit", "Plot Unit", "map-pin", False),
		],
	),
	(
		"15. Reports & Analytics",
		[
			("Page", "construction-bi-executive", "Executive BI", "trending-up", False),
			("Report", "Construction World Class Mock Audit", "World Class Mock Audit", "award", True),
			("Report", "Construction Executive Summary", "Executive Summary", "bar-chart-2", True),
			("Report", "Construction EVM Dashboard", "EVM Dashboard", "activity", True),
			("Report", "Construction Earned Value", "Earned Value (EVM)", "layers", True),
			("Report", "Construction Contract Control", "Contract Control", "sliders", True),
			("Report", "Construction FIDIC Compliance", "FIDIC Compliance", "check-circle", True),
			("Report", "Construction FIDIC Compliance Checklist", "FIDIC Checklist 100%", "check-square", True),
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
			("Report", "Construction Bid Comparison", "Bid Comparison", "target", True),
			("Report", "Construction CBS BOQ Summary", "CBS BOQ Summary", "git-branch", True),
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
	("DocType", "PM WBS Task", "PM WBS Task", "Purple", "List"),
	("Page", "construction-schedule-gantt", "Schedule Gantt", "Blue", None),
	("DocType", "Site Daily Report", "Site Daily Report", "Orange", "List"),
	("Page", "construction-site-mobile", "Site Mobile Hub", "Orange", None),
	("DocType", "Subcontract Work Order", "Subcontract Work Order", "Green", "List"),
	("DocType", "IPC Certificate", "IPC Certificate", "Cyan", "List"),
	("DocType", "Subcontract Payment Certificate", "Subcontract Payment", "Cyan", "List"),
	("DocType", "Construction Extension of Time", "Extension of Time (EOT)", "Teal", "List"),
	("DocType", "Construction Change Order", "Change Order", "Red", "List"),
	("DocType", "Construction Claim", "Construction Claim", "Pink", "List"),
	("DocType", "Project WIP Snapshot", "Project WIP Snapshot", "Purple", "List"),
	("Page", "construction-executive-dashboard", "Executive Dashboard", "Purple", None),
	("Page", "construction-bi-executive", "Executive BI", "Purple", None),
	("Page", "construction-hse-dashboard", "HSE KPI Dashboard", "Red", None),
	("Page", "construction-ifc-viewer", "IFC Viewer", "Grey", None),
	("Report", "Construction EVM Dashboard", "EVM Dashboard", "Grey", None),
	("Report", "Construction Executive Summary", "Executive Summary", "Grey", None),
	("Report", "BOQ Progress", "BOQ Progress", "Red", None),
	("DocType", "Construction RFI", "RFI", "Blue", "List"),
	("DocType", "Construction NCR", "NCR", "Orange", "List"),
	("DocType", "Construction Work Approval Request", "Work Approval", "Blue", "List"),
	("DocType", "Construction Fines Statement", "Fines Statement", "Red", "List"),
	("DocType", "Contractor Account Statement", "Contractor Statement", "Blue", "List"),
	("DocType", "Purchase Order", "Purchase Order", "Orange", "List"),
	("DocType", "Supplier", "Supplier", "Green", "List"),
]

WORKSPACE_FIXTURE_PATH = Path(__file__).resolve().parent.parent / "omnexa_construction" / "workspace" / "construction" / "construction.json"
CONTENT_SLUG = "construction"
QUICK_ACTIONS_HEADER = "Quick Actions"
ALL_MODULES_HEADER = "All modules & links"


def sync_construction_workspace_content(ws) -> int:
	"""Rebuild EditorJS body so every sidebar section renders as a card on the desk page.

	Frappe only paints ``Workspace Link`` groups when ``content`` contains matching ``card`` blocks.
	Without this, users see only a few Operations/Reports shortcuts from omnexa_core.
	"""
	blocks: list[dict] = []
	block_i = 0

	def _nid(suffix: str) -> str:
		nonlocal block_i
		block_i += 1
		return f"{CONTENT_SLUG}-{suffix}-{block_i}"

	existing = json.loads(ws.content or "[]")
	for row in existing:
		if isinstance(row, dict) and row.get("type") == "onboarding":
			blocks.append(row)
			break

	blocks.append(
		{
			"id": f"{CONTENT_SLUG
	}-h",
			"type": "header",
			"data": {"text": '<span class="h4"><b>Construction</b></span>', "col": 12}
	}
	)

	blocks.append(
		{
			"id": _nid("qa-h"),
			"type": "header",
			"data": {"text": f'<span class="h5"><b>{QUICK_ACTIONS_HEADER
	}</b></span>', "col": 12}
	}
	)
	for row in ws.shortcuts or []:
		st = _row_val(row, "type")
		if st == "Report":
			continue
		label = _row_val(row, "label")
		if not label:
			continue
		blocks.append(
			{
				"id": _nid("qa"),
				"type": "shortcut",
				"data": {"shortcut_name": label, "col": 4}
	}
		)

	blocks.append(
		{
			"id": _nid("all-h"),
			"type": "header",
			"data": {"text": f'<span class="h5"><b>{ALL_MODULES_HEADER
	}</b></span>', "col": 12}
	}
	)
	cards = 0
	for row in ws.links or []:
		if _row_val(row, "type") != "Card Break":
			continue
		label = (_row_val(row, "label") or "").strip()
		if not label:
			continue
		blocks.append(
			{
				"id": _nid("card"),
				"type": "card",
				"data": {"card_name": label, "col": 4}
	}
		)
		cards += 1

	if ws.number_cards:
		blocks.append(
			{
				"id": _nid("kpi-h"),
				"type": "header",
				"data": {"text": '<span class="h5"><b>KPIs</b></span>', "col": 12}
	}
		)
		for i, nc in enumerate(ws.number_cards[:12]):
			# Desk EditorJS resolves tiles by Number Card label, not document name.
			nc_label = _row_val(nc, "label") or frappe.db.get_value(
				"Number Card", _row_val(nc, "number_card_name"), "label"
			)
			if not nc_label:
				continue
			blocks.append(
				{
					"id": _nid("nc"),
					"type": "number_card",
					"data": {"number_card_name": nc_label, "col": 4}
	}
			)

	if ws.charts:
		blocks.append(
			{
				"id": _nid("ch-h"),
				"type": "header",
				"data": {"text": '<span class="h5"><b>Charts</b></span>', "col": 12}
	}
		)
		for ch in ws.charts[:9]:
			ch_label = _row_val(ch, "label") or _row_val(ch, "chart_name")
			if not ch_label:
				continue
			blocks.append(
				{
					"id": _nid("ch"),
					"type": "chart",
					"data": {"chart_name": ch_label, "col": 4}
	}
			)

	ws.content = json.dumps(blocks, separators=(",", ":"))
	return cards


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
		"onboard": 0
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
		"onboard": 0
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


def _serialize_workspace_child_row(row) -> dict:
	"""Strip DB-only fields for module workspace fixture export."""
	skip = {
		"name",
		"owner",
		"creation",
		"modified",
		"modified_by",
		"docstatus",
		"parent",
		"parentfield",
		"parenttype",
		"idx",
		"doctype",
	}
	out: dict = {}
	for key, value in (row.as_dict() if hasattr(row, "as_dict") else dict(row)).items():
		if key in skip or value in (None, ""):
			continue
		out[key] = value
	return out


def export_construction_workspace_fixture(ws=None) -> bool:
	"""Write synced sidebar links + shortcuts into module construction.json (fresh installs)."""
	path = WORKSPACE_FIXTURE_PATH
	if not path.is_file():
		return False

	if ws is None:
		if not frappe.db.exists("Workspace", "Construction"):
			return False
		ws = frappe.get_doc("Workspace", "Construction")

	data = json.loads(path.read_text(encoding="utf-8"))
	data["links"] = [_serialize_workspace_child_row(row) for row in (ws.links or [])]
	data["shortcuts"] = [_serialize_workspace_child_row(row) for row in (ws.shortcuts or [])]
	if ws.content:
		data["content"] = ws.content
	data["modified"] = frappe.utils.now_datetime().strftime("%Y-%m-%d %H:%M:%S.%f")
	path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
	return True


CONSTRUCTION_WORKSPACE_KPIS: list[tuple[str, str, list]] = [
	("Project contracts", "Project Contract", []),
	("Active contracts", "Project Contract", [["status", "=", "Active"]]),
	("Suspended contracts", "Project Contract", [["status", "=", "Suspended"]]),
	("Closed contracts", "Project Contract", [["status", "=", "Closed"]]),
	("BOQ lines", "BOQ Item", []),
	("Site daily reports", "Site Daily Report", []),
	("Subcontract work orders", "Subcontract Work Order", []),
	("IPC certificates", "IPC Certificate", []),
	("Construction claims", "Construction Claim", []),
	("Open NCRs", "Construction NCR", [["status", "in", ["Open", "Under Review"]]]),
	(
		"Open HSE incidents",
		"Construction HSE Incident",
		[["status", "in", ["Open", "Reported", "Under Investigation"]]],
	),
]


def _resolve_number_card_name(name_or_label: str | None) -> str | None:
	if not name_or_label:
		return None
	if frappe.db.exists("Number Card", name_or_label):
		return name_or_label
	return frappe.db.get_value("Number Card", {"label": name_or_label
	}, "name")


def _upsert_construction_number_card(label: str, document_type: str, filters: list | None) -> str | None:
	if not frappe.db.exists("DocType", document_type) or not frappe.db.exists("DocType", "Number Card"):
		return None
	from omnexa_construction.utils.number_card_filters import normalize_number_card_filters

	filters_json = json.dumps(
		normalize_number_card_filters(document_type, filters or []),
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


def _ensure_construction_workspace_kpis_local(ws) -> None:
	"""Fallback when omnexa_core workspace tower is unavailable."""
	card_rows: list[dict[str, str]] = []
	for label, doctype, filters in CONSTRUCTION_WORKSPACE_KPIS:
		nm = _upsert_construction_number_card(label, doctype, filters)
		if nm:
			card_rows.append({"number_card_name": nm, "label": label
	})
	ws.number_cards = []
	for row in card_rows:
		ws.append("number_cards", row)

	valid_charts: list[dict[str, str]] = []
	for row in ws.charts or []:
		cn = _row_val(row, "chart_name")
		if cn and frappe.db.exists("Dashboard Chart", cn):
			valid_charts.append({"chart_name": cn, "label": _row_val(row, "label") or cn})
	ws.charts = []
	for row in valid_charts:
		ws.append("charts", row)


def _ensure_construction_workspace_kpis(ws) -> None:
	"""Create KPI docs and bind workspace child rows to valid Number Card / Chart names."""
	try:
		from omnexa_core.omnexa_core.workspace_control_tower import MODULE_SPECS, _apply_kpi_to_workspace

		spec = MODULE_SPECS.get("omnexa_construction")
		if spec:
			_apply_kpi_to_workspace(ws, dict(spec), "Construction")
			return
	except Exception:
		frappe.log_error(frappe.get_traceback(), _("Construction workspace KPI sync (omnexa_core)"))

	_ensure_construction_workspace_kpis_local(ws)


def _prune_invalid_workspace_kpi_links(ws) -> int:
	"""Drop workspace KPI rows whose linked Number Card / Chart documents are missing."""
	kept_nc: list[dict[str, str]] = []
	for row in ws.number_cards or []:
		nm = _resolve_number_card_name(_row_val(row, "number_card_name") or _row_val(row, "label"))
		if nm:
			kept_nc.append(
				{
					"number_card_name": nm,
					"label": _row_val(row, "label") or nm}
			)
	ws.number_cards = []
	for row in kept_nc:
		ws.append("number_cards", row)

	kept_ch: list[dict[str, str]] = []
	for row in ws.charts or []:
		cn = _row_val(row, "chart_name")
		if cn and frappe.db.exists("Dashboard Chart", cn):
			kept_ch.append({"chart_name": cn, "label": _row_val(row, "label") or cn})
	ws.charts = []
	for row in kept_ch:
		ws.append("charts", row)
	return len(kept_nc) + len(kept_ch)


def _safe_save_construction_workspace(ws) -> None:
	"""Save workspace; on link validation errors prune stale KPI/chart rows and retry once."""
	try:
		ws.save(ignore_permissions=True, ignore_version=True)
	except frappe.LinkValidationError:
		_prune_invalid_workspace_kpi_links(ws)
		ws.content = sync_construction_workspace_content(ws)
		ws.save(ignore_permissions=True, ignore_version=True)


def remove_construction_qhse_workspace() -> bool:
	"""Remove standalone QHSE workspace; its links live under Construction."""
	if not frappe.db.exists("Workspace", QHSE_WORKSPACE_NAME):
		return False
	frappe.delete_doc("Workspace", QHSE_WORKSPACE_NAME, force=True, ignore_permissions=True)
	frappe.clear_cache(doctype="Workspace")
	return True


def sync_construction_workspace_menu(*, save: bool = True) -> dict:
	"""Rebuild Construction workspace sidebar links in logical order (idempotent).

	Preserves custom links not in the catalog under «Other».
	"""
	stats = {"sections": 0, "links": 0, "preserved": 0, "shortcuts": 0, "content_cards": 0
	}
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
		new_links.append(_card_break("Other"))
		new_links.extend(extras)

	ws.links = []
	for row in new_links:
		ws.append("links", row)
	_reindex_child_rows(ws.links)

	# Dashboard shortcuts — full catalog (sidebar + desk content parity)
	from omnexa_core.omnexa_core.vertical_workspace_sync import build_shortcuts_from_link_rows

	ws.shortcuts = []
	link_rows_for_sc: list[dict] = []
	for row in ws.links or []:
		if _row_val(row, "type") != "Link":
			continue
		link_rows_for_sc.append(
			{
				"type": "Link",
				"label": _row_val(row, "label"),
				"link_type": _row_val(row, "link_type"),
				"link_to": _row_val(row, "link_to"),
				"report_ref_doctype": _row_val(row, "report_ref_doctype")}
		)
	for values in build_shortcuts_from_link_rows(link_rows_for_sc):
		ws.append("shortcuts", values)
		stats["shortcuts"] += 1
	_reindex_child_rows(ws.shortcuts)

	_ensure_construction_workspace_kpis(ws)
	stats["content_cards"] = sync_construction_workspace_content(ws)

	remove_construction_qhse_workspace()

	if save:
		_safe_save_construction_workspace(ws)
		frappe.clear_cache(doctype="Workspace")
		try:
			export_construction_workspace_fixture(ws)
			stats["fixture_exported"] = True
		except OSError:
			stats["fixture_exported"] = False
	return stats

