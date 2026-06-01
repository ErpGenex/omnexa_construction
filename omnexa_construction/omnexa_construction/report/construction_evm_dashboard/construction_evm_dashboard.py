# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

from omnexa_construction.evm_metrics import evm_snapshot
from omnexa_core.omnexa_core.report_print.report_query_filters import get_all_filters, prepare_filters


def execute(filters=None):
	filters = prepare_filters(filters)
	as_of = filters.get("as_of_date")
	contracts = frappe.get_all(
		"Project Contract",
		filters=get_all_filters(filters, "Project Contract", company=True, branch=True),
		fields=["name"],
		limit_page_length=5000,
	)
	snapshots = [evm_snapshot(row.name, as_of) for row in contracts]
	columns = _columns()
	data = snapshots

	labels = [s.get("contract_title") or s.get("project_contract") for s in snapshots[:12]]
	ev_vals = [flt(s.get("ev")) for s in snapshots[:12]]
	pv_vals = [flt(s.get("pv")) for s in snapshots[:12]]
	ac_vals = [flt(s.get("ac")) for s in snapshots[:12]]

	chart = {
		"data": {
			"labels": labels or [_("No contracts")],
			"datasets": [
				{"name": _("EV"), "values": ev_vals or [0]},
				{"name": _("PV"), "values": pv_vals or [0]},
				{"name": _("AC"), "values": ac_vals or [0]},
			],
		},
		"type": "bar",
	}

	avg_cpi = sum(flt(s.get("cpi")) for s in snapshots) / len(snapshots) if snapshots else 0
	avg_spi = sum(flt(s.get("spi")) for s in snapshots) / len(snapshots) if snapshots else 0
	report_summary = [
		{"label": _("Contracts"), "value": len(snapshots), "indicator": "Blue"},
		{"label": _("Avg CPI"), "value": round(avg_cpi, 2), "indicator": "Green" if avg_cpi >= 1 else "Red"},
		{"label": _("Avg SPI"), "value": round(avg_spi, 2), "indicator": "Green" if avg_spi >= 1 else "Orange"},
	]
	return columns, data, None, chart, report_summary


def _columns():
	return [
		{"label": _("Contract"), "fieldname": "project_contract", "fieldtype": "Link", "options": "Project Contract", "width": 140},
		{"label": _("Title"), "fieldname": "contract_title", "fieldtype": "Data", "width": 160},
		{"label": _("BAC"), "fieldname": "bac", "fieldtype": "Currency", "width": 110},
		{"label": _("PV"), "fieldname": "pv", "fieldtype": "Currency", "width": 100},
		{"label": _("EV"), "fieldname": "ev", "fieldtype": "Currency", "width": 100},
		{"label": _("AC"), "fieldname": "ac", "fieldtype": "Currency", "width": 100},
		{"label": _("CPI"), "fieldname": "cpi", "fieldtype": "Float", "precision": 2, "width": 70},
		{"label": _("SPI"), "fieldname": "spi", "fieldtype": "Float", "precision": 2, "width": 70},
		{"label": _("CV"), "fieldname": "cv", "fieldtype": "Currency", "width": 100},
		{"label": _("SV"), "fieldname": "sv", "fieldtype": "Currency", "width": 100},
		{"label": _("EAC"), "fieldname": "eac", "fieldtype": "Currency", "width": 100},
		{"label": _("% Planned"), "fieldname": "schedule_percent", "fieldtype": "Percent", "width": 90},
	]
