# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Shared contract / change-order value helpers for IPC and Project Contract."""

from __future__ import annotations

import frappe
from frappe.utils import flt


def approved_change_order_impact(project_contract: str | None) -> float:
	if not project_contract:
		return 0.0
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(cost_impact), 0)
		FROM `tabConstruction Change Order`
		WHERE project_contract = %s
			AND docstatus < 2
			AND status IN ('Approved', 'Implemented')
		""",
		(project_contract,),
	)
	return flt(row[0][0] if row else 0)


def billable_contract_value(project_contract: str | None) -> float:
	if not project_contract:
		return 0.0
	base = flt(frappe.db.get_value("Project Contract", project_contract, "contract_value"))
	return base + approved_change_order_impact(project_contract)


def retention_held_from_certified_ipc(project_contract: str | None) -> float:
	if not project_contract:
		return 0.0
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(retention_deduction), 0)
		FROM `tabIPC Certificate`
		WHERE project_contract = %s
			AND status IN ('Certified', 'Posted')
			AND docstatus < 2
		""",
		(project_contract,),
	)
	return flt(row[0][0] if row else 0)


def certified_ipc_net_total(project_contract: str | None) -> float:
	if not project_contract:
		return 0.0
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(net_amount), 0)
		FROM `tabIPC Certificate`
		WHERE project_contract = %s
			AND status IN ('Certified', 'Posted')
			AND docstatus < 2
		""",
		(project_contract,),
	)
	return flt(row[0][0] if row else 0)


def eot_approved_count(project_contract: str | None) -> int:
	if not project_contract:
		return 0
	return frappe.db.count(
		"Construction Extension of Time",
		{
			"project_contract": project_contract,
			"status": "Approved",
			"docstatus": ["<", 2]},
	)


def claims_active_count(project_contract: str | None) -> int:
	if not project_contract:
		return 0
	return frappe.db.count(
		"Construction Claim",
		{
			"project_contract": project_contract,
			"status": ["in", ["Submitted", "Under Review"]],
			"docstatus": ["<", 2]},
	)


def refresh_project_contract_financials(project_contract: str | None) -> None:
	"""Recompute stored contract totals from change orders and certified IPCs."""
	if not project_contract or not frappe.db.exists("Project Contract", project_contract):
		return
	co = approved_change_order_impact(project_contract)
	base = flt(frappe.db.get_value("Project Contract", project_contract, "contract_value"))
	frappe.db.set_value(
		"Project Contract",
		project_contract,
		{
			"approved_change_orders_value": co,
			"revised_contract_value": base + co,
			"retention_held_to_date": retention_held_from_certified_ipc(project_contract)
	},
		update_modified=False,
	)
