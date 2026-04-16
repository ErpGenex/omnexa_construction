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
