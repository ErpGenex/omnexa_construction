# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Primavera P6 XER import into Schedule Baseline (TASK table)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, getdate

from omnexa_construction.primavera_xer_parser import (
	date_diff_safe,
	extract_xer_tasks,
	load_xer_content,
	parse_xer_file,
)


@frappe.whitelist()
def import_xer_to_baseline(baseline_name: str, file_url: str) -> dict:
	baseline = frappe.get_doc("Construction Schedule Baseline", baseline_name)
	content = load_xer_content(file_url)
	sections = parse_xer_file(content)
	tasks = extract_xer_tasks(sections)
	if not tasks:
		frappe.throw(_("No tasks found in XER file."), title=_("XER Import"))

	baseline.tasks = []
	project_start = getdate(baseline.planned_start) if baseline.planned_start else getdate()
	for row in tasks:
		start = row.get("start_date") or project_start
		end = row.get("end_date") or add_days(start, max(1, row.get("duration_days", 1) - 1))
		task_row = {
			"task_name": row["task_name"],
			"start_date": start,
			"end_date": end,
			"duration_days": row.get("duration_days") or date_diff_safe(end, start) + 1,
			"is_milestone": row.get("is_milestone") or 0,
			"cost_code": row.get("cost_code"),
		}
		meta = frappe.get_meta("Construction Schedule Baseline Task")
		if meta.has_field("predecessor_task") and row.get("predecessor_task"):
			task_row["predecessor_task"] = row["predecessor_task"]
		baseline.append("tasks", task_row)
	baseline.save()
	return {"imported": len(tasks), "baseline": baseline.name}


def parse_xer_tasks(content: str) -> list[dict]:
	"""Backward-compatible helper for tests and callers."""
	return extract_xer_tasks(parse_xer_file(content))


def _parse_xer_date(value: str | None):
	from omnexa_construction.primavera_xer_parser import parse_xer_date

	return parse_xer_date(value)
