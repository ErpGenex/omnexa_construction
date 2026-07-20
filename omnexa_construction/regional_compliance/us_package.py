# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""US compliance package — certified payroll export, OSHA checklist (Phase 13.3)."""

from __future__ import annotations

import csv
import io

import frappe
from frappe import _
from frappe.utils import getdate, nowdate


OSHA_CHECKLIST_ITEMS = [
	("PPE available on site", "personal_protective_equipment"),
	("Fall protection plan in place", "fall_protection"),
	("Excavation permits current", "excavation"),
	("Electrical lockout/tagout", "loto"),
	("Heat illness prevention", "heat_illness"),
]


@frappe.whitelist()
def export_certified_payroll(project_contract: str, from_date: str | None = None, to_date: str | None = None) -> dict:
	"""Export site labour hours for certified payroll (WH-347 style columns, MVP)."""
	from_date = from_date or str(getdate(nowdate()).replace(day=1))
	to_date = to_date or nowdate()

	if not frappe.db.exists("DocType", "Timesheet Entry"):
		return {"rows": [], "csv": "", "message": _("Timesheet Entry not installed.")}

	meta = frappe.get_meta("Timesheet Entry")
	project_field = "project" if meta.has_field("project") else None
	date_field = "start_date" if meta.has_field("start_date") else None
	if not project_field:
		return {"rows": [], "csv": "", "message": _("Timesheet Entry has no project link.")}

	filters = {project_field: project_contract, "docstatus": 1}
	if date_field:
		filters[date_field] = ["between", [from_date, to_date]]

	fields = ["name"]
	for f in ("employee", "employee_name", "hours", "start_date", "end_date"):
		if meta.has_field(f):
			fields.append(f)
	rows = frappe.get_all("Timesheet Entry", filters=filters, fields=fields, limit=5000)

	buf = io.StringIO()
	writer = csv.writer(buf)
	writer.writerow(["Employee", "Name", "Hours", "Period Start", "Period End", "Project Contract"])
	for r in rows:
		writer.writerow(
			[
				r.employee,
				r.employee_name,
				r.hours,
				r.start_date,
				r.end_date,
				project_contract,
			]
		)
	return {
		"rows": rows,
		"csv": buf.getvalue(),
		"filename": f"certified_payroll_{project_contract}.csv",
	}


@frappe.whitelist()
def get_osha_checklist_template() -> list[dict]:
	return [{"item": label, "fieldname": key} for label, key in OSHA_CHECKLIST_ITEMS]


@frappe.whitelist()
def get_us_compliance_snapshot(project_contract: str) -> dict:
	payroll_rows = 0
	if frappe.db.exists("DocType", "Timesheet Entry"):
		meta = frappe.get_meta("Timesheet Entry")
		if meta.has_field("project"):
			payroll_rows = frappe.db.count(
				"Timesheet Entry",
				{"project": project_contract, "docstatus": 1},
			)
	osha_logs = 0
	if frappe.db.exists("DocType", "Construction OSHA Site Checklist"):
		osha_logs = frappe.db.count(
			"Construction OSHA Site Checklist",
			{"project_contract": project_contract, "docstatus": ["<", 2]},
		)
	checks = [
		{
			"id": "payroll",
			"label": _("Certified payroll source data (timesheets)"),
			"status": "pass" if payroll_rows else "warn",
		},
		{
			"id": "osha",
			"label": _("OSHA site checklist records"),
			"status": "pass" if osha_logs else "info",
		},
	]
	return {
		"package": "US",
		"project_contract": project_contract,
		"checks": checks,
		"osha_template": get_osha_checklist_template(),
		"score_percent": round(100 * sum(1 for c in checks if c["status"] == "pass") / len(checks), 1),
	}
