# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""US WH-347 style certified payroll (extends certified payroll CSV)."""

from __future__ import annotations

import frappe

from omnexa_construction.regional_compliance.us_package import export_certified_payroll


@frappe.whitelist()
def export_wh347_payroll(project_contract: str, from_date: str | None = None, to_date: str | None = None) -> dict:
	base = export_certified_payroll(project_contract, from_date, to_date)
	header = "WH-347,Project,Employee,Name,Hours,Period Start,Period End\n"
	lines = [header]
	for row in base.get("rows") or []:
		lines.append(
			f"ROW,{project_contract},{row.get('employee')},{row.get('employee_name')},"
			f"{row.get('hours')},{row.get('start_date')},{row.get('end_date')}\n"
		)
	return {**base, "wh347_csv": "".join(lines), "format": "WH-347-MVP"}
