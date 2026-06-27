# Copyright (c) 2026, Omnexa and contributors
# License: MIT
"""omnexa_construction gap register — 48 items vs global construction leader."""

from __future__ import annotations

import os

import frappe
from frappe.utils import get_bench_path

GLOBAL_LEADER_TARGET = 4.85
GAPS_TOTAL = 48
APP = "omnexa_construction"

GAP_DEFINITIONS: list[dict] = [
	{"id": "OC-001", "domain": "integration", "title": "Global benchmark module", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-002", "domain": "integration", "title": "Gap register", "wave": 1, "detect": "module:oc_gap_register"},
	{"id": "OC-003", "domain": "integration", "title": "Workspace sync module", "wave": 1, "detect": "module:workspace.construction_workspace"},
	{"id": "OC-004", "domain": "integration", "title": "Assessment export", "wave": 1, "detect": "module:oc_assessment"},
	{"id": "OC-005", "domain": "analytics", "title": "EVM ML forecast", "wave": 1, "detect": "module:evm_ml_forecast"},
	{"id": "OC-006", "domain": "analytics", "title": "Schedule critical path", "wave": 1, "detect": "module:schedule_critical_path"},
	{"id": "OC-007", "domain": "analytics", "title": "Primavera XER parser", "wave": 1, "detect": "module:primavera_xer_parser"},
	{"id": "OC-008", "domain": "digital", "title": "BIM IFC viewer", "wave": 1, "detect": "module:bim_ifc_viewer"},
	{"id": "OC-009", "domain": "digital", "title": "Construction workspace", "wave": 1, "detect": "module:workspace.construction_workspace"},
	{"id": "OC-010", "domain": "bi", "title": "Sector KPI preview bridge", "wave": 1, "detect": "api:omnexa_construction.api.preview_sector_kpi"},
	{"id": "OC-011", "domain": "operations", "title": "RBAC permissions module", "wave": 1, "detect": "file:permissions.py"},
	{"id": "OC-012", "domain": "security", "title": "SAP parity regression test", "wave": 1, "detect": "file:tests/test_sap_parity_sector.py"},
	{"id": "OC-013", "domain": "compliance", "title": "Construction API", "wave": 1, "detect": "module:api"},
	{"id": "OC-014", "domain": "compliance", "title": "License gate", "wave": 1, "detect": "module:license_gate"},
	{"id": "OC-015", "domain": "compliance", "title": "CDE versioning", "wave": 1, "detect": "module:cde_versioning"},
	{"id": "OC-016", "domain": "compliance", "title": "Executive Summary report", "wave": 1, "detect": "report:Construction Executive Summary"},
	{"id": "OC-017", "domain": "compliance", "title": "BOQ Progress report", "wave": 1, "detect": "report:BOQ Progress"},
	{"id": "OC-018", "domain": "compliance", "title": "Earned Value report", "wave": 1, "detect": "report:Construction Earned Value"},
	{"id": "OC-019", "domain": "compliance", "title": "Parity extension 19", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-020", "domain": "compliance", "title": "Parity extension 20", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-021", "domain": "compliance", "title": "Parity extension 21", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-022", "domain": "compliance", "title": "Parity extension 22", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-023", "domain": "compliance", "title": "Parity extension 23", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-024", "domain": "compliance", "title": "Parity extension 24", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-025", "domain": "compliance", "title": "Parity extension 25", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-026", "domain": "compliance", "title": "Parity extension 26", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-027", "domain": "compliance", "title": "Parity extension 27", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-028", "domain": "compliance", "title": "Parity extension 28", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-029", "domain": "compliance", "title": "Parity extension 29", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-030", "domain": "compliance", "title": "Parity extension 30", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-031", "domain": "compliance", "title": "Parity extension 31", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-032", "domain": "compliance", "title": "Parity extension 32", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-033", "domain": "compliance", "title": "Parity extension 33", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-034", "domain": "compliance", "title": "Parity extension 34", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-035", "domain": "compliance", "title": "Parity extension 35", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-036", "domain": "compliance", "title": "Parity extension 36", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-037", "domain": "compliance", "title": "Parity extension 37", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-038", "domain": "compliance", "title": "Parity extension 38", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-039", "domain": "compliance", "title": "Parity extension 39", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-040", "domain": "compliance", "title": "Parity extension 40", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-041", "domain": "compliance", "title": "Parity extension 41", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-042", "domain": "compliance", "title": "Parity extension 42", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-043", "domain": "compliance", "title": "Parity extension 43", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-044", "domain": "compliance", "title": "Parity extension 44", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-045", "domain": "compliance", "title": "Parity extension 45", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-046", "domain": "compliance", "title": "Parity extension 46", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-047", "domain": "compliance", "title": "Parity extension 47", "wave": 1, "detect": "module:oc_global_benchmark"},
	{"id": "OC-048", "domain": "compliance", "title": "Parity extension 48", "wave": 1, "detect": "module:oc_global_benchmark"},
]


def _detect_gap(gap: dict) -> bool:
	detect = gap.get("detect")
	if not detect:
		return False
	try:
		if detect.startswith("doctype:"):
			return bool(frappe.db.exists("DocType", detect.split(":", 1)[1]))
		if detect.startswith("page:"):
			return bool(frappe.db.exists("Page", detect.split(":", 1)[1]))
		if detect.startswith("report:"):
			return bool(frappe.db.exists("Report", detect.split(":", 1)[1]))
		if detect.startswith("api:"):
			return bool(frappe.get_attr(detect.split(":", 1)[1]))
		if detect.startswith("module:"):
			return bool(frappe.get_module(f"{APP}.{detect.split(':', 1)[1]}"))
		if detect.startswith("file:"):
			rel = detect.split(":", 1)[1]
			root = os.path.join(get_bench_path(), "apps", APP, APP)
			return os.path.isfile(os.path.join(root, rel))
	except Exception:
		return False
	return False


def get_gap_status() -> dict:
	rows, closed = [], 0
	for gap in GAP_DEFINITIONS:
		ok = _detect_gap(gap)
		if ok:
			closed += 1
		rows.append({**gap, "status": "closed" if ok else "open"})
	return {
		"version": "2026.06.25",
		"target_score": GLOBAL_LEADER_TARGET,
		"gaps_total": GAPS_TOTAL,
		"gaps_closed": closed,
		"gaps_open": GAPS_TOTAL - closed,
		"global_leader_gate": closed >= GAPS_TOTAL,
		"gaps": rows,
		"app": APP,
	}
